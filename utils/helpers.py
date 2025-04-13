"""
Utility functions for the Australian Heavy Vehicle TCO Modeller.

This module provides helper functions for loading configuration files,
formatting data, and other utility operations used throughout the application.
"""

import os
import glob
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, TypeVar, Union

from pydantic import BaseModel, ValidationError
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
    Load a YAML configuration file and parse it into a Pydantic model,
    using the field mappings from terminology.py.
    
    Args:
        file_path: Path to the YAML file
        model_class: Pydantic model class to parse the data into
        
    Returns:
        Instance of the specified model class
        
    Example:
        >>> vehicle_params = load_config_as_model("config/vehicles/bet_truck.yaml", BETParameters)
    """
    from tco_model.terminology import CONFIG_FIELD_MAPPINGS
    
    # Constants for configuration file sections
    VEHICLE_INFO_SECTION = 'vehicle_info'
    VEHICLE_TYPE_FIELD = 'type'
    
    # Load raw data
    data = load_yaml_file(file_path)
    
    # Get vehicle type for proper mapping
    vehicle_type = None
    if VEHICLE_INFO_SECTION in data and VEHICLE_TYPE_FIELD in data[VEHICLE_INFO_SECTION]:
        vehicle_type = data[VEHICLE_INFO_SECTION][VEHICLE_TYPE_FIELD]
    
    # Transform data to model format
    if vehicle_type and vehicle_type in CONFIG_FIELD_MAPPINGS:
        # For vehicle parameters, use specific vehicle type mapping
        model_data = transform_vehicle_config(data, vehicle_type)
    else:
        # For other models, transform using convert_config_to_model_format
        model_data = convert_config_to_model_format(data)
    
    try:
        return model_class.parse_obj(model_data)
    except ValidationError as e:
        raise ValidationError(f"Validation error in {file_path}: {str(e)}", model_class)


def map_config_key_to_model_field(config_key: str) -> str:
    """
    Map a configuration file key to the corresponding model field name.
    
    Args:
        config_key: The configuration file key to map
        
    Returns:
        str: The corresponding model field name
        
    Example:
        >>> model_field = map_config_key_to_model_field("energy_consumption.base_rate_kwh_per_km")
        >>> print(model_field)  # "energy_consumption.base_rate"
    """
    from tco_model.terminology import CONFIG_TO_MODEL_MAPPING
    return CONFIG_TO_MODEL_MAPPING.get(config_key, config_key)


def map_model_field_to_config_key(model_field: str) -> str:
    """
    Map a model field name to the corresponding configuration file key.
    
    Args:
        model_field: The model field name to map
        
    Returns:
        str: The corresponding configuration file key
        
    Example:
        >>> config_key = map_model_field_to_config_key("energy_consumption.base_rate")
        >>> print(config_key)  # "energy_consumption.base_rate_kwh_per_km"
    """
    from tco_model.terminology import CONFIG_TO_MODEL_MAPPING
    
    # Create reverse mapping once and cache it in the function
    if not hasattr(map_model_field_to_config_key, "reverse_mapping"):
        map_model_field_to_config_key.reverse_mapping = {
            v: k for k, v in CONFIG_TO_MODEL_MAPPING.items()
        }
    
    return map_model_field_to_config_key.reverse_mapping.get(model_field, model_field)


def transform_vehicle_config(config_data: Dict[str, Any], vehicle_type: str) -> Dict[str, Any]:
    """
    Transform vehicle configuration data using the standardized field mappings.
    
    Args:
        config_data: Raw configuration data
        vehicle_type: Type of vehicle ('battery_electric' or 'diesel')
        
    Returns:
        Dict with transformed data mapped to model fields
    """
    from tco_model.terminology import CONFIG_FIELD_MAPPINGS
    from utils.config_utils import get_nested_config_value, set_nested_model_value
    
    # Create target dictionary
    model_data = {}
    
    # Get mapping for this vehicle type
    if vehicle_type not in CONFIG_FIELD_MAPPINGS:
        return config_data  # Return as-is if no mapping found
        
    mappings = CONFIG_FIELD_MAPPINGS[vehicle_type]
    
    # Apply mappings
    for config_key, model_key in mappings.items():
        value = get_nested_config_value(config_data, config_key)
        if value is not None:
            set_nested_model_value(model_data, model_key, value)
    
    return model_data


def convert_config_to_model_format(config_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert general configuration data using the standardized mappings.
    
    Args:
        config_data: Raw configuration data
        
    Returns:
        Dict with transformed data mapped to model fields
    """
    from tco_model.terminology import ECONOMIC_CONFIG_MAPPING, OPERATIONAL_CONFIG_MAPPING
    from utils.config_utils import get_nested_config_value, set_nested_model_value
    
    # Create target dictionary
    model_data = {}
    
    # Apply economic parameter mappings if present
    if 'economic' in config_data or 'general' in config_data or 'financing' in config_data:
        for config_key, model_key in ECONOMIC_CONFIG_MAPPING.items():
            value = get_nested_config_value(config_data, config_key)
            if value is not None:
                set_nested_model_value(model_data, f"economic.{model_key}", value)
    
    # Apply operational parameter mappings if present
    if 'operational' in config_data:
        for config_key, model_key in OPERATIONAL_CONFIG_MAPPING.items():
            value = get_nested_config_value(config_data, f"operational.{config_key}")
            if value is not None:
                set_nested_model_value(model_data, f"operational.{model_key}", value)
    
    return model_data


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
    infrastructure_params = None
    if infrastructure_data:
        infrastructure_params = InfrastructureParameters(
            charger_hardware_cost=infrastructure_data.get('charger_hardware_cost', 150000),
            installation_cost=infrastructure_data.get('installation_cost', 50000),
            maintenance_annual_percentage=infrastructure_data.get('maintenance_annual_percentage', 0.015),
            trucks_per_charger=infrastructure_data.get('trucks_per_charger', 1.0),
            grid_upgrade_cost=infrastructure_data.get('grid_upgrade_cost', 0)
        )
    else:
        # Try to load from operational parameters
        op_params_path = os.path.join(settings.defaults_config_path, "operational_parameters.yaml")
        op_data = load_yaml_file(op_params_path)
        infra_data = op_data.get('infrastructure', {})
        
        infrastructure_params = InfrastructureParameters(
            charger_hardware_cost=infra_data.get('charger_hardware', {}).get('high_power_350kw_plus', 150000),
            installation_cost=infra_data.get('installation', {}).get('default', 50000),
            maintenance_annual_percentage=infra_data.get('maintenance', {}).get('annual_percentage', 0.015),
            trucks_per_charger=1.0,
            grid_upgrade_cost=0
        )
    
    # Create the full BET parameters
    return BETParameters(
        name=vehicle_info.get('name', 'Default BET'),
        type=VehicleType.BATTERY_ELECTRIC,
        category=vehicle_info.get('category', 'articulated'),
        purchase_price=purchase.get('base_price_2025', 400000),
        annual_price_decrease_real=purchase.get('annual_price_decrease_real', 0.02),
        max_payload_tonnes=performance.get('max_payload_tonnes', 26),
        range_km=performance.get('range_km', 350),
        battery=battery_params,
        energy_consumption=energy_params,
        charging=charging_params,
        maintenance=maintenance_params,
        residual_value=residual_params,
        infrastructure=infrastructure_params
    )


def load_diesel_parameters(config_path: str) -> DieselParameters:
    """
    Load Diesel Truck parameters from configuration.
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        DieselParameters model with values from the configuration
    """
    data = load_yaml_file(config_path)
    
    # Extract sections
    vehicle_info = data.get('vehicle_info', {})
    purchase = data.get('purchase', {})
    engine_data = data.get('engine', {})
    fuel_data = data.get('fuel_consumption', {})
    maintenance_data = data.get('maintenance', {})
    residual_data = data.get('residual_values', {}) if 'residual_values' in data else None
    performance = data.get('performance', {})
    
    # Load residual value data from operational parameters if not in vehicle config
    if not residual_data:
        op_params_path = os.path.join(settings.defaults_config_path, "operational_parameters.yaml")
        op_data = load_yaml_file(op_params_path)
        
        if vehicle_info.get('category') == 'rigid':
            residual_data = op_data.get('residual_values', {}).get('rigid_diesel', {})
        else:
            residual_data = op_data.get('residual_values', {}).get('articulated_diesel', {})
    
    # Create engine parameters
    engine_params = EngineParameters(
        power_kw=engine_data.get('power_kw', 400),
        displacement_litres=engine_data.get('displacement_litres', 13),
        euro_emission_standard=engine_data.get('euro_emission_standard', 'Euro 6'),
        adblue_required=engine_data.get('adblue_required', True),
        adblue_consumption_percent_of_diesel=engine_data.get('adblue_consumption_percent_of_diesel', 0.05)
    )
    
    # Create fuel consumption parameters
    consumption_range = fuel_data.get('consumption_range', {})
    fuel_params = DieselConsumptionParameters(
        base_rate=fuel_data.get('base_rate_l_per_km', 0.53),
        min_rate=consumption_range.get('min', 0.45),
        max_rate=consumption_range.get('max', 0.60),
        load_adjustment_factor=fuel_data.get('load_adjustment_factor', 0.25),
        hot_weather_adjustment=fuel_data.get('temperature_adjustment', {}).get('hot_weather', 0.03),
        cold_weather_adjustment=fuel_data.get('temperature_adjustment', {}).get('cold_weather', 0.05)
    )
    
    # Create maintenance parameters
    detailed_costs = maintenance_data.get('detailed_costs', {})
    maintenance_params = MaintenanceParameters(
        cost_per_km=maintenance_data.get('cost_per_km', 0.15),
        annual_fixed_min=detailed_costs.get('annual_fixed_min', 2500),
        annual_fixed_max=detailed_costs.get('annual_fixed_max', 5000),
        annual_fixed_default=(detailed_costs.get('annual_fixed_min', 2500) + detailed_costs.get('annual_fixed_max', 5000)) / 2,
        scheduled_maintenance_interval_km=maintenance_data.get('scheduled_maintenance_interval_km', 25000),
        major_service_interval_km=maintenance_data.get('major_service_interval_km', 100000)
    )
    
    # Create residual value parameters
    residual_params = ResidualValueParameters(
        year_5_range=residual_data.get('year_5', [0.45, 0.55]),
        year_10_range=residual_data.get('year_10', [0.25, 0.35]),
        year_15_range=residual_data.get('year_15', [0.10, 0.20])
    )
    
    # Create the full diesel parameters
    return DieselParameters(
        name=vehicle_info.get('name', 'Default Diesel'),
        type=VehicleType.DIESEL,
        category=vehicle_info.get('category', 'articulated'),
        purchase_price=purchase.get('base_price_2025', 200000),
        annual_price_decrease_real=purchase.get('annual_price_decrease_real', 0.00),
        max_payload_tonnes=performance.get('max_payload_tonnes', 28),
        range_km=performance.get('range_km', 2200),
        engine=engine_params,
        fuel_consumption=fuel_params,
        maintenance=maintenance_params,
        residual_value=residual_params
    )


def load_default_scenario(vehicle_config_name: str) -> ScenarioInput:
    """
    Create a complete default scenario with all necessary parameters.
    
    Args:
        vehicle_config_name: Name of the vehicle configuration file (without extension)
        
    Returns:
        ScenarioInput model with default values
    """
    # Determine vehicle type from config name
    if "bet" in vehicle_config_name.lower():
        vehicle_type = VehicleType.BATTERY_ELECTRIC
    else:
        vehicle_type = VehicleType.DIESEL
    
    # Load parameters
    vehicle_path = os.path.join(settings.vehicles_config_path, f"{vehicle_config_name}.yaml")
    vehicle = load_vehicle_parameters(vehicle_type, vehicle_path)
    
    economic = load_economic_parameters()
    operational = load_operational_parameters()
    financing = load_financing_parameters()
    
    # Create scenario
    return ScenarioInput(
        scenario_name=f"Default {vehicle.name} Scenario",
        vehicle=vehicle,
        operational=operational,
        economic=economic,
        financing=financing
    )


def find_available_vehicle_configs() -> Dict[VehicleType, List[str]]:
    """
    Find all available vehicle configuration files in the config directory.
    
    Returns:
        Dictionary mapping vehicle types to lists of available configuration names
    """
    result = {
        VehicleType.BATTERY_ELECTRIC: [],
        VehicleType.DIESEL: []
    }
    
    vehicles_dir = settings.vehicles_config_path
    
    # Find all YAML files in the vehicles directory
    for file_path in glob.glob(os.path.join(vehicles_dir, "*.yaml")):
        try:
            # Get just the filename without extension
            filename = os.path.basename(file_path).replace(".yaml", "")
            
            # Load the file to determine vehicle type
            data = load_yaml_file(file_path)
            vehicle_info = data.get('vehicle_info', {})
            
            # Get vehicle type from the config file
            vehicle_type_str = vehicle_info.get('type', '').lower()
            
            # Map to the appropriate VehicleType and add to result
            if vehicle_type_str == 'battery_electric':
                result[VehicleType.BATTERY_ELECTRIC].append(filename)
            elif vehicle_type_str == 'diesel':
                result[VehicleType.DIESEL].append(filename)
            
        except Exception as e:
            # Skip files that can't be loaded properly
            print(f"Error loading vehicle config {file_path}: {str(e)}")
            continue
    
    # Sort the lists so they appear in a consistent order
    for vehicle_type in result:
        result[vehicle_type].sort()
    
    return result


# --- Streamlit State Management Helpers ---

def get_safe_state_value(key: str, default: Any = None) -> Any:
    """
    Safely access a possibly nested value in Streamlit session state.
    
    This function allows accessing deeply nested values in the session state
    using dot notation. If any part of the path doesn't exist, it returns
    the default value.
    
    Args:
        key: Dot-separated path to the value (e.g., "vehicle_1_input.vehicle.purchase_price")
        default: Default value to return if the key doesn't exist
        
    Returns:
        Value from session state or default
        
    Examples:
        >>> get_safe_state_value("vehicle_1_input.vehicle.purchase_price", 0)
        400000
        >>> get_safe_state_value("nonexistent_key", "default_value")
        'default_value'
    """
    if '.' not in key:
        return st.session_state.get(key, default)
    
    parts = key.split('.')
    current = st.session_state
    
    for part in parts:
        if hasattr(current, part):
            # Handle Pydantic models and other objects with attributes
            current = getattr(current, part)
        elif isinstance(current, dict) and part in current:
            # Handle dictionary access
            current = current[part]
        else:
            return default
    
    return current


def set_safe_state_value(key: str, value: Any, create_missing: bool = True) -> bool:
    """
    Safely set a possibly nested value in Streamlit session state.
    
    This function allows setting deeply nested values in the session state
    using dot notation. It can create missing intermediate dictionaries
    if create_missing is True.
    
    Args:
        key: Dot-separated path to the value (e.g., "vehicle_1_input.operational.annual_distance_km")
        value: Value to set
        create_missing: Whether to create missing intermediate dictionaries
        
    Returns:
        bool: True if the value was set successfully, False otherwise
        
    Examples:
        >>> set_safe_state_value("vehicle_1_input.operational.annual_distance_km", 120000)
        True
    """
    if '.' not in key:
        st.session_state[key] = value
        return True
    
    parts = key.split('.')
    last_part = parts.pop()
    
    # Start with session_state
    current = st.session_state
    parent_path = ""
    
    # Navigate to the parent object
    for part in parts:
        parent_path = f"{parent_path}.{part}" if parent_path else part
        
        if hasattr(current, part):
            # Handle Pydantic models and other objects with attributes
            current = getattr(current, part)
        elif isinstance(current, dict) and part in current:
            # Handle dictionary access
            current = current[part]
        elif create_missing and isinstance(current, dict):
            # Create missing dictionary
            current[part] = {}
            current = current[part]
        else:
            # Can't navigate further or create path
            return False
    
    # Set the value - handle both attribute and dict access
    try:
        if hasattr(current, last_part) or not isinstance(current, dict):
            # Handle object with attributes
            setattr(current, last_part, value)
        else:
            # Handle dictionary
            current[last_part] = value
        return True
    except (AttributeError, TypeError):
        return False


def update_state_from_model(prefix: str, model: BaseModel) -> None:
    """
    Update session state with all fields from a Pydantic model.
    
    This function is useful for updating session state after loading a model
    from a configuration file or after making changes to a model.
    
    Args:
        prefix: Prefix to use for session state keys (e.g., "vehicle_1_input")
        model: Pydantic model to extract values from
        
    Examples:
        >>> scenario = load_default_scenario("default_bet")
        >>> update_state_from_model("vehicle_1_input", scenario)
    """
    # Convert the model to a dictionary
    model_dict = model.dict()
    
    # Update session state for each key in the model
    _update_nested_state(prefix, model_dict)


def _update_nested_state(prefix: str, data: Dict[str, Any]) -> None:
    """
    Recursively update session state from a nested dictionary.
    
    Args:
        prefix: Prefix for session state keys
        data: Dictionary of values to update
    """
    for key, value in data.items():
        full_key = f"{prefix}.{key}"
        
        if isinstance(value, dict):
            # Recursively handle nested dictionaries
            _update_nested_state(full_key, value)
        else:
            # Set the value in session state
            set_safe_state_value(full_key, value)


def update_model_from_state(prefix: str, model_class: Type[T]) -> Optional[T]:
    """
    Create or update a Pydantic model with values from session state.
    
    This function is useful for collecting user inputs from Streamlit widgets
    and creating a validated model.
    
    Args:
        prefix: Prefix for session state keys (e.g., "vehicle_1_input")
        model_class: Pydantic model class to create
        
    Returns:
        Updated model instance or None if validation fails
        
    Examples:
        >>> updated_scenario = update_model_from_state("vehicle_1_input", ScenarioInput)
        >>> if updated_scenario:
        >>>     # Valid model created
        >>>     calculator.calculate(updated_scenario)
    """
    # Collect all relevant keys from session state
    model_dict = _extract_nested_state(prefix)
    
    # Create and validate the model
    try:
        # Handle potential empty dictionaries for nested models
        return model_class.parse_obj(model_dict)
    except ValidationError as e:
        st.error(f"Validation error: {str(e)}")
        return None


def _extract_nested_state(prefix: str) -> Dict[str, Any]:
    """
    Extract a nested dictionary from session state keys with a given prefix.
    
    Args:
        prefix: Prefix for session state keys
        
    Returns:
        Dictionary with values from session state
    """
    result = {}
    prefix_len = len(prefix) + 1  # +1 for the dot
    
    # Collect all keys that start with the prefix
    for key in st.session_state:
        if isinstance(key, str) and key.startswith(f"{prefix}."):
            # Extract the part after the prefix
            path = key[prefix_len:]
            
            # Navigate to the right place in the result dictionary
            current = result
            parts = path.split('.')
            
            for i, part in enumerate(parts[:-1]):
                if part not in current:
                    current[part] = {}
                current = current[part]
            
            # Set the value at the leaf
            current[parts[-1]] = st.session_state[key]
    
    return result


def debug_state(prefix: Optional[str] = None) -> Dict[str, Any]:
    """
    Generate a dictionary of session state values for debugging.
    
    Args:
        prefix: Optional prefix to filter keys
        
    Returns:
        Dictionary of session state values
        
    Examples:
        >>> st.write(debug_state("vehicle_1_input"))
    """
    if prefix is None:
        # Return the entire session state
        return dict(st.session_state)
    
    # Filter keys by prefix
    debug_dict = {}
    for key in st.session_state:
        if isinstance(key, str) and key.startswith(f"{prefix}"):
            debug_dict[key] = st.session_state[key]
    
    return debug_dict


def initialize_nested_state(key: str, default_value: Any) -> None:
    """
    Initialize a nested value in session state if it doesn't exist.
    
    This is useful for ensuring that nested paths exist before setting values.
    
    Args:
        key: Dot-separated path to initialize
        default_value: Default value to set if the key doesn't exist
        
    Examples:
        >>> initialize_nested_state("vehicle_1_input.operational", {})
        >>> initialize_nested_state("vehicle_1_input.operational.annual_distance_km", 100000)
    """
    if get_safe_state_value(key) is None:
        set_safe_state_value(key, default_value)


# --- Formatting Utilities ---

def format_currency(value: float, decimals: int = 0) -> str:
    """
    Format a value as Australian currency.
    
    Args:
        value: Value to format
        decimals: Number of decimal places to show
        
    Returns:
        Formatted currency string
    """
    return f"${value:,.{decimals}f}"


def format_percentage(value: float, decimals: int = 1) -> str:
    """
    Format a decimal value as a percentage.
    
    Args:
        value: Value to format (e.g., 0.07 for 7%)
        decimals: Number of decimal places to show
        
    Returns:
        Formatted percentage string
    """
    return f"{value * 100:.{decimals}f}%"