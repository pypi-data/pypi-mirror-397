from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.error_envelope import ErrorEnvelope
from ...models.tool_definition import ToolDefinition
from typing import cast



def _get_kwargs(
    tool_id: str,

) -> dict[str, Any]:
    

    

    

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/tools/{tool_id}".format(tool_id=quote(str(tool_id), safe=""),),
    }


    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> ErrorEnvelope | ToolDefinition:
    if response.status_code == 200:
        response_200 = ToolDefinition.from_dict(response.json())



        return response_200

    response_default = ErrorEnvelope.from_dict(response.json())



    return response_default



def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[ErrorEnvelope | ToolDefinition]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    tool_id: str,
    *,
    client: AuthenticatedClient | Client,

) -> Response[ErrorEnvelope | ToolDefinition]:
    """ Get tool

    Args:
        tool_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorEnvelope | ToolDefinition]
     """


    kwargs = _get_kwargs(
        tool_id=tool_id,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    tool_id: str,
    *,
    client: AuthenticatedClient | Client,

) -> ErrorEnvelope | ToolDefinition | None:
    """ Get tool

    Args:
        tool_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorEnvelope | ToolDefinition
     """


    return sync_detailed(
        tool_id=tool_id,
client=client,

    ).parsed

async def asyncio_detailed(
    tool_id: str,
    *,
    client: AuthenticatedClient | Client,

) -> Response[ErrorEnvelope | ToolDefinition]:
    """ Get tool

    Args:
        tool_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorEnvelope | ToolDefinition]
     """


    kwargs = _get_kwargs(
        tool_id=tool_id,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    tool_id: str,
    *,
    client: AuthenticatedClient | Client,

) -> ErrorEnvelope | ToolDefinition | None:
    """ Get tool

    Args:
        tool_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorEnvelope | ToolDefinition
     """


    return (await asyncio_detailed(
        tool_id=tool_id,
client=client,

    )).parsed
