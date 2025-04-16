"""
Validation System for Input Parameters

This module provides a comprehensive validation system for input parameters, ensuring that
user inputs are valid within defined constraints and providing appropriate feedback.
"""

from typing import Dict, Any, Optional, Callable, List, Union
import random

def validate_parameter(key: str, value: Any) -> Dict[str, Any]:
    """
    Validate a parameter value based on its key
    
    Args:
        key: Parameter key
        value: Parameter value
        
    Returns:
        Dictionary with validation result and message
    """
    # Extract parameter name from key
    param_name = key.split('.')[-1]
    
    # Define validation rules for specific parameters
    validation_rules = {
        "annual_distance_km": {
            "min": 1000, 
            "max": 500000,
            "message": "Annual distance must be between 1,000 and 500,000 km"
        },
        "analysis_period_years": {
            "min": 1,
            "max": 30,
            "message": "Analysis period must be between 1 and 30 years"
        },
        "purchase_price": {
            "min": 1000,
            "max": 10000000,
            "message": "Purchase price must be between $1,000 and $10,000,000"
        },
        "discount_rate_real": {
            "min": 0.0,
            "max": 0.2,
            "message": "Discount rate must be between 0% and 20%"
        },
        "inflation_rate": {
            "min": 0.0,
            "max": 0.15,
            "message": "Inflation rate must be between 0% and 15%"
        },
        "carbon_tax_rate_aud_per_tonne": {
            "min": 0.0,
            "max": 500.0,
            "message": "Carbon tax rate must be between $0 and $500 per tonne"
        },
        "vehicle_life_years": {
            "min": 1,
            "max": 30,
            "message": "Vehicle life must be between 1 and 30 years"
        },
        "operating_days_per_year": {
            "min": 1,
            "max": 365,
            "message": "Operating days must be between 1 and 365 days"
        },
        "daily_distance_km": {
            "min": 1,
            "max": 2000,
            "message": "Daily distance must be between 1 and 2,000 km"
        },
        "average_load_factor": {
            "min": 0.0,
            "max": 1.0,
            "message": "Load factor must be between 0 and 1.0"
        },
        "capacity_kwh": {
            "min": 50,
            "max": 1000,
            "message": "Battery capacity must be between 50 and 1,000 kWh"
        },
        "usable_capacity_percentage": {
            "min": 0.5,
            "max": 1.0,
            "message": "Usable capacity must be between 50% and 100%"
        },
        "degradation_rate_annual": {
            "min": 0.0,
            "max": 0.2,
            "message": "Annual degradation rate must be between 0% and 20%"
        },
        "replacement_threshold": {
            "min": 0.5,
            "max": 0.9,
            "message": "Replacement threshold must be between 50% and 90%"
        },
        "fuel_consumption_l_per_100km": {
            "min": 1.0,
            "max": 100.0,
            "message": "Fuel consumption must be between 1 and 100 L/100km"
        },
        "fuel_price_aud_per_litre": {
            "min": 0.5,
            "max": 10.0,
            "message": "Fuel price must be between $0.50 and $10.00 per litre"
        },
        "base_rate": {
            "min": 0.1,
            "max": 5.0,
            "message": "Energy consumption must be between 0.1 and 5.0 kWh/km"
        },
        "maintenance_cost_aud_per_km": {
            "min": 0.0,
            "max": 5.0,
            "message": "Maintenance cost must be between $0 and $5 per km"
        }
    }
    
    # Check if parameter has specific validation rules
    if param_name in validation_rules:
        rule = validation_rules[param_name]
        
        # Numeric validation
        if isinstance(value, (int, float)):
            if "min" in rule and value < rule["min"]:
                return {"valid": False, "message": rule["message"]}
            if "max" in rule and value > rule["max"]:
                return {"valid": False, "message": rule["message"]}
            
        # String validation
        elif isinstance(value, str):
            if "required" in rule and rule["required"] and not value.strip():
                return {"valid": False, "message": "This field is required"}
            if "max_length" in rule and len(value) > rule["max_length"]:
                return {"valid": False, "message": f"Maximum length is {rule['max_length']} characters"}
            
        # List validation
        elif isinstance(value, list) and "options" in rule:
            if value not in rule["options"]:
                return {"valid": False, "message": f"Value must be one of: {', '.join(rule['options'])}"}
    
    # Default to valid if no specific rules or all rules pass
    return {"valid": True, "message": ""}


def create_validated_input(
    label: str, 
    key: str, 
    input_type: str = "number",
    default: Optional[Any] = None,
    help_text: Optional[str] = None,
    **input_args
) -> Any:
    """
    Create an input with validation
    
    Args:
        label: Input label
        key: Session state key
        input_type: Input type (number, text, checkbox, select)
        default: Default value
        help_text: Help text
        **input_args: Additional input arguments
    
    Returns:
        Input value
    """
    import streamlit as st
    from utils.helpers import get_safe_state_value, set_safe_state_value
    
    # Get current value
    current_value = get_safe_state_value(key, default)
    
    # Create appropriate input based on type
    if input_type == "number":
        value = st.number_input(
            label=label,
            value=float(current_value) if current_value is not None else 0.0,
            help=help_text,
            **input_args
        )
    elif input_type == "text":
        value = st.text_input(
            label=label,
            value=current_value if current_value is not None else "",
            help=help_text,
            **input_args
        )
    elif input_type == "checkbox":
        value = st.checkbox(
            label=label,
            value=bool(current_value) if current_value is not None else False,
            help=help_text,
            **input_args
        )
    elif input_type == "select":
        options = input_args.pop("options", [])
        index = 0
        if current_value in options:
            index = options.index(current_value)
        value = st.selectbox(
            label=label,
            options=options,
            index=index,
            help=help_text,
            **input_args
        )
    elif input_type == "range_slider":
        # Handle the case where value is a tuple for range sliders
        if not isinstance(current_value, tuple):
            # If not a tuple, create a default range
            min_val = float(input_args.get('min_value', 0))
            max_val = float(input_args.get('max_value', 1))
            step_val = float(input_args.get('step', 0.1))
            # Create a default range that spans 10% of the available range
            range_span = (max_val - min_val) * 0.1
            current_value = (min_val, min_val + range_span)
        
        value = st.slider(
            label=label,
            value=current_value,
            min_value=float(input_args.get('min_value', 0)),
            max_value=float(input_args.get('max_value', 1)),
            step=float(input_args.get('step', 0.1)),
            help=help_text,
            format=input_args.get('format', '%.2f')
        )
    elif input_type == "slider":
        # Handle the case where value could be a list for range sliders
        if isinstance(current_value, list) or (isinstance(input_args.get("value"), list)):
            # For range sliders (if value is a list), ensure min_value and max_value are also lists
            slider_args = input_args.copy()
            
            # If current_value is a list, make sure min_value and max_value are lists too
            if isinstance(current_value, list) and len(current_value) == 2:
                # Ensure min_value is a list if value is a list
                if not isinstance(slider_args.get("min_value"), list):
                    min_val = slider_args.get("min_value", 0)
                    slider_args["min_value"] = [min_val, min_val]
                
                # Ensure max_value is a list if value is a list
                if not isinstance(slider_args.get("max_value"), list):
                    max_val = slider_args.get("max_value", 100)
                    slider_args["max_value"] = [max_val, max_val]
                
                # Ensure current_value elements are within min_value and max_value bounds
                min_vals = slider_args.get("min_value", [0, 0])
                max_vals = slider_args.get("max_value", [100, 100])
                step = float(slider_args.get("step", 1))
                
                # Apply constraints to each element of the current_value list
                for i in range(len(current_value)):
                    if i < len(min_vals) and i < len(max_vals):
                        # Ensure value is within bounds
                        current_value[i] = max(min_vals[i], min(max_vals[i], float(current_value[i])))
                        
                        # Adjust to nearest valid step if needed
                        if step > 0:
                            # Calculate steps from minimum
                            steps_from_min = round((current_value[i] - min_vals[i]) / step)
                            # Recalculate value based on steps
                            current_value[i] = min_vals[i] + (steps_from_min * step)
                            # Ensure we don't exceed max_val due to rounding
                            current_value[i] = min(current_value[i], max_vals[i])
                
                # Make sure first value <= second value for range sliders
                if len(current_value) >= 2 and current_value[0] > current_value[1]:
                    # Swap values if first is greater than second
                    current_value[0], current_value[1] = current_value[1], current_value[0]
            
            value = st.slider(
                label=label,
                value=current_value if current_value is not None else slider_args.get("value", 0.0),
                help=help_text,
                **slider_args
            )
        else:
            # Special case handling for analysis_period_years or any list value when the UI expects a scalar
            if isinstance(current_value, list):
                # For analysis_period_years specifically, or any key containing 'analysis_period'
                if "analysis_period" in key:
                    # Take the middle value if it's a list from sensitivity analysis
                    middle_index = len(current_value) // 2
                    current_value = current_value[middle_index]
                # For any other list value that needs to be converted to a scalar
                else:
                    # Try to extract a single value from the list
                    if len(current_value) > 0:
                        current_value = current_value[0]
                    else:
                        current_value = 0.0
            
            # For single value sliders
            # Handle tuple values by converting to a single float value if needed
            if isinstance(current_value, tuple):
                # For tuples, use the first value
                slider_value = current_value[0] if len(current_value) > 0 else 0.0
            else:
                slider_value = current_value
            
            # Get min, max, and step values
            min_val = float(input_args.get('min_value', 0))
            max_val = float(input_args.get('max_value', 100))
            step_val = float(input_args.get('step', 1))
            
            # Ensure min_value is strictly less than max_value
            if min_val >= max_val:
                # Adjust max_val to be at least one step greater than min_val
                max_val = min_val + step_val
            
            # Ensure slider_value is within min and max bounds and aligns with step
            if slider_value is not None:
                # Ensure value is within bounds
                slider_value = max(min_val, min(max_val, float(slider_value)))
                
                # Adjust to nearest valid step if needed
                if step_val > 0:
                    # Calculate steps from minimum
                    steps_from_min = round((slider_value - min_val) / step_val)
                    # Recalculate value based on steps to ensure it aligns with step size
                    slider_value = min_val + (steps_from_min * step_val)
                    # Ensure we don't exceed max_val due to rounding
                    slider_value = min(slider_value, max_val)
            
            value = st.slider(
                label=label,
                value=float(slider_value) if slider_value is not None else min_val,
                min_value=min_val,
                max_value=max_val,
                step=step_val,
                help=help_text,
                key=f"slider_{key}_{random.randint(10000, 99999)}"
            )
    else:
        raise ValueError(f"Unknown input type: {input_type}")
    
    # Validate the value
    validation_result = validate_parameter(key, value)
    
    # Show validation message if invalid
    if not validation_result["valid"]:
        st.error(validation_result["message"])
    else:
        # Update session state with valid value
        set_safe_state_value(key, value)
    
    return value, validation_result 


def validate_input(field_name: str, value: Any, param_type: str) -> Dict[str, Any]:
    """
    Validate a single input field based on field name and parameter type.
    
    Args:
        field_name: Name of the field to validate
        value: Value to validate
        param_type: Parameter type (vehicle, operational, economic)
        
    Returns:
        Dictionary with validation result and message
    """
    result = {
        "valid": True,
        "message": ""
    }
    
    # Field-specific validation based on parameter type
    if param_type == "vehicle":
        # Vehicle parameter validation
        if field_name == "purchase_price":
            if value is None or value <= 0:
                result["valid"] = False
                result["message"] = "Purchase price must be greater than zero"
        elif field_name == "range_km":
            if value is None or value <= 0:
                result["valid"] = False
                result["message"] = "Range must be greater than zero"
        elif field_name == "max_payload_tonnes":
            if value is None or value <= 0:
                result["valid"] = False
                result["message"] = "Maximum payload must be greater than zero"
        elif field_name == "capacity_kwh" and param_type == "battery":
            if value is None or value <= 0:
                result["valid"] = False
                result["message"] = "Battery capacity must be greater than zero"
                
    elif param_type == "operational":
        # Operational parameter validation
        if field_name == "annual_distance_km":
            if value is None or value <= 0:
                result["valid"] = False
                result["message"] = "Annual distance must be greater than zero"
        elif field_name == "operating_days_per_year":
            if value is None or value <= 0 or value > 365:
                result["valid"] = False
                result["message"] = "Operating days must be between 1 and 365"
        elif field_name == "vehicle_life_years":
            if value is None or value <= 0:
                result["valid"] = False
                result["message"] = "Vehicle life must be greater than zero"
                
    elif param_type == "economic":
        # Economic parameter validation
        if field_name == "discount_rate_real":
            if value is None or value < 0 or value > 0.5:
                result["valid"] = False
                result["message"] = "Discount rate must be between 0 and 50%"
        elif field_name == "inflation_rate":
            if value is None or value < 0 or value > 0.5:
                result["valid"] = False
                result["message"] = "Inflation rate must be between 0 and 50%"
        elif field_name == "analysis_period_years":
            if value is None or value <= 0:
                result["valid"] = False
                result["message"] = "Analysis period must be greater than zero"
                
    # Generic validation for all types
    if field_name.endswith("_price") and (value is None or value < 0):
        result["valid"] = False
        result["message"] = "Price must be non-negative"
        
    return result


def render_validation_feedback(validation_result: Dict[str, Any]) -> str:
    """
    Render validation feedback as HTML.
    
    Args:
        validation_result: Validation result dictionary with 'valid' and 'message' keys
        
    Returns:
        HTML string with validation feedback
    """
    if not validation_result["valid"]:
        return f"""
        <div class="validation-error">
            <span class="error-icon">⚠️</span>
            <span class="error-message">{validation_result["message"]}</span>
        </div>
        """
    return ""


# Mock implementation for test environments
def mock_input_field(label: str, value: Any, field_type: str = "text") -> str:
    """
    Create a mock HTML input field for testing.
    
    Args:
        label: Field label
        value: Field value
        field_type: Input type
        
    Returns:
        HTML string
    """
    return f"""
    <div class="form-field">
        <label>{label}</label>
        <input type="{field_type}" value="{value}">
    </div>
    """ 