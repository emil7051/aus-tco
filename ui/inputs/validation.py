"""
Validation System for Input Parameters

This module provides a comprehensive validation system for input parameters, ensuring that
user inputs are valid within defined constraints and providing appropriate feedback.
"""

from typing import Dict, Any, Optional, Callable, List, Union

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
    elif input_type == "slider":
        value = st.slider(
            label=label,
            value=float(current_value) if current_value is not None else 0.0,
            help=help_text,
            **input_args
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