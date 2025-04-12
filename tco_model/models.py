"""
Core data models for the Australian Heavy Vehicle TCO Modeller.

This module defines all Pydantic models used throughout the application,
providing strong typing, validation, and structure to the data.
"""

from datetime import date
from enum import Enum
from typing import Dict, List, Literal, Optional, Tuple, Union
from pydantic import BaseModel, Field, validator, root_validator
from pydantic_settings import BaseSettings
import numpy as np


# --- Utility Types and Enums ---

class VehicleType(str, Enum):
    """Type of vehicle powertrain."""
    DIESEL = "diesel"
    BATTERY_ELECTRIC = "battery_electric"


class VehicleCategory(str, Enum):
    """Category of heavy vehicle."""
    RIGID = "rigid"
    ARTICULATED = "articulated"


class ChargingStrategy(str, Enum):
    """Charging strategy for electric vehicles."""
    OVERNIGHT_DEPOT = "overnight_depot"
    OPPORTUNITY = "opportunity"
    MIXED = "mixed"


class FinancingMethod(str, Enum):
    """Method of financing the vehicle purchase."""
    LOAN = "loan"
    CASH = "cash"


class ElectricityRateType(str, Enum):
    """Type of electricity rate structure."""
    AVERAGE_FLAT_RATE = "average_flat_rate"
    OFF_PEAK_TOU = "off_peak_tou"
    EV_PLAN_LOW = "ev_plan_low"
    EV_PLAN_HIGH = "ev_plan_high"


class DieselPriceScenario(str, Enum):
    """Scenario for diesel price projections."""
    LOW_STABLE = "low_stable"
    MEDIUM_INCREASE = "medium_increase"
    HIGH_INCREASE = "high_increase"


# --- Parameter Models ---

class RangeValue(BaseModel):
    """Represents a value with a min, max, and optionally an average/default."""
    min: float
    max: float
    default: Optional[float] = None
    average: Optional[float] = None
    
    @root_validator(skip_on_failure=True)
    def set_default_if_missing(cls, values):
        """Set default to average of min and max if not provided."""
        if values.get('default') is None and 'min' in values and 'max' in values:
            values['default'] = (values['min'] + values['max']) / 2
        return values
    
    @validator('default')
    def default_in_range(cls, v, values):
        """Validate that default value is within min-max range."""
        if v is not None and 'min' in values and 'max' in values:
            if v < values['min'] or v > values['max']:
                raise ValueError(f'Default value {v} must be between min {values["min"]} and max {values["max"]}')
        return v


class YearlyValue(BaseModel):
    """A value that changes by year."""
    values: Dict[int, Union[float, List[float], Tuple[float, float]]]
    
    def get_for_year(self, year: int, interpolate: bool = True) -> Union[float, List[float], Tuple[float, float]]:
        """Get the value for a specific year, with optional interpolation."""
        if year in self.values:
            return self.values[year]
        
        if not interpolate:
            # Find the closest year that's less than or equal to the target year
            valid_years = [y for y in self.values.keys() if y <= year]
            if valid_years:
                return self.values[max(valid_years)]
            return self.values[min(self.values.keys())]
        
        # Interpolate between years
        years = sorted(self.values.keys())
        if year < years[0]:
            return self.values[years[0]]  # Use earliest value for years before first defined
        if year > years[-1]:
            return self.values[years[-1]]  # Use latest value for years after last defined
        
        # Find surrounding years for interpolation
        lower_year = max([y for y in years if y <= year])
        upper_year = min([y for y in years if y >= year])
        
        if lower_year == upper_year:
            return self.values[lower_year]
        
        # Linear interpolation
        lower_val = self.values[lower_year]
        upper_val = self.values[upper_year]
        
        weight = (year - lower_year) / (upper_year - lower_year)
        
        # Handle different value types
        if isinstance(lower_val, (int, float)) and isinstance(upper_val, (int, float)):
            return lower_val + weight * (upper_val - lower_val)
        elif isinstance(lower_val, (list, tuple)) and isinstance(upper_val, (list, tuple)):
            # Interpolate each element of the list/tuple
            if len(lower_val) != len(upper_val):
                raise ValueError(f"Cannot interpolate between values with different lengths: {lower_val} and {upper_val}")
            
            result = []
            for i in range(len(lower_val)):
                interpolated = lower_val[i] + weight * (upper_val[i] - lower_val[i])
                result.append(interpolated)
            
            if isinstance(lower_val, tuple):
                return tuple(result)
            return result
        
        # Cannot interpolate between different types
        return lower_val  # Default to lower value if types don't match


class BatteryParameters(BaseModel):
    """Parameters related to the battery of an electric vehicle."""
    capacity_kwh: float = Field(..., gt=0, description="Battery capacity in kilowatt-hours")
    usable_capacity_percentage: float = Field(0.9, ge=0, le=1, description="Percentage of battery capacity that is usable")
    degradation_rate_annual: float = Field(0.02, ge=0, le=0.2, description="Annual degradation rate of battery capacity")
    replacement_threshold: float = Field(0.7, ge=0, le=1, description="Threshold at which battery is replaced (as fraction of original capacity)")
    expected_lifecycle_years: Optional[int] = Field(None, ge=0, description="Expected lifecycle of battery in years")
    replacement_cost_factor: float = Field(0.8, ge=0, le=1, description="Replacement cost as a fraction of new battery cost")
    
    @property
    def usable_capacity_kwh(self) -> float:
        """Calculate usable battery capacity."""
        return self.capacity_kwh * self.usable_capacity_percentage
    
    def capacity_at_year(self, year: int) -> float:
        """Calculate battery capacity after a given number of years of degradation."""
        remaining_capacity_fraction = (1 - self.degradation_rate_annual) ** year
        return self.capacity_kwh * remaining_capacity_fraction
    
    def usable_capacity_at_year(self, year: int) -> float:
        """Calculate usable battery capacity after a given number of years of degradation."""
        return self.capacity_at_year(year) * self.usable_capacity_percentage
    
    def needs_replacement(self, year: int) -> bool:
        """Determine if battery needs replacement at a given year."""
        remaining_capacity_fraction = (1 - self.degradation_rate_annual) ** year
        return remaining_capacity_fraction < self.replacement_threshold


class EngineParameters(BaseModel):
    """Parameters related to the engine of a diesel vehicle."""
    power_kw: float = Field(..., gt=0, description="Engine power in kilowatts")
    displacement_litres: float = Field(..., gt=0, description="Engine displacement in litres")
    euro_emission_standard: str = Field(..., description="Euro emission standard of the engine")
    adblue_required: bool = Field(False, description="Whether AdBlue (DEF) is required")
    adblue_consumption_percent_of_diesel: Optional[float] = Field(None, ge=0, le=1, description="AdBlue consumption as a percentage of diesel consumption")


class EnergyConsumptionParameters(BaseModel):
    """Parameters related to energy consumption of a vehicle."""
    base_rate: float = Field(..., gt=0, description="Base energy consumption rate")
    min_rate: float = Field(..., gt=0, description="Minimum energy consumption rate")
    max_rate: float = Field(..., gt=0, description="Maximum energy consumption rate")
    load_adjustment_factor: float = Field(0, ge=0, description="Factor for adjusting consumption based on load")
    hot_weather_adjustment: float = Field(0, ge=0, description="Factor for adjusting consumption in hot weather")
    cold_weather_adjustment: float = Field(0, ge=0, description="Factor for adjusting consumption in cold weather")
    
    @validator('base_rate')
    def base_rate_in_range(cls, v, values):
        """Validate that base rate is within min-max range."""
        if 'min_rate' in values and 'max_rate' in values:
            if v < values['min_rate'] or v > values['max_rate']:
                raise ValueError(f'Base rate {v} must be between min {values["min_rate"]} and max {values["max_rate"]}')
        return v


class BETConsumptionParameters(EnergyConsumptionParameters):
    """Energy consumption parameters specific to battery electric trucks."""
    base_rate: float = Field(..., gt=0, description="Base energy consumption in kWh/km")
    regenerative_braking_efficiency: float = Field(0.65, ge=0, le=1, description="Efficiency of regenerative braking")
    regen_contribution_urban: float = Field(0.2, ge=0, le=1, description="Contribution of regenerative braking to energy saving in urban driving")
    
    def calculate_consumption(self, distance_km: float, load_factor: float = 1.0, 
                             is_urban: bool = False, is_cold: bool = False, 
                             is_hot: bool = False) -> float:
        """Calculate energy consumption for a given distance and conditions."""
        # Start with base consumption
        consumption_kwh_per_km = self.base_rate
        
        # Adjust for load
        if load_factor < 1.0:
            # Linear adjustment based on load factor and adjustment factor
            load_adjustment = (1.0 - load_factor) * self.load_adjustment_factor
            consumption_kwh_per_km -= load_adjustment
        
        # Adjust for temperature
        if is_cold:
            consumption_kwh_per_km *= (1 + self.cold_weather_adjustment)
        elif is_hot:
            consumption_kwh_per_km *= (1 + self.hot_weather_adjustment)
        
        # Adjust for regenerative braking in urban environments
        if is_urban and self.regenerative_braking_efficiency > 0:
            consumption_kwh_per_km *= (1 - self.regen_contribution_urban)
        
        # Calculate total consumption
        total_consumption_kwh = consumption_kwh_per_km * distance_km
        
        return total_consumption_kwh


class DieselConsumptionParameters(EnergyConsumptionParameters):
    """Energy consumption parameters specific to diesel trucks."""
    base_rate: float = Field(..., gt=0, description="Base fuel consumption in litres/km")
    
    def calculate_consumption(self, distance_km: float, load_factor: float = 1.0,
                             is_urban: bool = False, is_cold: bool = False,
                             is_hot: bool = False) -> float:
        """Calculate diesel consumption for a given distance and conditions."""
        # Start with base consumption
        consumption_l_per_km = self.base_rate
        
        # Adjust for load
        if load_factor < 1.0:
            # Linear adjustment based on load factor and adjustment factor
            load_adjustment = (1.0 - load_factor) * self.load_adjustment_factor
            consumption_l_per_km -= load_adjustment
        
        # Adjust for temperature
        if is_cold:
            consumption_l_per_km *= (1 + self.cold_weather_adjustment)
        elif is_hot:
            consumption_l_per_km *= (1 + self.hot_weather_adjustment)
        
        # Calculate total consumption
        total_consumption_l = consumption_l_per_km * distance_km
        
        return total_consumption_l


class ChargingParameters(BaseModel):
    """Parameters related to charging of electric vehicles."""
    max_charging_power_kw: float = Field(..., gt=0, description="Maximum charging power in kilowatts")
    charging_efficiency: float = Field(0.9, ge=0, le=1, description="Charging efficiency (grid to battery)")
    strategy: ChargingStrategy = Field(ChargingStrategy.OVERNIGHT_DEPOT, description="Default charging strategy")
    electricity_rate_type: ElectricityRateType = Field(ElectricityRateType.AVERAGE_FLAT_RATE, description="Type of electricity rate to use")
    
    def calculate_charging_time(self, energy_required_kwh: float) -> float:
        """Calculate time required to charge a given amount of energy."""
        # Account for charging efficiency
        grid_energy_required_kwh = energy_required_kwh / self.charging_efficiency
        
        # Time in hours
        time_hours = grid_energy_required_kwh / self.max_charging_power_kw
        
        return time_hours
    
    def calculate_grid_energy(self, battery_energy_kwh: float) -> float:
        """Calculate grid energy required to provide a given battery energy."""
        return battery_energy_kwh / self.charging_efficiency


class MaintenanceParameters(BaseModel):
    """Parameters related to vehicle maintenance."""
    cost_per_km: float = Field(..., ge=0, description="Maintenance cost per kilometer")
    annual_fixed_min: float = Field(..., ge=0, description="Minimum annual fixed maintenance cost")
    annual_fixed_max: float = Field(..., ge=0, description="Maximum annual fixed maintenance cost")
    annual_fixed_default: Optional[float] = Field(None, ge=0, description="Default annual fixed maintenance cost")
    scheduled_maintenance_interval_km: float = Field(..., gt=0, description="Interval for scheduled maintenance in kilometers")
    major_service_interval_km: float = Field(..., gt=0, description="Interval for major services in kilometers")
    
    @root_validator(skip_on_failure=True)
    def set_default_fixed_cost(cls, values):
        """Set default fixed cost to average of min and max if not provided."""
        if values.get('annual_fixed_default') is None and 'annual_fixed_min' in values and 'annual_fixed_max' in values:
            values['annual_fixed_default'] = (values['annual_fixed_min'] + values['annual_fixed_max']) / 2
        return values
    
    def calculate_annual_cost(self, annual_distance_km: float) -> float:
        """Calculate total annual maintenance cost."""
        # Variable cost based on distance
        variable_cost = self.cost_per_km * annual_distance_km
        
        # Fixed annual cost
        fixed_cost = self.annual_fixed_default or ((self.annual_fixed_min + self.annual_fixed_max) / 2)
        
        return variable_cost + fixed_cost
    
    def calculate_scheduled_services_per_year(self, annual_distance_km: float) -> float:
        """Calculate the number of scheduled services per year."""
        return annual_distance_km / self.scheduled_maintenance_interval_km
    
    def calculate_major_services_per_year(self, annual_distance_km: float) -> float:
        """Calculate the number of major services per year."""
        return annual_distance_km / self.major_service_interval_km


class InfrastructureParameters(BaseModel):
    """Parameters related to charging infrastructure for electric vehicles."""
    charger_hardware_cost: float = Field(..., ge=0, description="Cost of charging hardware")
    installation_cost: float = Field(..., ge=0, description="Cost of charger installation")
    maintenance_annual_percentage: float = Field(0.015, ge=0, le=1, description="Annual maintenance cost as percentage of capital")
    trucks_per_charger: float = Field(1.0, gt=0, description="Number of trucks sharing each charger")
    grid_upgrade_cost: Optional[float] = Field(0, ge=0, description="Cost of grid upgrades required")
    
    @property
    def total_capital_cost(self) -> float:
        """Calculate total capital cost of infrastructure."""
        return self.charger_hardware_cost + self.installation_cost + self.grid_upgrade_cost
    
    @property
    def cost_per_truck(self) -> float:
        """Calculate infrastructure cost per truck."""
        return self.total_capital_cost / self.trucks_per_charger
    
    def annual_maintenance_cost(self) -> float:
        """Calculate annual maintenance cost of infrastructure."""
        return self.total_capital_cost * self.maintenance_annual_percentage


class ResidualValueParameters(BaseModel):
    """Parameters for calculating residual value of vehicles."""
    year_5_range: Tuple[float, float] = Field(..., description="Residual value range at 5 years (as fraction of purchase price)")
    year_10_range: Tuple[float, float] = Field(..., description="Residual value range at 10 years (as fraction of purchase price)")
    year_15_range: Tuple[float, float] = Field(..., description="Residual value range at 15 years (as fraction of purchase price)")
    
    def calculate_residual_value(self, purchase_price: float, 
                                year: int, 
                                use_average: bool = True,
                                use_high: bool = False) -> float:
        """Calculate residual value for a specific year."""
        # Define our known points
        year_points = [5, 10, 15]
        
        # Choose which value from the range to use
        if use_high:
            value_points = [self.year_5_range[1], self.year_10_range[1], self.year_15_range[1]]
        elif use_average:
            value_points = [
                (self.year_5_range[0] + self.year_5_range[1]) / 2,
                (self.year_10_range[0] + self.year_10_range[1]) / 2,
                (self.year_15_range[0] + self.year_15_range[1]) / 2
            ]
        else:
            value_points = [self.year_5_range[0], self.year_10_range[0], self.year_15_range[0]]
        
        # Handle years at or beyond our defined points
        if year <= 0:
            return purchase_price
        elif year >= 15:
            fraction = value_points[2]
            return purchase_price * fraction
        
        # Interpolate for years between our defined points
        # Find surrounding years for interpolation
        if year <= 5:
            lower_idx, upper_idx = 0, 0  # 0 and 5 years
            lower_year, upper_year = 0, 5
            lower_val, upper_val = 1.0, value_points[0]  # Start at 100% of purchase price
        elif year <= 10:
            lower_idx, upper_idx = 0, 1  # 5 and 10 years
            lower_year, upper_year = 5, 10
            lower_val, upper_val = value_points[0], value_points[1]
        else:  # year < 15
            lower_idx, upper_idx = 1, 2  # 10 and 15 years
            lower_year, upper_year = 10, 15
            lower_val, upper_val = value_points[1], value_points[2]
        
        # Linear interpolation between the two points
        weight = (year - lower_year) / (upper_year - lower_year)
        fraction = lower_val + weight * (upper_val - lower_val)
        
        return purchase_price * fraction


class FinancingParameters(BaseModel):
    """Parameters related to vehicle financing."""
    method: FinancingMethod = Field(FinancingMethod.LOAN, description="Financing method (loan or cash)")
    loan_term_years: int = Field(5, ge=1, le=20, description="Loan term in years")
    loan_interest_rate: float = Field(0.07, ge=0, le=0.5, description="Annual interest rate on loan")
    down_payment_percentage: float = Field(0.2, ge=0, le=1, description="Down payment as percentage of purchase price")
    
    def calculate_loan_amount(self, purchase_price: float) -> float:
        """Calculate loan amount after down payment."""
        return purchase_price * (1 - self.down_payment_percentage)
    
    def calculate_monthly_payment(self, purchase_price: float) -> float:
        """Calculate monthly loan payment."""
        if self.method != FinancingMethod.LOAN:
            return 0
        
        loan_amount = self.calculate_loan_amount(purchase_price)
        monthly_rate = self.loan_interest_rate / 12
        num_payments = self.loan_term_years * 12
        
        if monthly_rate == 0:
            return loan_amount / num_payments
        
        # PMT formula
        payment = loan_amount * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)
        return payment
    
    def calculate_annual_payment(self, purchase_price: float) -> float:
        """Calculate total annual loan payment."""
        return self.calculate_monthly_payment(purchase_price) * 12
    
    def calculate_total_loan_cost(self, purchase_price: float) -> float:
        """Calculate total cost of the loan including interest."""
        monthly_payment = self.calculate_monthly_payment(purchase_price)
        num_payments = self.loan_term_years * 12
        return monthly_payment * num_payments


class EconomicParameters(BaseModel):
    """Economic parameters for TCO calculation."""
    discount_rate_real: float = Field(0.07, ge=0, le=0.5, description="Real discount rate for NPV calculations")
    inflation_rate: float = Field(0.025, ge=0, le=0.5, description="Annual inflation rate")
    analysis_period_years: int = Field(15, ge=1, le=30, description="Analysis period in years")
    electricity_price_type: ElectricityRateType = Field(ElectricityRateType.AVERAGE_FLAT_RATE, description="Type of electricity price to use")
    diesel_price_scenario: DieselPriceScenario = Field(DieselPriceScenario.MEDIUM_INCREASE, description="Diesel price scenario to use")
    carbon_tax_rate_aud_per_tonne: float = Field(30.0, ge=0, description="Carbon tax rate in AUD per tonne CO2e")
    carbon_tax_annual_increase_rate: float = Field(0.05, ge=0, description="Annual increase rate of carbon tax")
    
    @property
    def discount_rate_nominal(self) -> float:
        """Calculate nominal discount rate from real rate and inflation."""
        return (1 + self.discount_rate_real) * (1 + self.inflation_rate) - 1
    
    def get_carbon_tax_rate_for_year(self, year: int) -> float:
        """Get carbon tax rate for a specific year, accounting for annual increases."""
        return self.carbon_tax_rate_aud_per_tonne * ((1 + self.carbon_tax_annual_increase_rate) ** year)
    
    def calculate_npv(self, cash_flows: List[float]) -> float:
        """Calculate Net Present Value of a series of cash flows."""
        if len(cash_flows) == 0:
            return 0
            
        # Use nominal discount rate for NPV calculations
        discount_rate = self.discount_rate_nominal
        
        # Calculate NPV using vectorized operations
        periods = np.arange(len(cash_flows))
        discount_factors = 1 / (1 + discount_rate) ** periods
        
        return sum(np.array(cash_flows) * discount_factors)


class OperationalParameters(BaseModel):
    """Operational parameters for TCO calculation."""
    annual_distance_km: float = Field(..., gt=0, description="Annual distance traveled in kilometers")
    operating_days_per_year: int = Field(250, ge=1, le=365, description="Number of operating days per year")
    vehicle_life_years: int = Field(15, ge=1, le=30, description="Expected vehicle life in years")
    daily_distance_km: Optional[float] = Field(None, gt=0, description="Average daily distance in kilometers")
    requires_overnight_charging: bool = Field(True, description="Whether the vehicle requires overnight charging")
    is_urban_operation: bool = Field(False, description="Whether the vehicle operates in urban environments")
    average_load_factor: float = Field(0.8, ge=0, le=1, description="Average load factor (0-1, where 1 is full load)")
    
    @root_validator(skip_on_failure=True)
    def set_daily_distance(cls, values):
        """Calculate daily distance from annual distance if not provided."""
        if values.get('daily_distance_km') is None and 'annual_distance_km' in values and 'operating_days_per_year' in values:
            operating_days = values.get('operating_days_per_year')
            if operating_days > 0:
                values['daily_distance_km'] = values['annual_distance_km'] / operating_days
        return values


# --- Vehicle Models ---

class VehicleBaseParameters(BaseModel):
    """Base parameters common to all vehicle types."""
    name: str = Field(..., description="Name/description of the vehicle")
    type: VehicleType = Field(..., description="Type of vehicle (diesel, battery_electric)")
    category: VehicleCategory = Field(..., description="Category of vehicle (rigid, articulated)")
    purchase_price: float = Field(..., gt=0, description="Purchase price in AUD")
    annual_price_decrease_real: float = Field(0, ge=0, le=0.5, description="Annual real decrease in purchase price")
    max_payload_tonnes: float = Field(..., gt=0, description="Maximum payload in tonnes")
    range_km: float = Field(..., gt=0, description="Range in kilometers")
    
    def get_purchase_price_for_year(self, year: int, base_year: int = 2025) -> float:
        """Calculate purchase price for a future year, accounting for real price decreases."""
        years_elapsed = year - base_year
        if years_elapsed <= 0:
            return self.purchase_price
        
        # Apply real price decrease
        price = self.purchase_price * ((1 - self.annual_price_decrease_real) ** years_elapsed)
        return price


class BETParameters(VehicleBaseParameters):
    """Parameters specific to Battery Electric Trucks."""
    type: Literal[VehicleType.BATTERY_ELECTRIC] = VehicleType.BATTERY_ELECTRIC
    battery: BatteryParameters
    energy_consumption: BETConsumptionParameters
    charging: ChargingParameters
    maintenance: MaintenanceParameters
    residual_value: ResidualValueParameters
    infrastructure: Optional[InfrastructureParameters] = None


class DieselParameters(VehicleBaseParameters):
    """Parameters specific to Diesel Trucks."""
    type: Literal[VehicleType.DIESEL] = VehicleType.DIESEL
    engine: EngineParameters
    fuel_consumption: DieselConsumptionParameters
    maintenance: MaintenanceParameters
    residual_value: ResidualValueParameters


# --- Input and Output Models ---

class ScenarioInput(BaseModel):
    """Input parameters for a TCO scenario."""
    scenario_name: str = Field(..., description="Name of the scenario")
    vehicle: Union[BETParameters, DieselParameters] = Field(..., description="Vehicle parameters")
    operational: OperationalParameters = Field(..., description="Operational parameters")
    economic: EconomicParameters = Field(..., description="Economic parameters")
    financing: FinancingParameters = Field(..., description="Financing parameters")
    created_date: date = Field(default_factory=date.today, description="Date the scenario was created")


class AnnualCosts(BaseModel):
    """Breakdown of costs for a single year."""
    year: int = Field(..., ge=0, description="Year of analysis (0-based)")
    calendar_year: int = Field(..., ge=2020, description="Calendar year")
    acquisition: float = Field(0, description="Acquisition costs (loan payments or purchase)")
    energy: float = Field(0, description="Energy costs (electricity or diesel)")
    maintenance: float = Field(0, description="Maintenance costs")
    infrastructure: float = Field(0, description="Infrastructure costs")
    battery_replacement: float = Field(0, description="Battery replacement costs")
    insurance: float = Field(0, description="Insurance costs")
    registration: float = Field(0, description="Registration costs")
    carbon_tax: float = Field(0, description="Carbon tax")
    other_taxes: float = Field(0, description="Other taxes and levies")
    residual_value: float = Field(0, description="Residual value (negative cost/income)")
    
    @property
    def total(self) -> float:
        """Calculate total cost for the year."""
        # Sum all costs
        sum_costs = (self.acquisition + self.energy + self.maintenance + 
                    self.infrastructure + self.battery_replacement +
                    self.insurance + self.registration +
                    self.carbon_tax + self.other_taxes + self.residual_value)
        return sum_costs


class NPVCosts(BaseModel):
    """Net Present Value of costs over the analysis period."""
    acquisition: float = Field(0, description="NPV of acquisition costs")
    energy: float = Field(0, description="NPV of energy costs")
    maintenance: float = Field(0, description="NPV of maintenance costs")
    infrastructure: float = Field(0, description="NPV of infrastructure costs")
    battery_replacement: float = Field(0, description="NPV of battery replacement costs")
    insurance: float = Field(0, description="NPV of insurance costs")
    registration: float = Field(0, description="NPV of registration costs")
    carbon_tax: float = Field(0, description="NPV of carbon tax")
    other_taxes: float = Field(0, description="NPV of other taxes and levies")
    residual_value: float = Field(0, description="NPV of residual value (negative cost/income)")
    
    @property
    def total(self) -> float:
        """Calculate total NPV."""
        # Sum all NPV costs
        sum_npv = (self.acquisition + self.energy + self.maintenance + 
                  self.infrastructure + self.battery_replacement +
                  self.insurance + self.registration +
                  self.carbon_tax + self.other_taxes + self.residual_value)
        return sum_npv


class TCOOutput(BaseModel):
    """Output of TCO calculation."""
    scenario_name: str = Field(..., description="Name of the scenario")
    vehicle_name: str = Field(..., description="Name of the vehicle")
    vehicle_type: VehicleType = Field(..., description="Type of vehicle")
    analysis_period_years: int = Field(..., ge=1, description="Analysis period in years")
    total_distance_km: float = Field(..., gt=0, description="Total distance over analysis period")
    annual_costs: List[AnnualCosts] = Field(..., description="Annual breakdown of costs")
    npv_costs: NPVCosts = Field(..., description="Net Present Value of costs")
    total_nominal_cost: float = Field(..., description="Total nominal cost over analysis period")
    npv_total: float = Field(..., description="NPV of total cost")
    lcod_per_km: float = Field(..., description="Levelized Cost of Driving per km")
    calculation_date: date = Field(default_factory=date.today, description="Date of calculation")
    
    @property
    def total_acquisition_cost(self) -> float:
        """Calculate total nominal acquisition cost."""
        return sum(year.acquisition for year in self.annual_costs)
    
    @property
    def total_energy_cost(self) -> float:
        """Calculate total nominal energy cost."""
        return sum(year.energy for year in self.annual_costs)
    
    @property
    def total_maintenance_cost(self) -> float:
        """Calculate total nominal maintenance cost."""
        return sum(year.maintenance for year in self.annual_costs)
    
    @property
    def total_other_costs(self) -> float:
        """Calculate total of other costs."""
        return (self.total_nominal_cost - self.total_acquisition_cost - 
                self.total_energy_cost - self.total_maintenance_cost)


class ComparisonResult(BaseModel):
    """Comparison between two TCO results."""
    scenario_1: TCOOutput
    scenario_2: TCOOutput
    npv_difference: float
    npv_difference_percentage: float
    lcod_difference: float
    lcod_difference_percentage: float
    payback_year: Optional[int] = None
    
    @classmethod
    def create(cls, scenario_1: TCOOutput, scenario_2: TCOOutput):
        """Create a comparison between two TCO results."""
        # Calculate differences
        npv_diff = scenario_1.npv_total - scenario_2.npv_total
        npv_diff_pct = (npv_diff / scenario_2.npv_total) * 100 if scenario_2.npv_total != 0 else float('inf')
        
        lcod_diff = scenario_1.lcod_per_km - scenario_2.lcod_per_km
        lcod_diff_pct = (lcod_diff / scenario_2.lcod_per_km) * 100 if scenario_2.lcod_per_km != 0 else float('inf')
        
        # Calculate payback year if applicable
        payback_year = None
        if npv_diff < 0:  # Scenario 1 is cheaper overall
            # Calculate cumulative costs for each year
            cumulative_1 = [0]
            cumulative_2 = [0]
            
            for i in range(len(scenario_1.annual_costs)):
                cumulative_1.append(cumulative_1[-1] + scenario_1.annual_costs[i].total)
                cumulative_2.append(cumulative_2[-1] + scenario_2.annual_costs[i].total)
            
            # Find the first year where cumulative cost of scenario 1
            # becomes less than scenario 2
            for year in range(1, len(cumulative_1)):
                if cumulative_1[year] < cumulative_2[year]:
                    payback_year = year
                    break
        
        return cls(
            scenario_1=scenario_1,
            scenario_2=scenario_2,
            npv_difference=npv_diff,
            npv_difference_percentage=npv_diff_pct,
            lcod_difference=lcod_diff,
            lcod_difference_percentage=lcod_diff_pct,
            payback_year=payback_year
        )


# --- App Settings and Configuration ---

class AppSettings(BaseSettings):
    """Application settings that can be loaded from environment variables."""
    app_name: str = "Australian Heavy Vehicle TCO Modeller"
    app_version: str = "1.0.0"
    debug_mode: bool = False
    log_level: str = "INFO"
    config_path: str = "config"
    vehicles_config_path: str = "config/vehicles"
    defaults_config_path: str = "config/defaults"
    
    class Config:
        env_file = ".env"
        env_prefix = "TCO_"