import os
import unittest
from PyQt6.QtWidgets import QApplication

from src.implementations import (
    DomSearchStrategy,
    ElementTreeSearchStrategy,
    SaxSearchStrategy,
    XsltTransformer,
)
from src.interfaces import XmlSearchContext
from src.models import ArchiveMaterial, SearchCriteria
from src.ui import MainWindow

# Initialize offscreen application instance for GUI testing
app = QApplication.instance()
if app is None:
    app = QApplication(["-platform", "offscreen"])


class TestXmlStrategies(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cls.xml_path = os.path.join(base_dir, "data", "archive.xml")
        cls.xsl_path = os.path.join(base_dir, "data", "archive_transform.xsl")

    def test_all_strategies_match_full_archive(self):
        criteria = SearchCriteria()
        strategies = [SaxSearchStrategy(), DomSearchStrategy(), ElementTreeSearchStrategy()]
        results = [s.search(self.xml_path, criteria) for s in strategies]

        self.assertEqual(len(results[0]), 10)
        self.assertEqual(len(results[1]), 10)
        self.assertEqual(len(results[2]), 10)

        sax_ids = [m.id for m in results[0]]
        dom_ids = [m.id for m in results[1]]
        et_ids = [m.id for m in results[2]]
        self.assertEqual(sax_ids, dom_ids)
        self.assertEqual(sax_ids, et_ids)

    def test_dynamic_attributes_handling(self):
        dom_strat = DomSearchStrategy()
        results = dom_strat.search(self.xml_path, SearchCriteria())

        # Record 2 has custom attributes
        rec2 = next(m for m in results if m.id == "mat-002")
        self.assertEqual(rec2.attributes.get("language"), "українська")
        self.assertEqual(rec2.attributes.get("access"), "Відкритий")

        # Record 6 has edition and isbn
        rec6 = next(m for m in results if m.id == "mat-006")
        self.assertEqual(rec6.attributes.get("edition"), "2-ге видання")
        self.assertEqual(rec6.attributes.get("isbn"), "978-966-439-812-4")

        # Record 3 has minimal attributes
        rec3 = next(m for m in results if m.id == "mat-003")
        self.assertEqual(set(rec3.attributes.keys()), {"id", "faculty", "type"})

    def test_keyword_search(self):
        criteria = SearchCriteria(keyword="розподілених")
        sax_res = SaxSearchStrategy().search(self.xml_path, criteria)
        self.assertEqual(len(sax_res), 1)
        self.assertEqual(sax_res[0].id, "mat-002")

    def test_attribute_filter(self):
        criteria = SearchCriteria(attribute_name="type", attribute_value="Методичка")
        for strat in [SaxSearchStrategy(), DomSearchStrategy(), ElementTreeSearchStrategy()]:
            res = strat.search(self.xml_path, criteria)
            self.assertEqual(len(res), 2, f"Failed on strategy: {strat.name}")

    def test_no_results(self):
        criteria = SearchCriteria(keyword="nonexistent_value_xyz")
        for strat in [SaxSearchStrategy(), DomSearchStrategy(), ElementTreeSearchStrategy()]:
            res = strat.search(self.xml_path, criteria)
            self.assertEqual(len(res), 0)

    def test_xslt_transformation_and_extraction(self):
        transformer = XsltTransformer()
        types = transformer.extract_attribute_values(self.xml_path, "type")
        self.assertIn("Стаття", types)
        self.assertIn("Монографія", types)

        out_html = os.path.join(os.path.dirname(self.xml_path), "test_temp_output.html")
        saved = transformer.transform_to_html(self.xml_path, self.xsl_path, out_html)
        self.assertTrue(os.path.exists(saved))
        with open(saved, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("Електронний архів", content)
        self.assertIn("mat-001", content)
        if os.path.exists(out_html):
            os.remove(out_html)


class TestMainWindowUi(unittest.TestCase):
    def setUp(self):
        self.window = MainWindow()

    def test_window_title(self):
        self.assertEqual(self.window.windowTitle(), "Електронний архів факультету — Обробка XML")

    def test_dynamic_attributes_loaded(self):
        items = [self.window.attr_combo.itemText(i) for i in range(self.window.attr_combo.count())]
        self.assertEqual(items[0], "Усі")
        self.assertIn("Стаття", items)
        self.assertIn("Монографія", items)

    def test_search_and_clear_flow(self):
        self.window.kw_edit.setText("НАНУ")
        self.window.btn_search.click()
        self.assertIn("mat-007", self.window.results_edit.toHtml())

        self.window.btn_clear.click()
        self.assertEqual(self.window.kw_edit.text(), "")
        self.assertEqual(self.window.attr_combo.currentIndex(), 0)
        self.assertEqual(self.window.results_edit.toPlainText(), "")

    def test_strategy_switching(self):
        self.window.radio_dom.click()
        self.assertEqual(self.window.search_context.strategy.name, "DOM API")

        self.window.radio_elementtree.click()
        self.assertEqual(self.window.search_context.strategy.name, "LINQ to XML (ElementTree)")

        self.window.radio_sax.click()
        self.assertEqual(self.window.search_context.strategy.name, "SAX API")


if __name__ == "__main__":
    unittest.main()
