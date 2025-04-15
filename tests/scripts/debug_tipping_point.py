#!/usr/bin/env python
"""
Debug script for tipping point calculation.
This helps debug the issue with the tipping point detection in the tests.
"""

import sys
import os
import pandas as pd
from datetime import date

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from tco_model.calculator import TCOCalculator
from tco_model.models import (
    ScenarioInput, BETParameters, DieselParameters, 
    EconomicParameters, OperationalParameters, ChargingParameters,
    BatteryParameters, EngineParameters, BETConsumptionParameters,
    DieselConsumptionParameters, MaintenanceParameters, ResidualValueParameters,
    FinancingParameters, InfrastructureParameters, VehicleCategory,
    ElectricityRateType, DieselPriceScenario, ChargingStrategy,
    VehicleType, FinancingMethod
)

def create_test_bet_scenario():
    """Create a simple BET scenario for testing."""
    return ScenarioInput(
        scenario_name="BET Test Scenario",
        vehicle=BETParameters(
            name="Example BET",
            type=VehicleType.BATTERY_ELECTRIC,
            category=VehicleCategory.ARTICULATED,
            purchase_price=500000.0,
            max_payload_tonnes=30.0,
            range_km=300.0,
            battery=BatteryParameters(
                capacity_kwh=400.0,
                degradation_rate_annual=0.02,
                replacement_threshold=0.8,
                replacement_cost_factor=0.8,
                usable_capacity_percentage=0.9,
            ),
            energy_consumption=BETConsumptionParameters(
                base_rate=1.5,
                min_rate=1.0,
                max_rate=2.0,
                load_adjustment_factor=0.2,
                hot_weather_adjustment=0.05,
                cold_weather_adjustment=0.05,
                regenerative_braking_efficiency=0.65,
                regen_contribution_urban=0.2,
            ),
            charging=ChargingParameters(
                max_charging_power_kw=150.0,
                charging_efficiency=0.9,
                strategy=ChargingStrategy.OVERNIGHT_DEPOT,
                electricity_rate_type=ElectricityRateType.AVERAGE_FLAT_RATE
            ),
            maintenance=MaintenanceParameters(
                cost_per_km=0.15,
                annual_fixed_min=700,
                annual_fixed_max=1500,
                annual_fixed_default=1000,
                scheduled_maintenance_interval_km=40000,
                major_service_interval_km=120000
            ),
            residual_value=ResidualValueParameters(
                year_5_range=(0.45, 0.55),
                year_10_range=(0.25, 0.35),
                year_15_range=(0.10, 0.20),
            ),
        ),
        operational=OperationalParameters(
            annual_distance_km=100000,
            operating_days_per_year=260,
            vehicle_life_years=15,
            average_load_factor=0.8,
            is_urban_operation=False,
        ),
        economic=EconomicParameters(
            discount_rate_real=0.07,
            inflation_rate=0.025,
            analysis_period_years=15,
            electricity_price_type=ElectricityRateType.AVERAGE_FLAT_RATE,
            electricity_price_aud_per_kwh=0.25,
            diesel_price_scenario=DieselPriceScenario.MEDIUM_INCREASE,
            diesel_price_aud_per_l=1.85,
            carbon_tax_rate_aud_per_tonne=30.0,
            carbon_tax_annual_increase_rate=0.05,
        ),
        financing=FinancingParameters(
            method=FinancingMethod.LOAN,
            loan_term_years=5,
            loan_interest_rate=0.07,
            down_payment_percentage=0.2,
        ),
        created_date=date.today(),
    )

def create_test_diesel_scenario():
    """Create a simple diesel scenario for testing."""
    return ScenarioInput(
        scenario_name="Diesel Test Scenario",
        vehicle=DieselParameters(
            name="Example Diesel Truck",
            type=VehicleType.DIESEL,
            category=VehicleCategory.ARTICULATED,
            purchase_price=400000.0,
            max_payload_tonnes=35.0,
            range_km=800.0,
            engine=EngineParameters(
                power_kw=350,
                displacement_litres=13,
                euro_emission_standard="Euro VI",
                adblue_required=True,
                adblue_consumption_percent_of_diesel=0.05,
            ),
            fuel_consumption=DieselConsumptionParameters(
                base_rate=0.35,  # L/km
                min_rate=0.25,
                max_rate=0.45,
                load_adjustment_factor=0.15,
                hot_weather_adjustment=0.03,
                cold_weather_adjustment=0.03,
            ),
            maintenance=MaintenanceParameters(
                cost_per_km=0.15,
                annual_fixed_min=700,
                annual_fixed_max=1500,
                annual_fixed_default=1000,
                scheduled_maintenance_interval_km=40000,
                major_service_interval_km=120000
            ),
            residual_value=ResidualValueParameters(
                year_5_range=(0.45, 0.55),
                year_10_range=(0.25, 0.35),
                year_15_range=(0.10, 0.20),
            ),
        ),
        operational=OperationalParameters(
            annual_distance_km=100000,
            operating_days_per_year=260,
            vehicle_life_years=15,
            average_load_factor=0.8,
            is_urban_operation=False,
        ),
        economic=EconomicParameters(
            discount_rate_real=0.07,
            inflation_rate=0.025,
            analysis_period_years=15,
            electricity_price_type=ElectricityRateType.AVERAGE_FLAT_RATE,
            electricity_price_aud_per_kwh=0.25,
            diesel_price_scenario=DieselPriceScenario.MEDIUM_INCREASE,
            diesel_price_aud_per_l=1.5,  # Starting diesel price
            carbon_tax_rate_aud_per_tonne=30.0,
            carbon_tax_annual_increase_rate=0.05,
        ),
        financing=FinancingParameters(
            method=FinancingMethod.LOAN,
            loan_term_years=5,
            loan_interest_rate=0.07,
            down_payment_percentage=0.2,
        ),
        created_date=date.today(),
    )

def print_costs_breakdown(result):
    """Print detailed breakdown of costs for debugging."""
    print(f"Total TCO: {result.total_tco:.2f}")
    print(f"Annual costs (year 0): {result.annual_costs[0].total:.2f}")
    print(f"  - Acquisition: {result.annual_costs[0].acquisition:.2f}")
    print(f"  - Energy: {result.annual_costs[0].energy:.2f}")
    print(f"  - Maintenance: {result.annual_costs[0].maintenance:.2f}")
    print(f"NPV Costs:")
    print(f"  - Acquisition: {result.npv_costs.acquisition:.2f}")
    print(f"  - Energy: {result.npv_costs.energy:.2f}")
    print(f"  - Maintenance: {result.npv_costs.maintenance:.2f}")

def manual_sensitivity_test():
    """Manually test sensitivity to diesel price changes."""
    diesel_scenario = create_test_diesel_scenario()
    calculator = TCOCalculator()
    
    diesel_prices = [1.0, 1.5, 2.0, 2.5, 3.0]
    results = []
    
    print("\nManual Sensitivity Test for Diesel Price:")
    for price in diesel_prices:
        # Create a fresh scenario for each price
        test_scenario = create_test_diesel_scenario()
        test_scenario.economic.diesel_price_aud_per_l = price
        
        result = calculator.calculate(test_scenario)
        energy_cost = result.npv_costs.energy
        total_cost = result.total_tco
        
        results.append({
            "price": price,
            "energy_cost": energy_cost,
            "total_cost": total_cost,
        })
        
        print(f"Diesel Price: {price} AUD/L")
        print(f"  Energy Cost (NPV): {energy_cost:.2f}")
        print(f"  Total TCO: {total_cost:.2f}")
    
    # Verify there's actually variation in the results
    min_tco = min(r["total_cost"] for r in results)
    max_tco = max(r["total_cost"] for r in results)
    tco_range = max_tco - min_tco
    
    print(f"\nTCO Range: {min_tco:.2f} to {max_tco:.2f} (difference: {tco_range:.2f})")
    
    return results

def debug_tipping_point():
    """Debug the tipping point calculation."""
    # Create test scenarios
    bet_scenario = create_test_bet_scenario()
    diesel_scenario = create_test_diesel_scenario()
    
    # Create calculator
    calculator = TCOCalculator()
    
    # Calculate results
    bet_result = calculator.calculate(bet_scenario)
    diesel_result = calculator.calculate(diesel_scenario)
    
    # Print cost breakdowns
    print("BET Cost Breakdown:")
    print_costs_breakdown(bet_result)
    print("\nDiesel Cost Breakdown:")
    print_costs_breakdown(diesel_result)
    
    # Examine strategies implementation for diesel price
    print("\nExamining DieselConsumptionStrategy implementation...")
    
    # Run a manual sensitivity test to check if diesel prices affect TCO
    manual_results = manual_sensitivity_test()
    
    if max(r["total_cost"] for r in manual_results) - min(r["total_cost"] for r in manual_results) < 1000:
        print("\nISSUE FOUND: Diesel price variations have minimal impact on TCO.")
        print("Check DieselConsumptionStrategy._get_diesel_price method in tco_model/strategies.py")
        print("The problem might be that the strategy ignores the diesel_price_aud_per_l parameter.")
    
    # Define parameter and variations for diesel price
    parameter = "economic.diesel_price_aud_per_l"
    variations = [1.0, 1.5, 2.0, 2.5, 3.0]
    
    # Perform sensitivity analysis using the calculator's method
    print("\nRunning sensitivity analysis using calculator method:")
    sensitivity_bet = calculator.perform_sensitivity_analysis(
        bet_scenario,
        "economic.electricity_price_aud_per_kwh",
        [0.25] * len(variations)  # Constant electricity price
    )
    
    sensitivity_diesel = calculator.perform_sensitivity_analysis(
        diesel_scenario,
        parameter,
        variations
    )
    
    # Print sensitivity results
    print("BET TCO values:", sensitivity_bet["tco_values"])
    print("Diesel TCO values:", sensitivity_diesel["tco_values"])
    
    # Calculate differences
    tco_diff = []
    for i in range(len(variations)):
        diff = sensitivity_bet["tco_values"][i] - sensitivity_diesel["tco_values"][i]
        tco_diff.append(diff)
    
    print("TCO differences:", tco_diff)
    
    # Display results in a dataframe
    df = pd.DataFrame({
        'Diesel Price': variations,
        'BET TCO': sensitivity_bet["tco_values"],
        'Diesel TCO': sensitivity_diesel["tco_values"],
        'Difference': tco_diff
    })
    
    print("\nSensitivity Analysis Results:")
    print(df)
    
    # Check if there's a tipping point using our function
    from ui.results.live_preview import determine_has_tipping_point
    has_tipping_point = determine_has_tipping_point(sensitivity_bet, sensitivity_diesel)
    print(f"\nHas tipping point: {has_tipping_point}")
    
    # Calculate tipping point
    from ui.results.live_preview import calculate_tipping_point
    tipping_point = calculate_tipping_point(sensitivity_bet, sensitivity_diesel)
    print(f"Calculated tipping point: {tipping_point}")
    
    # Check calculate_diesel_costs function for more details
    print("\nExamining diesel_price_aud_per_l usage in calculator.py...")
    print("The problem is likely in the DieselConsumptionStrategy._get_diesel_price method")
    print("It might be using diesel_price_scenario instead of the direct diesel_price_aud_per_l value")

if __name__ == "__main__":
    debug_tipping_point() 