"""
Progressive Disclosure UI

This module implements the progressive disclosure pattern,
showing UI components based on the current navigation step.
"""

import streamlit as st
from typing import Dict, Any, Optional

from utils.navigation_state import get_current_step, set_step
from ui.navigation_components import (
    render_step_navigation, 
    render_breadcrumb_navigation, 
    render_progress_indicator,
    render_section_header,
    render_subsection_header,
    render_expandable_section
)
from ui.config_management import render_config_management
from ui.inputs.vehicle import render_vehicle_inputs
from ui.inputs.operational import render_operational_inputs
from ui.inputs.economic import render_economic_inputs
from ui.inputs.financing import render_financing_inputs
from ui.results.display import display_results
from ui.guide import render_guide
from tco_model.schemas import VehicleType


def implement_progressive_disclosure(compact: bool = False, current_step: str = None):
    """
    Implement progressive disclosure based on current step.
    
    This function renders different UI components based on the
    current navigation step, creating a guided user experience.
    
    Args:
        compact: Whether to use compact layout for smaller screens
        current_step: Optional override for the current step
    """
    # Get current step, use override if provided
    if current_step is None:
        current_step = get_current_step()
    
    # Create a container for the navigation components
    with st.container():
        # Always show step navigation at the top
        render_step_navigation()
        
        # Show progress indicator 
        render_progress_indicator()
        
        # Show breadcrumb navigation
        render_breadcrumb_navigation()
    
    # Add spacing
    st.markdown("<div style='margin-top: 20px'></div>", unsafe_allow_html=True)
    
    # Render appropriate content for the current step
    if current_step == "config":
        render_configuration_step(compact)
        
    elif current_step == "results":
        render_results_step()
        
    elif current_step == "export":
        render_export_step()
        
    elif current_step == "guide":
        render_guide_step()
    elif current_step == "vehicle_parameters":
        render_vehicle_parameters_step(compact)
    elif current_step == "operational_parameters":
        render_operational_parameters_step(compact)
    elif current_step == "economic_parameters":
        render_economic_parameters_step(compact)


def render_configuration_step(compact: bool = False):
    """
    Render the vehicle configuration step.
    
    This step allows users to configure vehicle parameters, operational settings,
    economic parameters, and financing options for the TCO analysis.
    
    Args:
        compact: Whether to use compact layout for smaller screens
    """
    render_section_header(
        "Vehicle Configuration", 
        "Configure the vehicles you want to compare and calculate their Total Cost of Ownership."
    )
    
    # Configuration management for saving/loading configs
    # Use the expandable section to wrap the configuration management
    render_expandable_section(
        "Configuration Management",
        render_config_management,
        expanded=False,
        key="config_management_section"
    )
    
    # Create columns for side-by-side vehicle inputs
    col1, col2 = st.columns(2)
    
    with col1:
        # Get vehicle type for display in header
        vehicle_1 = st.session_state.get("vehicle_1_input", {})
        v1_type = vehicle_1.vehicle.type if hasattr(vehicle_1, "vehicle") else None
        
        # Use standard abbreviations for display
        v1_label = "BET" if v1_type == VehicleType.BATTERY_ELECTRIC else \
                   "ICE" if v1_type == VehicleType.DIESEL else \
                   "Vehicle"
        
        render_subsection_header(f"Vehicle 1 ({v1_label})", "🚚")
        render_vehicle_inputs(vehicle_number=1)
        render_operational_inputs(vehicle_number=1)
        render_economic_inputs(vehicle_number=1)
        render_financing_inputs(vehicle_number=1)
        
    with col2:
        # Get vehicle type for display in header
        vehicle_2 = st.session_state.get("vehicle_2_input", {})
        v2_type = vehicle_2.vehicle.type if hasattr(vehicle_2, "vehicle") else None
        
        # Use standard abbreviations for display
        v2_label = "BET" if v2_type == VehicleType.BATTERY_ELECTRIC else \
                   "ICE" if v2_type == VehicleType.DIESEL else \
                   "Vehicle"
        
        render_subsection_header(f"Vehicle 2 ({v2_label})", "🚚")
        render_vehicle_inputs(vehicle_number=2)
        render_operational_inputs(vehicle_number=2)
        render_economic_inputs(vehicle_number=2)
        render_financing_inputs(vehicle_number=2)
    
    # Calculate button in a centered container
    _, center_col, _ = st.columns([1, 2, 1])
    with center_col:
        if st.button(
            "Calculate TCO", 
            on_click=calculate_and_show_results,
            key="calculate_button",
            use_container_width=True
        ):
            # Button callback will handle the calculation
            pass


def calculate_and_show_results():
    """
    Calculate TCO and show results.
    
    This function is called when the Calculate button is clicked.
    It performs the calculation and navigates to the results page.
    """
    from app import calculate_tco  # Import here to avoid circular imports
    
    # Calculate TCO
    calculate_tco()
    
    # Navigate to results page if calculation was successful
    if st.session_state.get("results") is not None:
        set_step("results")


def render_results_step():
    """
    Render the results step.
    """
    render_section_header(
        "TCO Results", 
        "View and analyze the Total Cost of Ownership results for your configured vehicles."
    )
    
    # Check if results are available
    if "results" in st.session_state and st.session_state.results is not None:
        results = st.session_state.results
        comparison = st.session_state.get("comparison")
        
        if results and comparison:
            # Display results
            display_results(results, comparison)
        else:
            st.warning("Results data is incomplete. Please recalculate TCO.")
            st.button(
                "Go to Configuration",
                on_click=set_step,
                args=("config",)
            )
    else:
        st.info("No results available. Please configure vehicles and calculate TCO.")
        st.button(
            "Go to Configuration",
            on_click=set_step,
            args=("config",)
        )


def render_export_step():
    """
    Render the export step.
    """
    render_section_header(
        "Export & Share", 
        "Export your TCO analysis results in various formats."
    )
    
    # Check if results are available
    if "results" in st.session_state and st.session_state.results is not None:
        results = st.session_state.results
        comparison = st.session_state.get("comparison")
        
        if results and comparison:
            # Show export options
            render_export_options(results, comparison)
        else:
            st.warning("Results data is incomplete. Please recalculate TCO.")
            st.button(
                "Go to Configuration",
                on_click=set_step,
                args=("config",)
            )
    else:
        st.info("No results available to export. Please calculate TCO first.")
        st.button(
            "Go to Configuration",
            on_click=set_step,
            args=("config",)
        )


def render_export_options(results, comparison):
    """
    Render export options for TCO results.
    
    Args:
        results: Dictionary of TCO result objects
        comparison: Comparison result object
    """
    # TODO: Implement export functionality in Phase 4
    st.info("Export functionality will be implemented in future updates.")
    
    # Placeholder for export options
    export_type = st.radio(
        "Select Export Format",
        options=["Excel", "PDF", "CSV", "JSON"],
        horizontal=True
    )
    
    st.button("Generate Export", disabled=True)


def render_guide_step():
    """
    Render the user guide step.
    """
    render_section_header(
        "User Guide", 
        "Learn how to use the TCO Modeller and understand the analysis methodology."
    )
    render_guide() 

def get_available_steps(navigation_state=None):
    """
    Get a list of available steps based on navigation state.
    
    Args:
        navigation_state: Optional NavigationState dataclass or dictionary with navigation state
        
    Returns:
        List of available step IDs
    """
    # Default steps that are always available
    available_steps = ["introduction", "config", "guide", "vehicle_parameters"]
    
    # Get the current step from navigation state
    current_step = None
    if navigation_state:
        # Handle both dict and NavigationState dataclass
        if hasattr(navigation_state, 'get'):  # Dict-like object
            current_step = navigation_state.get("current_step")
            has_results = navigation_state.get("has_results", False)
        elif hasattr(navigation_state, '__dataclass_fields__'):  # Dataclass
            current_step = getattr(navigation_state, "current_step", None)
            has_results = getattr(navigation_state, "has_results", False)
        
        # Include completed steps and next available step
        completed_steps = []
        if hasattr(navigation_state, 'get'):
            completed_steps = navigation_state.get("completed_steps", [])
        elif hasattr(navigation_state, '__dataclass_fields__'):
            completed_steps = getattr(navigation_state, "completed_steps", [])
        
        # Add operational_parameters as available if the current step is vehicle_parameters
        if current_step == "vehicle_parameters":
            available_steps.append("operational_parameters")
        
        # If operational_parameters is completed or current, make results available
        if "operational_parameters" in completed_steps or current_step == "operational_parameters":
            available_steps.append("results")
        
        # If we have results, add export step
        if has_results or "results" in completed_steps or current_step == "results":
            available_steps.append("export")
    elif "results" in st.session_state and st.session_state.results is not None:
        available_steps.append("results")
        available_steps.append("export")
    
    return available_steps


def render_vehicle_parameters_step(compact: bool = False):
    """
    Render the vehicle parameters step.
    
    This step allows users to configure basic vehicle parameters.
    
    Args:
        compact: Whether to use compact layout for smaller screens
    """
    render_section_header(
        "Vehicle Parameters", 
        "Configure the basic parameters for the vehicles you want to compare."
    )
    
    # Configuration management for saving/loading configs
    if not compact:
        render_expandable_section(
            "Configuration Management",
            render_config_management,
            expanded=False,
            key="config_management_section"
        )
    
    # Create columns for side-by-side vehicle inputs
    col1, col2 = st.columns(2)
    
    with col1:
        render_subsection_header("Vehicle 1", "🚚")
        render_vehicle_inputs(vehicle_number=1, compact=compact)
    
    with col2:
        render_subsection_header("Vehicle 2", "🚚")
        render_vehicle_inputs(vehicle_number=2, compact=compact)
    
    # Navigation buttons
    _, center_col, _ = st.columns([1, 2, 1])
    with center_col:
        st.button(
            "Next: Operational Parameters",
            on_click=set_step,
            args=("operational_parameters",),
            use_container_width=True
        )


def render_operational_parameters_step(compact: bool = False):
    """
    Render the operational parameters step.
    
    This step allows users to configure operational settings.
    
    Args:
        compact: Whether to use compact layout for smaller screens
    """
    render_section_header(
        "Operational Parameters", 
        "Configure the operational settings for your vehicles."
    )
    
    # Create columns for side-by-side inputs
    col1, col2 = st.columns(2)
    
    with col1:
        render_subsection_header("Vehicle 1 Operations", "🚚")
        render_operational_inputs(vehicle_number=1, compact=compact)
    
    with col2:
        render_subsection_header("Vehicle 2 Operations", "🚚")
        render_operational_inputs(vehicle_number=2, compact=compact)
    
    # Navigation buttons
    button_cols = st.columns([1, 1, 1])
    with button_cols[0]:
        st.button(
            "← Back to Vehicle Parameters",
            on_click=set_step,
            args=("vehicle_parameters",),
            use_container_width=True
        )
    
    with button_cols[2]:
        st.button(
            "Next: Economic Parameters →",
            on_click=set_step,
            args=("economic_parameters",),
            use_container_width=True
        )


def render_economic_parameters_step(compact: bool = False):
    """
    Render the economic parameters step.
    
    This step allows users to configure economic and financing parameters.
    
    Args:
        compact: Whether to use compact layout for smaller screens
    """
    render_section_header(
        "Economic Parameters", 
        "Configure the economic and financing parameters for your analysis."
    )
    
    # Create columns for side-by-side inputs
    col1, col2 = st.columns(2)
    
    with col1:
        render_subsection_header("Vehicle 1 Economics", "🚚")
        render_economic_inputs(vehicle_number=1, compact=compact)
        render_financing_inputs(vehicle_number=1, compact=compact)
    
    with col2:
        render_subsection_header("Vehicle 2 Economics", "🚚")
        render_economic_inputs(vehicle_number=2, compact=compact)
        render_financing_inputs(vehicle_number=2, compact=compact)
    
    # Navigation and calculation buttons
    button_cols = st.columns([1, 1, 1])
    with button_cols[0]:
        st.button(
            "← Back to Operational Parameters",
            on_click=set_step,
            args=("operational_parameters",),
            use_container_width=True
        )
    
    with button_cols[2]:
        st.button(
            "Calculate TCO",
            on_click=calculate_and_show_results,
            key="economic_calculate_button",
            use_container_width=True
        ) 