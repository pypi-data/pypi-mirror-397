from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.historical_prices_response_model import HistoricalPricesResponseModel
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Unset
from typing import cast
from typing import cast, Union
from typing import Union


def _get_kwargs(
    *,
    instance_type: Union[None, Unset, str] = UNSET,
    region: Union[None, Unset, str] = UNSET,
    num_samples: Union[Unset, int] = 100,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_instance_type: Union[None, Unset, str]
    if isinstance(instance_type, Unset):
        json_instance_type = UNSET
    else:
        json_instance_type = instance_type
    params["instance_type"] = json_instance_type

    json_region: Union[None, Unset, str]
    if isinstance(region, Unset):
        json_region = UNSET
    else:
        json_region = region
    params["region"] = json_region

    params["num_samples"] = num_samples

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v2/pricing/history",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, HistoricalPricesResponseModel]]:
    if response.status_code == 200:
        response_200 = HistoricalPricesResponseModel.from_dict(response.json())

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
) -> Response[Union[HTTPValidationError, HistoricalPricesResponseModel]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    instance_type: Union[None, Unset, str] = UNSET,
    region: Union[None, Unset, str] = UNSET,
    num_samples: Union[Unset, int] = 100,
) -> Response[Union[HTTPValidationError, HistoricalPricesResponseModel]]:
    """Get Historical Prices V2

     Get historical pricing information for instance types.

    Returns historical spot and reserved prices over time for instance types,
    optionally filtered by specific instance type and region.

    Args:
        instance_type (Union[None, Unset, str]):
        region (Union[None, Unset, str]):
        num_samples (Union[Unset, int]):  Default: 100.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, HistoricalPricesResponseModel]]
    """

    kwargs = _get_kwargs(
        instance_type=instance_type,
        region=region,
        num_samples=num_samples,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    instance_type: Union[None, Unset, str] = UNSET,
    region: Union[None, Unset, str] = UNSET,
    num_samples: Union[Unset, int] = 100,
) -> Optional[Union[HTTPValidationError, HistoricalPricesResponseModel]]:
    """Get Historical Prices V2

     Get historical pricing information for instance types.

    Returns historical spot and reserved prices over time for instance types,
    optionally filtered by specific instance type and region.

    Args:
        instance_type (Union[None, Unset, str]):
        region (Union[None, Unset, str]):
        num_samples (Union[Unset, int]):  Default: 100.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, HistoricalPricesResponseModel]
    """

    return sync_detailed(
        client=client,
        instance_type=instance_type,
        region=region,
        num_samples=num_samples,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    instance_type: Union[None, Unset, str] = UNSET,
    region: Union[None, Unset, str] = UNSET,
    num_samples: Union[Unset, int] = 100,
) -> Response[Union[HTTPValidationError, HistoricalPricesResponseModel]]:
    """Get Historical Prices V2

     Get historical pricing information for instance types.

    Returns historical spot and reserved prices over time for instance types,
    optionally filtered by specific instance type and region.

    Args:
        instance_type (Union[None, Unset, str]):
        region (Union[None, Unset, str]):
        num_samples (Union[Unset, int]):  Default: 100.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, HistoricalPricesResponseModel]]
    """

    kwargs = _get_kwargs(
        instance_type=instance_type,
        region=region,
        num_samples=num_samples,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    instance_type: Union[None, Unset, str] = UNSET,
    region: Union[None, Unset, str] = UNSET,
    num_samples: Union[Unset, int] = 100,
) -> Optional[Union[HTTPValidationError, HistoricalPricesResponseModel]]:
    """Get Historical Prices V2

     Get historical pricing information for instance types.

    Returns historical spot and reserved prices over time for instance types,
    optionally filtered by specific instance type and region.

    Args:
        instance_type (Union[None, Unset, str]):
        region (Union[None, Unset, str]):
        num_samples (Union[Unset, int]):  Default: 100.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, HistoricalPricesResponseModel]
    """

    return (
        await asyncio_detailed(
            client=client,
            instance_type=instance_type,
            region=region,
            num_samples=num_samples,
        )
    ).parsed
