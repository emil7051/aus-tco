"""
UI Terminology Utilities

This module provides utilities for consistent terminology usage in the UI layer,
drawing from the canonical definitions in tco_model/terminology.py. It includes
functions for formatting, labelling, and accessing standard terminology.
"""

from typing import Dict, List, Any, Optional, Union, Tuple
from tco_model.terminology import (
    UI_COMPONENT_LABELS,
    UI_COMPONENT_MAPPING,
    VEHICLE_TYPE_LABELS,
    VEHICLE_CATEGORY_LABELS,
    COST_COMPONENTS,
    UI_COMPONENT_KEYS,
    get_ui_component_label,
    get_component_description,
)
from tco_model.schemas import VehicleType


def get_formatted_label(key: str, include_units: bool = False, 
                       include_tooltip: bool = False) -> Union[str, Tuple[str, str]]:
    """
    Get a consistently formatted label for a UI element with optional units and tooltip.
    
    Args:
        key: The terminology key
        include_units: Whether to include units in the label
        include_tooltip: Whether to include a tooltip 
        
    Returns:
        The formatted label string, or a tuple of (label, tooltip) if include_tooltip is True
    """
    # Get the base label
    if key in UI_COMPONENT_LABELS:
        label = UI_COMPONENT_LABELS[key]
    elif key in VEHICLE_TYPE_LABELS:
        label = VEHICLE_TYPE_LABELS[key]
    elif key in VEHICLE_CATEGORY_LABELS:
        label = VEHICLE_CATEGORY_LABELS[key]
    else:
        # Use key as fallback with title casing and underscores replaced
        label = key.replace('_', ' ').title()
    
    # Add units if requested and available
    if include_units and key in UI_COMPONENT_MAPPING:
        units = UI_COMPONENT_MAPPING[key].get('units', '')
        if units:
            label = f"{label} ({units})"
    
    # Generate tooltip if requested
    if include_tooltip:
        tooltip = get_component_description(key) if key in UI_COMPONENT_KEYS else ''
        return label, tooltip
    
    return label


def get_component_label(component_key: str) -> str:
    """
    Get the label for a cost component.
    
    Args:
        component_key: The component key
        
    Returns:
        The formatted label for the component
    """
    if component_key in UI_COMPONENT_LABELS:
        return UI_COMPONENT_LABELS[component_key]
    return component_key.replace('_', ' ').title()


def get_vehicle_type_label(vehicle_type: Union[str, VehicleType]) -> str:
    """
    Get a formatted label for a vehicle type with abbreviation.
    
    Args:
        vehicle_type: The vehicle type (string or enum)
        
    Returns:
        Formatted vehicle type label with abbreviation
    """
    # Convert enum to value if needed
    if isinstance(vehicle_type, VehicleType):
        vehicle_type = vehicle_type.value
        
    # Map of vehicle types to labels with abbreviations
    labels = {
        VehicleType.BATTERY_ELECTRIC.value: "Battery Electric Truck (BET)",
        VehicleType.DIESEL.value: "Diesel Truck (ICE)",
        "hydrogen_fuel_cell": "Hydrogen Fuel Cell (FCEV)",
        "hybrid": "Hybrid Electric Truck (HET)"
    }
    
    return labels.get(vehicle_type, vehicle_type.replace('_', ' ').title())


def format_currency(value: float, include_cents: bool = True) -> str:
    """
    Format a value as Australian currency.
    
    Args:
        value: The value to format
        include_cents: Whether to include cents in the formatting
        
    Returns:
        Formatted currency string
    """
    if include_cents:
        return f"${value:,.2f}"
    return f"${value:,.0f}"


def format_percentage(value: float, include_decimal: bool = True) -> str:
    """
    Format a value as a percentage.
    
    Args:
        value: The value to format (e.g., 0.15 for 15%)
        include_decimal: Whether to include decimal places
        
    Returns:
        Formatted percentage string
    """
    if include_decimal:
        return f"{value * 100:.1f}%"
    return f"{int(value * 100)}%"


def format_number_with_unit(value: float, unit: str, decimal_places: int = 1) -> str:
    """
    Format a number with its unit.
    
    Args:
        value: The value to format
        unit: The unit to append
        decimal_places: Number of decimal places to include
        
    Returns:
        Formatted number with unit
    """
    format_str = f"{{:.{decimal_places}f}} {unit}"
    return format_str.format(value)


def create_impact_indicator(key: str) -> dict:
    """
    Create an impact indicator configuration for a parameter.
    
    Args:
        key: The parameter key
        
    Returns:
        A dictionary with impact level, icon, and tooltip
    """
    # Map component keys to impact levels
    impact_mapping = {
        # High impact components
        "acquisition": "high",
        "energy": "high",
        "battery_replacement": "high",
        
        # Medium impact components
        "maintenance": "medium",
        "infrastructure": "medium",
        "residual_value": "medium",
        
        # Low impact components
        "insurance_registration": "low",
        "taxes_levies": "low",
    }
    
    # Map operation parameters to impact levels
    operation_impact_mapping = {
        "annual_distance_km": "high",
        "analysis_period_years": "high",
        "discount_rate_real": "medium",
        "load_factor": "medium",
        "vehicle_life_years": "medium",
        "operating_days_per_year": "low",
    }
    
    # Combine mappings
    all_impacts = {**impact_mapping, **operation_impact_mapping}
    
    # Get impact level with fallback to medium
    impact_level = all_impacts.get(key, "medium")
    
    # Define icons and tooltips for each impact level
    impact_indicators = {
        "high": {
            "icon": "🔴",
            "tooltip": "High impact on TCO results",
            "class": "high"
        },
        "medium": {
            "icon": "🟠", 
            "tooltip": "Medium impact on TCO results",
            "class": "medium"
        },
        "low": {
            "icon": "🟢",
            "tooltip": "Low impact on TCO results",
            "class": "low"
        }
    }
    
    return impact_indicators[impact_level]


def get_component_color(component_key: str) -> str:
    """
    Get the standard color for a cost component.
    
    Args:
        component_key: The component key
        
    Returns:
        The hex color code for the component
    """
    if component_key in UI_COMPONENT_MAPPING:
        return UI_COMPONENT_MAPPING[component_key].get('color', '#7f7f7f')
    return '#7f7f7f'  # Default gray


def get_vehicle_type_color(vehicle_type: Union[str, VehicleType]) -> str:
    """
    Get the standard color for a vehicle type.
    
    Args:
        vehicle_type: The vehicle type (string or enum)
        
    Returns:
        The hex color code for the vehicle type
    """
    # Convert enum to value if needed
    if isinstance(vehicle_type, VehicleType):
        vehicle_type = vehicle_type.value
        
    vehicle_colors = {
        VehicleType.BATTERY_ELECTRIC.value: "#26A69A",  # Teal
        VehicleType.DIESEL.value: "#FB8C00",            # Orange
    }
    return vehicle_colors.get(vehicle_type, "#7f7f7f")


def get_australian_spelling(term: str) -> str:
    """
    Convert a term to Australian English spelling.
    
    Args:
        term: The term to convert
        
    Returns:
        The term with Australian English spelling
    """
    # Common US to Australian English spelling conversions
    spelling_map = {
        "color": "colour",
        "center": "centre", 
        "kilometer": "kilometre",
        "liter": "litre",
        "modeling": "modelling",
        "modeled": "modelled",
        "license": "licence",
        "analyze": "analyse",
        "analyzed": "analysed",
        "analyzing": "analysing",
        "customize": "customise",
        "customized": "customised",
        "customizing": "customising",
    }
    
    result = term
    
    # Apply each conversion
    for us_spelling, aus_spelling in spelling_map.items():
        # Case-insensitive replacement preserving case
        if us_spelling in result.lower():
            i = result.lower().find(us_spelling)
            orig_case = result[i:i+len(us_spelling)]
            if orig_case.isupper():
                replacement = aus_spelling.upper()
            elif orig_case[0].isupper():
                replacement = aus_spelling.capitalize()
            else:
                replacement = aus_spelling
                
            result = result.replace(orig_case, replacement)
    
    return result 