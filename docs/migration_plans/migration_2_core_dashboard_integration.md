# Migration 2: Core Dashboard Integration

## Overview

This migration phase integrates the Key Metrics Panel and Standard Dashboard views with the enhanced TCO model implemented in Migration 1. This phase focuses on the core visualisation components that present TCO results.

## Implementation Tasks

### 1. Update Key Metrics Panel

Modify the Key Metrics Panel to use actual TCO model data:

```python
# In ui/results/metrics.py

def render_key_metrics_panel(results, comparison):
    """
    Render an interactive key metrics panel with insights
    
    Args:
        results: Dictionary of TCO result objects with actual model data
        comparison: Comparison result object with investment analysis
    """
    # Get results for each vehicle
    result1 = results["vehicle_1"]
    result2 = results["vehicle_2"]
    
    # Format metrics with actual data
    total_tco_1 = format_currency(result1.total_tco)
    total_tco_2 = format_currency(result2.total_tco)
    lcod_1 = f"{format_currency(result1.lcod)}/km"
    lcod_2 = f"{format_currency(result2.lcod)}/km"
    
    # Get actual cost difference data
    cheaper_vehicle = result1.vehicle_name if comparison.cheaper_option == 1 else result2.vehicle_name
    saving_amount = format_currency(abs(comparison.tco_difference))
    saving_percent = f"{abs(comparison.tco_percentage):.1f}%"
    
    # Get actual investment analysis data
    payback_info = get_payback_information(result1, result2, comparison)
    
    # Create metrics container
    st.markdown('<div class="metrics-panel">', unsafe_allow_html=True)
    
    # Create TCO comparison card
    col1, col2, col3 = st.columns(3)
    
    # TCO Comparison card
    with col1:
        with st.container():
            st.markdown('<div class="metric-card comparison">', unsafe_allow_html=True)
            
            # Use TCO from terminology
            from tco_model.terminology import TCO
            st.markdown(f"#### {TCO}")
            
            # Create comparison visualisation with actual data
            fig = create_tco_comparison_visualisation(result1, result2, comparison)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            
            # Key insight with actual data
            st.markdown(f"""
            <div class="metric-insight">
                <span class="highlight">{cheaper_vehicle}</span> is {saving_percent} cheaper
                <br>Saving <span class="highlight">{saving_amount}</span> over lifetime
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Cost per km card with actual data
    with col2:
        with st.container():
            st.markdown('<div class="metric-card lcod">', unsafe_allow_html=True)
            
            # Use LCOD from terminology
            from tco_model.terminology import LCOD
            st.markdown(f"#### {LCOD}")
            
            # Create LCOD comparison with actual data
            fig = create_lcod_comparison_visualisation(result1, result2, comparison)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            
            # Key insight with actual data
            lcod_diff = format_currency(abs(comparison.lcod_difference))
            lcod_pct = f"{abs(comparison.lcod_difference_percentage):.1f}%"
            lcod_comparison = "lower" if comparison.cheaper_option == 1 else "higher"
            
            st.markdown(f"""
            <div class="metric-insight">
                <span class="highlight">{lcod_diff}/km</span> difference
                <br>{lcod_pct} {lcod_comparison} cost per km
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Payback period card with actual investment analysis
    with col3:
        with st.container():
            st.markdown('<div class="metric-card payback">', unsafe_allow_html=True)
            st.markdown("#### Investment Analysis")
            
            if payback_info["has_payback"]:
                # Create visualisation with actual investment data
                fig = create_payback_visualisation(payback_info)
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                
                # Key insight with actual ROI and payback data
                st.markdown(f"""
                <div class="metric-insight">
                    Payback in <span class="highlight">{payback_info['years']:.1f} years</span>
                    <br>ROI: {payback_info['roi']:.1f}% over lifetime
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="no-payback-message">
                    <i class="fas fa-info-circle"></i>
                    No payback occurs within the analysis period
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def get_payback_information(result1, result2, comparison):
    """
    Extract payback information from actual investment analysis.
    
    Args:
        result1: TCO result for vehicle 1
        result2: TCO result for vehicle 2
        comparison: Comparison result with investment analysis
        
    Returns:
        Dictionary with formatted payback information
    """
    # Use the actual investment analysis from comparison
    if comparison.investment_analysis:
        return {
            "has_payback": comparison.investment_analysis.has_payback,
            "years": comparison.investment_analysis.payback_years or 0,
            "roi": comparison.investment_analysis.roi or 0,
            "irr": comparison.investment_analysis.irr,
            "analysis_period": result1.analysis_period_years
        }
    
    # Fallback to default values if no investment analysis available
    return {
        "has_payback": False,
        "years": 0,
        "roi": 0,
        "irr": None,
        "analysis_period": result1.analysis_period_years
    }
```

### 2. Update Financial Overview Charts

Modify the financial visualisation components to use actual TCO model data:

```python
# In ui/results/charts.py

def create_cumulative_tco_chart(result1, result2, comparison=None, show_breakeven=True):
    """
    Create cumulative TCO chart with actual data
    
    Args:
        result1: Actual TCO result for vehicle 1
        result2: Actual TCO result for vehicle 2
        comparison: Comparison result object with investment analysis
        show_breakeven: Flag to show breakeven point
        
    Returns:
        Plotly figure with cumulative TCO chart
    """
    # Get actual annual costs
    annual_costs_1 = result1.annual_costs
    annual_costs_2 = result2.annual_costs
    
    # Calculate cumulative costs
    cumulative_1 = [sum(annual_costs_1[:i+1]) for i in range(len(annual_costs_1))]
    cumulative_2 = [sum(annual_costs_2[:i+1]) for i in range(len(annual_costs_2))]
    
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
        height=400,
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
```

### 3. Update Cost Component Breakdown

Modify the cost breakdown visualisations to use actual TCO model data:

```python
# In ui/results/dashboard.py

def render_cost_breakdown(results, comparison):
    """
    Render cost breakdown analysis with actual TCO data
    
    Args:
        results: Dictionary of actual TCO result objects
        comparison: Actual comparison result object
    """
    st.subheader("Cost Factors Analysis")
    
    # Get UI component keys from terminology
    from tco_model.terminology import UI_COMPONENT_KEYS, UI_COMPONENT_LABELS
    
    # Create interactive selector
    selected_component = st.selectbox(
        "Select cost component to analyse",
        options=UI_COMPONENT_KEYS,
        format_func=lambda x: UI_COMPONENT_LABELS[x]
    )
    
    # Create two-column layout
    col1, col2 = st.columns(2)
    
    with col1:
        # Get component details from actual TCO results
        component_details = get_component_details(results, selected_component)
        
        # Create component chart with actual data
        fig = create_component_details_chart(component_details)
        st.plotly_chart(fig, use_container_width=True)
        
        # Generate insights from actual data
        insights = generate_component_insights(component_details, comparison)
        st.markdown(f"""
        <div class="component-insights">
            <h4>Key Insights</h4>
            <ul>
                {insights}
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Show key drivers with actual data
        st.markdown(f"### Key Drivers of {UI_COMPONENT_LABELS[selected_component]}")
        
        # Display appropriate drivers visualisation based on component
        if selected_component == "energy":
            render_energy_cost_drivers(results)
        elif selected_component == "maintenance":
            render_maintenance_cost_drivers(results)
        elif selected_component == "acquisition":
            render_acquisition_cost_drivers(results)
        elif selected_component == "residual_value":
            render_residual_value_drivers(results)
        else:
            # Generic drivers visualisation with actual data
            render_generic_cost_drivers(results, selected_component)

def get_component_details(results, component):
    """
    Get component details from actual TCO results.
    
    Args:
        results: Dictionary of TCO results
        component: Component key from UI_COMPONENT_KEYS
        
    Returns:
        Dictionary with component details for visualisation
    """
    from tco_model.calculator import TCOCalculator
    from tco_model.terminology import UI_TO_MODEL_COMPONENT_MAPPING
    
    calculator = TCOCalculator()
    
    result1 = results["vehicle_1"]
    result2 = results["vehicle_2"]
    
    # Get component values using calculator methods
    value1 = calculator.get_component_value(result1, component)
    value2 = calculator.get_component_value(result2, component)
    
    # Get component percentages
    percentage1 = calculator.get_component_percentage(result1, component)
    percentage2 = calculator.get_component_percentage(result2, component)
    
    # Get detailed breakdown if available
    breakdown1 = {}
    breakdown2 = {}
    
    detailed_breakdown1 = calculator.calculate_component_breakdown(result1)
    detailed_breakdown2 = calculator.calculate_component_breakdown(result2)
    
    if component in detailed_breakdown1:
        breakdown1 = detailed_breakdown1[component]
    
    if component in detailed_breakdown2:
        breakdown2 = detailed_breakdown2[component]
    
    # Get component colour from UI terminology
    from utils.ui_terminology import get_component_color
    color = get_component_color(component)
    
    return {
        "component": component,
        "color": color,
        "vehicle_1": {
            "name": result1.vehicle_name,
            "value": value1,
            "percentage": percentage1,
            "breakdown": breakdown1
        },
        "vehicle_2": {
            "name": result2.vehicle_name,
            "value": value2,
            "percentage": percentage2,
            "breakdown": breakdown2
        },
        "difference": value2 - value1,
        "difference_percentage": (value2 - value1) / value1 * 100 if value1 != 0 else 0
    }

def generate_component_insights(component_details, comparison):
    """
    Generate insights from component details using Australian spelling.
    
    Args:
        component_details: Component details from get_component_details
        comparison: Comparison result
        
    Returns:
        HTML string with insights
    """
    component = component_details["component"]
    value1 = component_details["vehicle_1"]["value"]
    value2 = component_details["vehicle_2"]["value"]
    name1 = component_details["vehicle_1"]["name"]
    name2 = component_details["vehicle_2"]["name"]
    diff = component_details["difference"]
    diff_pct = component_details["difference_percentage"]
    
    # Get nice formatting
    from utils.formatting import format_currency, format_percentage
    
    insights = []
    
    # Component-specific insights based on Australian terminology
    if component == "energy":
        insights.append(f"<li>{name1}'s energy costs are {format_currency(value1)}, while {name2}'s are {format_currency(value2)}</li>")
        
        if diff != 0:
            cheaper = name1 if diff > 0 else name2
            savings = format_currency(abs(diff))
            insights.append(f"<li>{cheaper} has {format_percentage(abs(diff_pct))} lower energy costs, saving {savings}</li>")
    
    elif component == "maintenance":
        insights.append(f"<li>Maintenance costs are {format_currency(value1)} for {name1} and {format_currency(value2)} for {name2}</li>")
        
        if diff != 0:
            cheaper = name1 if diff > 0 else name2
            savings = format_currency(abs(diff))
            insights.append(f"<li>{cheaper} has {format_percentage(abs(diff_pct))} lower maintenance costs, saving {savings}</li>")
    
    # Add more component-specific insights with Australian spelling
    
    # Generic insight if no specific ones were added
    if not insights:
        if diff != 0:
            cheaper = name1 if diff > 0 else name2
            savings = format_currency(abs(diff))
            insights.append(f"<li>{cheaper} has {format_percentage(abs(diff_pct))} lower {component.replace('_', ' ')} costs, a difference of {savings}</li>")
    
    return "".join(insights)
```

### 4. Update Annual Timeline Analysis

Modify the timeline visualisation to use actual TCO model data:

```python
# In ui/results/dashboard.py

def render_annual_timeline(results, comparison):
    """
    Render annual timeline analysis with actual TCO data
    
    Args:
        results: Dictionary of actual TCO result objects
        comparison: Actual comparison result object
    """
    st.subheader("Annual Cost Timeline")
    
    # Get results
    result1 = results["vehicle_1"]
    result2 = results["vehicle_2"]
    
    # Get actual annual costs
    annual_costs_1 = result1.annual_costs
    annual_costs_2 = result2.annual_costs
    
    # Create display options
    view_options = st.radio(
        "View",
        options=["Total Annual Costs", "Cost Difference", "Cumulative Costs"],
        horizontal=True
    )
    
    show_components = st.checkbox("Show cost components", value=False)
    
    # Create visualisation based on selected view
    if view_options == "Total Annual Costs":
        fig = create_annual_costs_chart(
            result1,
            result2,
            show_components=show_components
        )
    elif view_options == "Cost Difference":
        fig = create_annual_difference_chart(
            result1,
            result2,
            comparison
        )
    else:  # Cumulative Costs
        fig = create_cumulative_tco_chart(
            result1,
            result2,
            comparison,
            show_breakeven=True
        )
    
    # Display the chart
    st.plotly_chart(fig, use_container_width=True)
    
    # Add insights based on actual data
    with st.expander("Annual Cost Insights"):
        insights = generate_annual_cost_insights(result1, result2, comparison)
        st.markdown(f"""
        ### Key Annual Cost Insights
        
        {insights}
        """)

def create_annual_costs_chart(result1, result2, show_components=False):
    """
    Create annual costs chart with actual data.
    
    Args:
        result1: TCO result for vehicle 1
        result2: TCO result for vehicle 2
        show_components: Whether to show cost components
        
    Returns:
        Plotly figure with annual costs
    """
    # Get annual costs
    annual_costs_1 = result1.annual_costs
    annual_costs_2 = result2.annual_costs
    
    # Create years array
    years = list(range(1, max(len(annual_costs_1), len(annual_costs_2)) + 1))
    
    # Create figure
    fig = go.Figure()
    
    # Get vehicle colours
    from utils.ui_terminology import get_vehicle_type_color
    color1 = get_vehicle_type_color(result1.vehicle_type)
    color2 = get_vehicle_type_color(result2.vehicle_type)
    
    if show_components:
        # Get component breakdown by year
        from tco_model.calculator import TCOCalculator
        calculator = TCOCalculator()
        from tco_model.terminology import UI_COMPONENT_KEYS, UI_COMPONENT_MAPPING
        
        # For each component, add a trace per vehicle
        for component in UI_COMPONENT_KEYS:
            if component == "residual_value":
                continue  # Skip residual value for annual breakdown
            
            # Get component colour
            component_color = UI_COMPONENT_MAPPING[component].get("color", "#cccccc")
            
            # Get annual values for this component using UI_TO_MODEL_COMPONENT_MAPPING
            component_value_1 = calculator.get_component_value(result1, component)
            component_value_2 = calculator.get_component_value(result2, component)
            
            component_annual_1 = [component_value_1 / len(annual_costs_1)] * len(annual_costs_1)
            component_annual_2 = [component_value_2 / len(annual_costs_2)] * len(annual_costs_2)
            
            # Add component traces
            fig.add_trace(go.Bar(
                x=years[:len(annual_costs_1)],
                y=component_annual_1,
                name=f"{result1.vehicle_name} - {UI_COMPONENT_MAPPING[component]['display_label']}",
                marker_color=component_color,
                opacity=0.7,
                legendgroup=result1.vehicle_name
            ))
            
            fig.add_trace(go.Bar(
                x=years[:len(annual_costs_2)],
                y=component_annual_2,
                name=f"{result2.vehicle_name} - {UI_COMPONENT_MAPPING[component]['display_label']}",
                marker_color=component_color,
                opacity=0.9,
                legendgroup=result2.vehicle_name
            ))
    else:
        # Simple bar chart without components
        fig.add_trace(go.Bar(
            x=years[:len(annual_costs_1)],
            y=annual_costs_1,
            name=result1.vehicle_name,
            marker_color=color1
        ))
        
        fig.add_trace(go.Bar(
            x=years[:len(annual_costs_2)],
            y=annual_costs_2,
            name=result2.vehicle_name,
            marker_color=color2
        ))
    
    # Update layout
    fig.update_layout(
        height=500,
        barmode='group',
        xaxis_title="Year",
        yaxis_title="Annual Cost ($)",
        legend=dict(
            orientation="h", 
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

def generate_annual_cost_insights(result1, result2, comparison):
    """
    Generate insights from annual cost analysis with Australian English.
    
    Args:
        result1: TCO result for vehicle 1
        result2: TCO result for vehicle 2
        comparison: Comparison result
        
    Returns:
        String with insights using Australian spelling
    """
    # Get annual costs
    annual_costs_1 = result1.annual_costs
    annual_costs_2 = result2.annual_costs
    
    # Format currency values
    from utils.formatting import format_currency
    
    insights = []
    
    # Initial costs
    if len(annual_costs_1) > 0 and len(annual_costs_2) > 0:
        year1_diff = annual_costs_2[0] - annual_costs_1[0]
        cheaper_initial = result1.vehicle_name if year1_diff > 0 else result2.vehicle_name
        insights.append(f"* In the first year, {cheaper_initial} has lower costs by {format_currency(abs(year1_diff))}")
    
    # Long-term trends
    if len(annual_costs_1) > 5 and len(annual_costs_2) > 5:
        later_years_1 = sum(annual_costs_1[5:]) / len(annual_costs_1[5:])
        later_years_2 = sum(annual_costs_2[5:]) / len(annual_costs_2[5:])
        later_diff = later_years_2 - later_years_1
        cheaper_later = result1.vehicle_name if later_diff > 0 else result2.vehicle_name
        insights.append(f"* After year 5, {cheaper_later} has lower average annual costs by {format_currency(abs(later_diff))}")
    
    # Payback related insight
    if comparison.investment_analysis and comparison.investment_analysis.has_payback:
        payback_year = comparison.investment_analysis.payback_years
        insights.append(f"* The higher initial investment is recovered in year {payback_year:.1f}")
    
    return "\n".join(insights)
```

## Testing and Verification

To test that the UI components correctly integrate with the TCO model:

```python
# In tests/test_ui_integration.py

def test_metrics_panel_integration():
    """Test that key metrics panel correctly uses TCO model data."""
    # Create test scenario
    from tco_model.calculator import TCOCalculator
    from tco_model.models import ScenarioInput
    
    calculator = TCOCalculator()
    
    # Create test scenarios with proper vehicle types
    scenario1 = ScenarioInput(
        vehicle_type="battery_electric",
        name="Test Electric",
        annual_distance=100000,
        analysis_period=8,
        # Other required parameters
    )
    
    scenario2 = ScenarioInput(
        vehicle_type="diesel",
        name="Test Diesel",
        annual_distance=100000,
        analysis_period=8,
        # Other required parameters
    )
    
    # Calculate results
    result1 = calculator.calculate(scenario1)
    result2 = calculator.calculate(scenario2)
    comparison = calculator.compare(result1, result2)
    
    results = {
        "vehicle_1": result1,
        "vehicle_2": result2
    }
    
    # Test integration by verifying the values used in payback information
    from ui.results.metrics import get_payback_information
    payback_info = get_payback_information(result1, result2, comparison)
    
    # Verify payback info matches investment analysis
    assert payback_info["has_payback"] == comparison.investment_analysis.has_payback
    if comparison.investment_analysis.payback_years:
        assert payback_info["years"] == comparison.investment_analysis.payback_years
    assert payback_info["roi"] == comparison.investment_analysis.roi or 0
    
    # Test component details extraction
    from ui.results.dashboard import get_component_details
    from tco_model.terminology import UI_COMPONENT_KEYS
    
    # Test each component
    for component in UI_COMPONENT_KEYS:
        details = get_component_details(results, component)
        
        # Verify structure
        assert "component" in details
        assert details["component"] == component
        assert "vehicle_1" in details
        assert "vehicle_2" in details
        assert "difference" in details
        
        # Verify values
        vehicle1_value = details["vehicle_1"]["value"]
        vehicle2_value = details["vehicle_2"]["value"]
        
        # Compare with TCO calculator's component value
        calculator_value1 = calculator.get_component_value(result1, component)
        calculator_value2 = calculator.get_component_value(result2, component)
        
        assert abs(vehicle1_value - calculator_value1) < 0.01
        assert abs(vehicle2_value - calculator_value2) < 0.01
```

## Expected Outputs

After implementing this migration:

1. The Key Metrics Panel will display actual TCO results, cost differences, and investment analysis
2. The Financial Overview will show actual cumulative costs and breakeven points
3. The Cost Breakdown will display actual component costs with detailed sub-components
4. The Annual Timeline will visualise actual annual costs across the analysis period

All visualisations will be directly connected to the TCO model following Australian terminology standards, with no placeholder data. 