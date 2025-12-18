from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.agent_chat_item import AgentChatItem
    from ..models.agent_chat_list_response_200_paginate import AgentChatListResponse200Paginate


T = TypeVar("T", bound="AgentChatListResponse200")


@_attrs_define
class AgentChatListResponse200:
    """
    Attributes:
        paginate (AgentChatListResponse200Paginate):
        data (list[AgentChatItem]):
    """

    paginate: AgentChatListResponse200Paginate
    data: list[AgentChatItem]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        paginate = self.paginate.to_dict()

        data = []
        for data_item_data in self.data:
            data_item = data_item_data.to_dict()
            data.append(data_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "paginate": paginate,
                "data": data,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.agent_chat_item import AgentChatItem
        from ..models.agent_chat_list_response_200_paginate import AgentChatListResponse200Paginate

        d = dict(src_dict)
        paginate = AgentChatListResponse200Paginate.from_dict(d.pop("paginate"))

        data = []
        _data = d.pop("data")
        for data_item_data in _data:
            data_item = AgentChatItem.from_dict(data_item_data)

            data.append(data_item)

        agent_chat_list_response_200 = cls(
            paginate=paginate,
            data=data,
        )

        agent_chat_list_response_200.additional_properties = d
        return agent_chat_list_response_200

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
