"""
Results Summary Module

This module renders the UI components for displaying TCO results in tabular format.
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any

from tco_model.models import TCOOutput, ComparisonResult
from utils.helpers import format_currency, format_percentage
from ui.results.utils import COMPONENT_KEYS, COMPONENT_LABELS


def render_summary(results: Dict[str, TCOOutput], comparison: ComparisonResult):
    """
    Render the summary tables for TCO results.
    
    Args:
        results: Dictionary containing TCO results for each vehicle
        comparison: The comparison result between the two vehicles
    """
    # Extract results
    result1 = results["vehicle_1"]
    result2 = results["vehicle_2"]
    
    # Display vehicle names
    st.subheader("TCO Summary")
    st.text(f"Comparing {result1.vehicle_name} vs {result2.vehicle_name}")
    
    # Create summary table
    summary_data = {
        "Metric": [
            "Total TCO (NPV)",
            "TCO per km (LCOD)",
            "Analysis Period",
            "Annual Distance",
            "Total Distance",
            "Cheaper Option",
            "Cost Difference",
            "Percentage Difference",
        ],
        result1.vehicle_name: [
            format_currency(result1.npv_total),
            f"{format_currency(result1.lcod_per_km)}/km",
            f"{result1.analysis_period_years} years",
            f"{result1.total_distance_km / result1.analysis_period_years:,.0f} km",
            f"{result1.total_distance_km:,.0f} km",
            "✓" if comparison.cheaper_option == 1 else "",
            "",
            "",
        ],
        result2.vehicle_name: [
            format_currency(result2.npv_total),
            f"{format_currency(result2.lcod_per_km)}/km",
            f"{result2.analysis_period_years} years",
            f"{result2.total_distance_km / result2.analysis_period_years:,.0f} km",
            f"{result2.total_distance_km:,.0f} km",
            "✓" if comparison.cheaper_option == 2 else "",
            format_currency(abs(comparison.npv_difference)),
            f"{abs(comparison.npv_difference_percentage):.1f}% {'higher' if comparison.npv_difference > 0 else 'lower'}",
        ],
    }
    
    summary_df = pd.DataFrame(summary_data)
    st.table(summary_df)
    
    # Display cost breakdown
    st.subheader("Cost Breakdown (NPV)")
    
    # Create cost breakdown table
    cost_components = COMPONENT_KEYS
    cost_labels = [COMPONENT_LABELS[component] for component in cost_components]
    cost_labels.append("Total")  # Add total row
    cost_components = list(cost_components) + ["total"]  # Add total to components
    
    breakdown_data = {
        "Component": cost_labels,
        result1.vehicle_name: [
            format_currency(getattr(result1.npv_costs, component) if component != "total" else result1.npv_total)
            for component in cost_components
        ],
        result2.vehicle_name: [
            format_currency(getattr(result2.npv_costs, component) if component != "total" else result2.npv_total)
            for component in cost_components
        ],
        "Difference": [
            format_currency(comparison.component_differences.get(component, 0) if component != "total" else comparison.npv_difference)
            for component in cost_components
        ],
    }
    
    breakdown_df = pd.DataFrame(breakdown_data)
    st.table(breakdown_df)
    
    # Display annual costs summary
    st.subheader("Annual Costs Summary")
    
    # Create a DataFrame with annual totals for both vehicles
    years = range(result1.analysis_period_years)
    annual_totals_data = {
        "Year": list(years),
        result1.vehicle_name: [
            result1.annual_costs[year].total for year in years
        ],
        result2.vehicle_name: [
            result2.annual_costs[year].total for year in years
        ],
        "Difference": [
            result2.annual_costs[year].total - result1.annual_costs[year].total 
            for year in years
        ],
    }
    
    annual_totals_df = pd.DataFrame(annual_totals_data)
    
    # Format currency values
    for col in [result1.vehicle_name, result2.vehicle_name, "Difference"]:
        annual_totals_df[col] = annual_totals_df[col].apply(format_currency)
    
    st.table(annual_totals_df) 