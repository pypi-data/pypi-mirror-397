from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.http_validation_error import HTTPValidationError
from ...models.list_lifecycle_scripts_response import ListLifecycleScriptsResponse
from ...models.list_lifecycle_scripts_v2_lifecycle_scripts_get_sort_by import (
    ListLifecycleScriptsV2LifecycleScriptsGetSortBy,
)
from ...models.sort_direction import SortDirection
from ...types import UNSET, Unset
from typing import cast
from typing import cast, Union
from typing import Union


def _get_kwargs(
    *,
    next_cursor: Union[Any, None, Unset] = UNSET,
    sort_by: Union[Unset, ListLifecycleScriptsV2LifecycleScriptsGetSortBy] = UNSET,
    sort_dir: Union[Unset, SortDirection] = UNSET,
    project: str,
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

    json_limit: Union[None, Unset, int]
    if isinstance(limit, Unset):
        json_limit = UNSET
    else:
        json_limit = limit
    params["limit"] = json_limit

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v2/lifecycle-scripts",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, ListLifecycleScriptsResponse]]:
    if response.status_code == 200:
        response_200 = ListLifecycleScriptsResponse.from_dict(response.json())

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
) -> Response[Union[HTTPValidationError, ListLifecycleScriptsResponse]]:
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
    sort_by: Union[Unset, ListLifecycleScriptsV2LifecycleScriptsGetSortBy] = UNSET,
    sort_dir: Union[Unset, SortDirection] = UNSET,
    project: str,
    limit: Union[None, Unset, int] = UNSET,
) -> Response[Union[HTTPValidationError, ListLifecycleScriptsResponse]]:
    """List Lifecycle Scripts

     Get all lifecycle scripts visible to user in a project

    Args:
        next_cursor (Union[Any, None, Unset]):
        sort_by (Union[Unset, ListLifecycleScriptsV2LifecycleScriptsGetSortBy]):
        sort_dir (Union[Unset, SortDirection]):
        project (str):
        limit (Union[None, Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, ListLifecycleScriptsResponse]]
    """

    kwargs = _get_kwargs(
        next_cursor=next_cursor,
        sort_by=sort_by,
        sort_dir=sort_dir,
        project=project,
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
    sort_by: Union[Unset, ListLifecycleScriptsV2LifecycleScriptsGetSortBy] = UNSET,
    sort_dir: Union[Unset, SortDirection] = UNSET,
    project: str,
    limit: Union[None, Unset, int] = UNSET,
) -> Optional[Union[HTTPValidationError, ListLifecycleScriptsResponse]]:
    """List Lifecycle Scripts

     Get all lifecycle scripts visible to user in a project

    Args:
        next_cursor (Union[Any, None, Unset]):
        sort_by (Union[Unset, ListLifecycleScriptsV2LifecycleScriptsGetSortBy]):
        sort_dir (Union[Unset, SortDirection]):
        project (str):
        limit (Union[None, Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, ListLifecycleScriptsResponse]
    """

    return sync_detailed(
        client=client,
        next_cursor=next_cursor,
        sort_by=sort_by,
        sort_dir=sort_dir,
        project=project,
        limit=limit,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    next_cursor: Union[Any, None, Unset] = UNSET,
    sort_by: Union[Unset, ListLifecycleScriptsV2LifecycleScriptsGetSortBy] = UNSET,
    sort_dir: Union[Unset, SortDirection] = UNSET,
    project: str,
    limit: Union[None, Unset, int] = UNSET,
) -> Response[Union[HTTPValidationError, ListLifecycleScriptsResponse]]:
    """List Lifecycle Scripts

     Get all lifecycle scripts visible to user in a project

    Args:
        next_cursor (Union[Any, None, Unset]):
        sort_by (Union[Unset, ListLifecycleScriptsV2LifecycleScriptsGetSortBy]):
        sort_dir (Union[Unset, SortDirection]):
        project (str):
        limit (Union[None, Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, ListLifecycleScriptsResponse]]
    """

    kwargs = _get_kwargs(
        next_cursor=next_cursor,
        sort_by=sort_by,
        sort_dir=sort_dir,
        project=project,
        limit=limit,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    next_cursor: Union[Any, None, Unset] = UNSET,
    sort_by: Union[Unset, ListLifecycleScriptsV2LifecycleScriptsGetSortBy] = UNSET,
    sort_dir: Union[Unset, SortDirection] = UNSET,
    project: str,
    limit: Union[None, Unset, int] = UNSET,
) -> Optional[Union[HTTPValidationError, ListLifecycleScriptsResponse]]:
    """List Lifecycle Scripts

     Get all lifecycle scripts visible to user in a project

    Args:
        next_cursor (Union[Any, None, Unset]):
        sort_by (Union[Unset, ListLifecycleScriptsV2LifecycleScriptsGetSortBy]):
        sort_dir (Union[Unset, SortDirection]):
        project (str):
        limit (Union[None, Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, ListLifecycleScriptsResponse]
    """

    return (
        await asyncio_detailed(
            client=client,
            next_cursor=next_cursor,
            sort_by=sort_by,
            sort_dir=sort_dir,
            project=project,
            limit=limit,
        )
    ).parsed
