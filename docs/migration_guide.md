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