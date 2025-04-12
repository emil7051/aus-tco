"""
Operational Input Module

This module renders the UI components for operational parameter inputs.
"""

import streamlit as st
from typing import Dict, Any, Optional

from utils.helpers import get_safe_state_value, set_safe_state_value


def render_operational_inputs(vehicle_number: int):
    """
    Render the UI components for operational parameters.
    
    Args:
        vehicle_number: The vehicle number (1 or 2)
    """
    state_prefix = f"vehicle_{vehicle_number}_input.operational"
    
    # Create a form for the operational parameters
    with st.form(key=f"operational_{vehicle_number}_form"):
        st.subheader("Operational Parameters")
        
        # Annual distance
        annual_distance = st.number_input(
            "Annual Distance (km)",
            min_value=0,
            value=get_safe_state_value(f"{state_prefix}.annual_distance", 100000),
            key=f"{state_prefix}.annual_distance",
        )
        
        # Operating days
        operating_days = st.slider(
            "Operating Days per Year",
            min_value=1,
            max_value=365,
            value=get_safe_state_value(f"{state_prefix}.operating_days", 260),
            key=f"{state_prefix}.operating_days",
        )
        
        # Analysis period
        col1, col2 = st.columns(2)
        
        with col1:
            analysis_period = st.slider(
                "Analysis Period (years)",
                min_value=1,
                max_value=25,
                value=get_safe_state_value(f"{state_prefix}.analysis_period", 15),
                key=f"{state_prefix}.analysis_period",
            )
        
        with col2:
            payload = st.number_input(
                "Payload (tonnes)",
                min_value=0.0,
                value=get_safe_state_value(f"{state_prefix}.payload", 20.0),
                format="%.1f",
                key=f"{state_prefix}.payload",
            )
        
        # Utilization
        utilization = st.slider(
            "Utilization (%)",
            min_value=0,
            max_value=100,
            value=get_safe_state_value(f"{state_prefix}.utilization", 80),
            key=f"{state_prefix}.utilization",
        )
        
        # Operational profile
        operational_profile = st.selectbox(
            "Operational Profile",
            options=["Urban", "Regional", "Long-haul"],
            index=get_safe_state_value(f"{state_prefix}.profile_index", 1),
            key=f"{state_prefix}.profile",
        )
        
        # Submit button
        submitted = st.form_submit_button("Update Operational Parameters")
        
        if submitted:
            # Update session state with the form values
            set_safe_state_value(f"{state_prefix}.annual_distance", annual_distance)
            set_safe_state_value(f"{state_prefix}.operating_days", operating_days)
            set_safe_state_value(f"{state_prefix}.analysis_period", analysis_period)
            set_safe_state_value(f"{state_prefix}.payload", payload)
            set_safe_state_value(f"{state_prefix}.utilization", utilization)
            set_safe_state_value(f"{state_prefix}.profile", operational_profile)
            set_safe_state_value(f"{state_prefix}.profile_index", 
                                ["Urban", "Regional", "Long-haul"].index(operational_profile))
            
            st.success("Operational parameters updated!") 