"""
Live Preview Results Module

This module provides optimized results display for the side-by-side layout mode.
"""

import streamlit as st
from typing import Dict, Any, Optional, List
import numpy as np
import plotly.graph_objects as go

from tco_model.models import TCOOutput, ComparisonResult
from utils.helpers import format_currency, format_percentage
from ui.results.charts import (
    create_cumulative_tco_chart,
    create_annual_costs_chart,
    create_cost_components_chart
)
from ui.results.utils import generate_results_export
from ui.results.metrics import render_key_metrics_panel
from ui.results.environmental import render_environmental_impact


def display_results_in_live_mode(results: Dict[str, TCOOutput], comparison: ComparisonResult, 
                                selected_parameter: Optional[str] = None):
    """
    Display results optimized for live preview mode with sidebar+main layout
    
    Args:
        results: Dictionary of TCO result objects
        comparison: Comparison result object
        selected_parameter: Optional parameter to show impact analysis for
    """
    # Get results for each vehicle
    result1 = results["vehicle_1"]
    result2 = results["vehicle_2"]
    
    # Use full width of main panel (since sidebar is used for config)
    st.markdown("## TCO Analysis Results")
    
    # Create dashboard controls in a single row
    control_cols = st.columns([3, 1, 1])
    with control_cols[0]:
        st.markdown(f"Comparing **{result1.vehicle_name}** vs **{result2.vehicle_name}**")
    
    with control_cols[1]:
        view_mode = st.selectbox(
            "View",
            options=["Summary", "Detailed", "Parameter Impact"],
            key="live_view_mode",
            label_visibility="collapsed"
        )
    
    with control_cols[2]:
        st.download_button(
            "Export",
            data=generate_results_export(results, comparison),
            file_name="tco_analysis.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    # Display key metrics panel at top
    render_key_metrics_panel(results, comparison)
    
    # Render view based on selected mode
    if view_mode == "Summary":
        render_summary_view(results, comparison)
    elif view_mode == "Detailed":
        render_detailed_view(results, comparison)
    elif view_mode == "Parameter Impact":
        render_parameter_impact_view(results, comparison, selected_parameter)


def render_summary_view(results: Dict[str, TCOOutput], comparison: ComparisonResult):
    """
    Render the summary view with key visualizations
    
    Args:
        results: Dictionary of TCO result objects
        comparison: Comparison result object
    """
    # Get results for each vehicle
    result1 = results["vehicle_1"]
    result2 = results["vehicle_2"]
    
    # Create two-column layout for charts
    cols = st.columns(2)
    
    with cols[0]:
        # Cumulative TCO chart
        st.subheader("Cumulative TCO Over Time")
        cumulative_chart = create_cumulative_tco_chart(
            result1, 
            result2,
            show_breakeven=True,
            height=400
        )
        st.plotly_chart(cumulative_chart, use_container_width=True, 
                      config={'displayModeBar': False})
    
    with cols[1]:
        # Component breakdown chart
        st.subheader("Cost Component Breakdown")
        components_chart = create_cost_components_chart(
            result1, 
            result2,
            comparison,
            stacked=True,
            height=400
        )
        st.plotly_chart(components_chart, use_container_width=True,
                      config={'displayModeBar': False})
    
    # Annual costs chart in full width
    st.subheader("Annual Costs")
    annual_chart = create_annual_costs_chart(
        result1,
        result2,
        show_components=True,
        stacked=True,
        height=350
    )
    st.plotly_chart(annual_chart, use_container_width=True,
                  config={'displayModeBar': False})


def render_detailed_view(results: Dict[str, TCOOutput], comparison: ComparisonResult):
    """
    Render the detailed view with multiple analysis perspectives
    
    Args:
        results: Dictionary of TCO result objects
        comparison: Comparison result object
    """
    # Create tabs for different analysis perspectives
    detail_tabs = st.tabs([
        "Financial", 
        "Component Breakdown", 
        "Annual Timeline",
        "Environmental"
    ])
    
    # Implement each tab with detailed analysis
    with detail_tabs[0]:
        render_financial_details(results, comparison)
    
    with detail_tabs[1]:
        render_component_details(results, comparison)
    
    with detail_tabs[2]:
        render_timeline_details(results, comparison)
    
    with detail_tabs[3]:
        render_environmental_details(results)


def render_financial_details(results: Dict[str, TCOOutput], comparison: ComparisonResult):
    """
    Render financial details analysis
    
    Args:
        results: Dictionary of TCO result objects
        comparison: Comparison result object
    """
    # Get results for each vehicle
    result1 = results["vehicle_1"]
    result2 = results["vehicle_2"]
    
    # Create financial summary
    st.subheader("Financial Summary")
    
    # Add key metrics in columns
    metric_cols = st.columns(3)
    
    with metric_cols[0]:
        st.metric(
            "Total TCO Difference",
            format_currency(abs(comparison.tco_difference)),
            f"{format_percentage(comparison.tco_percentage)} {'lower' if comparison.cheaper_option == 1 else 'higher'}"
        )
    
    with metric_cols[1]:
        st.metric(
            "Cost per Kilometer",
            f"{format_currency(result1.lcod)}/km vs {format_currency(result2.lcod)}/km",
            f"{format_currency(abs(comparison.lcod_difference))}/km difference"
        )
    
    with metric_cols[2]:
        # Show payback if available
        if hasattr(comparison, "payback_years") and comparison.payback_years:
            st.metric(
                "Payback Period",
                f"{comparison.payback_years:.1f} years",
                f"{(comparison.payback_years/result1.analysis_period_years*100):.1f}% of lifetime"
            )
        else:
            st.metric(
                "Annual Cost Difference",
                format_currency(abs(comparison.tco_difference / result1.analysis_period_years)),
                "per year"
            )
    
    # Create cumulative TCO chart
    st.subheader("Cumulative TCO Over Time")
    cumulative_chart = create_cumulative_tco_chart(
        result1, 
        result2,
        show_breakeven=True,
        height=400
    )
    st.plotly_chart(cumulative_chart, use_container_width=True, config={'displayModeBar': False})
    
    # Show detailed financial data
    st.subheader("Detailed Financial Comparison")
    
    # Create financial comparison table
    financial_data = {
        "Metric": [
            "Total TCO (NPV)",
            "Cost per Kilometer",
            "Acquisition Cost",
            "Residual Value",
            "Operating Cost",
            "Maintenance Cost",
            "Energy Cost",
            "Annual TCO"
        ],
        result1.vehicle_name: [
            format_currency(result1.total_tco),
            f"{format_currency(result1.lcod)}/km",
            format_currency(result1.acquisition_cost),
            format_currency(result1.residual_value),
            format_currency(result1.operating_cost),
            format_currency(result1.maintenance_cost),
            format_currency(result1.energy_cost),
            format_currency(result1.total_tco / result1.analysis_period_years)
        ],
        result2.vehicle_name: [
            format_currency(result2.total_tco),
            f"{format_currency(result2.lcod)}/km",
            format_currency(result2.acquisition_cost),
            format_currency(result2.residual_value),
            format_currency(result2.operating_cost),
            format_currency(result2.maintenance_cost),
            format_currency(result2.energy_cost),
            format_currency(result2.total_tco / result2.analysis_period_years)
        ],
        "Difference": [
            format_currency(result1.total_tco - result2.total_tco),
            f"{format_currency(result1.lcod - result2.lcod)}/km",
            format_currency(result1.acquisition_cost - result2.acquisition_cost),
            format_currency(result1.residual_value - result2.residual_value),
            format_currency(result1.operating_cost - result2.operating_cost),
            format_currency(result1.maintenance_cost - result2.maintenance_cost),
            format_currency(result1.energy_cost - result2.energy_cost),
            format_currency((result1.total_tco - result2.total_tco) / result1.analysis_period_years)
        ]
    }
    
    # Display as a dataframe
    import pandas as pd
    st.dataframe(pd.DataFrame(financial_data), use_container_width=True)


def render_component_details(results: Dict[str, TCOOutput], comparison: ComparisonResult):
    """
    Render component breakdown details
    
    Args:
        results: Dictionary of TCO result objects
        comparison: Comparison result object
    """
    # Component breakdown
    st.subheader("Cost Component Breakdown")
    
    # Get component chart
    components_chart = create_cost_components_chart(
        results["vehicle_1"], 
        results["vehicle_2"],
        comparison,
        stacked=True,
        height=400
    )
    st.plotly_chart(components_chart, use_container_width=True, config={'displayModeBar': False})
    
    # Add view options
    view_cols = st.columns(3)
    with view_cols[0]:
        chart_type = st.radio(
            "Chart Type",
            options=["Stacked", "Grouped", "Pie"],
            horizontal=True,
            key="component_chart_type"
        )
    
    # Update chart based on selection
    if chart_type == "Grouped":
        grouped_chart = create_cost_components_chart(
            results["vehicle_1"], 
            results["vehicle_2"],
            comparison,
            stacked=False,
            height=400
        )
        st.plotly_chart(grouped_chart, use_container_width=True, config={'displayModeBar': False})
    elif chart_type == "Pie":
        # Import pie chart function
        from ui.results.charts import create_cost_components_pie_chart
        
        pie_chart = create_cost_components_pie_chart(
            results["vehicle_1"], 
            results["vehicle_2"],
            comparison,
            height=400
        )
        st.plotly_chart(pie_chart, use_container_width=True, config={'displayModeBar': False})


def render_timeline_details(results: Dict[str, TCOOutput], comparison: ComparisonResult):
    """
    Render timeline details analysis
    
    Args:
        results: Dictionary of TCO result objects
        comparison: Comparison result object
    """
    # Timeline details
    st.subheader("Annual Timeline Analysis")
    
    # Create annual costs chart
    annual_chart = create_annual_costs_chart(
        results["vehicle_1"],
        results["vehicle_2"],
        show_components=True,
        stacked=True,
        height=400
    )
    st.plotly_chart(annual_chart, use_container_width=True, config={'displayModeBar': False})
    
    # Add component toggle
    show_components = st.checkbox("Show component breakdown", value=True, key="annual_show_components")
    view_type = st.radio("Chart type", ["Stacked", "Side-by-side"], horizontal=True, key="annual_chart_type")
    
    # Update chart based on selection
    if not show_components or view_type == "Side-by-side":
        updated_chart = create_annual_costs_chart(
            results["vehicle_1"],
            results["vehicle_2"],
            show_components=show_components,
            stacked=(view_type == "Stacked"),
            height=400
        )
        st.plotly_chart(updated_chart, use_container_width=True, config={'displayModeBar': False})


def render_environmental_details(results: Dict[str, TCOOutput]):
    """
    Render environmental impact details
    
    Args:
        results: Dictionary of TCO result objects
    """
    # Use the existing environmental impact module
    render_environmental_impact(results)


def render_parameter_impact_view(results: Dict[str, TCOOutput], comparison: ComparisonResult,
                                selected_parameter: Optional[str] = None):
    """
    Render the parameter impact analysis view
    
    Args:
        results: Dictionary of TCO result objects
        comparison: Comparison result object
        selected_parameter: The parameter to analyse
    """
    st.subheader("Parameter Impact Analysis")
    
    if selected_parameter:
        # If parameter is already selected, show its impact
        show_parameter_impact(selected_parameter, results, comparison)
    else:
        # Otherwise show parameter selection interface
        st.info("Select a parameter to analyse its impact on the TCO results.")
        
        # Display parameter categories for selection
        parameter_cats = st.tabs([
            "Vehicle Parameters",
            "Operational Parameters",
            "Economic Parameters",
            "Financing Parameters"
        ])
        
        with parameter_cats[0]:
            parameter_buttons = st.columns(3)
            with parameter_buttons[0]:
                if st.button("Vehicle Purchase Price"):
                    st.session_state["parameter_to_analyse"] = "vehicle.purchase_price"
                    show_parameter_impact("vehicle.purchase_price", results, comparison)
            
            with parameter_buttons[1]:
                if st.button("Residual Value"):
                    st.session_state["parameter_to_analyse"] = "vehicle.residual_value.year_5_range"
                    show_parameter_impact("vehicle.residual_value.year_5_range", results, comparison)
            
            with parameter_buttons[2]:
                if st.button("Vehicle Efficiency"):
                    parameter = "vehicle.energy_consumption.base_rate" if results["vehicle_1"].vehicle_type == "bet" else "vehicle.fuel_consumption.base_rate"
                    st.session_state["parameter_to_analyse"] = parameter
                    show_parameter_impact(parameter, results, comparison)
        
        with parameter_cats[1]:
            parameter_buttons = st.columns(3)
            with parameter_buttons[0]:
                if st.button("Annual Distance"):
                    st.session_state["parameter_to_analyse"] = "operational.annual_distance_km"
                    show_parameter_impact("operational.annual_distance_km", results, comparison)
            
            with parameter_buttons[1]:
                if st.button("Analysis Period"):
                    st.session_state["parameter_to_analyse"] = "economic.analysis_period_years"
                    show_parameter_impact("economic.analysis_period_years", results, comparison)
        
        with parameter_cats[2]:
            parameter_buttons = st.columns(3)
            with parameter_buttons[0]:
                if st.button("Diesel Price"):
                    st.session_state["parameter_to_analyse"] = "economic.diesel_price_aud_per_l"
                    show_parameter_impact("economic.diesel_price_aud_per_l", results, comparison)
            
            with parameter_buttons[1]:
                if st.button("Electricity Price"):
                    st.session_state["parameter_to_analyse"] = "economic.electricity_price_aud_per_kwh"
                    show_parameter_impact("economic.electricity_price_aud_per_kwh", results, comparison)
            
            with parameter_buttons[2]:
                if st.button("Discount Rate"):
                    st.session_state["parameter_to_analyse"] = "economic.discount_rate_real"
                    show_parameter_impact("economic.discount_rate_real", results, comparison)


def show_parameter_impact(parameter: str, results: Dict[str, TCOOutput], 
                         comparison: ComparisonResult):
    """
    Show the impact of changing a specific parameter using actual sensitivity analysis
    
    Args:
        parameter: The parameter to analyse
        results: Dictionary of TCO result objects
        comparison: Comparison result object
    """
    # Create a more readable parameter name for display
    parameter_display_name = parameter.split('.')[-1].replace('_', ' ').title()
    st.markdown(f"### Impact of {parameter_display_name}")
    
    # Get calculator instance
    from tco_model.calculator import TCOCalculator
    calculator = TCOCalculator()
    
    # Get scenarios from results
    scenario1 = results["vehicle_1"].scenario
    scenario2 = results["vehicle_2"].scenario
    
    if not scenario1 or not scenario2:
        st.error("Scenario data not available for sensitivity analysis.")
        return
    
    # Define variation range based on parameter type
    try:
        original_value1 = get_parameter_value(scenario1, parameter)
        original_value2 = get_parameter_value(scenario2, parameter)
        
        if not original_value1 or not original_value2:
            st.error(f"Parameter {parameter} not found in scenario data.")
            return
        
        # Create variation ranges appropriate for the parameter
        variations1 = create_variation_range(parameter, original_value1)
        variations2 = create_variation_range(parameter, original_value2)
        
        # Perform sensitivity analysis
        with st.spinner("Calculating sensitivity..."):
            sensitivity1 = calculator.perform_sensitivity_analysis(
                scenario1,
                parameter,
                variations1
            )
            
            sensitivity2 = calculator.perform_sensitivity_analysis(
                scenario2,
                parameter,
                variations2
            )
        
        # Create parameter information for visualization
        parameter_info = {
            "name": parameter_display_name,
            "unit": sensitivity1["unit"],
            "variations1": variations1,
            "variations2": variations2,
            "has_tipping_point": determine_has_tipping_point(sensitivity1, sensitivity2)
        }
        
        # Create visualization
        fig = create_parameter_impact_chart(sensitivity1, sensitivity2, parameter_info)
        st.plotly_chart(fig, use_container_width=True)
        
        # Show tipping point if it exists
        tipping_point = calculate_tipping_point(sensitivity1, sensitivity2)
        if parameter_info["has_tipping_point"] and tipping_point:
            st.info(f"""
            **Tipping Point**: When {parameter_display_name} reaches {tipping_point:.2f} {parameter_info['unit']}, 
            the more cost-effective vehicle switches.
            """)
        
        # Show insights
        st.markdown("### Key Insights")
        insights = generate_sensitivity_insights(sensitivity1, sensitivity2, results)
        st.markdown(insights)
        
        # Add interactive adjustment
        st.markdown("### Adjust Parameter Value")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            # Create adjustment slider with appropriate range and step
            min_val = min(min(variations1), min(variations2))
            max_val = max(max(variations1), max(variations2))
            step = (max_val - min_val) / 20
            
            adjusted_value1 = st.slider(
                f"{results['vehicle_1'].vehicle_name} {parameter_display_name}",
                min_value=min_val,
                max_value=max_val,
                value=original_value1,
                step=step,
                key=f"slider_{parameter}_1"
            )
            
            adjusted_value2 = st.slider(
                f"{results['vehicle_2'].vehicle_name} {parameter_display_name}",
                min_value=min_val,
                max_value=max_val,
                value=original_value2,
                step=step,
                key=f"slider_{parameter}_2"
            )
        
        with col2:
            if st.button("Recalculate", key=f"recalc_{parameter}"):
                st.session_state["recalculating"] = True
                st.info("Recalculation would be performed here in a real implementation.")
                # In a full implementation, this would trigger recalculation
                # and update the results with the new parameter values
    
    except Exception as e:
        st.error(f"Error performing sensitivity analysis: {str(e)}")


def create_parameter_impact_chart(sensitivity1: Dict[str, Any], sensitivity2: Dict[str, Any], 
                                parameter_info: Dict[str, Any]) -> go.Figure:
    """
    Create chart visualizing parameter impact using actual sensitivity analysis results
    
    Args:
        sensitivity1: Sensitivity analysis results for vehicle 1
        sensitivity2: Sensitivity analysis results for vehicle 2
        parameter_info: Information about the parameter
        
    Returns:
        go.Figure: Parameter impact chart
    """
    # Create figure
    fig = go.Figure()
    
    # Get variations and TCO values
    variations1 = sensitivity1["variation_values"]
    tco_values1 = sensitivity1["tco_values"]
    
    variations2 = sensitivity2["variation_values"]
    tco_values2 = sensitivity2["tco_values"]
    
    # Get vehicle names
    vehicle1_name = sensitivity1.get("vehicle_name", "Vehicle 1")
    vehicle2_name = sensitivity2.get("vehicle_name", "Vehicle 2")
    
    # Add traces for both vehicles
    fig.add_trace(go.Scatter(
        x=variations1,
        y=tco_values1,
        mode="lines+markers",
        name=vehicle1_name,
        line=dict(color="#1f77b4", width=3)
    ))
    
    fig.add_trace(go.Scatter(
        x=variations2,
        y=tco_values2,
        mode="lines+markers",
        name=vehicle2_name,
        line=dict(color="#ff7f0e", width=3)
    ))
    
    # Add current value markers
    fig.add_trace(go.Scatter(
        x=[sensitivity1["original_value"]],
        y=[sensitivity1["original_tco"]],
        mode="markers",
        marker=dict(size=12, symbol="circle", color="#1f77b4"),
        name=f"Current {vehicle1_name}",
        hoverinfo="text",
        hovertext=f"Current value: {sensitivity1['original_value']:.2f} {parameter_info['unit']}"
    ))
    
    fig.add_trace(go.Scatter(
        x=[sensitivity2["original_value"]],
        y=[sensitivity2["original_tco"]],
        mode="markers",
        marker=dict(size=12, symbol="circle", color="#ff7f0e"),
        name=f"Current {vehicle2_name}",
        hoverinfo="text",
        hovertext=f"Current value: {sensitivity2['original_value']:.2f} {parameter_info['unit']}"
    ))
    
    # Add tipping point if it exists
    if parameter_info["has_tipping_point"]:
        tipping_point = calculate_tipping_point(sensitivity1, sensitivity2)
        if tipping_point:
            # Interpolate to find approximate TCO at tipping point
            tco_at_tipping = np.interp(tipping_point, variations1, tco_values1)
            
            fig.add_trace(go.Scatter(
                x=[tipping_point],
                y=[tco_at_tipping],
                mode="markers",
                marker=dict(size=14, symbol="star", color="green"),
                name="Breakeven Point",
                hoverinfo="text",
                hovertext=f"Breakeven at {tipping_point:.2f} {parameter_info['unit']}"
            ))
    
    # Update layout
    fig.update_layout(
        title=f"TCO Sensitivity to {parameter_info['name']}",
        xaxis_title=f"{parameter_info['name']} ({parameter_info['unit']})",
        yaxis_title="Total Cost of Ownership ($)",
        height=400,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig


def get_parameter_value(scenario, parameter: str):
    """Get the value of a parameter from a scenario using dot notation."""
    current_obj = scenario
    for attr_name in parameter.split('.'):
        if hasattr(current_obj, attr_name):
            current_obj = getattr(current_obj, attr_name)
        else:
            return None
    return current_obj


def create_variation_range(parameter: str, original_value: float) -> List[float]:
    """Create appropriate variation range based on parameter type and original value."""
    # Economic parameters like prices and rates
    if "price" in parameter or "rate" in parameter:
        # Vary by percentage from -50% to +50%
        return [original_value * p for p in [0.5, 0.75, 0.9, 1.0, 1.1, 1.25, 1.5]]
    
    # Distance parameters
    elif "distance" in parameter:
        # Vary by percentage from -50% to +50%
        return [original_value * p for p in [0.5, 0.75, 0.9, 1.0, 1.1, 1.25, 1.5]]
    
    # Time period parameters
    elif "period" in parameter or "years" in parameter:
        # Vary by adding/subtracting years
        return [max(1, original_value + y) for y in [-5, -3, -1, 0, 1, 3, 5]]
    
    # Efficiency parameters
    elif "fuel_consumption" in parameter or "energy_consumption" in parameter:
        # Vary by percentage from -30% to +30% (improved to worse efficiency)
        return [original_value * p for p in [0.7, 0.85, 0.95, 1.0, 1.05, 1.15, 1.3]]
    
    # Default variation
    else:
        # General 20% variations
        return [original_value * p for p in [0.8, 0.9, 0.95, 1.0, 1.05, 1.1, 1.2]]


def determine_has_tipping_point(sensitivity1: Dict[str, Any], sensitivity2: Dict[str, Any]) -> bool:
    """Determine if there's a tipping point in the sensitivity analysis."""
    tco_diff = []
    
    # Use the shorter variations list
    min_len = min(len(sensitivity1["tco_values"]), len(sensitivity2["tco_values"]))
    
    for i in range(min_len):
        tco_diff.append(sensitivity1["tco_values"][i] - sensitivity2["tco_values"][i])
    
    # Check if tco_diff changes sign (crosses zero)
    sign_changes = 0
    for i in range(1, len(tco_diff)):
        if tco_diff[i-1] * tco_diff[i] <= 0:  # Zero or sign change
            sign_changes += 1
    
    return sign_changes > 0


def calculate_tipping_point(sensitivity1: Dict[str, Any], sensitivity2: Dict[str, Any]) -> Optional[float]:
    """Calculate the tipping point where TCO curves intersect."""
    # Check if there's a potential tipping point
    if not determine_has_tipping_point(sensitivity1, sensitivity2):
        return None
    
    # Combine data for interpolation
    x1 = np.array(sensitivity1["variation_values"])
    y1 = np.array(sensitivity1["tco_values"])
    
    x2 = np.array(sensitivity2["variation_values"])
    y2 = np.array(sensitivity2["tco_values"])
    
    # Create interpolation functions
    from scipy.interpolate import interp1d
    
    # Ensure x values are sorted for interpolation
    sort_idx1 = np.argsort(x1)
    x1, y1 = x1[sort_idx1], y1[sort_idx1]
    
    sort_idx2 = np.argsort(x2)
    x2, y2 = x2[sort_idx2], y2[sort_idx2]
    
    # Create interpolation functions
    f1 = interp1d(x1, y1, kind='linear', fill_value='extrapolate')
    f2 = interp1d(x2, y2, kind='linear', fill_value='extrapolate')
    
    # Find intersection using a simple approach
    # Create a common x range
    x_min = max(x1.min(), x2.min())
    x_max = min(x1.max(), x2.max())
    
    if x_min >= x_max:
        # No overlap in parameter ranges
        return None
    
    # Create a fine grid of x values to find crossover
    x_grid = np.linspace(x_min, x_max, 1000)
    y1_grid = f1(x_grid)
    y2_grid = f2(x_grid)
    
    # Find where difference changes sign
    diff = y1_grid - y2_grid
    for i in range(1, len(diff)):
        if diff[i-1] * diff[i] <= 0:  # Sign change or zero
            # Linear interpolation for more precise intersection
            x_intersect = x_grid[i-1] + (-diff[i-1]) * (x_grid[i] - x_grid[i-1]) / (diff[i] - diff[i-1])
            return x_intersect
    
    return None


def generate_sensitivity_insights(sensitivity1: Dict[str, Any], sensitivity2: Dict[str, Any], 
                               results: Dict[str, TCOOutput]) -> str:
    """Generate insights from sensitivity analysis results."""
    vehicle1_name = results["vehicle_1"].vehicle_name
    vehicle2_name = results["vehicle_2"].vehicle_name
    parameter_name = sensitivity1["parameter"].split('.')[-1].replace('_', ' ').title()
    
    # Calculate sensitivities (percent change in TCO for percent change in parameter)
    orig_value1 = sensitivity1["original_value"]
    orig_tco1 = sensitivity1["original_tco"]
    
    orig_value2 = sensitivity2["original_value"]
    orig_tco2 = sensitivity2["original_tco"]
    
    # Calculate elasticity for a 10% increase in parameter
    try:
        high_idx1 = sensitivity1["variation_values"].index(next(filter(lambda x: x > orig_value1, sensitivity1["variation_values"])))
        high_value1 = sensitivity1["variation_values"][high_idx1]
        high_tco1 = sensitivity1["tco_values"][high_idx1]
        
        value_pct_change1 = (high_value1 - orig_value1) / orig_value1 * 100
        tco_pct_change1 = (high_tco1 - orig_tco1) / orig_tco1 * 100
        
        elasticity1 = tco_pct_change1 / value_pct_change1 if value_pct_change1 != 0 else 0
        
        high_idx2 = sensitivity2["variation_values"].index(next(filter(lambda x: x > orig_value2, sensitivity2["variation_values"])))
        high_value2 = sensitivity2["variation_values"][high_idx2]
        high_tco2 = sensitivity2["tco_values"][high_idx2]
        
        value_pct_change2 = (high_value2 - orig_value2) / orig_value2 * 100
        tco_pct_change2 = (high_tco2 - orig_tco2) / orig_tco2 * 100
        
        elasticity2 = tco_pct_change2 / value_pct_change2 if value_pct_change2 != 0 else 0
    except (ValueError, IndexError):
        elasticity1 = 0
        elasticity2 = 0
    
    # Generate insights based on elasticity comparison
    insights = []
    
    # Which vehicle is more sensitive
    if abs(elasticity1) > abs(elasticity2) * 1.2:
        insights.append(f"* The {vehicle1_name} TCO is {abs(elasticity1):.1f}x more sensitive to changes in {parameter_name} than the {vehicle2_name}.")
    elif abs(elasticity2) > abs(elasticity1) * 1.2:
        insights.append(f"* The {vehicle2_name} TCO is {abs(elasticity2):.1f}x more sensitive to changes in {parameter_name} than the {vehicle1_name}.")
    else:
        insights.append(f"* Both vehicles show similar sensitivity to changes in {parameter_name}.")
    
    # Direction of impact
    if elasticity1 > 0:
        insights.append(f"* Increasing {parameter_name} will increase the {vehicle1_name} TCO.")
    else:
        insights.append(f"* Increasing {parameter_name} will decrease the {vehicle1_name} TCO.")
        
    if elasticity2 > 0:
        insights.append(f"* Increasing {parameter_name} will increase the {vehicle2_name} TCO.")
    else:
        insights.append(f"* Increasing {parameter_name} will decrease the {vehicle2_name} TCO.")
    
    # Tipping point insight
    tipping_point = calculate_tipping_point(sensitivity1, sensitivity2)
    if tipping_point:
        orig_diff = orig_tco2 - orig_tco1
        currently_cheaper = vehicle1_name if orig_diff > 0 else vehicle2_name
        tipping_difference = abs(tipping_point - orig_value1) / orig_value1 * 100
        
        insights.append(f"* The breakeven point occurs at a {parameter_name} value of {tipping_point:.2f} {sensitivity1['unit']}.")
        insights.append(f"* This represents a {tipping_difference:.1f}% {'increase' if tipping_point > orig_value1 else 'decrease'} from the current {vehicle1_name} value.")
    else:
        insights.append(f"* No breakeven point was found - the {vehicle1_name if orig_tco2 > orig_tco1 else vehicle2_name} remains more cost-effective across all analyzed {parameter_name} values.")
    
    return "\n".join(insights) 