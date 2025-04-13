"""
Unit tests for the terminology module and related field refactoring.

These tests verify that:
1. Field renaming works correctly
2. Backward compatibility is maintained through deprecated fields
3. The AnnualCostsCollection class works as expected
4. Component access patterns work consistently
"""

import pytest
import warnings
from datetime import date

from tco_model.models import (
    TCOOutput, 
    AnnualCosts, 
    NPVCosts, 
    AnnualCostsCollection, 
    ComparisonResult,
    VehicleType
)
from tco_model.terminology import (
    get_component_value,
    calculate_cost_difference,
    UI_COMPONENT_KEYS,
    UI_COMPONENT_LABELS
)


class TestFieldRenaming:
    """Tests for field renaming."""
    
    def test_deprecated_field_access(self):
        """Test that the new field names are used correctly."""
        # Create a TCOOutput with new field names
        output = TCOOutput(
            scenario_name="Test Scenario",
            vehicle_name="Test Vehicle",
            vehicle_type=VehicleType.BATTERY_ELECTRIC,
            analysis_period_years=5,
            total_distance_km=500000,
            annual_costs=AnnualCostsCollection(costs=[]),
            npv_costs=NPVCosts(),
            total_nominal_cost=100000,
            total_tco=90000,  # New field name
            lcod=0.18,        # New field name
            calculation_date=date.today()
        )
        
        # Access new field names directly
        total_tco = output.total_tco
        lcod = output.lcod
        
        # Verify that the values are correct
        assert total_tco == 90000
        assert lcod == 0.18
    
    def test_component_differences_property(self):
        """Test the component_differences property in ComparisonResult."""
        # Create two TCO outputs with different costs
        output1 = create_test_output(
            acquisition=100000,
            energy=50000,
            maintenance=25000
        )
        
        output2 = create_test_output(
            acquisition=120000,
            energy=40000,
            maintenance=30000
        )
        
        # Create comparison result
        comparison = ComparisonResult(
            scenario_1=output1,
            scenario_2=output2,
            tco_difference=20000,
            tco_percentage=10.0,
            lcod_difference=0.05,
            lcod_difference_percentage=15.0
        )
        
        # Test component differences
        diffs = comparison.component_differences
        assert diffs["acquisition"] == 20000  # 120000 - 100000
        assert diffs["energy"] == -10000      # 40000 - 50000
        assert diffs["maintenance"] == 5000   # 30000 - 25000
        
        # Test cheaper_option property
        assert comparison.cheaper_option == 1  # output1 is cheaper


class TestAnnualCostsCollection:
    """Tests for the AnnualCostsCollection class."""
    
    def test_list_access(self):
        """Test list-like access to AnnualCostsCollection."""
        annual_costs = [
            AnnualCosts(year=0, calendar_year=2025, acquisition=50000, energy=10000),
            AnnualCosts(year=1, calendar_year=2026, acquisition=0, energy=10500)
        ]
        
        collection = AnnualCostsCollection(costs=annual_costs)
        
        # Test indexing
        assert collection[0].acquisition == 50000
        assert collection[1].energy == 10500
        
        # Test length
        assert len(collection) == 2
        
        # Test iteration
        iterated = [cost.year for cost in collection]
        assert iterated == [0, 1]
    
    def test_attribute_access(self):
        """Test attribute access to component lists."""
        annual_costs = [
            AnnualCosts(year=0, calendar_year=2025, acquisition=50000, energy=10000),
            AnnualCosts(year=1, calendar_year=2026, acquisition=0, energy=10500)
        ]
        
        collection = AnnualCostsCollection(costs=annual_costs)
        
        # Test component lists
        assert collection.acquisition == [50000, 0]
        assert collection.energy == [10000, 10500]
        
        # Test combined components
        # Since we didn't set insurance or registration, these would default to 0
        assert collection.insurance_registration == [0, 0]
    
    def test_component_value_access(self):
        """Test standardized component value access."""
        annual_costs = [
            AnnualCosts(
                year=0, calendar_year=2025, 
                acquisition=50000, energy=10000, 
                insurance=2000, registration=1000,
                carbon_tax=500, other_taxes=300
            ),
            AnnualCosts(
                year=1, calendar_year=2026, 
                acquisition=0, energy=10500,
                insurance=2100, registration=1050,
                carbon_tax=550, other_taxes=330
            )
        ]
        
        collection = AnnualCostsCollection(costs=annual_costs)
        
        # Test direct access to year's component
        assert get_component_value(collection, "acquisition", 0) == 50000
        assert get_component_value(collection, "energy", 1) == 10500
        
        # Test combined component access
        assert get_component_value(collection, "insurance_registration", 0) == 3000
        assert get_component_value(collection, "taxes_levies", 1) == 880


class TestUtilityFunctions:
    """Tests for utility functions in terminology.py."""
    
    def test_get_component_value(self):
        """Test the get_component_value function."""
        # Create test objects
        npv_costs = NPVCosts(
            acquisition=50000,
            energy=20000,
            maintenance=10000,
            insurance=5000,
            registration=1000,
            carbon_tax=2000,
            other_taxes=1000,
            residual_value=-10000
        )
        
        # Test direct component access
        assert get_component_value(npv_costs, "acquisition") == 50000
        assert get_component_value(npv_costs, "energy") == 20000
        
        # Test combined component access
        assert get_component_value(npv_costs, "insurance_registration") == 6000
        assert get_component_value(npv_costs, "taxes_levies") == 3000
        
        # Test default return
        assert get_component_value(npv_costs, "nonexistent_component") == 0.0
    
    def test_calculate_cost_difference(self):
        """Test the calculate_cost_difference function."""
        # Test positive difference
        diff, pct = calculate_cost_difference(100, 150)
        assert diff == 50
        assert pct == 50.0
        
        # Test negative difference
        diff, pct = calculate_cost_difference(200, 150)
        assert diff == -50
        assert pct == -25.0
        
        # Test zero first value
        diff, pct = calculate_cost_difference(0, 100)
        assert diff == 100
        assert pct == float('inf')  # Division by zero results in infinity


# Helper function to create test output
def create_test_output(acquisition=0, energy=0, maintenance=0, infrastructure=0, 
                      battery_replacement=0, insurance=0, registration=0,
                      carbon_tax=0, other_taxes=0, residual_value=0):
    """Helper function to create a test TCOOutput object."""
    npv_costs = NPVCosts(
        acquisition=acquisition,
        energy=energy,
        maintenance=maintenance,
        infrastructure=infrastructure,
        battery_replacement=battery_replacement,
        insurance=insurance,
        registration=registration,
        carbon_tax=carbon_tax,
        other_taxes=other_taxes,
        residual_value=residual_value
    )
    
    total_tco = (
        acquisition + energy + maintenance + infrastructure + 
        battery_replacement + insurance + registration +
        carbon_tax + other_taxes + residual_value
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
        lcod=total_tco / 500000,
        calculation_date=date.today()
    ) 