"""
Test the BET energy consumption strategy to verify electricity prices affect costs.
"""

import pytest
from tco_model.models import ScenarioInput, BETParameters, VehicleType, EconomicParameters
from tco_model.strategies import BETEnergyConsumptionStrategy


class TestBETEnergyConsumptionStrategy:
    """Tests for the BET energy consumption strategy."""
    
    def test_electricity_price_affects_costs(self, bet_scenario):
        """Test that changing electricity price affects the calculated costs."""
        # Create the strategy
        strategy = BETEnergyConsumptionStrategy()
        
        # Set a base electricity price
        bet_scenario.economic.electricity_price_aud_per_kwh = 0.25
        
        # Set energy consumption to a fixed value for easier calculation
        bet_scenario.vehicle.energy_consumption.base_rate = 1.0  # kWh/km
        bet_scenario.operational.annual_distance_km = 100000  # km
        bet_scenario.vehicle.charging.charging_efficiency = 1.0  # For simple calculation
        
        # Disable demand charges to isolate the electricity price effect
        bet_scenario.vehicle.charging.max_charging_power_kw = 0.0
        
        # Calculate baseline costs
        baseline_costs = strategy.calculate_costs(bet_scenario, 0)
        print(f"Baseline costs with electricity price {bet_scenario.economic.electricity_price_aud_per_kwh}: {baseline_costs}")
        
        # Expected baseline energy cost (excluding demand charges)
        expected_baseline = bet_scenario.operational.annual_distance_km * bet_scenario.vehicle.energy_consumption.base_rate * bet_scenario.economic.electricity_price_aud_per_kwh
        assert abs(baseline_costs - expected_baseline) < 1.0, "Baseline costs should match expected calculation"
        
        # Now double the electricity price
        bet_scenario.economic.electricity_price_aud_per_kwh = 0.5
        
        # Calculate new costs
        new_costs = strategy.calculate_costs(bet_scenario, 0)
        print(f"New costs with electricity price {bet_scenario.economic.electricity_price_aud_per_kwh}: {new_costs}")
        
        # The new costs should be double the baseline costs (since we disabled demand charges)
        assert abs(new_costs - 2 * baseline_costs) < 1.0, "Doubling electricity price should double energy costs"
        
        # Try a third price to verify the relationship
        bet_scenario.economic.electricity_price_aud_per_kwh = 0.1
        third_costs = strategy.calculate_costs(bet_scenario, 0)
        print(f"Third costs with electricity price {bet_scenario.economic.electricity_price_aud_per_kwh}: {third_costs}")
        
        # The third costs should be 0.4x the baseline
        assert abs(third_costs - 0.4 * baseline_costs) < 1.0, "Reducing electricity price should proportionally reduce costs" 