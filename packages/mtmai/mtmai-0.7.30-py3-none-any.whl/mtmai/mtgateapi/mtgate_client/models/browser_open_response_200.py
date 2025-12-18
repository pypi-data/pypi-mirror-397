from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="BrowserOpenResponse200")


@_attrs_define
class BrowserOpenResponse200:
    """
    Attributes:
        vnc_url (str | Unset): vnc url
        ws_cdp_endpoint (str | Unset):
    """

    vnc_url: str | Unset = UNSET
    ws_cdp_endpoint: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        vnc_url = self.vnc_url

        ws_cdp_endpoint = self.ws_cdp_endpoint

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if vnc_url is not UNSET:
            field_dict["vncUrl"] = vnc_url
        if ws_cdp_endpoint is not UNSET:
            field_dict["wsCdpEndpoint"] = ws_cdp_endpoint

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        vnc_url = d.pop("vncUrl", UNSET)

        ws_cdp_endpoint = d.pop("wsCdpEndpoint", UNSET)

        browser_open_response_200 = cls(
            vnc_url=vnc_url,
            ws_cdp_endpoint=ws_cdp_endpoint,
        )

        browser_open_response_200.additional_properties = d
        return browser_open_response_200

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
