from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.adk_part import AdkPart


T = TypeVar("T", bound="GenaiContent")


@_attrs_define
class GenaiContent:
    """
    Attributes:
        role (str):
        parts (list[AdkPart]):
    """

    role: str
    parts: list[AdkPart]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        role = self.role

        parts = []
        for parts_item_data in self.parts:
            parts_item = parts_item_data.to_dict()
            parts.append(parts_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "role": role,
                "parts": parts,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.adk_part import AdkPart

        d = dict(src_dict)
        role = d.pop("role")

        parts = []
        _parts = d.pop("parts")
        for parts_item_data in _parts:
            parts_item = AdkPart.from_dict(parts_item_data)

            parts.append(parts_item)

        genai_content = cls(
            role=role,
            parts=parts,
        )

        genai_content.additional_properties = d
        return genai_content

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
