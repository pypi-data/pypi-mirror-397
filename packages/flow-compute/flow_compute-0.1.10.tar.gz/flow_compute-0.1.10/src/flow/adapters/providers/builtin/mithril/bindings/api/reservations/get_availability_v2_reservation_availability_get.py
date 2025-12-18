from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.availability_slot_model import AvailabilitySlotModel
from ...models.check_availability_response import CheckAvailabilityResponse
from ...models.get_availability_v2_reservation_availability_get_mode import (
    GetAvailabilityV2ReservationAvailabilityGetMode,
)
from ...models.get_latest_end_time_response import GetLatestEndTimeResponse
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Unset
from typing import cast
from typing import cast, Union
from typing import Union


def _get_kwargs(
    *,
    project: str,
    instance_type: str,
    region: str,
    mode: Union[
        Unset, GetAvailabilityV2ReservationAvailabilityGetMode
    ] = GetAvailabilityV2ReservationAvailabilityGetMode.LATEST_END_TIME,
    earliest_start_time: Union[Any, None, Unset] = UNSET,
    latest_end_time: Union[Any, None, Unset] = UNSET,
    start_time: Union[Any, None, Unset] = UNSET,
    end_time: Union[Any, None, Unset] = UNSET,
    quantity: Union[None, Unset, int] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["project"] = project

    params["instance_type"] = instance_type

    params["region"] = region

    json_mode: Union[Unset, str] = UNSET
    if not isinstance(mode, Unset):
        json_mode = mode.value

    params["mode"] = json_mode

    json_earliest_start_time: Union[Any, None, Unset]
    if isinstance(earliest_start_time, Unset):
        json_earliest_start_time = UNSET
    else:
        json_earliest_start_time = earliest_start_time
    params["earliest_start_time"] = json_earliest_start_time

    json_latest_end_time: Union[Any, None, Unset]
    if isinstance(latest_end_time, Unset):
        json_latest_end_time = UNSET
    else:
        json_latest_end_time = latest_end_time
    params["latest_end_time"] = json_latest_end_time

    json_start_time: Union[Any, None, Unset]
    if isinstance(start_time, Unset):
        json_start_time = UNSET
    else:
        json_start_time = start_time
    params["start_time"] = json_start_time

    json_end_time: Union[Any, None, Unset]
    if isinstance(end_time, Unset):
        json_end_time = UNSET
    else:
        json_end_time = end_time
    params["end_time"] = json_end_time

    json_quantity: Union[None, Unset, int]
    if isinstance(quantity, Unset):
        json_quantity = UNSET
    else:
        json_quantity = quantity
    params["quantity"] = json_quantity

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v2/reservation/availability",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[
    Union[
        HTTPValidationError,
        Union[
            "CheckAvailabilityResponse", "GetLatestEndTimeResponse", list["AvailabilitySlotModel"]
        ],
    ]
]:
    if response.status_code == 200:

        def _parse_response_200(
            data: object,
        ) -> Union[
            "CheckAvailabilityResponse", "GetLatestEndTimeResponse", list["AvailabilitySlotModel"]
        ]:
            try:
                if not isinstance(data, list):
                    raise TypeError()
                response_200_type_0 = []
                _response_200_type_0 = data
                for response_200_type_0_item_data in _response_200_type_0:
                    response_200_type_0_item = AvailabilitySlotModel.from_dict(
                        response_200_type_0_item_data
                    )

                    response_200_type_0.append(response_200_type_0_item)

                return response_200_type_0
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                response_200_type_1 = GetLatestEndTimeResponse.from_dict(data)

                return response_200_type_1
            except:  # noqa: E722
                pass
            if not isinstance(data, dict):
                raise TypeError()
            response_200_type_2 = CheckAvailabilityResponse.from_dict(data)

            return response_200_type_2

        response_200 = _parse_response_200(response.json())

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
) -> Response[
    Union[
        HTTPValidationError,
        Union[
            "CheckAvailabilityResponse", "GetLatestEndTimeResponse", list["AvailabilitySlotModel"]
        ],
    ]
]:
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
    instance_type: str,
    region: str,
    mode: Union[
        Unset, GetAvailabilityV2ReservationAvailabilityGetMode
    ] = GetAvailabilityV2ReservationAvailabilityGetMode.LATEST_END_TIME,
    earliest_start_time: Union[Any, None, Unset] = UNSET,
    latest_end_time: Union[Any, None, Unset] = UNSET,
    start_time: Union[Any, None, Unset] = UNSET,
    end_time: Union[Any, None, Unset] = UNSET,
    quantity: Union[None, Unset, int] = UNSET,
) -> Response[
    Union[
        HTTPValidationError,
        Union[
            "CheckAvailabilityResponse", "GetLatestEndTimeResponse", list["AvailabilitySlotModel"]
        ],
    ]
]:
    """Get Availability

     Get availability information for reservations.

    This endpoint supports three different modes for querying availability:

    ## Mode: latest_end_time (default)
    Get the latest possible end time for a reservation given a start time and
    quantity.

    **Required parameters:**
    - `start_time`: Desired start time for the reservation
    - `quantity`: Number of instances needed
    - `project`: Project FID
    - `instance_type`: Instance type FID
    - `region`: Region name

    **Returns:** Latest possible end time and availability status

    **Example:**
    ```
    GET /reservation/availability?
        start_time=2024-01-01T00:00:00Z&
        quantity=4&
        project=proj_01h8x2k9m3n4p5q6r7s8t9u0v&
        instance_type=it_01h8x2k9m3n4p5q6r7s8t9u0v&
        region=us-central1-a
    ```

    ## Mode: slots
    Get all available slots in a time range.

    **Required parameters:**
    - `earliest_start_time`: Start of the time range to search
    - `latest_end_time`: End of the time range to search
    - `project`: Project FID
    - `instance_type`: Instance type FID
    - `region`: Region name

    **Returns:** List of available time slots with quantities

    **Example:**
    ```
    GET /reservation/availability?
        mode=slots&
        earliest_start_time=2024-01-01T00:00:00Z&
        latest_end_time=2024-01-02T00:00:00Z&
        project=proj_01h8x2k9m3n4p5q6r7s8t9u0v&
        instance_type=it_01h8x2k9m3n4p5q6r7s8t9u0v&
        region=us-central1-a
    ```

    ## Mode: check
    Check if a specific time slot is available for reservation.

    **Required parameters:**
    - `start_time`: Start of the desired time slot
    - `end_time`: End of the desired time slot
    - `quantity`: Number of instances needed
    - `project`: Project FID
    - `instance_type`: Instance type FID
    - `region`: Region name

    **Returns:** Boolean indicating if the slot is available

    **Example:**
    ```
    GET /reservation/availability?
        mode=check&
        start_time=2024-01-01T00:00:00Z&
        end_time=2024-01-01T12:00:00Z&
        quantity=4&
        project=proj_01h8x2k9m3n4p5q6r7s8t9u0v&
        instance_type=it_01h8x2k9m3n4p5q6r7s8t9u0v&
        region=us-central1-a
    ```

    ## Common Parameters
    All modes require these parameters:
    - `project`: Project FID
    - `instance_type`: Instance type FID
    - `region`: Region name

    ## Authentication
    Requires authentication and user must be a member of the specified project.

    Args:
        project (str):
        instance_type (str):
        region (str):
        mode (Union[Unset, GetAvailabilityV2ReservationAvailabilityGetMode]):  Default:
            GetAvailabilityV2ReservationAvailabilityGetMode.LATEST_END_TIME.
        earliest_start_time (Union[Any, None, Unset]):
        latest_end_time (Union[Any, None, Unset]):
        start_time (Union[Any, None, Unset]):
        end_time (Union[Any, None, Unset]):
        quantity (Union[None, Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, Union['CheckAvailabilityResponse', 'GetLatestEndTimeResponse', list['AvailabilitySlotModel']]]]
    """

    kwargs = _get_kwargs(
        project=project,
        instance_type=instance_type,
        region=region,
        mode=mode,
        earliest_start_time=earliest_start_time,
        latest_end_time=latest_end_time,
        start_time=start_time,
        end_time=end_time,
        quantity=quantity,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    project: str,
    instance_type: str,
    region: str,
    mode: Union[
        Unset, GetAvailabilityV2ReservationAvailabilityGetMode
    ] = GetAvailabilityV2ReservationAvailabilityGetMode.LATEST_END_TIME,
    earliest_start_time: Union[Any, None, Unset] = UNSET,
    latest_end_time: Union[Any, None, Unset] = UNSET,
    start_time: Union[Any, None, Unset] = UNSET,
    end_time: Union[Any, None, Unset] = UNSET,
    quantity: Union[None, Unset, int] = UNSET,
) -> Optional[
    Union[
        HTTPValidationError,
        Union[
            "CheckAvailabilityResponse", "GetLatestEndTimeResponse", list["AvailabilitySlotModel"]
        ],
    ]
]:
    """Get Availability

     Get availability information for reservations.

    This endpoint supports three different modes for querying availability:

    ## Mode: latest_end_time (default)
    Get the latest possible end time for a reservation given a start time and
    quantity.

    **Required parameters:**
    - `start_time`: Desired start time for the reservation
    - `quantity`: Number of instances needed
    - `project`: Project FID
    - `instance_type`: Instance type FID
    - `region`: Region name

    **Returns:** Latest possible end time and availability status

    **Example:**
    ```
    GET /reservation/availability?
        start_time=2024-01-01T00:00:00Z&
        quantity=4&
        project=proj_01h8x2k9m3n4p5q6r7s8t9u0v&
        instance_type=it_01h8x2k9m3n4p5q6r7s8t9u0v&
        region=us-central1-a
    ```

    ## Mode: slots
    Get all available slots in a time range.

    **Required parameters:**
    - `earliest_start_time`: Start of the time range to search
    - `latest_end_time`: End of the time range to search
    - `project`: Project FID
    - `instance_type`: Instance type FID
    - `region`: Region name

    **Returns:** List of available time slots with quantities

    **Example:**
    ```
    GET /reservation/availability?
        mode=slots&
        earliest_start_time=2024-01-01T00:00:00Z&
        latest_end_time=2024-01-02T00:00:00Z&
        project=proj_01h8x2k9m3n4p5q6r7s8t9u0v&
        instance_type=it_01h8x2k9m3n4p5q6r7s8t9u0v&
        region=us-central1-a
    ```

    ## Mode: check
    Check if a specific time slot is available for reservation.

    **Required parameters:**
    - `start_time`: Start of the desired time slot
    - `end_time`: End of the desired time slot
    - `quantity`: Number of instances needed
    - `project`: Project FID
    - `instance_type`: Instance type FID
    - `region`: Region name

    **Returns:** Boolean indicating if the slot is available

    **Example:**
    ```
    GET /reservation/availability?
        mode=check&
        start_time=2024-01-01T00:00:00Z&
        end_time=2024-01-01T12:00:00Z&
        quantity=4&
        project=proj_01h8x2k9m3n4p5q6r7s8t9u0v&
        instance_type=it_01h8x2k9m3n4p5q6r7s8t9u0v&
        region=us-central1-a
    ```

    ## Common Parameters
    All modes require these parameters:
    - `project`: Project FID
    - `instance_type`: Instance type FID
    - `region`: Region name

    ## Authentication
    Requires authentication and user must be a member of the specified project.

    Args:
        project (str):
        instance_type (str):
        region (str):
        mode (Union[Unset, GetAvailabilityV2ReservationAvailabilityGetMode]):  Default:
            GetAvailabilityV2ReservationAvailabilityGetMode.LATEST_END_TIME.
        earliest_start_time (Union[Any, None, Unset]):
        latest_end_time (Union[Any, None, Unset]):
        start_time (Union[Any, None, Unset]):
        end_time (Union[Any, None, Unset]):
        quantity (Union[None, Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, Union['CheckAvailabilityResponse', 'GetLatestEndTimeResponse', list['AvailabilitySlotModel']]]
    """

    return sync_detailed(
        client=client,
        project=project,
        instance_type=instance_type,
        region=region,
        mode=mode,
        earliest_start_time=earliest_start_time,
        latest_end_time=latest_end_time,
        start_time=start_time,
        end_time=end_time,
        quantity=quantity,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    project: str,
    instance_type: str,
    region: str,
    mode: Union[
        Unset, GetAvailabilityV2ReservationAvailabilityGetMode
    ] = GetAvailabilityV2ReservationAvailabilityGetMode.LATEST_END_TIME,
    earliest_start_time: Union[Any, None, Unset] = UNSET,
    latest_end_time: Union[Any, None, Unset] = UNSET,
    start_time: Union[Any, None, Unset] = UNSET,
    end_time: Union[Any, None, Unset] = UNSET,
    quantity: Union[None, Unset, int] = UNSET,
) -> Response[
    Union[
        HTTPValidationError,
        Union[
            "CheckAvailabilityResponse", "GetLatestEndTimeResponse", list["AvailabilitySlotModel"]
        ],
    ]
]:
    """Get Availability

     Get availability information for reservations.

    This endpoint supports three different modes for querying availability:

    ## Mode: latest_end_time (default)
    Get the latest possible end time for a reservation given a start time and
    quantity.

    **Required parameters:**
    - `start_time`: Desired start time for the reservation
    - `quantity`: Number of instances needed
    - `project`: Project FID
    - `instance_type`: Instance type FID
    - `region`: Region name

    **Returns:** Latest possible end time and availability status

    **Example:**
    ```
    GET /reservation/availability?
        start_time=2024-01-01T00:00:00Z&
        quantity=4&
        project=proj_01h8x2k9m3n4p5q6r7s8t9u0v&
        instance_type=it_01h8x2k9m3n4p5q6r7s8t9u0v&
        region=us-central1-a
    ```

    ## Mode: slots
    Get all available slots in a time range.

    **Required parameters:**
    - `earliest_start_time`: Start of the time range to search
    - `latest_end_time`: End of the time range to search
    - `project`: Project FID
    - `instance_type`: Instance type FID
    - `region`: Region name

    **Returns:** List of available time slots with quantities

    **Example:**
    ```
    GET /reservation/availability?
        mode=slots&
        earliest_start_time=2024-01-01T00:00:00Z&
        latest_end_time=2024-01-02T00:00:00Z&
        project=proj_01h8x2k9m3n4p5q6r7s8t9u0v&
        instance_type=it_01h8x2k9m3n4p5q6r7s8t9u0v&
        region=us-central1-a
    ```

    ## Mode: check
    Check if a specific time slot is available for reservation.

    **Required parameters:**
    - `start_time`: Start of the desired time slot
    - `end_time`: End of the desired time slot
    - `quantity`: Number of instances needed
    - `project`: Project FID
    - `instance_type`: Instance type FID
    - `region`: Region name

    **Returns:** Boolean indicating if the slot is available

    **Example:**
    ```
    GET /reservation/availability?
        mode=check&
        start_time=2024-01-01T00:00:00Z&
        end_time=2024-01-01T12:00:00Z&
        quantity=4&
        project=proj_01h8x2k9m3n4p5q6r7s8t9u0v&
        instance_type=it_01h8x2k9m3n4p5q6r7s8t9u0v&
        region=us-central1-a
    ```

    ## Common Parameters
    All modes require these parameters:
    - `project`: Project FID
    - `instance_type`: Instance type FID
    - `region`: Region name

    ## Authentication
    Requires authentication and user must be a member of the specified project.

    Args:
        project (str):
        instance_type (str):
        region (str):
        mode (Union[Unset, GetAvailabilityV2ReservationAvailabilityGetMode]):  Default:
            GetAvailabilityV2ReservationAvailabilityGetMode.LATEST_END_TIME.
        earliest_start_time (Union[Any, None, Unset]):
        latest_end_time (Union[Any, None, Unset]):
        start_time (Union[Any, None, Unset]):
        end_time (Union[Any, None, Unset]):
        quantity (Union[None, Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, Union['CheckAvailabilityResponse', 'GetLatestEndTimeResponse', list['AvailabilitySlotModel']]]]
    """

    kwargs = _get_kwargs(
        project=project,
        instance_type=instance_type,
        region=region,
        mode=mode,
        earliest_start_time=earliest_start_time,
        latest_end_time=latest_end_time,
        start_time=start_time,
        end_time=end_time,
        quantity=quantity,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    project: str,
    instance_type: str,
    region: str,
    mode: Union[
        Unset, GetAvailabilityV2ReservationAvailabilityGetMode
    ] = GetAvailabilityV2ReservationAvailabilityGetMode.LATEST_END_TIME,
    earliest_start_time: Union[Any, None, Unset] = UNSET,
    latest_end_time: Union[Any, None, Unset] = UNSET,
    start_time: Union[Any, None, Unset] = UNSET,
    end_time: Union[Any, None, Unset] = UNSET,
    quantity: Union[None, Unset, int] = UNSET,
) -> Optional[
    Union[
        HTTPValidationError,
        Union[
            "CheckAvailabilityResponse", "GetLatestEndTimeResponse", list["AvailabilitySlotModel"]
        ],
    ]
]:
    """Get Availability

     Get availability information for reservations.

    This endpoint supports three different modes for querying availability:

    ## Mode: latest_end_time (default)
    Get the latest possible end time for a reservation given a start time and
    quantity.

    **Required parameters:**
    - `start_time`: Desired start time for the reservation
    - `quantity`: Number of instances needed
    - `project`: Project FID
    - `instance_type`: Instance type FID
    - `region`: Region name

    **Returns:** Latest possible end time and availability status

    **Example:**
    ```
    GET /reservation/availability?
        start_time=2024-01-01T00:00:00Z&
        quantity=4&
        project=proj_01h8x2k9m3n4p5q6r7s8t9u0v&
        instance_type=it_01h8x2k9m3n4p5q6r7s8t9u0v&
        region=us-central1-a
    ```

    ## Mode: slots
    Get all available slots in a time range.

    **Required parameters:**
    - `earliest_start_time`: Start of the time range to search
    - `latest_end_time`: End of the time range to search
    - `project`: Project FID
    - `instance_type`: Instance type FID
    - `region`: Region name

    **Returns:** List of available time slots with quantities

    **Example:**
    ```
    GET /reservation/availability?
        mode=slots&
        earliest_start_time=2024-01-01T00:00:00Z&
        latest_end_time=2024-01-02T00:00:00Z&
        project=proj_01h8x2k9m3n4p5q6r7s8t9u0v&
        instance_type=it_01h8x2k9m3n4p5q6r7s8t9u0v&
        region=us-central1-a
    ```

    ## Mode: check
    Check if a specific time slot is available for reservation.

    **Required parameters:**
    - `start_time`: Start of the desired time slot
    - `end_time`: End of the desired time slot
    - `quantity`: Number of instances needed
    - `project`: Project FID
    - `instance_type`: Instance type FID
    - `region`: Region name

    **Returns:** Boolean indicating if the slot is available

    **Example:**
    ```
    GET /reservation/availability?
        mode=check&
        start_time=2024-01-01T00:00:00Z&
        end_time=2024-01-01T12:00:00Z&
        quantity=4&
        project=proj_01h8x2k9m3n4p5q6r7s8t9u0v&
        instance_type=it_01h8x2k9m3n4p5q6r7s8t9u0v&
        region=us-central1-a
    ```

    ## Common Parameters
    All modes require these parameters:
    - `project`: Project FID
    - `instance_type`: Instance type FID
    - `region`: Region name

    ## Authentication
    Requires authentication and user must be a member of the specified project.

    Args:
        project (str):
        instance_type (str):
        region (str):
        mode (Union[Unset, GetAvailabilityV2ReservationAvailabilityGetMode]):  Default:
            GetAvailabilityV2ReservationAvailabilityGetMode.LATEST_END_TIME.
        earliest_start_time (Union[Any, None, Unset]):
        latest_end_time (Union[Any, None, Unset]):
        start_time (Union[Any, None, Unset]):
        end_time (Union[Any, None, Unset]):
        quantity (Union[None, Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, Union['CheckAvailabilityResponse', 'GetLatestEndTimeResponse', list['AvailabilitySlotModel']]]
    """

    return (
        await asyncio_detailed(
            client=client,
            project=project,
            instance_type=instance_type,
            region=region,
            mode=mode,
            earliest_start_time=earliest_start_time,
            latest_end_time=latest_end_time,
            start_time=start_time,
            end_time=end_time,
            quantity=quantity,
        )
    ).parsed
