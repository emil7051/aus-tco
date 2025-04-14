"""
Vehicle Input Module

This module renders the UI components for vehicle parameter inputs.
It handles different vehicle types (BET and Diesel) with appropriate
parameter fields for each type and improved visual organization.
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
from utils.ui_terminology import get_formatted_label, get_component_description
from utils.ui_components import UIComponentFactory
from ui.inputs.parameter_helpers import (
    render_parameter_with_impact,
    get_vehicle_type,
    render_vehicle_header
)

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
    Render improved vehicle input forms with visual hierarchy
    
    Args:
        vehicle_number: Vehicle number (1 or 2)
    """
    # Get vehicle type for styling
    state_prefix = f"vehicle_{vehicle_number}_input"
    vehicle_type = get_vehicle_type(state_prefix)
    
    # Add vehicle type visual indicator
    render_vehicle_header(vehicle_number, vehicle_type)
    
    # Create tabbed interface for parameter categories
    param_tabs = st.tabs([
        "Basic Parameters",
        "Performance",
        "Economics", 
        "Advanced Settings"
    ])
    
    # Implement each tab with properly grouped inputs
    with param_tabs[0]:
        render_basic_parameters(vehicle_number, state_prefix, vehicle_type)
        
    with param_tabs[1]:
        if vehicle_type == "bet":
            render_bet_performance_parameters(vehicle_number, state_prefix)
        else:
            render_diesel_performance_parameters(vehicle_number, state_prefix)
        
    with param_tabs[2]:
        from ui.inputs.economic import render_economic_parameters
        render_economic_parameters(vehicle_number, state_prefix, vehicle_type)
        
    with param_tabs[3]:
        render_advanced_parameters(vehicle_number, state_prefix, vehicle_type)


def render_basic_parameters(vehicle_number: int, state_prefix: str, vehicle_type: str) -> None:
    """
    Render basic vehicle parameters
    
    Args:
        vehicle_number: Vehicle number
        state_prefix: State key prefix
        vehicle_type: Vehicle type
    """
    # Create a card for basic parameters
    with UIComponentFactory.create_card("Basic Parameters", f"v{vehicle_number}_basic", vehicle_type):
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
            vehicle_type_input = st.selectbox(
                "Vehicle Type",
                options=[vt.value for vt in VehicleType],
                index=1 if vehicle_number == 1 else 0,  # DIESEL=0, BATTERY_ELECTRIC=1
                key=f"{state_prefix}.vehicle.{STATE_TYPE}_input",
                help="The powertrain type of the vehicle",
                on_change=lambda: on_vehicle_type_change(vehicle_number)
            )
            set_safe_state_value(f"{state_prefix}.vehicle.{STATE_TYPE}", vehicle_type_input)
        
        with col2:
            vehicle_category = st.selectbox(
                "Vehicle Category",
                options=[vc.value for vc in VehicleCategory],
                index=1 if get_safe_state_value(f"{state_prefix}.vehicle.{STATE_CATEGORY}") == VehicleCategory.ARTICULATED.value else 0,
                key=f"{state_prefix}.vehicle.{STATE_CATEGORY}_input",
                help="The category of the heavy vehicle (rigid or articulated)",
            )
            set_safe_state_value(f"{state_prefix}.vehicle.{STATE_CATEGORY}", vehicle_category)


def render_bet_performance_parameters(vehicle_number: int, state_prefix: str) -> None:
    """
    Render BET-specific performance parameters
    
    Args:
        vehicle_number: Vehicle number
        state_prefix: State key prefix
    """
    # Create card for performance parameters
    with UIComponentFactory.create_card("Performance Parameters", f"v{vehicle_number}_bet_performance", "bet"):
        # Performance metrics
        col1, col2 = st.columns(2)
        
        with col1:
            # Purchase price with impact indicator
            purchase_price = render_parameter_with_impact(
                "Purchase Price (AUD)",
                f"{state_prefix}.vehicle.{STATE_PURCHASE_PRICE}",
                default_value=get_safe_state_value(f"{state_prefix}.vehicle.{STATE_PURCHASE_PRICE}", 400000.0),
                min_value=50000.0,
                max_value=1000000.0,
                step=10000.0,
                format="%.2f",
                impact_level="high",
                help_text="The current purchase price of the vehicle"
            )
            
            # Annual price decrease
            annual_price_decrease = render_parameter_with_impact(
                "Annual Price Decrease (%)",
                f"{state_prefix}.vehicle.{STATE_ANNUAL_PRICE_DECREASE}",
                default_value=get_safe_state_value(f"{state_prefix}.vehicle.{STATE_ANNUAL_PRICE_DECREASE}", 0.02),
                min_value=0.0,
                max_value=0.10,
                step=0.005,
                format="%.3f",
                impact_level="medium",
                help_text="Expected annual decrease in purchase price in real terms"
            )
        
        with col2:
            # Max payload
            max_payload = render_parameter_with_impact(
                "Maximum Payload (tonnes)",
                f"{state_prefix}.vehicle.{STATE_MAX_PAYLOAD}",
                default_value=get_safe_state_value(f"{state_prefix}.vehicle.{STATE_MAX_PAYLOAD}", 26.0),
                min_value=1.0,
                max_value=50.0,
                step=0.5,
                format="%.1f",
                impact_level="medium",
                help_text="Maximum payload capacity in tonnes"
            )
            
            # Range
            range_km = render_parameter_with_impact(
                "Range (km)",
                f"{state_prefix}.vehicle.{STATE_RANGE}",
                default_value=get_safe_state_value(f"{state_prefix}.vehicle.{STATE_RANGE}", 350.0),
                min_value=50.0,
                max_value=3000.0,
                step=10.0,
                format="%.1f",
                impact_level="high",
                help_text="Maximum range on a full charge in kilometers"
            )
    
    # Create card for battery parameters
    with UIComponentFactory.create_card("Battery Parameters", f"v{vehicle_number}_battery", "bet"):
        col1, col2 = st.columns(2)
        
        with col1:
            battery_capacity = render_parameter_with_impact(
                "Battery Capacity (kWh)",
                f"{state_prefix}.vehicle.battery.capacity_kwh",
                default_value=get_safe_state_value(f"{state_prefix}.vehicle.battery.capacity_kwh", 400.0),
                min_value=100.0,
                max_value=1000.0,
                step=10.0,
                format="%.1f",
                impact_level="high",
                help_text="Total battery capacity in kilowatt-hours"
            )
            
            usable_capacity = render_parameter_with_impact(
                "Usable Capacity (%)",
                f"{state_prefix}.vehicle.battery.usable_capacity_percentage",
                default_value=get_safe_state_value(f"{state_prefix}.vehicle.battery.usable_capacity_percentage", 0.9),
                min_value=0.7,
                max_value=1.0,
                step=0.01,
                format="%.2f",
                impact_level="medium",
                help_text="Percentage of battery capacity that is usable"
            )
        
        with col2:
            degradation_rate = render_parameter_with_impact(
                "Annual Degradation Rate (%)",
                f"{state_prefix}.vehicle.battery.degradation_rate_annual",
                default_value=get_safe_state_value(f"{state_prefix}.vehicle.battery.degradation_rate_annual", 0.02),
                min_value=0.0,
                max_value=0.10,
                step=0.005,
                format="%.3f",
                impact_level="medium",
                help_text="Annual rate of battery capacity degradation"
            )
            
            replacement_threshold = render_parameter_with_impact(
                "Replacement Threshold (%)",
                f"{state_prefix}.vehicle.battery.replacement_threshold",
                default_value=get_safe_state_value(f"{state_prefix}.vehicle.battery.replacement_threshold", 0.7),
                min_value=0.5,
                max_value=0.9,
                step=0.05,
                format="%.2f",
                impact_level="low",
                help_text="Battery capacity threshold at which replacement is needed"
            )
    
    # Create card for energy consumption
    with UIComponentFactory.create_card("Energy Consumption", f"v{vehicle_number}_energy", "bet"):
        # Base consumption rate
        base_consumption = render_parameter_with_impact(
            "Base Energy Consumption (kWh/km)",
            f"{state_prefix}.vehicle.energy_consumption.base_rate",
            default_value=get_safe_state_value(f"{state_prefix}.vehicle.energy_consumption.base_rate", 1.45),
            min_value=0.5,
            max_value=3.0,
            step=0.05,
            format="%.2f",
            impact_level="high",
            help_text="Base energy consumption per kilometer under standard conditions"
        )
        
        # Min/max consumption ranges
        col1, col2 = st.columns(2)
        
        with col1:
            min_consumption = render_parameter_with_impact(
                "Minimum Consumption (kWh/km)",
                f"{state_prefix}.vehicle.energy_consumption.min_rate",
                default_value=get_safe_state_value(f"{state_prefix}.vehicle.energy_consumption.min_rate", 1.2),
                min_value=0.3,
                max_value=base_consumption,
                step=0.05,
                format="%.2f",
                impact_level="low",
                help_text="Minimum energy consumption under ideal conditions"
            )
        
        with col2:
            max_consumption = render_parameter_with_impact(
                "Maximum Consumption (kWh/km)",
                f"{state_prefix}.vehicle.energy_consumption.max_rate",
                default_value=get_safe_state_value(f"{state_prefix}.vehicle.energy_consumption.max_rate", 1.7),
                min_value=base_consumption,
                max_value=5.0,
                step=0.05,
                format="%.2f",
                impact_level="low",
                help_text="Maximum energy consumption under adverse conditions"
            )


def render_diesel_performance_parameters(vehicle_number: int, state_prefix: str) -> None:
    """
    Render diesel-specific performance parameters
    
    Args:
        vehicle_number: Vehicle number
        state_prefix: State key prefix
    """
    # Create card for performance parameters
    with UIComponentFactory.create_card("Performance Parameters", f"v{vehicle_number}_diesel_performance", "diesel"):
        # Performance metrics
        col1, col2 = st.columns(2)
        
        with col1:
            # Purchase price with impact indicator
            purchase_price = render_parameter_with_impact(
                "Purchase Price (AUD)",
                f"{state_prefix}.vehicle.{STATE_PURCHASE_PRICE}",
                default_value=get_safe_state_value(f"{state_prefix}.vehicle.{STATE_PURCHASE_PRICE}", 200000.0),
                min_value=50000.0,
                max_value=1000000.0,
                step=10000.0,
                format="%.2f",
                impact_level="high",
                help_text="The current purchase price of the vehicle"
            )
            
            # Annual price decrease
            annual_price_decrease = render_parameter_with_impact(
                "Annual Price Decrease (%)",
                f"{state_prefix}.vehicle.{STATE_ANNUAL_PRICE_DECREASE}",
                default_value=get_safe_state_value(f"{state_prefix}.vehicle.{STATE_ANNUAL_PRICE_DECREASE}", 0.0),
                min_value=0.0,
                max_value=0.10,
                step=0.005,
                format="%.3f",
                impact_level="low",
                help_text="Expected annual decrease in purchase price in real terms"
            )
        
        with col2:
            # Max payload
            max_payload = render_parameter_with_impact(
                "Maximum Payload (tonnes)",
                f"{state_prefix}.vehicle.{STATE_MAX_PAYLOAD}",
                default_value=get_safe_state_value(f"{state_prefix}.vehicle.{STATE_MAX_PAYLOAD}", 28.0),
                min_value=1.0,
                max_value=50.0,
                step=0.5,
                format="%.1f",
                impact_level="medium",
                help_text="Maximum payload capacity in tonnes"
            )
            
            # Range
            range_km = render_parameter_with_impact(
                "Range (km)",
                f"{state_prefix}.vehicle.{STATE_RANGE}",
                default_value=get_safe_state_value(f"{state_prefix}.vehicle.{STATE_RANGE}", 2200.0),
                min_value=50.0,
                max_value=3000.0,
                step=100.0,
                format="%.1f",
                impact_level="medium",
                help_text="Maximum range on a full tank in kilometers"
            )
    
    # Create card for engine parameters
    with UIComponentFactory.create_card("Engine Parameters", f"v{vehicle_number}_engine", "diesel"):
        col1, col2 = st.columns(2)
        
        with col1:
            # Engine power
            engine_power = render_parameter_with_impact(
                "Engine Power (kW)",
                f"{state_prefix}.vehicle.engine.power_kw",
                default_value=get_safe_state_value(f"{state_prefix}.vehicle.engine.power_kw", 350.0),
                min_value=100.0,
                max_value=600.0,
                step=10.0,
                format="%.1f",
                impact_level="low",
                help_text="Engine power in kilowatts"
            )
            
            # Engine efficiency
            engine_efficiency = render_parameter_with_impact(
                "Engine Efficiency",
                f"{state_prefix}.vehicle.engine.efficiency",
                default_value=get_safe_state_value(f"{state_prefix}.vehicle.engine.efficiency", 0.4),
                min_value=0.2,
                max_value=0.5,
                step=0.01,
                format="%.2f",
                impact_level="medium",
                help_text="Engine thermal efficiency"
            )
        
        with col2:
            # Emissions standard
            emissions_standard = st.selectbox(
                "Emissions Standard",
                options=["Euro III", "Euro IV", "Euro V", "Euro VI"],
                index=3,
                key=f"{state_prefix}.vehicle.engine.emissions_standard_input",
                help="Engine emissions standard"
            )
            set_safe_state_value(f"{state_prefix}.vehicle.engine.emissions_standard", emissions_standard)
            
            # AdBlue consumption
            adblue_consumption = render_parameter_with_impact(
                "AdBlue Consumption (%)",
                f"{state_prefix}.vehicle.engine.adblue_consumption_percentage",
                default_value=get_safe_state_value(f"{state_prefix}.vehicle.engine.adblue_consumption_percentage", 0.05),
                min_value=0.0,
                max_value=0.1,
                step=0.005,
                format="%.3f",
                impact_level="low",
                help_text="AdBlue consumption as a percentage of diesel consumption"
            )
    
    # Create card for fuel consumption
    with UIComponentFactory.create_card("Fuel Consumption", f"v{vehicle_number}_fuel", "diesel"):
        # Base consumption rate
        base_consumption = render_parameter_with_impact(
            "Base Fuel Consumption (L/100km)",
            f"{state_prefix}.vehicle.fuel_consumption.base_rate_l_per_100km",
            default_value=get_safe_state_value(f"{state_prefix}.vehicle.fuel_consumption.base_rate_l_per_100km", 38.0),
            min_value=10.0,
            max_value=100.0,
            step=0.5,
            format="%.1f",
            impact_level="high",
            help_text="Base fuel consumption per 100km under standard conditions"
        )
        
        # Min/max consumption ranges
        col1, col2 = st.columns(2)
        
        with col1:
            min_consumption = render_parameter_with_impact(
                "Minimum Consumption (L/100km)",
                f"{state_prefix}.vehicle.fuel_consumption.min_rate_l_per_100km",
                default_value=get_safe_state_value(f"{state_prefix}.vehicle.fuel_consumption.min_rate_l_per_100km", 34.0),
                min_value=10.0,
                max_value=base_consumption,
                step=0.5,
                format="%.1f",
                impact_level="low",
                help_text="Minimum fuel consumption under ideal conditions"
            )
        
        with col2:
            max_consumption = render_parameter_with_impact(
                "Maximum Consumption (L/100km)",
                f"{state_prefix}.vehicle.fuel_consumption.max_rate_l_per_100km",
                default_value=get_safe_state_value(f"{state_prefix}.vehicle.fuel_consumption.max_rate_l_per_100km", 42.0),
                min_value=base_consumption,
                max_value=120.0,
                step=0.5,
                format="%.1f",
                impact_level="low",
                help_text="Maximum fuel consumption under adverse conditions"
            )


def render_advanced_parameters(vehicle_number: int, state_prefix: str, vehicle_type: str) -> None:
    """
    Render advanced vehicle parameters
    
    Args:
        vehicle_number: Vehicle number
        state_prefix: State key prefix
        vehicle_type: Vehicle type
    """
    # Vehicle type-specific advanced parameters
    if vehicle_type == "bet":
        # Create card for charging parameters
        with UIComponentFactory.create_card("Charging Parameters", f"v{vehicle_number}_charging", "bet"):
            col1, col2 = st.columns(2)
            
            with col1:
                max_charging_power = render_parameter_with_impact(
                    "Max Charging Power (kW)",
                    f"{state_prefix}.vehicle.charging.max_charging_power_kw",
                    default_value=get_safe_state_value(f"{state_prefix}.vehicle.charging.max_charging_power_kw", 350.0),
                    min_value=50.0,
                    max_value=1000.0,
                    step=10.0,
                    format="%.1f",
                    impact_level="medium",
                    help_text="Maximum power at which the vehicle can charge"
                )
            
            with col2:
                charging_efficiency = render_parameter_with_impact(
                    "Charging Efficiency",
                    f"{state_prefix}.vehicle.charging.charging_efficiency",
                    default_value=get_safe_state_value(f"{state_prefix}.vehicle.charging.charging_efficiency", 0.9),
                    min_value=0.7,
                    max_value=1.0,
                    step=0.01,
                    format="%.2f",
                    impact_level="low",
                    help_text="Efficiency of the charging process (grid to battery)"
                )
        
        # Create card for infrastructure parameters
        with UIComponentFactory.create_card("Infrastructure Parameters", f"v{vehicle_number}_infrastructure", "bet"):
            col1, col2 = st.columns(2)
            
            with col1:
                charger_cost = render_parameter_with_impact(
                    "Charger Hardware Cost (AUD)",
                    f"{state_prefix}.vehicle.infrastructure.charger_hardware_cost",
                    default_value=get_safe_state_value(f"{state_prefix}.vehicle.infrastructure.charger_hardware_cost", 150000.0),
                    min_value=10000.0,
                    max_value=500000.0,
                    step=5000.0,
                    format="%.2f",
                    impact_level="medium",
                    help_text="Cost of the charging hardware"
                )
                
                installation_cost = render_parameter_with_impact(
                    "Installation Cost (AUD)",
                    f"{state_prefix}.vehicle.infrastructure.installation_cost",
                    default_value=get_safe_state_value(f"{state_prefix}.vehicle.infrastructure.installation_cost", 50000.0),
                    min_value=0.0,
                    max_value=200000.0,
                    step=5000.0,
                    format="%.2f",
                    impact_level="medium",
                    help_text="Cost of installing the charging infrastructure"
                )
            
            with col2:
                trucks_per_charger = render_parameter_with_impact(
                    "Trucks Per Charger",
                    f"{state_prefix}.vehicle.infrastructure.trucks_per_charger",
                    default_value=get_safe_state_value(f"{state_prefix}.vehicle.infrastructure.trucks_per_charger", 1.0),
                    min_value=0.5,
                    max_value=10.0,
                    step=0.5,
                    format="%.1f",
                    impact_level="medium",
                    help_text="Number of trucks sharing each charger"
                )
                
                grid_upgrade = render_parameter_with_impact(
                    "Grid Upgrade Cost (AUD)",
                    f"{state_prefix}.vehicle.infrastructure.grid_upgrade_cost",
                    default_value=get_safe_state_value(f"{state_prefix}.vehicle.infrastructure.grid_upgrade_cost", 0.0),
                    min_value=0.0,
                    max_value=500000.0,
                    step=10000.0,
                    format="%.2f",
                    impact_level="medium",
                    help_text="Cost of any grid upgrades required for charging infrastructure"
                )
    else:
        # Create card for maintenance parameters
        with UIComponentFactory.create_card("Maintenance Parameters", f"v{vehicle_number}_maintenance", "diesel"):
            col1, col2 = st.columns(2)
            
            with col1:
                maintenance_cost = render_parameter_with_impact(
                    "Maintenance Cost (AUD/km)",
                    f"{state_prefix}.vehicle.maintenance.cost_per_km",
                    default_value=get_safe_state_value(f"{state_prefix}.vehicle.maintenance.cost_per_km", 0.15),
                    min_value=0.05,
                    max_value=1.0,
                    step=0.01,
                    format="%.2f",
                    impact_level="high",
                    help_text="Maintenance cost per kilometer"
                )
            
            with col2:
                maintenance_increase = render_parameter_with_impact(
                    "Annual Maintenance Increase (%)",
                    f"{state_prefix}.vehicle.maintenance.annual_increase_percentage",
                    default_value=get_safe_state_value(f"{state_prefix}.vehicle.maintenance.annual_increase_percentage", 0.02),
                    min_value=0.0,
                    max_value=0.1,
                    step=0.005,
                    format="%.3f",
                    impact_level="medium",
                    help_text="Annual increase in maintenance costs"
                )
    
    # Create card for residual value parameters
    with UIComponentFactory.create_card("Residual Value", f"v{vehicle_number}_residual", vehicle_type):
        col1, col2 = st.columns(2)
        
        with col1:
            residual_value_percentage = render_parameter_with_impact(
                "Residual Value (%)",
                f"{state_prefix}.vehicle.residual_value.percentage",
                default_value=get_safe_state_value(f"{state_prefix}.vehicle.residual_value.percentage", 0.2),
                min_value=0.0,
                max_value=0.5,
                step=0.05,
                format="%.2f",
                impact_level="medium",
                help_text="Residual value as a percentage of purchase price"
            )
        
        with col2:
            residual_years = render_parameter_with_impact(
                "Residual Years",
                f"{state_prefix}.vehicle.residual_value.years",
                default_value=get_safe_state_value(f"{state_prefix}.vehicle.residual_value.years", 10),
                min_value=5,
                max_value=20,
                step=1,
                impact_level="low",
                help_text="Years at which the residual value applies"
            )


def display_derived_metrics(vehicle_number: int, state_prefix: str, vehicle_type: str) -> None:
    """
    Display derived metrics based on vehicle inputs
    
    Args:
        vehicle_number: Vehicle number
        state_prefix: State key prefix
        vehicle_type: Vehicle type string
    """
    # Show derived metrics in an expander
    with st.expander("Derived Metrics", expanded=False):
        cols = st.columns(2)
        
        # Common metrics for both vehicle types
        purchase_price = get_safe_state_value(f"{state_prefix}.vehicle.{STATE_PURCHASE_PRICE}", 0.0)
        max_payload = get_safe_state_value(f"{state_prefix}.vehicle.{STATE_MAX_PAYLOAD}", 0.0)
        range_km = get_safe_state_value(f"{state_prefix}.vehicle.{STATE_RANGE}", 0.0)
        
        with cols[0]:
            st.metric("Price per Tonne Capacity", 
                    format_currency(purchase_price / max_payload if max_payload > 0 else 0),
                    help="Purchase price divided by maximum payload capacity")
            
            st.metric("Price per km Range", 
                    format_currency(purchase_price / range_km if range_km > 0 else 0),
                    help="Purchase price divided by maximum range")
        
        # Vehicle type-specific metrics
        if vehicle_type == VehicleType.BATTERY_ELECTRIC.value:
            battery_capacity = get_safe_state_value(f"{state_prefix}.vehicle.battery.capacity_kwh", 0.0)
            base_consumption = get_safe_state_value(f"{state_prefix}.vehicle.energy_consumption.base_rate", 0.0)
            
            with cols[1]:
                st.metric("Battery Cost", 
                        format_currency(battery_capacity * 500),  # Assuming $500/kWh
                        help="Estimated battery cost at $500/kWh")
                
                theoretical_range = battery_capacity / base_consumption if base_consumption > 0 else 0
                st.metric("Theoretical Range (km)", 
                        f"{theoretical_range:.1f}",
                        delta=f"{theoretical_range - range_km:.1f}",
                        help="Theoretical range based on battery capacity and consumption")
        else:
            fuel_consumption = get_safe_state_value(f"{state_prefix}.vehicle.fuel_consumption.base_rate_l_per_100km", 0.0)
            tank_capacity = range_km * fuel_consumption / 100 if fuel_consumption > 0 else 0
            
            with cols[1]:
                st.metric("Estimated Tank Capacity (L)", 
                        f"{tank_capacity:.0f}",
                        help="Estimated fuel tank capacity based on range and consumption")
                
                fuel_efficiency = 100 / fuel_consumption if fuel_consumption > 0 else 0
                st.metric("Fuel Efficiency (km/L)", 
                        f"{fuel_efficiency:.2f}",
                        help="Distance travelled per litre of fuel") 