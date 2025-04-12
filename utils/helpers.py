"""
Utility functions for the Australian Heavy Vehicle TCO Modeller.

This module provides helper functions for loading configuration files,
formatting data, and other utility operations used throughout the application.
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional, Type, TypeVar, Union

from pydantic import BaseModel
import streamlit as st

from tco_model.models import (
    BETParameters, DieselParameters, EconomicParameters, OperationalParameters,
    ScenarioInput, AppSettings, VehicleType, FinancingParameters,
    BatteryParameters, EngineParameters, ChargingParameters, ElectricityRateType,
    BETConsumptionParameters, DieselConsumptionParameters, MaintenanceParameters,
    InfrastructureParameters, ResidualValueParameters
)

# Type variable for generic functions
T = TypeVar('T', bound=BaseModel)

# Load application settings
settings = AppSettings()


def load_yaml_file(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Load and parse a YAML file.
    
    Args:
        file_path: Path to the YAML file
        
    Returns:
        Dict containing the parsed YAML data
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        yaml.YAMLError: If the file contains invalid YAML
    """
    try:
        with open(file_path, 'r') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file not found: {file_path}")
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"Error parsing YAML file {file_path}: {str(e)}")


def load_config_as_model(file_path: Union[str, Path], model_class: Type[T]) -> T:
    """
    Load a YAML configuration file and parse it into a Pydantic model.
    
    Args:
        file_path: Path to the YAML file
        model_class: Pydantic model class to parse the data into
        
    Returns:
        Instance of the specified model class
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        yaml.YAMLError: If the file contains invalid YAML
        ValidationError: If the data doesn't match the model schema
    """
    data = load_yaml_file(file_path)
    return model_class.parse_obj(data)


def load_economic_parameters(config_path: Optional[str] = None) -> EconomicParameters:
    """
    Load default economic parameters from configuration.
    
    Args:
        config_path: Optional custom path to the configuration file
        
    Returns:
        EconomicParameters model with default values
    """
    file_path = config_path or os.path.join(settings.defaults_config_path, "economic_parameters.yaml")
    data = load_yaml_file(file_path)
    
    # Extract relevant sections
    general = data.get('general', {})
    financing = data.get('financing', {})
    carbon_pricing = data.get('carbon_pricing', {})
    
    # Construct parameters
    params = {
        'discount_rate_real': general.get('discount_rate_real', 0.07),
        'inflation_rate': general.get('inflation_rate', 0.025),
        'analysis_period_years': general.get('analysis_period_years', 15),
        'electricity_price_type': ElectricityRateType.AVERAGE_FLAT_RATE,
        'diesel_price_scenario': data.get('energy_prices', {}).get('diesel', {}).get('scenario', 'medium_increase'),
        'carbon_tax_rate_aud_per_tonne': carbon_pricing.get('carbon_tax_rate_2025', 30.0),
        'carbon_tax_annual_increase_rate': carbon_pricing.get('annual_increase_rate', 0.05)
    }
    
    return EconomicParameters.parse_obj(params)


def load_operational_parameters(config_path: Optional[str] = None) -> OperationalParameters:
    """
    Load default operational parameters from configuration.
    
    Args:
        config_path: Optional custom path to the configuration file
        
    Returns:
        OperationalParameters model with default values
    """
    file_path = config_path or os.path.join(settings.defaults_config_path, "operational_parameters.yaml")
    data = load_yaml_file(file_path)
    
    # Get values from the long_haul profile as defaults
    profile = data.get('standard_profiles', {}).get('long_haul', {})
    
    params = {
        'annual_distance_km': profile.get('annual_distance_km', 100000),
        'operating_days_per_year': profile.get('operating_days_per_year', 280),
        'vehicle_life_years': 15,
        'requires_overnight_charging': profile.get('charging_strategy') == 'overnight_depot',
        'is_urban_operation': profile.get('vehicle_type') == 'rigid',
        'average_load_factor': 0.8
    }
    
    return OperationalParameters.parse_obj(params)


def load_financing_parameters(config_path: Optional[str] = None) -> FinancingParameters:
    """
    Load default financing parameters from configuration.
    
    Args:
        config_path: Optional custom path to the configuration file
        
    Returns:
        FinancingParameters model with default values
    """
    file_path = config_path or os.path.join(settings.defaults_config_path, "economic_parameters.yaml")
    data = load_yaml_file(file_path)
    
    # Extract financing section
    financing = data.get('financing', {})
    loan = financing.get('loan', {})
    
    params = {
        'method': financing.get('default_method', 'loan'),
        'loan_term_years': loan.get('term_years', 5),
        'loan_interest_rate': loan.get('interest_rate', 0.07),
        'down_payment_percentage': loan.get('down_payment_percentage', 0.2)
    }
    
    return FinancingParameters.parse_obj(params)


def load_vehicle_parameters(vehicle_type: VehicleType, config_path: Optional[str] = None) -> Union[BETParameters, DieselParameters]:
    """
    Load vehicle parameters based on vehicle type.
    
    Args:
        vehicle_type: Type of vehicle to load parameters for
        config_path: Optional custom path to the configuration file
        
    Returns:
        BETParameters or DieselParameters model with default values
    """
    if vehicle_type == VehicleType.BATTERY_ELECTRIC:
        file_path = config_path or os.path.join(settings.vehicles_config_path, "default_bet.yaml")
        return load_bet_parameters(file_path)
    else:
        file_path = config_path or os.path.join(settings.vehicles_config_path, "default_ice.yaml")
        return load_diesel_parameters(file_path)


def load_bet_parameters(config_path: str) -> BETParameters:
    """
    Load Battery Electric Truck parameters from configuration.
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        BETParameters model with values from the configuration
    """
    data = load_yaml_file(config_path)
    
    # Extract sections
    vehicle_info = data.get('vehicle_info', {})
    purchase = data.get('purchase', {})
    battery_data = data.get('battery', {})
    energy_data = data.get('energy_consumption', {})
    charging_data = data.get('charging', {})
    maintenance_data = data.get('maintenance', {})
    residual_data = data.get('residual_values', {}) if 'residual_values' in data else None
    infrastructure_data = data.get('infrastructure', {}) if 'infrastructure' in data else None
    performance = data.get('performance', {})
    
    # Load residual value data from operational parameters if not in vehicle config
    if not residual_data:
        op_params_path = os.path.join(settings.defaults_config_path, "operational_parameters.yaml")
        op_data = load_yaml_file(op_params_path)
        
        if vehicle_info.get('category') == 'rigid':
            residual_data = op_data.get('residual_values', {}).get('rigid_bet', {})
        else:
            residual_data = op_data.get('residual_values', {}).get('articulated_bet', {})
    
    # Create battery parameters
    battery_params = BatteryParameters(
        capacity_kwh=battery_data.get('capacity_kwh', 500),
        usable_capacity_percentage=battery_data.get('usable_capacity_percentage', 0.9),
        degradation_rate_annual=battery_data.get('degradation_rate_annual', 0.02),
        replacement_threshold=battery_data.get('replacement_threshold', 0.7),
        expected_lifecycle_years=battery_data.get('expected_lifecycle_years', 8),
        replacement_cost_factor=battery_data.get('replacement_cost_factor', 0.8)
    )
    
    # Create energy consumption parameters
    consumption_range = energy_data.get('consumption_range', {})
    energy_params = BETConsumptionParameters(
        base_rate=energy_data.get('base_rate_kwh_per_km', 1.45),
        min_rate=consumption_range.get('min', 1.4),
        max_rate=consumption_range.get('max', 1.5),
        load_adjustment_factor=energy_data.get('load_adjustment_factor', 0.15),
        hot_weather_adjustment=energy_data.get('temperature_adjustment', {}).get('hot_weather', 0.05),
        cold_weather_adjustment=energy_data.get('temperature_adjustment', {}).get('cold_weather', 0.15),
        regenerative_braking_efficiency=energy_data.get('regenerative_braking_efficiency', 0.65),
        regen_contribution_urban=energy_data.get('regen_contribution_urban', 0.2)
    )
    
    # Create charging parameters
    charging_params = ChargingParameters(
        max_charging_power_kw=charging_data.get('max_charging_power_kw', 350),
        charging_efficiency=charging_data.get('charging_efficiency', 0.9),
        strategy=charging_data.get('charging_strategy', 'overnight_depot'),
        electricity_rate_type=charging_data.get('strategies', {}).get(
            charging_data.get('charging_strategy', 'overnight_depot'), {}
        ).get('electricity_rate_type', 'off_peak_tou')
    )
    
    # Create maintenance parameters
    detailed_costs = maintenance_data.get('detailed_costs', {})
    maintenance_params = MaintenanceParameters(
        cost_per_km=maintenance_data.get('cost_per_km', 0.08),
        annual_fixed_min=detailed_costs.get('annual_fixed_min', 700),
        annual_fixed_max=detailed_costs.get('annual_fixed_max', 1500),
        annual_fixed_default=(detailed_costs.get('annual_fixed_min', 700) + detailed_costs.get('annual_fixed_max', 1500)) / 2,
        scheduled_maintenance_interval_km=maintenance_data.get('scheduled_maintenance_interval_km', 40000),
        major_service_interval_km=maintenance_data.get('major_service_interval_km', 120000)
    )
    
    # Create residual value parameters
    residual_params = ResidualValueParameters(
        year_5_range=residual_data.get('year_5', [0.4, 0.5]),
        year_10_range=residual_data.get('year_10', [0.2, 0.3]),
        year_15_range=residual_data.get('year_15', [0.1, 0.15])
    )
    
    # Create infrastructure parameters if available
    infrastructure_params