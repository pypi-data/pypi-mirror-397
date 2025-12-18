from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="BrowserCreateResult")


@_attrs_define
class BrowserCreateResult:
    """
    Attributes:
        id (str):
        title (str | Unset):
        created_at (str | Unset):
        provider (str | Unset):
    """

    id: str
    title: str | Unset = UNSET
    created_at: str | Unset = UNSET
    provider: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        title = self.title

        created_at = self.created_at

        provider = self.provider

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
            }
        )
        if title is not UNSET:
            field_dict["title"] = title
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if provider is not UNSET:
            field_dict["provider"] = provider

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        title = d.pop("title", UNSET)

        created_at = d.pop("created_at", UNSET)

        provider = d.pop("provider", UNSET)

        browser_create_result = cls(
            id=id,
            title=title,
            created_at=created_at,
            provider=provider,
        )

        browser_create_result.additional_properties = d
        return browser_create_result

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
