"""
Cost Calculation Module

This module contains functions for calculating individual cost components
for the TCO model. Each function calculates a specific cost for a given year.
"""

from typing import Dict, Any
import numpy as np
import numpy_financial as npf

from tco_model.models import ScenarioInput, VehicleType, BETParameters, DieselParameters, FinancingMethod


def battery_needs_replacement(scenario: ScenarioInput, year: int) -> bool:
    """
    Helper function to determine if a battery needs replacement in a given year.
    This is abstracted to make it easier to patch in tests.
    
    Args:
        scenario: The scenario input
        year: The year to check
        
    Returns:
        bool: True if battery needs replacement, False otherwise
    """
    if (scenario.vehicle.type == VehicleType.BATTERY_ELECTRIC and 
        isinstance(scenario.vehicle, BETParameters) and 
        hasattr(scenario.vehicle, 'battery')):
        return scenario.vehicle.battery.needs_replacement(year)
    return False


def calculate_acquisition_costs(scenario: ScenarioInput, year: int) -> float:
    """
    Calculate acquisition costs for a given year.
    
    This includes purchase price, financing costs, and subsidies.
    For year 0, this includes the initial cost (minus deposit if financed).
    For subsequent years, it includes loan repayments if applicable.
    
    Args:
        scenario: The scenario input
        year: The year to calculate costs for
        
    Returns:
        float: The acquisition cost for the given year
    """
    financing = scenario.financing
    
    # Year 0: Initial payment
    if year == 0:
        if financing.method == FinancingMethod.CASH:
            # Full purchase price paid upfront
            return scenario.vehicle.purchase_price
        else:
            # Loan: Only down payment in year 0
            return scenario.vehicle.purchase_price * financing.down_payment_percentage
    
    # Subsequent years: Loan payments if applicable
    if financing.method == FinancingMethod.LOAN:
        # Only apply loan payments for the duration of the loan term
        if year <= financing.loan_term_years:
            # Calculate annual loan payment
            annual_payment = financing.calculate_annual_payment(scenario.vehicle.purchase_price)
            return annual_payment
    
    # No costs for cash purchases after year 0 or after loan term
    return 0.0


def calculate_energy_costs(scenario: ScenarioInput, year: int) -> float:
    """
    Calculate energy costs for a given year.
    
    For BETs, this includes electricity costs (energy charges and potentially demand charges).
    For diesel vehicles, this includes diesel fuel costs and AdBlue if applicable.
    
    Note: In the full implementation, this function delegates to specific strategies, 
    which are implemented in the strategies module. This function provides a simpler 
    direct calculation for easier testing and modularity.
    
    Args:
        scenario: The scenario input
        year: The year to calculate costs for
        
    Returns:
        float: The energy cost for the given year
    """
    annual_distance = scenario.operational.annual_distance_km
    
    if scenario.vehicle.type == VehicleType.BATTERY_ELECTRIC:
        # Get the BET parameters
        vehicle = scenario.vehicle
        if not isinstance(vehicle, BETParameters):
            raise ValueError("Vehicle type is BET but parameters are not BETParameters")
        
        # Calculate consumption
        consumption_kwh_per_km = vehicle.energy_consumption.base_rate
        # Apply load factor adjustment if available
        if hasattr(vehicle.energy_consumption, 'load_adjustment_factor') and hasattr(scenario.operational, 'average_load_factor'):
            load_adjustment = (1.0 - scenario.operational.average_load_factor) * vehicle.energy_consumption.load_adjustment_factor
            consumption_kwh_per_km -= load_adjustment
        
        total_consumption_kwh = consumption_kwh_per_km * annual_distance
        
        # Apply charging efficiency
        grid_consumption_kwh = total_consumption_kwh / vehicle.charging.charging_efficiency
        
        # Get electricity price - simplified version, in reality would use YearlyValue model
        # Base electricity price (this would come from economic parameters/yearly values)
        electricity_price = 0.25  # AUD/kWh - simplified example
        
        # Apply year-on-year changes if available in economic parameters
        if hasattr(scenario.economic, 'electricity_price_aud_per_kwh'):
            electricity_price = scenario.economic.electricity_price_aud_per_kwh
        elif hasattr(scenario.economic, 'electricity_price_projections'):
            electricity_price = scenario.economic.electricity_price_projections.get_for_year(year)
        
        return grid_consumption_kwh * electricity_price
    
    elif scenario.vehicle.type == VehicleType.DIESEL:
        # Get the diesel parameters
        vehicle = scenario.vehicle
        if not isinstance(vehicle, DieselParameters):
            raise ValueError("Vehicle type is diesel but parameters are not DieselParameters")
        
        # Calculate consumption
        consumption_l_per_km = vehicle.fuel_consumption.base_rate
        # Apply load factor adjustment if available
        if hasattr(vehicle.fuel_consumption, 'load_adjustment_factor') and hasattr(scenario.operational, 'average_load_factor'):
            load_adjustment = (1.0 - scenario.operational.average_load_factor) * vehicle.fuel_consumption.load_adjustment_factor
            consumption_l_per_km -= load_adjustment
        
        total_consumption_l = consumption_l_per_km * annual_distance
        
        # Get diesel price - simplified version, in reality would use YearlyValue model
        diesel_price = 1.80  # AUD/L - simplified example
        
        # Apply year-on-year changes if available in economic parameters
        if hasattr(scenario.economic, 'diesel_price_projections'):
            diesel_price = scenario.economic.diesel_price_projections.get_for_year(year)
        
        # Calculate AdBlue costs if applicable
        adblue_cost = 0.0
        if (hasattr(vehicle.engine, 'adblue_required') and 
            vehicle.engine.adblue_required and 
            hasattr(vehicle.engine, 'adblue_consumption_percent_of_diesel')):
            adblue_percent = vehicle.engine.adblue_consumption_percent_of_diesel or 0.05
            adblue_consumption_l = total_consumption_l * adblue_percent
            adblue_price = 1.0  # AUD/L - simplified
            adblue_cost = adblue_consumption_l * adblue_price
        
        return total_consumption_l * diesel_price + adblue_cost
    
    # Unknown vehicle type
    return 0.0


def calculate_maintenance_costs(scenario: ScenarioInput, year: int) -> float:
    """
    Calculate maintenance costs for a given year.
    
    Maintenance costs typically include:
    - Routine maintenance (based on distance and/or time)
    - Scheduled services
    - Component replacements
    - Repairs
    
    Different vehicle types have different maintenance profiles.
    
    Args:
        scenario: The scenario input
        year: The year to calculate costs for
        
    Returns:
        float: The maintenance cost for the given year
    """
    # Extract relevant parameters
    annual_distance = scenario.operational.annual_distance_km
    vehicle = scenario.vehicle
    
    # Base maintenance parameters
    if not hasattr(vehicle, 'maintenance'):
        return 0.0
    
    maintenance = vehicle.maintenance
    
    # Calculate distance-based costs
    variable_cost = maintenance.cost_per_km * annual_distance
    
    # Calculate fixed annual costs
    fixed_cost = maintenance.annual_fixed_default or ((maintenance.annual_fixed_min + maintenance.annual_fixed_max) / 2)
    
    # Apply inflation if relevant
    # In a real implementation, you'd apply inflation based on the year
    if year > 0 and hasattr(scenario.economic, 'inflation_rate'):
        inflation_factor = (1 + scenario.economic.inflation_rate) ** year
        fixed_cost *= inflation_factor
    
    # Additional costs depending on vehicle type
    additional_cost = 0.0
    
    # For diesel vehicles, add costs related to emissions systems
    if scenario.vehicle.type == VehicleType.DIESEL and isinstance(vehicle, DieselParameters):
        if hasattr(vehicle.engine, 'euro_emission_standard'):
            # Higher emission standards have additional maintenance costs
            if vehicle.engine.euro_emission_standard == "Euro VI":
                additional_cost += 0.02 * annual_distance  # Extra cost per km for emission systems
    
    # For BETs, reduced costs for certain components (simplified model)
    if scenario.vehicle.type == VehicleType.BATTERY_ELECTRIC:
        # Reduced brake wear due to regenerative braking
        brake_maintenance_reduction = 0.02 * annual_distance
        additional_cost -= brake_maintenance_reduction
    
    return variable_cost + fixed_cost + additional_cost


def calculate_infrastructure_costs(scenario: ScenarioInput, year: int) -> float:
    """
    Calculate infrastructure costs for a given year.
    
    For BETs, this includes charging infrastructure costs.
    For ICE vehicles, this includes refueling infrastructure costs if applicable.
    
    Args:
        scenario: The scenario input
        year: The year to calculate costs for
        
    Returns:
        float: The infrastructure cost for the given year
    """
    # For year 0, include the initial infrastructure setup cost
    if year == 0 and scenario.vehicle.type == VehicleType.BATTERY_ELECTRIC:
        # Include charger cost, installation cost, and grid upgrade cost
        infrastructure = scenario.infrastructure
        
        # Infrastructure costs per truck
        cost_per_truck = (
            infrastructure.charger_hardware_cost +
            infrastructure.installation_cost +
            infrastructure.grid_upgrade_cost
        ) / infrastructure.trucks_per_charger
        
        return cost_per_truck
    
    # For subsequent years, include maintenance costs if applicable
    if scenario.vehicle.type == VehicleType.BATTERY_ELECTRIC:
        # Annual maintenance cost as percentage of capital cost
        infrastructure = scenario.infrastructure
        total_capital = (
            infrastructure.charger_hardware_cost +
            infrastructure.installation_cost +
            infrastructure.grid_upgrade_cost
        )
        
        annual_maintenance = total_capital * infrastructure.maintenance_annual_percentage / infrastructure.trucks_per_charger
        
        return annual_maintenance
    
    # For ICE vehicles, typically no infrastructure costs
    return 0.0


def calculate_battery_replacement_costs(scenario: ScenarioInput, year: int) -> float:
    """
    Calculate battery replacement costs for a given year.
    
    Only applicable for BETs. Depends on the battery degradation model
    and replacement threshold.
    
    Args:
        scenario: The scenario input
        year: The year to calculate costs for
        
    Returns:
        float: The battery replacement cost for the given year
    """
    # Only applicable for BETs
    if scenario.vehicle.type != VehicleType.BATTERY_ELECTRIC or not isinstance(scenario.vehicle, BETParameters):
        return 0.0
    
    battery = scenario.vehicle.battery
    
    # Check if battery needs replacement in this year
    needs_replacement = battery_needs_replacement(scenario, year)
    
    if needs_replacement:
        # Calculate replacement cost
        # Get the battery price per kWh for the current year
        # This would normally come from projections in economic parameters
        base_battery_price_per_kwh = 800.0  # AUD/kWh, simplified example
        
        # Apply year-based price reduction (simplified model)
        # In reality, this would use the YearlyValue model
        yearly_price_reduction = 0.05  # 5% reduction per year
        battery_price_per_kwh = base_battery_price_per_kwh * ((1 - yearly_price_reduction) ** year)
        
        # Calculate total replacement cost
        # Apply replacement cost factor (replacement might cost less than a new battery)
        replacement_cost = (
            battery.capacity_kwh * 
            battery_price_per_kwh * 
            battery.replacement_cost_factor
        )
        
        return replacement_cost
    
    return 0.0


def calculate_insurance_registration_costs(scenario: ScenarioInput, year: int) -> float:
    """
    Calculate insurance and registration costs for a given year.
    
    Insurance costs typically depend on:
    - Vehicle value
    - Vehicle type
    - Usage pattern
    
    Registration costs depend on:
    - Vehicle type
    - Weight
    - Jurisdiction
    
    Args:
        scenario: The scenario input
        year: The year to calculate costs for
        
    Returns:
        float: The insurance and registration cost for the given year
    """
    vehicle = scenario.vehicle
    purchase_price = vehicle.purchase_price
    
    # Insurance cost as percentage of vehicle value (simplified model)
    # In reality, this would be more complex and depend on many factors
    insurance_percentage = 0.04  # 4% of vehicle value per year
    
    # Vehicle value decreases each year (simplified depreciation model)
    # In reality, would use the residual value model
    if year == 0:
        current_value = purchase_price
    else:
        annual_depreciation = 0.15  # 15% per year
        current_value = purchase_price * ((1 - annual_depreciation) ** year)
    
    insurance_cost = current_value * insurance_percentage
    
    # Registration costs - fixed base cost plus variable based on vehicle type
    base_registration = 1000.0  # AUD per year
    
    # Additional costs for specific vehicle types
    if vehicle.type == VehicleType.DIESEL:
        # Additional road user charges for diesel trucks
        road_user_charge_per_km = 0.02  # AUD per km
        annual_distance = scenario.operational.annual_distance_km
        road_user_charges = road_user_charge_per_km * annual_distance
        registration_cost = base_registration + road_user_charges
    else:
        # For BETs, simplified model with lower registration due to incentives
        registration_cost = base_registration * 0.8  # 20% discount
    
    # Apply inflation for subsequent years
    if year > 0 and hasattr(scenario.economic, 'inflation_rate'):
        inflation_factor = (1 + scenario.economic.inflation_rate) ** year
        registration_cost *= inflation_factor
    
    return insurance_cost + registration_cost


def calculate_taxes_levies(scenario: ScenarioInput, year: int) -> float:
    """
    Calculate taxes and levies for a given year.
    
    This includes road user charges, carbon taxes, and other applicable
    taxes or levies.
    
    Args:
        scenario: The scenario input
        year: The year to calculate costs for
        
    Returns:
        float: The taxes and levies for the given year
    """
    vehicle = scenario.vehicle
    annual_distance = scenario.operational.annual_distance_km
    
    # Carbon tax calculation (if enabled)
    carbon_tax = 0.0
    if hasattr(scenario.economic, 'carbon_tax_rate_aud_per_tonne') and scenario.economic.carbon_tax_rate_aud_per_tonne > 0:
        # Get base carbon tax rate
        base_carbon_tax_rate = scenario.economic.carbon_tax_rate_aud_per_tonne
        
        # Apply year-on-year increase if applicable
        if hasattr(scenario.economic, 'carbon_tax_annual_increase_rate'):
            carbon_tax_rate = base_carbon_tax_rate * (
                (1 + scenario.economic.carbon_tax_annual_increase_rate) ** year
            )
        else:
            carbon_tax_rate = base_carbon_tax_rate
        
        # Calculate emissions and apply tax rate
        if vehicle.type == VehicleType.DIESEL and isinstance(vehicle, DieselParameters):
            # Calculate fuel consumption
            consumption_l_per_km = vehicle.fuel_consumption.base_rate
            total_consumption_l = consumption_l_per_km * annual_distance
            
            # Calculate CO2 emissions (kg)
            if hasattr(vehicle.engine, 'co2_per_liter'):
                co2_per_liter = vehicle.engine.co2_per_liter
            else:
                co2_per_liter = 2.68  # Default kg CO2 per liter diesel
            
            total_emissions_tonnes = (total_consumption_l * co2_per_liter) / 1000
            
            # Apply carbon tax
            carbon_tax = total_emissions_tonnes * carbon_tax_rate
        
        # For BETs, carbon tax would depend on grid emissions factor, which is omitted in this simplified model
    
    # Road user charges (if applicable)
    road_user_charges = 0.0
    # In some jurisdictions, electric vehicles pay a specific road user charge
    # to compensate for not paying fuel excise
    if vehicle.type == VehicleType.BATTERY_ELECTRIC:
        # Apply a road user charge
        road_user_charge_rate = 0.025  # AUD per km (example value)
        road_user_charges = road_user_charge_rate * annual_distance
    
    # Other taxes and levies could be added here
    
    return carbon_tax + road_user_charges


def calculate_residual_value(scenario: ScenarioInput, year: int) -> float:
    """
    Calculate the residual value for a given year.
    
    This is typically only applied in the final year of the analysis period.
    The residual value is a negative cost (i.e., an income).
    
    Args:
        scenario: The scenario input
        year: The year to calculate residual value for
        
    Returns:
        float: The residual value (negative cost) for the given year
    """
    # Only calculate residual value for the final year
    analysis_period = scenario.economic.analysis_period_years
    if year != analysis_period - 1:
        return 0.0
    
    vehicle = scenario.vehicle
    purchase_price = vehicle.purchase_price
    
    # If the vehicle has a residual value model, use it
    if hasattr(vehicle, 'residual_value') and hasattr(vehicle.residual_value, 'calculate_residual_value'):
        # Total years at the end of the analysis period
        total_years = analysis_period
        
        # The actual implementation would use the model with proper parameters
        residual_value = vehicle.residual_value.calculate_residual_value(
            purchase_price=purchase_price,
            year=total_years
        )
        
        # Return negative value (it's an income, not a cost)
        return -residual_value
    
    # If no residual value model is available, use a simple fallback method
    # Use different approaches for different vehicle types
    if vehicle.type == VehicleType.BATTERY_ELECTRIC:
        # For BETs: Higher initial decay rate, but stabilizes over time
        # max(10%, 50% - (3% per year of analysis period))
        residual_value_percentage = max(0.1, 0.5 - (0.03 * scenario.economic.analysis_period_years))
    else:
        # For diesel: Lower but steadier decay rate
        # max(5%, 40% - (3.5% per year of analysis period))
        residual_value_percentage = max(0.05, 0.4 - (0.035 * scenario.economic.analysis_period_years))
    
    # Handle edge case of zero vehicle price
    if purchase_price == 0:
        return 0.0
    
    # Return negative value (it's an income, not a cost)
    return -(purchase_price * residual_value_percentage) 