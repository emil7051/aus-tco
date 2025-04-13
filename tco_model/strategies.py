"""
Calculation Strategies Module

This module implements the Strategy pattern for different calculation methods
that can be used for specific cost components in the TCO model.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple, Union, Type, Protocol, Callable
from datetime import datetime, date

from tco_model.models import (
    ScenarioInput, VehicleType, BETParameters, DieselParameters,
    ElectricityRateType, DieselPriceScenario, FinancingMethod
)

# Calendar year for base calculations
BASE_CALENDAR_YEAR = 2025


class CostCalculationStrategy(ABC):
    """
    Abstract base class defining the interface for cost calculation strategies.
    All cost calculation strategies should inherit from this class.
    """
    
    @abstractmethod
    def calculate_costs(self, scenario: ScenarioInput, year: int) -> float:
        """
        Calculate costs for a specific year.
        
        Args:
            scenario: The scenario input
            year: The year to calculate costs for (0-based index)
            
        Returns:
            float: The calculated cost for the given year
        """
        pass
    
    def get_calendar_year(self, year: int) -> int:
        """
        Convert analysis year (0-based) to calendar year.
        
        Args:
            year: Analysis year (0-based)
            
        Returns:
            int: Calendar year
        """
        return BASE_CALENDAR_YEAR + year


class EnergyConsumptionStrategy(CostCalculationStrategy):
    """
    Abstract base class for energy consumption calculation strategies.
    Different vehicle types can implement different calculation methods.
    """
    
    @abstractmethod
    def calculate_consumption(self, scenario: ScenarioInput, year: int) -> float:
        """
        Calculate the energy consumption for a given year.
        
        Args:
            scenario: The scenario input containing vehicle and operational parameters
            year: The year of analysis (0-based, where 0 is the first year)
            
        Returns:
            float: The energy consumption for the given year (kWh for BET, liters for diesel)
        """
        pass
    
    @abstractmethod
    def calculate_costs(self, scenario: ScenarioInput, year: int) -> float:
        """
        Calculate the energy costs for a given year.
        
        Args:
            scenario: The scenario input containing vehicle and operational parameters
            year: The year of analysis (0-based, where 0 is the first year)
            
        Returns:
            float: The energy cost for the given year in AUD
        """
        pass
    
    def get_calendar_year(self, year: int) -> int:
        """
        Convert analysis year (0-based) to calendar year.
        
        Args:
            year: The year of analysis (0-based)
            
        Returns:
            int: The corresponding calendar year
        """
        return BASE_CALENDAR_YEAR + year


class BETEnergyConsumptionStrategy(EnergyConsumptionStrategy):
    """
    Energy consumption strategy for Battery Electric Trucks (BETs).
    
    Calculates electricity consumption and costs based on:
    - Base energy consumption rate (kWh/km)
    - Vehicle load and operational adjustments
    - Charging efficiency
    - Electricity price with optional demand charges
    """
    
    def calculate_consumption(self, scenario: ScenarioInput, year: int) -> float:
        """
        Calculate the energy consumption for a given year.
        
        Args:
            scenario: The scenario input
            year: The year to calculate consumption for
            
        Returns:
            float: Energy consumption in kWh
        """
        if not isinstance(scenario.vehicle, BETParameters):
            raise ValueError("Vehicle must be a BET for this strategy")
        
        # Extract relevant parameters
        vehicle = scenario.vehicle
        operational = scenario.operational
        consumption_params = vehicle.energy_consumption
        charging_params = vehicle.charging
        annual_distance = operational.annual_distance_km
        
        # Calculate base consumption per km with adjustment factors
        consumption_kwh_per_km = consumption_params.calculate_consumption(
            distance_km=1.0,  # Per km calculation
            load_factor=operational.average_load_factor,
            is_urban=operational.is_urban_operation,
            is_cold=False,  # This could be made dynamic in a more complex model
            is_hot=False    # This could be made dynamic in a more complex model
        )
        
        # Calculate total consumption for the distance
        consumption_kwh = consumption_kwh_per_km * annual_distance
        
        # Account for charging efficiency losses
        grid_consumption_kwh = charging_params.calculate_grid_energy(consumption_kwh)
        
        return grid_consumption_kwh
    
    def calculate_costs(self, scenario: ScenarioInput, year: int) -> float:
        """
        Calculate the electricity costs for a BET in a given year.
        
        This includes:
        1. Energy charges based on consumption and the applicable electricity rate
        2. Demand charges if applicable (for certain electricity tariffs)
        3. Time of use adjustments based on charging strategy
        
        Args:
            scenario: The scenario input
            year: The year to calculate costs for
            
        Returns:
            float: The electricity cost for the given year in AUD
        """
        if not isinstance(scenario.vehicle, BETParameters):
            raise ValueError("Vehicle must be a BET for this strategy")
        
        # Calculate consumption
        consumption_kwh = self.calculate_consumption(scenario, year)
        
        # Get electricity price for the given year
        calendar_year = self.get_calendar_year(year)
        electricity_price = self._get_electricity_price(
            scenario=scenario,
            calendar_year=calendar_year
        )
        
        # Calculate basic energy cost
        energy_cost = consumption_kwh * electricity_price
        
        # Add demand charges if applicable
        demand_charges = self._calculate_demand_charges(scenario, year)
        
        return energy_cost + demand_charges
    
    def _get_electricity_price(self, scenario: ScenarioInput, calendar_year: int) -> float:
        """
        Get the applicable electricity price for the given year and rate type.
        
        Args:
            scenario: The scenario input
            calendar_year: The calendar year
            
        Returns:
            float: The electricity price in AUD/kWh
        """
        if not isinstance(scenario.vehicle, BETParameters):
            raise ValueError("Vehicle must be a BET for this strategy")
        
        # Use the rate type from economic parameters
        rate_type = scenario.economic.electricity_price_type
        charging_strategy = scenario.vehicle.charging.strategy
        
        # This would be implemented to fetch prices from configuration or projections
        # Here's a simplified implementation
        base_prices = {
            ElectricityRateType.AVERAGE_FLAT_RATE: 0.35,  # AUD/kWh
            ElectricityRateType.OFF_PEAK_TOU: 0.20,       # AUD/kWh
            ElectricityRateType.EV_PLAN_LOW: 0.08,        # AUD/kWh
            ElectricityRateType.EV_PLAN_HIGH: 0.15,       # AUD/kWh
        }
        
        # Adjustment for future years (simplistic model)
        years_from_base = calendar_year - BASE_CALENDAR_YEAR
        price_reduction_factor = max(0.0, 1.0 - (0.01 * years_from_base))  # 1% reduction per year
        
        base_price = base_prices.get(rate_type, 0.35)
        adjusted_price = base_price * price_reduction_factor
        
        return adjusted_price
    
    def _calculate_demand_charges(self, scenario: ScenarioInput, year: int) -> float:
        """
        Calculate demand charges if applicable.
        
        Demand charges apply to certain electricity tariffs and depend on:
        1. Maximum power draw (charging power)
        2. Number of chargers
        3. Coincidence factor of charging sessions
        
        Args:
            scenario: The scenario input
            year: The year to calculate for
            
        Returns:
            float: The demand charges in AUD
        """
        if not isinstance(scenario.vehicle, BETParameters):
            raise ValueError("Vehicle must be a BET for this strategy")
        
        # Only apply demand charges for average flat rate (simplified model)
        rate_type = scenario.economic.electricity_price_type
        if rate_type != ElectricityRateType.AVERAGE_FLAT_RATE:
            return 0.0
        
        # Extract parameters
        charging_power_kw = scenario.vehicle.charging.max_charging_power_kw
        
        # Simplified demand charge calculation
        # In reality, this would consider peak demand, time of use, etc.
        demand_charge_rate = 10.0  # AUD per kW per month
        months_per_year = 12
        utilization_factor = 0.5  # Assume we don't always use maximum power
        
        demand_charge = charging_power_kw * utilization_factor * demand_charge_rate * months_per_year
        
        return demand_charge


class DieselConsumptionStrategy(EnergyConsumptionStrategy):
    """
    Energy consumption strategy for diesel trucks.
    
    Calculates fuel consumption and costs based on:
    - Base fuel consumption rate (L/km)
    - Vehicle load and operational adjustments
    - Diesel price projections
    - AdBlue consumption if applicable
    """
    
    def calculate_consumption(self, scenario: ScenarioInput, year: int) -> float:
        """
        Calculate the diesel consumption for an ICE truck in a given year.
        
        The consumption calculation considers:
        1. Base fuel efficiency of the vehicle (L/km)
        2. Load factor adjustment (consumption increases with load)
        3. Operational environment (urban/highway)
        4. Weather adjustments (if applicable)
        
        Args:
            scenario: The scenario input
            year: The year to calculate consumption for
            
        Returns:
            float: The diesel consumption in liters for the given year
        """
        if not isinstance(scenario.vehicle, DieselParameters):
            raise ValueError("Vehicle must be a diesel truck for this strategy")
        
        # Extract relevant parameters
        vehicle = scenario.vehicle
        operational = scenario.operational
        consumption_params = vehicle.fuel_consumption
        annual_distance = operational.annual_distance_km
        
        # Calculate base consumption per km with adjustment factors
        consumption_l_per_km = consumption_params.calculate_consumption(
            distance_km=1.0,  # Per km calculation
            load_factor=operational.average_load_factor,
            is_urban=operational.is_urban_operation,
            is_cold=False,  # This could be made dynamic in a more complex model
            is_hot=False    # This could be made dynamic in a more complex model
        )
        
        # Calculate total consumption for the distance
        total_consumption_l = consumption_l_per_km * annual_distance
        
        return total_consumption_l
    
    def calculate_costs(self, scenario: ScenarioInput, year: int) -> float:
        """
        Calculate the diesel costs for an ICE truck in a given year.
        
        This includes:
        1. Base diesel cost
        2. AdBlue costs if applicable
        
        Args:
            scenario: The scenario input
            year: The year to calculate costs for
            
        Returns:
            float: The diesel cost for the given year in AUD
        """
        if not isinstance(scenario.vehicle, DieselParameters):
            raise ValueError("Vehicle must be a diesel truck for this strategy")
        
        # Calculate consumption
        consumption_liters = self.calculate_consumption(scenario, year)
        
        # Get diesel price for the given year
        calendar_year = self.get_calendar_year(year)
        diesel_price = self._get_diesel_price(
            scenario=scenario,
            calendar_year=calendar_year
        )
        
        # Calculate diesel cost
        diesel_cost = consumption_liters * diesel_price
        
        # Calculate AdBlue costs if applicable
        adblue_cost = self._calculate_adblue_cost(scenario, consumption_liters)
        
        return diesel_cost + adblue_cost
    
    def _get_diesel_price(self, scenario: ScenarioInput, calendar_year: int) -> float:
        """
        Get the diesel price for the given year and price scenario.
        
        Args:
            scenario: The scenario input
            calendar_year: The calendar year
            
        Returns:
            float: The diesel price in AUD/L
        """
        # Use the price scenario from economic parameters
        price_scenario = scenario.economic.diesel_price_scenario
        
        # This would be implemented to fetch prices from configuration or projections
        # Here's a simplified implementation
        base_price = 1.85  # AUD/L in 2025
        
        # Adjustments for different scenarios
        years_from_base = calendar_year - BASE_CALENDAR_YEAR
        
        if price_scenario == DieselPriceScenario.LOW_STABLE:
            # No change in real terms
            return base_price
        elif price_scenario == DieselPriceScenario.HIGH_INCREASE:
            # 5% increase per year in real terms
            return base_price * (1.05 ** years_from_base)
        else:  # Medium increase is default
            # 2.5% increase per year in real terms
            return base_price * (1.025 ** years_from_base)
    
    def _calculate_adblue_cost(self, scenario: ScenarioInput, diesel_consumption_l: float) -> float:
        """
        Calculate AdBlue costs if applicable.
        
        Args:
            scenario: The scenario input
            diesel_consumption_l: Diesel consumption in liters
            
        Returns:
            float: AdBlue cost in AUD
        """
        if not isinstance(scenario.vehicle, DieselParameters):
            raise ValueError("Vehicle must be a diesel truck for this strategy")
        
        # Check if AdBlue is required
        if not scenario.vehicle.engine.adblue_required:
            return 0.0
        
        # Get AdBlue consumption as percentage of diesel
        adblue_percent = scenario.vehicle.engine.adblue_consumption_percent_of_diesel
        if not adblue_percent:
            adblue_percent = 0.05  # Default 5%
        
        # Calculate AdBlue consumption
        adblue_consumption_l = diesel_consumption_l * adblue_percent
        
        # AdBlue price (simplified)
        adblue_price_per_l = 1.0  # AUD/L
        
        return adblue_consumption_l * adblue_price_per_l


class MaintenanceStrategy(CostCalculationStrategy):
    """
    Abstract base class for maintenance cost calculation strategies.
    Different vehicle types can implement different calculation methods.
    """
    
    @abstractmethod
    def calculate_costs(self, scenario: ScenarioInput, year: int) -> float:
        """
        Calculate the maintenance costs for a given year.
        
        Args:
            scenario: The scenario input
            year: The year to calculate costs for
            
        Returns:
            float: The maintenance cost for the given year in AUD
        """
        pass
    
    def get_calendar_year(self, year: int) -> int:
        """
        Convert analysis year (0-based) to calendar year.
        
        Args:
            year: The year of analysis (0-based)
            
        Returns:
            int: The corresponding calendar year
        """
        return BASE_CALENDAR_YEAR + year


class DistanceBasedMaintenanceStrategy(MaintenanceStrategy):
    """
    Base maintenance strategy that calculates costs based on distance traveled.
    
    Includes:
    - Variable costs per kilometer
    - Fixed annual costs
    - Scheduled maintenance intervals
    """
    
    def calculate_costs(self, scenario: ScenarioInput, year: int) -> float:
        """
        Calculate maintenance costs based on distance traveled.
        
        The calculation includes:
        1. Fixed annual maintenance costs
        2. Variable costs based on distance
        3. Age-based adjustments (older vehicles cost more to maintain)
        
        Args:
            scenario: The scenario input
            year: The year to calculate costs for
            
        Returns:
            float: The maintenance cost for the given year in AUD
        """
        # Extract relevant parameters
        vehicle = scenario.vehicle
        maintenance_params = vehicle.maintenance
        annual_distance = scenario.operational.annual_distance_km
        
        # Fixed annual cost component
        fixed_cost = maintenance_params.annual_fixed_default or (
            (maintenance_params.annual_fixed_min + maintenance_params.annual_fixed_max) / 2
        )
        
        # Variable cost based on distance
        variable_cost = maintenance_params.cost_per_km * annual_distance
        
        # Age adjustment factor (simplified model)
        # Maintenance costs increase as the vehicle ages
        age_factor = 1.0 + (year * 0.05)  # 5% increase per year
        
        # Scheduled maintenance costs
        scheduled_services = maintenance_params.calculate_scheduled_services_per_year(annual_distance)
        major_services = maintenance_params.calculate_major_services_per_year(annual_distance)
        
        # Simplified model for scheduled and major service costs
        scheduled_service_cost = 500  # AUD per service
        major_service_cost = 2000     # AUD per major service
        
        # Calculate total scheduled maintenance cost
        scheduled_maintenance_cost = (
            scheduled_services * scheduled_service_cost +
            major_services * major_service_cost
        )
        
        # Total maintenance cost
        total_cost = (fixed_cost + variable_cost) * age_factor + scheduled_maintenance_cost
        
        return total_cost


class BETMaintenanceStrategy(DistanceBasedMaintenanceStrategy):
    """
    Maintenance cost strategy for Battery Electric Trucks (BETs).
    
    BETs generally have:
    - Lower variable maintenance costs due to fewer moving parts
    - Different scheduled maintenance requirements
    - Different fixed costs
    """
    
    def calculate_costs(self, scenario: ScenarioInput, year: int) -> float:
        """
        Calculate the maintenance costs for a BET in a given year.
        
        BETs have unique maintenance characteristics:
        1. Lower drivetrain maintenance (fewer moving parts)
        2. Higher electrical system maintenance
        3. Different scheduled service intervals
        
        Args:
            scenario: The scenario input
            year: The year to calculate costs for
            
        Returns:
            float: The maintenance cost for the given year in AUD
        """
        if not isinstance(scenario.vehicle, BETParameters):
            raise ValueError("Vehicle must be a BET for this strategy")
        
        # Base calculation using the distance-based strategy
        base_cost = super().calculate_costs(scenario, year)
        
        # BET-specific adjustments
        # BETs typically have lower maintenance costs due to simpler drivetrain
        # but may have specific electrical system maintenance needs
        
        # Electrical system inspections (simplified model)
        electrical_inspection_cost = 500  # AUD per year
        
        # Final cost (typically lower than diesel equivalent)
        final_cost = base_cost + electrical_inspection_cost
        
        return final_cost


class DieselMaintenanceStrategy(DistanceBasedMaintenanceStrategy):
    """
    Maintenance cost strategy for diesel trucks.
    
    Diesel trucks generally have:
    - Higher variable maintenance costs due to more complex engines
    - More frequent service intervals
    - Oil changes and other consumables
    """
    
    def calculate_costs(self, scenario: ScenarioInput, year: int) -> float:
        """
        Calculate the maintenance costs for a diesel truck in a given year.
        
        Diesel maintenance includes:
        1. Engine-specific maintenance (oil changes, filters, injectors)
        2. Exhaust system maintenance (DPF, SCR)
        3. Transmission maintenance
        4. More frequent service intervals
        
        Args:
            scenario: The scenario input
            year: The year to calculate costs for
            
        Returns:
            float: The maintenance cost for the given year in AUD
        """
        if not isinstance(scenario.vehicle, DieselParameters):
            raise ValueError("Vehicle must be a diesel truck for this strategy")
        
        # Base calculation using the distance-based strategy
        base_cost = super().calculate_costs(scenario, year)
        
        # Diesel-specific maintenance components
        
        # Engine oil and filter changes
        annual_distance = scenario.operational.annual_distance_km
        oil_change_interval_km = 15000  # km
        oil_changes_per_year = annual_distance / oil_change_interval_km
        oil_change_cost = 300  # AUD per change
        oil_change_total = oil_changes_per_year * oil_change_cost
        
        # Diesel particulate filter (DPF) maintenance
        # Simplified model - age-based probability of DPF cleaning/replacement
        dpf_cost = 0.0
        if year >= 3:  # After 3 years
            dpf_probability = min(0.1 * (year - 2), 0.5)  # Increasing probability with age
            dpf_service_cost = 1500  # AUD
            dpf_cost = dpf_probability * dpf_service_cost
        
        # Add diesel-specific costs
        final_cost = base_cost + oil_change_total + dpf_cost
        
        return final_cost


class ResidualValueStrategy(ABC):
    """
    Abstract base class defining the interface for residual value strategies.
    All residual value strategies should inherit from this class.
    """
    
    @abstractmethod
    def calculate_residual_value(self, scenario: ScenarioInput, year: int) -> float:
        """
        Calculate residual value for a specific year.
        
        Args:
            scenario: The scenario input
            year: The year to calculate residual value for (0-based index)
            
        Returns:
            float: The calculated residual value for the given year
        """
        pass
    
    def get_calendar_year(self, year: int) -> int:
        """
        Convert analysis year (0-based) to calendar year.
        
        Args:
            year: Analysis year (0-based)
            
        Returns:
            int: Calendar year
        """
        return BASE_CALENDAR_YEAR + year


class StandardResidualValueStrategy(ResidualValueStrategy):
    """
    Standard residual value calculation strategy that applies to both BETs and diesel trucks.
    
    Uses predefined depreciation curves based on:
    - Vehicle type
    - Vehicle age
    - Market trends
    """
    
    def calculate_residual_value(self, scenario: ScenarioInput, year: int) -> float:
        """
        Calculate the residual value based on the vehicle's depreciation curve.
        
        The calculation uses:
        1. Initial purchase price
        2. Predefined residual value percentages at key years (e.g., 5, 10, 15)
        3. Interpolation between defined points
        
        Returns 0 for all years except the final year of the analysis period,
        when the residual value is returned as a negative cost (income).
        
        Args:
            scenario: The scenario input
            year: The year to calculate the residual value for
            
        Returns:
            float: The residual value as a negative cost for the final year, 0 otherwise
        """
        # Only calculate residual value for the final year of analysis
        if year != scenario.economic.analysis_period_years - 1:
            return 0.0
        
        # Get original purchase price
        purchase_price = scenario.vehicle.purchase_price
        
        # Calculate vehicle age at the end of analysis
        vehicle_age = year + 1  # 0-based year + 1
        
        # Use the residual value parameters from the vehicle
        residual_params = scenario.vehicle.residual_value
        
        # Calculate residual value
        residual_value = residual_params.calculate_residual_value(
            purchase_price=purchase_price,
            year=vehicle_age,
            use_average=True
        )
        
        # Return as negative cost (income)
        return -residual_value


class BatteryReplacementStrategy(ABC):
    """
    Abstract base class for battery replacement calculation strategies.
    Different approaches can be used for determining when and how to replace batteries.
    """
    
    @abstractmethod
    def calculate_costs(self, scenario: ScenarioInput, year: int) -> float:
        """
        Calculate the battery replacement costs for a given year.
        
        Args:
            scenario: The scenario input
            year: The year to calculate costs for
            
        Returns:
            float: The battery replacement cost for the given year in AUD
        """
        pass
    
    def get_calendar_year(self, year: int) -> int:
        """
        Convert analysis year (0-based) to calendar year.
        
        Args:
            year: The year of analysis (0-based)
            
        Returns:
            int: The corresponding calendar year
        """
        return BASE_CALENDAR_YEAR + year


class DegradationBasedBatteryReplacementStrategy(BatteryReplacementStrategy):
    """
    Battery replacement strategy based on capacity degradation.
    
    Determines replacement timing based on:
    - Annual degradation rate
    - Replacement threshold
    - Expected lifecycle
    """
    
    def calculate_costs(self, scenario: ScenarioInput, year: int) -> float:
        """
        Calculate battery replacement costs based on battery degradation.
        
        The strategy:
        1. Determines if the battery needs replacement based on capacity degradation
        2. Calculates replacement cost based on battery size and future battery prices
        
        Args:
            scenario: The scenario input
            year: The year to calculate costs for
            
        Returns:
            float: The battery replacement cost for the given year in AUD (0 if no replacement)
        """
        if not isinstance(scenario.vehicle, BETParameters):
            return 0.0  # Not applicable to non-BET vehicles
        
        # Extract battery parameters
        battery_params = scenario.vehicle.battery
        
        # Check if the battery needs replacement this year
        needs_replacement = battery_params.needs_replacement(year)
        
        # Battery is already replaced or doesn't need replacement
        if not needs_replacement:
            return 0.0
        
        # Calculate replacement cost
        battery_capacity = battery_params.capacity_kwh
        replacement_cost_factor = battery_params.replacement_cost_factor
        
        # Get the calendar year for battery pricing
        calendar_year = self.get_calendar_year(year)
        
        # Simplified model for future battery prices ($/kWh)
        # This would ideally come from projections in the configuration
        battery_price_per_kwh = self._get_battery_price_per_kwh(calendar_year)
        
        # Calculate total replacement cost
        replacement_cost = battery_capacity * battery_price_per_kwh * replacement_cost_factor
        
        return replacement_cost
    
    def _get_battery_price_per_kwh(self, calendar_year: int) -> float:
        """
        Get the projected battery price per kWh for a given calendar year.
        
        Args:
            calendar_year: The calendar year
            
        Returns:
            float: The battery price in AUD/kWh
        """
        # Base price in 2025
        base_price_per_kwh = 170.0  # AUD/kWh
        
        # Simplified price reduction model
        # Battery prices decline approximately 8% per year in real terms
        years_from_base = calendar_year - BASE_CALENDAR_YEAR
        price_factor = (0.92 ** years_from_base)  # 8% reduction per year
        
        return base_price_per_kwh * price_factor


class InfrastructureStrategy(ABC):
    """
    Abstract base class for infrastructure cost calculation strategies.
    Different vehicle types and operational models require different infrastructure.
    """
    
    @abstractmethod
    def calculate_costs(self, scenario: ScenarioInput, year: int) -> float:
        """
        Calculate the infrastructure costs for a given year.
        
        Args:
            scenario: The scenario input
            year: The year to calculate costs for
            
        Returns:
            float: The infrastructure cost for the given year in AUD
        """
        pass
    
    def get_calendar_year(self, year: int) -> int:
        """
        Convert analysis year (0-based) to calendar year.
        
        Args:
            year: The year of analysis (0-based)
            
        Returns:
            int: The corresponding calendar year
        """
        return BASE_CALENDAR_YEAR + year


class BETInfrastructureStrategy(InfrastructureStrategy):
    """
    Infrastructure cost strategy for Battery Electric Trucks (BETs).
    
    Includes:
    - Charging equipment capital costs
    - Installation costs
    - Maintenance costs
    - Grid connection costs
    """
    
    def calculate_costs(self, scenario: ScenarioInput, year: int) -> float:
        """
        Calculate infrastructure costs for BET charging.
        
        The strategy:
        1. Allocates capital costs to the first year
        2. Applies ongoing maintenance costs each year
        
        Args:
            scenario: The scenario input
            year: The year to calculate costs for
            
        Returns:
            float: The infrastructure cost for the given year in AUD
        """
        if not isinstance(scenario.vehicle, BETParameters):
            return 0.0  # Not applicable to non-BET vehicles
        
        # If no infrastructure parameters are provided, return 0
        if not scenario.vehicle.infrastructure:
            return 0.0
        
        # Extract infrastructure parameters
        infra_params = scenario.vehicle.infrastructure
        
        # Capital costs only in the first year
        capital_cost = 0.0
        if year == 0:
            capital_cost = infra_params.cost_per_truck
        
        # Maintenance costs every year
        maintenance_cost = infra_params.annual_maintenance_cost()
        
        return capital_cost + maintenance_cost


class DieselInfrastructureStrategy(InfrastructureStrategy):
    """
    Infrastructure cost strategy for diesel trucks.
    
    Includes:
    - Refueling infrastructure capital costs (if private)
    - Maintenance costs
    """
    
    def calculate_costs(self, scenario: ScenarioInput, year: int) -> float:
        """
        Calculate infrastructure costs for diesel refueling.
        
        For most diesel operations, infrastructure costs are minimal
        as public refueling infrastructure is used.
        
        Args:
            scenario: The scenario input
            year: The year to calculate costs for
            
        Returns:
            float: The infrastructure cost for the given year in AUD
        """
        # Most diesel operations use public infrastructure, so costs are minimal
        # or already included in the fuel price
        
        # For a private refueling facility, costs could be included here
        private_refueling = False  # This could be a parameter in the scenario
        
        if private_refueling and year == 0:
            # Capital cost for private diesel refueling infrastructure
            return 50000.0  # Example value
        
        # Maintenance costs if applicable
        maintenance_cost = 0.0
        if private_refueling:
            maintenance_cost = 500.0  # Example annual maintenance
        
        return maintenance_cost


class FinancingStrategy(ABC):
    """
    Abstract base class for financing cost calculation strategies.
    Different financing methods (loan, cash purchase) require different calculations.
    """
    
    @abstractmethod
    def calculate_costs(self, scenario: ScenarioInput, year: int) -> float:
        """
        Calculate the financing costs for a given year.
        
        Args:
            scenario: The scenario input
            year: The year to calculate costs for
            
        Returns:
            float: The financing cost for the given year in AUD
        """
        pass
    
    def get_calendar_year(self, year: int) -> int:
        """
        Convert analysis year (0-based) to calendar year.
        
        Args:
            year: The year of analysis (0-based)
            
        Returns:
            int: The corresponding calendar year
        """
        return BASE_CALENDAR_YEAR + year


class LoanFinancingStrategy(FinancingStrategy):
    """
    Financing strategy for loan-based vehicle purchases.
    
    Calculates:
    - Down payment
    - Annual loan payments
    - Interest costs
    """
    
    def calculate_costs(self, scenario: ScenarioInput, year: int) -> float:
        """
        Calculate loan financing costs.
        
        The strategy:
        1. Down payment in year 0
        2. Annual loan payments for the duration of the loan term
        
        Args:
            scenario: The scenario input
            year: The year to calculate costs for
            
        Returns:
            float: The financing cost for the given year in AUD
        """
        if scenario.financing.method != FinancingMethod.LOAN:
            return 0.0
        
        # Get financing parameters
        financing = scenario.financing
        purchase_price = scenario.vehicle.purchase_price
        
        # Down payment in year 0
        if year == 0:
            down_payment = purchase_price * financing.down_payment_percentage
            annual_payment = financing.calculate_annual_payment(purchase_price)
            return down_payment + annual_payment
        
        # Annual payments for the loan term
        if year < financing.loan_term_years:
            return financing.calculate_annual_payment(purchase_price)
        
        # No payments after loan term
        return 0.0


class CashFinancingStrategy(FinancingStrategy):
    """
    Financing strategy for cash purchases.
    
    Simply allocates the full purchase price to year 0.
    """
    
    def calculate_costs(self, scenario: ScenarioInput, year: int) -> float:
        """
        Calculate cash financing costs.
        
        The strategy:
        1. Full purchase price in year 0
        2. No costs in subsequent years
        
        Args:
            scenario: The scenario input
            year: The year to calculate costs for
            
        Returns:
            float: The financing cost for the given year in AUD
        """
        if scenario.financing.method != FinancingMethod.CASH:
            return 0.0
        
        # Full purchase price in year 0
        if year == 0:
            return scenario.vehicle.purchase_price
        
        # No costs in subsequent years
        return 0.0


class InsuranceStrategy(ABC):
    """
    Abstract base class for insurance cost calculation strategies.
    Different vehicle types may have different insurance premiums.
    """
    
    @abstractmethod
    def calculate_costs(self, scenario: ScenarioInput, year: int) -> float:
        """
        Calculate the insurance costs for a given year.
        
        Args:
            scenario: The scenario input
            year: The year to calculate costs for
            
        Returns:
            float: The insurance cost for the given year in AUD
        """
        pass
    
    def get_calendar_year(self, year: int) -> int:
        """
        Convert analysis year (0-based) to calendar year.
        
        Args:
            year: The year of analysis (0-based)
            
        Returns:
            int: The corresponding calendar year
        """
        return BASE_CALENDAR_YEAR + year


class ValueBasedInsuranceStrategy(InsuranceStrategy):
    """
    Insurance strategy that calculates premiums based on vehicle value.
    
    Premium rates vary by:
    - Vehicle type (BET vs diesel)
    - Vehicle value
    - Vehicle age
    """
    
    def calculate_costs(self, scenario: ScenarioInput, year: int) -> float:
        """
        Calculate insurance costs based on vehicle value.
        
        The strategy:
        1. Determines current vehicle value based on depreciation
        2. Applies premium rate based on vehicle type and value
        
        Args:
            scenario: The scenario input
            year: The year to calculate costs for
            
        Returns:
            float: The insurance cost for the given year in AUD
        """
        # Get vehicle parameters
        vehicle = scenario.vehicle
        purchase_price = vehicle.purchase_price
        
        # Calculate current value based on depreciation
        residual_params = vehicle.residual_value
        vehicle_age = year
        current_value = residual_params.calculate_residual_value(
            purchase_price=purchase_price,
            year=vehicle_age,
            use_high=True  # Insurance typically based on higher value estimate
        )
        
        # Base premium rates as percentage of vehicle value
        if isinstance(vehicle, BETParameters):
            # BETs typically have higher rates due to higher value and newer technology
            premium_rate = 0.05  # 5% of value
        else:
            # Diesel trucks have established risk profiles
            premium_rate = 0.04  # 4% of value
        
        # Age-based adjustment (older vehicles may have lower premium rates)
        age_factor = max(0.8, 1.0 - (year * 0.02))  # 2% reduction per year, min 80%
        
        # Calculate premium
        premium = current_value * premium_rate * age_factor
        
        return premium


class RegistrationStrategy(ABC):
    """
    Abstract base class for registration cost calculation strategies.
    Different vehicle types and regions may have different registration fees.
    """
    
    @abstractmethod
    def calculate_costs(self, scenario: ScenarioInput, year: int) -> float:
        """
        Calculate the registration costs for a given year.
        
        Args:
            scenario: The scenario input
            year: The year to calculate costs for
            
        Returns:
            float: The registration cost for the given year in AUD
        """
        pass
    
    def get_calendar_year(self, year: int) -> int:
        """
        Convert analysis year (0-based) to calendar year.
        
        Args:
            year: The year of analysis (0-based)
            
        Returns:
            int: The corresponding calendar year
        """
        return BASE_CALENDAR_YEAR + year


class StandardRegistrationStrategy(RegistrationStrategy):
    """
    Standard registration cost strategy for all vehicle types.
    
    Registration costs vary by:
    - Vehicle type and category
    - Potentially special rates for zero-emission vehicles
    """
    
    def calculate_costs(self, scenario: ScenarioInput, year: int) -> float:
        """
        Calculate standard registration costs.
        
        The strategy applies a base registration cost based on vehicle type
        and category, with potential discounts for zero-emission vehicles.
        
        Args:
            scenario: The scenario input
            year: The year to calculate costs for
            
        Returns:
            float: The registration cost for the given year in AUD
        """
        # Base registration costs by vehicle category
        if scenario.vehicle.category == "rigid":
            base_registration = 3000.0  # AUD
        else:  # Articulated
            base_registration = 5000.0  # AUD
        
        # Zero-emission vehicle discount
        if isinstance(scenario.vehicle, BETParameters):
            # Some regions offer discounts for zero-emission vehicles
            calendar_year = self.get_calendar_year(year)
            
            # Simplified model: discounts phased out over time
            if calendar_year <= 2030:
                discount_rate = max(0.0, 0.2 - (0.02 * (calendar_year - 2025)))  # Starts at 20%, reduces by 2% per year
                discount = base_registration * discount_rate
                return base_registration - discount
        
        return base_registration


class CarbonTaxStrategy(ABC):
    """
    Abstract base class for carbon tax calculation strategies.
    Different vehicle types and emissions profiles lead to different carbon tax liabilities.
    """
    
    @abstractmethod
    def calculate_costs(self, scenario: ScenarioInput, year: int) -> float:
        """
        Calculate the carbon tax for a given year.
        
        Args:
            scenario: The scenario input
            year: The year to calculate costs for
            
        Returns:
            float: The carbon tax for the given year in AUD
        """
        pass
    
    def get_calendar_year(self, year: int) -> int:
        """
        Convert analysis year (0-based) to calendar year.
        
        Args:
            year: The year of analysis (0-based)
            
        Returns:
            int: The corresponding calendar year
        """
        return BASE_CALENDAR_YEAR + year


class FuelBasedCarbonTaxStrategy(CarbonTaxStrategy):
    """
    Carbon tax strategy based on fuel consumption and emissions factors.
    
    Calculates tax based on:
    - Fuel consumption
    - Emissions factor (kg CO2e per liter)
    - Carbon tax rate
    """
    
    def calculate_costs(self, scenario: ScenarioInput, year: int) -> float:
        """
        Calculate carbon tax based on fuel consumption.
        
        The strategy:
        1. Only applies to diesel vehicles (BETs have zero direct emissions)
        2. Calculates emissions from fuel consumption
        3. Applies the carbon tax rate
        
        Args:
            scenario: The scenario input
            year: The year to calculate costs for
            
        Returns:
            float: The carbon tax for the given year in AUD
        """
        # Only diesel vehicles are subject to carbon tax based on fuel consumption
        if not isinstance(scenario.vehicle, DieselParameters):
            return 0.0
        
        # Get carbon tax parameters
        carbon_tax_rate = scenario.economic.get_carbon_tax_rate_for_year(year)
        
        # Simplified: create a consumption strategy to calculate fuel consumption
        consumption_strategy = DieselConsumptionStrategy()
        fuel_consumption_l = consumption_strategy.calculate_consumption(scenario, year)
        
        # Emissions factor for diesel (kg CO2e per liter)
        # This could be obtained from the vehicle configuration
        emissions_factor = 2.68  # kg CO2e per liter
        
        # Calculate total emissions
        emissions_tonnes = (fuel_consumption_l * emissions_factor) / 1000  # Convert kg to tonnes
        
        # Calculate carbon tax
        carbon_tax = emissions_tonnes * carbon_tax_rate
        
        return carbon_tax


class StrategyFactory:
    """
    Factory for creating strategy instances with standardized naming.
    
    This factory manages the registration and retrieval of strategy classes,
    providing a consistent interface for obtaining strategy instances.
    """
    
    # Constants for default keys
    DEFAULT_STRATEGY_KEY = ":"
    
    # Registry of strategies by domain and type
    _strategies: Dict[str, Dict[str, Type[Any]]] = {}
    
    @classmethod
    def register_strategy(cls, domain: str, vehicle_type: Optional[str], 
                         implementation: Optional[str], strategy_class: Type[Any]) -> None:
        """
        Register a strategy class for a domain and type.
        
        Args:
            domain: Strategy domain (e.g., 'energy', 'maintenance')
            vehicle_type: Optional vehicle type ('battery_electric' or 'diesel')
            implementation: Optional implementation approach (e.g., 'distance_based')
            strategy_class: Strategy class to register
        """
        if domain not in cls._strategies:
            cls._strategies[domain] = {}
        
        # Create a key for this strategy variant
        variant_key = f"{vehicle_type or ''}:{implementation or ''}"
        cls._strategies[domain][variant_key] = strategy_class
    
    @classmethod
    def get_strategy(cls, domain: str, vehicle_type: Optional[str] = None,
                    implementation: Optional[str] = None) -> Any:
        """
        Get a strategy instance for a domain and type.
        
        Args:
            domain: Strategy domain (e.g., 'energy', 'maintenance')
            vehicle_type: Optional vehicle type (battery_electric or diesel)
            implementation: Optional implementation approach (e.g., 'distance_based')
            
        Returns:
            Instance of the appropriate strategy
            
        Raises:
            ValueError: If no suitable strategy is found
        """
        if domain not in cls._strategies:
            raise ValueError(f"No strategies registered for domain '{domain}'")
        
        # Try to find a strategy using progressively less specific keys
        # 1. Exact match with both vehicle_type and implementation
        variant_key = f"{vehicle_type or ''}:{implementation or ''}"
        if variant_key in cls._strategies[domain]:
            return cls._strategies[domain][variant_key]()
        
        # 2. Match with just vehicle type
        vehicle_variant = f"{vehicle_type or ''}:"
        if vehicle_variant in cls._strategies[domain]:
            return cls._strategies[domain][vehicle_variant]()
        
        # 3. Match with just implementation
        impl_variant = f":{implementation or ''}"
        if impl_variant in cls._strategies[domain]:
            return cls._strategies[domain][impl_variant]()
        
        # 4. Default strategy (empty key)
        if cls.DEFAULT_STRATEGY_KEY in cls._strategies[domain]:
            return cls._strategies[domain][cls.DEFAULT_STRATEGY_KEY]()
        
        # If all else fails, raise an error
        raise ValueError(
            f"No suitable strategy found for domain '{domain}', "
            f"vehicle type '{vehicle_type}', implementation '{implementation}'"
        )


def register_all_strategies():
    """
    Register all standard strategies with the factory.
    
    This function should be called once at module initialization to 
    register all available strategies with the StrategyFactory.
    """
    # Use naming utility from terminology module
    from tco_model.terminology import get_strategy_class_name
    
    # Energy consumption strategies
    StrategyFactory.register_strategy("energy", "battery_electric", None, BETEnergyConsumptionStrategy)
    StrategyFactory.register_strategy("energy", "diesel", None, DieselConsumptionStrategy)
    
    # Maintenance strategies
    StrategyFactory.register_strategy("maintenance", "battery_electric", None, BETMaintenanceStrategy)
    StrategyFactory.register_strategy("maintenance", "diesel", None, DieselMaintenanceStrategy)
    
    # Standard distance-based variants
    StrategyFactory.register_strategy("maintenance", None, "distance_based", DistanceBasedMaintenanceStrategy)
    
    # Residual value strategies
    StrategyFactory.register_strategy("residual_value", None, None, StandardResidualValueStrategy)
    
    # Financing strategies
    StrategyFactory.register_strategy("financing", None, "loan", LoanFinancingStrategy)
    StrategyFactory.register_strategy("financing", None, "cash", CashFinancingStrategy)
    
    # Infrastructure strategies
    StrategyFactory.register_strategy("infrastructure", "battery_electric", None, BETInfrastructureStrategy)
    StrategyFactory.register_strategy("infrastructure", "diesel", None, DieselInfrastructureStrategy)
    
    # Insurance strategies
    StrategyFactory.register_strategy("insurance", None, None, ValueBasedInsuranceStrategy)
    
    # Registration strategies
    StrategyFactory.register_strategy("registration", None, None, StandardRegistrationStrategy)
    
    # Carbon tax strategies
    StrategyFactory.register_strategy("carbon_tax", None, None, FuelBasedCarbonTaxStrategy)
    
    # Battery replacement strategies
    StrategyFactory.register_strategy(
        "battery_replacement", 
        "battery_electric", 
        None, 
        DegradationBasedBatteryReplacementStrategy
    )


# Update strategy getter functions to use the factory pattern
def get_energy_consumption_strategy(vehicle_type: VehicleType) -> EnergyConsumptionStrategy:
    """
    Get the appropriate energy consumption strategy based on vehicle type.
    
    Args:
        vehicle_type: The vehicle type
        
    Returns:
        EnergyConsumptionStrategy: The appropriate strategy for the vehicle type
    """
    return StrategyFactory.get_strategy("energy", vehicle_type.value)


def get_maintenance_strategy(vehicle_type: VehicleType) -> MaintenanceStrategy:
    """
    Get the appropriate maintenance strategy based on vehicle type.
    
    Args:
        vehicle_type: The vehicle type
        
    Returns:
        MaintenanceStrategy: The appropriate strategy for the vehicle type
    """
    return StrategyFactory.get_strategy("maintenance", vehicle_type.value)


def get_residual_value_strategy() -> ResidualValueStrategy:
    """
    Get the standard residual value strategy.
    
    Returns:
        ResidualValueStrategy: The appropriate strategy for residual value calculation
    """
    return StrategyFactory.get_strategy("residual_value")


def get_battery_replacement_strategy() -> BatteryReplacementStrategy:
    """
    Get the battery replacement strategy.
    
    Returns:
        BatteryReplacementStrategy: The appropriate strategy for battery replacement
    """
    return StrategyFactory.get_strategy("battery_replacement", "battery_electric")


def get_infrastructure_strategy(vehicle_type: VehicleType) -> InfrastructureStrategy:
    """
    Get the appropriate infrastructure strategy based on vehicle type.
    
    Args:
        vehicle_type: The vehicle type
        
    Returns:
        InfrastructureStrategy: The appropriate strategy for the vehicle type
    """
    return StrategyFactory.get_strategy("infrastructure", vehicle_type.value)


def get_financing_strategy(financing_method: FinancingMethod) -> FinancingStrategy:
    """
    Get the appropriate financing strategy based on method.
    
    Args:
        financing_method: The financing method
        
    Returns:
        FinancingStrategy: The appropriate strategy for the financing method
    """
    implementation = financing_method.value  # 'loan' or 'cash'
    return StrategyFactory.get_strategy("financing", None, implementation)


def get_insurance_strategy() -> InsuranceStrategy:
    """
    Get the standard insurance strategy.
    
    Returns:
        InsuranceStrategy: The standard insurance strategy
    """
    return StrategyFactory.get_strategy("insurance")


def get_registration_strategy() -> RegistrationStrategy:
    """
    Get the standard registration strategy.
    
    Returns:
        RegistrationStrategy: The standard registration strategy
    """
    return StrategyFactory.get_strategy("registration")


def get_carbon_tax_strategy() -> CarbonTaxStrategy:
    """
    Get the standard carbon tax strategy.
    
    Returns:
        CarbonTaxStrategy: The standard carbon tax strategy
    """
    return StrategyFactory.get_strategy("carbon_tax")


# Initialize strategy registry
register_all_strategies() 