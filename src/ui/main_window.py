import os
import webbrowser
from typing import Dict, List, Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QFileDialog,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QSizePolicy,
    QSplitter,
    QStatusBar,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from src.implementations import (
    DomSearchStrategy,
    ElementTreeSearchStrategy,
    SaxSearchStrategy,
    XsltTransformer,
)
from src.interfaces import XmlSearchContext, XmlSearchStrategy, XmlTransformer
from src.models import ArchiveMaterial, SearchCriteria


class MainWindow(QMainWindow):
    """
    Main application window for Faculty Electronic Archive XML processor.
    Strictly handles UI presentation and user interaction, delegating all XML
    and transformation logic to services according to the Strategy Pattern.
    """

    def __init__(
        self,
        search_context: Optional[XmlSearchContext] = None,
        transformer: Optional[XmlTransformer] = None,
    ) -> None:
        super().__init__()

        # Service dependencies
        self.strategies: Dict[str, XmlSearchStrategy] = {
            "SAX API": SaxSearchStrategy(),
            "DOM API": DomSearchStrategy(),
            "LINQ to XML (ElementTree)": ElementTreeSearchStrategy(),
        }
        self.search_context = search_context or XmlSearchContext(self.strategies["SAX API"])
        self.transformer = transformer or XsltTransformer()

        # Default paths to bundled sample data
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        default_xml = os.path.join(base_dir, "data", "archive.xml")
        default_xsl = os.path.join(base_dir, "data", "archive_transform.xsl")

        self.xml_path: str = default_xml if os.path.exists(default_xml) else ""
        self.xsl_path: str = default_xsl if os.path.exists(default_xsl) else ""

        self._init_ui()
        self._post_init_load()

    def _init_ui(self) -> None:
        self.setWindowTitle("Електронний архів факультету — Обробка XML")
        self.resize(1100, 750)
        self.setMinimumSize(850, 600)

        # Main Central Widget
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        # 1. File Selection Section
        file_group = self._create_file_group()
        main_layout.addWidget(file_group)

        # 2. Strategy Selector Section
        strategy_group = self._create_strategy_group()
        main_layout.addWidget(strategy_group)

        # 3. Search Controls Section
        search_group = self._create_search_group()
        main_layout.addWidget(search_group)

        # 4. Results Display Area
        results_group = self._create_results_group()
        main_layout.addWidget(results_group, stretch=1)

        # 5. Bottom Action Bar (Clear, Transform, Exit)
        bottom_bar = self._create_bottom_bar()
        main_layout.addLayout(bottom_bar)

        # Status Bar
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Готово до роботи")

    def _create_file_group(self) -> QGroupBox:
        group = QGroupBox("Вибір файлів для обробки", self)
        layout = QVBoxLayout(group)
        layout.setSpacing(8)

        # XML file row
        xml_row = QHBoxLayout()
        xml_label = QLabel("XML-файл:", self)
        xml_label.setFixedWidth(85)
        self.xml_path_edit = QLineEdit(self)
        self.xml_path_edit.setReadOnly(True)
        self.xml_path_edit.setText(self.xml_path)
        self.xml_path_edit.setPlaceholderText("Оберіть файл архіву (.xml)...")

        self.btn_browse_xml = QPushButton("Обрати XML-файл", self)
        self.btn_browse_xml.setFixedWidth(160)
        self.btn_browse_xml.clicked.connect(self._on_browse_xml)

        xml_row.addWidget(xml_label)
        xml_row.addWidget(self.xml_path_edit)
        xml_row.addWidget(self.btn_browse_xml)
        layout.addLayout(xml_row)

        # XSL file row
        xsl_row = QHBoxLayout()
        xsl_label = QLabel("XSL-файл:", self)
        xsl_label.setFixedWidth(85)
        self.xsl_path_edit = QLineEdit(self)
        self.xsl_path_edit.setReadOnly(True)
        self.xsl_path_edit.setText(self.xsl_path)
        self.xsl_path_edit.setPlaceholderText("Оберіть файл стилю (.xsl)...")

        self.btn_browse_xsl = QPushButton("Обрати XSL-файл", self)
        self.btn_browse_xsl.setFixedWidth(160)
        self.btn_browse_xsl.clicked.connect(self._on_browse_xsl)

        xsl_row.addWidget(xsl_label)
        xsl_row.addWidget(self.xsl_path_edit)
        xsl_row.addWidget(self.btn_browse_xsl)
        layout.addLayout(xsl_row)

        return group

    def _create_strategy_group(self) -> QGroupBox:
        group = QGroupBox("Метод аналізу XML:", self)
        layout = QHBoxLayout(group)
        layout.setSpacing(25)

        self.strategy_button_group = QButtonGroup(self)
        self.radio_sax = QRadioButton("SAX API", self)
        self.radio_dom = QRadioButton("DOM API", self)
        self.radio_elementtree = QRadioButton("LINQ to XML (ElementTree)", self)

        self.radio_sax.setChecked(True)

        self.strategy_button_group.addButton(self.radio_sax)
        self.strategy_button_group.addButton(self.radio_dom)
        self.strategy_button_group.addButton(self.radio_elementtree)

        layout.addWidget(self.radio_sax)
        layout.addWidget(self.radio_dom)
        layout.addWidget(self.radio_elementtree)
        layout.addStretch()

        self.radio_sax.toggled.connect(self._on_strategy_changed)
        self.radio_dom.toggled.connect(self._on_strategy_changed)
        self.radio_elementtree.toggled.connect(self._on_strategy_changed)

        return group

    def _create_search_group(self) -> QGroupBox:
        group = QGroupBox("Параметри пошуку та фільтрації", self)
        layout = QHBoxLayout(group)
        layout.setSpacing(12)

        # Keyword Search
        kw_label = QLabel("Ключове слово:", self)
        self.kw_edit = QLineEdit(self)
        self.kw_edit.setPlaceholderText("Введіть ключове слово...")
        self.kw_edit.returnPressed.connect(self._on_search)

        # Attribute selector & filter
        attr_label = QLabel("Вид матеріалу (type):", self)
        self.attr_combo = QComboBox(self)
        self.attr_combo.setMinimumWidth(180)
        self.attr_combo.addItem("Усі")

        # Search Button
        self.btn_search = QPushButton("Пошук", self)
        self.btn_search.setStyleSheet(
            "QPushButton { background-color: #2b6cb0; color: white; font-weight: bold; padding: 6px 18px; border-radius: 4px; }"
            "QPushButton:hover { background-color: #2c5282; }"
        )
        self.btn_search.clicked.connect(self._on_search)

        layout.addWidget(kw_label)
        layout.addWidget(self.kw_edit, stretch=2)
        layout.addWidget(attr_label)
        layout.addWidget(self.attr_combo, stretch=1)
        layout.addWidget(self.btn_search)

        return group

    def _create_results_group(self) -> QGroupBox:
        group = QGroupBox("Результати вибірки", self)
        layout = QVBoxLayout(group)

        self.results_edit = QTextEdit(self)
        self.results_edit.setReadOnly(True)
        self.results_edit.setPlaceholderText("Результати пошуку відображатимуться тут...")
        layout.addWidget(self.results_edit)

        return group

    def _create_bottom_bar(self) -> QHBoxLayout:
        bar = QHBoxLayout()
        bar.setSpacing(12)

        # Clear button
        self.btn_clear = QPushButton("Очистити (Clear)", self)
        self.btn_clear.clicked.connect(self._on_clear)

        # Transform to HTML button
        self.btn_transform = QPushButton("Трансформувати в HTML", self)
        self.btn_transform.setStyleSheet(
            "QPushButton { background-color: #276749; color: white; font-weight: bold; padding: 6px 16px; border-radius: 4px; }"
            "QPushButton:hover { background-color: #22543d; }"
        )
        self.btn_transform.clicked.connect(self._on_transform)

        # Exit button
        self.btn_exit = QPushButton("Вихід", self)
        self.btn_exit.setStyleSheet(
            "QPushButton { background-color: #c53030; color: white; padding: 6px 16px; border-radius: 4px; }"
            "QPushButton:hover { background-color: #9b2c2c; }"
        )
        self.btn_exit.clicked.connect(self.close)

        bar.addWidget(self.btn_clear)
        bar.addWidget(self.btn_transform)
        bar.addStretch()
        bar.addWidget(self.btn_exit)

        return bar

    def _post_init_load(self) -> None:
        """Dynamically populate attribute values if default XML exists."""
        if self.xml_path and os.path.exists(self.xml_path):
            self._reload_attribute_values()

    def _on_browse_xml(self) -> None:
        start_dir = os.path.dirname(self.xml_path) if self.xml_path else ""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Обрати XML-файл",
            start_dir,
            "XML файли (*.xml);;Усі файли (*.*)",
        )
        if file_path:
            self.xml_path = file_path
            self.xml_path_edit.setText(file_path)
            self._reload_attribute_values()
            self.status_bar.showMessage(f"Завантажено XML: {os.path.basename(file_path)}")

    def _on_browse_xsl(self) -> None:
        start_dir = os.path.dirname(self.xsl_path) if self.xsl_path else ""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Обрати XSL-файл",
            start_dir,
            "XSL файли (*.xsl *.xslt);;Усі файли (*.*)",
        )
        if file_path:
            self.xsl_path = file_path
            self.xsl_path_edit.setText(file_path)
            self.status_bar.showMessage(f"Завантажено XSL: {os.path.basename(file_path)}")

    def _reload_attribute_values(self) -> None:
        """Scan XML and populate unique attribute values."""
        if not self.xml_path or not os.path.exists(self.xml_path):
            return

        try:
            unique_types = self.transformer.extract_attribute_values(self.xml_path, "type")
            current_selection = self.attr_combo.currentText()

            self.attr_combo.clear()
            self.attr_combo.addItem("Усі")
            for val in unique_types:
                self.attr_combo.addItem(val)

            # Restore previous selection if possible
            idx = self.attr_combo.findText(current_selection)
            if idx >= 0:
                self.attr_combo.setCurrentIndex(idx)
            else:
                self.attr_combo.setCurrentIndex(0)
        except Exception as e:
            QMessageBox.warning(
                self,
                "Помилка зчитування атрибутів",
                f"Не вдалося зчитати унікальні атрибути з XML:\n{str(e)}",
            )

    def _on_strategy_changed(self) -> None:
        if self.radio_sax.isChecked():
            strategy_name = "SAX API"
        elif self.radio_dom.isChecked():
            strategy_name = "DOM API"
        else:
            strategy_name = "LINQ to XML (ElementTree)"

        self.search_context.strategy = self.strategies[strategy_name]
        self.status_bar.showMessage(f"Встановлено метод аналізу: {strategy_name}")

    def _on_search(self) -> None:
        if not self.xml_path or not os.path.exists(self.xml_path):
            QMessageBox.warning(
                self,
                "Файл не знайдено",
                "Будь ласка, оберіть дійсний XML-файл перед виконанням пошуку.",
            )
            return

        # Prepare criteria
        keyword = self.kw_edit.text().strip()
        selected_attr = self.attr_combo.currentText()
        criteria = SearchCriteria(
            keyword=keyword,
            attribute_name="type",
            attribute_value=selected_attr,
        )

        current_strat_name = self.search_context.strategy.name if self.search_context.strategy else "Невідомо"

        try:
            results = self.search_context.execute_search(self.xml_path, criteria)
            self._render_results(results, current_strat_name)
            self.status_bar.showMessage(
                f"Пошук завершено ({current_strat_name}). Знайдено записів: {len(results)}"
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Помилка аналізу XML",
                f"Сталася помилка під час обробки XML-документа:\n{str(e)}",
            )

    def _render_results(self, materials: List[ArchiveMaterial], strategy_name: str) -> None:
        if not materials:
            html = (
                "<div style='font-family: sans-serif; padding: 20px; text-align: center; color: #718096;'>"
                "<h3>За вашим запитом нічого не знайдено.</h3>"
                "<p>Спробуйте змінити ключове слово або критерій фільтрації.</p>"
                "</div>"
            )
            self.results_edit.setHtml(html)
            return

        cards_html: List[str] = []
        cards_html.append(
            f"<div style='font-family: sans-serif; font-size: 13px; color: #2d3748;'>"
            f"<div style='background-color: #ebf8ff; border: 1px solid #bee3f8; padding: 8px 12px; border-radius: 4px; margin-bottom: 12px; color: #2b6cb0; font-weight: bold;'>"
            f"Метод: {strategy_name} | Знайдено матеріалів: {len(materials)}"
            f"</div>"
        )

        for idx, m in enumerate(materials, start=1):
            # Dynamic attributes tags
            attrs_badges: List[str] = []
            for k, v in m.attributes.items():
                if k not in ("id", "type"):
                    attrs_badges.append(
                        f"<span style='background-color: #edf2f7; color: #4a5568; padding: 2px 6px; border-radius: 3px; font-size: 11px; margin-right: 4px; display: inline-block;'>"
                        f"<strong>{k}:</strong> {v}</span>"
                    )
            attrs_str = " ".join(attrs_badges) if attrs_badges else "<em style='color:#a0aec0;'>відсутні</em>"

            card = f"""
            <div style='background-color: #ffffff; border: 1px solid #e2e8f0; border-left: 4px solid #3182ce; padding: 12px 14px; margin-bottom: 12px; border-radius: 4px;'>
                <div style='display: flex; justify-content: space-between; margin-bottom: 6px;'>
                    <span style='background-color: #e9d8fd; color: #553c9a; font-weight: bold; padding: 2px 8px; border-radius: 4px; font-size: 11px;'>ID: {m.id}</span>
                    <span style='background-color: #feebc8; color: #7b341e; font-weight: bold; padding: 2px 8px; border-radius: 4px; font-size: 11px;'>Вид: {m.material_type or "—"}</span>
                </div>
                <div style='font-size: 15px; font-weight: bold; color: #2b6cb0; margin-top: 4px; margin-bottom: 6px;'>
                    {idx}. {m.title}
                </div>
                <div style='margin-bottom: 4px;'>
                    <strong>Автор:</strong> {m.author or "—"}
                </div>
                <div style='margin-bottom: 4px;'>
                    <strong>Факультет:</strong> {m.department or "—"} | <strong>Кафедра:</strong> {m.chair or "—"}
                </div>
                <div style='margin-bottom: 4px;'>
                    <strong>Обсяг:</strong> {m.volume} стор. | <strong>Дата створення:</strong> {m.created_date or "—"}
                </div>
                <div style='margin-top: 6px; margin-bottom: 6px;'>
                    <strong>Додаткові атрибути:</strong> {attrs_str}
                </div>
                {f"<div style='margin-top: 6px; padding: 6px 10px; background-color: #f7fafc; border-radius: 4px; font-style: italic; color: #4a5568;'><strong>Анотація:</strong> {m.annotation}</div>" if m.annotation else ""}
                {f"<div style='margin-top: 4px; font-size: 11px; color: #718096;'><em>Теги: {m.keywords}</em></div>" if m.keywords else ""}
            </div>
            """
            cards_html.append(card)

        cards_html.append("</div>")
        self.results_edit.setHtml("".join(cards_html))

    def _on_clear(self) -> None:
        """Clear results, keyword input, and reset attribute combo to 'Усі'."""
        self.kw_edit.clear()
        if self.attr_combo.count() > 0:
            self.attr_combo.setCurrentIndex(0)
        self.results_edit.clear()
        self.status_bar.showMessage("Параметри очищено")

    def _on_transform(self) -> None:
        """Perform XSLT transformation to HTML."""
        if not self.xml_path or not os.path.exists(self.xml_path):
            QMessageBox.warning(
                self,
                "Файл не знайдено",
                "Будь ласка, оберіть дійсний XML-файл для трансформації.",
            )
            return

        if not self.xsl_path or not os.path.exists(self.xsl_path):
            QMessageBox.warning(
                self,
                "Файл не знайдено",
                "Будь ласка, оберіть дійсний XSL-файл для трансформації.",
            )
            return

        default_out = os.path.join(
            os.path.dirname(self.xml_path),
            "archive_transformed.html",
        )

        out_path, _ = QFileDialog.getSaveFileName(
            self,
            "Зберегти трансформований HTML-файл",
            default_out,
            "HTML файли (*.html);;Усі файли (*.*)",
        )

        if not out_path:
            return

        try:
            saved_path = self.transformer.transform_to_html(self.xml_path, self.xsl_path, out_path)
            self.status_bar.showMessage(f"Трансформація успішна: {os.path.basename(saved_path)}")

            # Ask user if they wish to open the HTML document in a browser
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Трансформація успішна")
            msg_box.setText(
                f"HTML-документ успішно сформовано та збережено за шляхом:\n{saved_path}\n\nБажаєте відкрити його у веб-браузері?"
            )
            msg_box.setIcon(QMessageBox.Icon.Information)
            btn_yes = msg_box.addButton("Так", QMessageBox.ButtonRole.YesRole)
            btn_no = msg_box.addButton("Ні", QMessageBox.ButtonRole.NoRole)
            msg_box.setDefaultButton(btn_yes)
            msg_box.exec()

            if msg_box.clickedButton() == btn_yes:
                webbrowser.open(f"file://{os.path.abspath(saved_path)}")
        except Exception as e:
            QMessageBox.critical(
                self,
                "Помилка XSLT-трансформації",
                f"Під час виконання трансформації виникла помилка:\n{str(e)}",
            )

    def closeEvent(self, event) -> None:
        """Prompt user with Ukrainian exit confirmation dialog."""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Підтвердження виходу")
        msg_box.setText("Чи дійсно ви хочете завершити роботу з програмою?")
        msg_box.setIcon(QMessageBox.Icon.Question)
        btn_yes = msg_box.addButton("Так", QMessageBox.ButtonRole.YesRole)
        btn_no = msg_box.addButton("Ні", QMessageBox.ButtonRole.NoRole)
        msg_box.setDefaultButton(btn_no)

        msg_box.exec()

        if msg_box.clickedButton() == btn_yes:
            event.accept()
        else:
            event.ignore()
