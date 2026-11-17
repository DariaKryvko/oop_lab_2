from abc import ABC, abstractmethod
from typing import Optional
from src.models import ArchiveMaterial, SearchCriteria


class XmlSearchStrategy(ABC):
    """Abstract base class defining the search strategy for XML documents."""

    @abstractmethod
    def search(self, xml_path: str, criteria: SearchCriteria) -> list[ArchiveMaterial]:
        """
        Parse and filter records in the given XML document according to criteria.
        
        :param xml_path: Path to the XML file.
        :param criteria: Search and filter criteria.
        :return: List of matching ArchiveMaterial objects.
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the human-readable Ukrainian name of the strategy."""
        pass


class XmlSearchContext:
    """Context class in the Strategy pattern allowing runtime algorithm switching."""

    def __init__(self, strategy: Optional[XmlSearchStrategy] = None) -> None:
        self._strategy = strategy

    @property
    def strategy(self) -> Optional[XmlSearchStrategy]:
        return self._strategy

    @strategy.setter
    def strategy(self, strategy: XmlSearchStrategy) -> None:
        self._strategy = strategy

    def execute_search(self, xml_path: str, criteria: SearchCriteria) -> list[ArchiveMaterial]:
        if not self._strategy:
            raise ValueError("Стратегію аналізу XML не встановлено.")
        return self._strategy.search(xml_path, criteria)
