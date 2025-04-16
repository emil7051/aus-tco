"""
Standardized schemas for configuration files.

This module provides Pydantic schema classes for validating configuration files
across the system, ensuring consistency in data structure and field validation.
"""

from typing import Dict, Any, List, Optional, Union, Tuple
from pydantic import BaseModel, Field, validator, field_validator
from enum import Enum


class VehicleType(str, Enum):
    """Vehicle type enumeration."""
    BATTERY_ELECTRIC = "battery_electric"
    DIESEL = "diesel"


class VehicleCategory(str, Enum):
    """Vehicle category enumeration."""
    RIGID = "rigid"
    ARTICULATED = "articulated"


class VehicleInfoSchema(BaseModel):
    """Schema for vehicle_info section in vehicle config files."""
    type: VehicleType = Field(..., description="Vehicle type (battery_electric or diesel)")
    category: VehicleCategory = Field(..., description="Vehicle category (rigid or articulated)")
    name: str = Field(..., description="Vehicle name/description")


class PurchaseSchema(BaseModel):
    """Schema for purchase section in vehicle config files."""
    base_price_2025: float = Field(..., gt=0, description="Base purchase price in 2025")
    annual_price_decrease_real: float = Field(0.0, ge=0, le=0.5, description="Annual real decrease in price")


class PerformanceSchema(BaseModel):
    """Schema for performance section in vehicle config files."""
    max_payload_tonnes: float = Field(..., gt=0, le=50, description="Maximum payload capacity in tonnes")
    range_km: float = Field(..., gt=0, description="Vehicle range in kilometers")


class BatterySchema(BaseModel):
    """Schema for battery section in BET config files."""
    capacity_kwh: float = Field(..., gt=0, description="Battery capacity in kWh")
    usable_capacity_percentage: float = Field(0.9, ge=0.5, le=1.0, description="Usable capacity percentage")
    degradation_rate_annual: float = Field(0.02, ge=0, le=0.1, description="Annual degradation rate")
    replacement_threshold: float = Field(0.7, ge=0.5, le=0.9, description="Replacement threshold (fraction of original capacity)")
    expected_lifecycle_years: int = Field(8, ge=1, le=20, description="Expected battery lifecycle in years")
    replacement_cost_factor: float = Field(0.8, ge=0, le=1.0, description="Replacement cost as a factor of original cost")


class TemperatureAdjustmentSchema(BaseModel):
    """Schema for temperature adjustment section in energy consumption."""
    hot_weather: float = Field(0.05, ge=0, le=0.5, description="Hot weather adjustment factor")
    cold_weather: float = Field(0.15, ge=0, le=0.5, description="Cold weather adjustment factor")


class EnergyConsumptionSchema(BaseModel):
    """Schema for energy_consumption section in BET config files."""
    base_rate_kwh_per_km: float = Field(..., gt=0, description="Base energy consumption in kWh/km")
    min_rate: float = Field(..., gt=0, description="Minimum energy consumption in kWh/km")
    max_rate: float = Field(..., gt=0, description="Maximum energy consumption in kWh/km")
    load_adjustment_factor: float = Field(0.15, ge=0, description="Load adjustment factor")
    temperature_adjustment: TemperatureAdjustmentSchema = Field(default_factory=TemperatureAdjustmentSchema, description="Temperature adjustments")
    regenerative_braking_efficiency: float = Field(0.65, ge=0, le=1, description="Regenerative braking efficiency")
    regen_contribution_urban: float = Field(0.2, ge=0, le=1, description="Regenerative braking contribution in urban environments")
    
    @field_validator('min_rate', 'max_rate')
    def validate_rates(cls, v, info):
        values = info.data
        if 'base_rate_kwh_per_km' in values and v > values['base_rate_kwh_per_km'] * 2:
            raise ValueError("Rate should not be more than twice the base rate")
        return v


class ChargingStrategyType(str, Enum):
    """Charging strategy type enumeration."""
    OVERNIGHT_DEPOT = "overnight_depot"
    OPPORTUNITY = "opportunity"
    DESTINATION = "destination"
    FAST_CHARGING = "fast_charging"


class ElectricityRateType(str, Enum):
    """Electricity rate type enumeration."""
    FLAT_RATE = "flat_rate"
    OFF_PEAK_TOU = "off_peak_tou"
    AVERAGE_TOU = "average_tou"


class ChargingStrategySchema(BaseModel):
    """Schema for charging strategy section."""
    electricity_rate_type: ElectricityRateType = Field(ElectricityRateType.OFF_PEAK_TOU, description="Electricity rate type for this strategy")


class ChargingSchema(BaseModel):
    """Schema for charging section in BET config files."""
    max_charging_power_kw: float = Field(..., gt=0, description="Maximum charging power in kW")
    charging_efficiency: float = Field(0.9, ge=0.7, le=1.0, description="Charging efficiency")
    charging_strategy: ChargingStrategyType = Field(ChargingStrategyType.OVERNIGHT_DEPOT, description="Charging strategy to use")
    strategies: Dict[str, ChargingStrategySchema] = Field(default_factory=dict, description="Strategy-specific settings")


class MaintenanceDetailedCostsSchema(BaseModel):
    """Schema for detailed_costs section in maintenance."""
    annual_fixed_min: float = Field(..., ge=0, description="Minimum annual fixed maintenance cost")
    annual_fixed_max: float = Field(..., ge=0, description="Maximum annual fixed maintenance cost")


class MaintenanceSchema(BaseModel):
    """Schema for maintenance section in vehicle config files."""
    cost_per_km: float = Field(..., ge=0, description="Maintenance cost per km")
    detailed_costs: MaintenanceDetailedCostsSchema = Field(..., description="Detailed maintenance costs")
    scheduled_maintenance_interval_km: float = Field(..., gt=0, description="Scheduled maintenance interval in km")
    major_service_interval_km: float = Field(..., gt=0, description="Major service interval in km")
    
    @field_validator('major_service_interval_km')
    def validate_intervals(cls, v, info):
        values = info.data
        if 'scheduled_maintenance_interval_km' in values and v < values['scheduled_maintenance_interval_km']:
            raise ValueError("Major service interval must be greater than or equal to scheduled maintenance interval")
        return v


class ResidualValuesSchema(BaseModel):
    """Schema for residual_values section in vehicle config files."""
    year_5: Tuple[float, float] = Field(..., description="Residual value range at 5 years (min, max)")
    year_10: Tuple[float, float] = Field(..., description="Residual value range at 10 years (min, max)")
    year_15: Tuple[float, float] = Field(..., description="Residual value range at 15 years (min, max)")
    
    @field_validator('year_5', 'year_10', 'year_15')
    def validate_range(cls, v):
        if len(v) != 2 or v[0] > v[1] or v[0] < 0 or v[1] > 1:
            raise ValueError("Residual value range must be a tuple of (min, max) with values between 0 and 1, and min <= max")
        return v


class InfrastructureSchema(BaseModel):
    """Schema for infrastructure section in BET config files."""
    charger_hardware_cost: float = Field(..., ge=0, description="Charger hardware cost")
    installation_cost: float = Field(..., ge=0, description="Installation cost")
    maintenance_annual_percentage: float = Field(0.015, ge=0, le=0.1, description="Annual maintenance cost as percentage of hardware cost")
    trucks_per_charger: float = Field(1.0, gt=0, description="Number of trucks per charger")
    grid_upgrade_cost: float = Field(0, ge=0, description="Grid upgrade cost")


class EngineSchema(BaseModel):
    """Schema for engine section in diesel vehicle config files."""
    power_kw: float = Field(..., gt=0, description="Engine power in kW")
    displacement_litres: float = Field(..., gt=0, description="Engine displacement in litres")
    euro_emission_standard: str = Field(..., description="Euro emission standard (e.g., 'Euro 6')")
    adblue_required: bool = Field(True, description="Whether AdBlue is required")
    adblue_consumption_percent_of_diesel: float = Field(0.05, ge=0, le=0.2, description="AdBlue consumption as percentage of diesel consumption")
    co2_per_liter: float = Field(2.68, ge=2.0, le=3.0, description="CO2 emissions per liter of diesel in kg")


class FuelConsumptionSchema(BaseModel):
    """Schema for fuel_consumption section in diesel vehicle config files."""
    base_rate_l_per_km: float = Field(..., gt=0, description="Base fuel consumption in L/km")
    min_rate: float = Field(..., gt=0, description="Minimum fuel consumption in L/km")
    max_rate: float = Field(..., gt=0, description="Maximum fuel consumption in L/km")
    load_adjustment_factor: float = Field(0.25, ge=0, description="Load adjustment factor")
    temperature_adjustment: TemperatureAdjustmentSchema = Field(default_factory=TemperatureAdjustmentSchema, description="Temperature adjustments")
    
    @field_validator('min_rate', 'max_rate')
    def validate_rates(cls, v, info):
        values = info.data
        if 'base_rate_l_per_km' in values and v > values['base_rate_l_per_km'] * 2:
            raise ValueError("Rate should not be more than twice the base rate")
        return v


class BETConfigSchema(BaseModel):
    """Complete schema for BET configuration files."""
    vehicle_info: VehicleInfoSchema
    purchase: PurchaseSchema
    performance: PerformanceSchema
    battery: BatterySchema
    energy_consumption: EnergyConsumptionSchema
    charging: ChargingSchema
    maintenance: MaintenanceSchema
    residual_values: Optional[ResidualValuesSchema] = None
    infrastructure: Optional[InfrastructureSchema] = None


class DieselConfigSchema(BaseModel):
    """Complete schema for diesel vehicle configuration files."""
    vehicle_info: VehicleInfoSchema
    purchase: PurchaseSchema
    performance: PerformanceSchema
    engine: EngineSchema
    fuel_consumption: FuelConsumptionSchema
    maintenance: MaintenanceSchema
    residual_values: Optional[ResidualValuesSchema] = None 