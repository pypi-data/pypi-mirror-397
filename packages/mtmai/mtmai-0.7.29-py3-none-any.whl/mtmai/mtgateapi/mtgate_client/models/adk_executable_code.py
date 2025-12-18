from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.adk_executable_code_language import AdkExecutableCodeLanguage

T = TypeVar("T", bound="AdkExecutableCode")


@_attrs_define
class AdkExecutableCode:
    """
    Attributes:
        language (AdkExecutableCodeLanguage):
        code (str):
    """

    language: AdkExecutableCodeLanguage
    code: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        language = self.language.value

        code = self.code

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "language": language,
                "code": code,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        language = AdkExecutableCodeLanguage(d.pop("language"))

        code = d.pop("code")

        adk_executable_code = cls(
            language=language,
            code=code,
        )

        adk_executable_code.additional_properties = d
        return adk_executable_code

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
