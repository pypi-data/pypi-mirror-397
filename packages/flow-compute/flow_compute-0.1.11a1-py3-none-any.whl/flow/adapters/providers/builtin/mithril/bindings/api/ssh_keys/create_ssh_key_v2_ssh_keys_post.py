from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.create_ssh_key_request import CreateSshKeyRequest
from ...models.created_ssh_key_model import CreatedSshKeyModel
from ...models.http_validation_error import HTTPValidationError
from typing import cast


def _get_kwargs(
    *,
    body: CreateSshKeyRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v2/ssh-keys",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[CreatedSshKeyModel, HTTPValidationError]]:
    if response.status_code == 201:
        response_201 = CreatedSshKeyModel.from_dict(response.json())

        return response_201

    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[CreatedSshKeyModel, HTTPValidationError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: CreateSshKeyRequest,
) -> Response[Union[CreatedSshKeyModel, HTTPValidationError]]:
    """Create Ssh Key

     Create a new SSH key. If public_key is not provided, this endpoint will generate
    a new RSA key pair and return both the private and public keys.

    Args:
        body (CreateSshKeyRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[CreatedSshKeyModel, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    body: CreateSshKeyRequest,
) -> Optional[Union[CreatedSshKeyModel, HTTPValidationError]]:
    """Create Ssh Key

     Create a new SSH key. If public_key is not provided, this endpoint will generate
    a new RSA key pair and return both the private and public keys.

    Args:
        body (CreateSshKeyRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[CreatedSshKeyModel, HTTPValidationError]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: CreateSshKeyRequest,
) -> Response[Union[CreatedSshKeyModel, HTTPValidationError]]:
    """Create Ssh Key

     Create a new SSH key. If public_key is not provided, this endpoint will generate
    a new RSA key pair and return both the private and public keys.

    Args:
        body (CreateSshKeyRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[CreatedSshKeyModel, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: CreateSshKeyRequest,
) -> Optional[Union[CreatedSshKeyModel, HTTPValidationError]]:
    """Create Ssh Key

     Create a new SSH key. If public_key is not provided, this endpoint will generate
    a new RSA key pair and return both the private and public keys.

    Args:
        body (CreateSshKeyRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[CreatedSshKeyModel, HTTPValidationError]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
