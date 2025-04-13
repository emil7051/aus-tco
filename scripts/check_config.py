#!/usr/bin/env python
"""
Configuration file checker script.

This script validates all configuration files against their schemas
and reports any inconsistencies or errors.
"""

import os
import sys
from pathlib import Path
import argparse
from typing import Dict, List, Tuple
import yaml

# Add parent directory to path to allow imports
sys.path.append(str(Path(__file__).parent.parent))
from utils.config_utils import validate_config_file
from tco_model.schemas import (
    VehicleInfoSchema, 
    PurchaseSchema, 
    EnergyConsumptionSchema, 
    FuelConsumptionSchema,
    BETConfigSchema,
    DieselConfigSchema
)

# Constants
CONFIG_DIRS = {
    "vehicles_bet": "config/vehicles/bet",
    "vehicles_diesel": "config/vehicles/diesel",
    "root": "config"
}

SCHEMA_MAPPING = {
    "vehicle_info": VehicleInfoSchema,
    "purchase": PurchaseSchema,
    "energy_consumption": EnergyConsumptionSchema,
    "fuel_consumption": FuelConsumptionSchema
}

VEHICLE_SCHEMA_MAPPING = {
    "battery_electric": BETConfigSchema,
    "diesel": DieselConfigSchema
}

def check_vehicle_config_files(directory: Path) -> Tuple[List[str], Dict[str, List[str]]]:
    """
    Check all vehicle config files in a directory for consistency.
    
    Args:
        directory: Directory containing vehicle config files
        
    Returns:
        Tuple containing (valid_files, invalid_files_with_errors)
    """
    valid_files = []
    invalid_files = {}
    
    for file_path in directory.glob("*.yaml"):
        try:
            # Load the file to check basic YAML validity
            with open(file_path, 'r') as f:
                config_data = yaml.safe_load(f)
                
            # Determine vehicle type
            vehicle_type = None
            if "vehicle_info" in config_data and "type" in config_data["vehicle_info"]:
                vehicle_type = config_data["vehicle_info"]["type"]
            
            # Use appropriate schema based on vehicle type
            schema_class = None
            if vehicle_type == "battery_electric":
                schema_class = BETConfigSchema
            elif vehicle_type == "diesel":
                schema_class = DieselConfigSchema
                
            if schema_class:
                # Validate the entire file against the appropriate schema
                is_valid, errors = validate_config_file(file_path, schema_class)
                
                if not is_valid:
                    invalid_files[str(file_path)] = errors
                else:
                    valid_files.append(str(file_path))
            else:
                invalid_files[str(file_path)] = ["Could not determine vehicle type"]
                
        except Exception as e:
            invalid_files[str(file_path)] = [f"Error checking file: {str(e)}"]
    
    return valid_files, invalid_files


def check_economic_parameters(file_path: Path) -> Tuple[bool, List[str]]:
    """
    Check economic parameters configuration file.
    
    Args:
        file_path: Path to the economic parameters file
        
    Returns:
        Tuple containing (is_valid, list_of_errors)
    """
    # This would use a dedicated schema for economic parameters
    # For now just check basic validity
    is_valid = True
    errors = []
    
    if not file_path.exists():
        return False, ["File not found"]
        
    return is_valid, errors


def check_operational_parameters(file_path: Path) -> Tuple[bool, List[str]]:
    """
    Check operational parameters configuration file.
    
    Args:
        file_path: Path to the operational parameters file
        
    Returns:
        Tuple containing (is_valid, list_of_errors)
    """
    # This would use a dedicated schema for operational parameters
    # For now just check basic validity
    is_valid = True
    errors = []
    
    if not file_path.exists():
        return False, ["File not found"]
        
    return is_valid, errors


def main():
    """Main entry point for the config checker script."""
    parser = argparse.ArgumentParser(description="Check configuration files for consistency")
    parser.add_argument("directory", nargs="?", default=None, 
                        help="Directory containing configuration files (default: check all)")
    args = parser.parse_args()
    
    all_valid_files = []
    all_invalid_files = {}
    
    # Check vehicle config files
    if args.directory:
        directories = [Path(args.directory)]
    else:
        directories = [Path(CONFIG_DIRS["vehicles_bet"]), Path(CONFIG_DIRS["vehicles_diesel"])]
    
        # Also check economic and operational parameters
        economic_file = Path(CONFIG_DIRS["root"]) / "economic_parameters.yaml"
        operational_file = Path(CONFIG_DIRS["root"]) / "operational_parameters.yaml"
        
        eco_valid, eco_errors = check_economic_parameters(economic_file)
        if eco_valid:
            all_valid_files.append(str(economic_file))
        else:
            all_invalid_files[str(economic_file)] = eco_errors
            
        op_valid, op_errors = check_operational_parameters(operational_file)
        if op_valid:
            all_valid_files.append(str(operational_file))
        else:
            all_invalid_files[str(operational_file)] = op_errors
    
    for directory in directories:
        if not directory.exists() or not directory.is_dir():
            print(f"Warning: {directory} is not a valid directory")
            continue
        
        print(f"Checking config files in {directory}...")
        valid_files, invalid_files = check_vehicle_config_files(directory)
        all_valid_files.extend(valid_files)
        all_invalid_files.update(invalid_files)
    
    print(f"\nSummary:")
    print(f"- Valid files: {len(all_valid_files)}")
    print(f"- Invalid files: {len(all_invalid_files)}")
    
    if all_invalid_files:
        print("\nFailed validation:")
        for file, errors in all_invalid_files.items():
            print(f"- {file}:")
            for error in errors:
                print(f"  - {error}")
        sys.exit(1)
    else:
        print("\nAll files are valid!")
        sys.exit(0)


if __name__ == "__main__":
    main() 