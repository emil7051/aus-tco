"""
Results Charts Module

This module renders the UI components for displaying TCO results as interactive charts.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from plotly.subplots import make_subplots

from tco_model.models import TCOOutput, ComparisonResult
from utils.helpers import format_currency, format_percentage
from tco_model.terminology import UI_COMPONENT_KEYS, UI_COMPONENT_LABELS
from ui.results.utils import (
    get_component_value, get_component_color, get_component_display_order,
    get_chart_settings, apply_chart_theme, get_annual_component_value,
    validate_tco_results
)


def render_charts(results: Dict[str, TCOOutput], comparison: ComparisonResult):
    """
    Render the interactive charts for TCO results.
    
    Args:
        results: Dictionary containing TCO results for each vehicle
        comparison: The comparison result between the two vehicles
    """
    # Validate results
    if not validate_tco_results(results):
        st.warning("Invalid results data. Cannot display charts.")
        return
        
    # Extract results
    result1 = results["vehicle_1"]
    result2 = results["vehicle_2"]
    
    # Create chart tabs
    chart_tabs = st.tabs([
        "Cumulative TCO",
        "Annual Costs",
        "Cost Components",
        "Sensitivity Analysis",
        "Chart Settings"
    ])
    
    # Get chart settings
    settings = get_chart_settings()
    
    # Cumulative TCO chart
    with chart_tabs[0]:
        st.subheader("Cumulative TCO Over Time")
        
        try:
            cumulative_chart = create_cumulative_tco_chart(
                result1, 
                result2, 
                show_breakeven=settings["show_breakeven_point"],
                height=settings["chart_height"]
            )
            st.plotly_chart(cumulative_chart, use_container_width=True)
        except Exception as e:
            st.error(f"Error creating cumulative TCO chart: {str(e)}")
    
    # Annual costs chart
    with chart_tabs[1]:
        st.subheader("Annual Costs")
        
        # Add filters for annual costs chart
        st.checkbox("Show components breakdown", key="show_annual_components", value=False)
        annual_view = st.radio(
            "View type",
            ["Side by side", "Stacked"],
            key="annual_view_type",
            horizontal=True
        )
        
        try:
            annual_costs_chart = create_annual_costs_chart(
                result1, 
                result2, 
                show_components=st.session_state.show_annual_components,
                stacked=(annual_view == "Stacked"),
                height=settings["chart_height"]
            )
            st.plotly_chart(annual_costs_chart, use_container_width=True)
        except Exception as e:
            st.error(f"Error creating annual costs chart: {str(e)}")
    
    # Cost components chart
    with chart_tabs[2]:
        st.subheader("Cost Component Comparison")
        
        # Add display options for component chart
        component_view = st.radio(
            "Component view",
            ["Stacked Bar", "Grouped Bar", "Pie Chart"],
            key="component_view_type",
            horizontal=True
        )
        
        try:
            # Create the appropriate chart based on selected view
            if component_view == "Pie Chart":
                components_chart = create_cost_components_pie_chart(
                    result1, 
                    result2, 
                    comparison,
                    components=settings["components_to_show"],
                    height=settings["chart_height"]
                )
            else:
                components_chart = create_cost_components_chart(
                    result1, 
                    result2, 
                    comparison,
                    stacked=(component_view == "Stacked Bar"),
                    components=settings["components_to_show"],
                    height=settings["chart_height"]
                )
            
            st.plotly_chart(components_chart, use_container_width=True)
        except Exception as e:
            st.error(f"Error creating cost components chart: {str(e)}")
    
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
    
    # Chart settings tab
    with chart_tabs[4]:
        render_chart_settings(settings)


def render_chart_settings(settings: Dict[str, Any]):
    """
    Render the chart settings UI controls
    
    Args:
        settings: Current chart settings dictionary
    """
    st.subheader("Chart Settings")
    
    # General chart settings
    settings["show_breakeven_point"] = st.checkbox(
        "Show break-even point", 
        value=settings["show_breakeven_point"]
    )
    
    settings["show_grid"] = st.checkbox(
        "Show grid lines", 
        value=settings["show_grid"]
    )
    
    settings["show_annotations"] = st.checkbox(
        "Show annotations", 
        value=settings["show_annotations"]
    )
    
    settings["chart_height"] = st.slider(
        "Chart height", 
        min_value=300, 
        max_value=800, 
        value=settings["chart_height"],
        step=50
    )
    
    # Color scheme selection
    settings["color_scheme"] = st.selectbox(
        "Color scheme",
        ["default", "Plotly", "D3", "G10", "T10", "Alphabet", "Dark24", "Light24"],
        index=0
    )
    
    # Component filter
    st.subheader("Components to Display")
    components = [
        (key, UI_COMPONENT_LABELS[key]) for key in UI_COMPONENT_KEYS
    ]
    
    selected_components = []
    for comp_key, comp_label in components:
        if st.checkbox(comp_label, value=comp_key in settings["components_to_show"]):
            selected_components.append(comp_key)
    
    # Update components to show
    if selected_components:
        settings["components_to_show"] = selected_components
    else:
        # Ensure at least one component is selected
        st.warning("At least one component must be selected.")
        settings["components_to_show"] = ["acquisition"]


def create_cumulative_tco_chart(result1: TCOOutput, result2: TCOOutput, 
                               show_breakeven: bool = True, height: int = 500) -> go.Figure:
    """
    Create a cumulative TCO chart showing how TCO accumulates over time.
    
    Args:
        result1: TCO result for the first vehicle
        result2: TCO result for the second vehicle
        show_breakeven: Whether to show the break-even point
        height: Chart height in pixels
        
    Returns:
        go.Figure: The plotly figure object for the chart
    """
    # Get the analysis period and vehicle names
    years = range(result1.analysis_period_years)
    vehicle1_name = result1.vehicle_name
    vehicle2_name = result2.vehicle_name
    
    # Calculate cumulative costs for both vehicles
    v1_cumulative = np.cumsum([result1.annual_costs[year].total for year in years])
    v2_cumulative = np.cumsum([result2.annual_costs[year].total for year in years])
    
    # Create the figure
    fig = go.Figure()
    
    # Add traces for both vehicles
    fig.add_trace(go.Scatter(
        x=list(years),
        y=v1_cumulative,
        mode="lines+markers",
        name=vehicle1_name,
        line=dict(color="#1f77b4", width=3),
        hovertemplate="%{y:$,.0f}<extra></extra>",
    ))
    
    fig.add_trace(go.Scatter(
        x=list(years),
        y=v2_cumulative,
        mode="lines+markers",
        name=vehicle2_name,
        line=dict(color="#ff7f0e", width=3),
        hovertemplate="%{y:$,.0f}<extra></extra>",
    ))
    
    # Apply theme and update layout
    fig = apply_chart_theme(fig, height, title="Cumulative TCO Over Time")
    fig.update_layout(
        xaxis_title="Year",
        yaxis_title="Cumulative Cost (AUD)",
        legend_title="Vehicle",
        hovermode="x unified",
    )
    
    # Add break-even point annotation if applicable and requested
    settings = get_chart_settings()
    if show_breakeven:
        breakeven_found = False
        for i in range(1, len(years)):
            if (v1_cumulative[i-1] <= v2_cumulative[i-1] and v1_cumulative[i] > v2_cumulative[i]) or \
            (v1_cumulative[i-1] >= v2_cumulative[i-1] and v1_cumulative[i] < v2_cumulative[i]):
                try:
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
                        visible=settings["show_annotations"],
                    )
                    breakeven_found = True
                    break
                except Exception:
                    # Skip if interpolation fails
                    pass
        
        if not breakeven_found and settings["show_annotations"]:
            # Add annotation indicating no break-even point
            fig.add_annotation(
                x=0.5,
                y=0.9,
                xref="paper",
                yref="paper",
                text="No break-even point found in analysis period",
                showarrow=False,
                font=dict(size=12, color="red"),
                visible=settings["show_annotations"],
            )
    
    return fig


def create_annual_costs_chart(result1: TCOOutput, result2: TCOOutput, 
                             show_components: bool = False, stacked: bool = False,
                             height: int = 500) -> go.Figure:
    """
    Create a chart showing the annual costs for both vehicles.
    
    Args:
        result1: TCO result for the first vehicle
        result2: TCO result for the second vehicle
        show_components: Whether to break down costs by component
        stacked: Whether to use stacked bars instead of grouped bars
        height: Chart height in pixels
        
    Returns:
        go.Figure: The plotly figure object for the chart
    """
    # Get the analysis period and vehicle names
    years = range(result1.analysis_period_years)
    vehicle1_name = result1.vehicle_name
    vehicle2_name = result2.vehicle_name
    
    title = "Annual Costs Breakdown" if show_components else "Annual Costs by Year"
    
    if not show_components:
        # Simple annual totals chart
        annual_data = {
            "Year": list(years) * 2,
            "Vehicle": [vehicle1_name] * len(years) + [vehicle2_name] * len(years),
            "Annual Cost": [result1.annual_costs[year].total for year in years] + 
                        [result2.annual_costs[year].total for year in years],
        }
        
        annual_df = pd.DataFrame(annual_data)
        
        # Create the figure using plotly express
        fig = px.bar(
            annual_df,
            x="Year",
            y="Annual Cost",
            color="Vehicle",
            barmode="group" if not stacked else "stack",
            title=title,
            labels={"Annual Cost": "Annual Cost (AUD)"},
            height=height,
            color_discrete_sequence=get_color_sequence(),
        )
        
        # Format currency values in hover text
        fig.update_traces(
            hovertemplate="Year: %{x}<br>Annual Cost: %{y:$,.0f}<extra></extra>"
        )
        
        # Apply theme
        fig = apply_chart_theme(fig, height, title=title)
    else:
        # Component breakdown chart
        fig = go.Figure()
        settings = get_chart_settings()
        components = []
        
        # Filter components based on settings
        for comp in UI_COMPONENT_KEYS:
            if comp in settings["components_to_show"]:
                components.append(comp)
        
        if stacked:
            # Create stacked bar chart for each vehicle
            for year in years:
                # Vehicle 1
                year_costs_v1 = {}
                for comp in components:
                    year_costs_v1[comp] = get_annual_component_value(result1, comp, year)
                
                fig.add_trace(go.Bar(
                    x=[year],
                    y=[sum(year_costs_v1.values())],
                    name=f"Year {year} - {vehicle1_name}",
                    legendgroup=vehicle1_name,
                    hovertemplate=f"Year {year}<br>Total: {format_currency(sum(year_costs_v1.values()))}<extra></extra>",
                ))
                
                # Vehicle 2
                year_costs_v2 = {}
                for comp in components:
                    year_costs_v2[comp] = get_annual_component_value(result2, comp, year)
                
                fig.add_trace(go.Bar(
                    x=[year + 0.2],  # Offset for side-by-side
                    y=[sum(year_costs_v2.values())],
                    name=f"Year {year} - {vehicle2_name}",
                    legendgroup=vehicle2_name,
                    hovertemplate=f"Year {year}<br>Total: {format_currency(sum(year_costs_v2.values()))}<extra></extra>",
                ))
        else:
            # Create traces for each component
            for comp in components:
                comp_label = UI_COMPONENT_LABELS[comp]
                
                # Get annual values using utility function for consistency
                v1_values = [get_annual_component_value(result1, comp, year) for year in years]
                v2_values = [get_annual_component_value(result2, comp, year) for year in years]
                
                # Vehicle 1
                fig.add_trace(go.Bar(
                    x=list(years),
                    y=v1_values,
                    name=f"{comp_label} - {vehicle1_name}",
                    legendgroup=vehicle1_name,
                    hovertemplate="Year: %{x}<br>Cost: %{y:$,.0f}<extra></extra>",
                ))
                
                # Vehicle 2
                fig.add_trace(go.Bar(
                    x=[y + 0.2 for y in years],  # Offset for side-by-side
                    y=v2_values,
                    name=f"{comp_label} - {vehicle2_name}",
                    legendgroup=vehicle2_name,
                    hovertemplate="Year: %{x}<br>Cost: %{y:$,.0f}<extra></extra>",
                ))
        
        # Apply theme and update layout
        fig = apply_chart_theme(fig, height, title=title)
        
        # Update layout
        barmode = "stack" if stacked else "group"
        fig.update_layout(
            barmode=barmode,
            xaxis_title="Year",
            yaxis_title="Annual Cost (AUD)",
            legend_title="Cost Component",
        )
    
    return fig


def create_cost_components_chart(result1: TCOOutput, result2: TCOOutput, comparison: ComparisonResult,
                                stacked: bool = True, components: List[str] = None,
                                height: int = 500) -> go.Figure:
    """
    Create a chart showing the cost component breakdown for both vehicles.
    
    Args:
        result1: TCO result for the first vehicle
        result2: TCO result for the second vehicle
        comparison: The comparison result between the two vehicles
        stacked: Whether to use stacked bars (True) or grouped bars (False)
        components: List of component keys to include
        height: Chart height in pixels
        
    Returns:
        go.Figure: The plotly figure object for the chart
    """
    # Get vehicle names
    vehicle1_name = result1.vehicle_name
    vehicle2_name = result2.vehicle_name
    
    # Define cost components and their labels if not provided
    if not components:
        components = UI_COMPONENT_KEYS.copy()
    
    # Chart title
    title = "Cost Components Distribution (NPV)"
    
    # Create the figure
    fig = go.Figure()
    
    if stacked:
        # Process components, separating positive and negative values
        positive_components = []
        negative_components = []
        
        for comp in components:
            v1_value = get_component_value(result1, comp)
            v2_value = get_component_value(result2, comp)
            
            if comp == "residual_value" or v1_value < 0 or v2_value < 0:
                negative_components.append(comp)
            else:
                positive_components.append(comp)
        
        # Add traces for positive cost components (stacked bar)
        for comp in positive_components:
            v1_value = max(0, get_component_value(result1, comp))
            v2_value = max(0, get_component_value(result2, comp))
            
            fig.add_trace(go.Bar(
                name=UI_COMPONENT_LABELS[comp],
                x=[vehicle1_name, vehicle2_name],
                y=[v1_value, v2_value],
                text=[format_currency(v1_value), format_currency(v2_value)],
                textposition="auto",
                hovertemplate="%{x}<br>%{fullData.name}: %{y:$,.0f}<extra></extra>",
            ))
        
        # Add negative value components as separate bars
        for comp in negative_components:
            v1_value = min(0, get_component_value(result1, comp))
            v2_value = min(0, get_component_value(result2, comp))
            
            fig.add_trace(go.Bar(
                name=UI_COMPONENT_LABELS[comp],
                x=[vehicle1_name, vehicle2_name],
                y=[v1_value, v2_value],
                text=[format_currency(v1_value), format_currency(v2_value)],
                textposition="auto",
                marker_color="green" if comp == "residual_value" else None,
                hovertemplate="%{x}<br>%{fullData.name}: %{y:$,.0f}<extra></extra>",
            ))
    else:
        # Grouped bar chart, one bar per component
        for comp in components:
            v1_value = get_component_value(result1, comp)
            v2_value = get_component_value(result2, comp)
            
            # Add a trace for each vehicle
            fig.add_trace(go.Bar(
                name=f"{UI_COMPONENT_LABELS[comp]} - {vehicle1_name}",
                x=[UI_COMPONENT_LABELS[comp]],
                y=[v1_value],
                text=[format_currency(v1_value)],
                textposition="auto",
                legendgroup=vehicle1_name,
                hovertemplate="%{x}<br>%{y:$,.0f}<extra></extra>",
            ))
            
            fig.add_trace(go.Bar(
                name=f"{UI_COMPONENT_LABELS[comp]} - {vehicle2_name}",
                x=[UI_COMPONENT_LABELS[comp]],
                y=[v2_value],
                text=[format_currency(v2_value)],
                textposition="auto",
                legendgroup=vehicle2_name,
                hovertemplate="%{x}<br>%{y:$,.0f}<extra></extra>",
            ))
    
    # Add a total value marker if using annotations
    settings = get_chart_settings()
    if settings["show_annotations"]:
        fig.add_trace(go.Scatter(
            name="Total TCO",
            x=[vehicle1_name, vehicle2_name],
            y=[result1.total_tco, result2.total_tco],
            mode="markers+text",
            marker=dict(size=15, color="black", symbol="diamond"),
            text=[f"Total: {format_currency(result1.total_tco)}", f"Total: {format_currency(result2.total_tco)}"],
            textposition="top center",
            hovertemplate="%{x}<br>Total TCO: %{y:$,.0f}<extra></extra>",
        ))
    
    # Apply theme and update layout
    fig = apply_chart_theme(fig, height, title=title)
    
    # Update layout
    fig.update_layout(
        barmode="stack" if stacked else "group",
        yaxis_title="Cost (AUD)",
        legend_title="Cost Component",
        hovermode="x unified",
    )
    
    return fig


def create_cost_components_pie_chart(result1: TCOOutput, result2: TCOOutput, 
                                    comparison: ComparisonResult, components: List[str] = None,
                                    height: int = 500) -> go.Figure:
    """
    Create pie charts showing the cost component breakdown for both vehicles.
    
    Args:
        result1: TCO result for the first vehicle
        result2: TCO result for the second vehicle
        comparison: The comparison result between the two vehicles
        components: List of component keys to include
        height: Chart height in pixels
        
    Returns:
        go.Figure: The plotly figure object for the chart
    """
    # Get vehicle names
    vehicle1_name = result1.vehicle_name
    vehicle2_name = result2.vehicle_name
    
    # Define cost components and their labels if not provided
    if not components:
        components = [c for c in UI_COMPONENT_KEYS if c != "residual_value"]
    
    # Skip residual value for pie chart as it's usually negative
    if "residual_value" in components:
        components.remove("residual_value")
    
    # Create data for pie charts, handling possible zero totals
    v1_values = [max(0, get_component_value(result1, comp)) for comp in components]
    v2_values = [max(0, get_component_value(result2, comp)) for comp in components]
    labels = [UI_COMPONENT_LABELS[comp] for comp in components]
    
    # Check for valid data (non-zero sum)
    if sum(v1_values) == 0 or sum(v2_values) == 0:
        # Create a figure with warning message
        fig = go.Figure()
        fig.add_annotation(
            x=0.5, y=0.5,
            text="Insufficient data for pie chart (zero total cost)",
            showarrow=False,
            font=dict(size=14, color="red")
        )
        fig = apply_chart_theme(fig, height, title="Cost Component Distribution (NPV)")
        return fig
    
    # Create subplots
    fig = make_subplots(rows=1, cols=2, specs=[[{"type": "domain"}, {"type": "domain"}]])
    
    # Add pie charts
    fig.add_trace(go.Pie(
        labels=labels,
        values=v1_values,
        name=vehicle1_name,
        title=vehicle1_name,
        textinfo="percent+label",
        hovertemplate="%{label}<br>%{value:$,.0f} (%{percent})<extra></extra>",
    ), 1, 1)
    
    fig.add_trace(go.Pie(
        labels=labels,
        values=v2_values,
        name=vehicle2_name,
        title=vehicle2_name,
        textinfo="percent+label",
        hovertemplate="%{label}<br>%{value:$,.0f} (%{percent})<extra></extra>",
    ), 1, 2)
    
    # Apply theme and update layout
    fig = apply_chart_theme(fig, height, title="Cost Component Distribution (NPV)")
    
    return fig


def get_color_sequence():
    """
    Get the color sequence based on the selected color scheme.
    
    Returns:
        List[str]: List of color hex codes
    """
    settings = get_chart_settings()
    color_scheme = settings.get("color_scheme", "default")
    
    if color_scheme == "default":
        return px.colors.qualitative.Plotly
    else:
        # Get colors from the selected qualitative color scheme
        try:
            return getattr(px.colors.qualitative, color_scheme)
        except AttributeError:
            return px.colors.qualitative.Plotly 

def create_cost_breakdown_chart(result: TCOOutput, height: int = 500) -> go.Figure:
    """
    Create a bar chart showing the cost breakdown for a TCO result.
    
    Args:
        result: TCO result to display
        height: Chart height in pixels
        
    Returns:
        plotly.graph_objects.Figure: The cost breakdown chart
    """
    # Get all component values using standardized access
    component_values = {
        component: get_component_value(result, component)
        for component in UI_COMPONENT_KEYS
    }
    
    # Sort components by display order
    sorted_components = sorted(
        UI_COMPONENT_KEYS,
        key=get_component_display_order
    )
    
    # Create sorted lists for chart
    components = [UI_COMPONENT_LABELS[c] for c in sorted_components]
    values = [component_values[c] for c in sorted_components]
    colors = [get_component_color(c) for c in sorted_components]
    
    # Create the chart
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=components,
        y=values,
        marker_color=colors,
        text=[format_currency(v) for v in values],
        textposition='auto'
    ))
    
    # Style the chart
    fig.update_layout(
        title=f"Cost Breakdown: {result.vehicle_name}",
        height=height,
        yaxis_title="NPV Cost (AUD)"
    )
    
    return fig

def create_tco_breakdown_bar(result1: TCOOutput, result2: TCOOutput, height: int = 400) -> go.Figure:
    """
    Create a bar chart comparing total TCO between two vehicles.
    
    Args:
        result1: TCO result for the first vehicle
        result2: TCO result for the second vehicle
        height: Height of the chart in pixels
        
    Returns:
        go.Figure: Plotly figure object
    """
    from utils.helpers import format_currency
    
    # Extract vehicle names
    vehicle1_name = result1.vehicle_name
    vehicle2_name = result2.vehicle_name
    
    # Create figure
    fig = go.Figure()
    
    # Add trace for total TCO
    fig.add_trace(go.Bar(
        name="Total TCO",
        x=[vehicle1_name, vehicle2_name],
        y=[result1.total_tco, result2.total_tco],
        marker_color="#1f77b4",  # Blue
        text=[f"Total: {format_currency(result1.total_tco)}", f"Total: {format_currency(result2.total_tco)}"],
        textposition="outside",
        hovertemplate="%{x}<br>Total TCO: %{y:$,.0f}<extra></extra>"
    )) 