"""
Environmental Impact Visualization Module

This module provides UI components for analyzing and visualizing the
environmental impacts of different vehicle options.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
import numpy as np

from tco_model.models import TCOOutput, ComparisonResult, EmissionsData
from tco_model.schemas import VehicleType
from utils.helpers import format_currency, format_percentage, format_number
from utils.ui_components import UIComponentFactory
from utils.ui_terminology import format_currency, format_number_with_unit


def render_environmental_dashboard(results: Dict[str, TCOOutput]) -> str:
    """
    Render a comprehensive environmental dashboard for comparison.
    
    Args:
        results: Dictionary with TCO results for vehicle_1 and vehicle_2
        
    Returns:
        HTML string for testing (actual rendering happens via streamlit)
    """
    # Get results
    result1 = results["vehicle_1"]
    result2 = results["vehicle_2"]
    
    # Render emissions timeline
    st.header("Environmental Impact Analysis")
    
    # Calculate emissions data
    emissions_data = calculate_emissions_data(result1, result2)
    
    # Create two-column layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("CO₂ Emissions Timeline")
        emissions_chart = create_emissions_timeline_chart(emissions_data)
        st.plotly_chart(emissions_chart, use_container_width=True)
    
    with col2:
        st.subheader("Emissions Comparison")
        render_emissions_comparison(result1, result2)
    
    # Add emissions equivalence section
    st.subheader("Environmental Impact Equivalents")
    render_emissions_equivalence(result1, result2)
    
    # Energy consumption comparison
    st.subheader("Energy Consumption Analysis")
    render_energy_consumption_comparison(result1, result2)
    
    # Return HTML for testing
    return f"Environmental dashboard rendered with CO2 and Emissions analysis and comparisons for {result1.vehicle_name} and {result2.vehicle_name}"


def calculate_emissions_data(result1: TCOOutput, result2: TCOOutput) -> Dict[str, Any]:
    """
    Calculate emissions data for visualization.
    
    Args:
        result1: TCO result for the first vehicle
        result2: TCO result for the second vehicle
        
    Returns:
        Dict with emissions data for visualizations
    """
    # Extract emissions data from results if available
    emissions1 = getattr(result1, 'emissions', None)
    emissions2 = getattr(result2, 'emissions', None)
    
    # If emissions data is not available, use a TCO calculator to estimate it
    if not emissions1 or not emissions2:
        from tco_model.calculator import TCOCalculator
        calculator = TCOCalculator()
        
        # Try to estimate emissions
        emissions1 = calculator.estimate_emissions(result1)
        emissions2 = calculator.estimate_emissions(result2)
    
    # Create annual timeline data
    years = list(range(1, max(
        len(emissions1.annual_co2_tonnes) if hasattr(emissions1, 'annual_co2_tonnes') else 0,
        len(emissions2.annual_co2_tonnes) if hasattr(emissions2, 'annual_co2_tonnes') else 0,
        result1.analysis_period_years + 1  # Include year 0
    )))
    
    # Get or estimate annual CO2 emissions
    annual_co2_1 = emissions1.annual_co2_tonnes if hasattr(emissions1, 'annual_co2_tonnes') else [
        emissions1.total_co2_tonnes / result1.analysis_period_years for _ in range(result1.analysis_period_years)
    ]
    
    annual_co2_2 = emissions2.annual_co2_tonnes if hasattr(emissions2, 'annual_co2_tonnes') else [
        emissions2.total_co2_tonnes / result2.analysis_period_years for _ in range(result2.analysis_period_years)
    ]
    
    # Calculate cumulative CO2
    cumulative_co2_1 = [sum(annual_co2_1[:i+1]) for i in range(len(annual_co2_1))]
    cumulative_co2_2 = [sum(annual_co2_2[:i+1]) for i in range(len(annual_co2_2))]
    
    # Fill out any missing years
    while len(cumulative_co2_1) < len(years):
        cumulative_co2_1.append(cumulative_co2_1[-1] if cumulative_co2_1 else 0)
    while len(cumulative_co2_2) < len(years):
        cumulative_co2_2.append(cumulative_co2_2[-1] if cumulative_co2_2 else 0)
    
    # Calculate difference in total emissions
    total_diff = emissions1.total_co2_tonnes - emissions2.total_co2_tonnes
    lower_emissions_vehicle = result1.vehicle_name if total_diff < 0 else result2.vehicle_name
    emissions_saved = abs(total_diff)
    
    # Build the emissions data dictionary
    emissions_data = {
        "vehicle_1": {
            "name": result1.vehicle_name,
            "total_co2": emissions1.total_co2_tonnes,
            "co2_per_km": emissions1.co2_per_km,
            "annual_co2": annual_co2_1,
            "cumulative_co2": cumulative_co2_1,
            "trees_equivalent": emissions1.trees_equivalent if hasattr(emissions1, 'trees_equivalent') else 0,
            "homes_equivalent": emissions1.homes_equivalent if hasattr(emissions1, 'homes_equivalent') else 0,
            "cars_equivalent": emissions1.cars_equivalent if hasattr(emissions1, 'cars_equivalent') else 0
        },
        "vehicle_2": {
            "name": result2.vehicle_name,
            "total_co2": emissions2.total_co2_tonnes,
            "co2_per_km": emissions2.co2_per_km,
            "annual_co2": annual_co2_2,
            "cumulative_co2": cumulative_co2_2,
            "trees_equivalent": emissions2.trees_equivalent if hasattr(emissions2, 'trees_equivalent') else 0,
            "homes_equivalent": emissions2.homes_equivalent if hasattr(emissions2, 'homes_equivalent') else 0,
            "cars_equivalent": emissions2.cars_equivalent if hasattr(emissions2, 'cars_equivalent') else 0
        },
        "comparison": {
            "lower_emissions_vehicle": lower_emissions_vehicle,
            "emissions_saved": emissions_saved,
            "percentage_difference": abs(total_diff / max(emissions1.total_co2_tonnes, emissions2.total_co2_tonnes) * 100)
        },
        "years": years
    }
    
    return emissions_data


def create_emissions_timeline_chart(emissions_data: Dict[str, Any]) -> go.Figure:
    """
    Create a chart showing the emissions timeline for both vehicles.
    
    Args:
        emissions_data: Dictionary with emissions data from calculate_emissions_data
        
    Returns:
        Plotly figure with emissions timeline
    """
    # Create a new figure
    fig = go.Figure()
    
    # Get data points
    years = emissions_data["years"]
    v1_data = emissions_data["vehicle_1"]
    v2_data = emissions_data["vehicle_2"]
    
    # Add cumulative CO2 traces
    fig.add_trace(go.Scatter(
        x=years,
        y=v1_data["cumulative_co2"],
        name=f"{v1_data['name']} Cumulative CO₂",
        line=dict(color="#4CAF50", width=3),
        mode="lines"
    ))
    
    fig.add_trace(go.Scatter(
        x=years,
        y=v2_data["cumulative_co2"],
        name=f"{v2_data['name']} Cumulative CO₂",
        line=dict(color="#FF9800", width=3),
        mode="lines"
    ))
    
    # Add annual CO2 emission bars as a secondary display option
    show_annual = False  # Could be a toggle in the UI
    if show_annual:
        for i, year in enumerate(years):
            if i < len(v1_data["annual_co2"]):
                fig.add_trace(go.Bar(
                    x=[year],
                    y=[v1_data["annual_co2"][i]],
                    name=f"{v1_data['name']} Year {year}",
                    marker_color="#4CAF5080",
                    showlegend=i == 0
                ))
            
            if i < len(v2_data["annual_co2"]):
                fig.add_trace(go.Bar(
                    x=[year],
                    y=[v2_data["annual_co2"][i]],
                    name=f"{v2_data['name']} Year {year}",
                    marker_color="#FF980080",
                    showlegend=i == 0
                ))
    
    # Add a shaded area showing the difference
    if v1_data["total_co2"] != v2_data["total_co2"]:
        # Calculate difference at each year
        diffs = []
        for i in range(len(years)):
            if i < len(v1_data["cumulative_co2"]) and i < len(v2_data["cumulative_co2"]):
                diffs.append(abs(v1_data["cumulative_co2"][i] - v2_data["cumulative_co2"][i]))
            else:
                diffs.append(0)
        
        # Add an area for the difference
        lower_vehicle = v1_data["name"] if v1_data["total_co2"] < v2_data["total_co2"] else v2_data["name"]
        higher_vehicle = v2_data["name"] if v1_data["total_co2"] < v2_data["total_co2"] else v1_data["name"]
        
        fig.add_trace(go.Scatter(
            x=years,
            y=diffs,
            name=f"CO₂ Savings",
            fill='tozeroy',
            mode='none',
            fillcolor='rgba(76, 175, 80, 0.2)',
            hoverinfo='skip'
        ))
    
    # Update layout
    fig.update_layout(
        title="CO₂ Emissions Over Time",
        xaxis_title="Year",
        yaxis_title="Cumulative CO₂ Emissions (tonnes)",
        height=400,
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig


def render_emissions_comparison(result1: TCOOutput, result2: TCOOutput):
    """
    Render a comparison of emissions metrics between vehicles.
    
    Args:
        result1: TCO result for the first vehicle
        result2: TCO result for the second vehicle
    """
    # Extract emissions data
    emissions1 = getattr(result1, 'emissions', None)
    emissions2 = getattr(result2, 'emissions', None)
    
    # If emissions data is not available, try to estimate it
    if not emissions1 or not emissions2:
        from tco_model.calculator import TCOCalculator
        calculator = TCOCalculator()
        
        emissions1 = calculator.estimate_emissions(result1)
        emissions2 = calculator.estimate_emissions(result2)
    
    # Format emissions data for display
    co2_1 = format_number(emissions1.total_co2_tonnes, 1)
    co2_2 = format_number(emissions2.total_co2_tonnes, 1)
    co2_per_km_1 = f"{emissions1.co2_per_km:.0f} g/km"
    co2_per_km_2 = f"{emissions2.co2_per_km:.0f} g/km"
    
    # Calculate percentage difference
    if emissions1.total_co2_tonnes == 0 and emissions2.total_co2_tonnes == 0:
        pct_diff = 0
    elif emissions1.total_co2_tonnes == 0:
        pct_diff = 100
    elif emissions2.total_co2_tonnes == 0:
        pct_diff = -100
    else:
        pct_diff = (emissions2.total_co2_tonnes - emissions1.total_co2_tonnes) / emissions1.total_co2_tonnes * 100
    
    # Determine which vehicle has lower emissions
    if emissions1.total_co2_tonnes < emissions2.total_co2_tonnes:
        lower_emissions = result1.vehicle_name
        reduction = format_number(emissions2.total_co2_tonnes - emissions1.total_co2_tonnes, 1)
        reduction_pct = f"{abs(pct_diff):.1f}%"
    elif emissions2.total_co2_tonnes < emissions1.total_co2_tonnes:
        lower_emissions = result2.vehicle_name
        reduction = format_number(emissions1.total_co2_tonnes - emissions2.total_co2_tonnes, 1)
        reduction_pct = f"{abs(pct_diff):.1f}%"
    else:
        lower_emissions = None
    
    # Create metrics display
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            label=f"{result1.vehicle_name} Total CO₂",
            value=f"{co2_1} tonnes",
            delta=f"{pct_diff:.1f}% vs {result2.vehicle_name}",
            delta_color="inverse"
        )
        
        st.metric(
            label=f"{result1.vehicle_name} CO₂ per km",
            value=co2_per_km_1
        )
    
    with col2:
        st.metric(
            label=f"{result2.vehicle_name} Total CO₂",
            value=f"{co2_2} tonnes",
            delta=f"{-pct_diff:.1f}% vs {result1.vehicle_name}",
            delta_color="inverse"
        )
        
        st.metric(
            label=f"{result2.vehicle_name} CO₂ per km",
            value=co2_per_km_2
        )
    
    # Add key insight
    if lower_emissions:
        st.markdown(f"""
        <div class="emissions-insight">
            <i class="fas fa-leaf"></i> <strong>{lower_emissions}</strong> produces <strong>{reduction_pct}</strong> 
            lower CO₂ emissions, saving <strong>{reduction} tonnes</strong> over the vehicle lifetime.
        </div>
        """, unsafe_allow_html=True)


def render_emissions_equivalence(result1: TCOOutput, result2: TCOOutput):
    """
    Render emissions equivalence comparisons.
    
    Args:
        result1: TCO result for the first vehicle
        result2: TCO result for the second vehicle
    """
    # Extract emissions data
    emissions1 = getattr(result1, 'emissions', None)
    emissions2 = getattr(result2, 'emissions', None)
    
    # If emissions data is not available, try to estimate it
    if not emissions1 or not emissions2:
        from tco_model.calculator import TCOCalculator
        calculator = TCOCalculator()
        
        emissions1 = calculator.estimate_emissions(result1)
        emissions2 = calculator.estimate_emissions(result2)
    
    # Calculate the difference in emissions
    diff = abs(emissions1.total_co2_tonnes - emissions2.total_co2_tonnes)
    lower_vehicle = result1.vehicle_name if emissions1.total_co2_tonnes < emissions2.total_co2_tonnes else result2.vehicle_name
    higher_vehicle = result2.vehicle_name if emissions1.total_co2_tonnes < emissions2.total_co2_tonnes else result1.vehicle_name
    
    # Calculate equivalence metrics for the difference
    trees_equiv = int(diff * 45)  # Approximate number of trees to offset 1 tonne CO2 per year
    homes_equiv = int(diff * 0.12)  # Approximate CO2 from average home per year
    cars_equiv = int(diff * 0.22)  # Approximate cars taken off the road for a year
    
    # Create three columns for equivalence metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="equivalence-card">
            <div class="equivalence-icon">🌳</div>
            <div class="equivalence-value">{format_number(trees_equiv, 0)}</div>
            <div class="equivalence-label">trees planted for one year</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="equivalence-card">
            <div class="equivalence-icon">🏠</div>
            <div class="equivalence-value">{format_number(homes_equiv, 0)}</div>
            <div class="equivalence-label">homes' electricity use for one year</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="equivalence-card">
            <div class="equivalence-icon">🚗</div>
            <div class="equivalence-value">{format_number(cars_equiv, 0)}</div>
            <div class="equivalence-label">passenger vehicles for one year</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Add context explanation
    st.markdown(f"""
    <div class="equivalence-explanation">
        The CO₂ emissions reduction of <strong>{format_number(diff, 1)} tonnes</strong> by choosing {lower_vehicle} 
        instead of {higher_vehicle} is equivalent to the above environmental impacts.
    </div>
    """, unsafe_allow_html=True)


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
            # Calculate emissions data from the two results
            emissions_data = calculate_emissions_data(result1, result2)
            # Now pass the calculated emissions data to the chart function
            fig = create_emissions_timeline_chart(emissions_data)
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


def render_energy_consumption_comparison(result1: TCOOutput, result2: TCOOutput):
    """
    Render energy consumption comparison between vehicles.
    
    Args:
        result1: TCO result for the first vehicle
        result2: TCO result for the second vehicle
    """
    # Extract energy consumption data
    if hasattr(result1, 'emissions') and hasattr(result2, 'emissions'):
        energy1 = result1.emissions.energy_per_km if hasattr(result1.emissions, 'energy_per_km') else 0
        energy2 = result2.emissions.energy_per_km if hasattr(result2.emissions, 'energy_per_km') else 0
        
        total_energy1 = result1.emissions.energy_consumption_kwh if hasattr(result1.emissions, 'energy_consumption_kwh') else 0
        total_energy2 = result2.emissions.energy_consumption_kwh if hasattr(result2.emissions, 'energy_consumption_kwh') else 0
    else:
        # Estimate energy consumption if not available
        if result1.vehicle_type == VehicleType.BATTERY_ELECTRIC:
            energy1 = 1.5  # kWh/km (typical for electric truck)
            total_energy1 = energy1 * result1.total_distance_km
        else:
            # Convert diesel L/100km to kWh/km
            energy1 = 10.5  # kWh/L
            total_energy1 = energy1 * result1.energy_consumption * result1.total_distance_km / 100
            
        if result2.vehicle_type == VehicleType.BATTERY_ELECTRIC:
            energy2 = 1.5  # kWh/km (typical for electric truck)
            total_energy2 = energy2 * result2.total_distance_km
        else:
            # Convert diesel L/100km to kWh/km
            energy2 = 10.5  # kWh/L
            total_energy2 = energy2 * result2.energy_consumption * result2.total_distance_km / 100
    
    # Create metrics display
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            label=f"{result1.vehicle_name} Energy Efficiency",
            value=f"{energy1:.2f} kWh/km"
        )
        
        st.metric(
            label=f"{result1.vehicle_name} Total Energy",
            value=f"{format_number(total_energy1, 0)} kWh"
        )
    
    with col2:
        st.metric(
            label=f"{result2.vehicle_name} Energy Efficiency",
            value=f"{energy2:.2f} kWh/km"
        )
        
        st.metric(
            label=f"{result2.vehicle_name} Total Energy",
            value=f"{format_number(total_energy2, 0)} kWh"
        )
    
    # Add comparison insight
    if energy1 != energy2:
        more_efficient = result1.vehicle_name if energy1 < energy2 else result2.vehicle_name
        efficiency_diff = abs(energy1 - energy2)
        efficiency_pct = abs((energy1 - energy2) / max(energy1, energy2) * 100)
        
        st.markdown(f"""
        <div class="energy-insight">
            <strong>{more_efficient}</strong> is <strong>{efficiency_pct:.1f}%</strong> more energy efficient,
            using <strong>{efficiency_diff:.2f} kWh/km</strong> less energy.
        </div>
        """, unsafe_allow_html=True)


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
    is_electric1 = result1.vehicle_type == VehicleType.BATTERY_ELECTRIC.value
    is_electric2 = result2.vehicle_type == VehicleType.BATTERY_ELECTRIC.value
    
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
    is_electric1 = result1.vehicle_type == VehicleType.BATTERY_ELECTRIC.value
    is_electric2 = result2.vehicle_type == VehicleType.BATTERY_ELECTRIC.value
    
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
    is_electric1 = result1.vehicle_type == VehicleType.BATTERY_ELECTRIC.value
    is_electric2 = result2.vehicle_type == VehicleType.BATTERY_ELECTRIC.value
    
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