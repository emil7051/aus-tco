"""
Results Summary Module

This module renders the UI components for displaying TCO results in tabular format.
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any

from tco_model.models import TCOOutput, ComparisonResult
from utils.helpers import format_currency, format_percentage


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
    st.text(f"Comparing {result1.scenario.vehicle.name} vs {result2.scenario.vehicle.name}")
    
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
        result1.scenario.vehicle.name: [
            format_currency(result1.total_tco),
            f"{format_currency(result1.lcod)}/km",
            f"{result1.scenario.operational.analysis_period} years",
            f"{result1.scenario.operational.annual_distance:,} km",
            f"{result1.scenario.operational.annual_distance * result1.scenario.operational.analysis_period:,} km",
            "✓" if comparison.cheaper_option == 1 else "",
            "",
            "",
        ],
        result2.scenario.vehicle.name: [
            format_currency(result2.total_tco),
            f"{format_currency(result2.lcod)}/km",
            f"{result2.scenario.operational.analysis_period} years",
            f"{result2.scenario.operational.annual_distance:,} km",
            f"{result2.scenario.operational.annual_distance * result2.scenario.operational.analysis_period:,} km",
            "✓" if comparison.cheaper_option == 2 else "",
            format_currency(abs(comparison.tco_difference)),
            f"{abs(comparison.tco_percentage):.1f}% {'higher' if comparison.tco_difference > 0 else 'lower'}",
        ],
    }
    
    summary_df = pd.DataFrame(summary_data)
    st.table(summary_df)
    
    # Display cost breakdown
    st.subheader("Cost Breakdown (NPV)")
    
    # Create cost breakdown table
    cost_components = [
        "acquisition",
        "energy",
        "maintenance",
        "infrastructure",
        "battery_replacement",
        "insurance_registration",
        "taxes_levies",
        "residual_value",
        "total",
    ]
    
    cost_labels = [
        "Acquisition Costs",
        "Energy Costs",
        "Maintenance & Repair",
        "Infrastructure",
        "Battery Replacement",
        "Insurance & Registration",
        "Taxes & Levies",
        "Residual Value",
        "Total",
    ]
    
    breakdown_data = {
        "Component": cost_labels,
        result1.scenario.vehicle.name: [
            format_currency(getattr(result1.npv_costs, component))
            for component in cost_components
        ],
        result2.scenario.vehicle.name: [
            format_currency(getattr(result2.npv_costs, component))
            for component in cost_components
        ],
        "Difference": [
            format_currency(comparison.component_differences.get(component, 0))
            for component in cost_components
        ],
    }
    
    breakdown_df = pd.DataFrame(breakdown_data)
    st.table(breakdown_df)
    
    # Display annual costs summary
    st.subheader("Annual Costs Summary")
    
    # Create a DataFrame with annual totals for both vehicles
    years = range(result1.scenario.operational.analysis_period)
    annual_totals_data = {
        "Year": list(years),
        result1.scenario.vehicle.name: [
            result1.annual_costs.total[year] for year in years
        ],
        result2.scenario.vehicle.name: [
            result2.annual_costs.total[year] for year in years
        ],
        "Difference": [
            result2.annual_costs.total[year] - result1.annual_costs.total[year] 
            for year in years
        ],
    }
    
    annual_totals_df = pd.DataFrame(annual_totals_data)
    
    # Format currency values
    for col in [result1.scenario.vehicle.name, result2.scenario.vehicle.name, "Difference"]:
        annual_totals_df[col] = annual_totals_df[col].apply(format_currency)
    
    st.table(annual_totals_df) 