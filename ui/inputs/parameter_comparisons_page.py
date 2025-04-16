"""
Parameter Comparisons Page

This module provides a dedicated page for comparing parameters between vehicles.
"""

import streamlit as st
from typing import Dict, Any, List, Optional

from ui.inputs.parameter_comparison import (
    render_parameter_comparison_tool,
    add_parameter_comparison_css
)
from utils.ui_components import UIComponentFactory


def render_parameter_comparisons_page() -> None:
    """
    Render a dedicated page for parameter comparisons
    """
    # Add custom CSS for parameter comparison
    add_parameter_comparison_css()
    
    # Create page header
    st.markdown("# Parameter Comparison Tool")
    st.markdown("""
    Compare key parameters between vehicles to understand their differences and impact on TCO.
    Parameter values with higher impact on TCO results are highlighted.
    """)
    
    # Create UIComponentFactory instance
    ui_factory = UIComponentFactory()
    
    # Create a card for parameter comparison
    with ui_factory.create_card("Parameter Comparison", "param_comparison", card_type="info"):
        render_parameter_comparison_tool()
    
    # Add explanation and guide
    with st.expander("Understanding Parameter Impact", expanded=False):
        st.markdown("""
        ### Parameter Impact Levels
        
        Parameters are marked with impact indicators:
        
        - 🔴 **High Impact**: These parameters have a significant effect on TCO results
        - 🟠 **Medium Impact**: These parameters have a moderate effect on TCO results
        - 🟢 **Low Impact**: These parameters have a minimal effect on TCO results
        
        ### Key High-Impact Parameters
        
        - **Annual Distance**: Directly affects fuel/energy costs and maintenance
        - **Purchase Price**: Major component of capital costs
        - **Analysis Period**: Determines time horizon for TCO calculation
        - **Discount Rate**: Affects present value calculations
        - **Energy/Fuel Prices**: Directly impacts operational costs
        
        ### Understanding Differences
        
        The comparison tool shows the absolute and percentage differences between parameters.
        Large differences in high-impact parameters require careful consideration.
        """) 