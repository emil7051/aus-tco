"""
Unit tests for cost calculation functions in the TCO Modeller.

These tests verify that the cost calculation functions correctly
compute individual cost components.
"""

import pytest
import numpy as np

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
from tco_model.models import VehicleType, FinancingMethod


class TestAcquisitionCosts:
    """Tests for acquisition cost calculations."""

    def test_acquisition_costs_cash_purchase(self, bet_scenario):
        """Test acquisition costs for cash purchase."""
        # Set financing method to cash
        bet_scenario.financing.method = FinancingMethod.CASH
        
        # Year 0 should have the full purchase price
        cost_year_0 = calculate_acquisition_costs(bet_scenario, 0)
        assert cost_year_0 == bet_scenario.vehicle.purchase_price
        
        # Subsequent years should have zero acquisition costs
        cost_year_1 = calculate_acquisition_costs(bet_scenario, 1)
        assert cost_year_1 == 0
        
        cost_year_5 = calculate_acquisition_costs(bet_scenario, 5)
        assert cost_year_5 == 0

    def test_acquisition_costs_loan_purchase(self, bet_scenario):
        """Test acquisition costs for loan purchase."""
        # Set financing method to loan
        bet_scenario.financing.method = FinancingMethod.LOAN
        
        # Set loan parameters
        bet_scenario.financing.loan_term_years = 5
        bet_scenario.financing.loan_interest_rate = 0.05
        bet_scenario.financing.down_payment_percentage = 0.2
        
        # Year 0 should have the down payment
        cost_year_0 = calculate_acquisition_costs(bet_scenario, 0)
        expected_down_payment = bet_scenario.vehicle.purchase_price * bet_scenario.financing.down_payment_percentage
        assert cost_year_0 == expected_down_payment
        
        # Years 1-5 should have annual loan payments
        cost_year_1 = calculate_acquisition_costs(bet_scenario, 1)
        expected_annual_payment = bet_scenario.financing.calculate_annual_payment(bet_scenario.vehicle.purchase_price)
        assert cost_year_1 == pytest.approx(expected_annual_payment, rel=1e-3)
        
        # After loan term, should have zero acquisition costs
        cost_year_6 = calculate_acquisition_costs(bet_scenario, 6)
        assert cost_year_6 == 0


class TestEnergyCosts:
    """Tests for energy cost calculations."""

    def test_energy_costs_bet(self, bet_scenario):
        """Test energy costs for BET vehicles."""
        # Set energy consumption parameters
        bet_scenario.vehicle.energy_consumption.base_rate = 1.5  # kWh/km
        bet_scenario.operational.annual_distance_km = 100000  # km
        bet_scenario.vehicle.charging.charging_efficiency = 0.9  # 90% charging efficiency
        
        # Calculate expected energy costs
        expected_consumption_kwh = 1.5 * 100000  # Base consumption
        expected_grid_consumption_kwh = expected_consumption_kwh / 0.9  # Account for charging efficiency
        expected_cost = expected_grid_consumption_kwh * 0.25  # Using the simplified price in the function
        
        # Calculate actual costs
        cost = calculate_energy_costs(bet_scenario, 0)
        
        # Verify the result
        assert cost == pytest.approx(expected_cost, rel=1e-3)
    
    def test_energy_costs_diesel(self, diesel_scenario):
        """Test energy costs for diesel vehicles."""
        # Set fuel consumption parameters
        diesel_scenario.vehicle.fuel_consumption.base_rate = 0.35  # L/km
        diesel_scenario.operational.annual_distance_km = 100000  # km
        
        # Calculate expected energy costs
        expected_consumption_l = 0.35 * 100000  # Base consumption
        expected_cost = expected_consumption_l * 1.80  # Using the simplified price in the function
        
        # Calculate actual costs
        cost = calculate_energy_costs(diesel_scenario, 0)
        
        # Verify the result
        assert cost == pytest.approx(expected_cost, rel=1e-3)
    
    def test_energy_costs_with_load_adjustment(self, bet_scenario):
        """Test energy costs with load factor adjustment."""
        # Set energy consumption parameters with load adjustment
        bet_scenario.vehicle.energy_consumption.base_rate = 1.5  # kWh/km
        bet_scenario.vehicle.energy_consumption.load_adjustment_factor = 0.2  # Adjustment factor
        bet_scenario.operational.annual_distance_km = 100000  # km
        bet_scenario.operational.average_load_factor = 0.8  # 80% loaded
        bet_scenario.vehicle.charging.charging_efficiency = 0.9  # 90% charging efficiency
        
        # Calculate expected energy costs
        load_adjustment = (1.0 - 0.8) * 0.2  # 0.04 kWh/km reduction
        adjusted_consumption_kwh_per_km = 1.5 - load_adjustment  # 1.46 kWh/km
        expected_consumption_kwh = adjusted_consumption_kwh_per_km * 100000
        expected_grid_consumption_kwh = expected_consumption_kwh / 0.9
        expected_cost = expected_grid_consumption_kwh * 0.25
        
        # Calculate actual costs
        cost = calculate_energy_costs(bet_scenario, 0)
        
        # Verify the result
        assert cost == pytest.approx(expected_cost, rel=1e-3)

    def test_energy_costs_diesel_with_adblue(self, diesel_scenario):
        """Test diesel energy costs with AdBlue."""
        # Set fuel consumption parameters
        diesel_scenario.vehicle.fuel_consumption.base_rate = 0.35  # L/km
        diesel_scenario.operational.annual_distance_km = 100000  # km
        
        # Set up AdBlue
        diesel_scenario.vehicle.engine.adblue_required = True
        diesel_scenario.vehicle.engine.adblue_consumption_percent_of_diesel = 0.05  # 5% of diesel
        
        # Calculate expected energy costs
        expected_consumption_l = 0.35 * 100000  # Base diesel consumption
        expected_diesel_cost = expected_consumption_l * 1.80
        
        expected_adblue_consumption_l = expected_consumption_l * 0.05
        expected_adblue_cost = expected_adblue_consumption_l * 1.0  # AdBlue price in function
        
        expected_total_cost = expected_diesel_cost + expected_adblue_cost
        
        # Calculate actual costs
        cost = calculate_energy_costs(diesel_scenario, 0)
        
        # Verify the result
        assert cost == pytest.approx(expected_total_cost, rel=1e-3)


class TestMaintenanceCosts:
    """Tests for maintenance cost calculations."""

    def test_maintenance_costs_basic(self, bet_scenario):
        """Test basic maintenance cost calculation."""
        # Set maintenance parameters
        bet_scenario.vehicle.maintenance.cost_per_km = 0.15  # AUD/km
        bet_scenario.vehicle.maintenance.annual_fixed_min = 2000  # AUD
        bet_scenario.vehicle.maintenance.annual_fixed_max = 3000  # AUD
        bet_scenario.vehicle.maintenance.annual_fixed_default = 2500  # AUD
        bet_scenario.operational.annual_distance_km = 100000  # km
        
        # Calculate expected costs
        expected_variable_cost = 0.15 * 100000  # 15,000 AUD
        expected_fixed_cost = 2500  # From default value
        expected_total = expected_variable_cost + expected_fixed_cost  # 17,500 AUD
        
        # Calculate actual costs
        cost = calculate_maintenance_costs(bet_scenario, 0)
        
        # Verify the result
        assert cost == pytest.approx(expected_total, rel=1e-3)

    def test_maintenance_costs_with_inflation(self, bet_scenario):
        """Test maintenance costs with inflation in later years."""
        # Set maintenance parameters
        bet_scenario.vehicle.maintenance.cost_per_km = 0.15  # AUD/km
        bet_scenario.vehicle.maintenance.annual_fixed_min = 2000  # AUD
        bet_scenario.vehicle.maintenance.annual_fixed_max = 3000  # AUD
        bet_scenario.vehicle.maintenance.annual_fixed_default = 2500  # AUD
        bet_scenario.operational.annual_distance_km = 100000  # km
        bet_scenario.economic.inflation_rate = 0.025  # 2.5%
        
        # Year 5 calculation
        year = 5
        
        # Calculate expected costs
        expected_variable_cost = 0.15 * 100000  # 15,000 AUD
        expected_fixed_cost = 2500 * ((1 + 0.025) ** year)  # With inflation
        
        # For BETs, there's a brake maintenance reduction
        brake_maintenance_reduction = 0.02 * 100000  # 2,000 AUD
        
        expected_total = expected_variable_cost + expected_fixed_cost - brake_maintenance_reduction
        
        # Calculate actual costs
        cost = calculate_maintenance_costs(bet_scenario, year)
        
        # Verify the result
        assert cost == pytest.approx(expected_total, rel=1e-3)
    
    def test_maintenance_costs_diesel_with_emissions(self, diesel_scenario):
        """Test diesel maintenance costs with emissions systems."""
        # Set maintenance parameters
        diesel_scenario.vehicle.maintenance.cost_per_km = 0.20  # AUD/km
        diesel_scenario.vehicle.maintenance.annual_fixed_min = 3000  # AUD
        diesel_scenario.vehicle.maintenance.annual_fixed_max = 4000  # AUD
        diesel_scenario.vehicle.maintenance.annual_fixed_default = 3500  # AUD
        diesel_scenario.operational.annual_distance_km = 100000  # km
        diesel_scenario.vehicle.engine.euro_emission_standard = "Euro VI"
        
        # Calculate expected costs
        expected_variable_cost = 0.20 * 100000  # 20,000 AUD
        expected_fixed_cost = 3500  # From default value
        
        # Additional costs for Euro VI emission systems
        euro_vi_additional_cost = 0.02 * 100000  # 2,000 AUD
        
        expected_total = expected_variable_cost + expected_fixed_cost + euro_vi_additional_cost
        
        # Calculate actual costs
        cost = calculate_maintenance_costs(diesel_scenario, 0)
        
        # Verify the result
        assert cost == pytest.approx(expected_total, rel=1e-3)


class TestInfrastructureCosts:
    """Tests for infrastructure cost calculations."""

    def test_bet_infrastructure_costs_year_0(self, bet_scenario):
        """Test that BET infrastructure costs in year 0 include initial setup costs."""
        # Set infrastructure parameters
        bet_scenario.infrastructure.charger_hardware_cost = 50000  # AUD
        bet_scenario.infrastructure.installation_cost = 25000  # AUD
        bet_scenario.infrastructure.grid_upgrade_cost = 15000  # AUD
        bet_scenario.infrastructure.trucks_per_charger = 2  # Share between 2 trucks
        
        # Calculate expected cost
        expected_cost = (50000 + 25000 + 15000) / 2  # 45,000 AUD per truck
        
        # Calculate actual cost
        cost = calculate_infrastructure_costs(bet_scenario, 0)
        
        # Verify the result
        assert cost == expected_cost

    def test_bet_infrastructure_costs_subsequent_years(self, bet_scenario):
        """Test that BET infrastructure costs in subsequent years include only maintenance costs."""
        # Set infrastructure parameters
        bet_scenario.infrastructure.charger_hardware_cost = 50000  # AUD
        bet_scenario.infrastructure.installation_cost = 25000  # AUD
        bet_scenario.infrastructure.grid_upgrade_cost = 15000  # AUD
        bet_scenario.infrastructure.maintenance_annual_percentage = 0.02  # 2% of capital cost
        bet_scenario.infrastructure.trucks_per_charger = 2  # Share between 2 trucks
        
        # Calculate expected maintenance cost
        total_capital = 50000 + 25000 + 15000  # 90,000 AUD
        expected_maintenance = total_capital * 0.02 / 2  # 900 AUD per truck
        
        # Calculate actual cost
        cost_year_1 = calculate_infrastructure_costs(bet_scenario, 1)
        
        # Verify the result
        assert cost_year_1 == expected_maintenance
        
        # Verify the same for year 5
        cost_year_5 = calculate_infrastructure_costs(bet_scenario, 5)
        assert cost_year_5 == expected_maintenance

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

    def test_bet_no_replacement_needed(self, bet_scenario, monkeypatch):
        """Test BET battery replacement costs when no replacement is needed."""
        # Patch the needs_replacement function to return False
        def mock_needs_replacement(*args, **kwargs):
            return False
        
        monkeypatch.setattr(bet_scenario.vehicle.battery, "needs_replacement", mock_needs_replacement)
        
        # Calculate battery replacement costs
        costs = calculate_battery_replacement_costs(bet_scenario, 5)
        
        # Should be zero when no replacement is needed
        assert costs == 0

    def test_bet_replacement_needed(self, bet_scenario, monkeypatch):
        """Test BET battery replacement costs when replacement is needed."""
        # Patch the needs_replacement function to return True
        def mock_needs_replacement(*args, **kwargs):
            return True
        
        monkeypatch.setattr(bet_scenario.vehicle.battery, "needs_replacement", mock_needs_replacement)
        
        # Set battery parameters
        bet_scenario.vehicle.battery.capacity_kwh = 400  # kWh
        bet_scenario.vehicle.battery.replacement_cost_factor = 0.8  # 80% of new battery cost
        
        # Year for calculation (affects battery price)
        year = 5
        
        # Calculate expected costs
        base_battery_price_per_kwh = 800  # AUD/kWh from function
        yearly_price_reduction = 0.05  # 5% per year from function
        expected_battery_price_per_kwh = base_battery_price_per_kwh * ((1 - yearly_price_reduction) ** year)
        expected_cost = 400 * expected_battery_price_per_kwh * 0.8
        
        # Calculate actual costs
        costs = calculate_battery_replacement_costs(bet_scenario, year)
        
        # Verify the result
        assert costs == pytest.approx(expected_cost, rel=1e-3)


class TestInsuranceRegistrationCosts:
    """Tests for insurance and registration cost calculations."""

    def test_insurance_registration_costs_bet_year_0(self, bet_scenario):
        """Test insurance and registration costs for BET in year 0."""
        # Set vehicle parameters
        bet_scenario.vehicle.purchase_price = 500000  # AUD
        bet_scenario.operational.annual_distance_km = 100000  # km
        
        # Calculate expected costs
        # Insurance: 4% of current value
        expected_insurance = 500000 * 0.04  # 20,000 AUD
        
        # Registration: Base with 20% discount for BET
        expected_registration = 1000 * 0.8  # 800 AUD
        
        expected_total = expected_insurance + expected_registration
        
        # Calculate actual costs
        costs = calculate_insurance_registration_costs(bet_scenario, 0)
        
        # Verify the result
        assert costs == pytest.approx(expected_total, rel=1e-3)

    def test_insurance_registration_costs_diesel_year_0(self, diesel_scenario):
        """Test insurance and registration costs for diesel in year 0."""
        # Set vehicle parameters
        diesel_scenario.vehicle.purchase_price = 400000  # AUD
        diesel_scenario.operational.annual_distance_km = 100000  # km
        
        # Calculate expected costs
        # Insurance: 4% of current value
        expected_insurance = 400000 * 0.04  # 16,000 AUD
        
        # Registration: Base + road user charges
        road_user_charge_per_km = 0.02  # From function
        road_user_charges = road_user_charge_per_km * 100000  # 2,000 AUD
        expected_registration = 1000 + road_user_charges  # 3,000 AUD
        
        expected_total = expected_insurance + expected_registration
        
        # Calculate actual costs
        costs = calculate_insurance_registration_costs(diesel_scenario, 0)
        
        # Verify the result
        assert costs == pytest.approx(expected_total, rel=1e-3)

    def test_insurance_registration_costs_with_depreciation(self, bet_scenario):
        """Test insurance costs with vehicle depreciation in later years."""
        # Set vehicle parameters
        bet_scenario.vehicle.purchase_price = 500000  # AUD
        bet_scenario.operational.annual_distance_km = 100000  # km
        bet_scenario.economic.inflation_rate = 0.025  # 2.5%
        
        # Year for calculation
        year = 3
        
        # Calculate expected costs
        # Insurance: 4% of depreciated value
        annual_depreciation = 0.15  # 15% per year from function
        expected_vehicle_value = 500000 * ((1 - annual_depreciation) ** year)
        expected_insurance = expected_vehicle_value * 0.04
        
        # Registration: Base with 20% discount for BET, plus inflation
        expected_registration = 1000 * 0.8 * ((1 + 0.025) ** year)
        
        expected_total = expected_insurance + expected_registration
        
        # Calculate actual costs
        costs = calculate_insurance_registration_costs(bet_scenario, year)
        
        # Verify the result
        assert costs == pytest.approx(expected_total, rel=1e-3)


class TestTaxesLevies:
    """Tests for taxes and levies calculations."""

    def test_carbon_tax_diesel(self, diesel_scenario):
        """Test carbon tax calculation for diesel vehicles."""
        # Set vehicle and economic parameters
        diesel_scenario.vehicle.fuel_consumption.base_rate = 0.35  # L/km
        diesel_scenario.operational.annual_distance_km = 100000  # km
        diesel_scenario.economic.carbon_tax_rate_aud_per_tonne = 30.0  # AUD/tonne
        diesel_scenario.economic.carbon_tax_annual_increase_rate = 0.05  # 5% per year
        
        # Set up engine
        diesel_scenario.vehicle.engine.co2_per_liter = 2.68  # kg CO2/L
        
        # Year for calculation
        year = 2
        
        # Calculate expected costs
        # Carbon tax
        total_consumption_l = 0.35 * 100000  # 35,000 L
        total_emissions_tonnes = (total_consumption_l * 2.68) / 1000  # 93.8 tonnes
        carbon_tax_rate = 30.0 * ((1 + 0.05) ** year)  # Increased by 5% per year
        expected_carbon_tax = total_emissions_tonnes * carbon_tax_rate
        
        # No road user charges for diesel (handled in registration)
        expected_total = expected_carbon_tax
        
        # Calculate actual costs
        costs = calculate_taxes_levies(diesel_scenario, year)
        
        # Verify the result
        assert costs == pytest.approx(expected_total, rel=1e-3)

    def test_road_user_charges_bet(self, bet_scenario):
        """Test road user charges for BET vehicles."""
        # Set vehicle parameters
        bet_scenario.operational.annual_distance_km = 100000  # km
        
        # Calculate expected costs
        # Road user charge for BET
        road_user_charge_rate = 0.025  # AUD/km from function
        expected_road_user_charges = road_user_charge_rate * 100000  # 2,500 AUD
        
        # No carbon tax for BET in this simplified model
        expected_total = expected_road_user_charges
        
        # Calculate actual costs
        costs = calculate_taxes_levies(bet_scenario, 0)
        
        # Verify the result
        assert costs == pytest.approx(expected_total, rel=1e-3)

    def test_no_carbon_tax(self, diesel_scenario):
        """Test taxes when carbon tax is zero."""
        # Set carbon tax to zero
        diesel_scenario.economic.carbon_tax_rate_aud_per_tonne = 0.0
        
        # For diesel, should have zero taxes in this case
        costs = calculate_taxes_levies(diesel_scenario, 0)
        
        # Verify the result
        assert costs == 0


class TestResidualValue:
    """Tests for residual value calculations."""

    def test_residual_value_final_year_only(self, bet_scenario):
        """Test that residual value is calculated in the final year only."""
        # Set parameters
        bet_scenario.operational.analysis_period = 10
        bet_scenario.vehicle.purchase_price = 500000  # AUD
        
        # Define the final year of the analysis
        final_year = bet_scenario.operational.analysis_period - 1
        
        # In the final year, residual value should be calculated
        final_year_value = calculate_residual_value(bet_scenario, final_year)
        
        # For earlier years, residual value should be zero
        early_year_value = calculate_residual_value(bet_scenario, 5)
        assert early_year_value == 0
        
        # Final year value should be negative (income)
        assert final_year_value < 0

    def test_residual_value_with_model(self, bet_scenario, monkeypatch):
        """Test residual value calculation using the residual value model."""
        # Set parameters
        bet_scenario.operational.analysis_period = 10
        bet_scenario.vehicle.purchase_price = 500000  # AUD
        
        # Mock the calculate_residual_value method
        def mock_calculate_residual_value(**kwargs):
            return 150000  # 30% of initial value
        
        monkeypatch.setattr(bet_scenario.vehicle.residual_value, "calculate_residual_value", mock_calculate_residual_value)
        
        # Calculate residual value in final year
        final_year = bet_scenario.operational.analysis_period - 1
        residual_value = calculate_residual_value(bet_scenario, final_year)
        
        # Should be negative of the mocked value
        assert residual_value == -150000

    def test_residual_value_fallback_calculation(self, bet_scenario, monkeypatch):
        """Test residual value calculation using the fallback method."""
        # Set parameters
        bet_scenario.operational.analysis_period = 10
        bet_scenario.vehicle.purchase_price = 500000  # AUD
        
        # Remove the residual value model
        monkeypatch.delattr(bet_scenario.vehicle, "residual_value", raising=False)
        
        # Calculate residual value in final year
        final_year = bet_scenario.operational.analysis_period - 1
        residual_value = calculate_residual_value(bet_scenario, final_year)
        
        # Verify the result is negative (income)
        assert residual_value < 0
        
        # Verify it's calculated using the fallback method for BETs
        # For BETs: max(0.1, 0.5 - (0.03 * analysis_period))
        expected_percentage = max(0.1, 0.5 - (0.03 * 10))  # 0.2
        expected_value = -(500000 * expected_percentage)
        assert residual_value == pytest.approx(expected_value, rel=1e-3)

    def test_residual_value_diesel_fallback(self, diesel_scenario, monkeypatch):
        """Test residual value calculation for diesel using the fallback method."""
        # Set parameters
        diesel_scenario.operational.analysis_period = 10
        diesel_scenario.vehicle.purchase_price = 400000  # AUD
        
        # Remove the residual value model
        monkeypatch.delattr(diesel_scenario.vehicle, "residual_value", raising=False)
        
        # Calculate residual value in final year
        final_year = diesel_scenario.operational.analysis_period - 1
        residual_value = calculate_residual_value(diesel_scenario, final_year)
        
        # Verify the result is negative (income)
        assert residual_value < 0
        
        # Verify it's calculated using the fallback method for diesel
        # For diesel: max(0.05, 0.4 - (0.035 * analysis_period))
        expected_percentage = max(0.05, 0.4 - (0.035 * 10))  # 0.05
        expected_value = -(400000 * expected_percentage)
        assert residual_value == pytest.approx(expected_value, rel=1e-3)


class TestEdgeCases:
    """Tests for edge cases in cost calculations."""

    def test_zero_values_scenario(self, edge_case_zero_values_scenario):
        """Test cost calculations with zero values."""
        # Verify infrastructure costs with zero values
        infra_cost = calculate_infrastructure_costs(edge_case_zero_values_scenario, 0)
        # Even with zero vehicle price, infrastructure costs should still be calculated
        assert infra_cost > 0
        
        # Verify residual value with zero vehicle price
        residual_value = calculate_residual_value(edge_case_zero_values_scenario, 
                                               edge_case_zero_values_scenario.operational.analysis_period - 1)
        # For a zero-price vehicle, residual value should be zero
        assert residual_value == 0
        
        # Verify energy costs with zero distance
        energy_cost = calculate_energy_costs(edge_case_zero_values_scenario, 0)
        assert energy_cost == 0
        
        # Verify maintenance costs with zero distance
        maintenance_cost = calculate_maintenance_costs(edge_case_zero_values_scenario, 0)
        # Should still have fixed costs
        assert maintenance_cost > 0

    def test_high_usage_scenario(self, edge_case_high_usage_scenario):
        """Test cost calculations with high usage values."""
        # Calculate various costs
        energy_cost = calculate_energy_costs(edge_case_high_usage_scenario, 0)
        maintenance_cost = calculate_maintenance_costs(edge_case_high_usage_scenario, 0)
        taxes_cost = calculate_taxes_levies(edge_case_high_usage_scenario, 0)
        
        # High usage should result in proportionally high energy costs
        assert energy_cost > 0
        
        # High usage should result in proportionally high maintenance costs
        assert maintenance_cost > 0
        
        # High usage should result in proportionally high road user charges
        assert taxes_cost > 0 