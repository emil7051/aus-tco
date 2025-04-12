"""
Economic Input Module

This module renders the UI components for economic parameter inputs.
"""

import streamlit as st
from typing import Dict, Any, Optional

from tco_model.models import FinancingMethod, ElectricityRateType, DieselPriceScenario
from utils.helpers import get_safe_state_value, set_safe_state_value


def render_economic_inputs(vehicle_number: int):
    """
    Render the UI components for economic parameters.
    
    Args:
        vehicle_number: The vehicle number (1 or 2)
    """
    state_prefix = f"vehicle_{vehicle_number}_input.economic"
    
    # Create a form for the economic parameters
    with st.form(key=f"economic_{vehicle_number}_form"):
        st.subheader("Economic Parameters")
        
        # Discount rate and inflation
        col1, col2 = st.columns(2)
        
        with col1:
            discount_rate = st.number_input(
                "Discount Rate (%)",
                min_value=0.0,
                max_value=100.0,
                value=get_safe_state_value(f"{state_prefix}.discount_rate", 7.0),
                format="%.1f",
                key=f"{state_prefix}.discount_rate",
            )
        
        with col2:
            inflation_rate = st.number_input(
                "Inflation Rate (%)",
                min_value=0.0,
                max_value=100.0,
                value=get_safe_state_value(f"{state_prefix}.inflation_rate", 2.5),
                format="%.1f",
                key=f"{state_prefix}.inflation_rate",
            )
        
        # Financing options
        st.subheader("Financing Options")
        
        # Financing method
        financing_method = st.selectbox(
            "Financing Method",
            options=[fm.value for fm in FinancingMethod],
            index=0,
            key=f"{state_prefix}.financing.method",
        )
        
        # Conditional financing parameters
        if financing_method == FinancingMethod.LOAN.value:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                loan_term = st.slider(
                    "Loan Term (years)",
                    min_value=1,
                    max_value=10,
                    value=get_safe_state_value(f"{state_prefix}.financing.loan_term", 5),
                    key=f"{state_prefix}.financing.loan_term",
                )
            
            with col2:
                interest_rate = st.number_input(
                    "Interest Rate (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=get_safe_state_value(f"{state_prefix}.financing.interest_rate", 5.0),
                    format="%.1f",
                    key=f"{state_prefix}.financing.interest_rate",
                )
            
            with col3:
                deposit_percentage = st.number_input(
                    "Deposit (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=get_safe_state_value(f"{state_prefix}.financing.deposit_percentage", 20.0),
                    format="%.1f",
                    key=f"{state_prefix}.financing.deposit_percentage",
                )
        
        # Energy prices
        st.subheader("Energy Prices")
        
        # Different tabs for different energy types
        energy_tabs = st.tabs(["Electricity", "Diesel", "Carbon Tax"])
        
        # Electricity tab
        with energy_tabs[0]:
            electricity_rate_type = st.selectbox(
                "Electricity Rate Type",
                options=[ert.value for ert in ElectricityRateType],
                index=0,
                key=f"{state_prefix}.energy.electricity_rate_type",
            )
            
            electricity_price = st.number_input(
                "Electricity Price (AUD/kWh)",
                min_value=0.0,
                value=get_safe_state_value(f"{state_prefix}.energy.electricity_price", 0.25),
                format="%.3f",
                key=f"{state_prefix}.energy.electricity_price",
            )
            
            if electricity_rate_type == ElectricityRateType.TIME_OF_USE.value:
                # Additional parameters for time-of-use pricing
                col1, col2 = st.columns(2)
                
                with col1:
                    off_peak_price = st.number_input(
                        "Off-Peak Price (AUD/kWh)",
                        min_value=0.0,
                        value=get_safe_state_value(f"{state_prefix}.energy.off_peak_price", 0.15),
                        format="%.3f",
                        key=f"{state_prefix}.energy.off_peak_price",
                    )
                
                with col2:
                    peak_price = st.number_input(
                        "Peak Price (AUD/kWh)",
                        min_value=0.0,
                        value=get_safe_state_value(f"{state_prefix}.energy.peak_price", 0.35),
                        format="%.3f",
                        key=f"{state_prefix}.energy.peak_price",
                    )
                
                # Demand charges
                demand_charge = st.number_input(
                    "Demand Charge (AUD/kVA/month)",
                    min_value=0.0,
                    value=get_safe_state_value(f"{state_prefix}.energy.demand_charge", 15.0),
                    format="%.2f",
                    key=f"{state_prefix}.energy.demand_charge",
                )
        
        # Diesel tab
        with energy_tabs[1]:
            diesel_price_scenario = st.selectbox(
                "Diesel Price Scenario",
                options=[dps.value for dps in DieselPriceScenario],
                index=0,
                key=f"{state_prefix}.energy.diesel_price_scenario",
            )
            
            diesel_price = st.number_input(
                "Diesel Price (AUD/L)",
                min_value=0.0,
                value=get_safe_state_value(f"{state_prefix}.energy.diesel_price", 1.50),
                format="%.2f",
                key=f"{state_prefix}.energy.diesel_price",
            )
            
            diesel_price_annual_change = st.slider(
                "Annual Price Change (%)",
                min_value=-10.0,
                max_value=10.0,
                value=get_safe_state_value(f"{state_prefix}.energy.diesel_price_annual_change", 2.0),
                format="%.1f",
                key=f"{state_prefix}.energy.diesel_price_annual_change",
            )
        
        # Carbon tax tab
        with energy_tabs[2]:
            carbon_tax = st.checkbox(
                "Apply Carbon Tax",
                value=get_safe_state_value(f"{state_prefix}.carbon_tax.enabled", False),
                key=f"{state_prefix}.carbon_tax.enabled",
            )
            
            if carbon_tax:
                carbon_tax_rate = st.number_input(
                    "Carbon Tax Rate (AUD/tonne CO2)",
                    min_value=0.0,
                    value=get_safe_state_value(f"{state_prefix}.carbon_tax.rate", 25.0),
                    format="%.2f",
                    key=f"{state_prefix}.carbon_tax.rate",
                )
                
                carbon_tax_annual_change = st.slider(
                    "Annual Rate Change (%)",
                    min_value=-10.0,
                    max_value=10.0,
                    value=get_safe_state_value(f"{state_prefix}.carbon_tax.annual_change", 5.0),
                    format="%.1f",
                    key=f"{state_prefix}.carbon_tax.annual_change",
                )
        
        # Submit button
        submitted = st.form_submit_button("Update Economic Parameters")
        
        if submitted:
            # Update session state with the form values
            set_safe_state_value(f"{state_prefix}.discount_rate", discount_rate / 100.0)  # Convert to decimal
            set_safe_state_value(f"{state_prefix}.inflation_rate", inflation_rate / 100.0)  # Convert to decimal
            
            # Financing
            set_safe_state_value(f"{state_prefix}.financing.method", financing_method)
            if financing_method == FinancingMethod.LOAN.value:
                set_safe_state_value(f"{state_prefix}.financing.loan_term", loan_term)
                set_safe_state_value(f"{state_prefix}.financing.interest_rate", interest_rate / 100.0)  # Convert to decimal
                set_safe_state_value(f"{state_prefix}.financing.deposit_percentage", deposit_percentage / 100.0)  # Convert to decimal
            
            # Energy prices
            # Electricity
            set_safe_state_value(f"{state_prefix}.energy.electricity_rate_type", electricity_rate_type)
            set_safe_state_value(f"{state_prefix}.energy.electricity_price", electricity_price)
            if electricity_rate_type == ElectricityRateType.TIME_OF_USE.value:
                set_safe_state_value(f"{state_prefix}.energy.off_peak_price", off_peak_price)
                set_safe_state_value(f"{state_prefix}.energy.peak_price", peak_price)
                set_safe_state_value(f"{state_prefix}.energy.demand_charge", demand_charge)
            
            # Diesel
            set_safe_state_value(f"{state_prefix}.energy.diesel_price_scenario", diesel_price_scenario)
            set_safe_state_value(f"{state_prefix}.energy.diesel_price", diesel_price)
            set_safe_state_value(f"{state_prefix}.energy.diesel_price_annual_change", diesel_price_annual_change / 100.0)  # Convert to decimal
            
            # Carbon tax
            set_safe_state_value(f"{state_prefix}.carbon_tax.enabled", carbon_tax)
            if carbon_tax:
                set_safe_state_value(f"{state_prefix}.carbon_tax.rate", carbon_tax_rate)
                set_safe_state_value(f"{state_prefix}.carbon_tax.annual_change", carbon_tax_annual_change / 100.0)  # Convert to decimal
            
            st.success("Economic parameters updated!") 