# TCO Model Developer Guide

This guide explains how to work with the TCO model codebase following our standardized naming conventions and patterns.

## Vehicle Type Standardization

### Canonical Vehicle Type Enum

The codebase uses a canonical `VehicleType` enum from `tco_model.schemas` for vehicle type identification:

```python
from tco_model.schemas import VehicleType

# Use enum values directly
electric_vehicle = VehicleType.BATTERY_ELECTRIC
diesel_vehicle = VehicleType.DIESEL

# For string comparisons, use .value
if vehicle.type == VehicleType.BATTERY_ELECTRIC.value:
    # Handle electric vehicle logic
elif vehicle.type == VehicleType.DIESEL.value:
    # Handle diesel vehicle logic
```

### Correct Usage Patterns

✅ DO:
- Import `VehicleType` from `tco_model.schemas`
- Use `VehicleType.BATTERY_ELECTRIC` and `VehicleType.DIESEL` directly
- Compare string values with `VehicleType.BATTERY_ELECTRIC.value` or `VehicleType.DIESEL.value`
- Use the canonical values in database fields, API responses, and configuration files

❌ DON'T:
- Import `VehicleType` from `tco_model.models` (deprecated)
- Use string literals like `"bet"`, `"ice"`, `"battery_electric"`, `"diesel"`
- Use the `normalize_vehicle_type` function (deprecated)
- Use `VehicleType.BET` or `VehicleType.ICE` aliases (deprecated)

### CSS Class Mapping

For backward compatibility, the codebase uses a mapping function to translate between canonical VehicleType enum values and CSS class names:

```python
def get_css_class_for_vehicle_type(vehicle_type: str) -> str:
    """
    Convert canonical vehicle type to CSS class name for backward compatibility.
    
    Args:
        vehicle_type: Vehicle type (canonical value from VehicleType.value)
        
    Returns:
        CSS class name (legacy format)
    """
    if vehicle_type == VehicleType.BATTERY_ELECTRIC.value:
        return "bet"
    elif vehicle_type == VehicleType.DIESEL.value:
        return "diesel"
    return vehicle_type  # Fallback to original value for other types
```

Use this function when creating UI components that need CSS classes:

```python
# Get canonical vehicle type
vehicle_type = get_vehicle_type(state_prefix)  # Returns "battery_electric" or "diesel"

# Get legacy CSS class name
css_class = get_css_class_for_vehicle_type(vehicle_type)  # Returns "bet" or "diesel"

# Use the CSS class in UI components
with UIComponentFactory.create_card("Component Title", component_id, css_class):
    # Component content
```

In a future release, the CSS classes will be updated to match the canonical enum values.

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

### CSS Classes and Styling

When working with vehicle-specific styling, the codebase currently uses CSS classes with legacy naming 
like `.vehicle-bet` and `.vehicle-diesel`. These will be updated in a future release to match the canonical 
enum values (`.vehicle-battery_electric` and `.vehicle-diesel`).

For now, continue using the existing CSS class naming patterns until a full CSS refactoring is performed:

```python
# Current pattern for UI components
if vehicle_type == VehicleType.BATTERY_ELECTRIC.value:
    # Still use "bet" for CSS classes
    with UIComponentFactory.create_card("Battery Parameters", card_id, "bet"):
        # Component content
else:
    # Use "diesel" for CSS classes
    with UIComponentFactory.create_card("Engine Parameters", card_id, "diesel"):
        # Component content
```

> **Note:** The VehicleType standardization project has been completed. All code now uses the canonical VehicleType enum from tco_model.schemas. The following section is kept for historical reference only.

**Legacy approach (deprecated and removed):**
- Import `VehicleType` from `tco_model.models` (deprecated)
- Use `VehicleType.BET` or `VehicleType.ICE` aliases (deprecated) 