from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="AgentChatMessageListResponse200Paginate")


@_attrs_define
class AgentChatMessageListResponse200Paginate:
    """
    Attributes:
        total (float): Total number of records
        page (float): Current page number
        page_size (float): Number of records per page
        total_pages (float): Total number of pages
        has_next (bool): Whether there is a next page
    """

    total: float
    page: float
    page_size: float
    total_pages: float
    has_next: bool
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        total = self.total

        page = self.page

        page_size = self.page_size

        total_pages = self.total_pages

        has_next = self.has_next

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "total": total,
                "page": page,
                "pageSize": page_size,
                "totalPages": total_pages,
                "hasNext": has_next,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        total = d.pop("total")

        page = d.pop("page")

        page_size = d.pop("pageSize")

        total_pages = d.pop("totalPages")

        has_next = d.pop("hasNext")

        agent_chat_message_list_response_200_paginate = cls(
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=has_next,
        )

        agent_chat_message_list_response_200_paginate.additional_properties = d
        return agent_chat_message_list_response_200_paginate

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
