from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="AgentChatItem")


@_attrs_define
class AgentChatItem:
    """
    Attributes:
        id (str):
        title (str):
        user_id (str):
        visibility (str):
        created_at (datetime.datetime):
        updated_at (datetime.datetime):
        last_context (Any | Unset):
    """

    id: str
    title: str
    user_id: str
    visibility: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    last_context: Any | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        title = self.title

        user_id = self.user_id

        visibility = self.visibility

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        last_context = self.last_context

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "title": title,
                "user_id": user_id,
                "visibility": visibility,
                "created_at": created_at,
                "updated_at": updated_at,
            }
        )
        if last_context is not UNSET:
            field_dict["lastContext"] = last_context

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        title = d.pop("title")

        user_id = d.pop("user_id")

        visibility = d.pop("visibility")

        created_at = isoparse(d.pop("created_at"))

        updated_at = isoparse(d.pop("updated_at"))

        last_context = d.pop("lastContext", UNSET)

        agent_chat_item = cls(
            id=id,
            title=title,
            user_id=user_id,
            visibility=visibility,
            created_at=created_at,
            updated_at=updated_at,
            last_context=last_context,
        )

        agent_chat_item.additional_properties = d
        return agent_chat_item

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
