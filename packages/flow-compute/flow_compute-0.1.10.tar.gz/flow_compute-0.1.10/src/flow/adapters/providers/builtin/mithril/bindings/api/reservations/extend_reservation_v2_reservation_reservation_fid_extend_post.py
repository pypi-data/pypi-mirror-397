from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.extend_reservation_request import ExtendReservationRequest
from ...models.http_validation_error import HTTPValidationError
from ...models.reservation_model import ReservationModel
from typing import cast


def _get_kwargs(
    reservation_fid: str,
    *,
    body: ExtendReservationRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v2/reservation/{reservation_fid}/extend".format(
            reservation_fid=reservation_fid,
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, ReservationModel]]:
    if response.status_code == 200:
        response_200 = ReservationModel.from_dict(response.json())

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
) -> Response[Union[HTTPValidationError, ReservationModel]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    reservation_fid: str,
    *,
    client: AuthenticatedClient,
    body: ExtendReservationRequest,
) -> Response[Union[HTTPValidationError, ReservationModel]]:
    """Extend Reservation

     Extend a reservation to the requested time.

    Args:
        reservation_fid (str):
        body (ExtendReservationRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, ReservationModel]]
    """

    kwargs = _get_kwargs(
        reservation_fid=reservation_fid,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    reservation_fid: str,
    *,
    client: AuthenticatedClient,
    body: ExtendReservationRequest,
) -> Optional[Union[HTTPValidationError, ReservationModel]]:
    """Extend Reservation

     Extend a reservation to the requested time.

    Args:
        reservation_fid (str):
        body (ExtendReservationRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, ReservationModel]
    """

    return sync_detailed(
        reservation_fid=reservation_fid,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    reservation_fid: str,
    *,
    client: AuthenticatedClient,
    body: ExtendReservationRequest,
) -> Response[Union[HTTPValidationError, ReservationModel]]:
    """Extend Reservation

     Extend a reservation to the requested time.

    Args:
        reservation_fid (str):
        body (ExtendReservationRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, ReservationModel]]
    """

    kwargs = _get_kwargs(
        reservation_fid=reservation_fid,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    reservation_fid: str,
    *,
    client: AuthenticatedClient,
    body: ExtendReservationRequest,
) -> Optional[Union[HTTPValidationError, ReservationModel]]:
    """Extend Reservation

     Extend a reservation to the requested time.

    Args:
        reservation_fid (str):
        body (ExtendReservationRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, ReservationModel]
    """

    return (
        await asyncio_detailed(
            reservation_fid=reservation_fid,
            client=client,
            body=body,
        )
    ).parsed
