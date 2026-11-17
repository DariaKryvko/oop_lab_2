import xml.sax
from xml.sax.handler import ContentHandler
from typing import Optional
from src.interfaces import XmlSearchStrategy
from src.models import ArchiveMaterial, SearchCriteria


class _ArchiveSaxHandler(ContentHandler):
    """SAX content handler that processes XML records in a streaming fashion."""

    def __init__(self, criteria: SearchCriteria) -> None:
        super().__init__()
        self.criteria = criteria
        self.materials: list[ArchiveMaterial] = []
        self._current_material: Optional[ArchiveMaterial] = None
        self._current_tag: str = ""
        self._buffer: list[str] = []

    def startElement(self, name: str, attrs) -> None:
        if name == "Material":
            attr_dict = {key: attrs.getValue(key) for key in attrs.getNames()}
            self._current_material = ArchiveMaterial(
                id=attr_dict.get("id", ""),
                material_type=attr_dict.get("type", ""),
                attributes=attr_dict,
            )
        elif self._current_material is not None:
            self._current_tag = name
            self._buffer = []

    def characters(self, content: str) -> None:
        if self._current_material is not None and self._current_tag:
            self._buffer.append(content)

    def endElement(self, name: str) -> None:
        if name == "Material" and self._current_material is not None:
            if self._current_material.matches(self.criteria):
                self.materials.append(self._current_material)
            self._current_material = None
        elif self._current_material is not None and self._current_tag:
            text = "".join(self._buffer).strip()
            if self._current_tag == "Title":
                self._current_material.title = text
            elif self._current_tag == "Author":
                self._current_material.author = text
            elif self._current_tag == "Department":
                self._current_material.department = text
            elif self._current_tag == "Chair":
                self._current_material.chair = text
            elif self._current_tag == "Volume":
                self._current_material.volume = text
            elif self._current_tag == "CreatedDate":
                self._current_material.created_date = text
            elif self._current_tag == "Annotation":
                self._current_material.annotation = text
            elif self._current_tag == "Keywords":
                self._current_material.keywords = text
            self._current_tag = ""
            self._buffer = []


class SaxSearchStrategy(XmlSearchStrategy):
    """XML search strategy using the event-driven SAX API."""

    @property
    def name(self) -> str:
        return "SAX API"

    def search(self, xml_path: str, criteria: SearchCriteria) -> list[ArchiveMaterial]:
        handler = _ArchiveSaxHandler(criteria)
        parser = xml.sax.make_parser()
        parser.setFeature(xml.sax.handler.feature_namespaces, False)
        parser.setContentHandler(handler)
        with open(xml_path, "r", encoding="utf-8") as f:
            parser.parse(f)
        return handler.materials
