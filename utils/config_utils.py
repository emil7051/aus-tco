"""
Configuration utilities for validating and loading config files.

This module provides utility functions for working with configuration files,
including validation against schemas and loading with field mapping.
"""

import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Type, Union
from pydantic import BaseModel, ValidationError


def validate_config_file(file_path: Union[str, Path], schema_class: Type[BaseModel]) -> Tuple[bool, Optional[List[str]]]:
    """
    Validate a configuration file against a schema.
    
    Args:
        file_path: Path to the config file
        schema_class: Pydantic schema class to validate against
        
    Returns:
        Tuple containing (is_valid, list_of_errors)
    """
    try:
        # Load the YAML file
        with open(file_path, 'r') as f:
            config_data = yaml.safe_load(f)
            
        # Try to parse the config data with the schema
        schema_class.parse_obj(config_data)
        return True, None
    
    except FileNotFoundError:
        return False, [f"File not found: {file_path}"]
    
    except yaml.YAMLError as e:
        return False, [f"YAML parsing error: {str(e)}"]
    
    except ValidationError as e:
        errors = []
        for error in e.errors():
            location = " -> ".join(str(loc) for loc in error["loc"])
            message = error["msg"]
            errors.append(f"{location}: {message}")
        return False, errors


def load_yaml_file(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Load a YAML file and return its contents as a dictionary.
    
    Args:
        file_path: Path to the YAML file
        
    Returns:
        Dictionary containing the file contents
        
    Raises:
        FileNotFoundError: If the file does not exist
        yaml.YAMLError: If the file is not valid YAML
    """
    with open(file_path, 'r') as f:
        return yaml.safe_load(f)


def get_nested_config_value(config_data: Dict[str, Any], key_path: str) -> Any:
    """
    Get a value from a nested dictionary using a dot-separated key path.
    
    Args:
        config_data: Configuration data dictionary
        key_path: Dot-separated path to the value (e.g., "energy_consumption.base_rate")
        
    Returns:
        The value at the specified path, or None if not found
    """
    keys = key_path.split('.')
    current = config_data
    
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return None
            
    return current


def set_nested_model_value(model_data: Dict[str, Any], key_path: str, value: Any) -> None:
    """
    Set a value in a nested dictionary using a dot-separated key path.
    
    Args:
        model_data: Model data dictionary to modify
        key_path: Dot-separated path to the value (e.g., "energy_consumption.base_rate")
        value: Value to set
    """
    keys = key_path.split('.')
    current = model_data
    
    # Create intermediate dictionaries if they don't exist
    for i, key in enumerate(keys[:-1]):
        if key not in current:
            current[key] = {}
        current = current[key]
        
    # Set the final value
    current[keys[-1]] = value


def migrate_config_to_standard(file_path: Union[str, Path], 
                              vehicle_type: Optional[str] = None) -> Dict[str, Any]:
    """
    Migrate a configuration file to use standardized field names.
    
    Args:
        file_path: Path to the config file
        vehicle_type: Vehicle type to determine appropriate mappings
        
    Returns:
        Dict with standardized configuration data
    """
    from tco_model.terminology import CONFIG_FIELD_MAPPINGS
    
    # Constants for common configuration sections
    VEHICLE_INFO_SECTION = 'vehicle_info'
    VEHICLE_TYPE_FIELD = 'type'
    
    # Load the file
    with open(file_path, 'r') as f:
        config_data = yaml.safe_load(f)
    
    # Determine vehicle type if not provided
    if not vehicle_type and VEHICLE_INFO_SECTION in config_data:
        vehicle_type = config_data[VEHICLE_INFO_SECTION].get(VEHICLE_TYPE_FIELD)
    
    if not vehicle_type or vehicle_type not in CONFIG_FIELD_MAPPINGS:
        return config_data  # Return as-is if we can't determine mappings
    
    # Create a standardized version
    standardized_data = {}
    
    # Extract mappings for just this vehicle type
    mappings = CONFIG_FIELD_MAPPINGS[vehicle_type]
    for config_key, model_key in mappings.items():
        value = get_nested_config_value(config_data, config_key)
        if value is not None:
            set_nested_model_value(standardized_data, model_key, value)
    
    return standardized_data 