"""
Vehicle Module

This module handles vehicle-specific data loading and functionality for
different types of vehicles used in the TCO model.
"""

from typing import Dict, Any, List, Optional
from pathlib import Path

from tco_model.models import (
    VehicleType,
    VehicleBaseParameters,
    BETParameters,
    DieselParameters,
    BatteryParameters,
    EngineParameters,
    ChargingParameters,
    MaintenanceParameters,
    ResidualValueParameters,
    BETConsumptionParameters,
    DieselConsumptionParameters,
)
from utils.helpers import load_yaml_file


def get_vehicle_parameters(vehicle_type: VehicleType, config_name: Optional[str] = None) -> VehicleBaseParameters:
    """
    Get the appropriate vehicle parameters based on the vehicle type and configuration.
    
    Args:
        vehicle_type: The type of vehicle (BATTERY_ELECTRIC, DIESEL, etc.)
        config_name: Optional name of the specific configuration to load
            If None, the default configuration for the vehicle type is used
            
    Returns:
        VehicleBaseParameters: The vehicle parameters for the specified vehicle type
    """
    if vehicle_type == VehicleType.BATTERY_ELECTRIC:
        return get_bet_parameters(config_name)
    elif vehicle_type == VehicleType.DIESEL:
        return get_diesel_parameters(config_name)
    else:
        raise ValueError(f"Unsupported vehicle type: {vehicle_type}")


def get_bet_parameters(config_name: Optional[str] = None) -> BETParameters:
    """
    Get the parameters for a Battery Electric Truck (BET).
    
    Args:
        config_name: Optional name of the specific configuration to load
            If None, the default BET configuration is used
            
    Returns:
        BETParameters: The parameters for the specified BET configuration
    """
    # Use the default config if none specified
    if config_name is None:
        config_name = "default_bet"
    
    # Load the YAML configuration file
    config_path = Path("config/vehicles/bet") / f"{config_name}.yaml"
    yaml_data = load_yaml_file(config_path)
    
    # Transform YAML structure to match model expectations
    model_data = transform_bet_yaml_to_model(yaml_data)
    
    # Convert the transformed data to a BETParameters object
    return BETParameters(**model_data)


def get_diesel_parameters(config_name: Optional[str] = None) -> DieselParameters:
    """
    Get the parameters for a diesel truck.
    
    Args:
        config_name: Optional name of the specific configuration to load
            If None, the default diesel configuration is used
            
    Returns:
        DieselParameters: The parameters for the specified diesel configuration
    """
    # Use the default config if none specified
    if config_name is None:
        config_name = "default_ice"
    
    # Load the YAML configuration file
    config_path = Path("config/vehicles/diesel") / f"{config_name}.yaml"
    yaml_data = load_yaml_file(config_path)
    
    # Transform YAML structure to match model expectations
    model_data = transform_diesel_yaml_to_model(yaml_data)
    
    # Convert the transformed data to a DieselParameters object
    return DieselParameters(**model_data)


def transform_bet_yaml_to_model(yaml_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform BET YAML data to match the Pydantic model structure.
    
    Args:
        yaml_data: Raw YAML data
        
    Returns:
        Transformed data ready for Pydantic model
    """
    # Start with a new dictionary for the transformed data
    model_data = {}
    
    # Extract top-level fields
    vehicle_info = yaml_data.get('vehicle_info', {})
    purchase_info = yaml_data.get('purchase', {})
    performance = yaml_data.get('performance', {})
    
    # Map basic vehicle fields
    model_data['type'] = VehicleType.BATTERY_ELECTRIC
    model_data['name'] = vehicle_info.get('name', yaml_data.get('name', 'Electric Truck'))
    model_data['category'] = vehicle_info.get('category', yaml_data.get('category', 'articulated'))
    model_data['purchase_price'] = purchase_info.get('base_price_2025', yaml_data.get('purchase_price', 0))
    model_data['annual_price_decrease_real'] = purchase_info.get('annual_price_decrease_real', 0)
    
    # Map performance parameters
    model_data['max_payload_tonnes'] = performance.get('max_payload_tonnes', yaml_data.get('max_payload_tonnes', 25))
    model_data['range_km'] = performance.get('range_km', yaml_data.get('range_km', 300))
    
    # Transform battery parameters
    battery_yaml = yaml_data.get('battery', {})
    battery_model = {
        'capacity_kwh': battery_yaml.get('capacity_kwh', battery_yaml.get('capacity', 400)),
        'usable_capacity_percentage': battery_yaml.get('usable_capacity_percentage', 0.9),
        'degradation_rate_annual': battery_yaml.get('degradation_rate_annual', battery_yaml.get('degradation_rate', 0.02)),
        'replacement_threshold': battery_yaml.get('replacement_threshold', 0.7),
        'expected_lifecycle_years': battery_yaml.get('expected_lifecycle_years', None),
        'replacement_cost_factor': battery_yaml.get('replacement_cost_factor', 0.8)
    }
    model_data['battery'] = battery_model
    
    # Transform energy consumption parameters
    consumption_yaml = yaml_data.get('energy_consumption', yaml_data.get('consumption', {}))
    consumption_range = consumption_yaml.get('consumption_range', {})
    consumption_model = {
        'base_rate': consumption_yaml.get('base_rate_kwh_per_km', consumption_yaml.get('base_rate', 1.5)),
        'min_rate': consumption_range.get('min', 1.4),
        'max_rate': consumption_range.get('max', 1.6),
        'load_adjustment_factor': consumption_yaml.get('load_adjustment_factor', 0.15),
        'hot_weather_adjustment': consumption_yaml.get('temperature_adjustment', {}).get('hot_weather', 0.05),
        'cold_weather_adjustment': consumption_yaml.get('temperature_adjustment', {}).get('cold_weather', 0.15),
        'regenerative_braking_efficiency': consumption_yaml.get('regenerative_braking_efficiency', 0.65),
        'regen_contribution_urban': consumption_yaml.get('regen_contribution_urban', 0.2)
    }
    model_data['energy_consumption'] = consumption_model
    
    # Transform charging parameters
    charging_yaml = yaml_data.get('charging', {})
    charging_model = {
        'max_charging_power_kw': charging_yaml.get('max_charging_power_kw', charging_yaml.get('power', 350)),
        'charging_efficiency': charging_yaml.get('charging_efficiency', 0.9),
        'strategy': charging_yaml.get('charging_strategy', 'overnight_depot'),
        'electricity_rate_type': charging_yaml.get('electricity_rate_type', 'average_flat_rate')
    }
    model_data['charging'] = charging_model
    
    # Transform maintenance parameters
    maintenance_yaml = yaml_data.get('maintenance', {})
    maintenance_detailed = maintenance_yaml.get('detailed_costs', {})
    maintenance_model = {
        'cost_per_km': maintenance_yaml.get('cost_per_km', 0.08),
        'annual_fixed_min': maintenance_detailed.get('annual_fixed_min', 700),
        'annual_fixed_max': maintenance_detailed.get('annual_fixed_max', 1500),
        'annual_fixed_default': maintenance_detailed.get('annual_fixed_default', None),
        'scheduled_maintenance_interval_km': maintenance_yaml.get('scheduled_maintenance_interval_km', 40000),
        'major_service_interval_km': maintenance_yaml.get('major_service_interval_km', 120000)
    }
    model_data['maintenance'] = maintenance_model
    
    # Transform residual value parameters
    residual_yaml = yaml_data.get('residual_value', {})
    residual_model = {
        'year_5_range': (0.5, 0.6),  # Default values
        'year_10_range': (0.3, 0.4),
        'year_15_range': (0.1, 0.2)
    }
    if 'year_5_range' in residual_yaml:
        residual_model['year_5_range'] = tuple(residual_yaml['year_5_range'])
    if 'year_10_range' in residual_yaml:
        residual_model['year_10_range'] = tuple(residual_yaml['year_10_range'])
    if 'year_15_range' in residual_yaml:
        residual_model['year_15_range'] = tuple(residual_yaml['year_15_range'])
    model_data['residual_value'] = residual_model
    
    # Add infrastructure parameters if present
    if 'infrastructure' in yaml_data:
        infra_yaml = yaml_data['infrastructure']
        infra_model = {
            'charger_hardware_cost': infra_yaml.get('charger_hardware_cost', 15000),
            'installation_cost': infra_yaml.get('installation_cost', 10000),
            'maintenance_annual_percentage': infra_yaml.get('maintenance_annual_percentage', 0.015),
            'trucks_per_charger': infra_yaml.get('trucks_per_charger', 1.0),
            'grid_upgrade_cost': infra_yaml.get('grid_upgrade_cost', 0)
        }
        model_data['infrastructure'] = infra_model
    
    return model_data


def transform_diesel_yaml_to_model(yaml_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform Diesel YAML data to match the Pydantic model structure.
    
    Args:
        yaml_data: Raw YAML data
        
    Returns:
        Transformed data ready for Pydantic model
    """
    # Start with a new dictionary for the transformed data
    model_data = {}
    
    # Extract top-level fields
    vehicle_info = yaml_data.get('vehicle_info', {})
    purchase_info = yaml_data.get('purchase', {})
    performance = yaml_data.get('performance', {})
    
    # Map basic vehicle fields
    model_data['type'] = VehicleType.DIESEL
    model_data['name'] = vehicle_info.get('name', yaml_data.get('name', 'Diesel Truck'))
    model_data['category'] = vehicle_info.get('category', yaml_data.get('category', 'articulated'))
    model_data['purchase_price'] = purchase_info.get('base_price_2025', yaml_data.get('purchase_price', 0))
    model_data['annual_price_decrease_real'] = purchase_info.get('annual_price_decrease_real', 0)
    
    # Map performance parameters
    model_data['max_payload_tonnes'] = performance.get('max_payload_tonnes', yaml_data.get('max_payload_tonnes', 28))
    model_data['range_km'] = performance.get('range_km', yaml_data.get('range_km', 800))
    
    # Transform engine parameters
    engine_yaml = yaml_data.get('engine', {})
    engine_model = {
        'power_kw': engine_yaml.get('power_kw', engine_yaml.get('power', 400)),
        'displacement_litres': engine_yaml.get('displacement_litres', 13),
        'euro_emission_standard': engine_yaml.get('euro_emission_standard', engine_yaml.get('emissions_standard', 'Euro VI')),
        'adblue_required': engine_yaml.get('adblue_required', True),
        'adblue_consumption_percent_of_diesel': engine_yaml.get('adblue_consumption_percent_of_diesel', 0.05)
    }
    model_data['engine'] = engine_model
    
    # Transform fuel consumption parameters
    consumption_yaml = yaml_data.get('fuel_consumption', yaml_data.get('consumption', {}))
    consumption_range = consumption_yaml.get('consumption_range', {})
    consumption_model = {
        'base_rate': consumption_yaml.get('base_rate_l_per_100km', consumption_yaml.get('base_rate', 35)) / 100.0,  # Convert to l/km
        'min_rate': consumption_range.get('min', 30) / 100.0 if 'min' in consumption_range else 0.3,  # Convert to l/km
        'max_rate': consumption_range.get('max', 40) / 100.0 if 'max' in consumption_range else 0.4,  # Convert to l/km
        'load_adjustment_factor': consumption_yaml.get('load_adjustment_factor', 0.15),
        'hot_weather_adjustment': consumption_yaml.get('temperature_adjustment', {}).get('hot_weather', 0.03),
        'cold_weather_adjustment': consumption_yaml.get('temperature_adjustment', {}).get('cold_weather', 0.05)
    }
    model_data['fuel_consumption'] = consumption_model
    
    # Transform maintenance parameters
    maintenance_yaml = yaml_data.get('maintenance', {})
    maintenance_detailed = maintenance_yaml.get('detailed_costs', {})
    maintenance_model = {
        'cost_per_km': maintenance_yaml.get('cost_per_km', 0.12),
        'annual_fixed_min': maintenance_detailed.get('annual_fixed_min', 1000),
        'annual_fixed_max': maintenance_detailed.get('annual_fixed_max', 2000),
        'annual_fixed_default': maintenance_detailed.get('annual_fixed_default', None),
        'scheduled_maintenance_interval_km': maintenance_yaml.get('scheduled_maintenance_interval_km', 30000),
        'major_service_interval_km': maintenance_yaml.get('major_service_interval_km', 100000)
    }
    model_data['maintenance'] = maintenance_model
    
    # Transform residual value parameters
    residual_yaml = yaml_data.get('residual_value', {})
    residual_model = {
        'year_5_range': (0.4, 0.5),  # Default values
        'year_10_range': (0.2, 0.3),
        'year_15_range': (0.05, 0.1)
    }
    if 'year_5_range' in residual_yaml:
        residual_model['year_5_range'] = tuple(residual_yaml['year_5_range'])
    if 'year_10_range' in residual_yaml:
        residual_model['year_10_range'] = tuple(residual_yaml['year_10_range'])
    if 'year_15_range' in residual_yaml:
        residual_model['year_15_range'] = tuple(residual_yaml['year_15_range'])
    model_data['residual_value'] = residual_model
    
    return model_data


def list_available_vehicle_configurations() -> Dict[VehicleType, List[str]]:
    """
    List all available vehicle configurations in the config directory.
    
    Returns:
        Dict[VehicleType, List[str]]: A dictionary mapping vehicle types to
            lists of available configuration names
    """
    # Dictionary to store the results
    available_configs: Dict[VehicleType, List[str]] = {
        VehicleType.BATTERY_ELECTRIC: [],
        VehicleType.DIESEL: [],
    }
    
    # Check each vehicle type subdirectory
    for vehicle_type in available_configs.keys():
        type_dir = Path("config/vehicles") / vehicle_type.value
        if not type_dir.exists():
            continue
            
        # Get all YAML files in the vehicle type directory
        for config_file in type_dir.glob("*.yaml"):
            try:
                # Load the YAML file to check the vehicle type
                config_data = load_yaml_file(config_file)
                
                # Try to get vehicle type from both formats
                vehicle_info = config_data.get('vehicle_info', {})
                vehicle_type_str = vehicle_info.get('type', config_data.get('type', ''))
                
                if not vehicle_type_str:
                    continue
                
                # Convert string to VehicleType enum
                try:
                    file_vehicle_type = VehicleType(vehicle_type_str)
                    
                    # Add the configuration name to the appropriate list
                    config_name = config_file.stem
                    available_configs[file_vehicle_type].append(config_name)
                except ValueError:
                    # Skip if the vehicle type is not recognized
                    continue
            except Exception as e:
                print(f"Error loading config file {config_file}: {str(e)}")
                continue
    
    return available_configs 