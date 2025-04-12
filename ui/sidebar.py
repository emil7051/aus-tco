"""
Sidebar Module

This module renders the sidebar for the Streamlit application,
including app configuration options and information.
"""

import streamlit as st
from tco_model.models import VehicleType
from tco_model.vehicles import list_available_vehicle_configurations
from utils.helpers import load_default_scenario


def render_sidebar():
    """
    Render the sidebar for the Streamlit application.
    
    This includes:
    - Application information
    - Default vehicle configuration selection
    - Additional configuration options
    """
    st.sidebar.title("TCO Modeller")
    st.sidebar.markdown("---")
    
    # Default vehicle configurations
    st.sidebar.subheader("Default Configurations")
    
    # List available vehicle configurations
    available_configs = list_available_vehicle_configurations()
    
    # Vehicle 1 (BET) configuration
    bet_configs = available_configs.get(VehicleType.BATTERY_ELECTRIC, ["default_bet"])
    selected_bet_config = st.sidebar.selectbox(
        "Vehicle 1 (BET) Configuration",
        bet_configs,
        index=bet_configs.index("default_bet") if "default_bet" in bet_configs else 0,
        key="sidebar_bet_config",
    )
    
    if st.sidebar.button("Load BET Configuration", key="load_bet_config"):
        st.session_state.vehicle_1_input = load_default_scenario(selected_bet_config)
        st.sidebar.success(f"Loaded {selected_bet_config} configuration for Vehicle 1")
    
    # Vehicle 2 (ICE) configuration
    ice_configs = available_configs.get(VehicleType.DIESEL, ["default_ice"])
    selected_ice_config = st.sidebar.selectbox(
        "Vehicle 2 (ICE) Configuration",
        ice_configs,
        index=ice_configs.index("default_ice") if "default_ice" in ice_configs else 0,
        key="sidebar_ice_config",
    )
    
    if st.sidebar.button("Load ICE Configuration", key="load_ice_config"):
        st.session_state.vehicle_2_input = load_default_scenario(selected_ice_config)
        st.sidebar.success(f"Loaded {selected_ice_config} configuration for Vehicle 2")
    
    st.sidebar.markdown("---")
    
    # Application information
    st.sidebar.subheader("About")
    st.sidebar.markdown(
        """
        **Australian Heavy Vehicle TCO Modeller** is a tool for comparing 
        the Total Cost of Ownership (TCO) of different heavy vehicle types.
        
        Version: 0.1.0
        """
    )
    
    # Add additional sidebar content as needed
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        """
        Made with ❤️ in Australia
        
        Data source: Various industry reports and publications
        """
    ) 