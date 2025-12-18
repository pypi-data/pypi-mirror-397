from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="BrowserCreateReq")


@_attrs_define
class BrowserCreateReq:
    """
    Attributes:
        title (str): 配置名称
        id (str | Unset): 如果不传则自动生成，传入则更新对应记录
        description (str | Unset): 描述信息
        profile_id (str | Unset): 关联的 profile ID
        provider (str | Unset): 底层提供商,如 nst
        provider_config (Any | Unset): 提供商特定配置
        config (Any | Unset): 通用配置
    """

    title: str
    id: str | Unset = UNSET
    description: str | Unset = UNSET
    profile_id: str | Unset = UNSET
    provider: str | Unset = UNSET
    provider_config: Any | Unset = UNSET
    config: Any | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        title = self.title

        id = self.id

        description = self.description

        profile_id = self.profile_id

        provider = self.provider

        provider_config = self.provider_config

        config = self.config

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "title": title,
            }
        )
        if id is not UNSET:
            field_dict["id"] = id
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

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        title = d.pop("title")

        id = d.pop("id", UNSET)

        description = d.pop("description", UNSET)

        profile_id = d.pop("profile_id", UNSET)

        provider = d.pop("provider", UNSET)

        provider_config = d.pop("provider_config", UNSET)

        config = d.pop("config", UNSET)

        browser_create_req = cls(
            title=title,
            id=id,
            description=description,
            profile_id=profile_id,
            provider=provider,
            provider_config=provider_config,
            config=config,
        )

        browser_create_req.additional_properties = d
        return browser_create_req

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
