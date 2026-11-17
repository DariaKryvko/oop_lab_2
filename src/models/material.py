from dataclasses import dataclass, field
from typing import Dict, Any, Optional


@dataclass
class SearchCriteria:
    """Represents search and filtering criteria for archive materials."""
    keyword: str = ""
    attribute_name: str = ""
    attribute_value: str = ""

    def is_empty(self) -> bool:
        has_kw = bool(self.keyword and self.keyword.strip())
        has_attr = bool(
            self.attribute_value 
            and self.attribute_value.strip() 
            and self.attribute_value.strip() != "Усі"
        )
        return not has_kw and not has_attr


@dataclass
class ArchiveMaterial:
    """Represents a record of an academic or educational material."""
    id: str = ""
    title: str = ""
    author: str = ""
    department: str = ""
    chair: str = ""
    material_type: str = ""
    volume: str = ""
    created_date: str = ""
    annotation: str = ""
    keywords: str = ""
    attributes: dict[str, str] = field(default_factory=dict)

    def matches(self, criteria: SearchCriteria) -> bool:
        """Check if this material satisfies the given search criteria."""
        if criteria.is_empty():
            return True

        # Check attribute filter
        attr_val = criteria.attribute_value.strip() if criteria.attribute_value else ""
        if attr_val and attr_val != "Усі":
            attr_name = criteria.attribute_name.strip() if criteria.attribute_name else ""
            if attr_name:
                val = self.attributes.get(attr_name, "")
                if val.casefold() != attr_val.casefold():
                    return False
            else:
                # If no specific attribute name, check any attribute value
                matches_any = any(
                    v.casefold() == attr_val.casefold()
                    for v in self.attributes.values()
                )
                if not matches_any:
                    return False

        # Check keyword search
        kw = criteria.keyword.strip().casefold() if criteria.keyword else ""
        if kw:
            # Check all text fields
            field_values = [
                self.id,
                self.title,
                self.author,
                self.department,
                self.chair,
                self.material_type,
                self.volume,
                self.created_date,
                self.annotation,
                self.keywords,
            ]
            # Check attributes keys and values
            for k, v in self.attributes.items():
                field_values.append(k)
                field_values.append(v)

            found = any(kw in field_val.casefold() for field_val in field_values)
            if not found:
                return False

        return True
