# Field Refactoring Analysis

This document provides a comprehensive analysis of all field references that need to be updated as part of the naming standardization effort. It includes specific file locations, line numbers, and required code changes to implement the canonical field names defined in the naming conventions document.

## TCOOutput Field References

### `npv_total` → `total_tco`

| File | Line Numbers | Context | Required Change |
|------|-------------|---------|----------------|
| `tco_model/models.py` | ~618 | Field definition | Rename field from `npv_total` to `total_tco` |
| `tco_model/calculator.py` | ~217 | Result creation | Update field name in TCOOutput creation |
| `tco_model/models.py` | ~661 | ComparisonResult creation | Update reference from `scenario_1.npv_total` to `scenario_1.total_tco` |
| `tco_model/models.py` | ~662 | ComparisonResult creation | Update reference from `scenario_2.npv_total` to `scenario_2.total_tco` |
| `tco_model/calculator.py` | ~222-224 | Compare results method | Update references from `npv_total` to `total_tco` |
| `tests/integration/test_calculator.py` | ~27, ~69, ~85, ~93, ~116, ~120, ~163 | Test assertions | Update assertions to use `total_tco` |
| `tests/integration/test_payback.py` | ~63, ~106, ~160, ~197, ~249, ~286 | Mock objects | Update field name in mock TCOOutput objects |
| `ui/results/display.py` | Various | Results display | Check and update any direct references |
| `ui/results/summary.py` | Various | Summary display | Check and update any direct references |
| `ui/results/detailed.py` | Various | Detailed display | Check and update any direct references |

### `lcod_per_km` → `lcod`

| File | Line Numbers | Context | Required Change |
|------|-------------|---------|----------------|
| `tco_model/models.py` | ~619 | Field definition | Rename field from `lcod_per_km` to `lcod` |
| `tco_model/calculator.py` | ~170 | LCOD calculation | Update variable name to match field |
| `tco_model/calculator.py` | ~217 | Result creation | Update field name in TCOOutput creation |
| `tco_model/models.py` | ~661 | ComparisonResult creation | Update references from `lcod_per_km` to `lcod` |
| `tco_model/models.py` | ~662 | ComparisonResult creation | Update references from `lcod_per_km` to `lcod` |
| `tco_model/calculator.py` | ~240-246 | LCOD difference calculation | Update all references |
| `tests/integration/test_calculator.py` | ~28, ~74, ~86, ~94, ~125, ~152, ~164, ~175 | Test assertions | Update references for consistency |
| `tests/integration/test_payback.py` | ~63, ~106, ~160, ~197, ~249, ~286 | Mock objects | Update field names in mock TCOOutput objects |
| `ui/results/summary.py` | ~35, ~45, ~55 | Display formatting | Update field references |
| `ui/results/display.py` | ~104 | Results display | Update field reference |
| `ui/results/detailed.py` | ~272-274, ~287-289 | Component chart | Update all references |

### Add `scenario` property

| File | Line Numbers | Context | Required Change |
|------|-------------|---------|----------------|
| `tco_model/models.py` | After TCOOutput class definition | Add property | Add `_scenario` private field and `scenario` property |
| `tco_model/calculator.py` | ~217 | Result creation | Set `_scenario = scenario` after creating TCOOutput |
| `tests/integration/test_calculator.py` | ~29, ~87 | Test assertions | Will now work with the new property |

### Annual Costs Collection

| File | Line Numbers | Context | Required Change |
|------|-------------|---------|----------------|
| `tco_model/models.py` | New | Add new class | Create `AnnualCostsCollection` wrapper class |
| `tco_model/models.py` | ~616 | Field definition | Update type annotation but keep field name |
| `tco_model/calculator.py` | ~170-196 | List creation | Modify to create AnnualCostsCollection |
| `tco_model/calculator.py` | ~217 | Result creation | Wrap annual_costs_list with AnnualCostsCollection |
| `tests/integration/test_calculator.py` | ~32-41, ~90, ~178 | Test assertions | Will now work with the new collection class |
| `tests/integration/test_payback.py` | Throughout | Mock objects | Update TCOOutput mock creation to use AnnualCostsCollection |

## ComparisonResult Field References

### `npv_difference` → `tco_difference`

| File | Line Numbers | Context | Required Change |
|------|-------------|---------|----------------|
| `tco_model/models.py` | ~649 | Field definition | Rename field from `npv_difference` to `tco_difference` |
| `tco_model/models.py` | ~687 | Result creation | Update field name in creation |
| `tco_model/calculator.py` | ~222 | Difference calculation | Update variable name to match field |
| `tco_model/calculator.py` | ~256 | Result creation | Update field name in ComparisonResult creation |
| `tests/integration/test_calculator.py` | ~109, ~116 | Test assertions | Update references for consistency |
| `ui/results/summary.py` | ~88 | Summary display | Update reference from `npv_difference` to `tco_difference` |

### `npv_difference_percentage` → `tco_percentage`

| File | Line Numbers | Context | Required Change |
|------|-------------|---------|----------------|
| `tco_model/models.py` | ~650 | Field definition | Rename field from `npv_difference_percentage` to `tco_percentage` |
| `tco_model/models.py` | ~688 | Result creation | Update field name in creation |
| `tco_model/calculator.py` | ~225-228 | Percentage calculation | Update variable name to match field |
| `tco_model/calculator.py` | ~256 | Result creation | Update field name in ComparisonResult creation |
| `tests/integration/test_calculator.py` | ~110, ~122 | Test assertions | Update assertions to use new field name |

### Add `component_differences` property

| File | Line Numbers | Context | Required Change |
|------|-------------|---------|----------------|
| `tco_model/models.py` | After ComparisonResult class | Add property | Add `component_differences` property method |
| `tests/integration/test_calculator.py` | ~112, ~127-132 | Test assertions | Will now work with the new property |
| `ui/results/summary.py` | ~88 | Summary table | Update to use new property |

### Add `cheaper_option` property

| File | Line Numbers | Context | Required Change |
|------|-------------|---------|----------------|
| `tco_model/models.py` | After ComparisonResult class | Add property | Add `cheaper_option` property method |
| `tests/integration/test_calculator.py` | ~113, ~135, ~137 | Test assertions | Will now work with the new property |
| `ui/results/summary.py` | ~49, ~59 | Summary display | Update to use new property |

## Cost Component References

### NPVCosts Class

| Current Structure | Required Change | Description |
|------------------|----------------|-------------|
| `insurance` + `registration` | Add `insurance_registration` property | Add a property that combines these two values |
| `carbon_tax` + `other_taxes` | Add `taxes_levies` property | Add a property that combines these two values |

### UI Helper Functions

| File | Line Numbers | Context | Required Change |
|------|-------------|---------|----------------|
| `ui/results/utils.py` | ~38-59 | `get_component_value` | Update to use new NPVCosts properties |
| `ui/results/utils.py` | ~78-94 | `get_annual_component_value` | Update to use new AnnualCostsCollection |

## Helper and Configuration Mappings

### Config Loading Functions

| File | Line Numbers | Context | Required Change |
|------|-------------|---------|----------------|
| `utils/helpers.py` | ~61-356 | Config loading functions | Update to use consistent terminology with model fields |
| `utils/helpers.py` | ~272-399 | Vehicle parameter loading | Add mapping from config field names to model field names |
| `utils/helpers.py` | ~415-529 | Streamlit state management | Update state keys to use consistent terminology |

### Test Fixtures

| File | Line Numbers | Context | Required Change |
|------|-------------|---------|----------------|
| `tests/conftest.py` | ~41-105 | Parameter fixtures | Ensure consistent field naming in test fixtures |
| `tests/conftest.py` | ~199-298 | Scenario fixtures | Update to use canonical property names |
| `tests/unit/test_models.py` | Throughout | Model tests | Update field references to use canonical names |
| `tests/unit/test_costs.py` | Throughout | Cost tests | Update field references to use canonical names |

### Config to Model Mapping

| Config File Structure | Model Field | Required Change |
|----------------------|------------|----------------|
| `vehicle_info.type` | `vehicle.type` | Add CONFIG_TO_MODEL_MAPPING in terminology.py |
| `purchase.base_price_2025` | `vehicle.purchase_price` | Add mapping in terminology.py |
| `energy_consumption.base_rate_kwh_per_km` | `vehicle.energy_consumption.base_rate` | Add mapping in terminology.py |
| Nested YAML structure | Flat Pydantic model | Create helper function to convert between formats |

## Combined UI Components vs. Model Components

### AnnualCosts Structure

| Current Implementation | AnnualCostsCollection Implementation | Required Change |
|----------------------|------------------------------------|----------------|
| List[AnnualCosts] | AnnualCostsCollection | Add combined properties to match UI components |
| No property for `insurance_registration` | Add `insurance_registration` property | Property returns insurance + registration |
| No property for `taxes_levies` | Add `taxes_levies` property | Property returns carbon_tax + other_taxes |

## Strategy Pattern Inconsistencies 

| Strategy Class | Direct Function | Required Change |
|---------------|----------------|----------------|
| `EnergyConsumptionStrategy` | `calculate_energy_costs` | Standardize to use one approach consistently |
| `MaintenanceStrategy` | `calculate_maintenance_costs` | Consider converting all to strategy pattern |
| `BatteryReplacementStrategy` | `calculate_battery_replacement_costs` | Update naming to be consistent |
| `FinancingStrategy` | `calculate_acquisition_costs` | Align naming between strategies and functions |

## Implementation Order

To minimize the risk of introducing bugs, implementation should follow this order:

1. **Model Classes**: Update field names in the data model classes first
2. **Properties**: Add properties to preserve backward compatibility (if needed)
3. **Calculator Logic**: Update field references in calculator and related functions
4. **Tests**: Update test assertions and fixtures to use new field names
5. **UI Components**: Update UI components to use new field names
6. **Configuration Loading**: Update configuration loading functions to map to new field names
7. **Documentation**: Update all documentation to reflect new naming conventions
8. **Remove Deprecations**: If temporary property aliases were added, remove them after sufficient transition time

## Validation Plan

After each stage of implementation:

1. Run the test suite to ensure no regressions
2. Verify UI components render correctly 
3. Manual testing of key features to ensure calculations remain correct 