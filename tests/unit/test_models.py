"""
Unit tests for Pydantic model validation in the TCO Modeller.

These tests ensure that the Pydantic models correctly validate
input data and enforce constraints.
"""

import pytest
from pydantic import ValidationError

from tco_model.models import (
    VehicleType,
    VehicleCategory,
    FinancingMethod,
    ElectricityRateType,
    DieselPriceScenario,
    BETParameters,
    DieselParameters,
    EconomicParameters,
    OperationalParameters,
    FinancingParameters,
    BatteryParameters,
    ScenarioInput,
)


class TestVehicleParametersValidation:
    """Test validation of vehicle parameter models."""

    def test_bet_parameters_valid(self, bet_parameters):
        """Test that valid BET parameters are accepted."""
        # The fixture should be valid, so no exception should be raised
        assert bet_parameters.type == VehicleType.BATTERY_ELECTRIC
        assert bet_parameters.name == "Example BET"
        assert bet_parameters.purchase_price == 500000.0
        assert bet_parameters.battery.capacity == 400.0

    def test_diesel_parameters_valid(self, diesel_parameters):
        """Test that valid diesel parameters are accepted."""
        # The fixture should be valid, so no exception should be raised
        assert diesel_parameters.type == VehicleType.DIESEL
        assert diesel_parameters.name == "Example Diesel Truck"
        assert diesel_parameters.purchase_price == 400000.0
        assert diesel_parameters.engine.power == 350

    def test_bet_parameters_invalid_type(self, bet_parameters):
        """Test that BET parameters with wrong vehicle type are rejected."""
        # Ensure validation error when providing incorrect vehicle type
        with pytest.raises(ValidationError):
            BETParameters(
                type=VehicleType.DIESEL,  # Wrong type for BET
                category=bet_parameters.category,
                name=bet_parameters.name,
                purchase_price=bet_parameters.purchase_price,
                battery=bet_parameters.battery,
                consumption=bet_parameters.consumption,
                charging=bet_parameters.charging,
                maintenance=bet_parameters.maintenance,
                residual_value=bet_parameters.residual_value,
            )

    def test_bet_parameters_negative_price(self, bet_parameters):
        """Test that BET parameters with negative price are rejected."""
        # Ensure validation error when providing negative price
        with pytest.raises(ValidationError):
            BETParameters(
                type=bet_parameters.type,
                category=bet_parameters.category,
                name=bet_parameters.name,
                purchase_price=-100000.0,  # Negative price
                battery=bet_parameters.battery,
                consumption=bet_parameters.consumption,
                charging=bet_parameters.charging,
                maintenance=bet_parameters.maintenance,
                residual_value=bet_parameters.residual_value,
            )

    def test_battery_parameters_validation(self):
        """Test validation for battery parameters."""
        # Valid parameters should work
        battery = BatteryParameters(
            capacity=400.0,
            degradation_rate=0.02,
            replacement_threshold=0.8,
            price_per_kwh=800.0,
        )
        assert battery.capacity == 400.0
        
        # Capacity must be positive
        with pytest.raises(ValidationError):
            BatteryParameters(
                capacity=-100.0,  # Negative capacity
                degradation_rate=0.02,
                replacement_threshold=0.8,
                price_per_kwh=800.0,
            )
        
        # Degradation rate must be between 0 and 1
        with pytest.raises(ValidationError):
            BatteryParameters(
                capacity=400.0,
                degradation_rate=1.5,  # >1
                replacement_threshold=0.8,
                price_per_kwh=800.0,
            )

        # Replacement threshold must be between 0 and 1
        with pytest.raises(ValidationError):
            BatteryParameters(
                capacity=400.0,
                degradation_rate=0.02,
                replacement_threshold=1.2,  # >1
                price_per_kwh=800.0,
            )


class TestEconomicParametersValidation:
    """Test validation of economic parameter models."""

    def test_economic_parameters_valid(self, economic_parameters):
        """Test that valid economic parameters are accepted."""
        # The fixture should be valid, so no exception should be raised
        assert economic_parameters.discount_rate == 0.07
        assert economic_parameters.inflation_rate == 0.025
        assert economic_parameters.financing.method == FinancingMethod.LOAN

    def test_negative_rates(self):
        """Test that negative rates are rejected."""
        # Ensure validation error when providing negative discount rate
        with pytest.raises(ValidationError):
            EconomicParameters(
                discount_rate=-0.05,  # Negative discount rate
                inflation_rate=0.025,
                financing=FinancingParameters(
                    method=FinancingMethod.LOAN,
                    loan_term=5,
                    interest_rate=0.05,
                    deposit_percentage=0.2,
                ),
                energy_prices={
                    "electricity": {
                        "rate_type": ElectricityRateType.FLAT_RATE,
                        "price": 0.25,
                        "annual_change": 0.01,
                    },
                    "diesel": {
                        "price": 1.50,
                        "scenario": DieselPriceScenario.CONSTANT,
                        "annual_change": 0.02,
                    },
                },
                carbon_tax={
                    "enabled": False,
                    "rate": 25.0,
                    "annual_change": 0.05,
                },
            )

        # Ensure validation error when providing negative inflation rate
        with pytest.raises(ValidationError):
            EconomicParameters(
                discount_rate=0.07,
                inflation_rate=-0.03,  # Negative inflation rate
                financing=FinancingParameters(
                    method=FinancingMethod.LOAN,
                    loan_term=5,
                    interest_rate=0.05,
                    deposit_percentage=0.2,
                ),
                energy_prices={
                    "electricity": {
                        "rate_type": ElectricityRateType.FLAT_RATE,
                        "price": 0.25,
                        "annual_change": 0.01,
                    },
                    "diesel": {
                        "price": 1.50,
                        "scenario": DieselPriceScenario.CONSTANT,
                        "annual_change": 0.02,
                    },
                },
                carbon_tax={
                    "enabled": False,
                    "rate": 25.0,
                    "annual_change": 0.05,
                },
            )

    def test_financing_parameters_validation(self):
        """Test validation for financing parameters."""
        # Valid parameters should work
        financing = FinancingParameters(
            method=FinancingMethod.LOAN,
            loan_term=5,
            interest_rate=0.05,
            deposit_percentage=0.2,
        )
        assert financing.loan_term == 5
        
        # Loan term must be positive
        with pytest.raises(ValidationError):
            FinancingParameters(
                method=FinancingMethod.LOAN,
                loan_term=-2,  # Negative loan term
                interest_rate=0.05,
                deposit_percentage=0.2,
            )
        
        # Interest rate must be non-negative
        with pytest.raises(ValidationError):
            FinancingParameters(
                method=FinancingMethod.LOAN,
                loan_term=5,
                interest_rate=-0.05,  # Negative interest rate
                deposit_percentage=0.2,
            )
        
        # Deposit percentage must be between 0 and 1
        with pytest.raises(ValidationError):
            FinancingParameters(
                method=FinancingMethod.LOAN,
                loan_term=5,
                interest_rate=0.05,
                deposit_percentage=1.2,  # >1
            )


class TestOperationalParametersValidation:
    """Test validation of operational parameter models."""

    def test_operational_parameters_valid(self, operational_parameters):
        """Test that valid operational parameters are accepted."""
        # The fixture should be valid, so no exception should be raised
        assert operational_parameters.annual_distance == 100000
        assert operational_parameters.operating_days == 260
        assert operational_parameters.analysis_period == 15

    def test_negative_annual_distance(self):
        """Test that negative annual distance is rejected."""
        # Ensure validation error when providing negative annual distance
        with pytest.raises(ValidationError):
            OperationalParameters(
                annual_distance=-50000,  # Negative annual distance
                operating_days=260,
                analysis_period=15,
                payload=20.0,
                utilization=0.8,
                profile="Regional",
            )

    def test_invalid_operating_days(self):
        """Test that invalid operating days are rejected."""
        # Ensure validation error when providing operating days > 365
        with pytest.raises(ValidationError):
            OperationalParameters(
                annual_distance=100000,
                operating_days=366,  # More than 365 days
                analysis_period=15,
                payload=20.0,
                utilization=0.8,
                profile="Regional",
            )

    def test_utilization_range(self):
        """Test that utilization outside 0-1 range is rejected."""
        # Ensure validation error when providing utilization > 1
        with pytest.raises(ValidationError):
            OperationalParameters(
                annual_distance=100000,
                operating_days=260,
                analysis_period=15,
                payload=20.0,
                utilization=1.2,  # > 1
                profile="Regional",
            )


class TestScenarioValidation:
    """Test validation of complete scenario inputs."""

    def test_valid_bet_scenario(self, bet_scenario):
        """Test that a valid BET scenario is accepted."""
        # The fixture should be valid, so no exception should be raised
        assert bet_scenario.vehicle.type == VehicleType.BATTERY_ELECTRIC
        assert bet_scenario.operational.annual_distance == 100000
        assert bet_scenario.economic.discount_rate == 0.07

    def test_valid_diesel_scenario(self, diesel_scenario):
        """Test that a valid diesel scenario is accepted."""
        # The fixture should be valid, so no exception should be raised
        assert diesel_scenario.vehicle.type == VehicleType.DIESEL
        assert diesel_scenario.operational.annual_distance == 100000
        assert diesel_scenario.economic.discount_rate == 0.07

    def test_mix_vehicle_type_compatibility(self, bet_parameters, diesel_parameters, operational_parameters, economic_parameters, infrastructure_parameters):
        """Test that vehicle type compatibility is enforced in scenarios."""
        # Create a valid BET scenario
        bet_scenario = ScenarioInput(
            vehicle=bet_parameters,
            operational=operational_parameters,
            economic=economic_parameters,
            infrastructure=infrastructure_parameters,
        )
        assert bet_scenario.vehicle.type == VehicleType.BATTERY_ELECTRIC
        
        # Create a valid diesel scenario
        diesel_scenario = ScenarioInput(
            vehicle=diesel_parameters,
            operational=operational_parameters,
            economic=economic_parameters,
            infrastructure=infrastructure_parameters,
        )
        assert diesel_scenario.vehicle.type == VehicleType.DIESEL 