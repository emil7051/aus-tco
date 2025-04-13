# Phase 3: UI Components and Configuration Updates

This document outlines the implementation steps for Phase 3 of the field refactoring project, focusing on standardizing UI component access and configuration file handling.

## Goals

- Update UI helper functions to use standardized component access
- Standardize configuration file loading and transformation
- Implement consistent field mapping between config files and models
- Ensure configuration validation and defaults handling

## Implementation Steps

### Step 1: Update UI Helper Functions

Modify the helper functions in `ui/results/utils.py` to use the new collection and property structure:

```python
from typing import Any, Dict, List, Optional, Union
from tco_model.models import TCOOutput, ComparisonResult, AnnualCostsCollection
from tco_model.terminology import (
    UI_COMPONENT_MAPPING, 
    UI_COMPONENT_KEYS, 
    UI_COMPONENT_LABELS,
    get_component_value as get_model_component_value
)

def get_component_value(result: TCOOutput, component: str) -> float:
    """
    Get component NPV value from a result using the standardized access pattern.
    
    Args:
        result: TCO result object containing the cost data
        component: Component key to access
        
    Returns:
        float: The component value in AUD
        
    Example:
        >>> energy_cost = get_component_value(result, "energy")
        >>> insurance_reg = get_component_value(result, "insurance_registration")
    """
    if not result or not result.npv_costs:
        return 0.0
    
    # Use the standardized access function from terminology
    return get_model_component_value(result.npv_costs, component)


def get_annual_component_value(result: TCOOutput, component: str, year: int) -> float:
    """
    Get component value for a specific year using the standardized access pattern.
    
    Args:
        result: TCO result object containing the annual costs data
        component: Component key to access
        year: Year index (0-based)
        
    Returns:
        float: The component value for the specified year in AUD
        
    Example:
        >>> # Get energy costs for year 3
        >>> energy_cost_year_3 = get_annual_component_value(result, "energy", 3)
    """
    if not result or not result.annual_costs or year >= len(result.annual_costs):
        return 0.0
    
    # Use the standardized access function from terminology
    return get_model_component_value(result.annual_costs, component, year)


def get_component_color(component: str) -> str:
    """
    Get the standard color for a component.
    
    Args:
        component: Component key
        
    Returns:
        str: Color hex code for the component
    """
    # Constant for default color
    DEFAULT_COLOR = "#333333"  # Default gray
    
    if component in UI_COMPONENT_MAPPING:
        return UI_COMPONENT_MAPPING[component].get("color", DEFAULT_COLOR)
    return DEFAULT_COLOR


def get_component_display_order(component: str) -> int:
    """
    Get the standard display order for a component.
    
    Args:
        component: Component key
        
    Returns:
        int: Display order value (1-based)
    """
    # Constant for default display order
    DEFAULT_DISPLAY_ORDER = 999  # Default to end
    
    if component in UI_COMPONENT_MAPPING:
        return UI_COMPONENT_MAPPING[component].get("display_order", DEFAULT_DISPLAY_ORDER)
    return DEFAULT_DISPLAY_ORDER
```

### Step 2: Update UI Display Components

Update references in display components to use the new field names:

```python
# In ui/results/summary.py
def display_comparison_summary(comparison: ComparisonResult):
    """
    Display a summary of the comparison between two scenarios.
    
    Args:
        comparison: The comparison result to display
    """
    st.subheader("TCO Comparison Summary")
    
    cols = st.columns(2)
    with cols[0]:
        st.metric(
            "Total TCO Difference",
            format_currency(comparison.tco_difference),  # Renamed from npv_difference
            format_percentage(comparison.tco_percentage / 100)  # Renamed from npv_difference_percentage
        )
    
    with cols[1]:
        st.metric(
            "LCOD Difference",
            f"{format_currency(comparison.lcod_difference)}/km",
            format_percentage(comparison.lcod_difference_percentage / 100)
        )
    
    # Use new cheaper_option property
    cheaper_index = comparison.cheaper_option
    cheaper_scenario = comparison.scenario_1 if cheaper_index == 1 else comparison.scenario_2
    
    st.info(f"The {cheaper_scenario.vehicle_name} has a lower total cost of ownership.")
    
    # Display payback year if available
    if comparison.payback_year is not None:
        payback_message = f"The higher initial cost is paid back in year {comparison.payback_year + 1}."
        st.success(payback_message)
```

### Step 3: Update Chart and Table Rendering Functions

Modify chart and table rendering functions to use the new standardized access functions:

```python
def create_cost_breakdown_chart(result: TCOOutput, height: int = 500) -> go.Figure:
    """
    Create a bar chart showing the cost breakdown for a TCO result.
    
    Args:
        result: TCO result to display
        height: Chart height in pixels
        
    Returns:
        plotly.graph_objects.Figure: The cost breakdown chart
    """
    # Get all component values using standardized access
    component_values = {
        component: get_component_value(result, component)
        for component in UI_COMPONENT_KEYS
    }
    
    # Sort components by display order
    sorted_components = sorted(
        UI_COMPONENT_KEYS,
        key=get_component_display_order
    )
    
    # Create sorted lists for chart
    components = [UI_COMPONENT_LABELS[c] for c in sorted_components]
    values = [component_values[c] for c in sorted_components]
    colors = [get_component_color(c) for c in sorted_components]
    
    # Create the chart
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=components,
        y=values,
        marker_color=colors,
        text=[format_currency(v) for v in values],
        textposition='auto'
    ))
    
    # Style the chart
    fig.update_layout(
        title=f"Cost Breakdown: {result.vehicle_name}",
        height=height,
        yaxis_title="NPV Cost (AUD)"
    )
    
    return fig
```

### Step 4: Create Configuration Validation Utility

Add a utility to validate configuration files against the schemas in `utils/config_utils.py`:

```python
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
```

### Step 5: Update Config Loading Functions

Modify the loading functions in `utils/helpers.py` to use the standardized terminology mappings:

```python
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
```

### Step 6: Add Config Field Mapping Utilities

Add utility functions to `utils/helpers.py` to map between config file keys and model fields:

```python
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
```

### Step 7: Create Config File Schema Standards

Define standardized schema for all configuration files across the system in `tco_model/schemas.py`:

```python
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, validator

class VehicleInfoSchema(BaseModel):
    """Schema for vehicle_info section in vehicle config files."""
    type: str = Field(..., description="Vehicle type (battery_electric or diesel)")
    category: str = Field(..., description="Vehicle category (rigid or articulated)")
    name: str = Field(..., description="Vehicle name/description")
    
    @validator('type')
    def validate_type(cls, v):
        valid_types = ["battery_electric", "diesel"]
        if v not in valid_types:
            raise ValueError(f"Type must be one of {valid_types}")
        return v
    
    @validator('category')
    def validate_category(cls, v):
        valid_categories = ["rigid", "articulated"]
        if v not in valid_categories:
            raise ValueError(f"Category must be one of {valid_categories}")
        return v


class PurchaseSchema(BaseModel):
    """Schema for purchase section in vehicle config files."""
    base_price_2025: float = Field(..., gt=0, description="Base purchase price in 2025")
    annual_price_decrease_real: float = Field(0.0, ge=0, le=0.5, description="Annual real decrease in price")


class EnergyConsumptionSchema(BaseModel):
    """Schema for energy_consumption section in BET config files."""
    base_rate_kwh_per_km: float = Field(..., gt=0, description="Base energy consumption in kWh/km")
    min_rate: float = Field(..., gt=0, description="Minimum energy consumption in kWh/km")
    max_rate: float = Field(..., gt=0, description="Maximum energy consumption in kWh/km")
    load_adjustment_factor: float = Field(0.15, ge=0, description="Load adjustment factor")
    temperature_adjustment: Dict[str, float] = Field(default_factory=lambda: {
        "hot_weather": 0.05,
        "cold_weather": 0.15
    }, description="Temperature adjustments")
    regenerative_braking_efficiency: float = Field(0.65, ge=0, le=1, description="Regenerative braking efficiency")
    regen_contribution_urban: float = Field(0.2, ge=0, le=1, description="Regenerative braking contribution in urban environments")
    
    @validator('min_rate', 'max_rate')
    def validate_rates(cls, v, values):
        if 'base_rate_kwh_per_km' in values and v > values['base_rate_kwh_per_km'] * 2:
            raise ValueError("Rate should not be more than twice the base rate")
        return v
```

## Results and Benefits

- Consistent UI component access patterns
- Elimination of duplicated component mapping code
- Standardized configuration file loading and validation
- Clear mapping between configuration files and models
- Improved error handling for configuration issues
- Better documentation with examples

## Acceptance Criteria

- [ ] UI components use standardized access functions
- [ ] Chart and table rendering functions work with new field names
- [ ] Configuration files can be validated against schemas
- [ ] Configuration loading handles mapping between file keys and model fields
- [ ] Helper functions have clear documentation with examples
- [ ] Default values are applied consistently 