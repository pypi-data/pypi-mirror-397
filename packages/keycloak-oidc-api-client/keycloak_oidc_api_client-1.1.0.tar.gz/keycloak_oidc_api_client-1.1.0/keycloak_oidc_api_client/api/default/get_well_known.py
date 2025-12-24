from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.well_known import WellKnown
from ...types import Response


def _get_kwargs(
    realm: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/realms/{realm}/.well-known/openid-configuration",
    }

    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Error | WellKnown | None:
    if response.status_code == 200:
        response_200 = WellKnown.from_dict(response.json())

        return response_200

    if response.status_code == 404:
        response_404 = Error.from_dict(response.json())

        return response_404

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Error | WellKnown]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    realm: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[Error | WellKnown]:
    """Get the well_known object.

     Lists endpoints and other relevant configuration options

    Args:
        realm (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | WellKnown]
    """

    kwargs = _get_kwargs(
        realm=realm,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    realm: str,
    *,
    client: AuthenticatedClient | Client,
) -> Error | WellKnown | None:
    """Get the well_known object.

     Lists endpoints and other relevant configuration options

    Args:
        realm (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | WellKnown
    """

    return sync_detailed(
        realm=realm,
        client=client,
    ).parsed


async def asyncio_detailed(
    realm: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[Error | WellKnown]:
    """Get the well_known object.

     Lists endpoints and other relevant configuration options

    Args:
        realm (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | WellKnown]
    """

    kwargs = _get_kwargs(
        realm=realm,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    realm: str,
    *,
    client: AuthenticatedClient | Client,
) -> Error | WellKnown | None:
    """Get the well_known object.

     Lists endpoints and other relevant configuration options

    Args:
        realm (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | WellKnown
    """

    return (
        await asyncio_detailed(
            realm=realm,
            client=client,
        )
    ).parsed
