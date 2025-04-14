"""
Integration tests for the complete integration of the TCO model with the UI.

These tests verify that the TCO model's extensions are properly integrated
with the UI components, including:
1. Environmental Impact Analysis
2. Live Preview with Parameter Impact Analysis
3. Enhanced Report Export
"""

import pytest
import numpy as np
import pandas as pd
import io
from openpyxl import load_workbook

from tco_model.calculator import TCOCalculator
from tco_model.models import VehicleType, ScenarioInput, TCOOutput, ComparisonResult


class TestEnvironmentalIntegration:
    """Test environmental impact analysis integration."""

    def test_emissions_data_integration(self, bet_scenario, diesel_scenario):
        """Test that emissions data is correctly integrated with UI components."""
        # Create calculator
        calculator = TCOCalculator()
        
        # Calculate results
        bet_result = calculator.calculate(bet_scenario)
        diesel_result = calculator.calculate(diesel_scenario)
        
        # Verify emissions data exists
        assert bet_result.emissions is not None
        assert diesel_result.emissions is not None
        
        # Test emissions timeline chart
        from ui.results.environmental import create_emissions_timeline_chart
        fig = create_emissions_timeline_chart(bet_result, diesel_result)
        
        # Verify chart has data from both vehicles (2 bar traces + 2 line traces)
        assert len(fig.data) == 4
        assert len(fig.data[0].y) == len(bet_result.emissions.annual_co2_tonnes)
        assert len(fig.data[1].y) == len(diesel_result.emissions.annual_co2_tonnes)
    
    def test_energy_efficiency_chart(self, bet_scenario, diesel_scenario):
        """Test energy efficiency chart with real emissions data."""
        # Create calculator
        calculator = TCOCalculator()
        
        # Calculate results
        bet_result = calculator.calculate(bet_scenario)
        diesel_result = calculator.calculate(diesel_scenario)
        
        # Test energy efficiency chart
        from ui.results.environmental import create_energy_efficiency_chart
        fig = create_energy_efficiency_chart(bet_result, diesel_result)
        
        # Verify chart contains energy per km data
        assert len(fig.data) == 2
        assert fig.data[0].y[0] == bet_result.emissions.energy_per_km
        assert fig.data[1].y[0] == diesel_result.emissions.energy_per_km
    
    def test_sustainability_metrics_integration(self, bet_scenario, diesel_scenario):
        """Test sustainability metrics with real data."""
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
        
        # Test sustainability impact calculation
        from ui.results.environmental import calculate_sustainability_impact
        impact = calculate_sustainability_impact(bet_result, diesel_result)
        
        # Verify impact has the expected structure
        assert "air_quality" in impact
        assert "renewability" in impact
        assert "resource" in impact
        
        # Values should be reasonable
        assert isinstance(impact["air_quality"], int)
        assert isinstance(impact["renewability"], int)
        assert isinstance(impact["resource"], int)


class TestSensitivityAnalysisIntegration:
    """Test sensitivity analysis integration."""

    def test_parameter_impact_analysis(self, bet_scenario, diesel_scenario):
        """Test parameter impact analysis with real sensitivity data."""
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
        
        # Test parameter impact chart creation
        from ui.results.live_preview import create_parameter_impact_chart
        
        parameter_info = {
            "name": "Electricity Price",
            "unit": "$/kWh",
            "variations1": variations,
            "variations2": variations,
            "has_tipping_point": False
        }
        
        fig = create_parameter_impact_chart(sensitivity1, sensitivity2, parameter_info)
        
        # Verify chart has proper structure (2 lines + 2 markers)
        assert len(fig.data) == 4
        assert len(fig.data[0].x) == len(variations)
    
    def test_tipping_point_calculation(self, bet_scenario, diesel_scenario):
        """Test tipping point calculation in parameter impact analysis."""
        # Create calculator
        calculator = TCOCalculator()
        
        # Set up scenarios to have a tipping point for diesel price
        bet_scenario.economic.electricity_price_aud_per_kwh = 0.25  # Fixed electricity price
        diesel_scenario.economic.diesel_price_aud_per_l = 1.5  # Starting diesel price
        
        # Calculate results
        bet_result = calculator.calculate(bet_scenario)
        diesel_result = calculator.calculate(diesel_scenario)
        
        # Define parameter and variations that should cross a tipping point
        parameter = "economic.diesel_price_aud_per_l"
        variations = [1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5]
        
        # Perform sensitivity analysis
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
        
        # Test tipping point determination
        from ui.results.live_preview import determine_has_tipping_point
        has_tipping_point = determine_has_tipping_point(sensitivity_bet, sensitivity_diesel)
        
        # Changing diesel price should create a tipping point
        assert has_tipping_point is True
        
        # Test tipping point calculation
        from ui.results.live_preview import calculate_tipping_point
        tipping_point = calculate_tipping_point(sensitivity_bet, sensitivity_diesel)
        
        # Tipping point should be a float value within the variations range
        assert tipping_point is not None
        assert min(variations) <= tipping_point <= max(variations)


class TestExportFunctionality:
    """Test the enhanced export functionality."""

    def test_excel_export_with_all_data(self, bet_scenario, diesel_scenario):
        """Test that Excel export includes all TCO model data."""
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
        
        # Generate export
        from ui.results.utils import generate_results_export
        export_data = generate_results_export(results, comparison)
        
        # Verify export data is not empty
        assert export_data is not None
        assert len(export_data) > 0
        
        # Load the workbook to verify contents
        try:
            workbook = load_workbook(io.BytesIO(export_data))
            
            # Verify all required sheets exist
            required_sheets = ["Summary", "Annual Costs", "Cost Components", "Emissions", "Parameters"]
            for sheet_name in required_sheets:
                assert sheet_name in workbook.sheetnames
            
            # Verify emissions data in summary sheet
            summary_sheet = workbook["Summary"]
            found_co2 = False
            for row in summary_sheet.iter_rows(values_only=True):
                if row and isinstance(row[0], str) and "CO2" in row[0]:
                    found_co2 = True
                    break
            assert found_co2
            
            # Verify emissions sheet has data
            emissions_sheet = workbook["Emissions"]
            assert emissions_sheet.max_row > 1  # Header plus at least one data row
        except Exception as e:
            pytest.fail(f"Failed to validate Excel export: {str(e)}")


class TestFullIntegrationWorkflow:
    """Test complete end-to-end integration workflow."""

    def test_complete_integration_workflow(self, bet_scenario, diesel_scenario):
        """Test a complete workflow with all integrated components."""
        # Create calculator
        calculator = TCOCalculator()
        
        # Calculate results with real scenarios
        bet_result = calculator.calculate(bet_scenario)
        diesel_result = calculator.calculate(diesel_scenario)
        
        # Compare results
        comparison = calculator.compare(bet_result, diesel_result)
        
        # Create results dictionary
        results = {
            "vehicle_1": bet_result,
            "vehicle_2": diesel_result
        }
        
        # 1. Verify emissions data is available
        assert bet_result.emissions is not None
        assert diesel_result.emissions is not None
        
        # 2. Test environmental impact analysis
        from ui.results.environmental import create_emissions_timeline_chart
        emissions_fig = create_emissions_timeline_chart(bet_result, diesel_result)
        assert len(emissions_fig.data) == 4
        
        # 3. Test parameter impact analysis
        from ui.results.live_preview import create_parameter_impact_chart, determine_has_tipping_point
        
        parameter = "economic.electricity_price_aud_per_kwh"
        variations = [0.15, 0.20, 0.25, 0.30, 0.35]
        
        sensitivity_bet = calculator.perform_sensitivity_analysis(
            bet_scenario,
            parameter,
            variations
        )
        
        sensitivity_diesel = calculator.perform_sensitivity_analysis(
            diesel_scenario,
            parameter,
            variations
        )
        
        has_tipping_point = determine_has_tipping_point(sensitivity_bet, sensitivity_diesel)
        
        parameter_info = {
            "name": "Electricity Price",
            "unit": "$/kWh",
            "variations1": variations,
            "variations2": variations,
            "has_tipping_point": has_tipping_point
        }
        
        impact_fig = create_parameter_impact_chart(sensitivity_bet, sensitivity_diesel, parameter_info)
        assert len(impact_fig.data) >= 4  # Should have at least 4 traces
        
        # 4. Test results export
        from ui.results.utils import generate_results_export
        export_data = generate_results_export(results, comparison)
        assert export_data is not None
        assert len(export_data) > 0
        
        # 5. Test key metrics panel integration
        from ui.results.metrics import render_key_metrics_panel
        
        # This can't be fully tested in a unit test since it uses Streamlit,
        # but we can verify the function exists and doesn't raise an error when imported
        assert callable(render_key_metrics_panel) 