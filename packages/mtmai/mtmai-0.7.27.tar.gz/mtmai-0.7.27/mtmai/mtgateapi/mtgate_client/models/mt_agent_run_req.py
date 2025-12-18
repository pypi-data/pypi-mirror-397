from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="MtAgentRunReq")


@_attrs_define
class MtAgentRunReq:
    """
    Attributes:
        messages (list[Any]):
        agent_name (str | Unset):  Default: 'assistant'.
        session_id (str | Unset):
        state_delta (Any | Unset):
        streaming (bool | Unset):  Default: False.
        user_id (str | Unset):
    """

    messages: list[Any]
    agent_name: str | Unset = "assistant"
    session_id: str | Unset = UNSET
    state_delta: Any | Unset = UNSET
    streaming: bool | Unset = False
    user_id: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        messages = self.messages

        agent_name = self.agent_name

        session_id = self.session_id

        state_delta = self.state_delta

        streaming = self.streaming

        user_id = self.user_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "messages": messages,
            }
        )
        if agent_name is not UNSET:
            field_dict["agentName"] = agent_name
        if session_id is not UNSET:
            field_dict["sessionId"] = session_id
        if state_delta is not UNSET:
            field_dict["stateDelta"] = state_delta
        if streaming is not UNSET:
            field_dict["streaming"] = streaming
        if user_id is not UNSET:
            field_dict["userId"] = user_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        messages = cast(list[Any], d.pop("messages"))

        agent_name = d.pop("agentName", UNSET)

        session_id = d.pop("sessionId", UNSET)

        state_delta = d.pop("stateDelta", UNSET)

        streaming = d.pop("streaming", UNSET)

        user_id = d.pop("userId", UNSET)

        mt_agent_run_req = cls(
            messages=messages,
            agent_name=agent_name,
            session_id=session_id,
            state_delta=state_delta,
            streaming=streaming,
            user_id=user_id,
        )

        mt_agent_run_req.additional_properties = d
        return mt_agent_run_req

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
