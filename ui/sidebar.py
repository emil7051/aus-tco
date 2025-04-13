"""
Sidebar Module

This module contains functions to render and manage the sidebar components
of the TCO Modeller application. The sidebar provides application-wide controls
and settings that affect the entire UI experience.
"""

from typing import Dict, Any, Optional, List, Callable
import streamlit as st

from tco_model.models import VehicleType
from utils.helpers import load_default_scenario, find_available_vehicle_configs


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
        
        # Vehicle configuration selection section
        render_vehicle_config_selector()
        
        # Add a separator for visual clarity
        st.markdown("---")
        
        # Display mode and settings
        render_display_settings()
        
        # Bottom section for developer tools
        with st.expander("Developer Tools"):
            render_developer_tools()


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
        default_config_name = f"default_{'bet' if current_type == VehicleType.BATTERY_ELECTRIC else 'ice'}"
        
        # Display a selectbox for available configurations
        with col2:
            selected_config = st.selectbox(
                f"", 
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