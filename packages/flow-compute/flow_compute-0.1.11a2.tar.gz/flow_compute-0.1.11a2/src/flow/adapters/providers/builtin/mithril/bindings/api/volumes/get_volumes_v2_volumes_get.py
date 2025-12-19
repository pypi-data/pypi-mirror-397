from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.http_validation_error import HTTPValidationError
from ...models.volume_model import VolumeModel
from ...types import UNSET, Unset
from typing import cast
from typing import cast, Union
from typing import Union


def _get_kwargs(
    *,
    project: str,
    region: Union[None, Unset, str] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["project"] = project

    json_region: Union[None, Unset, str]
    if isinstance(region, Unset):
        json_region = UNSET
    else:
        json_region = region
    params["region"] = json_region

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v2/volumes",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, list["VolumeModel"]]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = VolumeModel.from_dict(response_200_item_data)

            response_200.append(response_200_item)

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
) -> Response[Union[HTTPValidationError, list["VolumeModel"]]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    project: str,
    region: Union[None, Unset, str] = UNSET,
) -> Response[Union[HTTPValidationError, list["VolumeModel"]]]:
    """Get Volumes

     Get all storage volumes for a project

    Args:
        project (str):
        region (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, list['VolumeModel']]]
    """

    kwargs = _get_kwargs(
        project=project,
        region=region,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    project: str,
    region: Union[None, Unset, str] = UNSET,
) -> Optional[Union[HTTPValidationError, list["VolumeModel"]]]:
    """Get Volumes

     Get all storage volumes for a project

    Args:
        project (str):
        region (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, list['VolumeModel']]
    """

    return sync_detailed(
        client=client,
        project=project,
        region=region,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    project: str,
    region: Union[None, Unset, str] = UNSET,
) -> Response[Union[HTTPValidationError, list["VolumeModel"]]]:
    """Get Volumes

     Get all storage volumes for a project

    Args:
        project (str):
        region (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, list['VolumeModel']]]
    """

    kwargs = _get_kwargs(
        project=project,
        region=region,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    project: str,
    region: Union[None, Unset, str] = UNSET,
) -> Optional[Union[HTTPValidationError, list["VolumeModel"]]]:
    """Get Volumes

     Get all storage volumes for a project

    Args:
        project (str):
        region (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, list['VolumeModel']]
    """

    return (
        await asyncio_detailed(
            client=client,
            project=project,
            region=region,
        )
    ).parsed
