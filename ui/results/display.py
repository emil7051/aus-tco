"""
Results Display Module

This module provides functions to display TCO results from session state
and coordinates the rendering of different result components.
"""

import streamlit as st
from typing import Dict, Any, Optional

from tco_model.models import TCOOutput, ComparisonResult
from ui.results.summary import render_summary
from ui.results.detailed import render_detailed_breakdown
from ui.results.charts import render_charts
from ui.results.utils import validate_tco_results, get_chart_settings


def display_results(results: Dict[str, TCOOutput], comparison: Optional[ComparisonResult] = None):
    """
    Display TCO results using the various results modules.
    
    Args:
        results: Dictionary containing TCO results for each vehicle
        comparison: The comparison result between the two vehicles (optional)
    """
    # Check for valid results
    if not validate_tco_results(results):
        st.warning("No valid results available. Please run a calculation first.")
        return
    
    # Initialize comparison if not provided
    if not comparison and "vehicle_1" in results and "vehicle_2" in results:
        try:
            comparison = ComparisonResult.create(results["vehicle_1"], results["vehicle_2"])
        except Exception as e:
            st.error(f"Error creating comparison: {str(e)}")
            comparison = None
    
    # Display warning if comparison is missing
    if not comparison:
        st.warning("Comparison data is missing. Some features may not be available.")
    
    # Create main display tabs
    main_tabs = st.tabs(["Summary", "Detailed Breakdown", "Charts"])
    
    # Summary tab
    with main_tabs[0]:
        if comparison:
            render_summary(results, comparison)
        else:
            st.warning("Summary view requires comparison data. Please run a complete calculation.")
    
    # Detailed breakdown tab
    with main_tabs[1]:
        render_detailed_breakdown(results, comparison)
    
    # Charts tab
    with main_tabs[2]:
        if comparison:
            # Initialize chart settings if needed
            get_chart_settings()
            render_charts(results, comparison)
        else:
            st.warning("Chart view requires comparison data. Please run a complete calculation.")


def display_from_session_state():
    """
    Extract results from session state and display them.
    
    This function reads TCO results and comparison data from Streamlit's session state
    and passes them to the display_results function.
    """
    # Check if results exist in session state
    if "results" not in st.session_state or not st.session_state.results:
        st.warning("No calculation results available. Please run a calculation first.")
        return
    
    # Extract results from session state
    results = st.session_state.results
    comparison = st.session_state.get("comparison")
    
    # Display the results
    display_results(results, comparison)


def format_result_metrics(result: TCOOutput) -> Dict[str, str]:
    """
    Format key metrics from a TCO result for display.
    
    Args:
        result: TCO result for a vehicle
        
    Returns:
        Dict[str, str]: Dictionary of formatted metrics
    """
    from utils.helpers import format_currency
    
    if not result:
        return {}
    
    try:
        metrics = {
            "Total TCO (NPV)": format_currency(result.total_tco),
            "Cost per km": f"{format_currency(result.lcod)}/km",
            "Analysis Period": f"{result.analysis_period_years} years",
            "Total Distance": f"{result.total_distance_km:,.0f} km",
        }
        
        return metrics
    except (AttributeError, TypeError) as e:
        st.error(f"Error formatting metrics: {str(e)}")
        return {} 