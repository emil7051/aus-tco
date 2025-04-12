"""
Detailed Cost Breakdown Module

This module renders detailed cost breakdowns for TCO results, providing granular
views of costs by year and component.
"""

import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional

from tco_model.models import TCOOutput, ComparisonResult
from utils.helpers import format_currency, format_percentage
from ui.results.utils import (
    COMPONENT_KEYS, COMPONENT_LABELS, get_component_value, 
    get_annual_component_value
)


def render_detailed_breakdown(results: Dict[str, TCOOutput], comparison: ComparisonResult):
    """
    Render detailed cost breakdowns for TCO results.
    
    Args:
        results: Dictionary containing TCO results for each vehicle
        comparison: The comparison result between the two vehicles
    """
    if not results or "vehicle_1" not in results or "vehicle_2" not in results:
        st.warning("No valid results available for detailed breakdown.")
        return
        
    # Extract results
    result1 = results["vehicle_1"]
    result2 = results["vehicle_2"]
    
    # Create tabs for different detailed views
    detailed_tabs = st.tabs([
        "Year-by-Year Breakdown", 
        "Component Details",
        "Cost Per Kilometer"
    ])
    
    # Year-by-Year breakdown tab
    with detailed_tabs[0]:
        render_yearly_breakdown(result1, result2)
    
    # Component details tab
    with detailed_tabs[1]:
        render_component_details(result1, result2)
    
    # Cost per kilometer tab
    with detailed_tabs[2]:
        render_cost_per_km(result1, result2)


def render_yearly_breakdown(result1: TCOOutput, result2: TCOOutput):
    """
    Render a year-by-year breakdown of all costs.
    
    Args:
        result1: TCO result for the first vehicle
        result2: TCO result for the second vehicle
    """
    st.subheader("Year-by-Year Cost Breakdown")
    
    # Create vehicle selection
    selected_vehicle = st.radio(
        "Select Vehicle",
        [result1.vehicle_name, result2.vehicle_name],
        horizontal=True
    )
    
    # Determine which result to display
    result = result1 if selected_vehicle == result1.vehicle_name else result2
    
    # Create DataFrame with all annual costs
    years = range(result.analysis_period_years)
    
    # Define components to show in the yearly breakdown
    components = [
        "acquisition",
        "energy",
        "maintenance",
        "infrastructure",
        "battery_replacement",
        "insurance",
        "registration",
        "carbon_tax",
        "other_taxes",
        "residual_value"
    ]
    
    # Create data dictionary
    data = {
        "Year": list(years),
        "Calendar Year": [result.annual_costs[year].calendar_year for year in years],
    }
    
    # Add component data
    for comp in components:
        # Convert snake_case to Title Case for display
        label = " ".join(word.capitalize() for word in comp.split("_"))
        data[label] = [get_annual_component_value(result, comp, year) for year in years]
    
    # Add total row
    data["Total"] = [result.annual_costs[year].total for year in years]
    
    df = pd.DataFrame(data)
    
    # Format currency values
    for col in df.columns:
        if col not in ["Year", "Calendar Year"]:
            df[col] = df[col].apply(format_currency)
    
    # Display the table
    st.dataframe(df, use_container_width=True)
    
    # Download button
    csv = df.to_csv(index=False)
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name=f"{result.vehicle_name}_yearly_breakdown.csv",
        mime="text/csv",
    )


def render_component_details(result1: TCOOutput, result2: TCOOutput):
    """
    Render detailed analysis of specific cost components.
    
    Args:
        result1: TCO result for the first vehicle
        result2: TCO result for the second vehicle
    """
    st.subheader("Cost Component Details")
    
    # Create component selection using display-friendly names
    component_options = {
        "acquisition": "Acquisition",
        "energy": "Energy",
        "maintenance": "Maintenance",
        "infrastructure": "Infrastructure",
        "battery_replacement": "Battery Replacement",
        "insurance": "Insurance", 
        "registration": "Registration",
        "taxes_levies": "Taxes",  # Special handling
        "residual_value": "Residual Value"
    }
    
    selected_display_name = st.selectbox(
        "Select Cost Component",
        list(component_options.values())
    )
    
    # Map display name back to component key
    selected_component = None
    for key, display_name in component_options.items():
        if display_name == selected_display_name:
            selected_component = key
            break
    
    if not selected_component:
        st.error("Component selection error")
        return
    
    # Create comparison data for the selected component
    years = range(result1.analysis_period_years)
    
    # Handle special case for taxes which combines multiple fields
    if selected_component == "taxes_levies":
        data = {
            "Year": list(years),
            f"{result1.vehicle_name}": [get_annual_component_value(result1, "taxes_levies", year) for year in years],
            f"{result2.vehicle_name}": [get_annual_component_value(result2, "taxes_levies", year) for year in years],
            "Difference": [get_annual_component_value(result2, "taxes_levies", year) - 
                          get_annual_component_value(result1, "taxes_levies", year) for year in years]
        }
    else:
        # For other components, use the component key directly
        data = {
            "Year": list(years),
            f"{result1.vehicle_name}": [get_annual_component_value(result1, selected_component, year) for year in years],
            f"{result2.vehicle_name}": [get_annual_component_value(result2, selected_component, year) for year in years],
            "Difference": [get_annual_component_value(result2, selected_component, year) - 
                          get_annual_component_value(result1, selected_component, year) for year in years]
        }
    
    df = pd.DataFrame(data)
    
    # Format currency values for all except Year column
    for col in df.columns:
        if col != "Year":
            df[col] = df[col].apply(format_currency)
    
    # Display table
    st.dataframe(df, use_container_width=True)
    
    # NPV of this component
    st.subheader(f"NPV of {selected_display_name}")
    
    # Get NPV values using component getter for consistency
    npv1 = get_component_value(result1, selected_component)
    npv2 = get_component_value(result2, selected_component)
    npv_diff = npv2 - npv1
    
    npv_data = {
        "Vehicle": [result1.vehicle_name, result2.vehicle_name, "Difference"],
        f"NPV of {selected_display_name}": [npv1, npv2, npv_diff]
    }
    
    npv_df = pd.DataFrame(npv_data)
    npv_df[f"NPV of {selected_display_name}"] = npv_df[f"NPV of {selected_display_name}"].apply(format_currency)
    
    st.dataframe(npv_df, use_container_width=True)


def render_cost_per_km(result1: TCOOutput, result2: TCOOutput):
    """
    Render cost per kilometer analysis.
    
    Args:
        result1: TCO result for the first vehicle
        result2: TCO result for the second vehicle
    """
    st.subheader("Cost Per Kilometer Analysis")
    
    # Use component keys from utils
    single_components = ["acquisition", "energy", "maintenance", "infrastructure", 
                       "battery_replacement", "insurance", "registration", 
                       "carbon_tax", "other_taxes", "residual_value"]
    
    try:
        # Calculate per-km costs
        v1_km_costs = {}
        v2_km_costs = {}
        
        for component in single_components:
            if result1.total_distance_km > 0:
                v1_km_costs[component] = get_component_value(result1, component) / result1.total_distance_km
            else:
                v1_km_costs[component] = 0
                
            if result2.total_distance_km > 0:
                v2_km_costs[component] = get_component_value(result2, component) / result2.total_distance_km
            else:
                v2_km_costs[component] = 0
        
        # Create DataFrame
        component_labels = {
            "acquisition": "Acquisition",
            "energy": "Energy",
            "maintenance": "Maintenance", 
            "infrastructure": "Infrastructure",
            "battery_replacement": "Battery Replacement",
            "insurance": "Insurance",
            "registration": "Registration",
            "carbon_tax": "Carbon Tax",
            "other_taxes": "Other Taxes",
            "residual_value": "Residual Value"
        }
        
        data = {
            "Component": [component_labels[c] for c in single_components],
            f"{result1.vehicle_name} ($/km)": [v1_km_costs[c] for c in single_components],
            f"{result2.vehicle_name} ($/km)": [v2_km_costs[c] for c in single_components],
            "Difference ($/km)": [v2_km_costs[c] - v1_km_costs[c] for c in single_components]
        }
        
        # Add total row
        data["Component"].append("Total")
        data[f"{result1.vehicle_name} ($/km)"].append(result1.lcod_per_km)
        data[f"{result2.vehicle_name} ($/km)"].append(result2.lcod_per_km)
        data["Difference ($/km)"].append(result2.lcod_per_km - result1.lcod_per_km)
        
        df = pd.DataFrame(data)
        
        # Format values as currency
        for col in df.columns:
            if col != "Component":
                df[col] = df[col].apply(lambda x: f"${x:.4f}")
        
        # Display table
        st.dataframe(df, use_container_width=True)
        
        # Highlight the LCOD difference
        if result2.lcod_per_km != 0:
            lcod_diff = result2.lcod_per_km - result1.lcod_per_km
            lcod_pct = (lcod_diff / result2.lcod_per_km) * 100
            
            st.metric(
                "LCOD Difference",
                f"${abs(lcod_diff):.4f}/km",
                f"{abs(lcod_pct):.1f}% {'lower' if lcod_diff < 0 else 'higher'} for {result1.vehicle_name}"
            )
    except Exception as e:
        st.error(f"Error calculating cost per kilometer: {str(e)}")
        st.info("Please check that your results contain valid data with non-zero distance values.") 