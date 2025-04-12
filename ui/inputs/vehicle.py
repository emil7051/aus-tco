"""
Vehicle Input Module

This module renders the UI components for vehicle parameter inputs.
"""

import streamlit as st
from typing import Dict, Any, Optional

from tco_model.models import VehicleType, VehicleCategory
from utils.helpers import get_safe_state_value, set_safe_state_value


def render_vehicle_inputs(vehicle_number: int):
    """
    Render the UI components for vehicle parameters.
    
    Args:
        vehicle_number: The vehicle number (1 or 2)
    """
    state_prefix = f"vehicle_{vehicle_number}_input.vehicle"
    
    # Create a form for the vehicle parameters
    with st.form(key=f"vehicle_{vehicle_number}_form"):
        st.subheader("Vehicle Parameters")
        
        # Vehicle name
        vehicle_name = st.text_input(
            "Vehicle Name",
            value=get_safe_state_value(f"{state_prefix}.name", ""),
            key=f"{state_prefix}.name",
        )
        
        # Vehicle type
        col1, col2 = st.columns(2)
        
        with col1:
            vehicle_type = st.selectbox(
                "Vehicle Type",
                options=[vt.value for vt in VehicleType],
                index=0 if vehicle_number == 1 else 1,  # BET for vehicle 1, DIESEL for vehicle 2
                key=f"{state_prefix}.type",
            )
        
        with col2:
            vehicle_category = st.selectbox(
                "Vehicle Category",
                options=[vc.value for vc in VehicleCategory],
                key=f"{state_prefix}.category",
            )
        
        # Purchase price
        purchase_price = st.number_input(
            "Purchase Price (AUD)",
            min_value=0.0,
            value=get_safe_state_value(f"{state_prefix}.purchase_price", 500000.0),
            format="%.2f",
            key=f"{state_prefix}.purchase_price",
        )
        
        # Vehicle-specific parameters based on type
        if vehicle_type == VehicleType.BATTERY_ELECTRIC.value:
            render_bet_parameters(vehicle_number, state_prefix)
        else:
            render_diesel_parameters(vehicle_number, state_prefix)
        
        # Submit button
        submitted = st.form_submit_button("Update Vehicle Parameters")
        
        if submitted:
            # Update session state with the form values
            set_safe_state_value(f"{state_prefix}.name", vehicle_name)
            set_safe_state_value(f"{state_prefix}.type", vehicle_type)
            set_safe_state_value(f"{state_prefix}.category", vehicle_category)
            set_safe_state_value(f"{state_prefix}.purchase_price", purchase_price)
            
            st.success("Vehicle parameters updated!")


def render_bet_parameters(vehicle_number: int, state_prefix: str):
    """
    Render the UI components for BET-specific parameters.
    
    Args:
        vehicle_number: The vehicle number (1 or 2)
        state_prefix: The state prefix for session state access
    """
    st.subheader("Battery Electric Truck Parameters")
    
    # Battery capacity
    battery_capacity = st.number_input(
        "Battery Capacity (kWh)",
        min_value=0.0,
        value=get_safe_state_value(f"{state_prefix}.battery.capacity", 400.0),
        format="%.1f",
        key=f"{state_prefix}.battery.capacity",
    )
    
    # Energy consumption
    energy_consumption = st.number_input(
        "Energy Consumption (kWh/km)",
        min_value=0.0,
        value=get_safe_state_value(f"{state_prefix}.consumption.base_rate", 1.5),
        format="%.2f",
        key=f"{state_prefix}.consumption.base_rate",
    )
    
    # Battery degradation
    col1, col2 = st.columns(2)
    
    with col1:
        degradation_rate = st.number_input(
            "Annual Degradation Rate (%)",
            min_value=0.0,
            max_value=100.0,
            value=get_safe_state_value(f"{state_prefix}.battery.degradation_rate", 2.0),
            format="%.1f",
            key=f"{state_prefix}.battery.degradation_rate",
        )
    
    with col2:
        replacement_threshold = st.number_input(
            "Replacement Threshold (%)",
            min_value=0.0,
            max_value=100.0,
            value=get_safe_state_value(f"{state_prefix}.battery.replacement_threshold", 80.0),
            format="%.1f",
            key=f"{state_prefix}.battery.replacement_threshold",
        )
    
    # Update session state values
    set_safe_state_value(f"{state_prefix}.battery.capacity", battery_capacity)
    set_safe_state_value(f"{state_prefix}.consumption.base_rate", energy_consumption)
    set_safe_state_value(f"{state_prefix}.battery.degradation_rate", degradation_rate)
    set_safe_state_value(f"{state_prefix}.battery.replacement_threshold", replacement_threshold)


def render_diesel_parameters(vehicle_number: int, state_prefix: str):
    """
    Render the UI components for diesel-specific parameters.
    
    Args:
        vehicle_number: The vehicle number (1 or 2)
        state_prefix: The state prefix for session state access
    """
    st.subheader("Diesel Truck Parameters")
    
    # Fuel consumption
    fuel_consumption = st.number_input(
        "Fuel Consumption (L/100km)",
        min_value=0.0,
        value=get_safe_state_value(f"{state_prefix}.consumption.base_rate", 35.0),
        format="%.1f",
        key=f"{state_prefix}.consumption.base_rate",
    )
    
    # Engine specifications
    col1, col2 = st.columns(2)
    
    with col1:
        engine_power = st.number_input(
            "Engine Power (kW)",
            min_value=0,
            value=get_safe_state_value(f"{state_prefix}.engine.power", 350),
            key=f"{state_prefix}.engine.power",
        )
    
    with col2:
        emissions_standard = st.selectbox(
            "Emissions Standard",
            options=["Euro V", "Euro VI"],
            index=1,
            key=f"{state_prefix}.engine.emissions_standard",
        )
    
    # Emissions
    emissions_rate = st.number_input(
        "CO2 Emissions (kg/L)",
        min_value=0.0,
        value=get_safe_state_value(f"{state_prefix}.emissions.co2_per_liter", 2.7),
        format="%.2f",
        key=f"{state_prefix}.emissions.co2_per_liter",
    )
    
    # Update session state values
    set_safe_state_value(f"{state_prefix}.consumption.base_rate", fuel_consumption)
    set_safe_state_value(f"{state_prefix}.engine.power", engine_power)
    set_safe_state_value(f"{state_prefix}.engine.emissions_standard", emissions_standard)
    set_safe_state_value(f"{state_prefix}.emissions.co2_per_liter", emissions_rate) 