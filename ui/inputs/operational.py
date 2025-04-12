"""
Operational Input Module

This module renders the UI components for operational parameter inputs,
including annual distance, operating days, analysis period, and other
operational characteristics.
"""

import streamlit as st
from typing import Dict, Any, Optional

from utils.helpers import (
    get_safe_state_value, 
    set_safe_state_value, 
    initialize_nested_state,
    format_currency
)


# Constants for state keys
STATE_ANNUAL_DISTANCE = "annual_distance_km"
STATE_OPERATING_DAYS = "operating_days_per_year"
STATE_VEHICLE_LIFE = "vehicle_life_years"
STATE_REQUIRES_OVERNIGHT = "requires_overnight_charging"
STATE_IS_URBAN = "is_urban_operation"
STATE_LOAD_FACTOR = "average_load_factor"


def render_operational_inputs(vehicle_number: int) -> None:
    """
    Render the UI components for operational parameters.
    
    This function renders input fields for operational parameters such as
    annual distance, operating days, and operational environment.
    
    Args:
        vehicle_number: The vehicle number (1 or 2)
    """
    state_prefix = f"vehicle_{vehicle_number}_input"
    
    with st.expander("Operational Parameters", expanded=True):
        # Annual distance and operating days
        col1, col2 = st.columns(2)
        
        with col1:
            annual_distance = st.number_input(
                "Annual Distance (km)",
                min_value=1000,
                max_value=500000,
                value=int(get_safe_state_value(f"{state_prefix}.operational.{STATE_ANNUAL_DISTANCE}", 100000)),
                step=1000,
                key=f"{state_prefix}.operational.{STATE_ANNUAL_DISTANCE}_input",
                help="Total distance traveled per year in kilometers"
            )
            set_safe_state_value(f"{state_prefix}.operational.{STATE_ANNUAL_DISTANCE}", annual_distance)
        
        with col2:
            operating_days = st.slider(
                "Operating Days per Year",
                min_value=100,
                max_value=365,
                value=int(get_safe_state_value(f"{state_prefix}.operational.{STATE_OPERATING_DAYS}", 250)),
                key=f"{state_prefix}.operational.{STATE_OPERATING_DAYS}_input",
                help="Number of days the vehicle operates per year"
            )
            set_safe_state_value(f"{state_prefix}.operational.{STATE_OPERATING_DAYS}", operating_days)
        
        # Daily distance (calculated)
        daily_distance = annual_distance / operating_days if operating_days > 0 else 0
        st.info(f"Daily Distance: {daily_distance:.1f} km/day")
        
        # Vehicle life expectancy
        vehicle_life = st.slider(
            "Vehicle Life (years)",
            min_value=5,
            max_value=25,
            value=int(get_safe_state_value(f"{state_prefix}.operational.{STATE_VEHICLE_LIFE}", 15)),
            key=f"{state_prefix}.operational.{STATE_VEHICLE_LIFE}_input",
            help="Expected operational life of the vehicle in years"
        )
        set_safe_state_value(f"{state_prefix}.operational.{STATE_VEHICLE_LIFE}", vehicle_life)
        
        # Operational characteristics in columns
        col1, col2 = st.columns(2)
        
        with col1:
            requires_overnight = st.checkbox(
                "Requires Overnight Charging",
                value=bool(get_safe_state_value(f"{state_prefix}.operational.{STATE_REQUIRES_OVERNIGHT}", True)),
                key=f"{state_prefix}.operational.{STATE_REQUIRES_OVERNIGHT}_input",
                help="Whether the vehicle requires overnight charging (for BETs)"
            )
            set_safe_state_value(f"{state_prefix}.operational.{STATE_REQUIRES_OVERNIGHT}", requires_overnight)
        
        with col2:
            is_urban = st.checkbox(
                "Urban Operation",
                value=bool(get_safe_state_value(f"{state_prefix}.operational.{STATE_IS_URBAN}", False)),
                key=f"{state_prefix}.operational.{STATE_IS_URBAN}_input",
                help="Whether the vehicle operates primarily in urban environments"
            )
            set_safe_state_value(f"{state_prefix}.operational.{STATE_IS_URBAN}", is_urban)
        
        # Load factor
        load_factor = st.slider(
            "Average Load Factor (%)",
            min_value=0,
            max_value=100,
            value=int(get_safe_state_value(f"{state_prefix}.operational.{STATE_LOAD_FACTOR}", 0.8) * 100),
            key=f"{state_prefix}.operational.{STATE_LOAD_FACTOR}_input",
            help="Average load as a percentage of maximum capacity"
        )
        set_safe_state_value(f"{state_prefix}.operational.{STATE_LOAD_FACTOR}", load_factor / 100.0)
        
        # Display operational profile summary
        st.subheader("Operational Profile Summary")
        
        # Determine operational profile based on inputs
        profile_name = "Urban Distribution" if is_urban else "Regional" if daily_distance < 500 else "Long-haul"
        
        cols = st.columns(3)
        with cols[0]:
            st.metric("Profile Type", profile_name)
        with cols[1]:
            st.metric("Annual Distance", f"{annual_distance:,} km")
        with cols[2]:
            if requires_overnight:
                st.metric("Charging Strategy", "Overnight Depot")
            else:
                st.metric("Charging Strategy", "Opportunity")
        
        # Additional operational statistics
        if st.checkbox("Show Additional Statistics", value=False):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Daily Distance", f"{daily_distance:.1f} km")
                st.metric("Total Lifetime Distance", f"{annual_distance * vehicle_life:,} km")
            
            with col2:
                st.metric("Average Speed", f"{daily_distance / 8:.1f} km/h" if daily_distance > 0 else "N/A")
                st.metric("Working Hours/Day", "8 hours")
            
            with col3:
                st.metric("Daily Stops", "Multiple" if is_urban else "Few")
                st.metric("Load Factor", f"{load_factor}%") 