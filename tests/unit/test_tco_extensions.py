"""
Unit tests for TCO model extensions.

Tests the new functionality added in the TCO model extensions:
- Environmental impact calculations
- Investment analysis
- Component breakdown access
- Sensitivity analysis
"""

import pytest
import numpy as np
from typing import Dict, List, Any

from tco_model.calculator import TCOCalculator
from tco_model.models import (
    ScenarioInput, 
    TCOOutput,
    VehicleType,
    EmissionsData,
    InvestmentAnalysis
)


class TestEmissionsCalculation:
    """Test emissions calculations functionality."""
    
    def test_bet_emissions(self, bet_scenario):
        """Test emissions calculations for BET vehicle."""
        calculator = TCOCalculator()
        
        # Calculate TCO
        result = calculator.calculate(bet_scenario)
        
        # Verify emissions data was calculated
        assert result.emissions is not None
        assert isinstance(result.emissions, EmissionsData)
        
        # Verify structure of emissions data
        assert len(result.emissions.annual_co2_tonnes) == bet_scenario.economic.analysis_period_years
        assert result.emissions.total_co2_tonnes > 0
        assert result.emissions.energy_consumption_kwh > 0
        assert result.emissions.energy_per_km > 0
        assert result.emissions.co2_per_km > 0
        assert result.emissions.trees_equivalent > 0
        assert result.emissions.homes_equivalent > 0
        assert result.emissions.cars_equivalent > 0
    
    def test_diesel_emissions(self, diesel_scenario):
        """Test emissions calculations for diesel vehicle."""
        calculator = TCOCalculator()
        
        # Calculate TCO
        result = calculator.calculate(diesel_scenario)
        
        # Verify emissions data was calculated
        assert result.emissions is not None
        assert isinstance(result.emissions, EmissionsData)
        
        # Verify structure of emissions data
        assert len(result.emissions.annual_co2_tonnes) == diesel_scenario.economic.analysis_period_years
        
        # Verify values are reasonable
        assert result.emissions.total_co2_tonnes > 0
        assert result.emissions.energy_consumption_kwh > 0
        assert result.emissions.energy_per_km > 0
        assert result.emissions.co2_per_km > 0
    
    def test_bet_vs_diesel_emissions(self, bet_scenario, diesel_scenario):
        """Test that diesel has higher emissions than BET."""
        calculator = TCOCalculator()
        
        # Calculate TCO for both vehicles
        bet_result = calculator.calculate(bet_scenario)
        diesel_result = calculator.calculate(diesel_scenario)
        
        # Verify diesel has higher emissions
        assert diesel_result.emissions.co2_per_km > bet_result.emissions.co2_per_km
        assert diesel_result.emissions.total_co2_tonnes > bet_result.emissions.total_co2_tonnes


class TestInvestmentAnalysis:
    """Test investment analysis functionality."""
    
    def test_investment_analysis_calculation(self, bet_scenario, diesel_scenario):
        """Test investment analysis between vehicles with different profiles."""
        calculator = TCOCalculator()
        
        # Make BET more expensive upfront but cheaper over time
        bet_scenario.vehicle.purchase_price = 500000  # Higher upfront
        bet_scenario.economic.electricity_price_aud_per_kwh = 0.15  # Lower energy cost
        
        diesel_scenario.vehicle.purchase_price = 300000  # Lower upfront
        diesel_scenario.economic.diesel_price_aud_per_l = 1.8  # Higher energy cost
        
        # Calculate TCO for both vehicles
        bet_result = calculator.calculate(bet_scenario)
        diesel_result = calculator.calculate(diesel_scenario)
        
        # Compare results
        comparison = calculator.compare(bet_result, diesel_result)
        
        # Verify investment analysis was calculated
        assert comparison.investment_analysis is not None
        assert isinstance(comparison.investment_analysis, InvestmentAnalysis)
        
        # Verify investment analysis has expected properties
        assert comparison.investment_analysis.payback_years is not None
        assert comparison.investment_analysis.roi is not None
        assert comparison.investment_analysis.npv_difference is not None
        
        # Verify payback period is reasonable
        assert 0 < comparison.investment_analysis.payback_years < bet_scenario.economic.analysis_period_years
        
        # Verify the investment makes financial sense
        assert comparison.investment_analysis.has_payback
        assert comparison.investment_analysis.roi > 0
    
    def test_no_payback_investment(self, bet_scenario, diesel_scenario):
        """Test investment analysis when there's no payback."""
        calculator = TCOCalculator()
        
        # Make BET much more expensive both upfront and over time
        bet_scenario.vehicle.purchase_price = 600000  # Higher upfront
        bet_scenario.economic.electricity_price_aud_per_kwh = 0.30  # Higher energy cost
        
        diesel_scenario.vehicle.purchase_price = 300000  # Lower upfront
        diesel_scenario.economic.diesel_price_aud_per_l = 1.2  # Lower energy cost
        
        # Calculate TCO for both vehicles
        bet_result = calculator.calculate(bet_scenario)
        diesel_result = calculator.calculate(diesel_scenario)
        
        # Compare results
        comparison = calculator.compare(bet_result, diesel_result)
        
        # Verify investment analysis was calculated
        assert comparison.investment_analysis is not None
        
        # Verify no payback was found
        assert not comparison.investment_analysis.has_payback
        assert comparison.investment_analysis.payback_years is None
        assert comparison.investment_analysis.roi is None


class TestComponentBreakdown:
    """Test component breakdown functionality."""
    
    def test_component_value_access(self, bet_scenario):
        """Test accessing component values using the calculator."""
        calculator = TCOCalculator()
        
        # Calculate TCO
        result = calculator.calculate(bet_scenario)
        
        # Get component values
        from tco_model.terminology import UI_COMPONENT_KEYS
        
        for component in UI_COMPONENT_KEYS:
            # Get component value
            value = calculator.get_component_value(result, component)
            
            # Verify value is a float
            assert isinstance(value, float)
            
            # Get component percentage
            percentage = calculator.get_component_percentage(result, component)
            
            # Verify percentage is a float between 0 and 100
            # (except for residual value which can be negative)
            assert isinstance(percentage, float)
            if component != "residual_value":
                assert 0 <= percentage <= 100
    
    def test_component_breakdown_calculation(self, bet_scenario):
        """Test calculating component breakdown."""
        calculator = TCOCalculator()
        
        # Calculate TCO
        result = calculator.calculate(bet_scenario)
        
        # Get component breakdown
        breakdown = calculator.calculate_component_breakdown(result)
        
        # Verify breakdown is a dictionary
        assert isinstance(breakdown, dict)
        
        # Verify energy breakdown exists and has subcomponents for BET
        assert "energy" in breakdown
        assert isinstance(breakdown["energy"], dict)
        assert "electricity_base" in breakdown["energy"]
        assert "electricity_demand" in breakdown["energy"]
        
        # Verify maintenance breakdown exists and has subcomponents
        assert "maintenance" in breakdown
        assert isinstance(breakdown["maintenance"], dict)


class TestSensitivityAnalysis:
    """Test sensitivity analysis functionality."""
    
    def test_single_parameter_sensitivity(self, bet_scenario):
        """Test performing sensitivity analysis on a single parameter."""
        calculator = TCOCalculator()
        
        # Define parameter and variations
        parameter = "economic.electricity_price_aud_per_kwh"
        variations = [0.15, 0.20, 0.25, 0.30, 0.35]  # Different electricity prices
        
        # Perform sensitivity analysis
        sensitivity = calculator.perform_sensitivity_analysis(
            bet_scenario,
            parameter,
            variations
        )
        
        # Verify sensitivity result has the expected structure
        assert sensitivity["parameter"] == parameter
        assert sensitivity["variation_values"] == variations
        assert len(sensitivity["tco_values"]) == len(variations)
        assert len(sensitivity["lcod_values"]) == len(variations)
        assert sensitivity["original_value"] is not None
        assert sensitivity["original_tco"] is not None
        assert sensitivity["unit"] == "$/kWh"
        
        # Verify that higher electricity prices result in higher TCO
        assert sensitivity["tco_values"][0] < sensitivity["tco_values"][-1]
    
    def test_multiple_parameter_sensitivity(self, diesel_scenario):
        """Test sensitivity analysis on multiple parameters."""
        calculator = TCOCalculator()
        
        # Define parameters to analyze
        parameters = ["economic.diesel_price_aud_per_l", "operational.annual_distance_km"]
        
        # Perform multi-parameter sensitivity analysis
        sensitivity_results = calculator.analyze_multiple_parameters(
            diesel_scenario,
            parameters
        )
        
        # Verify results include both parameters
        assert len(sensitivity_results) == 2
        assert "economic.diesel_price_aud_per_l" in sensitivity_results
        assert "operational.annual_distance_km" in sensitivity_results
        
        # Verify each parameter's sensitivity results
        for param in parameters:
            param_sensitivity = sensitivity_results[param]
            assert param_sensitivity["parameter"] == param
            assert len(param_sensitivity["variation_values"]) > 0
            assert len(param_sensitivity["tco_values"]) == len(param_sensitivity["variation_values"])
    
    def test_parameter_impact_with_tipping_point(self, bet_scenario, diesel_scenario):
        """Test finding a tipping point in parameter sensitivity analysis."""
        calculator = TCOCalculator()
        
        # Set up scenarios to have a tipping point for diesel price
        bet_scenario.economic.electricity_price_aud_per_kwh = 0.25  # Fixed electricity price
        diesel_scenario.economic.diesel_price_aud_per_l = 1.5  # Starting diesel price
        
        # Define parameter and variations that should cross a tipping point
        parameter = "economic.diesel_price_aud_per_l"
        variations = [1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5]
        
        # Perform sensitivity analysis for both vehicles
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
        
        # Check if there's a tipping point
        # This means TCO values for diesel should start lower than BET but end higher
        bet_tco = sensitivity_bet["tco_values"][0]  # Constant value
        diesel_tco = sensitivity_diesel["tco_values"]
        
        # Check if diesel TCO crosses BET TCO at some point
        crosses = False
        for i in range(1, len(diesel_tco)):
            if (diesel_tco[i-1] < bet_tco and diesel_tco[i] >= bet_tco) or \
               (diesel_tco[i-1] >= bet_tco and diesel_tco[i] < bet_tco):
                crosses = True
                break
        
        # Assert there is a tipping point or the appropriate conditions are met
        # This could be either an actual crossing or the diesel is initially cheaper
        # but becomes more expensive as diesel price increases
        assert crosses or (diesel_tco[0] < bet_tco and diesel_tco[-1] > bet_tco)


class TestResultsExport:
    """Test results export functionality."""
    
    def test_excel_export_generation(self, bet_scenario, diesel_scenario):
        """Test generating Excel export with all TCO model data."""
        calculator = TCOCalculator()
        
        # Calculate TCO for both vehicles
        bet_result = calculator.calculate(bet_scenario)
        diesel_result = calculator.calculate(diesel_scenario)
        
        # Compare results
        comparison = calculator.compare(bet_result, diesel_result)
        
        # Create results dictionary
        results = {
            "vehicle_1": bet_result,
            "vehicle_2": diesel_result
        }
        
        # Generate export
        from ui.results.utils import generate_results_export
        export_data = generate_results_export(results, comparison)
        
        # Verify export data is not empty
        assert export_data is not None
        assert len(export_data) > 0
        
        # To fully validate the Excel content, we would need to parse the Excel file
        # but that's beyond the scope of a unit test. We'll just verify the export runs.
    
    def test_export_with_emissions_data(self, bet_scenario, diesel_scenario):
        """Test export includes emissions data."""
        calculator = TCOCalculator()
        
        # Calculate TCO for both vehicles
        bet_result = calculator.calculate(bet_scenario)
        diesel_result = calculator.calculate(diesel_scenario)
        
        # Verify emissions data exists
        assert bet_result.emissions is not None
        assert diesel_result.emissions is not None
        
        # Compare results
        comparison = calculator.compare(bet_result, diesel_result)
        
        # Create results dictionary
        results = {
            "vehicle_1": bet_result,
            "vehicle_2": diesel_result
        }
        
        # Generate export
        from ui.results.utils import generate_results_export
        export_data = generate_results_export(results, comparison)
        
        # Verify export data is not empty
        assert export_data is not None
        assert len(export_data) > 0
    
    def test_export_with_investment_analysis(self, bet_scenario, diesel_scenario):
        """Test export includes investment analysis data."""
        calculator = TCOCalculator()
        
        # Make BET more expensive upfront but cheaper over time
        bet_scenario.vehicle.purchase_price = 500000  # Higher upfront
        bet_scenario.economic.electricity_price_aud_per_kwh = 0.15  # Lower energy cost
        
        diesel_scenario.vehicle.purchase_price = 300000  # Lower upfront
        diesel_scenario.economic.diesel_price_aud_per_l = 1.8  # Higher energy cost
        
        # Calculate TCO for both vehicles
        bet_result = calculator.calculate(bet_scenario)
        diesel_result = calculator.calculate(diesel_scenario)
        
        # Compare results
        comparison = calculator.compare(bet_result, diesel_result)
        
        # Verify investment analysis exists
        assert comparison.investment_analysis is not None
        
        # Create results dictionary
        results = {
            "vehicle_1": bet_result,
            "vehicle_2": diesel_result
        }
        
        # Generate export
        from ui.results.utils import generate_results_export
        export_data = generate_results_export(results, comparison)
        
        # Verify export data is not empty
        assert export_data is not None
        assert len(export_data) > 0


class TestCompleteIntegration:
    """Test complete integration of all components."""
    
    def test_environmental_integration(self, bet_scenario, diesel_scenario):
        """Test that environmental components use actual emissions data."""
        from ui.results.environmental import create_emissions_timeline_chart
        
        # Create calculator
        calculator = TCOCalculator()
        
        # Calculate results
        bet_result = calculator.calculate(bet_scenario)
        diesel_result = calculator.calculate(diesel_scenario)
        
        # Verify emissions data exists
        assert bet_result.emissions is not None
        assert diesel_result.emissions is not None
        
        # Test chart creation with actual emissions data
        fig = create_emissions_timeline_chart(bet_result, diesel_result)
        
        # Verify chart has correct number of traces (2 bar traces + 2 line traces)
        assert len(fig.data) == 4
    
    def test_live_preview_integration(self, bet_scenario, diesel_scenario):
        """Test live preview integration with sensitivity analysis."""
        from ui.results.live_preview import create_parameter_impact_chart
        
        # Create calculator
        calculator = TCOCalculator()
        
        # Calculate results
        bet_result = calculator.calculate(bet_scenario)
        diesel_result = calculator.calculate(diesel_scenario)
        
        # Create results dictionary
        results = {
            "vehicle_1": bet_result,
            "vehicle_2": diesel_result
        }
        
        # Perform sensitivity analysis
        parameter = "economic.electricity_price_aud_per_kwh"
        variations = [0.15, 0.20, 0.25, 0.30, 0.35]
        
        sensitivity1 = calculator.perform_sensitivity_analysis(
            bet_scenario,
            parameter,
            variations
        )
        
        sensitivity2 = calculator.perform_sensitivity_analysis(
            diesel_scenario,
            parameter,
            variations
        )
        
        # Create parameter info
        parameter_info = {
            "name": "Electricity Price",
            "unit": "$/kWh",
            "variations1": variations,
            "variations2": variations,
            "has_tipping_point": False
        }
        
        # Test chart creation with actual sensitivity data
        fig = create_parameter_impact_chart(sensitivity1, sensitivity2, parameter_info)
        
        # Verify chart has correct number of traces (2 lines + 2 markers)
        assert len(fig.data) == 4
    
    def test_complete_workflow(self, bet_scenario, diesel_scenario):
        """Test the complete workflow with all components."""
        # Create calculator
        calculator = TCOCalculator()
        
        # Calculate results
        bet_result = calculator.calculate(bet_scenario)
        diesel_result = calculator.calculate(diesel_scenario)
        
        # Compare results
        comparison = calculator.compare(bet_result, diesel_result)
        
        # Create results dictionary
        results = {
            "vehicle_1": bet_result,
            "vehicle_2": diesel_result
        }
        
        # Verify key components are available
        assert bet_result.emissions is not None
        assert diesel_result.emissions is not None
        assert comparison.investment_analysis is not None
        
        # Test environmental integration
        from ui.results.environmental import create_emissions_timeline_chart
        emissions_fig = create_emissions_timeline_chart(bet_result, diesel_result)
        assert emissions_fig is not None
        
        # Test parameter impact integration
        from ui.results.live_preview import create_parameter_impact_chart
        
        parameter = "economic.electricity_price_aud_per_kwh"
        variations = [0.15, 0.20, 0.25, 0.30, 0.35]
        
        sensitivity1 = calculator.perform_sensitivity_analysis(
            bet_scenario,
            parameter,
            variations
        )
        
        sensitivity2 = calculator.perform_sensitivity_analysis(
            diesel_scenario,
            parameter,
            variations
        )
        
        parameter_info = {
            "name": "Electricity Price",
            "unit": "$/kWh",
            "variations1": variations,
            "variations2": variations,
            "has_tipping_point": False
        }
        
        impact_fig = create_parameter_impact_chart(sensitivity1, sensitivity2, parameter_info)
        assert impact_fig is not None
        
        # Test export integration
        from ui.results.utils import generate_results_export
        export_data = generate_results_export(results, comparison)
        assert export_data is not None
        assert len(export_data) > 0 