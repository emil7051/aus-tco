"""
Parameter Comparison Module

This module provides utilities for comparing parameter values between vehicles
with visual feedback on the differences.
"""

import streamlit as st
from typing import Dict, Any, List, Optional, Tuple

from utils.helpers import get_safe_state_value
from utils.ui_terminology import get_formatted_label
from ui.inputs.parameter_helpers import format_parameter_value


def render_parameter_comparison_tool() -> None:
    """
    Render a tool for comparing parameter values between vehicles
    """
    st.markdown("## Parameter Comparison")
    st.markdown("Compare key parameters between vehicles to understand differences.")
    
    # Group parameters by category
    parameter_groups = {
        "Vehicle": [
            "vehicle.purchase_price",
            "vehicle.max_payload_tonnes",
            "vehicle.range_km",
            "vehicle.annual_price_decrease_real",
        ],
        "Operational": [
            "operational.annual_distance_km",
            "operational.vehicle_life_years",
            "operational.operating_days_per_year",
            "operational.average_load_factor",
            "operational.daily_distance_km",
        ],
        "Economic": [
            "economic.discount_rate_real",
            "economic.inflation_rate",
            "economic.analysis_period_years",
            "economic.carbon_tax_rate_aud_per_tonne",
        ],
    }
    
    # Create tabs for each parameter group
    tabs = st.tabs(list(parameter_groups.keys()))
    
    for i, (group, params) in enumerate(parameter_groups.items()):
        with tabs[i]:
            st.markdown(f"### {group} Parameters")
            
            # Render each parameter comparison
            for param in params:
                render_comparison(param)
                
                # Add divider
                st.markdown("<hr class='param-divider'>", unsafe_allow_html=True)


def render_comparison(param_path: str) -> None:
    """
    Render a comparison of a parameter between vehicles
    
    Args:
        param_path: Parameter path
    """
    # Get values from both vehicles
    v1_value = get_safe_state_value(f"vehicle_1_input.{param_path}")
    v2_value = get_safe_state_value(f"vehicle_2_input.{param_path}")
    
    # Skip if either value is missing
    if v1_value is None or v2_value is None:
        return
    
    # Parameter name/label
    param_name = param_path.split('.')[-1]
    label = get_formatted_label(param_name)
    
    # Display comparison in columns
    cols = st.columns([3, 2, 2, 4])
    
    # Parameter label
    with cols[0]:
        st.markdown(f"<div class='param-label'>{label}</div>", unsafe_allow_html=True)
    
    # Vehicle 1 value
    with cols[1]:
        v1_formatted = format_parameter_value(param_name, v1_value)
        st.markdown(f"<div class='param-value vehicle-1'>{v1_formatted}</div>", unsafe_allow_html=True)
    
    # Vehicle 2 value
    with cols[2]:
        v2_formatted = format_parameter_value(param_name, v2_value)
        st.markdown(f"<div class='param-value vehicle-2'>{v2_formatted}</div>", unsafe_allow_html=True)
    
    # Difference indicator
    with cols[3]:
        if isinstance(v1_value, (int, float)) and isinstance(v2_value, (int, float)):
            # Calculate difference
            diff = v2_value - v1_value
            if v1_value != 0:
                diff_pct = (diff / v1_value) * 100
            else:
                diff_pct = 0 if diff == 0 else float('inf')
            
            # Determine significance
            if abs(diff_pct) < 1:
                significance = "minimal"
            elif abs(diff_pct) < 10:
                significance = "moderate"
            else:
                significance = "significant"
            
            # Format difference text
            if abs(diff) < 0.001:
                diff_text = "No difference"
            else:
                diff_text = f"{diff:+.3g} ({diff_pct:+.1f}%)"
            
            # Render difference with appropriate styling
            st.markdown(f"""
            <div class='diff-indicator {significance} {"positive" if diff > 0 else "negative" if diff < 0 else "neutral"}'>
                {diff_text}
            </div>
            """, unsafe_allow_html=True)
        else:
            # For non-numeric values, just indicate if they're the same or different
            if v1_value == v2_value:
                st.markdown("<div class='diff-indicator same'>Same value</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='diff-indicator different'>Different values</div>", unsafe_allow_html=True)


def add_parameter_comparison_css() -> None:
    """
    Add custom CSS for parameter comparison
    """
    st.markdown("""
    <style>
    .param-label {
        font-weight: 600;
        font-size: 1rem;
    }
    
    .param-value {
        font-family: monospace;
        font-size: 0.9rem;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
    }
    
    .param-value.vehicle-1 {
        background-color: rgba(38, 166, 154, 0.1);
        border-left: 3px solid #26A69A;
    }
    
    .param-value.vehicle-2 {
        background-color: rgba(251, 140, 0, 0.1);
        border-left: 3px solid #FB8C00;
    }
    
    .diff-indicator {
        font-family: monospace;
        font-size: 0.9rem;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        display: inline-block;
    }
    
    .diff-indicator.positive {
        color: #2E7D32;
        background-color: rgba(46, 125, 50, 0.1);
    }
    
    .diff-indicator.negative {
        color: #D32F2F;
        background-color: rgba(211, 47, 47, 0.1);
    }
    
    .diff-indicator.neutral {
        color: #455A64;
        background-color: rgba(69, 90, 100, 0.1);
    }
    
    .diff-indicator.minimal {
        opacity: 0.7;
    }
    
    .diff-indicator.significant {
        font-weight: 600;
    }
    
    .param-divider {
        margin: 0.5rem 0;
        border: none;
        border-top: 1px solid rgba(0, 0, 0, 0.1);
    }
    </style>
    """, unsafe_allow_html=True) 