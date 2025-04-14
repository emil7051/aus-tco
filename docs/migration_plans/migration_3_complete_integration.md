# Migration 3: Complete Integration

## Overview

This final migration phase completes the integration of the TCO model with the UI by implementing:
1. Environmental Impact Analysis integration
2. Live Preview Mode with parameter impact analysis
3. Enhanced report export functionality

This phase builds on the previous migrations to deliver a fully integrated application with no placeholder data.

## Implementation Tasks

### 1. Implement Environmental Impact Analysis Integration

Connect the environmental analysis UI components to the TCO model's emissions data:

```python
# In ui/results/environmental.py

def render_environmental_impact(results):
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
                # Use actual equivalents from emissions data
                trees = result1.emissions.trees_equivalent if co2_diff > 0 else result2.emissions.trees_equivalent
                homes = result1.emissions.homes_equivalent if co2_diff > 0 else result2.emissions.homes_equivalent
                cars = result1.emissions.cars_equivalent if co2_diff > 0 else result2.emissions.cars_equivalent
                
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

def create_emissions_timeline_chart(result1, result2):
    """Create emissions timeline chart with actual emissions data."""
    # Get annual CO2 emissions
    annual_co2_1 = result1.emissions.annual_co2_tonnes
    annual_co2_2 = result2.emissions.annual_co2_tonnes
    
    # Create years array
    years = list(range(1, len(annual_co2_1) + 1))
    
    # Create figure
    fig = go.Figure()
    
    # Add traces with actual annual emissions
    fig.add_trace(go.Bar(
        x=years,
        y=annual_co2_1,
        name=f"{result1.vehicle_name} Emissions",
        marker_color=VEHICLE_COLORS.get(result1.vehicle_type, '#1f77b4')
    ))
    
    fig.add_trace(go.Bar(
        x=years,
        y=annual_co2_2,
        name=f"{result2.vehicle_name} Emissions",
        marker_color=VEHICLE_COLORS.get(result2.vehicle_type, '#ff7f0e')
    ))
    
    # Update layout
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
        yaxis_title="CO2 Emissions (tonnes)",
        barmode='group'
    )
    
    return fig
```

### 2. Implement Live Preview Mode with Parameter Impact Analysis

Connect the live preview mode to the TCO model's sensitivity analysis capabilities:

```python
# In ui/results/live_preview.py

def display_results_in_live_mode(results, comparison, selected_parameter=None):
    """
    Display results in live preview mode with real sensitivity analysis
    
    Args:
        results: Dictionary of actual TCO results
        comparison: Actual comparison result
        selected_parameter: Optional parameter to analyze
    """
    # Get results
    result1 = results["vehicle_1"]
    result2 = results["vehicle_2"]
    
    # Use full width of main panel
    st.markdown("## TCO Analysis Results")
    
    # Create dashboard controls
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
    
    # Display key metrics panel at top with actual data
    from ui.results.metrics import render_key_metrics_panel
    render_key_metrics_panel(results, comparison)
    
    # Render view based on selected mode
    if view_mode == "Parameter Impact":
        # Show parameter impact analysis with actual sensitivity analysis
        if selected_parameter:
            show_parameter_impact(selected_parameter, results, comparison)
        else:
            render_parameter_selection_interface(results, comparison)
    else:
        # Other views handled by existing functions...
        # (Summary and Detailed views were integrated in Migration 2)
        pass

def show_parameter_impact(parameter, results, comparison):
    """
    Show parameter impact analysis using actual sensitivity analysis
    
    Args:
        parameter: Parameter to analyze
        results: Dictionary of actual TCO results
        comparison: Actual comparison result
    """
    st.subheader(f"Parameter Impact Analysis: {parameter}")
    
    # Get calculator
    from tco_model.calculator import TCOCalculator
    calculator = TCOCalculator()
    
    # Get scenarios
    scenario1 = results["vehicle_1"].scenario
    scenario2 = results["vehicle_2"].scenario
    
    # Define variations (based on parameter type)
    parameter_info = get_parameter_variation_info(parameter, scenario1, scenario2)
    
    # Perform sensitivity analysis with actual model
    sensitivity1 = calculator.perform_sensitivity_analysis(
        scenario1,
        parameter,
        parameter_info["variations"]
    )
    
    sensitivity2 = calculator.perform_sensitivity_analysis(
        scenario2,
        parameter,
        parameter_info["variations"]
    )
    
    # Create visualization with actual sensitivity data
    fig = create_parameter_impact_chart(sensitivity1, sensitivity2, parameter_info)
    st.plotly_chart(fig, use_container_width=True)
    
    # Show insights
    st.markdown(f"""
    ### Key Insights
    
    {generate_sensitivity_insights(sensitivity1, sensitivity2, results)}
    """)
    
    # Show tipping point if it exists
    if parameter_info["has_tipping_point"]:
        tipping_point = calculate_tipping_point(sensitivity1, sensitivity2)
        if tipping_point:
            st.info(f"""
            **Tipping Point**: When {parameter} reaches {tipping_point:.2f} {parameter_info['unit']}, 
            the more cost-effective vehicle switches.
            """)
```

### 3. Implement Enhanced Results Export

Enhance the export functionality to include all TCO model data:

```python
# In ui/results/utils.py

def generate_results_export(results, comparison):
    """
    Generate Excel export with all TCO model data
    
    Args:
        results: Dictionary of actual TCO results
        comparison: Actual comparison result
        
    Returns:
        Excel file content as bytes
    """
    import io
    import pandas as pd
    import numpy as np
    from openpyxl import Workbook
    from openpyxl.utils.dataframe import dataframe_to_rows
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    
    # Create workbook
    wb = Workbook()
    
    # Remove default sheet
    default_sheet = wb.active
    wb.remove(default_sheet)
    
    # Create sheets
    summary_sheet = wb.create_sheet("Summary")
    annual_sheet = wb.create_sheet("Annual Costs")
    components_sheet = wb.create_sheet("Cost Components")
    emissions_sheet = wb.create_sheet("Emissions")
    params_sheet = wb.create_sheet("Parameters")
    
    # Get results
    result1 = results["vehicle_1"]
    result2 = results["vehicle_2"]
    
    # --- Summary Sheet ---
    summary_data = [
        ["TCO Analysis Results", "", ""],
        ["", "", ""],
        ["Metric", result1.vehicle_name, result2.vehicle_name],
        ["Total TCO", result1.total_tco, result2.total_tco],
        ["Cost per km", result1.lcod, result2.lcod],
        ["Total CO2 (tonnes)", result1.emissions.total_co2_tonnes, result2.emissions.total_co2_tonnes],
        ["CO2 per km (g/km)", result1.emissions.co2_per_km, result2.emissions.co2_per_km],
        ["", "", ""],
        ["Comparison", "", ""],
        ["Cheaper option", comparison.cheaper_option == 1 and result1.vehicle_name or result2.vehicle_name, ""],
        ["TCO difference", abs(comparison.tco_difference), f"{abs(comparison.tco_percentage):.1f}%"],
        ["", "", ""],
        ["Investment Analysis", "", ""],
    ]
    
    # Add investment analysis if available
    if comparison.investment_analysis:
        investment = comparison.investment_analysis
        summary_data.extend([
            ["Payback period", investment.has_payback and f"{investment.payback_years:.1f} years" or "No payback", ""],
            ["ROI", investment.roi and f"{investment.roi:.1f}%" or "N/A", ""],
            ["IRR", investment.irr and f"{investment.irr:.1f}%" or "N/A", ""],
        ])
    
    # Add summary data to sheet
    for row in summary_data:
        summary_sheet.append(row)
    
    # --- Annual Costs Sheet ---
    years = list(range(1, max(len(result1.annual_costs), len(result2.annual_costs)) + 1))
    annual_data = {
        "Year": years,
        f"{result1.vehicle_name} Costs": result1.annual_costs + [0] * (len(years) - len(result1.annual_costs)),
        f"{result2.vehicle_name} Costs": result2.annual_costs + [0] * (len(years) - len(result2.annual_costs)),
    }
    annual_df = pd.DataFrame(annual_data)
    
    # Add to sheet
    for row in dataframe_to_rows(annual_df, index=False, header=True):
        annual_sheet.append(row)
    
    # --- Cost Components Sheet ---
    from tco_model.calculator import TCOCalculator
    calculator = TCOCalculator()
    from tco_model.terminology import UI_COMPONENT_KEYS, UI_COMPONENT_LABELS
    
    # Get component values
    component_data = {"Component": [UI_COMPONENT_LABELS.get(k, k) for k in UI_COMPONENT_KEYS]}
    component_data[result1.vehicle_name] = [calculator.get_component_value(result1, k) for k in UI_COMPONENT_KEYS]
    component_data[result2.vehicle_name] = [calculator.get_component_value(result2, k) for k in UI_COMPONENT_KEYS]
    component_data["Difference"] = [v2 - v1 for v1, v2 in zip(component_data[result1.vehicle_name], component_data[result2.vehicle_name])]
    
    component_df = pd.DataFrame(component_data)
    
    # Add to sheet
    for row in dataframe_to_rows(component_df, index=False, header=True):
        components_sheet.append(row)
    
    # --- Emissions Sheet ---
    emissions_data = {
        "Year": years,
        f"{result1.vehicle_name} CO2 (tonnes)": result1.emissions.annual_co2_tonnes + [0] * (len(years) - len(result1.emissions.annual_co2_tonnes)),
        f"{result2.vehicle_name} CO2 (tonnes)": result2.emissions.annual_co2_tonnes + [0] * (len(years) - len(result2.emissions.annual_co2_tonnes)),
    }
    emissions_df = pd.DataFrame(emissions_data)
    
    # Add to sheet
    for row in dataframe_to_rows(emissions_df, index=False, header=True):
        emissions_sheet.append(row)
    
    # --- Parameters Sheet ---
    # Extract parameters from scenarios
    scenario1 = result1.scenario
    scenario2 = result2.scenario
    
    # Get common parameters
    common_params = {attr: getattr(scenario1, attr, None) for attr in dir(scenario1) 
                   if not attr.startswith('_') and not callable(getattr(scenario1, attr, None))}
    
    param_data = {"Parameter": [], result1.vehicle_name: [], result2.vehicle_name: []}
    
    for param, value in common_params.items():
        if param not in ["name", "vehicle_type"]:
            param_data["Parameter"].append(param)
            param_data[result1.vehicle_name].append(getattr(scenario1, param, None))
            param_data[result2.vehicle_name].append(getattr(scenario2, param, None))
    
    param_df = pd.DataFrame(param_data)
    
    # Add to sheet
    for row in dataframe_to_rows(param_df, index=False, header=True):
        params_sheet.append(row)
    
    # Apply styling (header fonts, column widths, etc.)
    # ...
    
    # Save to bytes buffer
    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    
    return buffer.getvalue()
```

### 4. Remove All Remaining Placeholders

Search for and remove any remaining placeholders:

```bash
# Command line
grep -r "placeholder" ./ui/results/
```

Replace any found placeholder data with actual model data.

## Integration Tests

Create comprehensive tests to verify the complete integration:

```python
# In tests/test_complete_integration.py

def test_environmental_integration():
    """Test that environmental components use actual emissions data."""
    # Create test data with emissions
    from tco_model.calculator import TCOCalculator
    calculator = TCOCalculator()
    
    # Create scenarios and calculate
    bet_scenario = create_test_bet_scenario()
    diesel_scenario = create_test_diesel_scenario()
    
    bet_result = calculator.calculate(bet_scenario)
    diesel_result = calculator.calculate(diesel_scenario)
    
    results = {
        "vehicle_1": bet_result,
        "vehicle_2": diesel_result
    }
    
    # Verify emissions data exists
    assert bet_result.emissions is not None
    assert diesel_result.emissions is not None
    
    # Test CO2 timeline creation
    from ui.results.environmental import create_emissions_timeline_chart
    fig = create_emissions_timeline_chart(bet_result, diesel_result)
    
    # Verify chart has data from both vehicles
    assert len(fig.data) == 2
    assert len(fig.data[0].y) == len(bet_result.emissions.annual_co2_tonnes)
    assert len(fig.data[1].y) == len(diesel_result.emissions.annual_co2_tonnes)

def test_sensitivity_analysis_integration():
    """Test that sensitivity analysis is correctly integrated."""
    # Create test data
    from tco_model.calculator import TCOCalculator
    calculator = TCOCalculator()
    
    # Create scenarios
    bet_scenario = create_test_bet_scenario()
    
    # Perform sensitivity analysis
    parameter = "electricity_price"
    variations = [0.15, 0.20, 0.25, 0.30, 0.35]
    
    sensitivity = calculator.perform_sensitivity_analysis(
        bet_scenario,
        parameter,
        variations
    )
    
    # Verify results
    assert len(sensitivity.variation_values) == 5
    assert len(sensitivity.tco_values) == 5
    
    # Test parameter impact visualization
    from ui.results.live_preview import create_parameter_impact_chart
    parameter_info = {
        "name": "Electricity Price",
        "unit": "$/kWh",
        "variations": variations,
        "has_tipping_point": True
    }
    
    # Create chart with actual sensitivity data
    fig = create_parameter_impact_chart(sensitivity, sensitivity, parameter_info)
    
    # Verify chart has correct data
    assert len(fig.data) == 2
    assert len(fig.data[0].x) == len(variations)
    assert len(fig.data[0].y) == len(sensitivity.tco_values)

def test_export_functionality():
    """Test that export includes all TCO model data."""
    # Create test data
    from tco_model.calculator import TCOCalculator
    calculator = TCOCalculator()
    
    # Create scenarios and calculate
    bet_scenario = create_test_bet_scenario()
    diesel_scenario = create_test_diesel_scenario()
    
    bet_result = calculator.calculate(bet_scenario)
    diesel_result = calculator.calculate(diesel_scenario)
    comparison = calculator.compare(bet_result, diesel_result)
    
    results = {
        "vehicle_1": bet_result,
        "vehicle_2": diesel_result
    }
    
    # Generate export
    from ui.results.utils import generate_results_export
    export_data = generate_results_export(results, comparison)
    
    # Verify export data is not empty
    assert export_data is not None
    assert len(export_data) > 0
    
    # Further analysis would require parsing the Excel file
    # but this at least verifies the export runs with actual data
```

## Final Verification

After implementing all three migrations, verify the complete integration:

1. Test creating and comparing BET and diesel vehicles
2. Verify all visualizations use actual TCO model data
3. Confirm that sensitivity analysis works in live preview mode
4. Ensure environmental impact analysis shows actual emissions data
5. Verify Excel export includes all TCO model data

## Expected Results

The completed integration will provide:

1. Fully integrated TCO model with all UI components
2. Actual environmental impact analysis with emissions data
3. Real-time parameter impact analysis with sensitivity curves
4. Comprehensive data export with all model details
5. No remaining placeholder or dummy data

All functionality will be directly tied to the TCO model, providing accurate and consistent analysis throughout the application. 