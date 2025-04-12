"""
Integration tests for the TCO Calculator payback calculation functionality.

These tests verify that the payback year calculation works correctly
for different scenarios.
"""

import pytest
import numpy as np

from tco_model.calculator import TCOCalculator
from tco_model.models import TCOOutput, AnnualCosts


class TestPaybackCalculation:
    """Tests for payback period calculation."""
    
    def test_simple_payback_calculation(self):
        """Test payback calculation with a simple crossover scenario."""
        # Create a calculator instance
        calculator = TCOCalculator()
        
        # Create mock TCOOutput objects with annual costs that have a clear payback period
        result1 = TCOOutput(
            scenario_name="Scenario1",
            vehicle_name="Vehicle1",
            vehicle_type="bet",
            analysis_period_years=5,
            total_distance_km=500000,
            annual_costs=[
                AnnualCosts(year=0, calendar_year=2023, acquisition=100000, energy=10000, maintenance=5000, 
                           infrastructure=20000, battery_replacement=0, insurance=5000, registration=1000, 
                           carbon_tax=0, other_taxes=0, residual_value=0, total=141000),
                AnnualCosts(year=1, calendar_year=2024, acquisition=0, energy=10000, maintenance=5000, 
                           infrastructure=1000, battery_replacement=0, insurance=5000, registration=1000, 
                           carbon_tax=0, other_taxes=0, residual_value=0, total=22000),
                AnnualCosts(year=2, calendar_year=2025, acquisition=0, energy=10000, maintenance=5000, 
                           infrastructure=1000, battery_replacement=0, insurance=5000, registration=1000, 
                           carbon_tax=0, other_taxes=0, residual_value=0, total=22000),
                AnnualCosts(year=3, calendar_year=2026, acquisition=0, energy=10000, maintenance=5000, 
                           infrastructure=1000, battery_replacement=0, insurance=5000, registration=1000, 
                           carbon_tax=0, other_taxes=0, residual_value=0, total=22000),
                AnnualCosts(year=4, calendar_year=2027, acquisition=0, energy=10000, maintenance=5000, 
                           infrastructure=1000, battery_replacement=0, insurance=5000, registration=1000, 
                           carbon_tax=0, other_taxes=0, residual_value=-40000, total=-18000)
            ],
            npv_costs=None,
            total_nominal_cost=189000,
            npv_total=172000,
            lcod_per_km=0.344
        )
        
        result2 = TCOOutput(
            scenario_name="Scenario2",
            vehicle_name="Vehicle2",
            vehicle_type="diesel",
            analysis_period_years=5,
            total_distance_km=500000,
            annual_costs=[
                AnnualCosts(year=0, calendar_year=2023, acquisition=80000, energy=20000, maintenance=7000, 
                           infrastructure=0, battery_replacement=0, insurance=4000, registration=2000, 
                           carbon_tax=2000, other_taxes=1000, residual_value=0, total=116000),
                AnnualCosts(year=1, calendar_year=2024, acquisition=0, energy=20000, maintenance=7000, 
                           infrastructure=0, battery_replacement=0, insurance=4000, registration=2000, 
                           carbon_tax=2000, other_taxes=1000, residual_value=0, total=36000),
                AnnualCosts(year=2, calendar_year=2025, acquisition=0, energy=20000, maintenance=7000, 
                           infrastructure=0, battery_replacement=0, insurance=4000, registration=2000, 
                           carbon_tax=2000, other_taxes=1000, residual_value=0, total=36000),
                AnnualCosts(year=3, calendar_year=2026, acquisition=0, energy=20000, maintenance=7000, 
                           infrastructure=0, battery_replacement=0, insurance=4000, registration=2000, 
                           carbon_tax=2000, other_taxes=1000, residual_value=0, total=36000),
                AnnualCosts(year=4, calendar_year=2027, acquisition=0, energy=20000, maintenance=7000, 
                           infrastructure=0, battery_replacement=0, insurance=4000, registration=2000, 
                           carbon_tax=2000, other_taxes=1000, residual_value=-30000, total=6000)
            ],
            npv_costs=None,
            total_nominal_cost=230000,
            npv_total=210000,
            lcod_per_km=0.42
        )
        
        # The payback year should be 3
        # Cumulative costs:
        # Year 0: 141000 vs 116000 (BET is more expensive)
        # Year 1: 163000 vs 152000 (BET is more expensive) 
        # Year 2: 185000 vs 188000 (BET is cheaper) - payback year
        # Year 3: 207000 vs 224000 (BET is cheaper)
        # Year 4: 189000 vs 230000 (BET is cheaper)
        
        payback_year = calculator._calculate_payback_year(result1, result2)
        assert payback_year == 2
    
    def test_no_payback_scenario(self):
        """Test scenario where there is no payback within the analysis period."""
        # Create a calculator instance
        calculator = TCOCalculator()
        
        # Create mock TCOOutput objects where the first option never becomes cheaper
        result1 = TCOOutput(
            scenario_name="NeverCheaper",
            vehicle_name="Vehicle1",
            vehicle_type="bet",
            analysis_period_years=3,
            total_distance_km=300000,
            annual_costs=[
                AnnualCosts(year=0, calendar_year=2023, acquisition=100000, energy=15000, maintenance=5000, 
                           infrastructure=20000, battery_replacement=0, insurance=5000, registration=1000, 
                           carbon_tax=0, other_taxes=0, residual_value=0, total=146000),
                AnnualCosts(year=1, calendar_year=2024, acquisition=0, energy=15000, maintenance=5000, 
                           infrastructure=1000, battery_replacement=0, insurance=5000, registration=1000, 
                           carbon_tax=0, other_taxes=0, residual_value=0, total=27000),
                AnnualCosts(year=2, calendar_year=2025, acquisition=0, energy=15000, maintenance=5000, 
                           infrastructure=1000, battery_replacement=20000, insurance=5000, registration=1000, 
                           carbon_tax=0, other_taxes=0, residual_value=-30000, total=17000)
            ],
            npv_costs=None,
            total_nominal_cost=190000,
            npv_total=180000,
            lcod_per_km=0.6
        )
        
        result2 = TCOOutput(
            scenario_name="AlwaysCheaper",
            vehicle_name="Vehicle2",
            vehicle_type="diesel",
            analysis_period_years=3,
            total_distance_km=300000,
            annual_costs=[
                AnnualCosts(year=0, calendar_year=2023, acquisition=60000, energy=15000, maintenance=5000, 
                           infrastructure=0, battery_replacement=0, insurance=3000, registration=1000, 
                           carbon_tax=1000, other_taxes=1000, residual_value=0, total=86000),
                AnnualCosts(year=1, calendar_year=2024, acquisition=0, energy=15000, maintenance=5000, 
                           infrastructure=0, battery_replacement=0, insurance=3000, registration=1000, 
                           carbon_tax=1000, other_taxes=1000, residual_value=0, total=26000),
                AnnualCosts(year=2, calendar_year=2025, acquisition=0, energy=15000, maintenance=5000, 
                           infrastructure=0, battery_replacement=0, insurance=3000, registration=1000, 
                           carbon_tax=1000, other_taxes=1000, residual_value=-20000, total=6000)
            ],
            npv_costs=None,
            total_nominal_cost=118000,
            npv_total=110000,
            lcod_per_km=0.367
        )
        
        # Cumulative costs:
        # Year 0: 146000 vs 86000 (BET is more expensive)
        # Year 1: 173000 vs 112000 (BET is more expensive)
        # Year 2: 190000 vs 118000 (BET is more expensive)
        # No payback
        
        payback_year = calculator._calculate_payback_year(result1, result2)
        assert payback_year is None
    
    def test_immediate_payback_scenario(self):
        """Test scenario where the first option is immediately cheaper."""
        # Create a calculator instance
        calculator = TCOCalculator()
        
        # Create mock TCOOutput objects where the first option is immediately cheaper
        result1 = TCOOutput(
            scenario_name="ImmediatelyCheaper",
            vehicle_name="Vehicle1",
            vehicle_type="bet",
            analysis_period_years=3,
            total_distance_km=300000,
            annual_costs=[
                AnnualCosts(year=0, calendar_year=2023, acquisition=50000, energy=10000, maintenance=5000, 
                           infrastructure=10000, battery_replacement=0, insurance=3000, registration=1000, 
                           carbon_tax=0, other_taxes=0, residual_value=0, total=79000),
                AnnualCosts(year=1, calendar_year=2024, acquisition=0, energy=10000, maintenance=5000, 
                           infrastructure=1000, battery_replacement=0, insurance=3000, registration=1000, 
                           carbon_tax=0, other_taxes=0, residual_value=0, total=20000),
                AnnualCosts(year=2, calendar_year=2025, acquisition=0, energy=10000, maintenance=5000, 
                           infrastructure=1000, battery_replacement=0, insurance=3000, registration=1000, 
                           carbon_tax=0, other_taxes=0, residual_value=-20000, total=0)
            ],
            npv_costs=None,
            total_nominal_cost=99000,
            npv_total=95000,
            lcod_per_km=0.317
        )
        
        result2 = TCOOutput(
            scenario_name="ExpensiveOption",
            vehicle_name="Vehicle2",
            vehicle_type="diesel",
            analysis_period_years=3,
            total_distance_km=300000,
            annual_costs=[
                AnnualCosts(year=0, calendar_year=2023, acquisition=80000, energy=15000, maintenance=7000, 
                           infrastructure=0, battery_replacement=0, insurance=4000, registration=2000, 
                           carbon_tax=2000, other_taxes=1000, residual_value=0, total=111000),
                AnnualCosts(year=1, calendar_year=2024, acquisition=0, energy=15000, maintenance=7000, 
                           infrastructure=0, battery_replacement=0, insurance=4000, registration=2000, 
                           carbon_tax=2000, other_taxes=1000, residual_value=0, total=31000),
                AnnualCosts(year=2, calendar_year=2025, acquisition=0, energy=15000, maintenance=7000, 
                           infrastructure=0, battery_replacement=0, insurance=4000, registration=2000, 
                           carbon_tax=2000, other_taxes=1000, residual_value=-25000, total=6000)
            ],
            npv_costs=None,
            total_nominal_cost=148000,
            npv_total=140000,
            lcod_per_km=0.467
        )
        
        # Cumulative costs:
        # Year 0: 79000 vs 111000 (BET is cheaper immediately)
        # Year 1: 99000 vs 142000 (BET is cheaper)
        # Year 2: 99000 vs 148000 (BET is cheaper)
        
        payback_year = calculator._calculate_payback_year(result1, result2)
        assert payback_year == 0 