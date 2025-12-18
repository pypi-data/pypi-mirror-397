from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.agent_chat_message_list_response_200 import AgentChatMessageListResponse200
from ...types import UNSET, Response


def _get_kwargs(
    *,
    chat_id: str,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["chat_id"] = chat_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/cf/agent/chat_messages",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> AgentChatMessageListResponse200 | None:
    if response.status_code == 200:
        response_200 = AgentChatMessageListResponse200.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[AgentChatMessageListResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    chat_id: str,
) -> Response[AgentChatMessageListResponse200]:
    """
    Args:
        chat_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AgentChatMessageListResponse200]
    """

    kwargs = _get_kwargs(
        chat_id=chat_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    chat_id: str,
) -> AgentChatMessageListResponse200 | None:
    """
    Args:
        chat_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AgentChatMessageListResponse200
    """

    return sync_detailed(
        client=client,
        chat_id=chat_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    chat_id: str,
) -> Response[AgentChatMessageListResponse200]:
    """
    Args:
        chat_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AgentChatMessageListResponse200]
    """

    kwargs = _get_kwargs(
        chat_id=chat_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    chat_id: str,
) -> AgentChatMessageListResponse200 | None:
    """
    Args:
        chat_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AgentChatMessageListResponse200
    """

    return (
        await asyncio_detailed(
            client=client,
            chat_id=chat_id,
        )
    ).parsed
