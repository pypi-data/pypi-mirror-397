from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.http_validation_error import HTTPValidationError
from ...models.kubernetes_cluster_model import KubernetesClusterModel
from typing import cast


def _get_kwargs(
    cluster_fid: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v2/kubernetes/clusters/{cluster_fid}".format(
            cluster_fid=cluster_fid,
        ),
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, KubernetesClusterModel]]:
    if response.status_code == 200:
        response_200 = KubernetesClusterModel.from_dict(response.json())

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
) -> Response[Union[HTTPValidationError, KubernetesClusterModel]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    cluster_fid: str,
    *,
    client: AuthenticatedClient,
) -> Response[Union[HTTPValidationError, KubernetesClusterModel]]:
    """Get Kubernetes Cluster

     Get a specific Kubernetes cluster

    Args:
        cluster_fid (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, KubernetesClusterModel]]
    """

    kwargs = _get_kwargs(
        cluster_fid=cluster_fid,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    cluster_fid: str,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[HTTPValidationError, KubernetesClusterModel]]:
    """Get Kubernetes Cluster

     Get a specific Kubernetes cluster

    Args:
        cluster_fid (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, KubernetesClusterModel]
    """

    return sync_detailed(
        cluster_fid=cluster_fid,
        client=client,
    ).parsed


async def asyncio_detailed(
    cluster_fid: str,
    *,
    client: AuthenticatedClient,
) -> Response[Union[HTTPValidationError, KubernetesClusterModel]]:
    """Get Kubernetes Cluster

     Get a specific Kubernetes cluster

    Args:
        cluster_fid (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, KubernetesClusterModel]]
    """

    kwargs = _get_kwargs(
        cluster_fid=cluster_fid,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    cluster_fid: str,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[HTTPValidationError, KubernetesClusterModel]]:
    """Get Kubernetes Cluster

     Get a specific Kubernetes cluster

    Args:
        cluster_fid (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, KubernetesClusterModel]
    """

    return (
        await asyncio_detailed(
            cluster_fid=cluster_fid,
            client=client,
        )
    ).parsed
