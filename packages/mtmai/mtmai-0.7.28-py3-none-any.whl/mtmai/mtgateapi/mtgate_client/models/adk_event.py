from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.adk_event_actions import AdkEventActions
    from ..models.genai_content import GenaiContent


T = TypeVar("T", bound="AdkEvent")


@_attrs_define
class AdkEvent:
    """
    Attributes:
        id (str | Unset):
        author (str | Unset):
        invocation_id (str | Unset):
        actions (AdkEventActions | Unset):
        long_running_tool_ids (list[str] | Unset):
        branch (str | Unset):
        timestamp (float | Unset):
        content (GenaiContent | Unset):
        error (str | Unset):
        error_message (str | Unset):
        error_code (str | Unset):
        grounding_metadata (Any | Unset):
        usage_metadata (Any | Unset):
        citation_metadata (Any | Unset):
        custom_metadata (Any | Unset):
        turn_complete (bool | Unset):
        interrupted (bool | Unset):
    """

    id: str | Unset = UNSET
    author: str | Unset = UNSET
    invocation_id: str | Unset = UNSET
    actions: AdkEventActions | Unset = UNSET
    long_running_tool_ids: list[str] | Unset = UNSET
    branch: str | Unset = UNSET
    timestamp: float | Unset = UNSET
    content: GenaiContent | Unset = UNSET
    error: str | Unset = UNSET
    error_message: str | Unset = UNSET
    error_code: str | Unset = UNSET
    grounding_metadata: Any | Unset = UNSET
    usage_metadata: Any | Unset = UNSET
    citation_metadata: Any | Unset = UNSET
    custom_metadata: Any | Unset = UNSET
    turn_complete: bool | Unset = UNSET
    interrupted: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        author = self.author

        invocation_id = self.invocation_id

        actions: dict[str, Any] | Unset = UNSET
        if not isinstance(self.actions, Unset):
            actions = self.actions.to_dict()

        long_running_tool_ids: list[str] | Unset = UNSET
        if not isinstance(self.long_running_tool_ids, Unset):
            long_running_tool_ids = self.long_running_tool_ids

        branch = self.branch

        timestamp = self.timestamp

        content: dict[str, Any] | Unset = UNSET
        if not isinstance(self.content, Unset):
            content = self.content.to_dict()

        error = self.error

        error_message = self.error_message

        error_code = self.error_code

        grounding_metadata = self.grounding_metadata

        usage_metadata = self.usage_metadata

        citation_metadata = self.citation_metadata

        custom_metadata = self.custom_metadata

        turn_complete = self.turn_complete

        interrupted = self.interrupted

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if author is not UNSET:
            field_dict["author"] = author
        if invocation_id is not UNSET:
            field_dict["invocationId"] = invocation_id
        if actions is not UNSET:
            field_dict["actions"] = actions
        if long_running_tool_ids is not UNSET:
            field_dict["longRunningToolIds"] = long_running_tool_ids
        if branch is not UNSET:
            field_dict["branch"] = branch
        if timestamp is not UNSET:
            field_dict["timestamp"] = timestamp
        if content is not UNSET:
            field_dict["content"] = content
        if error is not UNSET:
            field_dict["error"] = error
        if error_message is not UNSET:
            field_dict["errorMessage"] = error_message
        if error_code is not UNSET:
            field_dict["errorCode"] = error_code
        if grounding_metadata is not UNSET:
            field_dict["groundingMetadata"] = grounding_metadata
        if usage_metadata is not UNSET:
            field_dict["usageMetadata"] = usage_metadata
        if citation_metadata is not UNSET:
            field_dict["citationMetadata"] = citation_metadata
        if custom_metadata is not UNSET:
            field_dict["customMetadata"] = custom_metadata
        if turn_complete is not UNSET:
            field_dict["turnComplete"] = turn_complete
        if interrupted is not UNSET:
            field_dict["interrupted"] = interrupted

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.adk_event_actions import AdkEventActions
        from ..models.genai_content import GenaiContent

        d = dict(src_dict)
        id = d.pop("id", UNSET)

        author = d.pop("author", UNSET)

        invocation_id = d.pop("invocationId", UNSET)

        _actions = d.pop("actions", UNSET)
        actions: AdkEventActions | Unset
        if isinstance(_actions, Unset):
            actions = UNSET
        else:
            actions = AdkEventActions.from_dict(_actions)

        long_running_tool_ids = cast(list[str], d.pop("longRunningToolIds", UNSET))

        branch = d.pop("branch", UNSET)

        timestamp = d.pop("timestamp", UNSET)

        _content = d.pop("content", UNSET)
        content: GenaiContent | Unset
        if isinstance(_content, Unset):
            content = UNSET
        else:
            content = GenaiContent.from_dict(_content)

        error = d.pop("error", UNSET)

        error_message = d.pop("errorMessage", UNSET)

        error_code = d.pop("errorCode", UNSET)

        grounding_metadata = d.pop("groundingMetadata", UNSET)

        usage_metadata = d.pop("usageMetadata", UNSET)

        citation_metadata = d.pop("citationMetadata", UNSET)

        custom_metadata = d.pop("customMetadata", UNSET)

        turn_complete = d.pop("turnComplete", UNSET)

        interrupted = d.pop("interrupted", UNSET)

        adk_event = cls(
            id=id,
            author=author,
            invocation_id=invocation_id,
            actions=actions,
            long_running_tool_ids=long_running_tool_ids,
            branch=branch,
            timestamp=timestamp,
            content=content,
            error=error,
            error_message=error_message,
            error_code=error_code,
            grounding_metadata=grounding_metadata,
            usage_metadata=usage_metadata,
            citation_metadata=citation_metadata,
            custom_metadata=custom_metadata,
            turn_complete=turn_complete,
            interrupted=interrupted,
        )

        adk_event.additional_properties = d
        return adk_event

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
