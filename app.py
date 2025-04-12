"""
Main application entry point for the Australian Heavy Vehicle TCO Modeller.

This module serves as the controller layer for the Streamlit application. It initializes the app,
manages the session state, and orchestrates the interaction between the UI modules and the
TCO calculation engine.
"""

import streamlit as st
from typing import Dict, Any, Optional

# Import UI modules
from ui.sidebar import render_sidebar
from ui.inputs.vehicle import render_vehicle_inputs
from ui.inputs.operational import render_operational_inputs
from ui.inputs.economic import render_economic_inputs
from ui.results.summary import render_summary
from ui.results.charts import render_charts

# Import TCO model and utilities
from tco_model.calculator import TCOCalculator
from tco_model.models import ScenarioInput, TCOOutput
from utils.helpers import (
    load_default_scenario,
    get_safe_state_value,
    set_safe_state_value,
)


def initialize_session_state():
    """Initialize the Streamlit session state with default values."""
    if "initialized" not in st.session_state:
        st.session_state.initialized = True
        # Load default scenarios for BET and ICE vehicles
        st.session_state.vehicle_1_input = load_default_scenario("default_bet")
        st.session_state.vehicle_2_input = load_default_scenario("default_ice")
        st.session_state.results = None
        st.session_state.comparison = None
        st.session_state.show_results = False


def calculate_tco():
    """Calculate TCO for both vehicles and store results in session state."""
    try:
        # Get the current scenario inputs from session state
        vehicle_1_input: ScenarioInput = st.session_state.vehicle_1_input
        vehicle_2_input: ScenarioInput = st.session_state.vehicle_2_input
        
        # Initialize the TCO calculator
        calculator = TCOCalculator()
        
        # Calculate TCO for both vehicles
        vehicle_1_results = calculator.calculate(vehicle_1_input)
        vehicle_2_results = calculator.calculate(vehicle_2_input)
        
        # Store results in session state
        st.session_state.results = {
            "vehicle_1": vehicle_1_results,
            "vehicle_2": vehicle_2_results,
        }
        
        # Compare the results
        st.session_state.comparison = calculator.compare_results(
            vehicle_1_results, vehicle_2_results
        )
        
        # Show results section
        st.session_state.show_results = True
        
    except Exception as e:
        st.error(f"Error calculating TCO: {str(e)}")


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
    
    # Render the application title
    st.title("Australian Heavy Vehicle TCO Modeller")
    st.markdown("Compare the Total Cost of Ownership for different heavy vehicle types.")
    
    # Render sidebar
    render_sidebar()
    
    # Create tabs for inputs and results
    tabs = st.tabs(["Vehicle Configuration", "Results"])
    
    # Vehicle Configuration Tab
    with tabs[0]:
        st.header("Vehicle Configuration")
        
        # Create columns for side-by-side vehicle inputs
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Vehicle 1 (BET)")
            render_vehicle_inputs(vehicle_number=1)
            render_operational_inputs(vehicle_number=1)
            render_economic_inputs(vehicle_number=1)
            
        with col2:
            st.subheader("Vehicle 2 (ICE)")
            render_vehicle_inputs(vehicle_number=2)
            render_operational_inputs(vehicle_number=2)
            render_economic_inputs(vehicle_number=2)
        
        # Calculate button
        st.button("Calculate TCO", on_click=calculate_tco)
    
    # Results Tab
    with tabs[1]:
        if st.session_state.show_results:
            st.header("TCO Results")
            
            # Render summary tables
            render_summary(st.session_state.results, st.session_state.comparison)
            
            # Render visualizations
            render_charts(st.session_state.results, st.session_state.comparison)
        else:
            st.info("Configure vehicle parameters and click 'Calculate TCO' to see results.")


if __name__ == "__main__":
    main() 