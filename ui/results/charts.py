"""
Results Charts Module

This module renders the UI components for displaying TCO results as interactive charts.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from typing import Dict, Any, List

from tco_model.models import TCOOutput, ComparisonResult


def render_charts(results: Dict[str, TCOOutput], comparison: ComparisonResult):
    """
    Render the interactive charts for TCO results.
    
    Args:
        results: Dictionary containing TCO results for each vehicle
        comparison: The comparison result between the two vehicles
    """
    # Extract results
    result1 = results["vehicle_1"]
    result2 = results["vehicle_2"]
    
    # Create chart tabs
    chart_tabs = st.tabs([
        "Cumulative TCO",
        "Annual Costs",
        "Cost Components",
        "Sensitivity Analysis"
    ])
    
    # Cumulative TCO chart
    with chart_tabs[0]:
        st.subheader("Cumulative TCO Over Time")
        cumulative_chart = create_cumulative_tco_chart(result1, result2)
        st.plotly_chart(cumulative_chart, use_container_width=True)
    
    # Annual costs chart
    with chart_tabs[1]:
        st.subheader("Annual Costs")
        annual_costs_chart = create_annual_costs_chart(result1, result2)
        st.plotly_chart(annual_costs_chart, use_container_width=True)
    
    # Cost components chart
    with chart_tabs[2]:
        st.subheader("Cost Component Comparison")
        components_chart = create_cost_components_chart(result1, result2, comparison)
        st.plotly_chart(components_chart, use_container_width=True)
    
    # Sensitivity analysis (placeholder)
    with chart_tabs[3]:
        st.subheader("Sensitivity Analysis")
        st.markdown("Sensitivity analysis functionality will be implemented in a future version.")
        
        # Placeholder for sensitivity controls
        st.slider(
            "Electricity Price Adjustment (%)",
            min_value=-50,
            max_value=50,
            value=0,
            step=5,
            key="sensitivity_electricity_price",
        )
        
        st.slider(
            "Diesel Price Adjustment (%)",
            min_value=-50,
            max_value=50,
            value=0,
            step=5,
            key="sensitivity_diesel_price",
        )
        
        st.button("Recalculate with Sensitivity Adjustments")


def create_cumulative_tco_chart(result1: TCOOutput, result2: TCOOutput) -> go.Figure:
    """
    Create a cumulative TCO chart showing how TCO accumulates over time.
    
    Args:
        result1: TCO result for the first vehicle
        result2: TCO result for the second vehicle
        
    Returns:
        go.Figure: The plotly figure object for the chart
    """
    # Get the analysis period and vehicle names
    years = range(result1.scenario.operational.analysis_period)
    vehicle1_name = result1.scenario.vehicle.name
    vehicle2_name = result2.scenario.vehicle.name
    
    # Calculate cumulative costs for both vehicles
    v1_cumulative = np.cumsum([result1.annual_costs.total[year] for year in years])
    v2_cumulative = np.cumsum([result2.annual_costs.total[year] for year in years])
    
    # Create the figure
    fig = go.Figure()
    
    # Add traces for both vehicles
    fig.add_trace(go.Scatter(
        x=list(years),
        y=v1_cumulative,
        mode="lines+markers",
        name=vehicle1_name,
        line=dict(color="#1f77b4", width=3),
    ))
    
    fig.add_trace(go.Scatter(
        x=list(years),
        y=v2_cumulative,
        mode="lines+markers",
        name=vehicle2_name,
        line=dict(color="#ff7f0e", width=3),
    ))
    
    # Update layout
    fig.update_layout(
        xaxis_title="Year",
        yaxis_title="Cumulative Cost (AUD)",
        legend_title="Vehicle",
        hovermode="x unified",
    )
    
    # Add break-even point annotation if applicable
    for i in range(1, len(years)):
        if (v1_cumulative[i-1] <= v2_cumulative[i-1] and v1_cumulative[i] > v2_cumulative[i]) or \
           (v1_cumulative[i-1] >= v2_cumulative[i-1] and v1_cumulative[i] < v2_cumulative[i]):
            # Linear interpolation to find more precise break-even point
            t = (v2_cumulative[i-1] - v1_cumulative[i-1]) / ((v1_cumulative[i] - v1_cumulative[i-1]) - (v2_cumulative[i] - v2_cumulative[i-1]))
            break_even_year = i-1 + t
            break_even_cost = v1_cumulative[i-1] + t * (v1_cumulative[i] - v1_cumulative[i-1])
            
            fig.add_annotation(
                x=break_even_year,
                y=break_even_cost,
                text=f"Break-even at {break_even_year:.1f} years",
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=2,
                ax=50,
                ay=-50,
            )
            break
    
    return fig


def create_annual_costs_chart(result1: TCOOutput, result2: TCOOutput) -> go.Figure:
    """
    Create a chart showing the annual costs for both vehicles side by side.
    
    Args:
        result1: TCO result for the first vehicle
        result2: TCO result for the second vehicle
        
    Returns:
        go.Figure: The plotly figure object for the chart
    """
    # Get the analysis period and vehicle names
    years = range(result1.scenario.operational.analysis_period)
    vehicle1_name = result1.scenario.vehicle.name
    vehicle2_name = result2.scenario.vehicle.name
    
    # Create a DataFrame for the chart
    annual_data = {
        "Year": list(years) * 2,
        "Vehicle": [vehicle1_name] * len(years) + [vehicle2_name] * len(years),
        "Annual Cost": [result1.annual_costs.total[year] for year in years] + 
                       [result2.annual_costs.total[year] for year in years],
    }
    
    annual_df = pd.DataFrame(annual_data)
    
    # Create the figure using plotly express
    fig = px.bar(
        annual_df,
        x="Year",
        y="Annual Cost",
        color="Vehicle",
        barmode="group",
        title="Annual Costs by Year",
        labels={"Annual Cost": "Annual Cost (AUD)"},
    )
    
    # Update layout
    fig.update_layout(
        legend_title="Vehicle",
        hovermode="x unified",
    )
    
    return fig


def create_cost_components_chart(result1: TCOOutput, result2: TCOOutput, comparison: ComparisonResult) -> go.Figure:
    """
    Create a chart showing the cost component breakdown for both vehicles.
    
    Args:
        result1: TCO result for the first vehicle
        result2: TCO result for the second vehicle
        comparison: The comparison result between the two vehicles
        
    Returns:
        go.Figure: The plotly figure object for the chart
    """
    # Get vehicle names
    vehicle1_name = result1.scenario.vehicle.name
    vehicle2_name = result2.scenario.vehicle.name
    
    # Define cost components and their labels
    cost_components = [
        "acquisition",
        "energy",
        "maintenance",
        "infrastructure",
        "battery_replacement",
        "insurance_registration",
        "taxes_levies",
    ]
    
    # Skip residual value as it's negative and handled separately
    
    cost_labels = [
        "Acquisition Costs",
        "Energy Costs",
        "Maintenance & Repair",
        "Infrastructure",
        "Battery Replacement",
        "Insurance & Registration",
        "Taxes & Levies",
    ]
    
    # Create the figure
    fig = go.Figure()
    
    # Add traces for positive cost components (stacked bar)
    for i, component in enumerate(cost_components):
        v1_value = max(0, getattr(result1.npv_costs, component))
        v2_value = max(0, getattr(result2.npv_costs, component))
        
        fig.add_trace(go.Bar(
            name=cost_labels[i],
            x=[vehicle1_name, vehicle2_name],
            y=[v1_value, v2_value],
            text=[f"${v1_value:,.0f}", f"${v2_value:,.0f}"],
            textposition="auto",
        ))
    
    # Add residual value as a separate bar (negative value)
    fig.add_trace(go.Bar(
        name="Residual Value",
        x=[vehicle1_name, vehicle2_name],
        y=[min(0, result1.npv_costs.residual_value), min(0, result2.npv_costs.residual_value)],
        text=[f"${result1.npv_costs.residual_value:,.0f}", f"${result2.npv_costs.residual_value:,.0f}"],
        textposition="auto",
        marker_color="green",
    ))
    
    # Add a total value marker
    fig.add_trace(go.Scatter(
        name="Total TCO",
        x=[vehicle1_name, vehicle2_name],
        y=[result1.total_tco, result2.total_tco],
        mode="markers+text",
        marker=dict(size=15, color="black", symbol="diamond"),
        text=[f"Total: ${result1.total_tco:,.0f}", f"Total: ${result2.total_tco:,.0f}"],
        textposition="top center",
    ))
    
    # Update layout
    fig.update_layout(
        barmode="stack",
        title="Cost Components (NPV)",
        yaxis_title="Cost (AUD)",
        legend_title="Cost Component",
        hovermode="x unified",
    )
    
    return fig 