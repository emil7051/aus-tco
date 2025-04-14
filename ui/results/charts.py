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
                comparison,
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
        
        # Use actual sensitivity analysis from the TCO calculator
        from tco_model.calculator import TCOCalculator
        from utils.ui_terminology import get_australian_spelling, get_vehicle_type_color
        calculator = TCOCalculator()
        
        # Create parameter selection options (using Australian spelling)
        parameter_options = {
            "electricity_price": get_australian_spelling("Electricity Price"),
            "diesel_price": get_australian_spelling("Diesel Price"),
            "annual_distance": get_australian_spelling("Annual Distance"),
            "analysis_period": get_australian_spelling("Analysis Period"),
            "acquisition_cost": get_australian_spelling("Vehicle Purchase Price"),
            "maintenance_cost_per_km": get_australian_spelling("Maintenance Cost per km")
        }
        
        # Allow user to select parameters to analyse
        selected_parameter = st.selectbox(
            "Select parameter to analyse",
            options=list(parameter_options.keys()),
            format_func=lambda x: parameter_options[x],
            key="sensitivity_parameter"
        )
        
        # Get scenarios from results
        scenario1 = results["vehicle_1"].scenario
        scenario2 = results["vehicle_2"].scenario
        
        if scenario1 and scenario2:
            # Generate variation range based on parameter
            original_value1 = getattr(scenario1, selected_parameter, 0)
            original_value2 = getattr(scenario2, selected_parameter, 0)
            
            # Create variation ranges (±30% in 6 steps)
            variations1 = [original_value1 * (1 + pct/100) for pct in range(-30, 31, 10)]
            variations2 = [original_value2 * (1 + pct/100) for pct in range(-30, 31, 10)]
            
            # Calculate sensitivity analysis
            sensitivity1 = calculator.perform_sensitivity_analysis(
                scenario1,
                selected_parameter,
                variations1
            )
            
            sensitivity2 = calculator.perform_sensitivity_analysis(
                scenario2,
                selected_parameter,
                variations2
            )
            
            # Create sensitivity chart
            fig = go.Figure()
            
            # Add traces for TCO using correct vehicle colours from terminology
            fig.add_trace(go.Scatter(
                x=[f"{v:.2f}" for v in sensitivity1.variation_values],
                y=sensitivity1.tco_values,
                mode="lines+markers",
                name=f"{results['vehicle_1'].vehicle_name} TCO",
                marker=dict(size=8),
                line=dict(width=2, color=get_vehicle_type_color(results['vehicle_1'].vehicle_type))
            ))
            
            fig.add_trace(go.Scatter(
                x=[f"{v:.2f}" for v in sensitivity2.variation_values],
                y=sensitivity2.tco_values,
                mode="lines+markers",
                name=f"{results['vehicle_2'].vehicle_name} TCO",
                marker=dict(size=8),
                line=dict(width=2, color=get_vehicle_type_color(results['vehicle_2'].vehicle_type))
            ))
            
            # Update layout with Australian spelling
            fig.update_layout(
                title=f"TCO Sensitivity to {parameter_options[selected_parameter]}",
                xaxis_title=f"{parameter_options[selected_parameter]} ({get_australian_spelling(sensitivity1.unit)})",
                yaxis_title=f"{get_australian_spelling('Total Cost of Ownership')} ($)",
                height=450,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Add tipping point if one exists
            if has_tipping_point(sensitivity1, sensitivity2):
                tipping_point = calculate_tipping_point(sensitivity1, sensitivity2)
                if tipping_point:
                    st.info(f"""
                    **Tipping Point**: When {parameter_options[selected_parameter]} reaches 
                    {tipping_point:.2f} {sensitivity1.unit}, the more cost-effective vehicle switches.
                    """)
            
            # Add LCOD sensitivity chart
            fig2 = go.Figure()
            
            # Add traces for LCOD using correct vehicle colours
            fig2.add_trace(go.Scatter(
                x=[f"{v:.2f}" for v in sensitivity1.variation_values],
                y=sensitivity1.lcod_values,
                mode="lines+markers",
                name=f"{results['vehicle_1'].vehicle_name} LCOD",
                marker=dict(size=8),
                line=dict(width=2, color=get_vehicle_type_color(results['vehicle_1'].vehicle_type))
            ))
            
            fig2.add_trace(go.Scatter(
                x=[f"{v:.2f}" for v in sensitivity2.variation_values],
                y=sensitivity2.lcod_values,
                mode="lines+markers",
                name=f"{results['vehicle_2'].vehicle_name} LCOD",
                marker=dict(size=8),
                line=dict(width=2, color=get_vehicle_type_color(results['vehicle_2'].vehicle_type))
            ))
            
            # Use LCOD from terminology for consistency
            from tco_model.terminology import LCOD
            
            # Update layout with Australian spelling
            fig2.update_layout(
                title=f"{LCOD} Sensitivity to {parameter_options[selected_parameter]}",
                xaxis_title=f"{parameter_options[selected_parameter]} ({get_australian_spelling(sensitivity1.unit)})",
                yaxis_title=f"{get_australian_spelling(LCOD)} ($/km)",
                height=450,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.warning("Sensitivity analysis requires scenario data, which is not available in these results.")
    
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
                              comparison: Optional[ComparisonResult] = None, show_breakeven: bool = True,
                              height: int = 500) -> go.Figure:
    """
    Create cumulative TCO chart with actual data
    
    Args:
        result1: Actual TCO result for vehicle 1
        result2: Actual TCO result for vehicle 2
        comparison: Comparison result object with investment analysis
        show_breakeven: Flag to show breakeven point
        height: Chart height in pixels
        
    Returns:
        Plotly figure with cumulative TCO chart
    """
    # Get actual annual costs
    annual_costs_1 = [cost.total for cost in result1.annual_costs]
    annual_costs_2 = [cost.total for cost in result2.annual_costs]
    
    # Calculate cumulative costs
    cumulative_1 = np.cumsum(annual_costs_1)
    cumulative_2 = np.cumsum(annual_costs_2)
    
    # Create years array
    years = list(range(1, len(annual_costs_1) + 1))
    
    # Create figure
    fig = go.Figure()
    
    # Get vehicle colours from terminology
    from utils.ui_terminology import get_vehicle_type_color
    
    # Add traces
    fig.add_trace(go.Scatter(
        x=years,
        y=cumulative_1,
        mode='lines+markers',
        name=result1.vehicle_name,
        line=dict(color=get_vehicle_type_color(result1.vehicle_type), width=3)
    ))
    
    fig.add_trace(go.Scatter(
        x=years,
        y=cumulative_2,
        mode='lines+markers',
        name=result2.vehicle_name,
        line=dict(color=get_vehicle_type_color(result2.vehicle_type), width=3)
    ))
    
    # Add breakeven point if requested and exists in investment analysis
    if show_breakeven and comparison and hasattr(comparison, 'investment_analysis') and comparison.investment_analysis:
        if comparison.investment_analysis.has_payback:
            payback_year = comparison.investment_analysis.payback_years
            
            # Only show if payback occurs within analysis period
            if payback_year <= len(years):
                # Interpolate costs at payback point
                payback_cost = np.interp(payback_year, years, cumulative_1)
                
                fig.add_trace(go.Scatter(
                    x=[payback_year],
                    y=[payback_cost],
                    mode='markers',
                    marker=dict(size=12, symbol='star', color='green'),
                    name='Breakeven Point',
                    hoverinfo='text',
                    hovertext=f'Breakeven at year {payback_year:.1f}'
                ))
    
    # Update layout using Australian English
    fig.update_layout(
        height=height,
        margin=dict(l=20, r=20, t=30, b=20),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        xaxis_title="Year",
        yaxis_title="Cumulative Cost ($)",
        hovermode="x unified"
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

def create_annual_difference_chart(result1: TCOOutput, result2: TCOOutput, 
                                comparison: ComparisonResult,
                                height: int = 500) -> go.Figure:
    """
    Create chart showing annual cost differences between vehicles
    
    Args:
        result1: TCO result for vehicle 1
        result2: TCO result for vehicle 2
        comparison: Comparison result
        height: Chart height in pixels
        
    Returns:
        Plotly figure with annual cost differences
    """
    # Get annual costs
    annual_costs_1 = [cost.total for cost in result1.annual_costs]
    annual_costs_2 = [cost.total for cost in result2.annual_costs]
    
    # Calculate differences
    differences = [cost2 - cost1 for cost1, cost2 in zip(annual_costs_1, annual_costs_2)]
    
    # Create years array
    years = list(range(1, len(annual_costs_1) + 1))
    
    # Create figure
    fig = go.Figure()
    
    # Colors for cost differences
    positive_color = 'rgba(255, 0, 0, 0.7)'  # Red for higher costs
    negative_color = 'rgba(0, 128, 0, 0.7)'  # Green for lower costs
    
    # Add difference bars with appropriate colors
    colors = [positive_color if diff > 0 else negative_color for diff in differences]
    
    fig.add_trace(go.Bar(
        x=years,
        y=differences,
        marker_color=colors,
        name='Cost Difference',
        text=[f"{diff:+,.0f}" for diff in differences],
        textposition='outside',
        hovertemplate='Year %{x}<br>Difference: $%{y:,.0f}<extra></extra>'
    ))
    
    # Add zero line
    fig.add_shape(
        type='line',
        x0=min(years),
        y0=0,
        x1=max(years),
        y1=0,
        line=dict(color='black', width=1, dash='dash')
    )
    
    # Update layout
    fig.update_layout(
        height=height,
        title="Annual Cost Difference",
        xaxis_title="Year",
        yaxis_title=f"Cost Difference ({result2.vehicle_name} - {result1.vehicle_name})",
        showlegend=False,
        margin=dict(l=20, r=20, t=50, b=20),
    )
    
    # Add annotation explaining the chart
    fig.add_annotation(
        x=0.5,
        y=1.05,
        xref='paper',
        yref='paper',
        text=f"Positive values mean {result2.vehicle_name} costs more; negative values mean {result1.vehicle_name} costs more",
        showarrow=False,
        font=dict(size=10),
        align='center',
    )
    
    return fig 

def has_tipping_point(sensitivity1, sensitivity2):
    """Check if there's a tipping point where TCO curves cross."""
    # Compare first and last TCO difference signs
    first_diff = sensitivity1.tco_values[0] - sensitivity2.tco_values[0]
    last_diff = sensitivity1.tco_values[-1] - sensitivity2.tco_values[-1]
    
    # If signs are different, there's a crossing point
    return (first_diff * last_diff) < 0


def calculate_tipping_point(sensitivity1, sensitivity2):
    """Calculate the parameter value where TCO curves cross."""
    # Find where curves cross
    for i in range(len(sensitivity1.tco_values) - 1):
        diff1 = sensitivity1.tco_values[i] - sensitivity2.tco_values[i]
        diff2 = sensitivity1.tco_values[i+1] - sensitivity2.tco_values[i+1]
        
        # Check if sign changed
        if (diff1 * diff2) < 0:
            # Interpolate to find intersection
            x1 = sensitivity1.variation_values[i]
            x2 = sensitivity1.variation_values[i+1]
            
            # Linear interpolation
            ratio = abs(diff1) / (abs(diff1) + abs(diff2))
            return x1 + ratio * (x2 - x1)
    
    return None 