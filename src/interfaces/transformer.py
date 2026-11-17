from abc import ABC, abstractmethod


class XmlTransformer(ABC):
    """Abstract base class for XSLT transformation and XML attribute extraction."""

    @abstractmethod
    def transform_to_html(self, xml_path: str, xsl_path: str, output_html_path: str) -> str:
        """
        Transform an XML file using an XSL stylesheet and save the result to an HTML file.

        :param xml_path: Path to the source XML document.
        :param xsl_path: Path to the XSL stylesheet.
        :param output_html_path: Destination path for the resulting HTML document.
        :return: Absolute path to the saved HTML file.
        """
        pass

    @abstractmethod
    def extract_attribute_values(self, xml_path: str, attribute_name: str) -> list[str]:
        """
        Extract unique values of the specified attribute from searchable nodes in the XML document.

        :param xml_path: Path to the source XML document.
        :param attribute_name: Name of the attribute to extract (e.g. 'type' or 'faculty').
        :return: Sorted list of unique attribute values.
        """
        pass
