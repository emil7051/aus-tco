"""
Layout Module

This module provides layout options for the application, including the side-by-side
layout that shows configuration and results simultaneously.
"""

import streamlit as st
from typing import Dict, Any, Optional
import numpy as np
import datetime
from enum import Enum

from tco_model.models import TCOOutput, ComparisonResult
from ui.inputs.vehicle import render_vehicle_form
from utils.helpers import format_currency, format_percentage
from tco_model.calculator import TCOCalculator
from tco_model.models import ScenarioInput
import plotly.graph_objects as go
from ui.results.charts import apply_chart_theme
from ui.results.live_preview import display_results_in_live_mode


class LayoutMode(Enum):
    """
    Enum for defining different layout modes in the application.
    """
    STEP_BY_STEP = "step_by_step"    # Traditional step-based UI with linear flow
    SIDE_BY_SIDE = "side_by_side"    # Configuration and results side-by-side
    TABBED = "tabbed"                # Tab-based UI for different sections
    COMPACT = "compact"              # Compact UI for small screens
    DASHBOARD = "dashboard"          # Dashboard-style layout emphasizing results


def get_responsive_layout(viewport_width: int, viewport_height: int) -> Dict[str, Any]:
    """
    Get responsive layout configuration based on viewport dimensions.
    
    Args:
        viewport_width: Browser viewport width in pixels
        viewport_height: Browser viewport height in pixels
        
    Returns:
        Dictionary with layout configuration properties:
            - columns: Number of columns to use (1-3)
            - sidebar_expanded: Whether sidebar should be expanded
            - card_height: Height for cards
            - font_size: Base font size
    """
    # Define viewport size breakpoints
    mobile_max_width = 768
    tablet_max_width = 1200
    
    # Mobile layout (1 column, collapsed sidebar)
    if viewport_width <= mobile_max_width:
        return {
            "columns": 1,
            "sidebar_expanded": False,
            "card_height": "auto",
            "font_size": "small"
        }
    # Tablet layout (2 columns, conditionally expanded sidebar)
    elif viewport_width <= tablet_max_width:
        return {
            "columns": 2 if viewport_height > 800 else 1,
            "sidebar_expanded": viewport_width > 900,
            "card_height": "auto" if viewport_height < 800 else "250px",
            "font_size": "medium"
        }
    # Desktop layout (2-3 columns, expanded sidebar)
    else:
        return {
            "columns": 3 if viewport_width > 1600 and viewport_height > 900 else 2,
            "sidebar_expanded": True,
            "card_height": "300px" if viewport_height > 900 else "250px",
            "font_size": "medium"
        }


def switch_layout_mode(config: Dict[str, Any], mode: LayoutMode) -> Dict[str, Any]:
    """
    Switch between different layout modes, preserving relevant configuration.
    
    Args:
        config: Current layout configuration dictionary
        mode: Target LayoutMode to switch to
        
    Returns:
        Updated configuration dictionary
    """
    # Create a copy of the configuration to avoid modifying the original
    new_config = config.copy()
    
    # Update the mode
    new_config["mode"] = mode
    
    # Apply mode-specific settings
    if mode == LayoutMode.STEP_BY_STEP:
        new_config["sidebar_visible"] = False
        new_config["show_breadcrumbs"] = True
        new_config["show_progress"] = True
    elif mode == LayoutMode.SIDE_BY_SIDE:
        new_config["sidebar_visible"] = True
        new_config["sidebar_expanded"] = True
        new_config["show_breadcrumbs"] = False
        new_config["show_progress"] = False
    elif mode == LayoutMode.TABBED:
        new_config["sidebar_visible"] = False
        new_config["show_breadcrumbs"] = True
        new_config["show_progress"] = True
    elif mode == LayoutMode.COMPACT:
        new_config["sidebar_visible"] = True
        new_config["sidebar_expanded"] = False
        new_config["show_breadcrumbs"] = False
        new_config["show_progress"] = True
    elif mode == LayoutMode.DASHBOARD:
        new_config["sidebar_visible"] = True
        new_config["sidebar_expanded"] = False
        new_config["show_breadcrumbs"] = False
        new_config["show_progress"] = False
    
    return new_config


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
        # Load BET vehicle as vehicle 1
        bet_scenario = ScenarioData(
            vehicle_type="BET",
            vehicle_name="Battery Electric Truck",
            purchase_price=450000,
            annual_maintenance_cost=7500,
            annual_insurance_cost=8000,
            years_of_ownership=10
        )
        
        # Load ICE vehicle as vehicle 2
        ice_scenario = ScenarioData(
            vehicle_type="Diesel",
            vehicle_name="Diesel Truck",
            purchase_price=250000,
            annual_maintenance_cost=15000,
            annual_insurance_cost=6000,
            years_of_ownership=10
        )
        
        # Set in session state
        st.session_state["vehicle_1_input"] = bet_scenario
        st.session_state["vehicle_2_input"] = ice_scenario
        
        # Run calculation
        calculate_tco()
        
        # Show success message
        st.success("Loaded sample BET vs Diesel comparison")
    except Exception as e:
        st.error(f"Error loading default comparison: {str(e)}")


def create_side_by_side_comparison(result1, result2):
    """
    Create a side-by-side comparison view of two vehicles.

    Args:
        result1: TCO result for the first vehicle
        result2: TCO result for the second vehicle
        
    Returns:
        HTML string with side-by-side comparison
    """
    # Import required modules
    from tco_model.calculator import TCOCalculator
    from utils.helpers import format_currency
    
    calculator = TCOCalculator()
    comparison = calculator.compare(result1, result2)
    
    # Format key metrics
    result1_tco = format_currency(result1.total_tco)
    result2_tco = format_currency(result2.total_tco)
    result1_lcod = format_currency(result1.lcod)
    result2_lcod = format_currency(result2.lcod)
    
    # Calculate difference and % difference
    tco_diff = format_currency(abs(comparison.tco_difference))
    tco_diff_pct = f"{abs(comparison.tco_percentage):.1f}%"
    
    # Determine which vehicle is cheaper
    if comparison.cheaper_option == 1:
        cheaper_vehicle = result1.vehicle_name
        cost_diff_indicator = "lower"
    else:
        cheaper_vehicle = result2.vehicle_name
        cost_diff_indicator = "higher"
    
    # Get emissions data if available
    emissions_1 = getattr(result1, 'emissions', None)
    emissions_2 = getattr(result2, 'emissions', None)
    
    emissions_html = ""
    if emissions_1 and emissions_2:
        # Format emissions data
        co2_1 = f"{emissions_1.total_co2_tonnes:.1f} tonnes"
        co2_2 = f"{emissions_2.total_co2_tonnes:.1f} tonnes"
        co2_per_km_1 = f"{emissions_1.co2_per_km:.0f} g/km"
        co2_per_km_2 = f"{emissions_2.co2_per_km:.0f} g/km"
        
        # Calculate emissions difference
        co2_diff = abs(emissions_1.total_co2_tonnes - emissions_2.total_co2_tonnes)
        co2_diff_pct = abs(100 * (emissions_1.total_co2_tonnes - emissions_2.total_co2_tonnes) / 
                      max(emissions_1.total_co2_tonnes, emissions_2.total_co2_tonnes))
        
        lower_emissions = result1.vehicle_name if emissions_1.total_co2_tonnes < emissions_2.total_co2_tonnes else result2.vehicle_name
        
        emissions_html = f"""
        <div class="comparison-section emissions">
            <h4>Emissions Comparison</h4>
            <div class="comparison-row">
                <div class="comparison-cell"><span class="label">Total CO₂:</span> {co2_1}</div>
                <div class="comparison-cell"><span class="label">Total CO₂:</span> {co2_2}</div>
            </div>
            <div class="comparison-row">
                <div class="comparison-cell"><span class="label">CO₂ per km:</span> {co2_per_km_1}</div>
                <div class="comparison-cell"><span class="label">CO₂ per km:</span> {co2_per_km_2}</div>
            </div>
            <div class="comparison-insight">
                <span class="highlight">{lower_emissions}</span> produces <span class="highlight">{co2_diff:.1f} tonnes</span> 
                ({co2_diff_pct:.1f}%) less CO₂ over the vehicle lifetime
            </div>
        </div>
        """
    
    # Build the HTML with component costs
    from tco_model.terminology import UI_COMPONENT_KEYS, UI_COMPONENT_LABELS
    
    component_rows = ""
    for component in UI_COMPONENT_KEYS:
        # Skip residual value for better display
        if component == "residual_value":
            continue
            
        # Get component values
        component_value1 = calculator.get_component_value(result1, component)
        component_value2 = calculator.get_component_value(result2, component)
        
        # Format values
        formatted_value1 = format_currency(component_value1)
        formatted_value2 = format_currency(component_value2)
        
        # Get component label
        component_label = UI_COMPONENT_LABELS.get(component, component.replace("_", " ").title())
        
        # Add component row
        component_rows += f"""
        <div class="comparison-row">
            <div class="comparison-cell"><span class="label">{component_label}:</span> {formatted_value1}</div>
            <div class="comparison-cell"><span class="label">{component_label}:</span> {formatted_value2}</div>
        </div>
        """
    
    # Build the complete HTML
    html = f"""
    <div class="side-by-side-comparison">
        <div class="comparison-header">
            <div class="vehicle-name">{result1.vehicle_name}</div>
            <div class="vehicle-name">{result2.vehicle_name}</div>
        </div>
        
        <div class="comparison-section tco">
            <h4>TCO Comparison</h4>
            <div class="comparison-row">
                <div class="comparison-cell"><span class="label">Total TCO:</span> {result1_tco}</div>
                <div class="comparison-cell"><span class="label">Total TCO:</span> {result2_tco}</div>
            </div>
            <div class="comparison-row">
                <div class="comparison-cell"><span class="label">Cost per km:</span> {result1_lcod}/km</div>
                <div class="comparison-cell"><span class="label">Cost per km:</span> {result2_lcod}/km</div>
            </div>
            <div class="comparison-insight">
                <span class="highlight">{cheaper_vehicle}</span> is <span class="highlight">{tco_diff_pct}</span> 
                {cost_diff_indicator} ({tco_diff})
            </div>
        </div>
        
        {emissions_html}
        
        <div class="comparison-section components">
            <h4>Cost Components</h4>
            {component_rows}
        </div>
    </div>
    """
    
    return html 