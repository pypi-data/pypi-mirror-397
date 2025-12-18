from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.bid_model import BidModel
from ...models.http_validation_error import HTTPValidationError
from ...models.update_bid_request import UpdateBidRequest
from typing import cast


def _get_kwargs(
    bid_fid: str,
    *,
    body: UpdateBidRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": "/v2/spot/bids/{bid_fid}".format(
            bid_fid=bid_fid,
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[BidModel, HTTPValidationError]]:
    if response.status_code == 200:
        response_200 = BidModel.from_dict(response.json())

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
) -> Response[Union[BidModel, HTTPValidationError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    bid_fid: str,
    *,
    client: AuthenticatedClient,
    body: UpdateBidRequest,
) -> Response[Union[BidModel, HTTPValidationError]]:
    """Update Bid

     Update the limit price of a Spot bid

    Args:
        bid_fid (str):
        body (UpdateBidRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[BidModel, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        bid_fid=bid_fid,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    bid_fid: str,
    *,
    client: AuthenticatedClient,
    body: UpdateBidRequest,
) -> Optional[Union[BidModel, HTTPValidationError]]:
    """Update Bid

     Update the limit price of a Spot bid

    Args:
        bid_fid (str):
        body (UpdateBidRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[BidModel, HTTPValidationError]
    """

    return sync_detailed(
        bid_fid=bid_fid,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    bid_fid: str,
    *,
    client: AuthenticatedClient,
    body: UpdateBidRequest,
) -> Response[Union[BidModel, HTTPValidationError]]:
    """Update Bid

     Update the limit price of a Spot bid

    Args:
        bid_fid (str):
        body (UpdateBidRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[BidModel, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        bid_fid=bid_fid,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    bid_fid: str,
    *,
    client: AuthenticatedClient,
    body: UpdateBidRequest,
) -> Optional[Union[BidModel, HTTPValidationError]]:
    """Update Bid

     Update the limit price of a Spot bid

    Args:
        bid_fid (str):
        body (UpdateBidRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[BidModel, HTTPValidationError]
    """

    return (
        await asyncio_detailed(
            bid_fid=bid_fid,
            client=client,
            body=body,
        )
    ).parsed
