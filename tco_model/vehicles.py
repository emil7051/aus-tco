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
    config_path = Path("config/vehicles") / f"{config_name}.yaml"
    config_data = load_yaml_file(config_path)
    
    # Convert the configuration data to a BETParameters object
    return BETParameters(**config_data)


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
    config_path = Path("config/vehicles") / f"{config_name}.yaml"
    config_data = load_yaml_file(config_path)
    
    # Convert the configuration data to a DieselParameters object
    return DieselParameters(**config_data)


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
    
    # Get all YAML files in the vehicles directory
    config_dir = Path("config/vehicles")
    for config_file in config_dir.glob("*.yaml"):
        # Load the YAML file to check the vehicle type
        config_data = load_yaml_file(config_file)
        
        # Skip if the file doesn't contain vehicle type information
        if "type" not in config_data:
            continue
        
        # Get the vehicle type
        vehicle_type_str = config_data["type"]
        
        # Convert string to VehicleType enum
        try:
            vehicle_type = VehicleType(vehicle_type_str)
        except ValueError:
            # Skip if the vehicle type is not recognized
            continue
        
        # Add the configuration name to the appropriate list
        config_name = config_file.stem
        available_configs[vehicle_type].append(config_name)
    
    return available_configs 