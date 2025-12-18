from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="AdkSessionCreateBody")


@_attrs_define
class AdkSessionCreateBody:
    """
    Attributes:
        agent_name (str):
        state (Any | Unset):
        session_id (str | Unset):
        user_id (str | Unset):
    """

    agent_name: str
    state: Any | Unset = UNSET
    session_id: str | Unset = UNSET
    user_id: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        agent_name = self.agent_name

        state = self.state

        session_id = self.session_id

        user_id = self.user_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "agentName": agent_name,
            }
        )
        if state is not UNSET:
            field_dict["state"] = state
        if session_id is not UNSET:
            field_dict["sessionId"] = session_id
        if user_id is not UNSET:
            field_dict["userId"] = user_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        agent_name = d.pop("agentName")

        state = d.pop("state", UNSET)

        session_id = d.pop("sessionId", UNSET)

        user_id = d.pop("userId", UNSET)

        adk_session_create_body = cls(
            agent_name=agent_name,
            state=state,
            session_id=session_id,
            user_id=user_id,
        )

        adk_session_create_body.additional_properties = d
        return adk_session_create_body

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
