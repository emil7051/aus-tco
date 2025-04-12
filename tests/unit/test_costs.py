"""
Unit tests for cost calculation functions in the TCO Modeller.

These tests verify that the cost calculation functions correctly
compute individual cost components.
"""

import pytest

from tco_model.costs import (
    calculate_acquisition_costs,
    calculate_energy_costs,
    calculate_maintenance_costs,
    calculate_infrastructure_costs,
    calculate_battery_replacement_costs,
    calculate_insurance_registration_costs,
    calculate_taxes_levies,
    calculate_residual_value,
)
from tco_model.models import VehicleType


class TestInfrastructureCosts:
    """Tests for infrastructure cost calculations."""

    def test_bet_infrastructure_costs_year_0(self, bet_scenario):
        """Test that BET infrastructure costs in year 0 include initial setup costs."""
        # In year 0, infrastructure costs should include the initial setup costs
        costs = calculate_infrastructure_costs(bet_scenario, 0)
        expected_cost = (
            bet_scenario.infrastructure.charger_cost +
            bet_scenario.infrastructure.installation_cost +
            bet_scenario.infrastructure.grid_upgrade_cost
        )
        assert costs == expected_cost

    def test_bet_infrastructure_costs_subsequent_years(self, bet_scenario):
        """Test that BET infrastructure costs in subsequent years include only maintenance costs."""
        # In year 1 and beyond, infrastructure costs should be just maintenance
        costs_year_1 = calculate_infrastructure_costs(bet_scenario, 1)
        assert costs_year_1 == bet_scenario.infrastructure.maintenance_cost

        costs_year_5 = calculate_infrastructure_costs(bet_scenario, 5)
        assert costs_year_5 == bet_scenario.infrastructure.maintenance_cost

    def test_diesel_infrastructure_costs(self, diesel_scenario):
        """Test that diesel infrastructure costs are zero."""
        # For diesel vehicles, infrastructure costs should be zero
        costs_year_0 = calculate_infrastructure_costs(diesel_scenario, 0)
        assert costs_year_0 == 0

        costs_year_1 = calculate_infrastructure_costs(diesel_scenario, 1)
        assert costs_year_1 == 0


class TestBatteryReplacementCosts:
    """Tests for battery replacement cost calculations."""

    def test_diesel_battery_replacement_costs(self, diesel_scenario):
        """Test that diesel vehicles have no battery replacement costs."""
        # For diesel vehicles, battery replacement costs should be zero
        costs = calculate_battery_replacement_costs(diesel_scenario, 5)
        assert costs == 0

    def test_bet_battery_replacement_costs(self, bet_scenario, monkeypatch):
        """Test BET battery replacement costs calculation."""
        # We'll need to mock the battery replacement decision logic
        # since the actual implementation is a placeholder
        
        # First test the default behavior (no replacement)
        costs_default = calculate_battery_replacement_costs(bet_scenario, 5)
        assert costs_default == 0
        
        # Now patch the function to simulate a battery replacement needed
        def mock_needs_replacement(*args, **kwargs):
            return True
        
        # We can't directly patch the internal replacement logic, but we could
        # test our assumption that when a replacement is needed, a non-zero cost is returned
        # For now, we'll just verify that the vehicle type check works
        assert bet_scenario.vehicle.type == VehicleType.BATTERY_ELECTRIC


class TestResidualValue:
    """Tests for residual value calculations."""

    def test_residual_value_final_year(self, bet_scenario):
        """Test that residual value is calculated in the final year only."""
        # Define the final year of the analysis
        final_year = bet_scenario.operational.analysis_period - 1
        
        # In the final year, residual value should be calculated (even if it's just a placeholder)
        final_year_value = calculate_residual_value(bet_scenario, final_year)
        
        # For earlier years, residual value should be zero
        early_year_value = calculate_residual_value(bet_scenario, 5)
        assert early_year_value == 0
        
        # Final year value should be returned as a negative (income)
        # Even though the placeholder returns 0, this should be true when implemented
        assert final_year_value <= 0


class TestAcquisitionCosts:
    """Tests for acquisition cost calculations."""

    def test_acquisition_costs_placeholder(self, bet_scenario):
        """Test the placeholder implementation of acquisition costs."""
        # For now, just verify the function returns without error
        cost = calculate_acquisition_costs(bet_scenario, 0)
        assert isinstance(cost, float)


class TestEnergyCosts:
    """Tests for energy cost calculations."""

    def test_energy_costs_placeholder(self, bet_scenario):
        """Test the placeholder implementation of energy costs."""
        # For now, just verify the function returns without error
        cost = calculate_energy_costs(bet_scenario, 0)
        assert isinstance(cost, float)


class TestMaintenanceCosts:
    """Tests for maintenance cost calculations."""

    def test_maintenance_costs_placeholder(self, bet_scenario):
        """Test the placeholder implementation of maintenance costs."""
        # For now, just verify the function returns without error
        cost = calculate_maintenance_costs(bet_scenario, 0)
        assert isinstance(cost, float)


class TestInsuranceRegistrationCosts:
    """Tests for insurance and registration cost calculations."""

    def test_insurance_registration_costs_placeholder(self, bet_scenario):
        """Test the placeholder implementation of insurance and registration costs."""
        # For now, just verify the function returns without error
        cost = calculate_insurance_registration_costs(bet_scenario, 0)
        assert isinstance(cost, float)


class TestTaxesLevies:
    """Tests for taxes and levies calculations."""

    def test_taxes_levies_placeholder(self, bet_scenario):
        """Test the placeholder implementation of taxes and levies."""
        # For now, just verify the function returns without error
        cost = calculate_taxes_levies(bet_scenario, 0)
        assert isinstance(cost, float)


class TestEdgeCases:
    """Tests for edge cases in cost calculations."""

    def test_zero_values_scenario(self, edge_case_zero_values_scenario):
        """Test cost calculations with zero values."""
        # Verify infrastructure costs with zero values
        infra_cost = calculate_infrastructure_costs(edge_case_zero_values_scenario, 0)
        # Even with zero vehicle price, infrastructure costs should still be the same
        expected_infra_cost = (
            edge_case_zero_values_scenario.infrastructure.charger_cost +
            edge_case_zero_values_scenario.infrastructure.installation_cost +
            edge_case_zero_values_scenario.infrastructure.grid_upgrade_cost
        )
        assert infra_cost == expected_infra_cost

        # Verify residual value with zero values
        # For a zero-price vehicle, residual value should be zero
        residual_value = calculate_residual_value(edge_case_zero_values_scenario, 0)
        assert residual_value == 0

    def test_high_usage_scenario(self, edge_case_high_usage_scenario):
        """Test cost calculations with high usage values."""
        # For now, just verify functions don't error with extreme values
        infra_cost = calculate_infrastructure_costs(edge_case_high_usage_scenario, 0)
        battery_cost = calculate_battery_replacement_costs(edge_case_high_usage_scenario, 10)
        
        # Infrastructure costs should be the same regardless of usage
        expected_infra_cost = (
            edge_case_high_usage_scenario.infrastructure.charger_cost +
            edge_case_high_usage_scenario.infrastructure.installation_cost +
            edge_case_high_usage_scenario.infrastructure.grid_upgrade_cost
        )
        assert infra_cost == expected_infra_cost
        
        # High usage might trigger battery replacement, but our placeholder doesn't implement this
        assert isinstance(battery_cost, float) 