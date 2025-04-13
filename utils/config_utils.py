"""
Configuration Validation Utilities

This module provides functions for validating configuration files against schema
definitions and transforming configuration data to standardized formats.
"""

from typing import Dict, Any, Type, Union, List, Optional, Tuple
from pathlib import Path
import yaml
from pydantic import BaseModel, ValidationError


def validate_config_file(file_path: Union[str, Path], schema_class: Type[BaseModel]) -> Tuple[bool, Optional[List[str]]]:
    """
    Validate a configuration file against a schema.
    
    Args:
        file_path: Path to the config file
        schema_class: Pydantic schema class to validate against
        
    Returns:
        Tuple containing (is_valid, list_of_errors)
        
    Example:
        >>> is_valid, errors = validate_config_file("config/vehicles/bet_truck.yaml", BETSchema)
        >>> if not is_valid:
        >>>     for error in errors:
        >>>         print(f"Error: {error}")
    """
    try:
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


def get_nested_config_value(config_data: Dict[str, Any], field_path: str) -> Any:
    """
    Retrieve a nested value from a configuration dictionary using dot notation.
    
    Args:
        config_data: Configuration data dictionary
        field_path: Dot-separated path to the field (e.g., "battery.capacity_kwh")
        
    Returns:
        The value at the specified path, or None if not found
    """
    parts = field_path.split('.')
    current = config_data
    
    try:
        for part in parts:
            current = current[part]
        return current
    except (KeyError, TypeError):
        return None


def set_nested_model_value(model_data: Dict[str, Any], field_path: str, value: Any) -> None:
    """
    Set a nested value in a model dictionary using dot notation.
    
    Args:
        model_data: Model data dictionary to update
        field_path: Dot-separated path to the field (e.g., "battery.capacity_kwh")
        value: Value to set
    """
    parts = field_path.split('.')
    current = model_data
    
    # Navigate to the parent object, creating dictionaries as needed
    for part in parts[:-1]:
        if part not in current:
            current[part] = {}
        current = current[part]
    
    # Set the value
    current[parts[-1]] = value 