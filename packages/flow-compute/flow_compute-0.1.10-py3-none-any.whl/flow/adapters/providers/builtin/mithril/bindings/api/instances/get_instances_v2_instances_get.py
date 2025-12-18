from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.get_instances_response import GetInstancesResponse
from ...models.get_instances_v2_instances_get_order_type_in_type_0_item import (
    GetInstancesV2InstancesGetOrderTypeInType0Item,
)
from ...models.get_instances_v2_instances_get_sort_by import GetInstancesV2InstancesGetSortBy
from ...models.get_instances_v2_instances_get_status_in_type_0_item import (
    GetInstancesV2InstancesGetStatusInType0Item,
)
from ...models.http_validation_error import HTTPValidationError
from ...models.sort_direction import SortDirection
from ...types import UNSET, Unset
from typing import cast
from typing import cast, Union
from typing import Union


def _get_kwargs(
    *,
    next_cursor: Union[Any, None, Unset] = UNSET,
    sort_by: Union[Unset, GetInstancesV2InstancesGetSortBy] = UNSET,
    sort_dir: Union[Unset, SortDirection] = UNSET,
    project: str,
    instance_type: Union[None, Unset, str] = UNSET,
    region: Union[None, Unset, str] = UNSET,
    status_in: Union[None, Unset, list[GetInstancesV2InstancesGetStatusInType0Item]] = UNSET,
    order_type_in: Union[None, Unset, list[GetInstancesV2InstancesGetOrderTypeInType0Item]] = UNSET,
    bid_fid_in: Union[None, Unset, list[str]] = UNSET,
    reservation_fid_in: Union[None, Unset, list[str]] = UNSET,
    limit: Union[None, Unset, int] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_next_cursor: Union[Any, None, Unset]
    if isinstance(next_cursor, Unset):
        json_next_cursor = UNSET
    else:
        json_next_cursor = next_cursor
    params["next_cursor"] = json_next_cursor

    json_sort_by: Union[Unset, str] = UNSET
    if not isinstance(sort_by, Unset):
        json_sort_by = sort_by.value

    params["sort_by"] = json_sort_by

    json_sort_dir: Union[Unset, str] = UNSET
    if not isinstance(sort_dir, Unset):
        json_sort_dir = sort_dir.value

    params["sort_dir"] = json_sort_dir

    params["project"] = project

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

    json_status_in: Union[None, Unset, list[str]]
    if isinstance(status_in, Unset):
        json_status_in = UNSET
    elif isinstance(status_in, list):
        json_status_in = []
        for status_in_type_0_item_data in status_in:
            status_in_type_0_item = status_in_type_0_item_data.value
            json_status_in.append(status_in_type_0_item)

    else:
        json_status_in = status_in
    params["status_in"] = json_status_in

    json_order_type_in: Union[None, Unset, list[str]]
    if isinstance(order_type_in, Unset):
        json_order_type_in = UNSET
    elif isinstance(order_type_in, list):
        json_order_type_in = []
        for order_type_in_type_0_item_data in order_type_in:
            order_type_in_type_0_item = order_type_in_type_0_item_data.value
            json_order_type_in.append(order_type_in_type_0_item)

    else:
        json_order_type_in = order_type_in
    params["order_type_in"] = json_order_type_in

    json_bid_fid_in: Union[None, Unset, list[str]]
    if isinstance(bid_fid_in, Unset):
        json_bid_fid_in = UNSET
    elif isinstance(bid_fid_in, list):
        json_bid_fid_in = bid_fid_in

    else:
        json_bid_fid_in = bid_fid_in
    params["bid_fid_in"] = json_bid_fid_in

    json_reservation_fid_in: Union[None, Unset, list[str]]
    if isinstance(reservation_fid_in, Unset):
        json_reservation_fid_in = UNSET
    elif isinstance(reservation_fid_in, list):
        json_reservation_fid_in = reservation_fid_in

    else:
        json_reservation_fid_in = reservation_fid_in
    params["reservation_fid_in"] = json_reservation_fid_in

    json_limit: Union[None, Unset, int]
    if isinstance(limit, Unset):
        json_limit = UNSET
    else:
        json_limit = limit
    params["limit"] = json_limit

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v2/instances",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[GetInstancesResponse, HTTPValidationError]]:
    if response.status_code == 200:
        response_200 = GetInstancesResponse.from_dict(response.json())

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
) -> Response[Union[GetInstancesResponse, HTTPValidationError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    next_cursor: Union[Any, None, Unset] = UNSET,
    sort_by: Union[Unset, GetInstancesV2InstancesGetSortBy] = UNSET,
    sort_dir: Union[Unset, SortDirection] = UNSET,
    project: str,
    instance_type: Union[None, Unset, str] = UNSET,
    region: Union[None, Unset, str] = UNSET,
    status_in: Union[None, Unset, list[GetInstancesV2InstancesGetStatusInType0Item]] = UNSET,
    order_type_in: Union[None, Unset, list[GetInstancesV2InstancesGetOrderTypeInType0Item]] = UNSET,
    bid_fid_in: Union[None, Unset, list[str]] = UNSET,
    reservation_fid_in: Union[None, Unset, list[str]] = UNSET,
    limit: Union[None, Unset, int] = UNSET,
) -> Response[Union[GetInstancesResponse, HTTPValidationError]]:
    """Get Instances

     Get all instances for a project

    Args:
        next_cursor (Union[Any, None, Unset]):
        sort_by (Union[Unset, GetInstancesV2InstancesGetSortBy]):
        sort_dir (Union[Unset, SortDirection]):
        project (str):
        instance_type (Union[None, Unset, str]):
        region (Union[None, Unset, str]):
        status_in (Union[None, Unset, list[GetInstancesV2InstancesGetStatusInType0Item]]): Comma-
            separated list of instance statuses
        order_type_in (Union[None, Unset, list[GetInstancesV2InstancesGetOrderTypeInType0Item]]):
            Comma-separated list of order types
        bid_fid_in (Union[None, Unset, list[str]]): Comma-separated list of bid FIDs
        reservation_fid_in (Union[None, Unset, list[str]]): Comma-separated list of reservation
            FIDs
        limit (Union[None, Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[GetInstancesResponse, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        next_cursor=next_cursor,
        sort_by=sort_by,
        sort_dir=sort_dir,
        project=project,
        instance_type=instance_type,
        region=region,
        status_in=status_in,
        order_type_in=order_type_in,
        bid_fid_in=bid_fid_in,
        reservation_fid_in=reservation_fid_in,
        limit=limit,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    next_cursor: Union[Any, None, Unset] = UNSET,
    sort_by: Union[Unset, GetInstancesV2InstancesGetSortBy] = UNSET,
    sort_dir: Union[Unset, SortDirection] = UNSET,
    project: str,
    instance_type: Union[None, Unset, str] = UNSET,
    region: Union[None, Unset, str] = UNSET,
    status_in: Union[None, Unset, list[GetInstancesV2InstancesGetStatusInType0Item]] = UNSET,
    order_type_in: Union[None, Unset, list[GetInstancesV2InstancesGetOrderTypeInType0Item]] = UNSET,
    bid_fid_in: Union[None, Unset, list[str]] = UNSET,
    reservation_fid_in: Union[None, Unset, list[str]] = UNSET,
    limit: Union[None, Unset, int] = UNSET,
) -> Optional[Union[GetInstancesResponse, HTTPValidationError]]:
    """Get Instances

     Get all instances for a project

    Args:
        next_cursor (Union[Any, None, Unset]):
        sort_by (Union[Unset, GetInstancesV2InstancesGetSortBy]):
        sort_dir (Union[Unset, SortDirection]):
        project (str):
        instance_type (Union[None, Unset, str]):
        region (Union[None, Unset, str]):
        status_in (Union[None, Unset, list[GetInstancesV2InstancesGetStatusInType0Item]]): Comma-
            separated list of instance statuses
        order_type_in (Union[None, Unset, list[GetInstancesV2InstancesGetOrderTypeInType0Item]]):
            Comma-separated list of order types
        bid_fid_in (Union[None, Unset, list[str]]): Comma-separated list of bid FIDs
        reservation_fid_in (Union[None, Unset, list[str]]): Comma-separated list of reservation
            FIDs
        limit (Union[None, Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[GetInstancesResponse, HTTPValidationError]
    """

    return sync_detailed(
        client=client,
        next_cursor=next_cursor,
        sort_by=sort_by,
        sort_dir=sort_dir,
        project=project,
        instance_type=instance_type,
        region=region,
        status_in=status_in,
        order_type_in=order_type_in,
        bid_fid_in=bid_fid_in,
        reservation_fid_in=reservation_fid_in,
        limit=limit,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    next_cursor: Union[Any, None, Unset] = UNSET,
    sort_by: Union[Unset, GetInstancesV2InstancesGetSortBy] = UNSET,
    sort_dir: Union[Unset, SortDirection] = UNSET,
    project: str,
    instance_type: Union[None, Unset, str] = UNSET,
    region: Union[None, Unset, str] = UNSET,
    status_in: Union[None, Unset, list[GetInstancesV2InstancesGetStatusInType0Item]] = UNSET,
    order_type_in: Union[None, Unset, list[GetInstancesV2InstancesGetOrderTypeInType0Item]] = UNSET,
    bid_fid_in: Union[None, Unset, list[str]] = UNSET,
    reservation_fid_in: Union[None, Unset, list[str]] = UNSET,
    limit: Union[None, Unset, int] = UNSET,
) -> Response[Union[GetInstancesResponse, HTTPValidationError]]:
    """Get Instances

     Get all instances for a project

    Args:
        next_cursor (Union[Any, None, Unset]):
        sort_by (Union[Unset, GetInstancesV2InstancesGetSortBy]):
        sort_dir (Union[Unset, SortDirection]):
        project (str):
        instance_type (Union[None, Unset, str]):
        region (Union[None, Unset, str]):
        status_in (Union[None, Unset, list[GetInstancesV2InstancesGetStatusInType0Item]]): Comma-
            separated list of instance statuses
        order_type_in (Union[None, Unset, list[GetInstancesV2InstancesGetOrderTypeInType0Item]]):
            Comma-separated list of order types
        bid_fid_in (Union[None, Unset, list[str]]): Comma-separated list of bid FIDs
        reservation_fid_in (Union[None, Unset, list[str]]): Comma-separated list of reservation
            FIDs
        limit (Union[None, Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[GetInstancesResponse, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        next_cursor=next_cursor,
        sort_by=sort_by,
        sort_dir=sort_dir,
        project=project,
        instance_type=instance_type,
        region=region,
        status_in=status_in,
        order_type_in=order_type_in,
        bid_fid_in=bid_fid_in,
        reservation_fid_in=reservation_fid_in,
        limit=limit,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    next_cursor: Union[Any, None, Unset] = UNSET,
    sort_by: Union[Unset, GetInstancesV2InstancesGetSortBy] = UNSET,
    sort_dir: Union[Unset, SortDirection] = UNSET,
    project: str,
    instance_type: Union[None, Unset, str] = UNSET,
    region: Union[None, Unset, str] = UNSET,
    status_in: Union[None, Unset, list[GetInstancesV2InstancesGetStatusInType0Item]] = UNSET,
    order_type_in: Union[None, Unset, list[GetInstancesV2InstancesGetOrderTypeInType0Item]] = UNSET,
    bid_fid_in: Union[None, Unset, list[str]] = UNSET,
    reservation_fid_in: Union[None, Unset, list[str]] = UNSET,
    limit: Union[None, Unset, int] = UNSET,
) -> Optional[Union[GetInstancesResponse, HTTPValidationError]]:
    """Get Instances

     Get all instances for a project

    Args:
        next_cursor (Union[Any, None, Unset]):
        sort_by (Union[Unset, GetInstancesV2InstancesGetSortBy]):
        sort_dir (Union[Unset, SortDirection]):
        project (str):
        instance_type (Union[None, Unset, str]):
        region (Union[None, Unset, str]):
        status_in (Union[None, Unset, list[GetInstancesV2InstancesGetStatusInType0Item]]): Comma-
            separated list of instance statuses
        order_type_in (Union[None, Unset, list[GetInstancesV2InstancesGetOrderTypeInType0Item]]):
            Comma-separated list of order types
        bid_fid_in (Union[None, Unset, list[str]]): Comma-separated list of bid FIDs
        reservation_fid_in (Union[None, Unset, list[str]]): Comma-separated list of reservation
            FIDs
        limit (Union[None, Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[GetInstancesResponse, HTTPValidationError]
    """

    return (
        await asyncio_detailed(
            client=client,
            next_cursor=next_cursor,
            sort_by=sort_by,
            sort_dir=sort_dir,
            project=project,
            instance_type=instance_type,
            region=region,
            status_in=status_in,
            order_type_in=order_type_in,
            bid_fid_in=bid_fid_in,
            reservation_fid_in=reservation_fid_in,
            limit=limit,
        )
    ).parsed
