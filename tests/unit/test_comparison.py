"""
Unit tests for the TCO comparison functionality.

These tests verify that comparison between scenarios works correctly with the new field names.
"""

import pytest
from datetime import date

from tco_model.models import (
    TCOOutput, 
    NPVCosts, 
    AnnualCosts,
    AnnualCostsCollection, 
    ComparisonResult,
    VehicleType
)
from tco_model.calculator import TCOCalculator


class TestComparisonFunctionality:
    """Tests for the comparison functionality."""
    
    def test_compare_results(self, bet_scenario, diesel_scenario):
        """Test that the calculator correctly compares two results."""
        calculator = TCOCalculator()
        
        result1 = calculator.calculate(bet_scenario)
        result2 = calculator.calculate(diesel_scenario)
        
        comparison = calculator.compare_results(result1, result2)
        
        # Verify comparison uses new field names
        assert hasattr(comparison, 'tco_difference')  # Renamed from npv_difference
        assert hasattr(comparison, 'tco_percentage')  # Renamed from npv_difference_percentage
        assert hasattr(comparison, 'lcod_difference')
        assert hasattr(comparison, 'lcod_difference_percentage')
        assert hasattr(comparison, 'payback_year')
        
        # Test new component_differences property
        assert hasattr(comparison, 'component_differences')
        diffs = comparison.component_differences
        
        # Should have the standardized UI components
        assert "acquisition" in diffs
        assert "energy" in diffs
        assert "maintenance" in diffs
        assert "insurance_registration" in diffs
        assert "taxes_levies" in diffs
        
        # Test cheaper_option property
        assert comparison.cheaper_option in [1, 2]
        if comparison.tco_difference > 0:
            assert comparison.cheaper_option == 1
        else:
            assert comparison.cheaper_option == 2
    
    def test_comparison_result_creation(self):
        """Test the creation of ComparisonResult with the factory method."""
        # Create test outputs
        output1 = create_test_output(total_tco=100000, lcod=0.20)
        output2 = create_test_output(total_tco=120000, lcod=0.24)
        
        # Use the factory method
        comparison = ComparisonResult.create(output1, output2)
        
        # Verify results
        assert comparison.tco_difference == 20000  # 120000 - 100000
        assert comparison.tco_percentage == 20.0   # (20000 / 100000) * 100
        assert comparison.lcod_difference == pytest.approx(0.04)  # 0.24 - 0.20
        assert comparison.lcod_difference_percentage == pytest.approx(20.0)  # (0.04 / 0.20) * 100
        
        # Test cheaper option
        assert comparison.cheaper_option == 1  # output1 is cheaper
    
    def test_deprecated_field_access_in_comparison(self):
        """Test that the new comparison field names are used correctly."""
        output1 = create_test_output(total_tco=100000)
        output2 = create_test_output(total_tco=120000)
        
        comparison = ComparisonResult.create(output1, output2)
        
        # Access new field names directly
        tco_diff = comparison.tco_difference
        tco_pct = comparison.tco_percentage
        
        # Verify the values are correct
        assert tco_diff == 20000
        assert tco_pct == 20.0


# Helper function to create test output
def create_test_output(total_tco=100000, lcod=0.2, **kwargs):
    """Helper function to create a test TCOOutput object."""
    npv_costs = NPVCosts(
        acquisition=kwargs.get('acquisition', 70000),
        energy=kwargs.get('energy', 20000),
        maintenance=kwargs.get('maintenance', 10000),
        infrastructure=kwargs.get('infrastructure', 5000),
        battery_replacement=kwargs.get('battery_replacement', 0),
        insurance=kwargs.get('insurance', 3000),
        registration=kwargs.get('registration', 2000),
        carbon_tax=kwargs.get('carbon_tax', 1000),
        other_taxes=kwargs.get('other_taxes', 500),
        residual_value=kwargs.get('residual_value', -10000)
    )
    
    return TCOOutput(
        scenario_name="Test Scenario",
        vehicle_name="Test Vehicle",
        vehicle_type=VehicleType.BATTERY_ELECTRIC,
        analysis_period_years=5,
        total_distance_km=500000,
        annual_costs=AnnualCostsCollection(costs=[]),
        npv_costs=npv_costs,
        total_nominal_cost=total_tco * 1.1,  # Just for test purposes
        total_tco=total_tco,
        lcod=lcod,
        calculation_date=date.today()
    ) 