from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="WorkerUpRequest")


@_attrs_define
class WorkerUpRequest:
    """WorkerUpRequest

    Attributes:
        worker_id (str | Unset):
        bot_type (str | Unset):  Default: 'mainapi'.
    """

    worker_id: str | Unset = UNSET
    bot_type: str | Unset = "mainapi"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        worker_id = self.worker_id

        bot_type = self.bot_type

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if worker_id is not UNSET:
            field_dict["workerId"] = worker_id
        if bot_type is not UNSET:
            field_dict["botType"] = bot_type

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        worker_id = d.pop("workerId", UNSET)

        bot_type = d.pop("botType", UNSET)

        worker_up_request = cls(
            worker_id=worker_id,
            bot_type=bot_type,
        )

        worker_up_request.additional_properties = d
        return worker_up_request

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
