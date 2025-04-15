# Deprecated Tests

This file documents tests that have been deprecated due to the UI refactoring and model extensions.

## Deprecated UI Tests

The following UI tests have been deprecated as they refer to the old UI structure that has been completely refactored:

1. **`tests/ui/test_old_sidebar.py`** - Replaced by new navigation and sidebar tests.
2. **`tests/ui/test_input_forms.py`** - Replaced by the enhanced input form tests with validation.
3. **`tests/ui/test_results_display.py`** - Replaced by the new results visualization tests.
4. **`tests/ui/test_app_layout.py`** - Replaced by responsive layout and theme tests.

## Deprecated Integration Tests

1. **`tests/integration/test_old_ui_flow.py`** - Replaced by the new navigation state integration tests.
2. **`tests/integration/test_basic_chart_rendering.py`** - Replaced by comprehensive dashboard and visualization tests.

## Tests Requiring Updates

The following tests have not been deprecated but require significant updates to work with the refactored components:

1. **`tests/unit/test_terminology.py`** - Should be updated to test new terminology functions.
2. **`tests/integration/test_calculator.py`** - Should be updated to work with the new TCO model extensions.

## Migration Path for Test Data

For tests that rely on fixtures or test data from deprecated tests, use the following migration paths:

| Old Fixture/Data | New Location |
|------------------|-------------|
| `old_scenario` | Use `bet_scenario` or `diesel_scenario` from conftest.py |
| `old_chart_data` | Use chart data from new visualization tests |
| `old_sidebar_config` | Use `navigation_state` fixture |
| `old_layout_options` | Use `layout_config` fixture |

## Deprecation Timeline

These tests will be maintained in the codebase with `@pytest.mark.skip` annotations until the refactoring is complete and the new tests are fully operational. They will be removed entirely in the next major version release.

## Notes on Test Coverage

The new test structure provides more comprehensive coverage of:

1. Theme switching and responsive layouts
2. Component rendering across different viewport sizes
3. Navigation state management
4. Input validation with immediate feedback
5. Environmental impact visualizations
6. Investment analysis metrics
7. Side-by-side layout comparison

Old tests focused primarily on basic rendering and limited interactivity, while the new test suite tests the entire component lifecycle and integration with the enhanced TCO model. 