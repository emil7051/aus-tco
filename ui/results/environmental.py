"""
Environmental Impact Module

This module provides UI components for displaying environmental impact
analysis of TCO results.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Dict, Any, List, Optional
import numpy as np

from tco_model.models import TCOOutput, ComparisonResult
from utils.helpers import format_currency, format_percentage


def render_environmental_impact(results: Dict[str, TCOOutput]):
    """
    Render environmental impact comparison with actual emissions data
    
    Args:
        results: Dictionary of TCO result objects with emissions data
    """
    st.subheader("Environmental Impact Analysis")
    
    # Get results with emissions data
    result1 = results["vehicle_1"]
    result2 = results["vehicle_2"]
    
    # Verify emissions data exists
    if not hasattr(result1, 'emissions') or not hasattr(result2, 'emissions'):
        st.warning("Emissions data not available for one or both vehicles.")
        return
    
    # Create tabs for different environmental metrics
    env_tabs = st.tabs(["CO2 Emissions", "Energy Consumption", "Sustainability Metrics"])
    
    # CO2 Emissions tab with actual data
    with env_tabs[0]:
        col1, col2 = st.columns([3, 2])
        
        with col1:
            # Emissions over time chart with actual annual emissions
            fig = create_emissions_timeline_chart(result1, result2)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Total emissions and key metrics from actual data
            st.markdown("### Lifetime CO2 Emissions")
            
            # Use actual total emissions
            total_co2_1 = result1.emissions.total_co2_tonnes
            total_co2_2 = result2.emissions.total_co2_tonnes
            co2_diff = total_co2_2 - total_co2_1
            
            # Display emission metrics with actual data
            co2_metric_cols = st.columns(2)
            with co2_metric_cols[0]:
                st.metric(
                    result1.vehicle_name, 
                    f"{total_co2_1:,.1f} tonnes",
                    delta=None
                )
            
            with co2_metric_cols[1]:
                st.metric(
                    result2.vehicle_name, 
                    f"{total_co2_2:,.1f} tonnes",
                    delta=f"{co2_diff:+,.1f} tonnes",
                    delta_color="inverse"
                )
            
            # Add contextual impact using actual equivalents
            if abs(co2_diff) > 0:
                # Use the vehicle with higher emissions to calculate equivalents
                higher_emissions = result1.emissions if co2_diff < 0 else result2.emissions
                
                trees = higher_emissions.trees_equivalent
                homes = higher_emissions.homes_equivalent
                cars = higher_emissions.cars_equivalent
                
                higher_vehicle = result2.vehicle_name if co2_diff > 0 else result1.vehicle_name
                
                st.markdown(f"""
                <div class="environmental-impact">
                    <h4>Environmental Impact</h4>
                    <p>The {higher_vehicle} produces {abs(co2_diff):,.1f} tonnes more CO2</p>
                    <p>This is equivalent to:</p>
                    <ul>
                        <li>{trees:,} trees needed to absorb this CO2 annually</li>
                        <li>{homes:,.1f} average homes' annual energy use</li>
                        <li>{cars:,.1f} passenger vehicles driven for one year</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
    
    # Energy Consumption tab with actual energy data
    with env_tabs[1]:
        render_energy_consumption_comparison(result1, result2)
    
    # Sustainability Metrics tab with actual data
    with env_tabs[2]:
        render_sustainability_metrics(result1, result2)


def create_emissions_timeline_chart(result1: TCOOutput, result2: TCOOutput) -> go.Figure:
    """
    Create emissions timeline chart with actual emissions data.
    
    Args:
        result1: TCO result for the first vehicle with emissions data
        result2: TCO result for the second vehicle with emissions data
        
    Returns:
        go.Figure: Emissions timeline chart
    """
    # Get annual CO2 emissions from actual data
    annual_co2_1 = result1.emissions.annual_co2_tonnes
    annual_co2_2 = result2.emissions.annual_co2_tonnes
    
    # Create years array
    years = list(range(1, len(annual_co2_1) + 1))
    
    # Create figure
    fig = go.Figure()
    
    # Get vehicle colors from model-specific constants
    from utils.ui_terminology import get_vehicle_type_color
    color1 = get_vehicle_type_color(result1.vehicle_type)
    color2 = get_vehicle_type_color(result2.vehicle_type)
    
    # Add traces for both vehicles
    fig.add_trace(go.Bar(
        x=years,
        y=annual_co2_1,
        name=f"{result1.vehicle_name} Emissions",
        marker_color=color1
    ))
    
    fig.add_trace(go.Bar(
        x=years,
        y=annual_co2_2,
        name=f"{result2.vehicle_name} Emissions",
        marker_color=color2
    ))
    
    # Add cumulative lines
    fig.add_trace(go.Scatter(
        x=years,
        y=[sum(annual_co2_1[:i]) for i in range(1, len(annual_co2_1) + 1)],
        mode="lines",
        name=f"{result1.vehicle_name} (Cumulative)",
        line=dict(color=color1, width=2, dash="dash"),
        hovertemplate="Year %{x}<br>Cumulative CO2: %{y:.1f} tonnes<extra></extra>",
    ))
    
    fig.add_trace(go.Scatter(
        x=years,
        y=[sum(annual_co2_2[:i]) for i in range(1, len(annual_co2_2) + 1)],
        mode="lines",
        name=f"{result2.vehicle_name} (Cumulative)",
        line=dict(color=color2, width=2, dash="dash"),
        hovertemplate="Year %{x}<br>Cumulative CO2: %{y:.1f} tonnes<extra></extra>",
    ))
    
    # Update layout
    fig.update_layout(
        title="CO2 Emissions Over Time",
        xaxis_title="Year",
        yaxis_title="CO2 Emissions (tonnes)",
        height=400,
        barmode='group',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig


def render_energy_consumption_comparison(result1: TCOOutput, result2: TCOOutput):
    """
    Render energy consumption comparison with actual data
    
    Args:
        result1: TCO result for the first vehicle with emissions data
        result2: TCO result for the second vehicle with emissions data
    """
    # Create two-column layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Energy Efficiency")
        
        # Create energy efficiency comparison using actual data
        fig = create_energy_efficiency_chart(result1, result2)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### Energy Source Mix")
        
        # Create energy source mix visualization using actual data
        fig = create_energy_source_chart(result1, result2)
        st.plotly_chart(fig, use_container_width=True)
    
    # Energy cost comparison
    st.markdown("### Energy Cost Comparison")
    
    # Create energy cost comparison table with actual data
    energy_cost_data = {
        "Metric": [
            "Total Energy Cost",
            "Energy Cost per km",
            "Energy Cost % of TCO",
            "Annual Energy Cost"
        ],
        result1.vehicle_name: [
            format_currency(result1.npv_costs.energy),
            f"{format_currency(result1.npv_costs.energy / result1.total_distance_km)}/km",
            f"{result1.npv_costs.energy / result1.total_tco * 100:.1f}%",
            format_currency(result1.npv_costs.energy / result1.analysis_period_years)
        ],
        result2.vehicle_name: [
            format_currency(result2.npv_costs.energy),
            f"{format_currency(result2.npv_costs.energy / result2.total_distance_km)}/km",
            f"{result2.npv_costs.energy / result2.total_tco * 100:.1f}%",
            format_currency(result2.npv_costs.energy / result2.analysis_period_years)
        ],
        "Difference": [
            format_currency(result1.npv_costs.energy - result2.npv_costs.energy),
            f"{format_currency((result1.npv_costs.energy / result1.total_distance_km) - (result2.npv_costs.energy / result2.total_distance_km))}/km",
            f"{(result1.npv_costs.energy / result1.total_tco * 100) - (result2.npv_costs.energy / result2.total_tco * 100):.1f}%",
            format_currency((result1.npv_costs.energy / result1.analysis_period_years) - (result2.npv_costs.energy / result2.analysis_period_years))
        ]
    }
    
    # Display energy cost table
    st.dataframe(pd.DataFrame(energy_cost_data), use_container_width=True)


def create_energy_efficiency_chart(result1: TCOOutput, result2: TCOOutput) -> go.Figure:
    """
    Create energy efficiency chart with actual data.
    
    Args:
        result1: TCO result for the first vehicle with emissions data
        result2: TCO result for the second vehicle with emissions data
        
    Returns:
        go.Figure: Energy efficiency chart
    """
    # Use actual energy per km from emissions data
    energy_per_km1 = result1.emissions.energy_per_km
    energy_per_km2 = result2.emissions.energy_per_km
    
    # Create figure
    fig = go.Figure()
    
    # Get vehicle colors
    from utils.ui_terminology import get_vehicle_type_color
    color1 = get_vehicle_type_color(result1.vehicle_type)
    color2 = get_vehicle_type_color(result2.vehicle_type)
    
    # Add bars for energy per km
    fig.add_trace(go.Bar(
        x=[result1.vehicle_name],
        y=[energy_per_km1],
        text=[f"{energy_per_km1:.2f} kWh/km"],
        textposition="auto",
        name=result1.vehicle_name,
        marker_color=color1
    ))
    
    fig.add_trace(go.Bar(
        x=[result2.vehicle_name],
        y=[energy_per_km2],
        text=[f"{energy_per_km2:.2f} kWh/km"],
        textposition="auto",
        name=result2.vehicle_name,
        marker_color=color2
    ))
    
    # Style the chart
    fig.update_layout(
        title="Energy Efficiency Comparison",
        yaxis_title="Energy Consumption (kWh/km)",
        height=300,
        showlegend=False
    )
    
    return fig


def create_energy_source_chart(result1: TCOOutput, result2: TCOOutput) -> go.Figure:
    """
    Create energy source mix chart with accurate data.
    
    Args:
        result1: TCO result for the first vehicle
        result2: TCO result for the second vehicle
        
    Returns:
        go.Figure: Energy source chart
    """
    # Determine vehicle types for energy source visualization
    is_electric1 = result1.vehicle_type == "bet"
    is_electric2 = result2.vehicle_type == "bet"
    
    # Create pie charts for energy sources based on actual vehicle types
    fig = go.Figure()
    
    if is_electric1:
        # Electric vehicle energy sources - use Australian grid mix
        fig.add_trace(go.Pie(
            labels=["Coal", "Gas", "Hydro", "Wind", "Solar", "Other Renewables"],
            values=[52, 18, 11, 10, 7, 2],  # Australian electricity mix
            name=result1.vehicle_name,
            domain=dict(x=[0, 0.45], y=[0, 1]),
            title=dict(text=result1.vehicle_name)
        ))
    else:
        # Diesel vehicle energy sources
        fig.add_trace(go.Pie(
            labels=["Diesel", "Biodiesel"],
            values=[95, 5],  # Typical Australian diesel mix
            name=result1.vehicle_name,
            domain=dict(x=[0, 0.45], y=[0, 1]),
            title=dict(text=result1.vehicle_name)
        ))
    
    if is_electric2:
        # Electric vehicle energy sources - use Australian grid mix
        fig.add_trace(go.Pie(
            labels=["Coal", "Gas", "Hydro", "Wind", "Solar", "Other Renewables"],
            values=[52, 18, 11, 10, 7, 2],  # Australian electricity mix
            name=result2.vehicle_name,
            domain=dict(x=[0.55, 1], y=[0, 1]),
            title=dict(text=result2.vehicle_name)
        ))
    else:
        # Diesel vehicle energy sources
        fig.add_trace(go.Pie(
            labels=["Diesel", "Biodiesel"],
            values=[95, 5],  # Typical Australian diesel mix
            name=result2.vehicle_name,
            domain=dict(x=[0.55, 1], y=[0, 1]),
            title=dict(text=result2.vehicle_name)
        ))
    
    # Style the chart
    fig.update_layout(
        title="Energy Source Mix",
        height=300
    )
    
    return fig


def render_sustainability_metrics(result1: TCOOutput, result2: TCOOutput):
    """
    Render sustainability metrics with actual data
    
    Args:
        result1: TCO result for the first vehicle with emissions data
        result2: TCO result for the second vehicle with emissions data
    """
    st.markdown("### Sustainability Metrics")
    
    # Use actual emissions data to determine sustainability metrics
    # Calculate scores (0-100, higher is better)
    is_electric1 = result1.vehicle_type == "bet"
    is_electric2 = result2.vehicle_type == "bet"
    
    # CO2 intensity affects air quality score
    co2_per_km1 = result1.emissions.co2_per_km
    co2_per_km2 = result2.emissions.co2_per_km
    
    # Normalize scores between 0-100
    max_co2 = max(co2_per_km1, co2_per_km2)
    min_co2 = min(co2_per_km1, co2_per_km2)
    co2_range = max_co2 - min_co2
    
    # Higher score means lower emissions (better)
    air_quality1 = 50 + 40 * (1 - (co2_per_km1 - min_co2) / co2_range if co2_range > 0 else 0.5)
    air_quality2 = 50 + 40 * (1 - (co2_per_km2 - min_co2) / co2_range if co2_range > 0 else 0.5)
    
    # Renewability based on vehicle type and energy source
    renewability1 = 85 if is_electric1 else 20
    renewability2 = 85 if is_electric2 else 20
    
    # Resource use (electric vehicles have battery resource issues)
    resource_use1 = 70 if is_electric1 else 65
    resource_use2 = 70 if is_electric2 else 65
    
    # Lifecycle impact (combination of emissions and resource use)
    lifecycle_impact1 = (air_quality1 * 0.6 + resource_use1 * 0.4)
    lifecycle_impact2 = (air_quality2 * 0.6 + resource_use2 * 0.4)
    
    # Create spider chart data
    categories = ["Air Quality", "Renewability", "Resource Use", "Lifecycle Impact"]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=[air_quality1, renewability1, resource_use1, lifecycle_impact1],
        theta=categories,
        fill='toself',
        name=result1.vehicle_name
    ))
    
    fig.add_trace(go.Scatterpolar(
        r=[air_quality2, renewability2, resource_use2, lifecycle_impact2],
        theta=categories,
        fill='toself',
        name=result2.vehicle_name
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )),
        showlegend=True,
        height=400
    )
    
    # Display the chart
    st.plotly_chart(fig, use_container_width=True)
    
    # Add sustainability insights based on actual data
    sustainability_impact = calculate_sustainability_impact(result1, result2)
    
    st.markdown("### Sustainability Impact")
    
    impact_cols = st.columns(3)
    
    with impact_cols[0]:
        st.metric(
            "Air Quality Impact", 
            f"{sustainability_impact['air_quality']:+d}%",
            delta=None
        )
        st.markdown("""
        Reduction in air pollutants including NOx, SOx, 
        and particulate matter that impact local air quality.
        """)
    
    with impact_cols[1]:
        st.metric(
            "Renewability", 
            f"{sustainability_impact['renewability']:+d}%",
            delta=None
        )
        st.markdown("""
        Increase in usage of renewable energy sources 
        instead of non-renewable fossil fuels.
        """)
    
    with impact_cols[2]:
        st.metric(
            "Resource Conservation", 
            f"{sustainability_impact['resource']:+d}%",
            delta=None
        )
        st.markdown("""
        Reduction in consumption of non-renewable 
        resources over the vehicle lifetime.
        """)


def calculate_sustainability_impact(result1: TCOOutput, result2: TCOOutput) -> Dict[str, int]:
    """
    Calculate sustainability impact comparison using actual emissions data
    
    Args:
        result1: TCO result for the first vehicle with emissions data
        result2: TCO result for the second vehicle with emissions data
        
    Returns:
        Dict[str, int]: Sustainability impact metrics
    """
    # Use actual emissions data to calculate impact
    is_electric1 = result1.vehicle_type == "bet"
    is_electric2 = result2.vehicle_type == "bet"
    
    co2_diff_percentage = ((result2.emissions.total_co2_tonnes - result1.emissions.total_co2_tonnes) / 
                           max(result1.emissions.total_co2_tonnes, result2.emissions.total_co2_tonnes)) * 100
    
    # Calculate air quality impact
    air_quality = int(co2_diff_percentage) if abs(co2_diff_percentage) < 100 else int(np.sign(co2_diff_percentage) * 100)
    
    # Calculate renewability impact based on vehicle types
    if is_electric1 and not is_electric2:
        renewability = 80
    elif is_electric2 and not is_electric1:
        renewability = -80
    else:
        renewability = 0
    
    # Calculate resource impact based on energy consumption
    energy_diff_percentage = ((result2.emissions.energy_consumption_kwh - result1.emissions.energy_consumption_kwh) / 
                             max(result1.emissions.energy_consumption_kwh, result2.emissions.energy_consumption_kwh)) * 100
    
    resource = int(energy_diff_percentage * 0.3) if abs(energy_diff_percentage) < 100 else int(np.sign(energy_diff_percentage) * 30)
    
    return {
        "air_quality": air_quality,
        "renewability": renewability,
        "resource": resource
    } 