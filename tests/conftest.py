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
    ChargingStrategy,
)


@pytest.fixture
def economic_parameters() -> EconomicParameters:
    """
    Fixture providing default economic parameters for tests.
    """
    return EconomicParameters(
        discount_rate_real=0.07,  # 7%
        inflation_rate=0.025,  # 2.5%
        analysis_period_years=15,
        electricity_price_type=ElectricityRateType.AVERAGE_FLAT_RATE,
        diesel_price_scenario=DieselPriceScenario.MEDIUM_INCREASE,
        carbon_tax_rate_aud_per_tonne=30.0,
        carbon_tax_annual_increase_rate=0.05,
        financing=FinancingParameters(
            method=FinancingMethod.LOAN,
            loan_term_years=5,
            loan_interest_rate=0.05,  # 5%
            down_payment_percentage=0.2,  # 20%
        ),
    )


@pytest.fixture
def operational_parameters() -> OperationalParameters:
    """
    Fixture providing default operational parameters for tests.
    """
    return OperationalParameters(
        annual_distance_km=100000,  # km
        operating_days_per_year=260,  # days
        vehicle_life_years=15,  # years
        average_load_factor=0.8,  # 80%
        is_urban_operation=False,
        profile="Regional",
    )


@pytest.fixture
def infrastructure_parameters() -> InfrastructureParameters:
    """
    Fixture providing default infrastructure parameters for tests.
    """
    return InfrastructureParameters(
        charger_hardware_cost=50000.0,
        installation_cost=20000.0,
        grid_upgrade_cost=30000.0,
        maintenance_annual_percentage=0.015,
        trucks_per_charger=1.0,
    )


@pytest.fixture
def financing_parameters() -> FinancingParameters:
    """
    Fixture providing default financing parameters for tests.
    """
    return FinancingParameters(
        method=FinancingMethod.LOAN,
        loan_term_years=5,
        loan_interest_rate=0.07,
        down_payment_percentage=0.2,
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
        max_payload_tonnes=30.0,
        range_km=300.0,
        battery=BatteryParameters(
            capacity_kwh=400.0,  # kWh
            degradation_rate_annual=0.02,  # 2% per year
            replacement_threshold=0.8,  # 80%
            replacement_cost_factor=0.8,  # 80% of original cost
            usable_capacity_percentage=0.9,  # 90% of capacity is usable
        ),
        energy_consumption=BETConsumptionParameters(
            base_rate=1.5,  # kWh/km
            min_rate=1.0,   # Minimum consumption rate
            max_rate=2.0,   # Maximum consumption rate
            load_adjustment_factor=0.2,  # Changed from adjustment_factors
            hot_weather_adjustment=0.05,  # Added
            cold_weather_adjustment=0.05,  # Added
            regenerative_braking_efficiency=0.65,  # Added for BETConsumptionParameters
            regen_contribution_urban=0.2,  # Added for BETConsumptionParameters
        ),
        charging=ChargingParameters(
            max_charging_power_kw=150.0,  # kW
            charging_efficiency=0.9,
            strategy=ChargingStrategy.OVERNIGHT_DEPOT,
            electricity_rate_type=ElectricityRateType.AVERAGE_FLAT_RATE
        ),
        maintenance=MaintenanceParameters(
            cost_per_km=0.15,  # AUD/km
            annual_fixed_min=700,
            annual_fixed_max=1500,
            annual_fixed_default=1000,  # Added default value
            scheduled_maintenance_interval_km=40000,
            major_service_interval_km=120000
        ),
        residual_value=ResidualValueParameters(
            year_5_range=(0.45, 0.55),
            year_10_range=(0.25, 0.35),
            year_15_range=(0.10, 0.20),
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
        max_payload_tonnes=35.0,
        range_km=800.0,
        engine=EngineParameters(
            power_kw=350,  # kW
            displacement_litres=13,  # liters
            euro_emission_standard="Euro VI",
            adblue_required=True,
            adblue_consumption_percent_of_diesel=0.05,  # 5% of diesel consumption
        ),
        fuel_consumption=DieselConsumptionParameters(
            base_rate=35.0,  # L/100km
            min_rate=25.0,   # Minimum consumption rate
            max_rate=45.0,   # Maximum consumption rate
            load_adjustment_factor=0.15,  # Changed from adjustment_factors
            hot_weather_adjustment=0.03,  # Added
            cold_weather_adjustment=0.03,  # Added
        ),
        maintenance=MaintenanceParameters(
            cost_per_km=0.15,  # AUD/km
            annual_fixed_min=700,
            annual_fixed_max=1500,
            annual_fixed_default=1000,  # Added default
            scheduled_maintenance_interval_km=40000,
            major_service_interval_km=120000
        ),
        residual_value=ResidualValueParameters(
            year_5_range=(0.45, 0.55),
            year_10_range=(0.25, 0.35),
            year_15_range=(0.10, 0.20),
        ),
    )


@pytest.fixture
def bet_scenario(bet_parameters, operational_parameters, economic_parameters, infrastructure_parameters, financing_parameters) -> ScenarioInput:
    """
    Fixture providing a complete BET scenario for tests.
    """
    return ScenarioInput(
        scenario_name="BET Test Scenario",
        vehicle=bet_parameters,
        operational=operational_parameters,
        economic=economic_parameters,
        financing=financing_parameters,
        infrastructure=infrastructure_parameters,
    )


@pytest.fixture
def diesel_scenario(diesel_parameters, operational_parameters, economic_parameters, infrastructure_parameters, financing_parameters) -> ScenarioInput:
    """
    Fixture providing a complete diesel scenario for tests.
    """
    return ScenarioInput(
        scenario_name="Diesel Test Scenario",
        vehicle=diesel_parameters,
        operational=operational_parameters,
        economic=economic_parameters,
        financing=financing_parameters,
        infrastructure=infrastructure_parameters,
    )


@pytest.fixture
def edge_case_high_usage_scenario(bet_parameters, economic_parameters, infrastructure_parameters, financing_parameters) -> ScenarioInput:
    """
    Fixture providing an edge case scenario with high annual distance.
    """
    # Create a modified operational parameters object with high usage
    high_usage_operational = OperationalParameters(
        annual_distance_km=500000,  # Very high annual distance
        operating_days_per_year=365,  # Maximum operating days
        vehicle_life_years=20,  # Extended analysis period
        average_load_factor=1.0,  # 100% utilization
        is_urban_operation=False,
    )
    
    return ScenarioInput(
        scenario_name="High Usage Edge Case",
        vehicle=bet_parameters,
        operational=high_usage_operational,
        economic=economic_parameters,
        financing=financing_parameters,
        infrastructure=infrastructure_parameters,
    )


@pytest.fixture
def edge_case_low_usage_scenario(diesel_parameters, economic_parameters, infrastructure_parameters, financing_parameters) -> ScenarioInput:
    """
    Fixture providing an edge case scenario with low annual distance.
    """
    # Create a modified operational parameters object with low usage
    low_usage_operational = OperationalParameters(
        annual_distance_km=10000,  # Very low annual distance
        operating_days_per_year=100,  # Limited operating days
        vehicle_life_years=5,  # Short analysis period
        average_load_factor=0.3,  # 30% utilization
        is_urban_operation=True,
    )
    
    return ScenarioInput(
        scenario_name="Low Usage Edge Case",
        vehicle=diesel_parameters,
        operational=low_usage_operational,
        economic=economic_parameters,
        financing=financing_parameters,
        infrastructure=infrastructure_parameters,
    )


@pytest.fixture
def edge_case_zero_values_scenario(bet_parameters, operational_parameters, economic_parameters, infrastructure_parameters, financing_parameters) -> ScenarioInput:
    """
    Fixture providing an edge case scenario with zero values.
    """
    # Create a modified operational parameters object with zero values
    zero_operational = OperationalParameters(
        annual_distance_km=0.01,  # Almost zero annual distance (can't be exactly zero due to validation)
        operating_days_per_year=1,  # Minimum operating days
        vehicle_life_years=1,  # Minimum vehicle life
        average_load_factor=0.01,  # Minimum load factor
        is_urban_operation=False,
    )
    
    return ScenarioInput(
        scenario_name="Zero Values Edge Case",
        vehicle=bet_parameters,
        operational=zero_operational,
        economic=economic_parameters,
        financing=financing_parameters,
        infrastructure=infrastructure_parameters,
    )
