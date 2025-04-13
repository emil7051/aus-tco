"""
Results UI Utilities

UI-specific utilities and constants for TCO results visualization.
This module provides helper functions, data mappings, and formatting tools
that support the visualization of TCO calculation results in the UI layer.
"""

from typing import Dict, List, Any, Optional, Tuple, Union, Callable

from tco_model.models import TCOOutput
from tco_model.terminology import (
    UI_COMPONENT_MAPPING, 
    UI_COMPONENT_KEYS, 
    UI_COMPONENT_LABELS,
    get_component_value as get_model_component_value
)
from utils.helpers import format_currency, format_percentage

# Common cost component mappings
# These represent the standardized cost categories shown across all visualizations
COMPONENT_KEYS = [
    "acquisition",
    "energy", 
    "maintenance",
    "infrastructure",
    "battery_replacement",
    "insurance_registration",  # Combined from insurance + registration
    "taxes_levies",            # Combined from carbon_tax + other_taxes
    "residual_value"
]

# Display labels for each cost component
COMPONENT_LABELS = {
    "acquisition": "Acquisition Costs",
    "energy": "Energy Costs",
    "maintenance": "Maintenance & Repair",
    "infrastructure": "Infrastructure",
    "battery_replacement": "Battery Replacement",
    "insurance_registration": "Insurance & Registration",
    "taxes_levies": "Taxes & Levies",
    "residual_value": "Residual Value"
}

def get_component_value(result: TCOOutput, component: str) -> float:
    """
    Get component NPV value from a result using the standardized access pattern.
    
    Args:
        result: TCO result object containing the cost data
        component: Component key to access
        
    Returns:
        float: The component value in AUD
        
    Example:
        >>> energy_cost = get_component_value(result, "energy")
        >>> insurance_reg = get_component_value(result, "insurance_registration")
    """
    if not result or not result.npv_costs:
        return 0.0
    
    # Use the standardized access function from terminology
    return get_model_component_value(result.npv_costs, component)


def get_annual_component_value(result: TCOOutput, component: str, year: int) -> float:
    """
    Get component value for a specific year using the standardized access pattern.
    
    Args:
        result: TCO result object containing the annual costs data
        component: Component key to access
        year: Year index (0-based)
        
    Returns:
        float: The component value for the specified year in AUD
        
    Example:
        >>> # Get energy costs for year 3
        >>> energy_cost_year_3 = get_annual_component_value(result, "energy", 3)
    """
    if not result or not result.annual_costs or year >= len(result.annual_costs):
        return 0.0
    
    # Use the standardized access function from terminology
    return get_model_component_value(result.annual_costs[year], component)


def get_component_color(component: str) -> str:
    """
    Get the standard color for a component.
    
    Args:
        component: Component key
        
    Returns:
        str: Color hex code for the component
    """
    # Constant for default color
    DEFAULT_COLOR = "#333333"  # Default gray
    
    if component in UI_COMPONENT_MAPPING:
        return UI_COMPONENT_MAPPING[component].get("color", DEFAULT_COLOR)
    return DEFAULT_COLOR


def get_component_display_order(component: str) -> int:
    """
    Get the standard display order for a component.
    
    Args:
        component: Component key
        
    Returns:
        int: Display order value (1-based)
    """
    # Constant for default display order
    DEFAULT_DISPLAY_ORDER = 999  # Default to end
    
    if component in UI_COMPONENT_MAPPING:
        return UI_COMPONENT_MAPPING[component].get("display_order", DEFAULT_DISPLAY_ORDER)
    return DEFAULT_DISPLAY_ORDER


def get_chart_settings(default_settings: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Get chart settings from session state or initialize with defaults.
    
    Maintains chart configuration consistency across different visualizations
    by storing settings in the Streamlit session state.
    
    Args:
        default_settings: Default settings to use if not already in session state
        
    Returns:
        Dict[str, Any]: Dictionary of chart settings
    
    Example:
        >>> settings = get_chart_settings({"chart_height": 600, "show_grid": True})
        >>> chart_height = settings["chart_height"]  # 600
    """
    import streamlit as st
    
    if default_settings is None:
        default_settings = {
            "show_breakeven_point": True,
            "chart_height": 500,
            "color_scheme": "default",
            "show_grid": True,
            "show_annotations": True,
            "components_to_show": COMPONENT_KEYS.copy()
        }
    
    if "chart_settings" not in st.session_state:
        st.session_state.chart_settings = default_settings
    
    return st.session_state.chart_settings


def apply_chart_theme(fig: Any, height: Optional[int] = None, title: Optional[str] = None) -> Any:
    """
    Apply consistent theme to a plotly figure.
    
    Ensures visual consistency across all charts by applying standardized
    styling, including colors, fonts, margins, and other visual properties.
    
    Args:
        fig: Plotly figure object to style
        height: Chart height in pixels (overrides settings if provided)
        title: Chart title (if provided)
        
    Returns:
        Any: Styled plotly figure
    
    Example:
        >>> fig = px.bar(data, x="year", y="value")
        >>> fig = apply_chart_theme(fig, height=400, title="Annual Costs")
    """
    import streamlit as st
    
    settings = get_chart_settings()
    
    # Base styling
    fig.update_layout(
        height=height or settings["chart_height"],
        grid=dict(visible=settings["show_grid"]),
        font=dict(family="Arial, sans-serif"),
        plot_bgcolor="white",
        margin=dict(l=50, r=50, t=50, b=50),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    # Add title if provided
    if title:
        fig.update_layout(title=title)
    
    # Style axes
    fig.update_xaxes(showgrid=settings["show_grid"], zeroline=True, zerolinewidth=1, zerolinecolor="lightgray")
    fig.update_yaxes(showgrid=settings["show_grid"], zeroline=True, zerolinewidth=1, zerolinecolor="lightgray")
    
    return fig


def validate_tco_results(results: Dict[str, TCOOutput]) -> bool:
    """
    Validate that TCO results contain the required data structure.
    
    Checks if results dictionary has the expected structure and contains
    valid TCO result objects with the necessary attributes for visualization.
    
    Args:
        results: Dictionary of TCO results, with keys like "vehicle_1" and "vehicle_2"
        
    Returns:
        bool: True if results are valid and can be visualized, False otherwise
    
    Example:
        >>> if validate_tco_results(results):
        >>>     render_charts(results, comparison)
        >>> else:
        >>>     st.error("Invalid TCO results")
    """
    if not results:
        return False
    
    for vehicle_key in ["vehicle_1", "vehicle_2"]:
        if vehicle_key not in results:
            return False
            
        result = results[vehicle_key]
        
        # Check for required attributes
        if not hasattr(result, "annual_costs") or not result.annual_costs:
            return False
            
        if not hasattr(result, "npv_costs") or not result.npv_costs:
            return False
            
        if not hasattr(result, "vehicle_name") or not result.vehicle_name:
            return False
    
    return True