# Task: Develop a Desktop Application in Python + PyQt6 for XML Document Processing and XSLT Transformation ("Faculty Electronic Archive")

## 1. Tech Stack & Project Initialization

* **Language & GUI Framework:** Python 3.11+, desktop user interface built with **PyQt6**.
* **UI Localization:** **All user interface elements** (window title, buttons, labels, dropdown default items, status messages, error dialogs, and exit confirmation prompt) **must be in Ukrainian**.
* **Package & Environment Manager:** The project must be initialized and managed using **`uv`** (`uv init`, dependency management via `pyproject.toml`, execution via `uv run`).
* **XML & XSLT Libraries:**
* Python Standard Library: `xml.sax` (SAX API), `xml.dom.minidom` (DOM API), `xml.etree.ElementTree` (query/object-tree approach).
* External packages: **`PyQt6`** and **`lxml`** (for XPath queries and XSLT transformations), installed via `uv add PyQt6 lxml`.



## 2. Architecture & Directory Structure (Strictly Required)

Follow the exact project layout below. Every package inside `src/` must be a proper Python module exporting its public classes and functions via `__init__.py` (defining `__all__`):

* `pyproject.toml`
* `data/`
* `archive.xml` — Sample input XML file (Domain: Faculty Electronic Archive)
* `archive_transform.xsl` — XSL stylesheet for HTML transformation


* `src/`
* `__init__.py`
* `main.py` — Application entry point
* `models/` — Data structures (`@dataclass`)
* `__init__.py`
* `material.py` — Archive record and search criteria dataclasses


* `interfaces/` — Abstract Base Classes (using Python's `abc` module)
* `__init__.py`
* `search_strategy.py` — ABC for XML parsing/search strategies
* `transformer.py` — ABC for XSLT transformation (and attribute extraction)


* `implementations/` — Concrete implementations of the ABCs
* `__init__.py`
* `sax_strategy.py` — Implementation using `xml.sax`
* `dom_strategy.py` — Implementation using `xml.dom.minidom`
* `elementtree_strategy.py` — Implementation using `xml.etree.ElementTree` / `lxml`
* `xslt_transformer.py` — Implementation for XML to HTML transformation & metadata loading


* `ui/` — Presentation layer (PyQt6)
* `__init__.py`
* `main_window.py` — Main application window





### Architectural Rules:

* **Strategy Design Pattern:** Must be implemented to dynamically switch between XML parsing algorithms (SAX, DOM, ElementTree/XPath). A context class (e.g., `XmlSearchContext`) must accept an instance of the abstract strategy interface and allow runtime switching from the UI.
* **No "Magic Pushbutton" Anti-Pattern:** The UI layer (`MainWindow` in `src/ui/`) must **only** handle widget rendering, reading user input, and delegating tasks to the context/services. Zero XML parsing, DOM/SAX traversal, or XSLT logic is allowed inside `src/ui/`.
* **Clean Module Exports:** Every `__init__.py` must re-export its module's public classes so imports across the codebase remain clean (e.g., `from src.models import ArchiveMaterial, SearchCriteria`).

## 3. Input Data Requirements (`data/`)

### A. `data/archive.xml` (Domain: "Електронний архів факультету")

* **Language:** Sample data content inside XML should be in Ukrainian.
* **Hierarchy:** At least a 2-level nested XML structure (e.g., `<FacultyArchive>` -> `<Material ...>` -> nested child tags such as `<Title>`, `<Author>`, `<Department>`, `<Volume>`, `<CreatedDate>`, `<Annotation>`).
* **Mandatory Constraint:** The primary searchable nodes (`<Material>`) **must have a varying number of attributes** across different records (e.g., record 1 has `id`, `faculty`, `type`, `year`; record 2 has `id`, `faculty`, `type`, `language`, `access`; record 3 has only `id`, `faculty`, etc.).
* **Content:** 7–10 realistic records containing: Author's full name (П.І.П. автора), material title (назва матеріалу), faculty/department/division (факультет/відділення), chair/sub-department (кафедра), material type (вид матеріалу: стаття, методичка, монографія, диплом), volume in pages (обсяг), and creation date (дата створення).

### B. `data/archive_transform.xsl`

* An XSLT 1.0 stylesheet that transforms `archive.xml` into a clean, well-formatted Ukrainian HTML document (featuring an embedded `<style>` block and a structured HTML table displaying both dynamic attributes and nested elements).

## 4. Functional Requirements

### A. Three XML Parsing & Search Strategies (`src/implementations/`)

1. **SAX API (`SaxSearchStrategy`):** Event-driven stream parsing using `xml.sax.ContentHandler` and `xml.sax.parse()`.
2. **DOM API (`DomSearchStrategy`):** Tree-based parsing using `xml.dom.minidom.parse()` and node/attribute traversal.
3. **ElementTree / Query-Based API (`ElementTreeSearchStrategy`):** Parsing and dynamic query filtering using `xml.etree.ElementTree` (or `lxml.etree` with dynamic XPath generation).

* All three strategies must gracefully handle `<Material>` elements having different sets/counts of attributes without raising `KeyError` or `AttributeError`, returning a list of `@dataclass` models (`ArchiveMaterial`) that preserve a dynamic dictionary of all attributes (`attributes: dict[str, str]`).

### B. Dynamic Data Loading ("Підгрузка даних")

* Whenever the user loads an `.xml` file via the file dialog, the application must automatically scan the file and extract all unique values of at least one key attribute (e.g., `faculty` or `type`) present across `<Material>` nodes.
* A dropdown (`QComboBox`) in the search panel must be dynamically populated with these extracted values (with `"Усі"` as the default first option).

### C. Keyword Search & Dynamic Query Filtering

* Support case-insensitive substring search by keyword (`QLineEdit`) across all nested text fields and attributes of `<Material>`, combined with filtering by the attribute value selected in the `QComboBox`.

### D. HTML Transformation

* Transform the currently selected `.xml` file using the selected `.xsl` stylesheet via `lxml.etree.XSLT`, save the output to an `.html` file, and notify the user in Ukrainian of the saved file path (optionally offering to open it in the default web browser via `webbrowser`).

## 5. User Interface Requirements (PyQt6 — Strictly in Ukrainian)

All visible UI text must be in Ukrainian:

1. **Window Title:** e.g., `"Електронний архів факультету — Обробка XML"`.
2. **File Selection:** Buttons (`QFileDialog.getOpenFileName`) to load input `.xml` (`"Обрати XML-файл"`) and `.xsl` (`"Обрати XSL-файл"`) files, displaying the currently selected file paths.
3. **Strategy Selector:** Radio buttons (`QRadioButton`) or a selector (`QComboBox`) labeled `"Метод аналізу XML:"` with options:
* `SAX API`
* `DOM API`
* `LINQ to XML (ElementTree)`


4. **Search Controls:**
* Keyword input field (`QLineEdit`) with placeholder `"Введіть ключове слово..."`.
* Attribute filter dropdown (`QComboBox`) **dynamically populated** upon loading an XML file (default item: `"Усі"`).
* Search button (`QPushButton`) labeled `"Пошук"`.


5. **Clear Button:** Button labeled `"Очистити (Clear)"` that clears the output display area, clears the keyword input field, and resets the attribute filter dropdown back to `"Усі"`.
6. **Transform to HTML Button:** Button labeled `"Трансформувати в HTML"` that triggers the XSL transformation and saves the resulting HTML document.
7. **Results Output Area:** A read-only `QTextEdit` or `QTableWidget` clearly displaying in Ukrainian all matching records, including all their dynamic attributes and nested tag values (or a message `"За вашим запитом нічого не знайдено."` if empty).
8. **Exit Confirmation Dialog:** Override `closeEvent(self, event)` in `MainWindow` (and connect an `"Вихід"` button if present) to display a `QMessageBox.question` dialog with title `"Підтвердження виходу"`, message `"Чи дійсно ви хочете завершити роботу з програмою?"`, and Ukrainian buttons **"Так"** and **"Ні"**. If **"Ні"** is chosen, call `event.ignore()`.

## 6. Execution Plan for the Agent

1. Initialize the project using `uv init` and install dependencies via `uv add PyQt6 lxml`.
2. Create the package directory structure (`src/models`, `src/interfaces`, `src/implementations`, `src/ui`) with properly configured `__init__.py` files.
3. Generate `data/archive.xml` (ensuring varying attribute counts on `<Material>` nodes and Ukrainian content) and `data/archive_transform.xsl`.
4. Implement the `@dataclass` models, `abc.ABC` interfaces, the 3 XML search strategies, the strategy context, and the XSLT transformer.
5. Build the PyQt6 `MainWindow` with full Ukrainian localization, strictly adhering to separation of concerns (no business logic in UI).
6. Verify the application runs cleanly with `uv run python -m src.main`.