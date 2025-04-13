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

from utils.config_utils import validate_config_file
from tco_model.schemas import (
    VehicleInfoSchema, 
    PurchaseSchema, 
    EnergyConsumptionSchema, 
    FuelConsumptionSchema
)

# Constants
CONFIG_DIRS = {
    "vehicles": "config/vehicles",
    "economic": "config/economic", 
    "operational": "config/operational"
}

SCHEMA_MAPPING = {
    "vehicle_info": VehicleInfoSchema,
    "purchase": PurchaseSchema,
    "energy_consumption": EnergyConsumptionSchema,
    "fuel_consumption": FuelConsumptionSchema
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
            errors = []
            
            # For each section, validate against the appropriate schema
            for section, schema_class in SCHEMA_MAPPING.items():
                is_valid, section_errors = validate_config_file(
                    file_path, 
                    schema_class,
                    section_path=section
                )
                if not is_valid and section_errors:
                    errors.extend([f"{section}: {e}" for e in section_errors])
            
            # Determine validity based on errors
            if errors:
                invalid_files[str(file_path)] = errors
            else:
                valid_files.append(str(file_path))
                
        except Exception as e:
            invalid_files[str(file_path)] = [f"Error checking file: {str(e)}"]
    
    return valid_files, invalid_files


def main():
    """Main entry point for the config checker script."""
    parser = argparse.ArgumentParser(description="Check configuration files for consistency")
    parser.add_argument("directory", nargs="?", default=None, 
                        help="Directory containing configuration files (default: check all)")
    args = parser.parse_args()
    
    if args.directory:
        directories = [Path(args.directory)]
    else:
        directories = [Path(dir_path) for dir_path in CONFIG_DIRS.values()]
    
    all_valid_files = []
    all_invalid_files = {}
    
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