"""
Main application entry point for the Australian Heavy Vehicle TCO Modeller.

This module serves as the controller layer for the Streamlit application. It initializes the app,
manages the session state, and orchestrates the interaction between the UI modules and the
TCO calculation engine.
"""

import streamlit as st
from typing import Dict, Any, Optional, Tuple
import traceback

# Import UI modules
from ui.sidebar import render_sidebar
from ui.progressive_disclosure import implement_progressive_disclosure
from ui.inputs.vehicle import render_vehicle_inputs
from ui.inputs.operational import render_operational_inputs
from ui.inputs.economic import render_economic_inputs
from ui.inputs.financing import render_financing_inputs
from ui.inputs.parameter_comparisons_page import render_parameter_comparisons_page
from ui.results.display import display_results, display_from_session_state
from ui.layout import create_live_preview_layout
from ui.guide import render_guide

# Import TCO model and utilities
from tco_model.calculator import TCOCalculator
from tco_model.models import ScenarioInput, TCOOutput, VehicleType, ComparisonResult
from utils.helpers import (
    load_default_scenario,
    get_safe_state_value,
    set_safe_state_value,
    update_state_from_model,
    update_model_from_state,
    debug_state,
    initialize_nested_state,
)

# Import UI terminology and component utilities
from utils.ui_terminology import get_formatted_label, get_component_color
from utils.ui_components import UIComponentFactory
from utils.css_loader import load_css, get_available_themes

# Import navigation utilities
from utils.navigation_state import initialize_navigation

# Constants for session state keys
STATE_INITIALIZED = "initialized"
STATE_VEHICLE_1_INPUT = "vehicle_1_input"
STATE_VEHICLE_2_INPUT = "vehicle_2_input"
STATE_RESULTS = "results"
STATE_COMPARISON = "comparison"
STATE_SHOW_RESULTS = "show_results"
STATE_ERROR = "error"
STATE_DEBUG_MODE = "debug_mode"
STATE_UI_THEME = "ui_theme"
STATE_CURRENT_PAGE = "current_page"
STATE_LAYOUT_MODE = "layout_mode"


def initialize_session_state():
    """
    Initialize the Streamlit session state with default values.
    
    This function sets up the initial state structure for the application,
    including loading default scenarios for the two vehicles being compared.
    It only runs once when the app is first loaded.
    """
    if STATE_INITIALIZED not in st.session_state:
        try:
            st.session_state[STATE_INITIALIZED] = True
            
            # Load default scenarios for BET and ICE vehicles
            bet_scenario = load_default_scenario("default_bet")
            ice_scenario = load_default_scenario("default_ice")
            
            # Store the full model objects in session state
            st.session_state[STATE_VEHICLE_1_INPUT] = bet_scenario
            st.session_state[STATE_VEHICLE_2_INPUT] = ice_scenario
            
            # Initialize results containers
            st.session_state[STATE_RESULTS] = None
            st.session_state[STATE_COMPARISON] = None
            st.session_state[STATE_SHOW_RESULTS] = False
            st.session_state[STATE_ERROR] = None
            st.session_state[STATE_DEBUG_MODE] = False
            st.session_state[STATE_UI_THEME] = "light"
            st.session_state[STATE_CURRENT_PAGE] = "inputs"
            st.session_state[STATE_LAYOUT_MODE] = "tabbed"
            
            # Initialize nested state for UI components to reference
            # This makes individual fields accessible via dot notation
            update_state_from_model(STATE_VEHICLE_1_INPUT, bet_scenario)
            update_state_from_model(STATE_VEHICLE_2_INPUT, ice_scenario)
            
            # Enable live preview by default
            st.session_state["enable_live_preview"] = True
            
            # Initialize navigation state
            initialize_navigation()
            
        except Exception as e:
            st.session_state[STATE_ERROR] = str(e)
            st.error(f"Error initializing application: {str(e)}")
            if st.session_state.get(STATE_DEBUG_MODE, False):
                st.exception(e)


def update_vehicle_inputs(vehicle_number: int) -> Tuple[bool, Optional[str]]:
    """
    Update the vehicle input model from UI component values in session state.
    
    Args:
        vehicle_number: The vehicle number (1 or 2)
        
    Returns:
        Tuple of (success, error_message)
    """
    state_key = f"vehicle_{vehicle_number}_input"
    
    try:
        # Update the model from session state values
        updated_model = update_model_from_state(state_key, ScenarioInput)
        
        if updated_model:
            # Store the updated model
            st.session_state[state_key] = updated_model
            return True, None
        else:
            return False, "Failed to validate input model"
            
    except Exception as e:
        error_msg = f"Error updating vehicle {vehicle_number} inputs: {str(e)}"
        return False, error_msg


def calculate_tco():
    """
    Calculate TCO for both vehicles and store results in session state.
    
    This function is called when the user clicks the Calculate button.
    It validates inputs, runs calculations, and prepares results for display.
    """
    # Reset error state
    st.session_state[STATE_ERROR] = None
    
    try:
        # First validate and update both vehicle models
        v1_valid, v1_error = update_vehicle_inputs(1)
        v2_valid, v2_error = update_vehicle_inputs(2)
        
        if not v1_valid:
            st.error(f"Vehicle 1 validation error: {v1_error}")
            return
            
        if not v2_valid:
            st.error(f"Vehicle 2 validation error: {v2_error}")
            return
        
        # Get the current scenario inputs from session state
        vehicle_1_input: ScenarioInput = st.session_state[STATE_VEHICLE_1_INPUT]
        vehicle_2_input: ScenarioInput = st.session_state[STATE_VEHICLE_2_INPUT]
        
        # Initialize the TCO calculator
        calculator = TCOCalculator()
        
        # Calculate TCO for both vehicles
        with st.spinner("Calculating TCO for Vehicle 1..."):
            vehicle_1_results = calculator.calculate(vehicle_1_input)
            
        with st.spinner("Calculating TCO for Vehicle 2..."):
            vehicle_2_results = calculator.calculate(vehicle_2_input)
        
        # Store results in session state
        st.session_state[STATE_RESULTS] = {
            "vehicle_1": vehicle_1_results,
            "vehicle_2": vehicle_2_results,
        }
        
        # Compare the results
        with st.spinner("Comparing results..."):
            st.session_state[STATE_COMPARISON] = calculator.compare_results(
                vehicle_1_results, vehicle_2_results
            )
        
        # Show results section
        st.session_state[STATE_SHOW_RESULTS] = True
        
        # In live preview mode, stay on current page
        # In tabbed mode, navigate to results
        if st.session_state.get(STATE_LAYOUT_MODE) != "live_preview":
            st.session_state[STATE_CURRENT_PAGE] = "results"
        
    except Exception as e:
        error_msg = f"Error calculating TCO: {str(e)}"
        st.session_state[STATE_ERROR] = error_msg
        st.error(error_msg)
        
        if st.session_state.get(STATE_DEBUG_MODE, False):
            st.exception(e)
            st.write(traceback.format_exc())


def load_app_styles():
    """Load application styles with theme support"""
    selected_theme = st.session_state.get(STATE_UI_THEME, "light")
    load_css(selected_theme)


def render_app_content():
    """Render the appropriate content based on the current page and layout mode"""
    current_page = st.session_state.get(STATE_CURRENT_PAGE, "inputs")
    layout_mode = st.session_state.get(STATE_LAYOUT_MODE, "tabbed")
    
    # If in live preview mode, use side-by-side layout
    if layout_mode == "live_preview":
        create_live_preview_layout()
        return
    
    # Otherwise use standard tabbed layout
    if current_page == "inputs":
        implement_progressive_disclosure()
    elif current_page == "parameter_comparison":
        render_parameter_comparisons_page()
    elif current_page == "results":
        if st.session_state.get(STATE_SHOW_RESULTS, False):
            # Render results content
            st.header("TCO Results & Comparison")
            display_from_session_state()
        else:
            # If no results available, show calculate button
            st.info("No results available yet. Configure vehicles and calculate TCO.")
            if st.button("Calculate TCO Now", key="calc_tco_now"):
                calculate_tco()
    elif current_page == "guide":
        render_guide()
    else:
        # Default to inputs if current page is invalid
        implement_progressive_disclosure()


def main():
    """Main application entry point."""
    # Page configuration
    st.set_page_config(
        page_title="Australian Heavy Vehicle TCO Modeller",
        page_icon="🚚",
        layout="wide",
    )
    
    # Initialize session state
    initialize_session_state()
    
    # Get selected theme from session state or default to light
    selected_theme = st.session_state.get(STATE_UI_THEME, "light")
    
    # Load CSS with theme
    load_css(selected_theme)
    
    # Render the application title
    st.title("Australian Heavy Vehicle TCO Modeller")
    st.markdown("Compare the Total Cost of Ownership for different heavy vehicle types.")
    
    # Render sidebar with navigation
    render_sidebar()
    
    # Display debug information if enabled
    if st.session_state.get(STATE_DEBUG_MODE, False):
        with st.expander("Debug Information"):
            st.write("Session State Overview:", debug_state())
            st.write("Vehicle 1 State:", debug_state(STATE_VEHICLE_1_INPUT))
            st.write("Vehicle 2 State:", debug_state(STATE_VEHICLE_2_INPUT))
    
    # Render the main content based on current page
    render_app_content()


if __name__ == "__main__":
    main() 