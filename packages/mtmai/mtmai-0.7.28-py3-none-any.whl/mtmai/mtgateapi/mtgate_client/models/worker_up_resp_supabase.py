from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="WorkerUpRespSupabase")


@_attrs_define
class WorkerUpRespSupabase:
    """
    Attributes:
        sb_user_name (str):
        sb_password (str):
        sb_url (str):
        sb_public_key (str):
    """

    sb_user_name: str
    sb_password: str
    sb_url: str
    sb_public_key: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        sb_user_name = self.sb_user_name

        sb_password = self.sb_password

        sb_url = self.sb_url

        sb_public_key = self.sb_public_key

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "sbUserName": sb_user_name,
                "sbPassword": sb_password,
                "sbUrl": sb_url,
                "sbPublicKey": sb_public_key,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        sb_user_name = d.pop("sbUserName")

        sb_password = d.pop("sbPassword")

        sb_url = d.pop("sbUrl")

        sb_public_key = d.pop("sbPublicKey")

        worker_up_resp_supabase = cls(
            sb_user_name=sb_user_name,
            sb_password=sb_password,
            sb_url=sb_url,
            sb_public_key=sb_public_key,
        )

        worker_up_resp_supabase.additional_properties = d
        return worker_up_resp_supabase

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
