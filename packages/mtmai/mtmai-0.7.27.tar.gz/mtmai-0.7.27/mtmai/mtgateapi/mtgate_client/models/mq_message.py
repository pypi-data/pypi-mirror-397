from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="MqMessage")


@_attrs_define
class MqMessage:
    """
    Attributes:
        msg_id (float):
        read_ct (float):
        message (Any):
        enqueued_at (str | Unset):
    """

    msg_id: float
    read_ct: float
    message: Any
    enqueued_at: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        msg_id = self.msg_id

        read_ct = self.read_ct

        message = self.message

        enqueued_at = self.enqueued_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "msg_id": msg_id,
                "read_ct": read_ct,
                "message": message,
            }
        )
        if enqueued_at is not UNSET:
            field_dict["enqueued_at"] = enqueued_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        msg_id = d.pop("msg_id")

        read_ct = d.pop("read_ct")

        message = d.pop("message")

        enqueued_at = d.pop("enqueued_at", UNSET)

        mq_message = cls(
            msg_id=msg_id,
            read_ct=read_ct,
            message=message,
            enqueued_at=enqueued_at,
        )

        mq_message.additional_properties = d
        return mq_message

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
