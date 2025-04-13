# Phase 5: Documentation and Cleanup

This document outlines the implementation steps for Phase 5 of the field refactoring project, focusing on finalizing documentation and cleaning up any remaining issues.

## Goals

- Create comprehensive documentation for the new naming conventions
- Add migration guides for developers
- Remove deprecated code after transition
- Ensure consistent documentation across the codebase
- Clean up any remaining inconsistencies

## Implementation Steps

### Step 1: Add Deprecation Warnings

Add clear deprecation warnings for old field names in key places:

```python
# In any function that returns a TCOOutput
def legacy_function_returning_tco_output() -> TCOOutput:
    """
    Get TCO results for a scenario.
    
    Note: This function returns TCOOutput with renamed fields.
    The field 'npv_total' is now 'total_tco', and 'lcod_per_km' is now 'lcod'.
    
    Returns:
        TCOOutput: The calculated TCO results
    """
    result = calculate_tco()
    warnings.warn(
        "This function returns TCOOutput with renamed fields: " 
        "npv_total -> total_tco, lcod_per_km -> lcod", 
        DeprecationWarning, 
        stacklevel=2  # Point to caller's code
    )
    return result
```

### Step 2: Update API Documentation

Update docstrings and any API documentation to reflect the new field names:

```python
def calculate(self, scenario: ScenarioInput) -> TCOOutput:
    """
    Calculate the TCO for a given scenario input.
    
    Args:
        scenario: The scenario input containing all parameters for the calculation.
        
    Returns:
        TCOOutput: The calculated TCO results with the following key fields:
            - total_tco: Total cost of ownership in NPV terms
            - lcod: Levelized cost of driving per km
            - annual_costs: Annual breakdown of costs as AnnualCostsCollection
            - npv_costs: NPV breakdown of costs by component
            
    Example:
        >>> calculator = TCOCalculator()
        >>> result = calculator.calculate(scenario)
        >>> print(f"Total TCO: {result.total_tco}")
        >>> print(f"LCOD: {result.lcod} AUD/km")
    """
    # ...implementation...
```

### Step 3: Create Migration Guide

Create a migration guide document to help users adapt to the renamed fields:

```markdown
# TCO Model Field Migration Guide

This guide explains the changes in field names and data structures in the TCO model.

## Key Field Renames

| Old Field | New Field | Description |
|-----------|-----------|-------------|
| `npv_total` | `total_tco` | Total Cost of Ownership (NPV) |
| `lcod_per_km` | `lcod` | Levelized Cost of Driving |
| `npv_difference` | `tco_difference` | Difference in TCO between scenarios |
| `npv_difference_percentage` | `tco_percentage` | Percentage difference in TCO |

## New Data Structures

### AnnualCostsCollection

We've introduced a new wrapper class for annual costs that provides both list-like access and attribute access:

```python
# Old way - list indexing only
annual_energy_year2 = result.annual_costs[2].energy

# New way - list indexing still works
annual_energy_year2 = result.annual_costs[2].energy

# New way - attribute access for all years
all_energy_costs = result.annual_costs.energy  # Returns list of all years
```

### Combined Cost Components

We've added combined cost components as properties:

```python
# Old way - access individual components and combine
insurance_reg = result.npv_costs.insurance + result.npv_costs.registration

# New way - use combined property
insurance_reg = result.npv_costs.insurance_registration
```

## Standardized Component Access

Use the new standardized component access functions:

```python
from tco_model.terminology import get_component_value

# Get NPV component value
acquisition_cost = get_component_value(result.npv_costs, "acquisition")

# Get combined component
insurance_reg = get_component_value(result.npv_costs, "insurance_registration")

# Get annual component for a specific year
year3_energy = get_component_value(result.annual_costs, "energy", 3)
```

## Usage Examples

### Before:
```python
result = calculator.calculate(scenario)
total_cost = result.npv_total
cost_per_km = result.lcod_per_km

comparison = calculator.compare_results(result1, result2)
cost_diff = comparison.npv_difference
percentage_diff = comparison.npv_difference_percentage
```

### After:
```python
result = calculator.calculate(scenario)
total_cost = result.total_tco
cost_per_km = result.lcod

comparison = calculator.compare_results(result1, result2)
cost_diff = comparison.tco_difference
percentage_diff = comparison.tco_percentage
cheaper_option = comparison.cheaper_option  # New property
component_diffs = comparison.component_differences  # New property
```

## Strategy Pattern Usage

Use the new factory pattern for strategies:

```python
# Old way - direct instantiation
if vehicle_type == VehicleType.BATTERY_ELECTRIC:
    strategy = BETPowerConsumptionStrategy()  # Old name
else:
    strategy = DieselConsumptionStrategy()

# New way - factory pattern
from tco_model.strategies import StrategyFactory
strategy = StrategyFactory.get_strategy("energy", vehicle_type.value)
```

## Configuration File Handling

Use the new standardized configuration utilities:

```python
# Validate config against schema
from utils.config_utils import validate_config_file
from tco_model.schemas import VehicleInfoSchema

is_valid, errors = validate_config_file("config/vehicle.yaml", VehicleInfoSchema)
if not is_valid:
    for error in errors:
        print(f"Error: {error}")

# Load config with field mapping
from utils.helpers import load_config_as_model
from tco_model.models import BETParameters

params = load_config_as_model("config/vehicle.yaml", BETParameters)
```

## Transition Timeline

- **Phase 1 (Current)**: Backward compatibility mode - old field names still work but issue deprecation warnings
- **Phase 2 (Next Release)**: Old field names will continue to work for backward compatibility
- **Phase 3 (Future Release)**: Old field names will be removed completely
```

### Step 4: Create Developer Guide

Create a detailed developer guide for working with the standardized fields and patterns:

```markdown
# TCO Model Developer Guide

This guide explains how to work with the TCO model codebase following our standardized naming conventions and patterns.

## Field Naming Conventions

### General Rules

1. **Be Explicit and Descriptive**
   - Names should clearly indicate their purpose
   - Avoid ambiguous abbreviations

2. **Use Units in Field Names**
   - Distance: `_km`, `_m`
   - Power: `_kw`, `_hp`
   - Energy: `_kwh`
   - Currency: No suffix (AUD is default)
   - Time: `_years`, `_months`, `_days`
   - Rates: `_per_km`, `_per_year`

3. **Use Consistent Casing**
   - `snake_case` for field and variable names
   - `PascalCase` for class names and enum values
   - `UPPER_SNAKE_CASE` for constants

4. **Use Consistent Boolean Naming**
   - Boolean fields should use prefixes like `is_`, `has_`, or `requires_`
   - Example: `is_urban_operation`, `has_regenerative_braking`

## Working with TCOOutput

The core result class has the following canonical fields:

```python
result = calculator.calculate(scenario)

# Primary fields
total_cost = result.total_tco        # Total cost of ownership (NPV)
per_km_cost = result.lcod            # Levelized cost of driving per km
components = result.npv_costs        # NPV breakdown by component
yearly_costs = result.annual_costs   # Annual costs breakdown

# Access the original scenario
original_scenario = result.scenario
```

## Working with Cost Components

To access individual cost components:

```python
# Direct property access - simple components
acquisition_cost = result.npv_costs.acquisition
energy_cost = result.npv_costs.energy

# Direct property access - combined components
insurance_reg_cost = result.npv_costs.insurance_registration
taxes_levies_cost = result.npv_costs.taxes_levies

# Standardized component access function
from tco_model.terminology import get_component_value
acquisition_cost = get_component_value(result.npv_costs, "acquisition")
insurance_reg_cost = get_component_value(result.npv_costs, "insurance_registration")
```

## Working with Annual Costs

The `annual_costs` field is now an `AnnualCostsCollection` which provides multiple access patterns:

```python
# Index-based access for a specific year
year_2_costs = result.annual_costs[2]
year_2_energy = result.annual_costs[2].energy

# Attribute access for all years
all_energy_costs = result.annual_costs.energy  # List of energy costs for all years
all_insurance_reg = result.annual_costs.insurance_registration  # Combined for all years

# Using standardized access function
from tco_model.terminology import get_component_value
year_2_energy = get_component_value(result.annual_costs, "energy", 2)
```

## Working with Comparisons

The comparison result now includes helpful properties:

```python
comparison = calculator.compare_results(result1, result2)

# Basic comparison fields
diff = comparison.tco_difference
percentage = comparison.tco_percentage

# Get the index of the cheaper option (1 or 2)
cheaper_index = comparison.cheaper_option
cheaper_scenario = comparison.scenario_1 if cheaper_index == 1 else comparison.scenario_2

# Get the differences by component
component_diffs = comparison.component_differences
energy_diff = component_diffs["energy"]
```

## Using the Strategy Pattern

Always use the factory pattern to obtain strategy instances:

```python
from tco_model.strategies import StrategyFactory

# Get vehicle-specific strategy
energy_strategy = StrategyFactory.get_strategy("energy", vehicle_type.value)

# Get strategy with specific implementation
financing_strategy = StrategyFactory.get_strategy("financing", None, "loan")

# Calculate costs using strategy
annual_cost = energy_strategy.calculate_costs(scenario, year)
```

## Working with Configuration Files

Use the standardized utilities for loading and validating configuration:

```python
from utils.config_utils import validate_config_file
from utils.helpers import load_config_as_model, map_config_key_to_model_field
from tco_model.schemas import VehicleInfoSchema
from tco_model.models import BETParameters

# Validate against schema
is_valid, errors = validate_config_file("config/vehicle.yaml", VehicleInfoSchema)

# Load with field mapping
params = load_config_as_model("config/vehicle.yaml", BETParameters)

# Map between config keys and model fields
model_field = map_config_key_to_model_field("energy_consumption.base_rate_kwh_per_km")
config_key = map_model_field_to_config_key("energy_consumption.base_rate")
```

## Adding New Components

When adding new cost components:

1. Add the field to the `NPVCosts` and `AnnualCosts` classes
2. Update the `total` properties to include the new component
3. Add the component to the `UI_COMPONENT_KEYS` if it should be displayed in the UI
4. Add appropriate entry to `UI_COMPONENT_MAPPING` with color and display order
5. Update component tests to include the new component
```

### Step 5: Update README.md

Update the project's README.md file to reflect the standardized field names:

```markdown
# Australian Heavy Vehicle TCO Modeller

## Overview

This project provides tools for calculating the Total Cost of Ownership (TCO) for heavy vehicles in Australia, with a focus on comparing Battery Electric Trucks (BETs) with diesel alternatives.

## Key Changes

We've recently standardized field names and component access patterns throughout the codebase. Key changes include:

- Renamed `npv_total` to `total_tco` for clarity
- Renamed `lcod_per_km` to `lcod` to follow naming conventions
- Added an `AnnualCostsCollection` class with improved access patterns
- Implemented a consistent strategy pattern with a factory
- Standardized component access across the codebase

See the [Migration Guide](docs/migration_guide.md) for details on transitioning to the new field names.

## Usage

### Basic TCO Calculation

```python
from tco_model.calculator import TCOCalculator
from tco_model.models import ScenarioInput

# Load scenario input
scenario = ScenarioInput.from_file("scenarios/example.yaml")

# Calculate TCO
calculator = TCOCalculator()
result = calculator.calculate(scenario)

# Access results
print(f"Total TCO: {result.total_tco}")
print(f"LCOD: {result.lcod} AUD/km")

# Access cost components
energy_cost = result.npv_costs.energy
maintenance_cost = result.npv_costs.maintenance
```

### Comparing Scenarios

```python
# Calculate two scenarios
bet_result = calculator.calculate(bet_scenario)
diesel_result = calculator.calculate(diesel_scenario)

# Compare results
comparison = calculator.compare_results(bet_result, diesel_result)

# Access comparison results
print(f"TCO difference: {comparison.tco_difference}")
print(f"Percentage difference: {comparison.tco_percentage}%")

# Identify cheaper option
cheaper_index = comparison.cheaper_option
cheaper_scenario = comparison.scenario_1 if cheaper_index == 1 else comparison.scenario_2
print(f"Cheaper option: {cheaper_scenario.vehicle_name}")

# Check if there's a payback period
if comparison.payback_year is not None:
    print(f"Payback in year {comparison.payback_year + 1}")
```

## Documentation

- [Developer Guide](docs/developer_guide.md)
- [Migration Guide](docs/migration_guide.md)
- [API Documentation](docs/api.md)
```

### Step 6: Remove Deprecated Code

After sufficient transition time, remove deprecated property aliases:

```python
class TCOOutput(BaseModel):
    """Output of TCO calculation."""
    scenario_name: str = Field(..., description="Name of the scenario")
    vehicle_name: str = Field(..., description="Name of the vehicle")
    vehicle_type: VehicleType = Field(..., description="Type of vehicle")
    analysis_period_years: int = Field(..., ge=1, description="Analysis period in years")
    total_distance_km: float = Field(..., gt=0, description="Total distance over analysis period")
    annual_costs: AnnualCostsCollection = Field(..., description="Annual breakdown of costs")
    npv_costs: NPVCosts = Field(..., description="Net Present Value of costs")
    total_tco: float = Field(..., description="Total cost of ownership (NPV)")
    lcod: float = Field(..., description="Levelized Cost of Driving per km")
    total_nominal_cost: float = Field(..., description="Total nominal cost over analysis period")
    calculation_date: date = Field(default_factory=date.today, description="Date of calculation")
    _scenario: Optional[ScenarioInput] = PrivateAttr(default=None)
    
    @property
    def scenario(self) -> Optional[ScenarioInput]:
        """Return the original scenario for testing purposes."""
        return self._scenario
    
    # All existing properties remain
    # Temporary compatibility aliases have been removed
```

### Step 7: Create Automated Config Checker Script

Add a script to check all configuration files for consistency:

```python
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
```

### Step 8: Create Automated Field Usage Checker

Add a script to find any remaining direct references to renamed fields:

```python
#!/usr/bin/env python
"""
Field reference checker script.

This script scans the codebase for direct references to renamed fields
and reports any remaining usages.
"""

import os
import sys
import re
from pathlib import Path
import argparse
from typing import Dict, List, Set, Tuple

# Constants
RENAMED_FIELDS = {
    "npv_total": "total_tco",
    "lcod_per_km": "lcod",
    "npv_difference": "tco_difference",
    "npv_difference_percentage": "tco_percentage"
}

# Exclude patterns (e.g., tests, compatibility aliases)
EXCLUDE_PATTERNS = [
    r"test_.*\.py",
    r".*_test\.py",
    r"@property\s+def\s+(npv_total|lcod_per_km|npv_difference|npv_difference_percentage)",
    r"warnings\.warn\("
]

def find_field_references(
    directory: Path, 
    renamed_fields: Dict[str, str],
    exclude_patterns: List[str]
) -> Dict[str, Dict[str, List[Tuple[int, str]]]]:
    """
    Find direct references to renamed fields in Python files.
    
    Args:
        directory: Root directory to scan
        renamed_fields: Dictionary mapping old field names to new ones
        exclude_patterns: Regex patterns to exclude from checking
        
    Returns:
        Dict mapping field names to file paths and line information
    """
    results = {field: {} for field in renamed_fields}
    compiled_excludes = [re.compile(pattern) for pattern in exclude_patterns]
    
    for py_file in directory.glob("**/*.py"):
        # Skip files matching exclude patterns
        if any(pattern.search(str(py_file)) for pattern in compiled_excludes):
            continue
            
        with open(py_file, 'r', encoding='utf-8') as f:
            try:
                lines = f.readlines()
                
                for i, line in enumerate(lines, 1):
                    # Skip lines matching exclude patterns
                    if any(pattern.search(line) for pattern in compiled_excludes):
                        continue
                        
                    for old_field, new_field in renamed_fields.items():
                        # Look for direct references to old field names
                        # Avoid false positives by checking for word boundaries
                        pattern = fr'\b{re.escape(old_field)}\b'
                        if re.search(pattern, line):
                            rel_path = str(py_file.relative_to(directory))
                            if rel_path not in results[old_field]:
                                results[old_field][rel_path] = []
                            results[old_field][rel_path].append((i, line.strip()))
            except UnicodeDecodeError:
                # Skip binary files
                continue
    
    return results


def main():
    """Main entry point for the field reference checker script."""
    parser = argparse.ArgumentParser(
        description="Check for direct references to renamed fields"
    )
    parser.add_argument("directory", nargs="?", default=".",
                        help="Directory to scan (default: current directory)")
    args = parser.parse_args()
    
    directory = Path(args.directory)
    if not directory.exists() or not directory.is_dir():
        print(f"Error: {args.directory} is not a valid directory")
        sys.exit(1)
    
    print(f"Scanning for field references in {directory}...")
    references = find_field_references(directory, RENAMED_FIELDS, EXCLUDE_PATTERNS)
    
    found_references = False
    for old_field, files in references.items():
        if files:
            found_references = True
            new_field = RENAMED_FIELDS[old_field]
            print(f"\nFound references to '{old_field}' (renamed to '{new_field}'):")
            
            for file_path, lines in files.items():
                print(f"  {file_path}:")
                for line_num, line_text in lines:
                    print(f"    Line {line_num}: {line_text}")
    
    if not found_references:
        print("\nNo direct references to renamed fields found!")
        sys.exit(0)
    else:
        print("\nFound references to renamed fields. These should be updated.")
        sys.exit(1)


if __name__ == "__main__":
    main()
```

## Results and Benefits

- Clear migration path for developers
- Comprehensive documentation of the new conventions
- Automated tools to ensure consistency
- Gradual deprecation process for backward compatibility
- Removal of deprecated code after sufficient transition

## Acceptance Criteria

- [ ] Migration guide is created and distributed
- [ ] Developer guide is updated with new conventions
- [ ] README.md reflects the new field naming
- [ ] Automated config checker script is implemented
- [ ] Field reference checker script is implemented
- [ ] Deprecation warnings are in place
- [ ] Plan for removing deprecated code is established 