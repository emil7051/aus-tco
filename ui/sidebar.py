"""
Sidebar Module

This module contains functions to render and manage the sidebar components
of the TCO Modeller application. The sidebar provides application-wide controls
and settings that affect the entire UI experience.
"""

from typing import Dict, Any, Optional, List, Callable
import streamlit as st
import datetime

from tco_model.schemas import VehicleType
from utils.helpers import load_default_scenario, find_available_vehicle_configs, format_currency, format_percentage
from utils.ui_terminology import get_formatted_label, get_vehicle_type_color
from utils.ui_components import UIComponentFactory
from utils.css_loader import get_available_themes, load_css
from utils.navigation_state import get_current_step, set_step
from tco_model.terminology import UI_COMPONENT_KEYS, UI_COMPONENT_LABELS
from tco_model.models import TCOOutput, ComparisonResult
from ui.results.utils import get_component_value


def render_sidebar() -> None:
    """
    Render the application sidebar with global controls and settings.
    
    The sidebar includes application information, vehicle configuration
    selection options, display settings, and developer tools.
    
    This function has no parameters and returns nothing, as it performs
    direct Streamlit UI rendering.
    """
    with st.sidebar:
        # Application information and title
        st.title("TCO Modeller")
        st.markdown("### Settings")
        
        # Add a separator for visual clarity
        st.markdown("---")
        
        # Navigation section
        render_navigation()
        
        # Add a separator for visual clarity
        st.markdown("---")
        
        # Vehicle configuration selection section
        render_vehicle_config_selector()
        
        # Add a separator for visual clarity
        st.markdown("---")
        
        # Display mode and settings
        render_display_settings()
        
        # Add a separator for visual clarity
        st.markdown("---")
        
        # Theme settings
        render_theme_selector()
        
        # Quick comparison tools
        render_quick_comparison_tools()
        
        # Bottom section for developer tools
        with st.expander("Developer Tools"):
            render_developer_tools()


def render_navigation() -> None:
    """
    Render navigation controls in the sidebar.
    
    Allows users to navigate between different sections of the application.
    """
    st.subheader("Navigation")
    
    # Current step
    current_step = get_current_step()
    
    # Create navigation buttons
    col1, col2 = st.columns(2)
    
    with col1:
        inputs_selected = current_step == "config"
        if st.button("Inputs", use_container_width=True, 
                    type="primary" if inputs_selected else "secondary"):
            set_step("config")
    
    with col2:
        results_selected = current_step == "results"
        if st.button("Results", use_container_width=True,
                    type="primary" if results_selected else "secondary",
                    disabled=not st.session_state.get("show_results", False)):
            set_step("results")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Note: parameter_comparison was likely intended to be a separate step
        # but isn't in APP_STEPS. Using config as the closest match.
        comparison_selected = False
        if st.button("Parameters", use_container_width=True,
                    type="primary" if comparison_selected else "secondary",
                    help="Compare parameters between vehicles"):
            set_step("config")
    
    with col2:
        guide_selected = current_step == "guide"
        if st.button("Guide", use_container_width=True,
                    type="primary" if guide_selected else "secondary"):
            set_step("guide")


def render_vehicle_config_selector() -> None:
    """
    Render the vehicle configuration selection UI in the sidebar.
    
    Allows users to select pre-configured vehicle setups for both
    vehicles being compared.
    """
    # Get available vehicle configurations
    available_configs = find_available_vehicle_configs()
    
    st.subheader("Vehicle Configurations")
    
    # Process selection for Vehicle 1
    _render_vehicle_selector(
        vehicle_number=1,
        available_configs=available_configs,
    )
    
    # Process selection for Vehicle 2
    _render_vehicle_selector(
        vehicle_number=2,
        available_configs=available_configs,
    )


def _render_vehicle_selector(
    vehicle_number: int, 
    available_configs: Dict[VehicleType, List[str]]
) -> None:
    """
    Render the selection UI for a single vehicle.
    
    This private helper function handles the UI and state management
    for selecting and loading a vehicle configuration.
    
    Args:
        vehicle_number: The vehicle number (1 or 2) being configured
        available_configs: Dictionary mapping vehicle types to available configurations
    """
    # Vehicle state key in session state
    state_key = f"vehicle_{vehicle_number}_input"
    
    # Get current vehicle type from session state
    current_vehicle = st.session_state.get(state_key)
    current_type = current_vehicle.vehicle.type if current_vehicle else VehicleType.DIESEL
    
    # Display selection boxes in a container for styling
    with st.container():
        # Create a column layout for the vehicle label and number
        col1, col2 = st.columns([1, 4])
        with col1:
            st.markdown(f"**V{vehicle_number}:**")
        
        # Get available configs for the current vehicle type
        type_configs = available_configs.get(current_type, [])
        
        # Get the selected config name (or default to the first one)
        # Handle both enum and string types
        if isinstance(current_type, VehicleType):
            default_config_name = f"default_{current_type.value}"
        else:
            # If it's already a string, use it directly
            default_config_name = f"default_{current_type}"
        
        # Display a selectbox for available configurations
        with col2:
            selected_config = st.selectbox(
                "Select configuration", 
                options=type_configs,
                index=type_configs.index(default_config_name) if default_config_name in type_configs else 0,
                key=f"config_select_{vehicle_number}",
                label_visibility="collapsed"
            )
        
        # If a configuration is selected, load it
        if selected_config:
            if f"last_config_{vehicle_number}" not in st.session_state:
                st.session_state[f"last_config_{vehicle_number}"] = selected_config
            
            # Only reload if the selection changed
            if st.session_state[f"last_config_{vehicle_number}"] != selected_config:
                st.session_state[f"last_config_{vehicle_number}"] = selected_config
                
                # Load the selected configuration
                selected_scenario = load_default_scenario(selected_config)
                st.session_state[state_key] = selected_scenario
                
                # Reset result display when configuration changes
                if "show_results" in st.session_state:
                    st.session_state.show_results = False
                
                # Rerun to update UI after state change
                st.rerun()


def render_display_settings() -> None:
    """
    Render display settings controls in the sidebar.
    
    These settings control how the TCO results are displayed,
    including chart options and visibility of components.
    """
    # Initialize chart settings in session state if not present
    if "chart_settings" not in st.session_state:
        st.session_state.chart_settings = {
            "show_breakeven_point": True,
            "chart_height": 500,
            "color_scheme": "default",
            "show_grid": True,
            "show_annotations": True,
        }
    
    # Settings for chart display
    st.subheader("Display Settings")
    
    # Toggle for breakeven point
    st.session_state.chart_settings["show_breakeven_point"] = st.toggle(
        "Show Breakeven Point", 
        value=st.session_state.chart_settings["show_breakeven_point"],
        key="toggle_breakeven"
    )
    
    # Toggle for grid lines
    st.session_state.chart_settings["show_grid"] = st.toggle(
        "Show Grid Lines", 
        value=st.session_state.chart_settings["show_grid"],
        key="toggle_grid"
    )
    
    # Toggle for annotations
    st.session_state.chart_settings["show_annotations"] = st.toggle(
        "Show Annotations", 
        value=st.session_state.chart_settings["show_annotations"],
        key="toggle_annotations"
    )
    
    # Slider for chart height
    st.session_state.chart_settings["chart_height"] = st.slider(
        "Chart Height", 
        min_value=300, 
        max_value=800, 
        value=st.session_state.chart_settings["chart_height"],
        step=50,
        key="slider_height"
    )


def render_theme_selector() -> None:
    """
    Render theme selection controls in the sidebar.
    
    Allows users to switch between different visual themes.
    """
    # Get available themes
    available_themes = get_available_themes()
    
    # Initialize theme in session state if not present
    if "ui_theme" not in st.session_state:
        st.session_state.ui_theme = "light"
    
    st.subheader("Theme")
    
    # Create theme selector
    col1, col2, col3 = st.columns(3)
    
    with col1:
        light_selected = st.session_state.ui_theme == "light"
        if st.button("Light", use_container_width=True, 
                    type="primary" if light_selected else "secondary"):
            st.session_state.ui_theme = "light"
            st.rerun()
    
    with col2:
        dark_selected = st.session_state.ui_theme == "dark"
        if st.button("Dark", use_container_width=True,
                    type="primary" if dark_selected else "secondary"):
            st.session_state.ui_theme = "dark"
            st.rerun()
    
    with col3:
        hc_selected = st.session_state.ui_theme == "high-contrast"
        if st.button("HC", use_container_width=True, 
                    type="primary" if hc_selected else "secondary",
                    help="High Contrast theme for accessibility"):
            st.session_state.ui_theme = "high-contrast"
            st.rerun()
    
    # Theme preview
    st.markdown(f"""
        <div class="theme-preview theme-{st.session_state.ui_theme}">
            <div class="preview-header">Theme Preview: {st.session_state.ui_theme.replace('-', ' ').title()}</div>
            <div class="preview-chart"></div>
            <div class="preview-text">Sample text</div>
        </div>
    """, unsafe_allow_html=True)


def render_developer_tools() -> None:
    """
    Render developer tools in the sidebar.
    
    These tools are primarily for development and debugging purposes,
    such as enabling debug mode and showing state information.
    """
    # Initialize debug mode in session state if not present
    if "debug_mode" not in st.session_state:
        st.session_state.debug_mode = False
    
    # Toggle for debug mode
    debug_mode = st.checkbox(
        "Debug Mode", 
        value=st.session_state.debug_mode,
        key="toggle_debug"
    )
    
    # Update debug mode in session state if changed
    if debug_mode != st.session_state.debug_mode:
        st.session_state.debug_mode = debug_mode
        
        # Rerun to update UI based on new debug mode setting
        st.rerun()


def render_quick_comparison_tools():
    """
    Create quick comparison tools for the sidebar
    """
    # Only show if results are available
    if "results" not in st.session_state or not st.session_state.results:
        return
    
    st.markdown("## Quick Analysis")
    
    # Get results
    results = st.session_state.results
    comparison = st.session_state.get("comparison")
    
    if not results or not comparison:
        st.info("Calculate TCO to enable quick analysis tools")
        return
    
    # Create summary snapshot
    result1 = results["vehicle_1"]
    result2 = results["vehicle_2"]
    
    # Summary card
    st.markdown(f"""
    <div class="quick-summary-card">
        <div class="card-header">TCO Snapshot</div>
        
        <div class="vehicle-comparison">
            <div class="vehicle-item">
                <div class="vehicle-name">{result1.vehicle_name}</div>
                <div class="vehicle-tco">{format_currency(result1.total_tco)}</div>
                <div class="vehicle-lcod">{format_currency(result1.lcod)}/km</div>
            </div>
            
            <div class="comparison-indicator">
                <div class="comparison-value">
                    {format_percentage(abs(comparison.tco_percentage))} 
                    {"cheaper" if comparison.cheaper_option == 1 else "more expensive"}
                </div>
                <div class="comparison-arrow">
                    {"↓" if comparison.cheaper_option == 1 else "↑"}
                </div>
            </div>
            
            <div class="vehicle-item">
                <div class="vehicle-name">{result2.vehicle_name}</div>
                <div class="vehicle-tco">{format_currency(result2.total_tco)}</div>
                <div class="vehicle-lcod">{format_currency(result2.lcod)}/km</div>
            </div>
        </div>
        
        <div class="key-insight">
            {generate_key_insight(comparison)}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Key differences analysis
    st.markdown("### Key Differences")
    
    # Get top 3 component differences
    top_diffs = get_top_component_differences(comparison, results, n=3)
    
    for comp in top_diffs:
        diff_value = get_component_value(result1, comp) - get_component_value(result2, comp)
        reference_value = abs(get_component_value(result2, comp)) if get_component_value(result2, comp) != 0 else 1.0
        diff_pct = diff_value / reference_value * 100
        
        st.markdown(f"""
        <div class="key-difference-item">
            <div class="diff-component">{UI_COMPONENT_LABELS[comp]}</div>
            <div class="diff-value">{format_currency(abs(diff_value))}</div>
            <div class="diff-percentage {"higher" if diff_pct > 0 else "lower"}">
                {format_percentage(abs(diff_pct))} {"higher" if diff_pct > 0 else "lower"}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Quick sensitivity check
    st.markdown("### Quick Sensitivity Check")
    
    # Create sensitivity slider
    sensitivity_param = st.selectbox(
        "Adjust parameter",
        options=["Diesel Price", "Electricity Price", "Annual Distance", "Analysis Period"],
        key="quick_sensitivity_param"
    )
    
    # Add parameter-specific slider
    if sensitivity_param == "Diesel Price":
        sensitivity_value = st.slider(
            "Adjustment",
            min_value=-50,
            max_value=50,
            value=0,
            step=5,
            key="sensitivity_diesel_price_pct",
            format="%d%%"
        )
    elif sensitivity_param == "Electricity Price":
        sensitivity_value = st.slider(
            "Adjustment",
            min_value=-50,
            max_value=50,
            value=0,
            step=5,
            key="sensitivity_electricity_price_pct",
            format="%d%%"
        )
    elif sensitivity_param == "Annual Distance":
        sensitivity_value = st.slider(
            "Adjustment",
            min_value=-50,
            max_value=50,
            value=0,
            step=5,
            key="sensitivity_annual_distance_pct",
            format="%d%%"
        )
    elif sensitivity_param == "Analysis Period":
        sensitivity_value = st.slider(
            "Adjustment",
            min_value=-5,
            max_value=5,
            value=0,
            step=1,
            key="sensitivity_analysis_period_years",
            format="%d years"
        )
    
    # Recalculate button
    st.button(
        "Check Impact",
        key="quick_sensitivity_check",
        on_click=run_quick_sensitivity_analysis,
        args=(sensitivity_param, sensitivity_value)
    )


def run_quick_sensitivity_analysis(parameter: str, value: float):
    """
    Run a quick sensitivity analysis based on parameter adjustment
    
    Args:
        parameter: The parameter to adjust
        value: The adjustment value
    """
    # This function would be implemented to recalculate TCO with adjusted parameters
    # For now, just show a message
    st.session_state["sensitivity_message"] = f"Impact of {parameter} changed by {value}"


def generate_key_insight(comparison: ComparisonResult) -> str:
    """
    Generate a key insight based on comparison results
    
    Args:
        comparison: The comparison result
        
    Returns:
        str: HTML-formatted key insight
    """
    # Generate a simple insight about payback period if available
    if hasattr(comparison, "payback_years") and comparison.payback_years:
        return f"Investment pays back in <strong>{comparison.payback_years:.1f} years</strong>"
    
    # Or about cost per km
    if comparison.cheaper_option == 1:
        return f"<strong>{abs(comparison.lcod_difference_percentage):.1f}%</strong> lower cost per km"
    else:
        return f"Higher upfront cost, <strong>{abs(comparison.tco_percentage):.1f}%</strong> higher TCO"


def get_top_component_differences(comparison: ComparisonResult, results: Dict[str, TCOOutput], n: int = 3) -> List[str]:
    """
    Get the top N components with the largest differences
    
    Args:
        comparison: The comparison result
        results: Dictionary of TCO results
        n: Number of components to return
        
    Returns:
        List[str]: List of component keys
    """
    # Check if comparison has component differences
    if not hasattr(comparison, "component_differences"):
        # Calculate differences manually
        result1 = results["vehicle_1"]
        result2 = results["vehicle_2"]
        
        differences = {}
        for comp in UI_COMPONENT_KEYS:
            v1_value = get_component_value(result1, comp)
            v2_value = get_component_value(result2, comp)
            differences[comp] = abs(v1_value - v2_value)
    else:
        # Use existing component differences
        differences = {comp: abs(diff) for comp, diff in comparison.component_differences.items()}
    
    # Sort components by absolute difference and return top N
    sorted_components = sorted(UI_COMPONENT_KEYS, key=lambda c: differences.get(c, 0), reverse=True)
    return sorted_components[:n]


def render_sidebar_footer():
    """
    Render the footer section of the sidebar.
    """
    st.markdown("---")
    
    # Add theme selector
    selected_theme = st.session_state.get("ui_theme", "light")
    theme_options = ["light", "dark", "australian"]
    
    st.selectbox(
        "Theme",
        options=theme_options,
        index=theme_options.index(selected_theme),
        key="theme_selector",
        on_change=update_theme
    )
    
    # Add debug mode toggle if in development
    if st.session_state.get("environment", "production") == "development":
        st.checkbox(
            "Debug Mode",
            value=st.session_state.get("debug_mode", False),
            key="debug_mode"
        )
    
    # Add version info
    st.markdown(
        f"""<div class="sidebar-footer">
            <p>Version 1.0.0<br>
            Last updated: {datetime.datetime.now().strftime("%Y-%m-%d")}</p>
        </div>""",
        unsafe_allow_html=True
    )


def update_theme():
    """
    Update the application theme based on selection.
    """
    # This would refresh CSS with the new theme
    # In a real implementation, this would trigger a page reload
    load_css(st.session_state.theme_selector) 