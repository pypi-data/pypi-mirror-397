from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.current_prices_response import CurrentPricesResponse
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Unset
from typing import cast
from typing import cast, Union
from typing import Union


def _get_kwargs(
    *,
    instance_type: str,
    region: Union[None, Unset, str] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["instance_type"] = instance_type

    json_region: Union[None, Unset, str]
    if isinstance(region, Unset):
        json_region = UNSET
    else:
        json_region = region
    params["region"] = json_region

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v2/pricing/current",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[CurrentPricesResponse, HTTPValidationError]]:
    if response.status_code == 200:
        response_200 = CurrentPricesResponse.from_dict(response.json())

        return response_200

    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[CurrentPricesResponse, HTTPValidationError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    instance_type: str,
    region: Union[None, Unset, str] = UNSET,
) -> Response[Union[CurrentPricesResponse, HTTPValidationError]]:
    """Get Current Prices V2

     Get current pricing information for an instance type.

    Returns the current spot price, reserved price, and minimum price for a given
    instance type, optionally filtered by region.

    Args:
        instance_type (str):
        region (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[CurrentPricesResponse, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        instance_type=instance_type,
        region=region,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    instance_type: str,
    region: Union[None, Unset, str] = UNSET,
) -> Optional[Union[CurrentPricesResponse, HTTPValidationError]]:
    """Get Current Prices V2

     Get current pricing information for an instance type.

    Returns the current spot price, reserved price, and minimum price for a given
    instance type, optionally filtered by region.

    Args:
        instance_type (str):
        region (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[CurrentPricesResponse, HTTPValidationError]
    """

    return sync_detailed(
        client=client,
        instance_type=instance_type,
        region=region,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    instance_type: str,
    region: Union[None, Unset, str] = UNSET,
) -> Response[Union[CurrentPricesResponse, HTTPValidationError]]:
    """Get Current Prices V2

     Get current pricing information for an instance type.

    Returns the current spot price, reserved price, and minimum price for a given
    instance type, optionally filtered by region.

    Args:
        instance_type (str):
        region (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[CurrentPricesResponse, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        instance_type=instance_type,
        region=region,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    instance_type: str,
    region: Union[None, Unset, str] = UNSET,
) -> Optional[Union[CurrentPricesResponse, HTTPValidationError]]:
    """Get Current Prices V2

     Get current pricing information for an instance type.

    Returns the current spot price, reserved price, and minimum price for a given
    instance type, optionally filtered by region.

    Args:
        instance_type (str):
        region (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[CurrentPricesResponse, HTTPValidationError]
    """

    return (
        await asyncio_detailed(
            client=client,
            instance_type=instance_type,
            region=region,
        )
    ).parsed
