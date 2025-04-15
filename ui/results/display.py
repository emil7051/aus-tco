"""
Results Display Module

This module provides functions to display TCO results from session state
and coordinates the rendering of different result components.
"""

import streamlit as st
from typing import Dict, Any, Optional
import datetime

from tco_model.models import TCOOutput, ComparisonResult
from ui.results.metrics import render_key_metrics_panel
from ui.results.dashboard import render_standard_dashboard
from ui.results.utils import validate_tco_results, get_chart_settings, generate_results_export


def display_results(results: Dict[str, TCOOutput], comparison: Optional[ComparisonResult] = None):
    """
    Create a modular, customisable results dashboard
    
    Args:
        results: Dictionary of TCO result objects
        comparison: Comparison result object
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
        return
    
    # Create dashboard container with custom styling
    st.markdown('<div class="results-dashboard">', unsafe_allow_html=True)
    
    # Add dashboard toolbar with options
    with st.container():
        st.markdown('<div class="dashboard-toolbar">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            st.markdown("### TCO Analysis Results")
            st.markdown(f"Comparing **{results['vehicle_1'].vehicle_name}** vs **{results['vehicle_2'].vehicle_name}**")
        
        with col2:
            layout = st.selectbox(
                "Dashboard Layout", 
                options=["Standard", "Detailed", "Executive Summary"],
                key="dashboard_layout"
            )
        
        with col3:
            st.download_button(
                "Export Results", 
                data=generate_results_export(results, comparison),
                file_name="tco_analysis.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Display key metrics with visual emphasis
    render_key_metrics_panel(results, comparison)
    
    # Render dashboard based on selected layout
    if layout == "Standard":
        render_standard_dashboard(results, comparison)
    elif layout == "Detailed":
        render_detailed_dashboard(results, comparison)
    else:
        render_executive_dashboard(results, comparison)
    
    st.markdown('</div>', unsafe_allow_html=True)


def display_from_session_state(session_id: str = None):
    """
    Display results from session state
    
    Args:
        session_id: Optional session identifier to use for retrieving results
    """
    # Determine which keys to use based on session_id
    if session_id:
        results_key = f"results_{session_id}"
        comparison_key = f"comparison_{session_id}"
    else:
        results_key = "results"
        comparison_key = "comparison"
    
    # Try to get results and comparison data
    results = st.session_state.get(results_key)
    comparison = st.session_state.get(comparison_key)
    
    # Fall back to original keys if specific ones aren't found
    if results is None:
        results = st.session_state.get("results")
    if comparison is None:
        comparison = st.session_state.get("comparison")
    
    # Display results if available
    if results and comparison:
        # Create tabs for different views
        tab1, tab2 = st.tabs(["Executive Dashboard", "Detailed Dashboard"])
        
        with tab1:
            render_executive_dashboard(results, comparison)
        
        with tab2:
            render_detailed_dashboard(results, comparison)
    else:
        st.info("No results to display. Please run the analysis first.")


def render_detailed_dashboard(results: Dict[str, TCOOutput], comparison: ComparisonResult):
    """
    Render a detailed dashboard with comprehensive analysis
    
    Args:
        results: Dictionary of TCO result objects
        comparison: Comparison result object
    """
    # Import here to avoid circular imports
    from ui.results.detailed import render_detailed_breakdown
    from ui.results.charts import render_charts
    
    # Create main analysis tabs
    tabs = st.tabs([
        "Detailed Breakdown",
        "Vehicle Analysis",
        "Interactive Charts",
        "Sensitivity Analysis",
        "Export Options"
    ])
    
    # Detailed breakdown tab
    with tabs[0]:
        render_detailed_breakdown(results, comparison)
    
    # Vehicle analysis tab
    with tabs[1]:
        # This would be implemented with vehicle-specific analysis
        st.subheader("Vehicle Comparison")
        st.info("Detailed vehicle analysis will be implemented in a future version.")
    
    # Interactive charts tab
    with tabs[2]:
        # Load current chart settings
        get_chart_settings()
        render_charts(results, comparison)
    
    # Sensitivity analysis tab
    with tabs[3]:
        st.subheader("Sensitivity Analysis")
        st.info("Comprehensive sensitivity analysis will be implemented in a future version.")
    
    # Export options tab
    with tabs[4]:
        st.subheader("Export Options")
        
        # Provide different export formats
        export_format = st.radio(
            "Export Format",
            options=["Excel", "PDF Report", "CSV", "JSON"],
            horizontal=True
        )
        
        if export_format == "Excel":
            st.download_button(
                "Download Excel Report",
                data=generate_results_export(results, comparison),
                file_name="tco_analysis_detailed.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        elif export_format == "PDF Report":
            st.info("PDF export will be implemented in a future version.")
        elif export_format == "CSV":
            st.info("CSV export will be implemented in a future version.")
        else:
            st.info("JSON export will be implemented in a future version.")


def render_executive_dashboard(results: Dict[str, TCOOutput], comparison: ComparisonResult):
    """
    Render an executive summary dashboard with key insights
    
    Args:
        results: Dictionary of TCO result objects
        comparison: Comparison result object
    """
    # Extract results for each vehicle
    result1 = results["vehicle_1"]
    result2 = results["vehicle_2"]
    
    # Create executive summary 
    st.markdown(f"""
    <div class="executive-summary">
        <h3>Executive Summary</h3>
        <p>
            This analysis compares the Total Cost of Ownership (TCO) between
            <strong>{result1.vehicle_name}</strong> and <strong>{result2.vehicle_name}</strong>
            over an analysis period of <strong>{result1.analysis_period_years} years</strong>.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Key findings
    st.markdown("### Key Findings")
    
    # Create a 2-column layout for key metrics
    col1, col2 = st.columns(2)
    
    with col1:
        # Create financial findings
        cheaper_vehicle = result1.vehicle_name if comparison.cheaper_option == 1 else result2.vehicle_name
        saving_amount = abs(comparison.tco_difference)
        saving_percent = abs(comparison.tco_percentage)
        
        from utils.helpers import format_currency
        
        st.markdown(f"""
        <div class="finding-card financial">
            <h4>Financial Summary</h4>
            <ul>
                <li>The <strong>{cheaper_vehicle}</strong> offers a lower TCO</li>
                <li>Total savings of <strong>{format_currency(saving_amount)}</strong> ({saving_percent:.1f}%)</li>
                <li>Equivalent to <strong>{format_currency(saving_amount / result1.analysis_period_years)}</strong> per year</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # Add payback information if relevant
        if hasattr(comparison, "payback_years") and comparison.payback_years:
            st.markdown(f"""
            <div class="finding-card payback">
                <h4>Investment Analysis</h4>
                <ul>
                    <li>Initial investment pays back in <strong>{comparison.payback_years:.1f} years</strong></li>
                    <li>Positive return on investment over the analysis period</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        # Create operational findings
        st.markdown(f"""
        <div class="finding-card operational">
            <h4>Operational Insights</h4>
            <ul>
                <li>Cost per kilometer is <strong>{format_currency(result1.lcod)}</strong> for {result1.vehicle_name}</li>
                <li>Cost per kilometer is <strong>{format_currency(result2.lcod)}</strong> for {result2.vehicle_name}</li>
                <li><strong>{abs(comparison.lcod_difference_percentage):.1f}%</strong> difference in cost per kilometer</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # Create environmental findings
        is_electric1 = "Electric" in result1.vehicle_name or "BET" in result1.vehicle_name
        is_electric2 = "Electric" in result2.vehicle_name or "BET" in result2.vehicle_name
        
        if is_electric1 != is_electric2:
            cleaner_vehicle = result1.vehicle_name if is_electric1 else result2.vehicle_name
            
            st.markdown(f"""
            <div class="finding-card environmental">
                <h4>Environmental Impact</h4>
                <ul>
                    <li>The <strong>{cleaner_vehicle}</strong> has significantly lower emissions</li>
                    <li>Reduced carbon footprint over vehicle lifetime</li>
                    <li>Lower impact on local air quality</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
    
    # Recommendations
    st.markdown("### Recommendations")
    
    # Generate basic recommendations
    recommendations = []
    
    if comparison.cheaper_option == 1:
        recommendations.append(f"Consider {result1.vehicle_name} for lower total cost of ownership")
    else:
        recommendations.append(f"Consider {result2.vehicle_name} for lower total cost of ownership")
    
    # Add financial recommendations
    if hasattr(comparison, "payback_years") and comparison.payback_years:
        if comparison.payback_years < result1.analysis_period_years / 2:
            recommendations.append("The higher upfront investment is quickly recovered and provides good financial returns")
        else:
            recommendations.append("Consider the longer payback period when making financial decisions")
    
    # Add environmental recommendations
    if is_electric1 != is_electric2:
        cleaner_vehicle = result1.vehicle_name if is_electric1 else result2.vehicle_name
        recommendations.append(f"Consider {cleaner_vehicle} for reduced environmental impact and lower emissions")
    
    # Display recommendations
    for i, recommendation in enumerate(recommendations):
        st.markdown(f"**{i+1}. {recommendation}**")
    
    # Key charts for executive summary
    st.markdown("### Key Charts")
    
    # Import required chart functions
    from ui.results.charts import create_cumulative_tco_chart, create_cost_components_chart
    
    # Create two-column layout for charts
    chart_cols = st.columns(2)
    
    with chart_cols[0]:
        # Cumulative TCO chart
        cumulative_chart = create_cumulative_tco_chart(
            result1, 
            result2,
            show_breakeven=True,
            height=350
        )
        st.plotly_chart(cumulative_chart, use_container_width=True, 
                      config={'displayModeBar': False})
    
    with chart_cols[1]:
        # Component breakdown chart
        components_chart = create_cost_components_chart(
            result1, 
            result2,
            comparison,
            stacked=True,
            height=350
        )
        st.plotly_chart(components_chart, use_container_width=True,
                      config={'displayModeBar': False})


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