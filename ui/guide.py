"""
Guide Module

This module contains functions to render the interactive user guide and tutorial components
of the TCO Modeller application. It provides educational content, example scenarios,
and step-by-step guidance for users.
"""

import streamlit as st
from typing import Dict, Any, List, Tuple

from tco_model.models import ScenarioInput, VehicleType
from utils.helpers import load_default_scenario, update_state_from_model

# Example scenario configurations
EXAMPLE_SCENARIOS = {
    "urban_delivery": {
        "name": "Urban Delivery",
        "description": "Short-haul delivery operations in urban areas with frequent stops and lower daily distances.",
        "vehicle_1": "default_bet_urban",  # Urban electric truck
        "vehicle_2": "default_ice_urban",  # Urban diesel truck
        "key_parameters": {
            "annual_distance": "40,000 km",
            "daily_distance": "160 km",
            "vehicle_lifespan": "10 years",
            "charging_strategy": "Overnight depot charging"
        }
    },
    "regional_distribution": {
        "name": "Regional Distribution",
        "description": "Medium-haul distribution routes between regional centers with higher daily distances.",
        "vehicle_1": "default_bet_regional",  # Regional electric truck
        "vehicle_2": "default_ice_regional",  # Regional diesel truck
        "key_parameters": {
            "annual_distance": "80,000 km",
            "daily_distance": "320 km",
            "vehicle_lifespan": "10 years",
            "charging_strategy": "Depot charging plus opportunity charging"
        }
    },
    "long_haul": {
        "name": "Long-Haul Transport",
        "description": "Long-distance interstate transport operations with maximum daily distances.",
        "vehicle_1": "default_bet_longhaul",  # Long-haul electric truck
        "vehicle_2": "default_ice_longhaul",  # Long-haul diesel truck
        "key_parameters": {
            "annual_distance": "150,000 km",
            "daily_distance": "600 km",
            "vehicle_lifespan": "7 years",
            "charging_strategy": "Fast charging network"
        }
    },
    "financing_comparison": {
        "name": "Financing Options Comparison",
        "description": "Compare different financing methods for the same vehicle and operation type.",
        "vehicle_1": "default_bet_financed",  # BET with loan financing
        "vehicle_2": "default_bet_cash",  # BET with upfront cash purchase
        "key_parameters": {
            "financing_method_1": "7-year loan at 5% interest",
            "financing_method_2": "Upfront cash purchase",
            "annual_distance": "60,000 km",
            "vehicle_lifespan": "10 years"
        }
    }
}

# Tutorial steps
TUTORIAL_STEPS = [
    {
        "title": "Welcome to the TCO Modeller",
        "content": """
        This tool helps you compare the Total Cost of Ownership (TCO) between different heavy vehicle types,
        particularly Battery Electric Trucks (BETs) and conventional diesel trucks.
        
        The TCO analysis considers all costs over the vehicle's lifetime, including:
        - Purchase price and financing
        - Energy costs (diesel or electricity)
        - Maintenance and repairs
        - Infrastructure (charging equipment for BETs)
        - Registration and insurance
        - Carbon taxes and incentives
        - Residual value
        
        This tutorial will guide you through using the tool effectively.
        """
    },
    {
        "title": "Step 1: Choose Vehicle Types",
        "content": """
        Start by selecting the vehicle types you want to compare:
        
        1. Use the sidebar to select predefined vehicle configurations, or
        2. Customize each vehicle in the "Vehicle Configuration" tab
        
        You can compare:
        - A BET against a diesel truck (most common)
        - Two different BETs with varying specifications
        - Two diesel trucks with different features
        - The same vehicle type with different operational parameters
        
        💡 **Tip**: Start with predefined configurations and then adjust parameters to match your specific needs.
        """
    },
    {
        "title": "Step 2: Set Operational Parameters",
        "content": """
        Operational parameters significantly impact TCO results:
        
        - **Annual Distance**: Higher annual distances typically favor vehicles with lower operating costs (often BETs)
        - **Daily Distance**: Important for BETs as it affects range requirements and charging needs
        - **Analysis Period**: The number of years to include in the TCO analysis
        - **Operational Days**: Days per year the vehicle operates
        
        💡 **Tip**: Different operational profiles can lead to very different TCO outcomes. Try varying the annual distance to see the impact on comparative TCO.
        """
    },
    {
        "title": "Step 3: Configure Economic Parameters",
        "content": """
        Economic parameters determine future costs and their present value:
        
        - **Discount Rate**: Higher rates reduce the impact of future costs
        - **Inflation Rate**: Affects how costs increase over time
        - **Energy Prices**: Future diesel and electricity price projections
        - **Carbon Price**: Optional carbon tax or pricing mechanism
        
        💡 **Tip**: The discount rate is particularly important as it determines how future costs are valued today. Industry standard rates typically range from 4-8% real (inflation-adjusted).
        """
    },
    {
        "title": "Step 4: Set Financing Options",
        "content": """
        Choose how the vehicles are purchased:
        
        - **Cash Purchase**: Full payment upfront
        - **Loan Financing**: Specify loan term, interest rate, and deposit
        
        💡 **Tip**: BETs often have higher upfront costs but lower operating costs. Financing can help spread out these initial costs, potentially making BETs more attractive from a cash flow perspective.
        """
    },
    {
        "title": "Step 5: Calculate and Interpret Results",
        "content": """
        After configuring all parameters, click "Calculate TCO" to generate results.
        
        Key metrics to understand:
        
        - **Net Present Value (NPV) of TCO**: The total lifetime cost in today's dollars
        - **Levelized Cost of Driving (LCOD)**: Cost per kilometer, useful for direct comparison
        - **Breakeven Point**: The year when cumulative costs of one vehicle become lower than the other
        - **Cost Breakdown**: Shows the contribution of different cost components
        
        💡 **Tip**: Focus on the NPV of TCO for overall comparison, but look at the annual cost breakdown to understand the timing of costs and potential cash flow implications.
        """
    }
]

def render_guide() -> None:
    """
    Render the main guide page with tutorial and examples.
    
    This function should be called from the main app when the guide tab is active.
    """
    st.header("Interactive User Guide")
    
    # Create tabs for different sections of the guide
    guide_tabs = st.tabs(["Getting Started", "Example Scenarios", "Step-by-Step Tutorial", "Interpreting Results"])
    
    with guide_tabs[0]:
        render_getting_started()
        
    with guide_tabs[1]:
        render_example_scenarios()
        
    with guide_tabs[2]:
        render_tutorial()
        
    with guide_tabs[3]:
        render_results_guide()


def render_getting_started() -> None:
    """Render the getting started section of the guide."""
    st.subheader("Getting Started with the TCO Modeller")
    
    st.markdown("""
    ### What is Total Cost of Ownership (TCO)?
    
    Total Cost of Ownership is a financial estimate that helps determine the direct and indirect costs of owning an asset over its entire lifecycle. For heavy vehicles, this includes:
    
    - **Initial costs**: Purchase price, registration, financing costs
    - **Operating costs**: Fuel/energy, maintenance, insurance, taxes
    - **End-of-life costs/values**: Residual value, disposal costs
    
    ### Why TCO Matters for Heavy Vehicles
    
    When comparing different vehicle types—particularly conventional diesel trucks versus battery electric trucks—purchase price alone can be misleading:
    
    - Battery electric trucks typically have **higher upfront costs** but **lower operating costs**
    - Diesel trucks usually have **lower upfront costs** but **higher lifetime fuel and maintenance costs**
    
    A proper TCO analysis helps reveal the true economic comparison over the vehicle's lifetime.
    
    ### How to Use This Tool
    
    1. **Configure vehicles**: Set up the parameters for two vehicles you want to compare
    2. **Define operations**: Specify how the vehicles will be used (distance, days, etc.)
    3. **Set economic parameters**: Input discount rates, energy prices, etc.
    4. **Calculate TCO**: Generate comprehensive cost comparisons
    5. **Analyze results**: Examine breakdowns, charts, and payback periods
    
    ### Key Concepts to Understand
    
    - **Net Present Value (NPV)**: Converts future costs to today's dollars using a discount rate
    - **Levelized Cost of Driving (LCOD)**: TCO divided by lifetime distance ($/km)
    - **Breakeven Point**: Year when cumulative costs of one vehicle become lower than the other
    """)


def render_example_scenarios() -> None:
    """Render the example scenarios section with predefined use cases."""
    st.subheader("Example Scenarios")
    
    st.markdown("""
    Explore these predefined scenarios to understand how different operational profiles and vehicle types compare.
    Select a scenario to load it into the vehicle configuration tabs.
    """)
    
    # Create cards for each scenario
    for scenario_id, scenario in EXAMPLE_SCENARIOS.items():
        with st.expander(f"{scenario['name']} - {scenario['description']}"):
            # Display scenario details
            st.markdown(f"### {scenario['name']}")
            st.markdown(scenario['description'])
            
            # Display key parameters
            st.markdown("#### Key Parameters")
            for param, value in scenario['key_parameters'].items():
                st.markdown(f"- **{param.replace('_', ' ').title()}**: {value}")
            
            # Button to load this scenario
            if st.button(f"Load {scenario['name']} Scenario", key=f"load_{scenario_id}"):
                load_example_scenario(scenario_id)
                st.success(f"Loaded {scenario['name']} scenario! Switch to the Vehicle Configuration tab to see the details.")
                # Hint about next steps
                st.info("Now click 'Calculate TCO' in the Vehicle Configuration tab to see the results.")


def load_example_scenario(scenario_id: str) -> None:
    """
    Load an example scenario into the application state.
    
    Args:
        scenario_id: The ID of the scenario to load from EXAMPLE_SCENARIOS
    """
    scenario = EXAMPLE_SCENARIOS.get(scenario_id)
    if not scenario:
        st.error(f"Scenario {scenario_id} not found")
        return
    
    try:
        # Load vehicle 1 configuration
        vehicle_1_scenario = load_default_scenario(scenario["vehicle_1"])
        st.session_state["vehicle_1_input"] = vehicle_1_scenario
        
        # Load vehicle 2 configuration
        vehicle_2_scenario = load_default_scenario(scenario["vehicle_2"])
        st.session_state["vehicle_2_input"] = vehicle_2_scenario
        
        # Update nested state for UI components to reference
        update_state_from_model("vehicle_1_input", vehicle_1_scenario)
        update_state_from_model("vehicle_2_input", vehicle_2_scenario)
        
        # Reset results when scenario changes
        st.session_state["show_results"] = False
        st.session_state["results"] = None
        st.session_state["comparison"] = None
        
    except Exception as e:
        st.error(f"Error loading scenario: {str(e)}")


def render_tutorial() -> None:
    """Render the step-by-step tutorial."""
    st.subheader("Step-by-Step Tutorial")
    
    st.markdown("""
    This tutorial will guide you through the process of creating and comparing TCO scenarios.
    Follow these steps to understand how to use all features of the tool effectively.
    """)
    
    # Create steps with visual indicators
    for i, step in enumerate(TUTORIAL_STEPS):
        with st.expander(f"Step {i+1}: {step['title']}", expanded=(i==0)):
            st.markdown(step['content'])


def render_results_guide() -> None:
    """Render the guide for interpreting results."""
    st.subheader("Understanding and Interpreting Results")
    
    st.markdown("""
    ### Key Metrics to Focus On
    
    #### 1. Net Present Value (NPV) of TCO
    
    This is the sum of all costs over the vehicle's lifetime, discounted to present value using the discount rate.
    - **Lower NPV** means **lower total lifetime cost**
    - The discount rate significantly impacts this value—higher rates reduce the impact of future costs
    
    #### 2. Levelized Cost of Driving (LCOD)
    
    This is the TCO divided by the lifetime distance, expressed in dollars per kilometer ($/km).
    - Provides a normalized comparison between vehicles regardless of lifetime
    - Useful when comparing vehicles with different annual distances or lifespans
    
    #### 3. Breakeven Point
    
    The year when the cumulative costs of the initially more expensive vehicle become lower than the alternative.
    - Earlier breakeven points are favorable for the initially more expensive option
    - No breakeven point means the initially cheaper vehicle remains cheaper throughout the analysis period
    
    ### Reading the Charts
    
    #### Cumulative TCO Chart
    
    Shows how total costs accumulate over time for both vehicles.
    - The steeper the curve, the faster costs are accumulating
    - Look for when lines cross—this is the breakeven point
    
    #### Annual Cost Breakdown
    
    Shows the cost components for each year of operation.
    - Financing costs are typically front-loaded
    - Energy and maintenance costs continue throughout the lifetime
    - Residual value appears as a negative cost in the final year
    
    #### Component Comparison
    
    Displays the relative contribution of different cost categories to the total TCO.
    - Helps identify which cost components drive the overall difference between vehicles
    - Useful for sensitivity analysis—which parameters should you focus on optimizing?
    
    ### Making Decisions Based on Results
    
    When interpreting results, consider:
    
    1. **Investment horizon**: How long will you actually keep the vehicles?
    2. **Certainty of parameters**: Which inputs have the most uncertainty?
    3. **Cash flow implications**: Can you manage higher upfront costs for lower total TCO?
    4. **Non-financial factors**: Consider emissions, driver acceptance, noise, etc.
    5. **Sensitivity to key assumptions**: Try varying the most uncertain parameters
    
    💡 **Tip**: For fleet operators, it's often beneficial to test a small number of new technology vehicles before committing to fleet-wide adoption. This tool can help identify good candidates for pilot programs.
    """)


def add_tooltips_to_ui() -> Dict[str, str]:
    """
    Return a dictionary of tooltips to add to the UI components.
    
    This function doesn't directly modify the UI but provides the content for tooltips
    that can be used throughout the application.
    
    Returns:
        Dictionary mapping field keys to tooltip content
    """
    return {
        # Vehicle Parameters
        "vehicle.purchase_price": "The initial cost to purchase the vehicle, excluding taxes and incentives.",
        "vehicle.payload_capacity": "The maximum cargo weight the vehicle can legally carry.",
        "vehicle.engine_power": "The rated power output of the engine or motor in kilowatts.",
        
        # Battery Parameters (for BETs)
        "vehicle.battery.capacity": "The usable energy capacity of the battery in kilowatt-hours (kWh).",
        "vehicle.battery.cycle_life": "The number of full charge-discharge cycles the battery can undergo before reaching end of life (typically 80% of original capacity).",
        "vehicle.battery.cost_per_kwh": "The cost of battery replacement on a per kilowatt-hour basis.",
        
        # Operational Parameters
        "operational.annual_distance": "The total distance traveled by the vehicle per year in kilometers.",
        "operational.daily_distance": "The average distance traveled per operational day in kilometers.",
        "operational.operational_days": "The number of days per year the vehicle operates.",
        "operational.analysis_period": "The number of years to include in the TCO analysis.",
        
        # Economic Parameters
        "economic.discount_rate": "The rate used to discount future costs to present value, accounting for the time value of money.",
        "economic.inflation_rate": "The general rate at which prices are expected to increase over time.",
        "economic.electricity_price.base_rate": "The cost per kilowatt-hour for electricity, excluding demand charges.",
        "economic.diesel_price.current_price": "The current price per liter of diesel fuel.",
        
        # Financing Parameters
        "financing.method": "Choose between full upfront payment or loan financing.",
        "financing.loan_term": "The duration of the loan in years.",
        "financing.interest_rate": "The annual interest rate on the loan.",
        "financing.deposit_percentage": "The percentage of the vehicle price paid upfront as a deposit.",
        
        # Results Interpretation
        "results.npv": "Net Present Value of all costs over the analysis period, discounted to present value.",
        "results.lcod": "Levelized Cost of Driving - the total cost per kilometer over the vehicle's lifetime.",
        "results.breakeven_year": "The year when the cumulative costs of the initially more expensive vehicle become lower than the alternative.",
        
        # Charts
        "charts.cumulative_tco": "Shows how total costs accumulate over time for both vehicles.",
        "charts.annual_breakdown": "Displays cost components for each year of operation.",
        "charts.component_comparison": "Shows the relative contribution of different cost categories to the total TCO."
    } 