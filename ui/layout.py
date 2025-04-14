"""
Layout Module

This module provides layout options for the application, including the side-by-side
layout that shows configuration and results simultaneously.
"""

import streamlit as st
from typing import Dict, Any, Optional
import numpy as np
import datetime

from tco_model.models import TCOOutput, ComparisonResult
from ui.inputs.vehicle import render_vehicle_form
from utils.helpers import format_currency, format_percentage
from tco_model.calculator import TCOCalculator
from tco_model.models import ScenarioInput
import plotly.graph_objects as go
from ui.results.charts import apply_chart_theme
from ui.results.live_preview import display_results_in_live_mode


def create_live_preview_layout():
    """
    Create a side-by-side layout with configuration in sidebar and results in main panel
    """
    # Set sidebar mode UI
    with st.sidebar:
        st.markdown('<div class="preview-mode-toggle">', unsafe_allow_html=True)
        
        # Layout mode selection with visual indicator
        enable_live_preview = st.checkbox(
            "Live Preview Mode",
            value=st.session_state.get("enable_live_preview", True),
            key="enable_live_preview_toggle",
            help="Show results in main panel while configuring in sidebar"
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    if enable_live_preview:
        # Save current layout mode
        st.session_state["layout_mode"] = "live_preview"
        
        # Set up sidebar for configuration
        with st.sidebar:
            st.markdown("## Vehicle Configuration")
            
            # Create tabs for vehicle 1 and vehicle 2
            vehicle_tabs = st.tabs(["Vehicle 1", "Vehicle 2"])
                          
            # Configure Vehicle 1
            with vehicle_tabs[0]:
                render_compact_vehicle_form(vehicle_number=1, compact=True)
            
            # Configure Vehicle 2
            with vehicle_tabs[1]:
                render_compact_vehicle_form(vehicle_number=2, compact=True)
            
            # Show calculation status
            with st.container():
                # Calculate button with loading indicator
                calculate_col, status_col = st.columns([3, 2])
                
                with calculate_col:
                    calculate_button = st.button(
                        "Calculate TCO",
                        on_click=calculate_tco,
                        key="sidebar_calculate_button",
                        use_container_width=True
                    )
                
                with status_col:
                    if "calculation_status" in st.session_state:
                        if st.session_state.calculation_status == "calculating":
                            st.markdown('<div class="calculation-status calculating">Calculating...</div>', 
                                      unsafe_allow_html=True)
                        elif st.session_state.calculation_status == "done":
                            st.markdown('<div class="calculation-status done">Up to date</div>', 
                                      unsafe_allow_html=True)
                
                # Show last calculation time
                if "last_calculation_time" in st.session_state:
                    st.markdown(f"""
                    <div class="last-calculation-time">
                        Last updated: {st.session_state.last_calculation_time}
                    </div>
                    """, unsafe_allow_html=True)
        
        # Main panel shows results with optimized layout for sidebar+main configuration
        main_container = st.container()
        with main_container:
            if "results" in st.session_state and st.session_state.results:
                # Special rendering for side-by-side mode with actual TCO model data
                display_results_in_live_mode(
                    st.session_state.results, 
                    st.session_state.comparison,
                    selected_parameter=st.session_state.get("parameter_to_analyse")
                )
            else:
                # Show guidance and example results using real TCO model calculations
                st.info("Configure vehicles in the sidebar and click 'Calculate TCO' to see results here.")
                render_example_results()
                
                # Add quick actions to help user get started
                st.markdown("### Quick Start Options")
                
                quick_start_cols = st.columns(3)
                with quick_start_cols[0]:
                    if st.button("Load Sample BET vs Diesel"):
                        load_default_comparison()
                
                with quick_start_cols[1]:
                    if st.button("Run with Current Settings"):
                        calculate_tco()
                
                with quick_start_cols[2]:
                    if st.button("Show Tutorial"):
                        st.session_state["show_tutorial"] = True
    else:
        # Use original tab-based layout
        st.session_state["layout_mode"] = "tabbed"
        render_tabbed_layout()


def render_compact_vehicle_form(vehicle_number: int, compact: bool = True):
    """
    Render a more compact version of the vehicle form suitable for sidebar display
    
    Args:
        vehicle_number: The vehicle number (1 or 2)
        compact: Whether to use compact mode
    """
    # Call the standard vehicle form with compact flag
    render_vehicle_form(vehicle_number, compact=compact)


def render_example_results():
    """
    Render example results using actual TCO model calculations instead of placeholder images
    """
    st.markdown("### Sample TCO Analysis Results")
    st.markdown("The results section will display visualizations like these once you calculate TCO:")
    
    # Create a calculator and sample scenarios
    calculator = TCOCalculator()
    
    # Create simplified sample scenarios
    bet_scenario = ScenarioInput(
        name="Sample BET",
        vehicle_type="bet",
        analysis_period=8,
        annual_distance=100000,
        acquisition_cost=450000,
        residual_value_pct=20,
        electricity_price=0.25,
        energy_consumption=1.2,
        maintenance_cost_per_km=0.12
    )
    
    diesel_scenario = ScenarioInput(
        name="Sample Diesel",
        vehicle_type="diesel",
        analysis_period=8,
        annual_distance=100000,
        acquisition_cost=300000,
        residual_value_pct=15,
        diesel_price=1.50,
        fuel_consumption=35,
        maintenance_cost_per_km=0.18
    )
    
    # Calculate sample results
    bet_result = calculator.calculate(bet_scenario)
    diesel_result = calculator.calculate(diesel_scenario)
    comparison = calculator.compare(bet_result, diesel_result)
    
    results = {
        "vehicle_1": bet_result,
        "vehicle_2": diesel_result
    }
    
    # Create two columns for sample charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Cumulative TCO Over Time")
        
        # Create cumulative TCO chart
        years = list(range(1, bet_result.analysis_period_years + 1))
        
        # Calculate cumulative costs
        bet_cumulative = [sum(bet_result.annual_costs[:i+1]) for i in range(len(bet_result.annual_costs))]
        diesel_cumulative = [sum(diesel_result.annual_costs[:i+1]) for i in range(len(diesel_result.annual_costs))]
        
        # Create the chart
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=years,
            y=bet_cumulative,
            mode='lines+markers',
            name=bet_result.vehicle_name,
            line=dict(color='#4CAF50', width=3)
        ))
        
        fig.add_trace(go.Scatter(
            x=years,
            y=diesel_cumulative,
            mode='lines+markers',
            name=diesel_result.vehicle_name,
            line=dict(color='#FF9800', width=3)
        ))
        
        # Add any breakeven point if it exists
        if comparison.investment_analysis and comparison.investment_analysis.has_payback:
            payback_year = comparison.investment_analysis.payback_years
            
            # Interpolate costs at payback point
            payback_cost = np.interp(payback_year, years, bet_cumulative)
            
            fig.add_trace(go.Scatter(
                x=[payback_year],
                y=[payback_cost],
                mode='markers',
                marker=dict(size=12, symbol='star', color='green'),
                name='Breakeven Point',
                hoverinfo='text',
                hovertext=f'Breakeven at year {payback_year:.1f}'
            ))
        
        # Update layout
        apply_chart_theme(fig, height=300)
        fig.update_layout(
            showlegend=True,
            xaxis_title="Year",
            yaxis_title="Cumulative Cost ($)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    with col2:
        st.markdown("#### Cost Component Breakdown")
        
        # Get component costs
        from tco_model.terminology import UI_COMPONENT_KEYS, UI_COMPONENT_LABELS
        from utils.ui_terminology import get_component_color
        
        components = []
        bet_values = []
        diesel_values = []
        
        for component in UI_COMPONENT_KEYS:
            if component != "residual_value":  # Handle residual value separately
                components.append(UI_COMPONENT_LABELS.get(component, component))
                bet_values.append(calculator.get_component_value(bet_result, component))
                diesel_values.append(calculator.get_component_value(diesel_result, component))
        
        # Create the chart
        fig = go.Figure()
        
        # Add stacked bars for each vehicle
        for i, component in enumerate(components):
            fig.add_trace(go.Bar(
                x=[bet_result.vehicle_name],
                y=[bet_values[i]],
                name=component,
                marker_color=get_component_color(UI_COMPONENT_KEYS[i]),
                legendgroup=component,
            ))
            
            fig.add_trace(go.Bar(
                x=[diesel_result.vehicle_name],
                y=[diesel_values[i]],
                name=component,
                marker_color=get_component_color(UI_COMPONENT_KEYS[i]),
                legendgroup=component,
                showlegend=False
            ))
        
        # Update layout
        apply_chart_theme(fig, height=300)
        fig.update_layout(
            barmode='stack',
            xaxis_title="",
            yaxis_title="Cost ($)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})


def render_tabbed_layout():
    """
    Render the original tabbed layout approach
    """
    # Import here to avoid circular imports
    from ui.progressive_disclosure import implement_progressive_disclosure
    
    # Just delegate to the existing tabbed layout implementation
    implement_progressive_disclosure()


def calculate_tco():
    """
    Calculate TCO with status tracking for live preview mode
    
    This wraps the main calculate_tco function with additional
    status tracking for the live preview mode
    """
    # Import here to avoid circular imports
    from app import calculate_tco as main_calculate_tco
    import datetime
    
    # Set calculating status
    st.session_state["calculation_status"] = "calculating"
    
    # Run calculation
    main_calculate_tco()
    
    # Update status
    st.session_state["calculation_status"] = "done"
    st.session_state["last_calculation_time"] = datetime.datetime.now().strftime("%H:%M:%S")


def load_default_comparison():
    """
    Load default comparison data for quick start
    """
    # Import here to avoid circular imports
    from utils.helpers import load_default_scenario
    
    # Load default scenarios
    try:
        bet_scenario = load_default_scenario("default_bet")
        ice_scenario = load_default_scenario("default_ice")
        
        # Set in session state
        st.session_state["vehicle_1_input"] = bet_scenario
        st.session_state["vehicle_2_input"] = ice_scenario
        
        # Run calculation
        calculate_tco()
        
        # Show success message
        st.success("Loaded sample BET vs Diesel comparison")
    except Exception as e:
        st.error(f"Error loading default comparison: {str(e)}") 