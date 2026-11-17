import xml.dom.minidom
from xml.dom import Node
from src.interfaces import XmlSearchStrategy
from src.models import ArchiveMaterial, SearchCriteria


class DomSearchStrategy(XmlSearchStrategy):
    """XML search strategy using the tree-based DOM API."""

    @property
    def name(self) -> str:
        return "DOM API"

    def search(self, xml_path: str, criteria: SearchCriteria) -> list[ArchiveMaterial]:
        doc = xml.dom.minidom.parse(xml_path)
        materials: list[ArchiveMaterial] = []
        try:
            material_nodes = doc.getElementsByTagName("Material")
            for node in material_nodes:
                # Dynamic attribute extraction
                attr_dict: dict[str, str] = {}
                if node.attributes:
                    for i in range(node.attributes.length):
                        attr_item = node.attributes.item(i)
                        if attr_item:
                            attr_dict[attr_item.name] = attr_item.value

                # Child elements text extraction
                child_data: dict[str, str] = {}
                for child in node.childNodes:
                    if child.nodeType == Node.ELEMENT_NODE:
                        text_chunks = [
                            text_node.data
                            for text_node in child.childNodes
                            if text_node.nodeType in (Node.TEXT_NODE, Node.CDATA_SECTION_NODE)
                        ]
                        child_data[child.tagName] = "".join(text_chunks).strip()

                material = ArchiveMaterial(
                    id=attr_dict.get("id", ""),
                    material_type=attr_dict.get("type", ""),
                    title=child_data.get("Title", ""),
                    author=child_data.get("Author", ""),
                    department=child_data.get("Department", ""),
                    chair=child_data.get("Chair", ""),
                    volume=child_data.get("Volume", ""),
                    created_date=child_data.get("CreatedDate", ""),
                    annotation=child_data.get("Annotation", ""),
                    keywords=child_data.get("Keywords", ""),
                    attributes=attr_dict,
                )

                if material.matches(criteria):
                    materials.append(material)
        finally:
            doc.unlink()

        return materials
