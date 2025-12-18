from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.genai_content import GenaiContent


T = TypeVar("T", bound="AgentRunReq")


@_attrs_define
class AgentRunReq:
    """
    Attributes:
        agent_name (str):
        new_message (GenaiContent):
        session_id (str):
        state_delta (Any | Unset):
        streaming (bool | Unset):  Default: False.
        user_id (str | Unset):
    """

    agent_name: str
    new_message: GenaiContent
    session_id: str
    state_delta: Any | Unset = UNSET
    streaming: bool | Unset = False
    user_id: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        agent_name = self.agent_name

        new_message = self.new_message.to_dict()

        session_id = self.session_id

        state_delta = self.state_delta

        streaming = self.streaming

        user_id = self.user_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "agentName": agent_name,
                "newMessage": new_message,
                "sessionId": session_id,
            }
        )
        if state_delta is not UNSET:
            field_dict["stateDelta"] = state_delta
        if streaming is not UNSET:
            field_dict["streaming"] = streaming
        if user_id is not UNSET:
            field_dict["userId"] = user_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.genai_content import GenaiContent

        d = dict(src_dict)
        agent_name = d.pop("agentName")

        new_message = GenaiContent.from_dict(d.pop("newMessage"))

        session_id = d.pop("sessionId")

        state_delta = d.pop("stateDelta", UNSET)

        streaming = d.pop("streaming", UNSET)

        user_id = d.pop("userId", UNSET)

        agent_run_req = cls(
            agent_name=agent_name,
            new_message=new_message,
            session_id=session_id,
            state_delta=state_delta,
            streaming=streaming,
            user_id=user_id,
        )

        agent_run_req.additional_properties = d
        return agent_run_req

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
