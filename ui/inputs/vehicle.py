"""
Vehicle Input Module

This module renders the UI components for vehicle parameter inputs.
It handles different vehicle types (BET and Diesel) with appropriate
parameter fields for each type.
"""

import streamlit as st
from typing import Dict, Any, Optional, Tuple

from tco_model.models import VehicleType, VehicleCategory, BETParameters, DieselParameters
from utils.helpers import (
    get_safe_state_value, 
    set_safe_state_value,
    initialize_nested_state,
    format_currency,
    handle_vehicle_switch
)
from ui.guide import add_tooltips_to_ui

# Constants for state keys
STATE_TYPE = "type"
STATE_CATEGORY = "category"
STATE_NAME = "name"
STATE_PURCHASE_PRICE = "purchase_price"
STATE_ANNUAL_PRICE_DECREASE = "annual_price_decrease_real"
STATE_MAX_PAYLOAD = "max_payload_tonnes"
STATE_RANGE = "range_km"


def on_vehicle_type_change(vehicle_number: int):
    """
    Handle vehicle type change by calling the handle_vehicle_switch function.
    
    Args:
        vehicle_number: The vehicle number (1 or 2)
    """
    state_prefix = f"vehicle_{vehicle_number}_input"
    new_type_str = st.session_state[f"{state_prefix}.vehicle.{STATE_TYPE}_input"]
    
    # Get the previous type
    old_type_str = get_safe_state_value(f"{state_prefix}.vehicle.{STATE_TYPE}")
    
    # Only call if the type actually changed
    if old_type_str != new_type_str:
        handle_vehicle_switch(old_type_str, new_type_str, vehicle_number)


def render_vehicle_inputs(vehicle_number: int) -> None:
    """
    Render the UI components for vehicle parameters.
    
    This function renders input fields for basic vehicle parameters and delegates
    to specialized functions for BET and diesel-specific parameters.
    
    Args:
        vehicle_number: The vehicle number (1 or 2)
    """
    # Get tooltips
    tooltips = add_tooltips_to_ui()
    
    state_prefix = f"vehicle_{vehicle_number}_input"
    
    # Get current vehicle type to determine which specialized inputs to show
    current_type = get_safe_state_value(f"{state_prefix}.vehicle.{STATE_TYPE}", VehicleType.BATTERY_ELECTRIC.value)
    
    # Create an expander for vehicle basic parameters
    with st.expander("Vehicle Parameters", expanded=True):
        # Vehicle name
        vehicle_name = st.text_input(
            "Vehicle Name",
            value=get_safe_state_value(f"{state_prefix}.vehicle.{STATE_NAME}", f"Vehicle {vehicle_number}"),
            key=f"{state_prefix}.vehicle.{STATE_NAME}_input",
            help="A descriptive name for this vehicle"
        )
        set_safe_state_value(f"{state_prefix}.vehicle.{STATE_NAME}", vehicle_name)
        
        # Vehicle type and category in columns
        col1, col2 = st.columns(2)
        
        with col1:
            vehicle_type = st.selectbox(
                "Vehicle Type",
                options=[vt.value for vt in VehicleType],
                index=1 if vehicle_number == 1 else 0,  # DIESEL=0, BATTERY_ELECTRIC=1
                key=f"{state_prefix}.vehicle.{STATE_TYPE}_input",
                help="The powertrain type of the vehicle",
                on_change=lambda: on_vehicle_type_change(vehicle_number)
            )
            set_safe_state_value(f"{state_prefix}.vehicle.{STATE_TYPE}", vehicle_type)
        
        with col2:
            vehicle_category = st.selectbox(
                "Vehicle Category",
                options=[vc.value for vc in VehicleCategory],
                index=1 if get_safe_state_value(f"{state_prefix}.vehicle.{STATE_CATEGORY}") == VehicleCategory.ARTICULATED.value else 0,
                key=f"{state_prefix}.vehicle.{STATE_CATEGORY}_input",
                help="The category of the heavy vehicle (rigid or articulated)",
            )
            set_safe_state_value(f"{state_prefix}.vehicle.{STATE_CATEGORY}", vehicle_category)
        
        # Purchase price and annual price decrease
        col1, col2 = st.columns(2)
        
        with col1:
            purchase_price = st.number_input(
                "Purchase Price (AUD)",
                min_value=50000.0,
                max_value=1000000.0,
                value=float(get_safe_state_value(f"{state_prefix}.vehicle.{STATE_PURCHASE_PRICE}", 
                                           400000.0 if vehicle_type == VehicleType.BATTERY_ELECTRIC.value else 200000.0)),
                format="%.2f",
                key=f"{state_prefix}.vehicle.{STATE_PURCHASE_PRICE}_input",
                help=tooltips.get("vehicle.purchase_price", "The current purchase price of the vehicle"),
            )
            set_safe_state_value(f"{state_prefix}.vehicle.{STATE_PURCHASE_PRICE}", purchase_price)
        
        with col2:
            annual_price_decrease = st.slider(
                "Annual Price Decrease (%)",
                min_value=0.0,
                max_value=10.0,
                value=float(get_safe_state_value(f"{state_prefix}.vehicle.{STATE_ANNUAL_PRICE_DECREASE}", 
                                           2.0 if vehicle_type == VehicleType.BATTERY_ELECTRIC.value else 0.0)) * 100,
                format="%.1f",
                key=f"{state_prefix}.vehicle.{STATE_ANNUAL_PRICE_DECREASE}_input",
                help="Expected annual decrease in purchase price in real terms (e.g., due to technology improvements)",
            )
            set_safe_state_value(f"{state_prefix}.vehicle.{STATE_ANNUAL_PRICE_DECREASE}", annual_price_decrease / 100.0)
        
        # Performance parameters
        col1, col2 = st.columns(2)
        
        with col1:
            max_payload = st.number_input(
                "Maximum Payload (tonnes)",
                min_value=1.0,
                max_value=50.0,
                value=float(get_safe_state_value(f"{state_prefix}.vehicle.{STATE_MAX_PAYLOAD}", 
                                           26.0 if vehicle_type == VehicleType.BATTERY_ELECTRIC.value else 28.0)),
                format="%.1f",
                key=f"{state_prefix}.vehicle.{STATE_MAX_PAYLOAD}_input",
                help=tooltips.get("vehicle.payload_capacity", "Maximum payload capacity in tonnes"),
            )
            set_safe_state_value(f"{state_prefix}.vehicle.{STATE_MAX_PAYLOAD}", max_payload)
        
        with col2:
            range_km = st.number_input(
                "Range (km)",
                min_value=50.0,
                max_value=3000.0,
                value=float(get_safe_state_value(f"{state_prefix}.vehicle.{STATE_RANGE}", 
                                           350.0 if vehicle_type == VehicleType.BATTERY_ELECTRIC.value else 2200.0)),
                format="%.1f",
                key=f"{state_prefix}.vehicle.{STATE_RANGE}_input",
                help="Maximum range on a full charge/tank in kilometers",
            )
            set_safe_state_value(f"{state_prefix}.vehicle.{STATE_RANGE}", range_km)
    
    # Vehicle type-specific parameters
    if vehicle_type == VehicleType.BATTERY_ELECTRIC.value:
        render_bet_parameters(vehicle_number, state_prefix, tooltips)
    else:
        render_diesel_parameters(vehicle_number, state_prefix, tooltips)
    
    # Display key metrics calculated from inputs
    display_derived_metrics(vehicle_number, state_prefix, vehicle_type)


def render_bet_parameters(vehicle_number: int, state_prefix: str, tooltips: Dict[str, str]) -> None:
    """
    Render the UI components for BET-specific parameters.
    
    Args:
        vehicle_number: The vehicle number (1 or 2)
        state_prefix: The state prefix for session state access
        tooltips: Dictionary of tooltips for UI components
    """
    # Create expandable sections for different BET parameter categories
    with st.expander("Battery Parameters", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            battery_capacity = st.number_input(
                "Battery Capacity (kWh)",
                min_value=100.0,
                max_value=1000.0,
                value=float(get_safe_state_value(f"{state_prefix}.vehicle.battery.capacity_kwh", 400.0)),
                format="%.1f",
                key=f"{state_prefix}.vehicle.battery.capacity_kwh_input",
                help=tooltips.get("vehicle.battery.capacity", "Total battery capacity in kilowatt-hours"),
            )
            set_safe_state_value(f"{state_prefix}.vehicle.battery.capacity_kwh", battery_capacity)
            
            usable_capacity = st.slider(
                "Usable Capacity (%)",
                min_value=70.0,
                max_value=100.0,
                value=float(get_safe_state_value(f"{state_prefix}.vehicle.battery.usable_capacity_percentage", 0.9)) * 100,
                format="%.1f",
                key=f"{state_prefix}.vehicle.battery.usable_capacity_percentage_input",
                help="Percentage of battery capacity that is usable (accounts for depth-of-discharge limits)",
            )
            set_safe_state_value(f"{state_prefix}.vehicle.battery.usable_capacity_percentage", usable_capacity / 100.0)
        
        with col2:
            degradation_rate = st.slider(
                "Annual Degradation Rate (%)",
                min_value=0.0,
                max_value=10.0,
                value=float(get_safe_state_value(f"{state_prefix}.vehicle.battery.degradation_rate_annual", 0.02)) * 100,
                format="%.1f",
                key=f"{state_prefix}.vehicle.battery.degradation_rate_annual_input",
                help="Annual rate of battery capacity degradation",
            )
            set_safe_state_value(f"{state_prefix}.vehicle.battery.degradation_rate_annual", degradation_rate / 100.0)
            
            replacement_threshold = st.slider(
                "Replacement Threshold (%)",
                min_value=50.0,
                max_value=90.0,
                value=float(get_safe_state_value(f"{state_prefix}.vehicle.battery.replacement_threshold", 0.7)) * 100,
                format="%.1f",
                key=f"{state_prefix}.vehicle.battery.replacement_threshold_input",
                help="Battery capacity threshold (as % of original) at which replacement is needed",
            )
            set_safe_state_value(f"{state_prefix}.vehicle.battery.replacement_threshold", replacement_threshold / 100.0)
        
        replacement_cost_factor = st.slider(
            "Replacement Cost Factor",
            min_value=0.3,
            max_value=1.0,
            value=float(get_safe_state_value(f"{state_prefix}.vehicle.battery.replacement_cost_factor", 0.8)),
            format="%.2f",
            key=f"{state_prefix}.vehicle.battery.replacement_cost_factor_input",
            help="Cost of battery replacement as a fraction of new battery cost (accounts for future price reductions)",
        )
        set_safe_state_value(f"{state_prefix}.vehicle.battery.replacement_cost_factor", replacement_cost_factor)
    
    with st.expander("Energy Consumption", expanded=False):
        # Energy consumption parameters
        base_consumption = st.number_input(
            "Base Energy Consumption (kWh/km)",
            min_value=0.5,
            max_value=3.0,
            value=float(get_safe_state_value(f"{state_prefix}.vehicle.energy_consumption.base_rate", 1.45)),
            format="%.3f",
            key=f"{state_prefix}.vehicle.energy_consumption.base_rate_input",
            help="Base energy consumption per kilometer under standard conditions",
        )
        set_safe_state_value(f"{state_prefix}.vehicle.energy_consumption.base_rate", base_consumption)
        
        # Min/max consumption ranges
        col1, col2 = st.columns(2)
        
        with col1:
            min_consumption = st.number_input(
                "Minimum Consumption (kWh/km)",
                min_value=0.3,
                max_value=base_consumption,
                value=float(get_safe_state_value(f"{state_prefix}.vehicle.energy_consumption.min_rate", 1.2)),
                format="%.3f",
                key=f"{state_prefix}.vehicle.energy_consumption.min_rate_input",
                help="Minimum energy consumption under ideal conditions",
            )
            set_safe_state_value(f"{state_prefix}.vehicle.energy_consumption.min_rate", min_consumption)
        
        with col2:
            max_consumption = st.number_input(
                "Maximum Consumption (kWh/km)",
                min_value=base_consumption,
                max_value=5.0,
                value=float(get_safe_state_value(f"{state_prefix}.vehicle.energy_consumption.max_rate", 1.7)),
                format="%.3f",
                key=f"{state_prefix}.vehicle.energy_consumption.max_rate_input",
                help="Maximum energy consumption under adverse conditions",
            )
            set_safe_state_value(f"{state_prefix}.vehicle.energy_consumption.max_rate", max_consumption)
        
        # Adjustment factors
        st.subheader("Adjustment Factors")
        
        col1, col2 = st.columns(2)
        
        with col1:
            load_adjustment = st.slider(
                "Load Adjustment",
                min_value=0.0,
                max_value=0.5,
                value=float(get_safe_state_value(f"{state_prefix}.vehicle.energy_consumption.load_adjustment_factor", 0.15)),
                format="%.2f",
                key=f"{state_prefix}.vehicle.energy_consumption.load_adjustment_factor_input",
                help="Factor for adjusting consumption based on load (higher means more impact)",
            )
            set_safe_state_value(f"{state_prefix}.vehicle.energy_consumption.load_adjustment_factor", load_adjustment)
        
        with col2:
            regen_efficiency = st.slider(
                "Regenerative Braking Efficiency",
                min_value=0.0,
                max_value=1.0,
                value=float(get_safe_state_value(f"{state_prefix}.vehicle.energy_consumption.regenerative_braking_efficiency", 0.65)),
                format="%.2f",
                key=f"{state_prefix}.vehicle.energy_consumption.regenerative_braking_efficiency_input",
                help="Efficiency of the regenerative braking system",
            )
            set_safe_state_value(f"{state_prefix}.vehicle.energy_consumption.regenerative_braking_efficiency", regen_efficiency)
    
    with st.expander("Charging Parameters", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            max_charging_power = st.number_input(
                "Max Charging Power (kW)",
                min_value=50.0,
                max_value=1000.0,
                value=float(get_safe_state_value(f"{state_prefix}.vehicle.charging.max_charging_power_kw", 350.0)),
                format="%.1f",
                key=f"{state_prefix}.vehicle.charging.max_charging_power_kw_input",
                help="Maximum power at which the vehicle can charge",
            )
            set_safe_state_value(f"{state_prefix}.vehicle.charging.max_charging_power_kw", max_charging_power)
        
        with col2:
            charging_efficiency = st.slider(
                "Charging Efficiency",
                min_value=0.7,
                max_value=1.0,
                value=float(get_safe_state_value(f"{state_prefix}.vehicle.charging.charging_efficiency", 0.9)),
                format="%.2f",
                key=f"{state_prefix}.vehicle.charging.charging_efficiency_input",
                help="Efficiency of the charging process (grid to battery)",
            )
            set_safe_state_value(f"{state_prefix}.vehicle.charging.charging_efficiency", charging_efficiency)
    
    with st.expander("Infrastructure Parameters", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            charger_cost = st.number_input(
                "Charger Hardware Cost (AUD)",
                min_value=10000.0,
                max_value=500000.0,
                value=float(get_safe_state_value(f"{state_prefix}.vehicle.infrastructure.charger_hardware_cost", 150000.0)),
                format="%.2f",
                key=f"{state_prefix}.vehicle.infrastructure.charger_hardware_cost_input",
                help="Cost of the charging hardware",
            )
            set_safe_state_value(f"{state_prefix}.vehicle.infrastructure.charger_hardware_cost", charger_cost)
            
            installation_cost = st.number_input(
                "Installation Cost (AUD)",
                min_value=0.0,
                max_value=200000.0,
                value=float(get_safe_state_value(f"{state_prefix}.vehicle.infrastructure.installation_cost", 50000.0)),
                format="%.2f",
                key=f"{state_prefix}.vehicle.infrastructure.installation_cost_input",
                help="Cost of installing the charging infrastructure",
            )
            set_safe_state_value(f"{state_prefix}.vehicle.infrastructure.installation_cost", installation_cost)
        
        with col2:
            trucks_per_charger = st.number_input(
                "Trucks Per Charger",
                min_value=0.5,
                max_value=10.0,
                value=float(get_safe_state_value(f"{state_prefix}.vehicle.infrastructure.trucks_per_charger", 1.0)),
                format="%.1f",
                key=f"{state_prefix}.vehicle.infrastructure.trucks_per_charger_input",
                help="Number of trucks sharing each charger",
            )
            set_safe_state_value(f"{state_prefix}.vehicle.infrastructure.trucks_per_charger", trucks_per_charger)
            
            grid_upgrade = st.number_input(
                "Grid Upgrade Cost (AUD)",
                min_value=0.0,
                max_value=500000.0,
                value=float(get_safe_state_value(f"{state_prefix}.vehicle.infrastructure.grid_upgrade_cost", 0.0)),
                format="%.2f",
                key=f"{state_prefix}.vehicle.infrastructure.grid_upgrade_cost_input",
                help="Cost of any grid upgrades required for charging infrastructure",
            )
            set_safe_state_value(f"{state_prefix}.vehicle.infrastructure.grid_upgrade_cost", grid_upgrade)


def render_diesel_parameters(vehicle_number: int, state_prefix: str, tooltips: Dict[str, str]) -> None:
    """
    Render the UI components for diesel-specific parameters.
    
    Args:
        vehicle_number: The vehicle number (1 or 2)
        state_prefix: The state prefix for session state access
        tooltips: Dictionary of tooltips for UI components
    """
    # Create expandable sections for different diesel parameter categories
    with st.expander("Engine Parameters", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            engine_power = st.number_input(
                "Engine Power (kW)",
                min_value=100,
                max_value=800,
                value=int(get_safe_state_value(f"{state_prefix}.vehicle.engine.power_kw", 400)),
                key=f"{state_prefix}.vehicle.engine.power_kw_input",
                help="Engine power in kilowatts",
            )
            set_safe_state_value(f"{state_prefix}.vehicle.engine.power_kw", engine_power)
            
            displacement = st.number_input(
                "Displacement (liters)",
                min_value=5.0,
                max_value=20.0,
                value=float(get_safe_state_value(f"{state_prefix}.vehicle.engine.displacement_litres", 13.0)),
                format="%.1f",
                key=f"{state_prefix}.vehicle.engine.displacement_litres_input",
                help="Engine displacement in liters",
            )
            set_safe_state_value(f"{state_prefix}.vehicle.engine.displacement_litres", displacement)
        
        with col2:
            emission_standard = st.selectbox(
                "Emission Standard",
                options=["Euro V", "Euro VI"],
                index=1 if get_safe_state_value(f"{state_prefix}.vehicle.engine.euro_emission_standard", "Euro VI") == "Euro VI" else 0,
                key=f"{state_prefix}.vehicle.engine.euro_emission_standard_input",
                help="Euro emission standard of the engine",
            )
            set_safe_state_value(f"{state_prefix}.vehicle.engine.euro_emission_standard", emission_standard)
            
            adblue_required = st.checkbox(
                "AdBlue Required",
                value=bool(get_safe_state_value(f"{state_prefix}.vehicle.engine.adblue_required", True)),
                key=f"{state_prefix}.vehicle.engine.adblue_required_input",
                help="Whether AdBlue (DEF) is required for this engine",
            )
            set_safe_state_value(f"{state_prefix}.vehicle.engine.adblue_required", adblue_required)
        
        if adblue_required:
            adblue_consumption = st.slider(
                "AdBlue Consumption (% of diesel)",
                min_value=1.0,
                max_value=10.0,
                value=float(get_safe_state_value(f"{state_prefix}.vehicle.engine.adblue_consumption_percent_of_diesel", 0.05)) * 100,
                format="%.1f",
                key=f"{state_prefix}.vehicle.engine.adblue_consumption_percent_of_diesel_input",
                help="AdBlue consumption as a percentage of diesel consumption",
            )
            set_safe_state_value(f"{state_prefix}.vehicle.engine.adblue_consumption_percent_of_diesel", adblue_consumption / 100.0)
    
    with st.expander("Fuel Consumption", expanded=False):
        # Fuel consumption parameters
        base_rate = get_safe_state_value(f"{state_prefix}.vehicle.fuel_consumption.base_rate", 0.53)
        # Make sure value is in L/km (not L/100km)
        if base_rate > 1.0:  # Unreasonably high for L/km, assume it's already in L/100km
            base_rate = base_rate / 100.0
            
        base_consumption = st.number_input(
            "Base Fuel Consumption (L/100km)",
            min_value=10.0,
            max_value=100.0,
            value=base_rate * 100,
            format="%.1f",
            key=f"{state_prefix}.vehicle.fuel_consumption.base_rate_input",
            help="Base fuel consumption per 100km under standard conditions",
        )
        set_safe_state_value(f"{state_prefix}.vehicle.fuel_consumption.base_rate", base_consumption / 100.0)  # Convert to L/km
        
        # Min/max consumption ranges
        col1, col2 = st.columns(2)
        
        with col1:
            min_rate = get_safe_state_value(f"{state_prefix}.vehicle.fuel_consumption.min_rate", 0.45)
            # Make sure value is in L/km (not L/100km)
            if min_rate > 1.0:  # Unreasonably high for L/km
                min_rate = min_rate / 100.0
                
            min_consumption = st.number_input(
                "Minimum Consumption (L/100km)",
                min_value=10.0,
                max_value=base_consumption,
                value=min_rate * 100,
                format="%.1f",
                key=f"{state_prefix}.vehicle.fuel_consumption.min_rate_input",
                help="Minimum fuel consumption under ideal conditions",
            )
            set_safe_state_value(f"{state_prefix}.vehicle.fuel_consumption.min_rate", min_consumption / 100.0)  # Convert to L/km
        
        with col2:
            max_rate = get_safe_state_value(f"{state_prefix}.vehicle.fuel_consumption.max_rate", 0.6)
            # Make sure value is in L/km (not L/100km)
            if max_rate > 1.0:  # Unreasonably high for L/km
                max_rate = max_rate / 100.0
                
            max_consumption = st.number_input(
                "Maximum Consumption (L/100km)",
                min_value=base_consumption,
                max_value=100.0,
                value=max_rate * 100,
                format="%.1f",
                key=f"{state_prefix}.vehicle.fuel_consumption.max_rate_input",
                help="Maximum fuel consumption under adverse conditions",
            )
            set_safe_state_value(f"{state_prefix}.vehicle.fuel_consumption.max_rate", max_consumption / 100.0)  # Convert to L/km
        
        # Adjustment factors
        st.subheader("Adjustment Factors")
        
        load_adjustment = st.slider(
            "Load Adjustment",
            min_value=0.0,
            max_value=0.5,
            value=float(get_safe_state_value(f"{state_prefix}.vehicle.fuel_consumption.load_adjustment_factor", 0.25)),
            format="%.2f",
            key=f"{state_prefix}.vehicle.fuel_consumption.load_adjustment_factor_input",
            help="Factor for adjusting consumption based on load (higher means more impact)",
        )
        set_safe_state_value(f"{state_prefix}.vehicle.fuel_consumption.load_adjustment_factor", load_adjustment)


def display_derived_metrics(vehicle_number: int, state_prefix: str, vehicle_type: str) -> None:
    """
    Display key metrics derived from the input parameters.
    
    Args:
        vehicle_number: The vehicle number (1 or 2)
        state_prefix: The state prefix for session state access
        vehicle_type: The vehicle type (BET or diesel)
    """
    with st.expander("Key Metrics", expanded=False):
        col1, col2 = st.columns(2)
        
        # Common metrics
        purchase_price = get_safe_state_value(f"{state_prefix}.vehicle.{STATE_PURCHASE_PRICE}", 0.0)
        
        with col1:
            st.metric("Purchase Price", format_currency(purchase_price))
        
        # Vehicle-specific metrics
        if vehicle_type == VehicleType.BATTERY_ELECTRIC.value:
            # BET metrics
            battery_capacity = get_safe_state_value(f"{state_prefix}.vehicle.battery.capacity_kwh", 0.0)
            consumption = get_safe_state_value(f"{state_prefix}.vehicle.energy_consumption.base_rate", 0.0)
            
            with col2:
                st.metric("Battery Price", format_currency(battery_capacity * 800))  # Assuming 800 AUD/kWh
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Energy Cost per km", f"${consumption * 0.25:.2f}")  # Assuming 0.25 AUD/kWh
            
            with col2:
                range_km = get_safe_state_value(f"{state_prefix}.vehicle.{STATE_RANGE}", 0.0)
                st.metric("Usable Range (km)", f"{range_km * 0.9:.1f}")  # Assuming 90% of stated range
        else:
            # Diesel metrics
            fuel_rate = get_safe_state_value(f"{state_prefix}.vehicle.fuel_consumption.base_rate", 0.0)
            
            with col2:
                st.metric("Fuel Cost per 100km", f"${fuel_rate * 100 * 1.8:.2f}")  # Assuming 1.8 AUD/L
            
            col1, col2 = st.columns(2)
            with col1:
                range_km = get_safe_state_value(f"{state_prefix}.vehicle.{STATE_RANGE}", 0.0)
                tank_size = range_km * fuel_rate
                st.metric("Estimated Tank Size (L)", f"{tank_size:.1f}")
            
            with col2:
                annual_distance = 100000  # Assume 100,000 km annual distance
                annual_fuel = annual_distance * fuel_rate
                st.metric("Annual Fuel Usage (L)", f"{annual_fuel:.1f}") 