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

# New imports for UI testing
from utils.ui_terminology import UI_COMPONENT_LABELS
from utils.navigation_state import get_current_step, set_step, get_navigation_history
from ui.layout import LayoutMode
from dataclasses import dataclass
from typing import List, Optional

# Define the NavigationState class that was missing
@dataclass
class NavigationState:
    """Navigation state for testing purposes."""
    current_step: str
    completed_steps: List[str]
    breadcrumb_history: List[str]
    can_proceed: bool
    can_go_back: bool
    next_step: Optional[str]
    previous_step: Optional[str]

# New UI Fixtures for testing the refactored components

@pytest.fixture
def ui_theme_config():
    """
    Fixture providing theme configuration for UI tests.
    """
    return {
        "current_theme": "default",
        "high_contrast": False,
        "available_themes": ["default", "high_contrast", "dark"]
    }

@pytest.fixture
def navigation_state():
    """
    Fixture providing a navigation state for UI navigation tests.
    """
    return NavigationState(
        current_step="vehicle_parameters",
        completed_steps=["introduction", "vehicle_parameters"],
        breadcrumb_history=["Home", "Vehicle Parameters"],
        can_proceed=True,
        can_go_back=True,
        next_step="operational_parameters",
        previous_step="introduction"
    )

@pytest.fixture
def layout_config():
    """
    Fixture providing layout configuration for UI tests.
    """
    return {
        "mode": LayoutMode.STEP_BY_STEP,
        "sidebar_visible": True,
        "sidebar_collapsed": False,
        "results_preview_enabled": True
    }

@pytest.fixture
def component_test_ids():
    """
    Fixture providing test IDs for UI component tests.
    """
    return {
        "navigation": "nav-container",
        "sidebar": "sidebar-container",
        "main_content": "main-content",
        "vehicle_form": "vehicle-form",
        "operational_form": "operational-form",
        "economic_form": "economic-form",
        "results_container": "results-container",
        "theme_switcher": "theme-switcher"
    }

@pytest.fixture
def emissions_comparison_data(bet_scenario, diesel_scenario):
    """
    Fixture providing emissions comparison data for UI tests.
    """
    # Calculate TCO
    from tco_model.calculator import TCOCalculator
    calculator = TCOCalculator()
    
    bet_result = calculator.calculate(bet_scenario)
    diesel_result = calculator.calculate(diesel_scenario)
    
    return {
        "vehicle_1": bet_result.emissions,
        "vehicle_2": diesel_result.emissions,
        "vehicle_1_name": bet_result.vehicle_name,
        "vehicle_2_name": diesel_result.vehicle_name,
        "lifetime_distance": bet_result.lifetime_distance
    }

@pytest.fixture
def investment_analysis_data(bet_scenario, diesel_scenario):
    """
    Fixture providing investment analysis data for UI tests.
    """
    from tco_model.calculator import TCOCalculator
    calculator = TCOCalculator()
    
    # Modify scenarios to ensure investment analysis can be calculated
    bet_scenario.vehicle.purchase_price = 500000  # Higher upfront
    bet_scenario.economic.electricity_price_aud_per_kwh = 0.15  # Lower energy cost
    
    diesel_scenario.vehicle.purchase_price = 300000  # Lower upfront
    diesel_scenario.economic.diesel_price_aud_per_l = 1.8  # Higher energy cost
    
    # Calculate TCO
    bet_result = calculator.calculate(bet_scenario)
    diesel_result = calculator.calculate(diesel_scenario)
    
    # Compare results
    comparison = calculator.compare(bet_result, diesel_result)
    
    return {
        "investment_analysis": comparison.investment_analysis,
        "vehicle_1_name": bet_result.vehicle_name,
        "vehicle_2_name": diesel_result.vehicle_name,
        "vehicle_1_initial_cost": bet_scenario.vehicle.purchase_price,
        "vehicle_2_initial_cost": diesel_scenario.vehicle.purchase_price
    }

@pytest.fixture
def mock_browser_viewport():
    """
    Fixture providing mock viewport sizes for responsive testing.
    """
    return [
        {"width": 375, "height": 667, "name": "mobile"},
        {"width": 768, "height": 1024, "name": "tablet"},
        {"width": 1366, "height": 768, "name": "laptop"},
        {"width": 1920, "height": 1080, "name": "desktop"}
    ]

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
