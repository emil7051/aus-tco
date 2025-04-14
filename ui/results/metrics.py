"""
Results Metrics Module

This module provides UI components for displaying key metrics and insights
from TCO analysis results.
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from typing import Dict, Any, List, Optional

from tco_model.models import TCOOutput, ComparisonResult
from utils.helpers import format_currency, format_percentage
from ui.results.charts import create_cumulative_tco_chart


def render_key_metrics_panel(results: Dict[str, TCOOutput], comparison: ComparisonResult):
    """
    Render an interactive key metrics panel with insights
    
    Args:
        results: Dictionary of TCO result objects
        comparison: Comparison result object
    """
    # Get results for each vehicle
    result1 = results["vehicle_1"]
    result2 = results["vehicle_2"]
    
    # Format metrics
    total_tco_1 = format_currency(result1.total_tco)
    total_tco_2 = format_currency(result2.total_tco)
    lcod_1 = f"{format_currency(result1.lcod)}/km"
    lcod_2 = f"{format_currency(result2.lcod)}/km"
    
    # Determine which vehicle is cheaper
    cheaper_vehicle = result1.vehicle_name if comparison.cheaper_option == 1 else result2.vehicle_name
    saving_amount = format_currency(abs(comparison.tco_difference))
    saving_percent = f"{abs(comparison.tco_percentage):.1f}%"
    
    # Calculate payback information
    payback_info = get_payback_information(result1, result2, comparison)
    
    # Create metrics container
    st.markdown('<div class="metrics-panel">', unsafe_allow_html=True)
    
    # Create expandable metrics cards in columns
    col1, col2, col3 = st.columns(3)
    
    # TCO Comparison card
    with col1:
        with st.container():
            st.markdown('<div class="metric-card comparison">', unsafe_allow_html=True)
            
            # Use TCO from terminology
            from tco_model.terminology import TCO
            st.markdown(f"#### {TCO}")
            
            # Create comparison visualization
            fig = create_tco_comparison_visualization(result1, result2, comparison)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            
            # Key insight
            st.markdown(f"""
            <div class="metric-insight">
                <span class="highlight">{cheaper_vehicle}</span> is {saving_percent} cheaper
                <br>Saving <span class="highlight">{saving_amount}</span> over lifetime
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Cost per km card
    with col2:
        with st.container():
            st.markdown('<div class="metric-card lcod">', unsafe_allow_html=True)
            
            # Use LCOD from terminology
            from tco_model.terminology import LCOD
            st.markdown(f"#### {LCOD}")
            
            # Create LCOD comparison
            fig = create_lcod_comparison_visualization(result1, result2)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            
            # Key insight
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
    
    # Payback period card  
    with col3:
        with st.container():
            st.markdown('<div class="metric-card payback">', unsafe_allow_html=True)
            st.markdown("#### Investment Analysis")
            
            # Conditional display based on payback info
            if payback_info["has_payback"]:
                fig = create_payback_visualization(payback_info)
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                
                # Key insight
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


def create_tco_comparison_visualization(result1: TCOOutput, result2: TCOOutput, 
                                      comparison: ComparisonResult) -> go.Figure:
    """
    Create a visualization comparing total TCO between vehicles
    
    Args:
        result1: TCO result for the first vehicle
        result2: TCO result for the second vehicle
        comparison: The comparison result
        
    Returns:
        go.Figure: Plotly figure with comparison visualization
    """
    # Create a simple bar chart for comparison
    fig = go.Figure()
    
    # Add bars for each vehicle
    fig.add_trace(go.Bar(
        x=[result1.vehicle_name],
        y=[result1.total_tco],
        text=[format_currency(result1.total_tco)],
        textposition='auto',
        name=result1.vehicle_name,
        marker_color='#1f77b4'
    ))
    
    fig.add_trace(go.Bar(
        x=[result2.vehicle_name],
        y=[result2.total_tco],
        text=[format_currency(result2.total_tco)],
        textposition='auto',
        name=result2.vehicle_name,
        marker_color='#ff7f0e'
    ))
    
    # Add arrow annotation showing the difference
    if comparison.cheaper_option == 1:
        arrow_color = 'green'
        arrow_text = f"{saving_percent} lower"
    else:
        arrow_color = 'red'
        arrow_text = f"{saving_percent} higher"
    
    # Style the chart
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        height=180,
        showlegend=False,
        xaxis=dict(showticklabels=True),
        yaxis=dict(title='Total TCO (AUD)', showticklabels=False)
    )
    
    return fig


def create_lcod_comparison_visualization(result1: TCOOutput, result2: TCOOutput) -> go.Figure:
    """
    Create a visualization comparing cost per km between vehicles
    
    Args:
        result1: TCO result for the first vehicle
        result2: TCO result for the second vehicle
        
    Returns:
        go.Figure: Plotly figure with LCOD comparison
    """
    # Create a simple gauge chart for each vehicle
    fig = go.Figure()
    
    # Add gauges for each vehicle
    fig.add_trace(go.Indicator(
        mode="gauge+number+delta",
        value=result1.lcod,
        number={"prefix": "$", "valueformat": ".2f"},
        delta={"reference": result2.lcod, "valueformat": ".2f"},
        title={"text": result1.vehicle_name},
        gauge={
            "axis": {"range": [None, max(result1.lcod, result2.lcod) * 1.5]},
            "bar": {"color": "#1f77b4"},
            "steps": [
                {"range": [0, min(result1.lcod, result2.lcod)], "color": "lightgray"},
                {"range": [min(result1.lcod, result2.lcod), max(result1.lcod, result2.lcod)], "color": "gray"}
            ]
        },
        domain={"x": [0, 0.45], "y": [0, 1]}
    ))
    
    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=result2.lcod,
        number={"prefix": "$", "valueformat": ".2f"},
        title={"text": result2.vehicle_name},
        gauge={
            "axis": {"range": [None, max(result1.lcod, result2.lcod) * 1.5]},
            "bar": {"color": "#ff7f0e"},
            "steps": [
                {"range": [0, min(result1.lcod, result2.lcod)], "color": "lightgray"},
                {"range": [min(result1.lcod, result2.lcod), max(result1.lcod, result2.lcod)], "color": "gray"}
            ]
        },
        domain={"x": [0.55, 1], "y": [0, 1]}
    ))
    
    # Style the chart
    fig.update_layout(
        margin=dict(l=20, r=20, t=30, b=20),
        height=180
    )
    
    return fig


def create_payback_visualization(payback_info: Dict[str, Any]) -> go.Figure:
    """
    Create a visualization showing payback period
    
    Args:
        payback_info: Dictionary with payback details
        
    Returns:
        go.Figure: Plotly figure with payback visualization
    """
    # Create a simple timeline visualization
    fig = go.Figure()
    
    # Add bar for payback period
    fig.add_trace(go.Bar(
        y=["Payback"],
        x=[payback_info["years"]],
        orientation='h',
        marker_color='green',
        text=[f"{payback_info['years']:.1f} years"],
        textposition='auto'
    ))
    
    # Add reference line for analysis period
    fig.add_shape(
        type="line",
        x0=payback_info["analysis_period"],
        y0=-0.5,
        x1=payback_info["analysis_period"],
        y1=0.5,
        line=dict(color="red", width=2, dash="dash"),
    )
    
    # Add annotation for analysis period
    fig.add_annotation(
        x=payback_info["analysis_period"],
        y=0.8,
        text=f"Analysis period: {payback_info['analysis_period']} years",
        showarrow=False,
        font=dict(color="red")
    )
    
    # Style the chart
    fig.update_layout(
        margin=dict(l=0, r=0, t=20, b=20),
        height=150,
        showlegend=False,
        xaxis=dict(
            title="Years",
            range=[0, max(payback_info["analysis_period"] * 1.1, payback_info["years"] * 1.1)]
        ),
        yaxis=dict(showticklabels=False)
    )
    
    return fig


def get_payback_information(result1: TCOOutput, result2: TCOOutput, 
                          comparison: ComparisonResult) -> Dict[str, Any]:
    """
    Extract payback information from actual investment analysis.
    
    Args:
        result1: TCO result for vehicle 1
        result2: TCO result for vehicle 2
        comparison: Comparison result with investment analysis
        
    Returns:
        Dict[str, Any]: Dictionary with payback information
    """
    # Default return structure
    payback_info = {
        "has_payback": False,
        "years": 0,
        "roi": 0,
        "analysis_period": result1.analysis_period_years
    }
    
    # Use the actual investment analysis from comparison
    if hasattr(comparison, "investment_analysis") and comparison.investment_analysis:
        return {
            "has_payback": comparison.investment_analysis.has_payback,
            "years": comparison.investment_analysis.payback_years or 0,
            "roi": comparison.investment_analysis.roi or 0,
            "irr": comparison.investment_analysis.irr,
            "analysis_period": result1.analysis_period_years
        }
    
    return payback_info 