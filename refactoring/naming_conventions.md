# TCO Model Field Naming Conventions

This document establishes standard naming conventions and terminology for the Australian Heavy Vehicle TCO Modeller project. It provides canonical field names, descriptions, and mappings to ensure consistency across the codebase.

## Core Terminology

### General Terms

| Term | Definition | 
|------|------------|
| TCO | Total Cost of Ownership - The comprehensive sum of all costs associated with acquiring and operating a vehicle over its lifetime, expressed in present value terms |
| LCOD | Levelized Cost of Driving - The per-kilometer cost of ownership, calculated by dividing the TCO by the total lifetime distance traveled |
| NPV | Net Present Value - The current value of future cash flows, accounting for the time value of money using a discount rate |
| BET | Battery Electric Truck - A heavy vehicle powered by electric batteries |
| ICE | Internal Combustion Engine - A traditional engine powered by fossil fuels (e.g., diesel) |

### Vehicle Types

| Term | Definition | Enum Value |
|------|------------|------------|
| BET | Battery Electric Truck | `VehicleType.BATTERY_ELECTRIC` |
| ICE | Internal Combustion Engine (Diesel) | `VehicleType.DIESEL` |

### Cost Categories

| Term | Definition |
|------|------------|
| Acquisition Costs | Costs related to purchasing the vehicle (initial capital outlay or loan payments) |
| Energy Costs | Costs of fuel or electricity used to power the vehicle |
| Maintenance Costs | Regular and corrective maintenance expenses to keep the vehicle operational |
| Infrastructure Costs | Costs of supporting infrastructure (e.g., charging equipment for BETs) |
| Battery Replacement | Costs associated with replacing batteries during the vehicle's lifetime |
| Insurance | Costs of vehicle insurance |
| Registration | Government registration and licensing fees |
| Carbon Tax | Taxes or levies applied to carbon emissions |
| Other Taxes | Additional taxes and government charges |
| Residual Value | The remaining value of the vehicle at the end of the analysis period |

## Field Naming Conventions

### General Naming Rules

1. **Be Explicit and Descriptive**
   - Names should clearly indicate their purpose and meaning
   - Avoid ambiguous abbreviations or overly terse names

2. **Units in Field Names**
   - Include units in field names when they represent physical quantities:
     - Distance: `_km`, `_m`
     - Power: `_kw`, `_hp`
     - Energy: `_kwh`
     - Currency: No suffix (AUD is default currency)
     - Time: `_years`, `_months`, `_days`, `_hours`
     - Weight: `_kg`, `_tonnes`
     - Rates: `_per_km`, `_per_year`, `_per_kwh`

3. **Consistent Casing**
   - Use `snake_case` for field names and variable names
   - Use `PascalCase` for class names and enum values
   - Use `UPPER_SNAKE_CASE` for constants

4. **Consistent Boolean Naming**
   - Boolean fields should use prefixes like `is_`, `has_`, or `requires_`
   - Example: `is_urban_operation`, `has_regenerative_braking`, `requires_overnight_charging`

### TCOOutput Class

| Current Field | Canonical Field | Change Required | Description | Data Type |
|---------------|----------------|----------------|-------------|-----------|
| `npv_total` | `total_tco` | Yes | Total cost of ownership (NPV) | float |
| `lcod_per_km` | `lcod` | Yes | Levelized cost of driving per kilometer | float |
| *missing* | `scenario` | Yes - Add | Reference to the original input scenario | Optional[ScenarioInput] |
| `annual_costs` | `annual_costs` | Structure change | Annual breakdown of costs | AnnualCostsCollection |
| `npv_costs` | `npv_costs` | No | Net present value breakdown of costs | NPVCosts |
| `total_nominal_cost` | `total_nominal_cost` | No | Total nominal cost without NPV adjustment | float |
| `calculation_date` | `calculation_date` | No | Date of the calculation | date |
| `scenario_name` | `scenario_name` | No | Name of the scenario | str |
| `vehicle_name` | `vehicle_name` | No | Name of the vehicle | str |
| `vehicle_type` | `vehicle_type` | No | Type of vehicle (BET or diesel) | VehicleType |
| `analysis_period_years` | `analysis_period_years` | No | Analysis period in years | int |
| `total_distance_km` | `total_distance_km` | No | Total distance over analysis period | float |

### ComparisonResult Class

| Current Field | Canonical Field | Change Required | Description | Data Type |
|---------------|----------------|----------------|-------------|-----------|
| `npv_difference` | `tco_difference` | Yes | Difference in TCO between scenarios | float |
| `npv_difference_percentage` | `tco_percentage` | Yes | Percentage difference in TCO | float |
| *missing* | `component_differences` | Yes - Add | Differences in cost components | Dict[str, float] |
| *missing* | `cheaper_option` | Yes - Add | Index of the cheaper scenario (1 or 2) | int |
| `lcod_difference` | `lcod_difference` | No | Difference in LCOD between scenarios | float | 
| `lcod_difference_percentage` | `lcod_difference_percentage` | No | Percentage difference in LCOD | float |
| `payback_year` | `payback_year` | No | Year when the more expensive option breaks even | Optional[int] |
| `scenario_1` | `scenario_1` | No | First scenario being compared | TCOOutput |
| `scenario_2` | `scenario_2` | No | Second scenario being compared | TCOOutput |

### Component Access Patterns

The model should provide consistent ways to access cost components with the following patterns:

1. **Direct Property Access**
   - Access individual components directly: `result.npv_costs.acquisition`
   - Access combined components via property: `result.npv_costs.insurance_registration`

2. **Standard Access Methods**
   - Use consistent helper functions for component access:
     - `get_component_value(result, "component_name")` for NPV costs
     - `get_annual_component_value(result, "component_name", year)` for annual costs

3. **Combined Component Calculation**
   - Combined components should be consistently calculated as the sum of their parts
   - Always use the utility functions or direct property access, never recalculate manually

4. **Annual Cost Access Patterns**
   - Support dual access patterns for annual costs:
     - Index-based access: `costs[year_index]` returns the AnnualCosts for a specific year
     - Attribute access for collections: `costs.total` returns a list of total costs for all years
     - Attribute access for components: `costs.acquisition` returns a list of acquisition costs for all years

### AnnualCosts Restructuring

The `annual_costs` field in TCOOutput needs to be restructured to support both list-like access and attribute access to collections of cost components.

| Current Structure | New Structure | Description |
|------------------|---------------|-------------|
| `List[AnnualCosts]` | `AnnualCostsCollection` | Custom collection class that wraps the list of AnnualCosts objects |

The `AnnualCostsCollection` should provide these access patterns:
- Index-based access: `costs[year_index]` returns the AnnualCosts for a specific year
- Attribute access for collections: `costs.total` returns a list of total costs for all years
- Attribute access for components: `costs.acquisition` returns a list of acquisition costs for all years
- Combined component access: `costs.insurance_registration` returns a list of combined costs for all years

## UI Specific Terminology

### Combined Cost Categories

The UI layer uses combined cost categories for visualization that differ from the model's internal structure:

| UI Component Key | UI Display Label | Source Component(s) | 
|-----------------|-----------------|-------------------|
| `acquisition` | "Acquisition Costs" | acquisition |
| `energy` | "Energy Costs" | energy |
| `maintenance` | "Maintenance & Repair" | maintenance |
| `infrastructure` | "Infrastructure" | infrastructure |
| `battery_replacement` | "Battery Replacement" | battery_replacement |
| `insurance_registration` | "Insurance & Registration" | insurance + registration |
| `taxes_levies` | "Taxes & Levies" | carbon_tax + other_taxes |
| `residual_value` | "Residual Value" | residual_value |

These combined categories are used in the `COMPONENT_KEYS` and `COMPONENT_LABELS` constants in `ui/results/utils.py`.

### UI Helper Functions

Consistent naming conventions for UI helper functions:

| Function | Purpose | Naming Convention |
|----------|---------|-------------------|
| `get_component_value` | Get NPV cost component values | Keep as is |
| `get_annual_component_value` | Get annual cost component values | Keep as is |
| `validate_tco_results` | Validate TCO result objects | Keep as is |
| `get_ui_component_label` | Get UI display label for a component key | Keep as is |
| `get_model_components_for_ui_component` | Get model components for a UI component | Keep as is |

### UI Result Component Naming

Chart and display components should use consistent terminology:

| UI Element | Purpose | Standard Naming |
|------------|---------|-----------------|
| Summary tables | Display TCO summary data | "TCO Summary" |
| Cost breakdowns | Display cost component details | "Cost Breakdown", "Component Details" |
| Annual costs | Display year-by-year costs | "Annual Costs" |
| Cumulative costs | Display costs over time | "Cumulative TCO" |
| Comparison results | Display comparison results | "Comparison Results" |

## Configuration Files Terminology

### General Configuration File Structure

All configuration files should follow a consistent structure with these sections:

| Section | Content | Example |
|---------|---------|---------|
| `vehicle_info` | Basic vehicle information | type, category, name |
| `purchase` | Purchase cost information | base_price_2025, annual_price_decrease_real |
| `performance` | Vehicle performance parameters | max_payload_tonnes, range_km |
| `energy_consumption` or `fuel_consumption` | Energy use parameters | base_rate_kwh_per_km or base_rate_l_per_km |
| `maintenance` | Maintenance parameters | cost_per_km, detailed_costs |
| `residual_values` | Residual value parameters | year_5, year_10, year_15 |

### Standardized Configuration Keys

All configuration keys should:
1. Use snake_case
2. Include units in the name when representing physical quantities
3. Use consistent prefixes for related fields
4. Follow a hierarchical structure with dot notation

### Vehicle Configuration Files

Vehicle configuration files use a different structure and naming convention than the model classes:

| Config File Key | Model Class Property | Description |
|----------------|---------------------|-------------|
| `vehicle_info.type` | `vehicle.type` | Vehicle type (battery_electric, diesel) |
| `vehicle_info.category` | `vehicle.category` | Vehicle category (rigid, articulated) |
| `vehicle_info.name` | `vehicle.name` | Vehicle name |
| `purchase.base_price_2025` | `vehicle.purchase_price` | Base purchase price |
| `battery.capacity_kwh` | `vehicle.battery.capacity_kwh` | Battery capacity in kWh |
| `energy_consumption.base_rate_kwh_per_km` | `vehicle.energy_consumption.base_rate` | Energy consumption rate |
| `maintenance.cost_per_km` | `vehicle.maintenance.cost_per_km` | Maintenance cost per km |
| `maintenance.detailed_costs.annual_fixed_min` | `vehicle.maintenance.annual_fixed_min` | Annual fixed maintenance |

### BET-Specific Configuration Keys

| Config File Key | Model Class Property | Description |
|----------------|---------------------|-------------|
| `battery.capacity_kwh` | `vehicle.battery.capacity_kwh` | Battery capacity in kilowatt-hours |
| `battery.usable_capacity_percentage` | `vehicle.battery.usable_capacity_percentage` | Percentage of battery capacity that is usable |
| `charging.max_charging_power_kw` | `vehicle.charging.max_charging_power_kw` | Maximum charging power in kilowatts |
| `charging.charging_efficiency` | `vehicle.charging.charging_efficiency` | Charging efficiency (grid to battery) |
| `charging.charging_strategy` | `vehicle.charging.strategy` | Default charging strategy |

### Diesel-Specific Configuration Keys

| Config File Key | Model Class Property | Description |
|----------------|---------------------|-------------|
| `engine.power_kw` | `vehicle.engine.power_kw` | Engine power in kilowatts |
| `engine.displacement_litres` | `vehicle.engine.displacement_litres` | Engine displacement in litres |
| `engine.euro_emission_standard` | `vehicle.engine.euro_emission_standard` | Euro emission standard of the engine |
| `fuel_consumption.base_rate_l_per_km` | `vehicle.fuel_consumption.base_rate` | Base fuel consumption in litres/km |

### Economic Parameters

Economic parameter files use a different structure than the model classes:

| Config File Key | Model Class Property | Description |
|----------------|---------------------|-------------|
| `general.discount_rate_real` | `economic.discount_rate_real` | Real discount rate |
| `general.inflation_rate` | `economic.inflation_rate` | Inflation rate |
| `financing.default_method` | `financing.method` | Financing method |
| `energy_prices.electricity` | Used in strategies | Electricity prices by year and type |
| `energy_prices.diesel.scenarios` | Used in strategies | Diesel price scenarios |
| `carbon_pricing.carbon_tax_rate_2025` | `economic.carbon_tax_rate_aud_per_tonne` | Carbon tax rate |

## Strategies and Models Terminology

### Cost Calculation Functions vs Strategy Classes

The codebase uses two different patterns for cost calculations, which should be consolidated to use the Strategy pattern consistently:

1. Direct functions in `costs.py`:
   - `calculate_acquisition_costs`
   - `calculate_energy_costs`
   - `calculate_maintenance_costs`
   - etc.

2. Strategy classes in `strategies.py`:
   - `EnergyConsumptionStrategy`
   - `MaintenanceStrategy`
   - `BatteryReplacementStrategy`
   - etc.

### Strategy Class Naming Conventions

All strategy classes should follow these naming conventions:

1. **Base Strategy Classes**
   - Abstract base classes should be named: `{Function}Strategy`
   - Example: `EnergyConsumptionStrategy`, `MaintenanceStrategy`

2. **Vehicle-Specific Strategies**
   - Add vehicle type prefix: `{VehiclePrefix}{Function}Strategy`
   - Example: `BETEnergyConsumptionStrategy`, `DieselMaintenanceStrategy`

3. **Implementation-Specific Strategies**
   - Add implementation approach: `{Implementation}{Function}Strategy`
   - Example: `DistanceBasedMaintenanceStrategy`, `DegradationBasedBatteryReplacementStrategy`

| Strategy Category | Naming Pattern | Examples |
|-------------------|---------------|----------|
| Base Strategies | `{Function}Strategy` | `EnergyConsumptionStrategy`, `MaintenanceStrategy` |
| Vehicle-Specific | `{VehiclePrefix}{Function}Strategy` | `BETEnergyConsumptionStrategy`, `DieselMaintenanceStrategy` |
| Implementation | `{Implementation}{Function}Strategy` | `DistanceBasedMaintenanceStrategy`, `ValueBasedInsuranceStrategy` |

### Strategy Class Method Naming

Strategy classes should use consistent method names:

| Method Type | Canonical Method Name | Purpose |
|------------|---------------------|---------|
| Cost Calculation | `calculate_costs(scenario, year)` | Calculate costs for a specific year |
| Consumption Calculation | `calculate_consumption(scenario, year)` | Calculate consumption for a specific year |
| Residual Value Calculation | `calculate_residual_value(scenario, year)` | Calculate residual value for a specific year |
| Helper Methods | `get_calendar_year(year)` | Consistent helper methods across all strategies |

### Strategy Factory Functions

Factory functions that return strategies should follow these naming conventions:

| Function Purpose | Naming Pattern | Example |
|-----------------|---------------|---------|
| Get Strategy | `get_{function}_strategy()` | `get_energy_consumption_strategy()` |
| Get Vehicle-Specific Strategy | `get_{function}_strategy(vehicle_type)` | `get_maintenance_strategy(vehicle_type)` |

### Parameter Model Classes

Parameter models should follow consistent naming conventions:

| Model Category | Naming Pattern | Examples |
|----------------|---------------|----------|
| Base Parameters | `{Function}Parameters` | `EnergyConsumptionParameters`, `MaintenanceParameters` |
| Vehicle-Specific | `{VehiclePrefix}Parameters` | `BETParameters`, `DieselParameters` |
| Component-Specific | `{Component}Parameters` | `BatteryParameters`, `ChargingParameters`, `EngineParameters` |

### Default Value Standardization

Default values should be centralized in the `terminology.py` module and follow these conventions:

1. **Constant naming**: `DEFAULT_{COMPONENT}_{PARAMETER}`
   - Example: `DEFAULT_BET_CONSUMPTION_RATE`, `DEFAULT_DIESEL_PRICE`

2. **Grouped default values**: Use nested dictionaries for related defaults
   - Example: `BET_DEFAULTS`, `DIESEL_DEFAULTS`, `ECONOMIC_DEFAULTS`

3. **Units in constant names**: Include units in the constant name for clarity
   - Example: `DEFAULT_BATTERY_CAPACITY_KWH`, `DEFAULT_CHARGING_POWER_KW`

## Vehicle Transformation Functions

The transformation functions in vehicles.py contain multiple field mappings and fallbacks, which need standardization:

| Function | Purpose | Naming Convention Issue |
|----------|---------|----------------------|
| `transform_bet_yaml_to_model` | Convert BET YAML to model | Multiple fallback field names with inconsistent naming |
| `transform_diesel_yaml_to_model` | Convert Diesel YAML to model | Multiple fallback field names with inconsistent naming |

### Standardized Transformation Functions

Replace with consistent transformation functions:

| New Function | Purpose | Naming Standard |
|--------------|---------|----------------|
| `transform_vehicle_config(config, vehicle_type)` | Generic transformation function | Descriptive of purpose |
| `get_nested_config_value(config, key_path, default)` | Get value from nested config | Descriptive of action |
| `set_nested_model_value(model_data, key_path, value)` | Set value in nested model | Descriptive of action |

### Field Mapping Standardization

Key inconsistencies in transformation functions that need standardization:

| Primary Field | Fallback Fields | Standardization Needed |
|--------------|----------------|----------------------|
| `base_rate_kwh_per_km` | `base_rate` | Standardize on `base_rate_kwh_per_km` with units |
| `power_kw` | `power` | Standardize on `power_kw` with units |
| `base_rate_l_per_km` | `base_rate` | Standardize on `base_rate_l_per_km` with units |

## Calculation Definitions

### Total Cost of Ownership (TCO)

The TCO is calculated as the sum of all discounted costs over the analysis period:

```
total_tco = npv(acquisition_costs + energy_costs + maintenance_costs + 
                infrastructure_costs + battery_replacement_costs + 
                insurance_costs + registration_costs + 
                carbon_tax + other_taxes - residual_value)
```

### Levelized Cost of Driving (LCOD)

The LCOD is calculated by dividing the total TCO by the total distance traveled:

```
lcod = total_tco / total_distance_km
```

Where:
- `total_tco` is the TCO in present value terms
- `total_distance_km` is the total distance traveled over the analysis period

## Implementation Guidelines

### General Refactoring Approach

When implementing these naming conventions, follow this sequence:

1. **Data Models First**: Update core model classes with new field names and property aliases
2. **Add Compatibility Layer**: Ensure backward compatibility with property aliases during transition
3. **Update Calculation Logic**: Update calculator methods to use new field names
4. **Update UI Components**: Modify UI components to use new field names and helper functions
5. **Update Configuration Handling**: Standardize configuration loading and transformation
6. **Update Tests**: Ensure all tests use the new field names and conventions
7. **Remove Compatibility Layer**: After full transition, remove deprecated aliases

### Refactoring Best Practices

1. **Incremental Changes**: Make smaller, focused pull requests to minimize risk
2. **Tests First**: Update tests before or alongside code changes
3. **Run Tests Often**: Verify each change with test runs
4. **Consistent Documentation**: Update docstrings and comments to use new terminology
5. **Clear Deprecation Warnings**: Use warnings.warn for deprecated field access

### Clean Code Guidelines

Follow these guidelines for all code changes:

1. **Self-Documenting Code**: Use clear names that explain purpose without comments
2. **Single Responsibility**: Each function and class should have one clear purpose
3. **DRY (Don't Repeat Yourself)**: Extract repeated logic into helper functions
4. **Consistent Patterns**: Use the same patterns throughout the codebase
5. **No Magic Values**: Use named constants for all fixed values

### Documentation Updates

When implementing naming changes, update these documentation sources:

1. **Docstrings**: Update all function and class docstrings to use new terminology
2. **README.md**: Update project documentation with new naming conventions
3. **API Documentation**: Update any API docs that reference the changed fields
4. **Code Comments**: Update comments to use the new terminology
5. **User Guide**: Update user-facing documentation with new field names

### Verification Steps

After each phase of implementation, verify:

1. **Test Coverage**: All tests pass and maintain coverage
2. **Code Linting**: No style or linting errors
3. **Documentation Accuracy**: Documentation matches the implementation
4. **UI Functionality**: UI components display correctly with new field names
5. **Performance Impact**: No negative performance impact from refactoring 