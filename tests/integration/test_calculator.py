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
        
        # Verify basic structure and properties of the result using new field names
        assert result.total_tco is not None  # Changed from npv_total
        assert result.lcod is not None       # Changed from lcod_per_km
        assert result.scenario == bet_scenario  # New property
        
        # Verify annual costs using the new collection structure
        # Now accessing properties directly from the collection
        assert len(result.annual_costs) == bet_scenario.economic.analysis_period_years
        assert len(result.annual_costs.acquisition) == bet_scenario.economic.analysis_period_years
        assert len(result.annual_costs.energy) == bet_scenario.economic.analysis_period_years
        assert len(result.annual_costs.maintenance) == bet_scenario.economic.analysis_period_years
        
        # Check combined properties
        assert len(result.annual_costs.insurance_registration) == bet_scenario.economic.analysis_period_years
        assert len(result.annual_costs.taxes_levies) == bet_scenario.economic.analysis_period_years
        
        # Verify NPV costs and combined properties
        assert hasattr(result.npv_costs, 'acquisition')
        assert hasattr(result.npv_costs, 'insurance_registration')
        assert hasattr(result.npv_costs, 'taxes_levies')
        
        # Verify result is reasonably close to expected values
        # These are just example assertions - actual values would be determined by test data
        assert result.total_tco > 0
        assert result.lcod > 0
        
        # Verify that the totals add up correctly
        component_sum = (
            result.npv_costs.acquisition +
            result.npv_costs.energy +
            result.npv_costs.maintenance +
            result.npv_costs.infrastructure +
            result.npv_costs.battery_replacement +
            result.npv_costs.insurance +
            result.npv_costs.registration +
            result.npv_costs.carbon_tax +
            result.npv_costs.other_taxes +
            result.npv_costs.residual_value
        )
        assert abs(result.total_tco - component_sum) < 0.01  # Allow for small rounding errors
        
        # Verify emissions data is calculated
        assert result.emissions is not None
        assert result.emissions.total_co2_tonnes > 0

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
        assert len(result.annual_costs.total) == diesel_scenario.economic.analysis_period_years
        
        # Verify consistency of data types
        assert isinstance(result.total_tco, float)
        assert isinstance(result.lcod, float)
        
        # Verify emissions data is calculated
        assert result.emissions is not None
        assert result.emissions.total_co2_tonnes > 0

    def test_compare_results(self, bet_scenario, diesel_scenario):
        """Test that the calculator correctly compares two TCO results."""
        # Initialize calculator
        calculator = TCOCalculator()
        
        # Calculate TCO for both scenarios
        bet_result = calculator.calculate(bet_scenario)
        diesel_result = calculator.calculate(diesel_scenario)
        
        # Compare results using the new compare method
        comparison = calculator.compare(bet_result, diesel_result)
        
        # Verify comparison structure and properties
        assert hasattr(comparison, 'tco_difference')  # Renamed from npv_difference
        assert hasattr(comparison, 'tco_percentage')  # Renamed from npv_difference_percentage
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
        # Should have the standardized UI components
        assert "acquisition" in comparison.component_differences
        assert "energy" in comparison.component_differences
        assert "maintenance" in comparison.component_differences
        assert "insurance_registration" in comparison.component_differences
        assert "taxes_levies" in comparison.component_differences
        
        # Verify cheaper option
        if expected_difference > 0:
            assert comparison.cheaper_option == 1  # BET is cheaper
        else:
            assert comparison.cheaper_option == 2  # Diesel is cheaper
            
        # Verify investment analysis is calculated
        assert comparison.investment_analysis is not None
        assert hasattr(comparison.investment_analysis, 'npv_difference')
        assert hasattr(comparison.investment_analysis, 'payback_years')
        assert hasattr(comparison.investment_analysis, 'roi')
        assert hasattr(comparison.investment_analysis, 'has_payback')


class TestTCOCalculatorEdgeCases:
    """Tests for edge cases in the TCO Calculator."""

    def test_zero_values_scenario(self, edge_case_zero_values_scenario):
        """Test calculator with zero values."""
        # Initialize calculator
        calculator = TCOCalculator()
        
        # Calculate TCO
        result = calculator.calculate(edge_case_zero_values_scenario)
        
        # With minimal distance, LCOD will be very high but should be a finite number
        assert result.lcod is not None
        assert result.lcod > 0
        assert np.isfinite(result.lcod)

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
        assert len(result.annual_costs.total) == edge_case_low_usage_scenario.economic.analysis_period_years 