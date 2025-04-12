"""
Integration tests for the TCO Calculator.

These tests verify that the TCO calculator correctly orchestrates
the calculation of all cost components and produces valid results.
"""

import pytest
import pandas as pd
import numpy as np

from tco_model.calculator import TCOCalculator
from tco_model.models import VehicleType


class TestTCOCalculator:
    """Integration tests for the TCO Calculator."""

    def test_calculate_bet_scenario(self, bet_scenario):
        """Test that the calculator produces valid results for a BET scenario."""
        # Initialize calculator
        calculator = TCOCalculator()
        
        # Calculate TCO
        result = calculator.calculate(bet_scenario)
        
        # Verify basic structure and properties of the result
        assert result.total_tco is not None
        assert result.lcod is not None
        assert result.scenario == bet_scenario
        
        # Verify annual costs
        assert hasattr(result, 'annual_costs')
        assert hasattr(result.annual_costs, 'acquisition')
        assert hasattr(result.annual_costs, 'energy')
        assert hasattr(result.annual_costs, 'maintenance')
        assert hasattr(result.annual_costs, 'infrastructure')
        assert hasattr(result.annual_costs, 'battery_replacement')
        assert hasattr(result.annual_costs, 'insurance_registration')
        assert hasattr(result.annual_costs, 'taxes_levies')
        assert hasattr(result.annual_costs, 'residual_value')
        assert hasattr(result.annual_costs, 'total')
        
        # Verify NPV costs
        assert hasattr(result, 'npv_costs')
        assert hasattr(result.npv_costs, 'acquisition')
        assert hasattr(result.npv_costs, 'energy')
        assert hasattr(result.npv_costs, 'maintenance')
        assert hasattr(result.npv_costs, 'infrastructure')
        assert hasattr(result.npv_costs, 'battery_replacement')
        assert hasattr(result.npv_costs, 'insurance_registration')
        assert hasattr(result.npv_costs, 'taxes_levies')
        assert hasattr(result.npv_costs, 'residual_value')
        assert hasattr(result.npv_costs, 'total')
        
        # Verify that NPV total equals sum of components
        component_sum = (
            result.npv_costs.acquisition +
            result.npv_costs.energy +
            result.npv_costs.maintenance +
            result.npv_costs.infrastructure +
            result.npv_costs.battery_replacement +
            result.npv_costs.insurance_registration +
            result.npv_costs.taxes_levies +
            result.npv_costs.residual_value
        )
        assert result.npv_costs.total == pytest.approx(component_sum)
        
        # Verify that total_tco equals npv_costs.total
        assert result.total_tco == result.npv_costs.total
        
        # Verify that LCOD calculation is correct (if annual distance > 0)
        if bet_scenario.operational.annual_distance > 0:
            expected_lcod = result.total_tco / (bet_scenario.operational.annual_distance * bet_scenario.operational.analysis_period)
            assert result.lcod == pytest.approx(expected_lcod)

    def test_calculate_diesel_scenario(self, diesel_scenario):
        """Test that the calculator produces valid results for a diesel scenario."""
        # Initialize calculator
        calculator = TCOCalculator()
        
        # Calculate TCO
        result = calculator.calculate(diesel_scenario)
        
        # Verify basic structure and properties of the result
        assert result.total_tco is not None
        assert result.lcod is not None
        assert result.scenario == diesel_scenario
        
        # Verify annual costs for each year
        assert len(result.annual_costs.total) == diesel_scenario.operational.analysis_period
        
        # Verify consistency of data types
        assert isinstance(result.total_tco, float)
        assert isinstance(result.lcod, float)

    def test_compare_results(self, bet_scenario, diesel_scenario):
        """Test that the calculator correctly compares two TCO results."""
        # Initialize calculator
        calculator = TCOCalculator()
        
        # Calculate TCO for both scenarios
        bet_result = calculator.calculate(bet_scenario)
        diesel_result = calculator.calculate(diesel_scenario)
        
        # Compare results
        comparison = calculator.compare_results(bet_result, diesel_result)
        
        # Verify comparison structure and properties
        assert hasattr(comparison, 'tco_difference')
        assert hasattr(comparison, 'tco_percentage')
        assert hasattr(comparison, 'lcod_difference')
        assert hasattr(comparison, 'component_differences')
        assert hasattr(comparison, 'cheaper_option')
        
        # Verify the difference calculation is correct
        expected_difference = diesel_result.total_tco - bet_result.total_tco
        assert comparison.tco_difference == expected_difference
        
        # Verify percentage calculation
        if bet_result.total_tco != 0:
            expected_percentage = (expected_difference / bet_result.total_tco) * 100
            assert comparison.tco_percentage == expected_percentage
        
        # Verify LCOD difference
        expected_lcod_difference = diesel_result.lcod - bet_result.lcod
        assert comparison.lcod_difference == expected_lcod_difference
        
        # Verify component differences
        for component in bet_result.npv_costs.__dict__.keys():
            expected_diff = getattr(diesel_result.npv_costs, component) - getattr(bet_result.npv_costs, component)
            assert comparison.component_differences[component] == expected_diff
        
        # Verify cheaper option
        if expected_difference > 0:
            assert comparison.cheaper_option == 1  # BET is cheaper
        else:
            assert comparison.cheaper_option == 2  # Diesel is cheaper


class TestTCOCalculatorEdgeCases:
    """Tests for edge cases in the TCO Calculator."""

    def test_zero_values_scenario(self, edge_case_zero_values_scenario):
        """Test calculator with zero values."""
        # Initialize calculator
        calculator = TCOCalculator()
        
        # Calculate TCO
        result = calculator.calculate(edge_case_zero_values_scenario)
        
        # Verify LCOD calculation handles zero distance
        assert result.lcod == 0 or result.lcod == pytest.approx(0)

    def test_high_usage_scenario(self, edge_case_high_usage_scenario):
        """Test calculator with high usage values."""
        # Initialize calculator
        calculator = TCOCalculator()
        
        # Calculate TCO
        result = calculator.calculate(edge_case_high_usage_scenario)
        
        # Just verify it runs without errors
        assert result.total_tco is not None
        assert result.lcod is not None

    def test_low_usage_scenario(self, edge_case_low_usage_scenario):
        """Test calculator with low usage values."""
        # Initialize calculator
        calculator = TCOCalculator()
        
        # Calculate TCO
        result = calculator.calculate(edge_case_low_usage_scenario)
        
        # Verify LCOD calculation with low distance
        assert result.lcod is not None
        
        # Low usage should still have annual costs for each year of the analysis period
        assert len(result.annual_costs.total) == edge_case_low_usage_scenario.operational.analysis_period 