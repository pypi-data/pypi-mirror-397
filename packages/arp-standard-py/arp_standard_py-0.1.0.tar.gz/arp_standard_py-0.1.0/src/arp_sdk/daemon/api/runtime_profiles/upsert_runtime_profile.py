from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.error_envelope import ErrorEnvelope
from ...models.runtime_profile import RuntimeProfile
from ...models.runtime_profile_upsert_request import RuntimeProfileUpsertRequest
from typing import cast



def _get_kwargs(
    runtime_profile: str,
    *,
    body: RuntimeProfileUpsertRequest,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}


    

    

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/v1/admin/runtime-profiles/{runtime_profile}".format(runtime_profile=quote(str(runtime_profile), safe=""),),
    }

    _kwargs["json"] = body.to_dict()


    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> ErrorEnvelope | RuntimeProfile:
    if response.status_code == 200:
        response_200 = RuntimeProfile.from_dict(response.json())



        return response_200

    response_default = ErrorEnvelope.from_dict(response.json())



    return response_default



def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[ErrorEnvelope | RuntimeProfile]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    runtime_profile: str,
    *,
    client: AuthenticatedClient | Client,
    body: RuntimeProfileUpsertRequest,

) -> Response[ErrorEnvelope | RuntimeProfile]:
    """ Upsert runtime profile (safe list)

    Args:
        runtime_profile (str):
        body (RuntimeProfileUpsertRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorEnvelope | RuntimeProfile]
     """


    kwargs = _get_kwargs(
        runtime_profile=runtime_profile,
body=body,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    runtime_profile: str,
    *,
    client: AuthenticatedClient | Client,
    body: RuntimeProfileUpsertRequest,

) -> ErrorEnvelope | RuntimeProfile | None:
    """ Upsert runtime profile (safe list)

    Args:
        runtime_profile (str):
        body (RuntimeProfileUpsertRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorEnvelope | RuntimeProfile
     """


    return sync_detailed(
        runtime_profile=runtime_profile,
client=client,
body=body,

    ).parsed

async def asyncio_detailed(
    runtime_profile: str,
    *,
    client: AuthenticatedClient | Client,
    body: RuntimeProfileUpsertRequest,

) -> Response[ErrorEnvelope | RuntimeProfile]:
    """ Upsert runtime profile (safe list)

    Args:
        runtime_profile (str):
        body (RuntimeProfileUpsertRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorEnvelope | RuntimeProfile]
     """


    kwargs = _get_kwargs(
        runtime_profile=runtime_profile,
body=body,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    runtime_profile: str,
    *,
    client: AuthenticatedClient | Client,
    body: RuntimeProfileUpsertRequest,

) -> ErrorEnvelope | RuntimeProfile | None:
    """ Upsert runtime profile (safe list)

    Args:
        runtime_profile (str):
        body (RuntimeProfileUpsertRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorEnvelope | RuntimeProfile
     """


    return (await asyncio_detailed(
        runtime_profile=runtime_profile,
client=client,
body=body,

    )).parsed
