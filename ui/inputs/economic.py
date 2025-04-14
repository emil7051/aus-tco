"""
Economic Input Module

This module renders the UI components for economic parameter inputs,
including discount rates, inflation, energy prices, and carbon tax.
"""

import streamlit as st
from typing import Dict, Any, Optional

from tco_model.models import ElectricityRateType, DieselPriceScenario
from utils.helpers import (
    get_safe_state_value, 
    set_safe_state_value, 
    initialize_nested_state,
    format_currency,
    format_percentage
)
from utils.ui_components import UIComponentFactory
from ui.inputs.parameter_helpers import render_parameter_with_impact


# Constants for state keys
STATE_DISCOUNT_RATE = "discount_rate_real"
STATE_INFLATION_RATE = "inflation_rate"
STATE_ANALYSIS_PERIOD = "analysis_period_years"
STATE_ELECTRICITY_PRICE_TYPE = "electricity_price_type"
STATE_DIESEL_PRICE_SCENARIO = "diesel_price_scenario"
STATE_CARBON_TAX_RATE = "carbon_tax_rate_aud_per_tonne"
STATE_CARBON_TAX_INCREASE = "carbon_tax_annual_increase_rate"


def render_economic_inputs(vehicle_number: int) -> None:
    """
    Render the UI components for economic parameters.
    
    This function renders input fields for economic parameters such as
    discount rate, inflation, energy prices, and carbon tax.
    
    Args:
        vehicle_number: The vehicle number (1 or 2)
    """
    state_prefix = f"vehicle_{vehicle_number}_input"
    
    # Create tabs for different economic parameter categories
    tabs = st.tabs(["General", "Energy Prices", "Carbon Tax"])
    
    # General economic parameters tab
    with tabs[0]:
        render_general_economic_parameters(state_prefix)
    
    # Energy prices tab
    with tabs[1]:
        render_energy_prices(state_prefix, vehicle_number)
    
    # Carbon tax tab
    with tabs[2]:
        render_carbon_tax(state_prefix)


def render_economic_parameters(vehicle_number: int, state_prefix: str, vehicle_type: str) -> None:
    """
    Render enhanced economic parameter inputs
    
    Args:
        vehicle_number: Vehicle number
        state_prefix: State key prefix
        vehicle_type: Vehicle type
    """
    # Create a card for economic parameters
    with UIComponentFactory.create_card("Economic Parameters", 
                                      f"v{vehicle_number}_economic", 
                                      vehicle_type):
        # Create responsive grid
        col1, col2 = st.columns(2)
        
        with col1:
            # Discount rate input with impact indicator
            discount_rate = render_parameter_with_impact(
                "Discount Rate (%)",
                f"{state_prefix}.economic.{STATE_DISCOUNT_RATE}",
                default_value=get_safe_state_value(f"{state_prefix}.economic.{STATE_DISCOUNT_RATE}", 0.07),
                min_value=0.0,
                max_value=0.20,
                impact_level="high",
                step=0.01,
                format="%.2f",
                help_text="Real discount rate used for NPV calculations"
            )
            
            # Inflation rate
            inflation_rate = render_parameter_with_impact(
                "Inflation Rate (%)",
                f"{state_prefix}.economic.{STATE_INFLATION_RATE}",
                default_value=get_safe_state_value(f"{state_prefix}.economic.{STATE_INFLATION_RATE}", 0.025),
                min_value=0.0,
                max_value=0.10,
                impact_level="medium",
                step=0.005,
                format="%.3f",
                help_text="Annual inflation rate"
            )
        
        with col2:
            # Analysis period
            analysis_period = render_parameter_with_impact(
                "Analysis Period (years)",
                f"{state_prefix}.economic.{STATE_ANALYSIS_PERIOD}",
                default_value=get_safe_state_value(f"{state_prefix}.economic.{STATE_ANALYSIS_PERIOD}", 10),
                min_value=1,
                max_value=30,
                impact_level="high",
                step=1,
                help_text="Time horizon for TCO analysis"
            )
            
            # Carbon tax rate
            carbon_tax_rate = render_parameter_with_impact(
                "Carbon Tax Rate ($/tonne)",
                f"{state_prefix}.economic.{STATE_CARBON_TAX_RATE}",
                default_value=get_safe_state_value(f"{state_prefix}.economic.{STATE_CARBON_TAX_RATE}", 25.0),
                min_value=0.0,
                max_value=200.0,
                impact_level="low",
                step=5.0,
                help_text="Carbon tax rate in AUD per tonne of CO2"
            )
    
    # Create a card for energy prices
    with UIComponentFactory.create_card("Energy Prices", 
                                      f"v{vehicle_number}_energy", 
                                      vehicle_type):
        # Energy price parameters based on vehicle type
        if vehicle_type == "bet":
            # Electricity prices for BET
            electricity_price = render_parameter_with_impact(
                "Electricity Price ($/kWh)",
                f"{state_prefix}.economic.energy.electricity_price",
                default_value=get_safe_state_value(f"{state_prefix}.economic.energy.electricity_price", 0.25),
                min_value=0.05,
                max_value=0.80,
                step=0.01,
                format="%.3f",
                impact_level="high",
                help_text="Average price per kWh"
            )
            
            # Optional time-of-use pricing
            tou_pricing = st.checkbox(
                "Use Time-of-Use Pricing",
                value=get_safe_state_value(f"{state_prefix}.economic.energy.tou_enabled", False),
                key=f"{state_prefix}.economic.energy.tou_enabled_input",
                help="Enable time-of-use electricity pricing"
            )
            set_safe_state_value(f"{state_prefix}.economic.energy.tou_enabled", tou_pricing)
            
            if tou_pricing:
                col1, col2 = st.columns(2)
                
                with col1:
                    off_peak_price = render_parameter_with_impact(
                        "Off-Peak Price ($/kWh)",
                        f"{state_prefix}.economic.energy.off_peak_price",
                        default_value=get_safe_state_value(f"{state_prefix}.economic.energy.off_peak_price", 0.15),
                        min_value=0.05,
                        max_value=0.50,
                        step=0.01,
                        format="%.3f",
                        impact_level="medium",
                        help_text="Price per kWh during off-peak hours"
                    )
                
                with col2:
                    off_peak_percentage = render_parameter_with_impact(
                        "Off-Peak Charging (%)",
                        f"{state_prefix}.economic.energy.off_peak_percentage",
                        default_value=get_safe_state_value(f"{state_prefix}.economic.energy.off_peak_percentage", 0.8),
                        min_value=0.0,
                        max_value=1.0,
                        step=0.05,
                        format="%.2f",
                        impact_level="medium",
                        help_text="Proportion of charging done during off-peak hours"
                    )
                
                peak_price = render_parameter_with_impact(
                    "Peak Price ($/kWh)",
                    f"{state_prefix}.economic.energy.peak_price",
                    default_value=get_safe_state_value(f"{state_prefix}.economic.energy.peak_price", 0.35),
                    min_value=0.10,
                    max_value=1.00,
                    step=0.01,
                    format="%.3f",
                    impact_level="medium",
                    help_text="Price per kWh during peak hours"
                )
        else:
            # Diesel prices for diesel vehicles
            diesel_price = render_parameter_with_impact(
                "Diesel Price ($/L)",
                f"{state_prefix}.economic.energy.diesel_price",
                default_value=get_safe_state_value(f"{state_prefix}.economic.energy.diesel_price", 1.80),
                min_value=0.50,
                max_value=5.00,
                step=0.05,
                format="%.2f",
                impact_level="high",
                help_text="Current price per liter of diesel fuel"
            )
            
            diesel_price_annual_change = render_parameter_with_impact(
                "Annual Price Change (%)",
                f"{state_prefix}.economic.energy.diesel_price_annual_change",
                default_value=get_safe_state_value(f"{state_prefix}.economic.energy.diesel_price_annual_change", 0.025),
                min_value=-0.05,
                max_value=0.10,
                step=0.005,
                format="%.3f",
                impact_level="medium",
                help_text="Annual percentage change in diesel price"
            )


def render_general_economic_parameters(state_prefix: str) -> None:
    """
    Render general economic parameters like discount rate and inflation.
    
    Args:
        state_prefix: The state prefix for session state access
    """
    with st.expander("General Economic Parameters", expanded=True):
        # Discount rate and inflation
        col1, col2 = st.columns(2)
        
        with col1:
            discount_rate = st.number_input(
                "Discount Rate (%)",
                min_value=0.0,
                max_value=20.0,
                value=float(get_safe_state_value(f"{state_prefix}.economic.{STATE_DISCOUNT_RATE}", 0.07)) * 100,
                format="%.1f",
                key=f"{state_prefix}.economic.{STATE_DISCOUNT_RATE}_input",
                help="Real discount rate used for NPV calculations (excluding inflation)"
            )
            set_safe_state_value(f"{state_prefix}.economic.{STATE_DISCOUNT_RATE}", discount_rate / 100.0)
        
        with col2:
            inflation_rate = st.number_input(
                "Inflation Rate (%)",
                min_value=0.0,
                max_value=15.0,
                value=float(get_safe_state_value(f"{state_prefix}.economic.{STATE_INFLATION_RATE}", 0.025)) * 100,
                format="%.1f",
                key=f"{state_prefix}.economic.{STATE_INFLATION_RATE}_input",
                help="Annual inflation rate for cost adjustments"
            )
            set_safe_state_value(f"{state_prefix}.economic.{STATE_INFLATION_RATE}", inflation_rate / 100.0)
        
        # Analysis period
        analysis_period = st.slider(
            "Analysis Period (years)",
            min_value=1,
            max_value=25,
            value=int(get_safe_state_value(f"{state_prefix}.economic.{STATE_ANALYSIS_PERIOD}", 15)),
            key=f"{state_prefix}.economic.{STATE_ANALYSIS_PERIOD}_input",
            help="Period over which to calculate TCO (should match or be less than vehicle life)"
        )
        set_safe_state_value(f"{state_prefix}.economic.{STATE_ANALYSIS_PERIOD}", analysis_period)
        
        # Derived metrics
        st.subheader("Derived Metrics")
        col1, col2 = st.columns(2)
        
        # Calculate nominal discount rate
        nominal_rate = (1 + discount_rate/100) * (1 + inflation_rate/100) - 1
        
        with col1:
            st.metric("Nominal Discount Rate", format_percentage(nominal_rate))
        
        with col2:
            st.metric("Present Value Factor (Year 15)", f"{(1 / (1 + discount_rate/100) ** 15):.3f}")


def render_energy_prices(state_prefix: str, vehicle_number: int) -> None:
    """
    Render energy price parameters for electricity and diesel.
    
    Args:
        state_prefix: The state prefix for session state access
        vehicle_number: The vehicle number (1 or 2)
    """
    with st.expander("Energy Prices", expanded=True):
        # Different tabs for different energy types
        energy_tabs = st.tabs(["Electricity", "Diesel"])
        
        # Electricity tab
        with energy_tabs[0]:
            # Electricity rate type
            electricity_rate_type = st.selectbox(
                "Electricity Rate Type",
                options=[ert.value for ert in ElectricityRateType],
                index=0,
                key=f"{state_prefix}.economic.{STATE_ELECTRICITY_PRICE_TYPE}_input",
                help="Type of electricity tariff to apply"
            )
            set_safe_state_value(f"{state_prefix}.economic.{STATE_ELECTRICITY_PRICE_TYPE}", electricity_rate_type)
            
            # Electricity pricing based on rate type
            if electricity_rate_type == ElectricityRateType.AVERAGE_FLAT_RATE.value:
                electricity_price = st.number_input(
                    "Average Electricity Price (AUD/kWh)",
                    min_value=0.05,
                    max_value=0.80,
                    value=float(get_safe_state_value(f"{state_prefix}.economic.energy.electricity_price", 0.25)),
                    format="%.3f",
                    key=f"{state_prefix}.economic.energy.electricity_price_input",
                    help="Average price per kWh across all time periods"
                )
                set_safe_state_value(f"{state_prefix}.economic.energy.electricity_price", electricity_price)
                
                # Simple annual electricity cost calculation
                annual_distance = get_safe_state_value(f"{state_prefix}.operational.annual_distance_km", 100000)
                energy_consumption = get_safe_state_value(f"{state_prefix}.vehicle.energy_consumption.base_rate", 1.45)
                
                # Only show BET energy costs for vehicle 1 if it's a BET
                if vehicle_number == 1 and get_safe_state_value(f"{state_prefix}.vehicle.type") == "battery_electric":
                    annual_consumption = annual_distance * energy_consumption
                    st.metric("Estimated Annual Electricity Cost", 
                             format_currency(annual_consumption * electricity_price))
                
            elif electricity_rate_type == ElectricityRateType.OFF_PEAK_TOU.value:
                col1, col2 = st.columns(2)
                
                with col1:
                    off_peak_price = st.number_input(
                        "Off-Peak Price (AUD/kWh)",
                        min_value=0.05,
                        max_value=0.50,
                        value=float(get_safe_state_value(f"{state_prefix}.economic.energy.off_peak_price", 0.15)),
                        format="%.3f",
                        key=f"{state_prefix}.economic.energy.off_peak_price_input",
                        help="Price per kWh during off-peak hours"
                    )
                    set_safe_state_value(f"{state_prefix}.economic.energy.off_peak_price", off_peak_price)
                
                with col2:
                    off_peak_percentage = st.slider(
                        "Off-Peak Charging (%)",
                        min_value=0,
                        max_value=100,
                        value=int(get_safe_state_value(f"{state_prefix}.economic.energy.off_peak_percentage", 80)),
                        key=f"{state_prefix}.economic.energy.off_peak_percentage_input",
                        help="Percentage of charging done during off-peak hours"
                    )
                    set_safe_state_value(f"{state_prefix}.economic.energy.off_peak_percentage", off_peak_percentage)
                
                peak_price = st.number_input(
                    "Peak Price (AUD/kWh)",
                    min_value=0.10,
                    max_value=1.00,
                    value=float(get_safe_state_value(f"{state_prefix}.economic.energy.peak_price", 0.35)),
                    format="%.3f",
                    key=f"{state_prefix}.economic.energy.peak_price_input",
                    help="Price per kWh during peak hours"
                )
                set_safe_state_value(f"{state_prefix}.economic.energy.peak_price", peak_price)
                
                # Calculate average price
                average_price = (off_peak_price * off_peak_percentage/100) + (peak_price * (100-off_peak_percentage)/100)
                st.metric("Effective Average Price", f"${average_price:.3f}/kWh")
            
            # Demand charges
            demand_charges = st.checkbox(
                "Apply Demand Charges",
                value=bool(get_safe_state_value(f"{state_prefix}.economic.energy.demand_charges_enabled", False)),
                key=f"{state_prefix}.economic.energy.demand_charges_enabled_input",
                help="Whether to apply demand charges based on maximum power draw"
            )
            set_safe_state_value(f"{state_prefix}.economic.energy.demand_charges_enabled", demand_charges)
            
            if demand_charges:
                demand_charge_rate = st.number_input(
                    "Demand Charge Rate (AUD/kW/month)",
                    min_value=0.0,
                    max_value=50.0,
                    value=float(get_safe_state_value(f"{state_prefix}.economic.energy.demand_charge_rate", 15.0)),
                    format="%.2f",
                    key=f"{state_prefix}.economic.energy.demand_charge_rate_input",
                    help="Monthly charge per kW of maximum power demand"
                )
                set_safe_state_value(f"{state_prefix}.economic.energy.demand_charge_rate", demand_charge_rate)
        
        # Diesel tab
        with energy_tabs[1]:
            # Diesel price scenario
            diesel_price_scenario = st.selectbox(
                "Diesel Price Scenario",
                options=[dps.value for dps in DieselPriceScenario],
                index=1,  # Medium increase default
                key=f"{state_prefix}.economic.{STATE_DIESEL_PRICE_SCENARIO}_input",
                help="Scenario for future diesel price projections"
            )
            set_safe_state_value(f"{state_prefix}.economic.{STATE_DIESEL_PRICE_SCENARIO}", diesel_price_scenario)
            
            # Current diesel price
            diesel_price = st.number_input(
                "Current Diesel Price (AUD/L)",
                min_value=0.50,
                max_value=3.00,
                value=float(get_safe_state_value(f"{state_prefix}.economic.energy.diesel_price", 1.80)),
                format="%.2f",
                key=f"{state_prefix}.economic.energy.diesel_price_input",
                help="Current price per liter of diesel fuel"
            )
            set_safe_state_value(f"{state_prefix}.economic.energy.diesel_price", diesel_price)
            
            # Annual price change
            annual_change = {
                DieselPriceScenario.LOW_STABLE.value: 0.0,
                DieselPriceScenario.MEDIUM_INCREASE.value: 2.5,
                DieselPriceScenario.HIGH_INCREASE.value: 5.0
            }.get(diesel_price_scenario, 2.5)
            
            diesel_price_annual_change = st.slider(
                "Annual Price Change (%)",
                min_value=-5.0,
                max_value=10.0,
                value=float(get_safe_state_value(f"{state_prefix}.economic.energy.diesel_price_annual_change", annual_change)),
                format="%.1f",
                key=f"{state_prefix}.economic.energy.diesel_price_annual_change_input",
                help="Annual percentage change in diesel price (can be positive or negative)"
            )
            set_safe_state_value(f"{state_prefix}.economic.energy.diesel_price_annual_change", diesel_price_annual_change / 100.0)
            
            # Only show diesel costs for vehicle 2 if it's a diesel vehicle
            if vehicle_number == 2 and get_safe_state_value(f"{state_prefix}.vehicle.type") == "diesel":
                # Simple annual diesel cost calculation
                annual_distance = get_safe_state_value(f"{state_prefix}.operational.annual_distance_km", 100000)
                fuel_consumption = get_safe_state_value(f"{state_prefix}.vehicle.fuel_consumption.base_rate", 0.53)
                
                annual_consumption = annual_distance * fuel_consumption
                st.metric("Estimated Annual Diesel Cost", 
                         format_currency(annual_consumption * diesel_price))
            
            # Projected prices
            st.subheader("Projected Diesel Prices")
            years = [1, 5, 10, 15]
            prices = [diesel_price * (1 + diesel_price_annual_change/100) ** year for year in years]
            
            cols = st.columns(4)
            for i, (year, price) in enumerate(zip(years, prices)):
                with cols[i]:
                    st.metric(f"Year {year}", f"${price:.2f}/L")


def render_carbon_tax(state_prefix: str) -> None:
    """
    Render carbon tax parameters.
    
    Args:
        state_prefix: The state prefix for session state access
    """
    with st.expander("Carbon Tax", expanded=True):
        carbon_tax_enabled = st.checkbox(
            "Apply Carbon Tax",
            value=bool(get_safe_state_value(f"{state_prefix}.economic.carbon_tax.enabled", False)),
            key=f"{state_prefix}.economic.carbon_tax.enabled_input",
            help="Whether to apply a carbon tax in the analysis"
        )
        set_safe_state_value(f"{state_prefix}.economic.carbon_tax.enabled", carbon_tax_enabled)
        
        if carbon_tax_enabled:
            col1, col2 = st.columns(2)
            
            with col1:
                carbon_tax_rate = st.number_input(
                    "Carbon Tax Rate (AUD/tonne CO2)",
                    min_value=0.0,
                    max_value=200.0,
                    value=float(get_safe_state_value(f"{state_prefix}.economic.{STATE_CARBON_TAX_RATE}", 30.0)),
                    format="%.2f",
                    key=f"{state_prefix}.economic.{STATE_CARBON_TAX_RATE}_input",
                    help="Tax rate per tonne of CO2 emissions"
                )
                set_safe_state_value(f"{state_prefix}.economic.{STATE_CARBON_TAX_RATE}", carbon_tax_rate)
            
            with col2:
                annual_increase = st.slider(
                    "Annual Rate Increase (%)",
                    min_value=0.0,
                    max_value=10.0,
                    value=float(get_safe_state_value(f"{state_prefix}.economic.{STATE_CARBON_TAX_INCREASE}", 0.05)) * 100,
                    format="%.1f",
                    key=f"{state_prefix}.economic.{STATE_CARBON_TAX_INCREASE}_input",
                    help="Annual percentage increase in carbon tax rate"
                )
                set_safe_state_value(f"{state_prefix}.economic.{STATE_CARBON_TAX_INCREASE}", annual_increase / 100.0)
            
            # Projected carbon tax rates
            st.subheader("Projected Carbon Tax Rates")
            years = [1, 5, 10, 15]
            rates = [carbon_tax_rate * (1 + annual_increase/100) ** year for year in years]
            
            cols = st.columns(4)
            for i, (year, rate) in enumerate(zip(years, rates)):
                with cols[i]:
                    st.metric(f"Year {year}", f"${rate:.2f}/tonne")
            
            # Impact information
            st.info("""
            Carbon tax primarily affects vehicles with direct emissions (diesel).
            Battery electric vehicles may be indirectly affected through electricity generation emissions,
            depending on the grid's generation mix.
            """) 