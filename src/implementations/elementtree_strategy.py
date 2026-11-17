import xml.etree.ElementTree as ET
from src.interfaces import XmlSearchStrategy
from src.models import ArchiveMaterial, SearchCriteria


class ElementTreeSearchStrategy(XmlSearchStrategy):
    """XML search strategy using the object-tree / LINQ to XML-like ElementTree API."""

    @property
    def name(self) -> str:
        return "LINQ to XML (ElementTree)"

    def search(self, xml_path: str, criteria: SearchCriteria) -> list[ArchiveMaterial]:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        materials: list[ArchiveMaterial] = []

        for elem in root.findall(".//Material"):
            attr_dict = dict(elem.attrib)

            def get_text(tag_name: str) -> str:
                child = elem.find(tag_name)
                return (child.text or "").strip() if child is not None else ""

            material = ArchiveMaterial(
                id=attr_dict.get("id", ""),
                material_type=attr_dict.get("type", ""),
                title=get_text("Title"),
                author=get_text("Author"),
                department=get_text("Department"),
                chair=get_text("Chair"),
                volume=get_text("Volume"),
                created_date=get_text("CreatedDate"),
                annotation=get_text("Annotation"),
                keywords=get_text("Keywords"),
                attributes=attr_dict,
            )

            if material.matches(criteria):
                materials.append(material)

        return materials
