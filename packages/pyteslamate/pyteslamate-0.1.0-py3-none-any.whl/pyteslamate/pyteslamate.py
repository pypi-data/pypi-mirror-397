"""Async client for Teslamate API."""
# pylint: disable=too-many-arguments,too-many-positional-arguments

import logging
from datetime import datetime
from typing import Any
from urllib.parse import urljoin

from aiohttp import (
    ClientConnectorError,
    ClientError,
    ClientResponseError,
    ClientSession,
    ClientTimeout,
)

from pyteslamate.exceptions import (
    TeslamateAuthenticationError,
    TeslamateError,
    TeslamateNotFoundError,
    TeslamateRateLimitError,
    TeslamateServerError,
    TeslamateTimeoutError,
)
from pyteslamate.models import (
    CarBatteryHealth,
    CarCharge,
    CarCharges,
    CarDrive,
    CarDrives,
    Cars,
    CarStatus,
    CarUpdates,
    GlobalSettings,
)

logger = logging.getLogger(__name__)


class Teslamate:
    """Asynchronous client for the Teslamate API.

    Provides convenience methods to fetch cars, drives, charges, status and
    global settings. Designed to be used as an async context manager so the
    underlying aiohttp ClientSession is opened and closed automatically.
    """

    def __init__(
        self,
        base_url: str,
        api_key: str | None = None,
        timeout: float = 30.0,
        max_retries: int = 3,
        session: ClientSession | None = None,
    ) -> None:
        """Create a Teslamate client wrapper.

        Parameters kept explicit for clarity in tests and usage.  Certain
        linters may flag the number of parameters; disabled above for this file.
        """
        self.base_url = base_url
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        self._session = session

    async def __aenter__(self) -> "Teslamate":
        """Enter async context and initialize aiohttp ClientSession."""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        else:
            logger.warning("No API key provided; requests may be unauthorized.")

        timeout = ClientTimeout(total=self.timeout)
        self._session = ClientSession(base_url=self.base_url, headers=headers, timeout=timeout)
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit async context and close the underlying session if open."""
        if self._session and not self._session.closed:
            await self._session.close()
            logger.debug("Client session closed.")

    async def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs: Any,
    ) -> Any:
        """Perform an HTTP request and handle common HTTP errors.

        Returns parsed JSON on success or raises a Teslamate* exception on error.
        """
        if not self._session:
            raise TeslamateError(
                "Client session not initialized. Use 'async with' context manager."
            )
        url = urljoin(self.base_url, endpoint)

        # Use lazy logging formatting to avoid building strings when debug is disabled
        logger.debug("Making %s request to %s", method, url)

        try:
            async with self._session.request(method, url, **kwargs) as response:
                if response.status == 401:
                    raise TeslamateAuthenticationError("Authentication failed")
                if response.status == 404:
                    raise TeslamateNotFoundError(f"Resource not found: {url}")
                if response.status == 429:
                    raise TeslamateRateLimitError("Rate limit exceeded")
                if 500 <= response.status < 600:
                    raise TeslamateServerError(f"Server error: {response.status}")

                response.raise_for_status()
                return await response.json()

        except ClientResponseError as e:
            raise TeslamateError(f"HTTP error: {e.status} {e.message}") from e
        except ClientConnectorError as e:
            raise TeslamateError(f"Connection error: {str(e)}") from e
        except TimeoutError as exc:
            raise TeslamateTimeoutError("Request timeout") from exc
        except ClientError as e:
            raise TeslamateError(f"Request failed: {str(e)}") from e

    async def get_cars(self) -> Cars:
        """Retrieve all cars and return a parsed Cars model."""
        data = await self._request("GET", "cars")
        return Cars.model_validate(data)

    async def get_car(self, car_id: int) -> Cars:
        """Retrieve a single car by id and return a Cars model."""
        data = await self._request("GET", f"cars/{car_id}")
        return Cars.model_validate(data)

    async def get_car_battery_health(self, car_id: int) -> CarBatteryHealth:
        """Retrieve battery health for a given car id."""
        data = await self._request("GET", f"cars/{car_id}/battery-health")
        return CarBatteryHealth.model_validate(data)

    async def get_car_charges(
        self, car_id: int, start_date: datetime | None = None, end_date: datetime | None = None
    ) -> CarCharges:
        """Retrieve charges for a car. Optional start_date/end_date are ISO-encoded."""
        params: dict[str, str] = {}
        if start_date:
            params["startDate"] = start_date.isoformat()
        if end_date:
            params["endDate"] = end_date.isoformat()
        data = await self._request("GET", f"cars/{car_id}/charges", params=params or None)
        print(data)
        return CarCharges.model_validate(data)

    async def get_car_charge(self, car_id: int, charge_id: int) -> CarCharge:
        """Retrieve a single charge by id for a car."""
        data = await self._request("GET", f"cars/{car_id}/charges/{charge_id}")
        return CarCharge.model_validate(data)

    async def get_car_drives(
        self,
        car_id: int,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        min_distance: str | None = None,
        max_distance: str | None = None,
    ) -> CarDrives:
        """Retrieve drives for a car. Optional date and distance filters supported."""
        params: dict[str, str] = {}
        if start_date:
            params["startDate"] = start_date.isoformat()
        if end_date:
            params["endDate"] = end_date.isoformat()
        if min_distance:
            params["minDistance"] = min_distance
        if max_distance:
            params["maxDistance"] = max_distance
        data = await self._request("GET", f"cars/{car_id}/drives", params=params or None)
        return CarDrives.model_validate(data)

    async def get_car_drive(self, car_id: int, drive_id: int) -> CarDrive:
        """Retrieve a single drive by id for a car."""
        data = await self._request("GET", f"cars/{car_id}/drives/{drive_id}")
        return CarDrive.model_validate(data)

    async def get_car_status(self, car_id: int) -> CarStatus:
        """Retrieve current status for a car and validate the response."""
        data = await self._request("GET", f"cars/{car_id}/status")
        return CarStatus.model_validate(data)

    async def get_car_updates(self, car_id: int) -> CarUpdates:
        """Retrieve updates for a car."""
        data = await self._request("GET", f"cars/{car_id}/updates")
        return CarUpdates.model_validate(data)

    async def get_global_settings(self) -> GlobalSettings:
        """Retrieve global settings."""
        data = await self._request("GET", "globalsettings")
        return GlobalSettings.model_validate(data)
