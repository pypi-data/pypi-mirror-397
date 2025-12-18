from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

T = TypeVar("T", bound="ChatMessage")


@_attrs_define
class ChatMessage:
    """
    Attributes:
        id (str):
        created_at (datetime.datetime):
        updated_at (datetime.datetime):
        chat_id (str):
        role (str):
        parts (Any):
        attachments (Any):
        user_id (str):
    """

    id: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    chat_id: str
    role: str
    parts: Any
    attachments: Any
    user_id: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        chat_id = self.chat_id

        role = self.role

        parts = self.parts

        attachments = self.attachments

        user_id = self.user_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "created_at": created_at,
                "updated_at": updated_at,
                "chat_id": chat_id,
                "role": role,
                "parts": parts,
                "attachments": attachments,
                "user_id": user_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        created_at = isoparse(d.pop("created_at"))

        updated_at = isoparse(d.pop("updated_at"))

        chat_id = d.pop("chat_id")

        role = d.pop("role")

        parts = d.pop("parts")

        attachments = d.pop("attachments")

        user_id = d.pop("user_id")

        chat_message = cls(
            id=id,
            created_at=created_at,
            updated_at=updated_at,
            chat_id=chat_id,
            role=role,
            parts=parts,
            attachments=attachments,
            user_id=user_id,
        )

        chat_message.additional_properties = d
        return chat_message

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
