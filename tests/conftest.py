"""
Main pytest configuration file.

This file contains shared fixtures and configurations for all tests.
"""

import os
import sys
import pytest
from pathlib import Path
from typing import Dict, Any

# Add the project root to the Python path to ensure imports work correctly
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import required modules
from tco_model.models import (
    VehicleType,
    VehicleCategory,
    FinancingMethod,
    ElectricityRateType,
    DieselPriceScenario,
    ScenarioInput,
    BETParameters,
    DieselParameters,
    BatteryParameters,
    EconomicParameters,
    OperationalParameters,
    FinancingParameters,
    InfrastructureParameters,
    ChargingParameters,
    BETConsumptionParameters,
    DieselConsumptionParameters,
    EngineParameters,
    ResidualValueParameters,
    MaintenanceParameters,
)


@pytest.fixture
def economic_parameters() -> EconomicParameters:
    """
    Fixture providing default economic parameters for tests.
    """
    return EconomicParameters(
        discount_rate=0.07,  # 7%
        inflation_rate=0.025,  # 2.5%
        financing=FinancingParameters(
            method=FinancingMethod.LOAN,
            loan_term=5,
            interest_rate=0.05,  # 5%
            deposit_percentage=0.2,  # 20%
        ),
        energy_prices={
            "electricity": {
                "rate_type": ElectricityRateType.FLAT_RATE,
                "price": 0.25,  # AUD/kWh
                "annual_change": 0.01,  # 1%
            },
            "diesel": {
                "price": 1.50,  # AUD/L
                "scenario": DieselPriceScenario.CONSTANT,
                "annual_change": 0.02,  # 2%
            },
        },
        carbon_tax={
            "enabled": False,
            "rate": 25.0,  # AUD/tonne CO2
            "annual_change": 0.05,  # 5%
        },
    )


@pytest.fixture
def operational_parameters() -> OperationalParameters:
    """
    Fixture providing default operational parameters for tests.
    """
    return OperationalParameters(
        annual_distance=100000,  # km
        operating_days=260,  # days
        analysis_period=15,  # years
        payload=20.0,  # tonnes
        utilization=0.8,  # 80%
        profile="Regional",
    )


@pytest.fixture
def infrastructure_parameters() -> InfrastructureParameters:
    """
    Fixture providing default infrastructure parameters for tests.
    """
    return InfrastructureParameters(
        charger_cost=50000.0,
        installation_cost=20000.0,
        grid_upgrade_cost=30000.0,
        maintenance_cost=2000.0,
        lifetime=15,
    )


@pytest.fixture
def bet_parameters() -> BETParameters:
    """
    Fixture providing default BET parameters for tests.
    """
    return BETParameters(
        type=VehicleType.BATTERY_ELECTRIC,
        category=VehicleCategory.ARTICULATED,
        name="Example BET",
        purchase_price=500000.0,
        battery=BatteryParameters(
            capacity=400.0,  # kWh
            degradation_rate=0.02,  # 2% per year
            replacement_threshold=0.8,  # 80%
            price_per_kwh=800.0,  # AUD/kWh
        ),
        consumption=BETConsumptionParameters(
            base_rate=1.5,  # kWh/km
            adjustment_factors={
                "load": 0.2,
                "terrain": 0.1,
                "temperature": 0.05,
            },
        ),
        charging=ChargingParameters(
            power=150.0,  # kW
            efficiency=0.9,
            time_per_session=1.0,  # hours
        ),
        maintenance=MaintenanceParameters(
            base_rate=0.15,  # AUD/km
            annual_increase=0.05,  # 5% per year
        ),
        residual_value=ResidualValueParameters(
            initial_percentage=0.5,  # 50% of purchase price
            annual_depreciation=0.1,  # 10% per year
        ),
    )


@pytest.fixture
def diesel_parameters() -> DieselParameters:
    """
    Fixture providing default diesel parameters for tests.
    """
    return DieselParameters(
        type=VehicleType.DIESEL,
        category=VehicleCategory.ARTICULATED,
        name="Example Diesel Truck",
        purchase_price=400000.0,
        engine=EngineParameters(
            power=350,  # kW
            emissions_standard="Euro VI",
        ),
        consumption=DieselConsumptionParameters(
            base_rate=35.0,  # L/100km
            adjustment_factors={
                "load": 0.15,
                "terrain": 0.1,
                "temperature": 0.03,
            },
        ),
        emissions={
            "co2_per_liter": 2.7,  # kg/L
        },
        maintenance=MaintenanceParameters(
            base_rate=0.2,  # AUD/km
            annual_increase=0.05,  # 5% per year
        ),
        residual_value=ResidualValueParameters(
            initial_percentage=0.4,  # 40% of purchase price
            annual_depreciation=0.12,  # 12% per year
        ),
    )


@pytest.fixture
def bet_scenario(bet_parameters, operational_parameters, economic_parameters, infrastructure_parameters) -> ScenarioInput:
    """
    Fixture providing a complete BET scenario for tests.
    """
    return ScenarioInput(
        vehicle=bet_parameters,
        operational=operational_parameters,
        economic=economic_parameters,
        infrastructure=infrastructure_parameters,
    )


@pytest.fixture
def diesel_scenario(diesel_parameters, operational_parameters, economic_parameters, infrastructure_parameters) -> ScenarioInput:
    """
    Fixture providing a complete diesel scenario for tests.
    """
    return ScenarioInput(
        vehicle=diesel_parameters,
        operational=operational_parameters,
        economic=economic_parameters,
        infrastructure=infrastructure_parameters,
    )


@pytest.fixture
def edge_case_high_usage_scenario(bet_parameters, economic_parameters, infrastructure_parameters) -> ScenarioInput:
    """
    Fixture providing an edge case scenario with high annual distance.
    """
    # Create a modified operational parameters object with high usage
    high_usage_operational = OperationalParameters(
        annual_distance=500000,  # Very high annual distance
        operating_days=365,  # Maximum operating days
        analysis_period=20,  # Extended analysis period
        payload=30.0,  # High payload
        utilization=1.0,  # 100% utilization
        profile="Long-haul",
    )
    
    return ScenarioInput(
        vehicle=bet_parameters,
        operational=high_usage_operational,
        economic=economic_parameters,
        infrastructure=infrastructure_parameters,
    )


@pytest.fixture
def edge_case_low_usage_scenario(diesel_parameters, economic_parameters, infrastructure_parameters) -> ScenarioInput:
    """
    Fixture providing an edge case scenario with low annual distance.
    """
    # Create a modified operational parameters object with low usage
    low_usage_operational = OperationalParameters(
        annual_distance=10000,  # Very low annual distance
        operating_days=100,  # Limited operating days
        analysis_period=5,  # Short analysis period
        payload=5.0,  # Low payload
        utilization=0.3,  # 30% utilization
        profile="Urban",
    )
    
    return ScenarioInput(
        vehicle=diesel_parameters,
        operational=low_usage_operational,
        economic=economic_parameters,
        infrastructure=infrastructure_parameters,
    )


@pytest.fixture
def edge_case_zero_values_scenario(bet_parameters, operational_parameters, economic_parameters, infrastructure_parameters) -> ScenarioInput:
    """
    Fixture providing an edge case scenario with zero values.
    """
    # Create a modified operational parameters object with zero values
    zero_operational = OperationalParameters(
        annual_distance=0,  # Zero annual distance
        operating_days=0,  # Zero operating days
        analysis_period=1,  # Minimum analysis period
        payload=0.0,  # Zero payload
        utilization=0.0,  # 0% utilization
        profile="Urban",
    )
    
    # Create a copy of the economic parameters with zero discount rate
    zero_economic = EconomicParameters(
        discount_rate=0.0,  # 0% discount rate
        inflation_rate=0.0,  # 0% inflation rate
        financing=economic_parameters.financing,
        energy_prices=economic_parameters.energy_prices,
        carbon_tax=economic_parameters.carbon_tax,
    )
    
    # Create a copy of BET parameters with zero purchase price
    zero_bet_parameters = BETParameters(
        type=bet_parameters.type,
        category=bet_parameters.category,
        name="Zero-Value BET",
        purchase_price=0.0,  # Zero purchase price
        battery=bet_parameters.battery,
        consumption=bet_parameters.consumption,
        charging=bet_parameters.charging,
        maintenance=bet_parameters.maintenance,
        residual_value=bet_parameters.residual_value,
    )
    
    return ScenarioInput(
        vehicle=zero_bet_parameters,
        operational=zero_operational,
        economic=zero_economic,
        infrastructure=infrastructure_parameters,
    ) 