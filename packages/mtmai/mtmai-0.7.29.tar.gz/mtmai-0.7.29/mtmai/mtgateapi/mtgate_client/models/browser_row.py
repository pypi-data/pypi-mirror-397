from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="BrowserRow")


@_attrs_define
class BrowserRow:
    """
    Attributes:
        id (str):
        created_at (str):
        updated_at (str):
        title (str | Unset):
        description (str | Unset):
        profile_id (str | Unset):
        provider (str | Unset):
        provider_config (Any | Unset):
        config (Any | Unset):
        sandbox_id (str | Unset):
        vnc_url (str | Unset):
        worker_name (str | Unset):
        is_running (bool | Unset):
    """

    id: str
    created_at: str
    updated_at: str
    title: str | Unset = UNSET
    description: str | Unset = UNSET
    profile_id: str | Unset = UNSET
    provider: str | Unset = UNSET
    provider_config: Any | Unset = UNSET
    config: Any | Unset = UNSET
    sandbox_id: str | Unset = UNSET
    vnc_url: str | Unset = UNSET
    worker_name: str | Unset = UNSET
    is_running: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        created_at = self.created_at

        updated_at = self.updated_at

        title = self.title

        description = self.description

        profile_id = self.profile_id

        provider = self.provider

        provider_config = self.provider_config

        config = self.config

        sandbox_id = self.sandbox_id

        vnc_url = self.vnc_url

        worker_name = self.worker_name

        is_running = self.is_running

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "created_at": created_at,
                "updated_at": updated_at,
            }
        )
        if title is not UNSET:
            field_dict["title"] = title
        if description is not UNSET:
            field_dict["description"] = description
        if profile_id is not UNSET:
            field_dict["profile_id"] = profile_id
        if provider is not UNSET:
            field_dict["provider"] = provider
        if provider_config is not UNSET:
            field_dict["provider_config"] = provider_config
        if config is not UNSET:
            field_dict["config"] = config
        if sandbox_id is not UNSET:
            field_dict["sandbox_id"] = sandbox_id
        if vnc_url is not UNSET:
            field_dict["vnc_url"] = vnc_url
        if worker_name is not UNSET:
            field_dict["worker_name"] = worker_name
        if is_running is not UNSET:
            field_dict["is_running"] = is_running

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        created_at = d.pop("created_at")

        updated_at = d.pop("updated_at")

        title = d.pop("title", UNSET)

        description = d.pop("description", UNSET)

        profile_id = d.pop("profile_id", UNSET)

        provider = d.pop("provider", UNSET)

        provider_config = d.pop("provider_config", UNSET)

        config = d.pop("config", UNSET)

        sandbox_id = d.pop("sandbox_id", UNSET)

        vnc_url = d.pop("vnc_url", UNSET)

        worker_name = d.pop("worker_name", UNSET)

        is_running = d.pop("is_running", UNSET)

        browser_row = cls(
            id=id,
            created_at=created_at,
            updated_at=updated_at,
            title=title,
            description=description,
            profile_id=profile_id,
            provider=provider,
            provider_config=provider_config,
            config=config,
            sandbox_id=sandbox_id,
            vnc_url=vnc_url,
            worker_name=worker_name,
            is_running=is_running,
        )

        browser_row.additional_properties = d
        return browser_row

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
