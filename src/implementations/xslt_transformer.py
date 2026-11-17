import os
from lxml import etree
from src.interfaces import XmlTransformer


class XsltTransformer(XmlTransformer):
    """XSLT transformation and XML metadata extraction service using lxml."""

    def transform_to_html(self, xml_path: str, xsl_path: str, output_html_path: str) -> str:
        if not os.path.exists(xml_path):
            raise FileNotFoundError(f"Файл XML не знайдено: {xml_path}")
        if not os.path.exists(xsl_path):
            raise FileNotFoundError(f"Файл XSL не знайдено: {xsl_path}")

        xml_tree = etree.parse(xml_path)
        xsl_tree = etree.parse(xsl_path)
        transform = etree.XSLT(xsl_tree)
        result_tree = transform(xml_tree)

        # Ensure target directory exists
        out_dir = os.path.dirname(os.path.abspath(output_html_path))
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)

        with open(output_html_path, "wb") as f:
            f.write(etree.tostring(result_tree, pretty_print=True, method="html", encoding="utf-8"))

        return os.path.abspath(output_html_path)

    def extract_attribute_values(self, xml_path: str, attribute_name: str) -> list[str]:
        if not os.path.exists(xml_path):
            raise FileNotFoundError(f"Файл XML не знайдено: {xml_path}")

        tree = etree.parse(xml_path)
        xpath_query = f"//Material/@{attribute_name}"
        raw_values = tree.xpath(xpath_query)
        unique_values = sorted({str(v).strip() for v in raw_values if str(v).strip()})
        return unique_values
