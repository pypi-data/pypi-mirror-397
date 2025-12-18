"""Teslamate API Client - A modern async REST API client library."""

from pyteslamate.exceptions import (
    TeslamateAuthenticationError,
    TeslamateError,
    TeslamateNotFoundError,
    TeslamateRateLimitError,
    TeslamateValidationError,
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
from pyteslamate.pyteslamate import Teslamate

__version__ = "0.1.0"

__all__ = [
    "Teslamate",
    "TeslamateError",
    "TeslamateAuthenticationError",
    "TeslamateNotFoundError",
    "TeslamateRateLimitError",
    "TeslamateValidationError",
    "Cars",
    "CarBatteryHealth",
    "CarCharges",
    "CarCharge",
    "CarDrives",
    "CarDrive",
    "CarStatus",
    "CarUpdates",
    "GlobalSettings",
]
