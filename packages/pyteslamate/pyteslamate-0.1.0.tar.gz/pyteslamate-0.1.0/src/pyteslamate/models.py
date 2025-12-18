"""Pydantic models for API request and response validation."""

# Disable class-docstring checks for this large models file
# (If you prefer, add docstrings to each class instead)
# pylint: disable=missing-class-docstring

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, field_validator


# Top Level Models
class Cars(BaseModel):
    data: CarsModel


class CarBatteryHealth(BaseModel):
    data: CarBatteryHealthModel


class CarCharges(BaseModel):
    data: CarChargesModel


class CarCharge(BaseModel):
    data: CarChargeModel


class CarDrives(BaseModel):
    data: CarDrivesModel


class CarDrive(BaseModel):
    data: CarDriveModel


class CarStatus(BaseModel):
    data: CarStatusModel


class CarUpdates(BaseModel):
    data: CarUpdatesModel


class GlobalSettings(BaseModel):
    data: GlobalSettingsModel


# Common Models
class CarDetailsReduced(BaseModel):
    car_id: int
    car_name: str


class Units(BaseModel):
    unit_of_length: Literal["km", "mi"]
    unit_of_temperature: Literal["C", "F"]


class UnitsStatus(Units):
    unit_of_pressure: Literal["bar", "psi"]


# Cars Models
class CarsModel(BaseModel):
    cars: list[Car] | None


class Car(BaseModel):
    car_id: int
    name: str
    car_details: CarDetails
    car_exterior: CarExterior
    car_settings: CarSettings
    teslamate_details: TeslamateDetails
    teslamate_stats: TeslamateStats


class CarDetails(BaseModel):
    eid: int
    vid: int
    vin: str
    model: str
    trim_badging: str
    efficiency: float


class CarExterior(BaseModel):
    exterior_color: str
    spoiler_type: str
    wheel_type: str


class CarSettings(BaseModel):
    suspend_min: int
    suspend_after_idle_min: int
    req_not_unlocked: bool
    free_supercharging: bool
    use_streaming_api: bool


class TeslamateDetails(BaseModel):
    inserted_at: datetime
    updated_at: datetime


class TeslamateStats(BaseModel):
    total_charges: int
    total_drives: int
    total_updates: int


# Battery Health Models
class CarBatteryHealthModel(BaseModel):
    car: CarDetailsReduced
    battery_health: BatteryHealth
    units: Units


class BatteryHealth(BaseModel):
    max_range: float
    current_range: float
    max_capacity: float
    current_capacity: float
    rated_efficiency: float
    battery_health_percentage: float


# Car Charges Models
class CarChargesModel(BaseModel):
    car: CarDetailsReduced
    charges: list[Charge]
    units: Units


class BatteryDetails(BaseModel):
    start_battery_level: int
    end_battery_level: int


class RangeModel(BaseModel):
    start_range: float
    end_range: float


class Charge(BaseModel):
    charge_id: int
    start_date: datetime
    end_date: datetime
    address: str
    charge_energy_added: float
    charge_energy_used: float
    cost: float
    duration_min: int
    duration_str: str
    battery_details: BatteryDetails
    range_ideal: RangeModel
    range_rated: RangeModel
    outside_temp_avg: float
    odometer: float
    latitude: float
    longitude: float


# Car Charge Models
class CarChargeModel(BaseModel):
    # Used for single charge details
    car: CarDetailsReduced
    charge: ChargeWithDetails
    units: Units


class ChargeWithDetails(Charge):
    charge_details: list[ChargeDetail]


class ChargeDetail(BaseModel):
    detail_id: int
    date: datetime
    battery_level: int
    usable_battery_level: int
    charge_energy_added: float
    not_enough_power_to_heat: bool | None
    charger_details: ChargerDetails
    battery_info: BatteryInfo
    conn_charge_cable: str
    fast_charger_info: FastChargerInfo
    outside_temp: float


class ChargerDetails(BaseModel):
    charger_actual_current: int
    charger_phases: int
    charger_pilot_current: int
    charger_power: int
    charger_voltage: int


class BatteryInfo(BaseModel):
    ideal_battery_range: float
    rated_battery_range: float
    battery_heater: bool
    battery_heater_on: bool
    battery_heater_no_power: bool | None


class FastChargerInfo(BaseModel):
    fast_charger_present: bool
    fast_charger_brand: str
    fast_charger_type: str


# Car Drives Models
class CarDrivesModel(BaseModel):
    car: CarDetailsReduced
    drives: list[Drive]
    units: Units


class Drive(BaseModel):
    drive_id: int
    start_date: datetime
    end_date: datetime
    start_address: str
    end_address: str
    odometer_details: OdometerDetails
    duration_min: int
    duration_str: str
    speed_max: int
    speed_avg: float
    power_max: int
    power_min: int
    battery_details: DriveBatteryDetails
    range_ideal: RangeWithDiff
    range_rated: RangeWithDiff
    outside_temp_avg: float
    inside_temp_avg: float
    energy_consumed_net: float | None
    consumption_net: float | None


class OdometerDetails(BaseModel):
    odometer_start: float
    odometer_end: float
    odometer_distance: float


class DriveBatteryDetails(BaseModel):
    start_usable_battery_level: int
    start_battery_level: int
    end_usable_battery_level: int
    end_battery_level: int
    reduced_range: bool
    is_sufficiently_precise: bool


class RangeWithDiff(BaseModel):
    start_range: float
    end_range: float
    range_diff: float


# Car Drive Models
class CarDriveModel(BaseModel):
    # Used for single drive details
    car: CarDetailsReduced
    drive: DriveWithDetails
    units: Units


class DriveWithDetails(Drive):
    drive_details: list[DriveDetail]


class DriveDetail(BaseModel):
    detail_id: int
    date: datetime
    latitude: float
    longitude: float
    speed: int
    power: int
    odometer: float
    battery_level: int
    usable_battery_level: int | None
    elevation: float | None
    climate_info: DriveClimateInfo
    battery_info: DriveBatteryInfo


class DriveClimateInfo(BaseModel):
    inside_temp: float | None
    outside_temp: float | None
    is_climate_on: bool | None
    fan_status: int | None
    driver_temp_setting: float | None
    passenger_temp_setting: float | None
    is_rear_defroster_on: bool | None
    is_front_defroster_on: bool | None


class DriveBatteryInfo(BaseModel):
    est_battery_range: float | None
    ideal_battery_range: float | None
    rated_battery_range: float | None
    battery_heater: bool | None
    battery_heater_on: bool | None
    battery_heater_no_power: bool | None


# Car Status Models
class CarStatusModel(BaseModel):
    car: CarDetailsReduced
    status: StatusDetails
    units: UnitsStatus


class StatusDetails(BaseModel):
    display_name: str
    state: str
    state_since: datetime
    odometer: float
    car_status: CarStatusSimple
    car_details: CarDetailsSimple
    car_exterior: CarExterior
    car_geodata: CarGeodata
    car_versions: CarVersions
    driving_details: DrivingDetails
    climate_details: ClimateDetails
    battery_details: BatteryDetailsStatus
    charging_details: ChargingDetails
    tpms_details: TPMSDetails


class CarStatusSimple(BaseModel):
    healthy: bool
    locked: bool
    sentry_mode: bool
    windows_open: bool
    doors_open: bool
    driver_front_door_open: bool
    driver_rear_door_open: bool
    passenger_front_door_open: bool
    passenger_rear_door_open: bool
    trunk_open: bool
    frunk_open: bool
    is_user_present: bool
    center_display_state: int


class CarDetailsSimple(BaseModel):
    model: str
    trim_badging: str


class GeoLocation(BaseModel):
    latitude: float
    longitude: float


class CarGeodata(BaseModel):
    geofence: str
    location: GeoLocation
    latitude: float
    longitude: float


class CarVersions(BaseModel):
    version: str
    update_available: bool
    update_version: str


class ActiveRoute(BaseModel):
    destination: str
    energy_at_arrival: float
    distance_to_arrival: float
    minutes_to_arrival: int
    traffic_minutes_delay: int
    location: GeoLocation


class DrivingDetails(BaseModel):
    active_route: ActiveRoute
    active_route_destination: str
    active_route_latitude: float
    active_route_longitude: float
    shift_state: str
    power: int
    speed: int
    heading: int
    elevation: int


class ClimateDetails(BaseModel):
    is_climate_on: bool
    inside_temp: float
    outside_temp: float
    is_preconditioning: bool
    climate_keeper_mode: str


class BatteryDetailsStatus(BaseModel):
    est_battery_range: float
    rated_battery_range: float
    ideal_battery_range: float
    battery_level: int
    usable_battery_level: int


class ChargingDetails(BaseModel):
    plugged_in: bool
    charging_state: str
    charge_energy_added: float
    charge_limit_soc: int
    charge_port_door_open: bool
    charger_actual_current: int
    charger_phases: int
    charger_power: int
    charger_voltage: int
    charge_current_request: int
    charge_current_request_max: int
    scheduled_charging_start_time: datetime | None
    time_to_full_charge: int

    @field_validator("scheduled_charging_start_time", mode="before")
    @classmethod
    def _validate_scheduled_charging_start_time(cls, v: Any) -> datetime | None:
        # Accept None / empty
        if v in (None, ""):
            return None
        # If the server returns a year "0000-..." treat it as missing
        if isinstance(v, str) and v.startswith("0000-"):
            return None
        # Try parse to datetime, fallback to None on failure
        if isinstance(v, str):
            try:
                return datetime.fromisoformat(v)
            except (ValueError, TypeError):
                return None
        return v if isinstance(v, datetime) else None


class TPMSDetails(BaseModel):
    tpms_pressure_fl: float
    tpms_pressure_fr: float
    tpms_pressure_rl: float
    tpms_pressure_rr: float
    tpms_soft_warning_fl: bool
    tpms_soft_warning_fr: bool
    tpms_soft_warning_rl: bool
    tpms_soft_warning_rr: bool


# Car Updates Models
class CarUpdatesModel(BaseModel):
    car: CarDetailsReduced
    updates: list[Update]


class Update(BaseModel):
    update_id: int
    start_date: datetime
    end_date: datetime
    version: str


# Global Settings Models
class GlobalSettingsModel(BaseModel):
    settings: Settings


class Settings(BaseModel):
    setting_id: int
    account_info: AccountInfo
    teslamate_units: Units
    teslamate_webgui: TeslamateWebgui
    teslamate_urls: TeslamateUrls


class AccountInfo(BaseModel):
    inserted_at: datetime
    updated_at: datetime


class TeslamateWebgui(BaseModel):
    preferred_range: str
    language: str


class TeslamateUrls(BaseModel):
    base_url: str
    grafana_url: str
