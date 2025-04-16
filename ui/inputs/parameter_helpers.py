"""
Parameter Helpers Module

This module provides helper functions for rendering parameters with impact indicators
and additional visual feedback to enhance the user experience.
"""

import streamlit as st
from typing import Dict, Any, Optional, List, Tuple, Union

from utils.helpers import get_safe_state_value, set_safe_state_value
from utils.ui_terminology import create_impact_indicator, get_formatted_label
from ui.inputs.validation import create_validated_input, validate_parameter


def render_parameter_with_impact(
    label: str, 
    key: str, 
    default_value: Any, 
    impact_level: str = "medium", 
    help_text: str = None,
    **input_args
) -> Any:
    """
    Render a parameter input with impact indicator
    
    Args:
        label: Parameter label
        key: State key
        default_value: Default value
        impact_level: Impact level (high/medium/low)
        help_text: Help text to display
        **input_args: Additional input arguments
        
    Returns:
        Parameter value
    """
    # Debug output
    print(f"DEBUG render_parameter_with_impact: Key={key}, Default value type={type(default_value)}, Value={default_value}")
    
    # Create a container for the parameter with impact indicator
    container = st.container()
    
    # Add custom CSS to position the impact indicator
    st.markdown("""
    <style>
    .parameter-container {
        position: relative;
        width: 100%;
    }
    .impact-indicator-overlay {
        position: absolute;
        top: 2px;
        right: 8px;
        z-index: 1000;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Get impact details based on parameter name
    param_name = key.split('.')[-1]
    impact_info = create_impact_indicator(param_name)
    
    # Determine input type based on default value
    input_type = "number"
    if isinstance(default_value, bool):
        input_type = "checkbox"
    elif isinstance(default_value, str):
        input_type = "text"
    elif "min_value" in input_args and "max_value" in input_args and "step" in input_args:
        input_type = "slider"
        
        # Handle case where default value is a list but min/max are not
        if isinstance(default_value, list) and len(default_value) == 2:
            # Create a copy of input_args to avoid modifying the original
            slider_args = input_args.copy()
            
            # For range sliders, convert min_value and max_value to lists if they're not already
            if not isinstance(slider_args.get("min_value"), list):
                min_val = slider_args.get("min_value", 0)
                slider_args["min_value"] = [min_val, min_val]
            
            if not isinstance(slider_args.get("max_value"), list):
                max_val = slider_args.get("max_value", 100)
                slider_args["max_value"] = [max_val, max_val]
            
            # Remove input_type from slider_args if present
            if "input_type" in slider_args:
                del slider_args["input_type"]
            
            # Create the input field with modified args
            with container:
                value, validation_result = create_validated_input(
                    label=label,
                    key=key,
                    default=default_value,
                    help_text=help_text,
                    input_type="slider",
                    **slider_args
                )
        else:
            # Standard case
            input_args_copy = input_args.copy()
            if "input_type" in input_args_copy:
                del input_args_copy["input_type"]
                
            with container:
                value, validation_result = create_validated_input(
                    label=label,
                    key=key,
                    default=default_value,
                    help_text=help_text,
                    input_type="slider",
                    **input_args_copy
                )
    else:
        # Create the input field
        if input_type == "number_input":
            with container:
                input_args_copy = input_args.copy()
                if "input_type" in input_args_copy:
                    del input_args_copy["input_type"]
                value, validation_result = create_validated_input(
                    label=label,
                    key=key,
                    default=default_value,
                    help_text=help_text,
                    input_type="number",
                    **input_args_copy
                )
        elif input_type == "slider":
            with container:
                input_args_copy = input_args.copy()
                if "input_type" in input_args_copy:
                    del input_args_copy["input_type"]
                value, validation_result = create_validated_input(
                    label=label,
                    key=key,
                    default=default_value,
                    help_text=help_text,
                    input_type="slider",
                    **input_args_copy
                )
        else:
            # Default case for other input types
            with container:
                input_args_copy = input_args.copy()
                if "input_type" in input_args_copy:
                    del input_args_copy["input_type"]
                value, validation_result = create_validated_input(
                    label=label,
                    key=key,
                    default=default_value,
                    help_text=help_text,
                    input_type=input_type,
                    **input_args_copy
                )
    
    # Add impact indicator as HTML overlay
    st.markdown(f"""
    <div class="impact-indicator-overlay" 
         title="{impact_info['tooltip']}">
        <div class="impact-indicator {impact_info['class']}">
            {impact_info['icon']}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    return value


def get_parameter_impact(key: str) -> Dict[str, str]:
    """
    Get parameter impact information
    
    Args:
        key: Parameter key
        
    Returns:
        Dictionary with impact information
    """
    # Extract parameter name from key
    param_name = key.split('.')[-1]
    
    # Get impact information
    return create_impact_indicator(param_name)


def render_parameter_comparison(param_path: str) -> None:
    """
    Render side-by-side comparison of a parameter between vehicles
    
    Args:
        param_path: Parameter path to compare
    """
    # Get values from both vehicles
    v1_value = get_safe_state_value(f"vehicle_1_input.{param_path}")
    v2_value = get_safe_state_value(f"vehicle_2_input.{param_path}")
    
    # Skip if either value is missing
    if v1_value is None or v2_value is None:
        return
    
    # Create comparison UI
    st.markdown('<div class="parameter-comparison">', unsafe_allow_html=True)
    
    # Parameter name/label
    param_name = param_path.split('.')[-1]
    label = get_formatted_label(param_name)
    st.markdown(f'<div class="param-label">{label}</div>', unsafe_allow_html=True)
    
    # Value comparison
    cols = st.columns([2, 2, 3])
    
    with cols[0]:
        st.markdown(f'<div class="param-vehicle">Vehicle 1</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="param-value v1">{format_parameter_value(param_name, v1_value)}</div>', 
                   unsafe_allow_html=True)
    
    with cols[1]:
        st.markdown(f'<div class="param-vehicle">Vehicle 2</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="param-value v2">{format_parameter_value(param_name, v2_value)}</div>', 
                   unsafe_allow_html=True)
    
    with cols[2]:
        # Calculate the difference
        if isinstance(v1_value, (int, float)) and isinstance(v2_value, (int, float)):
            diff = v2_value - v1_value
            diff_pct = (diff / v1_value * 100) if v1_value != 0 else 0
            
            # Format difference text
            if abs(diff) < 0.001:
                diff_text = "No difference"
                diff_class = "neutral"
            else:
                diff_text = f"{diff:+.3g} ({diff_pct:+.1f}%)"
                diff_class = "positive" if diff > 0 else "negative"
            
            st.markdown(f'<div class="param-diff {diff_class}">{diff_text}</div>', 
                       unsafe_allow_html=True)
        else:
            # Non-numeric comparison
            diff_class = "neutral" if v1_value == v2_value else "different"
            diff_text = "Same" if v1_value == v2_value else "Different"
            st.markdown(f'<div class="param-diff {diff_class}">{diff_text}</div>', 
                       unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)


def format_parameter_value(param_name: str, value: Any) -> str:
    """
    Format parameter value for display
    
    Args:
        param_name: Parameter name
        value: Parameter value
        
    Returns:
        Formatted value string
    """
    if isinstance(value, bool):
        return "Yes" if value else "No"
    
    # Format based on parameter type
    if "rate" in param_name and isinstance(value, (int, float)) and value <= 1.0:
        # Format as percentage
        return f"{value * 100:.1f}%"
    elif "price" in param_name or "cost" in param_name:
        # Format as currency
        return f"${value:,.2f}"
    elif param_name == "annual_distance_km" or param_name == "daily_distance_km":
        # Format with commas
        return f"{value:,.0f} km"
    elif isinstance(value, (int, float)):
        # Generic numeric formatting
        if abs(value) >= 1000:
            return f"{value:,.0f}"
        elif abs(value) >= 10:
            return f"{value:.1f}"
        else:
            return f"{value:.3g}"
    
    # Default format as string
    return str(value)


def get_vehicle_type(state_prefix: str) -> str:
    """
    Get the vehicle type from the session state
    
    Args:
        state_prefix: State prefix
        
    Returns:
        Vehicle type value as canonical string (battery_electric or diesel)
    """
    from tco_model.schemas import VehicleType
    
    # Get vehicle type
    vehicle_type = get_safe_state_value(f"{state_prefix}.vehicle.type", VehicleType.DIESEL.value)
    
    # Return canonical value
    if vehicle_type == VehicleType.BATTERY_ELECTRIC.value:
        return VehicleType.BATTERY_ELECTRIC.value
    else:
        return VehicleType.DIESEL.value


def render_vehicle_header(vehicle_number: int, vehicle_type: str) -> None:
    """
    Render vehicle header with type indicator
    
    Args:
        vehicle_number: Vehicle number
        vehicle_type: Vehicle type
    """
    state_prefix = f"vehicle_{vehicle_number}_input"
    vehicle_name = get_safe_state_value(f"{state_prefix}.vehicle.name", f"Vehicle {vehicle_number}")
    
    # Create header with vehicle type styling
    st.markdown(f"""
    <div class="vehicle-header {vehicle_type}">
        <h2 class="vehicle-title">{vehicle_name}</h2>
        <div class="vehicle-type-badge">{vehicle_type.upper()}</div>
    </div>
    """, unsafe_allow_html=True) 