"""
Results UI Utilities

UI-specific utilities and constants for TCO results visualization.
"""

from typing import Dict, List, Any, Optional

from tco_model.models import TCOOutput
from utils.helpers import format_currency, format_percentage

# Common cost component mappings
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

# Functions to access values considering data structure differences
def get_component_value(result: TCOOutput, component: str) -> float:
    """
    Get component NPV value from a result using the right structure
    
    Args:
        result: TCO result object
        component: Component key to access
        
    Returns:
        float: The component value
    """
    if not result or not result.npv_costs:
        return 0.0
        
    try:
        if component == "insurance_registration":
            return result.npv_costs.insurance + result.npv_costs.registration
        elif component == "taxes_levies":
            return result.npv_costs.carbon_tax + result.npv_costs.other_taxes
        else:
            return getattr(result.npv_costs, component, 0.0)
    except (AttributeError, TypeError):
        return 0.0


def get_annual_component_value(result: TCOOutput, component: str, year: int) -> float:
    """
    Get component value for a specific year
    
    Args:
        result: TCO result object
        component: Component key to access
        year: Year index
        
    Returns:
        float: The component value for the specified year
    """
    if not result or not result.annual_costs or year >= len(result.annual_costs):
        return 0.0
        
    try:
        if component == "insurance_registration":
            return result.annual_costs[year].insurance + result.annual_costs[year].registration
        elif component == "taxes_levies":
            return result.annual_costs[year].carbon_tax + result.annual_costs[year].other_taxes
        else:
            return getattr(result.annual_costs[year], component, 0.0)
    except (AttributeError, TypeError, IndexError):
        return 0.0


def get_chart_settings(default_settings: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Get chart settings from session state or initialize with defaults
    
    Args:
        default_settings: Default settings to use if not in session state
        
    Returns:
        Dictionary of chart settings
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


def apply_chart_theme(fig, height: int = None, title: Optional[str] = None):
    """
    Apply consistent theme to a plotly figure
    
    Args:
        fig: Plotly figure object to style
        height: Chart height in pixels (overrides settings if provided)
        title: Chart title (if provided)
        
    Returns:
        Styled plotly figure
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
    Validate that TCO results contain the required data structure
    
    Args:
        results: Dictionary of TCO results
        
    Returns:
        bool: True if results are valid, False otherwise
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