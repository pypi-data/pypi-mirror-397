from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.adk_function_call import AdkFunctionCall
    from ..models.adk_function_resp import AdkFunctionResp


T = TypeVar("T", bound="AdkEventActions")


@_attrs_define
class AdkEventActions:
    """
    Attributes:
        message (str | Unset):
        artifact_delta (Any | Unset):
        function_call (AdkFunctionCall | Unset):
        function_response (AdkFunctionResp | Unset):
        finish_reason (str | Unset):
    """

    message: str | Unset = UNSET
    artifact_delta: Any | Unset = UNSET
    function_call: AdkFunctionCall | Unset = UNSET
    function_response: AdkFunctionResp | Unset = UNSET
    finish_reason: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        message = self.message

        artifact_delta = self.artifact_delta

        function_call: dict[str, Any] | Unset = UNSET
        if not isinstance(self.function_call, Unset):
            function_call = self.function_call.to_dict()

        function_response: dict[str, Any] | Unset = UNSET
        if not isinstance(self.function_response, Unset):
            function_response = self.function_response.to_dict()

        finish_reason = self.finish_reason

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if message is not UNSET:
            field_dict["message"] = message
        if artifact_delta is not UNSET:
            field_dict["artifactDelta"] = artifact_delta
        if function_call is not UNSET:
            field_dict["functionCall"] = function_call
        if function_response is not UNSET:
            field_dict["functionResponse"] = function_response
        if finish_reason is not UNSET:
            field_dict["finishReason"] = finish_reason

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.adk_function_call import AdkFunctionCall
        from ..models.adk_function_resp import AdkFunctionResp

        d = dict(src_dict)
        message = d.pop("message", UNSET)

        artifact_delta = d.pop("artifactDelta", UNSET)

        _function_call = d.pop("functionCall", UNSET)
        function_call: AdkFunctionCall | Unset
        if isinstance(_function_call, Unset):
            function_call = UNSET
        else:
            function_call = AdkFunctionCall.from_dict(_function_call)

        _function_response = d.pop("functionResponse", UNSET)
        function_response: AdkFunctionResp | Unset
        if isinstance(_function_response, Unset):
            function_response = UNSET
        else:
            function_response = AdkFunctionResp.from_dict(_function_response)

        finish_reason = d.pop("finishReason", UNSET)

        adk_event_actions = cls(
            message=message,
            artifact_delta=artifact_delta,
            function_call=function_call,
            function_response=function_response,
            finish_reason=finish_reason,
        )

        adk_event_actions.additional_properties = d
        return adk_event_actions

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
