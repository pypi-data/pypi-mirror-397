from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.http_validation_error import HTTPValidationError
from ...models.lifecycle_script_model import LifecycleScriptModel
from ...models.update_lifecycle_script_request import UpdateLifecycleScriptRequest
from typing import cast


def _get_kwargs(
    ls_fid: str,
    *,
    body: UpdateLifecycleScriptRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": "/v2/lifecycle-scripts/{ls_fid}".format(
            ls_fid=ls_fid,
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, LifecycleScriptModel]]:
    if response.status_code == 200:
        response_200 = LifecycleScriptModel.from_dict(response.json())

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
) -> Response[Union[HTTPValidationError, LifecycleScriptModel]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    ls_fid: str,
    *,
    client: AuthenticatedClient,
    body: UpdateLifecycleScriptRequest,
) -> Response[Union[HTTPValidationError, LifecycleScriptModel]]:
    """Update Lifecycle Script

    Args:
        ls_fid (str):
        body (UpdateLifecycleScriptRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, LifecycleScriptModel]]
    """

    kwargs = _get_kwargs(
        ls_fid=ls_fid,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    ls_fid: str,
    *,
    client: AuthenticatedClient,
    body: UpdateLifecycleScriptRequest,
) -> Optional[Union[HTTPValidationError, LifecycleScriptModel]]:
    """Update Lifecycle Script

    Args:
        ls_fid (str):
        body (UpdateLifecycleScriptRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, LifecycleScriptModel]
    """

    return sync_detailed(
        ls_fid=ls_fid,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    ls_fid: str,
    *,
    client: AuthenticatedClient,
    body: UpdateLifecycleScriptRequest,
) -> Response[Union[HTTPValidationError, LifecycleScriptModel]]:
    """Update Lifecycle Script

    Args:
        ls_fid (str):
        body (UpdateLifecycleScriptRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, LifecycleScriptModel]]
    """

    kwargs = _get_kwargs(
        ls_fid=ls_fid,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    ls_fid: str,
    *,
    client: AuthenticatedClient,
    body: UpdateLifecycleScriptRequest,
) -> Optional[Union[HTTPValidationError, LifecycleScriptModel]]:
    """Update Lifecycle Script

    Args:
        ls_fid (str):
        body (UpdateLifecycleScriptRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, LifecycleScriptModel]
    """

    return (
        await asyncio_detailed(
            ls_fid=ls_fid,
            client=client,
            body=body,
        )
    ).parsed
