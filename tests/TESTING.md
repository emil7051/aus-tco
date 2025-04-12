# Testing Approach for Australian Heavy Vehicle TCO Modeller

This document outlines the testing approach used for the Australian Heavy Vehicle TCO Modeller project, including the testing framework, test categories, and guidelines for writing effective tests.

## Testing Framework

The project uses pytest as the primary testing framework, with the following additional tools and libraries:

- **pytest-cov**: For generating code coverage reports
- **unittest.mock**: For mocking external dependencies and isolating components
- **pytest fixtures**: For setting up test data and dependencies

## Test Organization

Tests are organized into the following directories:

- `tests/unit/`: Unit tests for individual functions and classes
- `tests/integration/`: Integration tests for component interactions
- `tests/fixtures/`: Test fixtures and data used across multiple tests

## Test Categories

### Unit Tests

Unit tests focus on testing individual components in isolation:

1. **Model Validation Tests**: Verify that Pydantic models correctly validate input data and enforce constraints
2. **Cost Function Tests**: Verify that cost calculation functions produce correct results
3. **Strategy Implementation Tests**: Verify that the implementation of the Strategy pattern works correctly
4. **Vehicle Module Tests**: Verify the functionality related to vehicle data loading and handling
5. **YearlyValue Tests**: Verify the interpolation functionality of the YearlyValue class

### Integration Tests

Integration tests focus on testing the interaction between multiple components:

1. **Calculator Integration Tests**: Verify that the TCO calculator correctly orchestrates the calculation of cost components
2. **End-to-End Flow Tests**: Verify that the complete calculation flow works as expected
3. **Payback Calculation Tests**: Verify that the payback year calculation works correctly for different scenarios

### Edge Case Tests

Edge case tests focus on testing the system's behavior with extreme or unusual inputs:

1. **Zero Values**: Test with zero values for key parameters
2. **High Usage**: Test with extremely high usage values
3. **Low Usage**: Test with extremely low usage values

## Test Fixtures

Test fixtures provide consistent test data across multiple test cases. The main fixtures include:

1. **Economic Parameters**: Default economic parameters for testing (discount rate, inflation, etc.)
2. **Operational Parameters**: Default operational parameters for testing (annual distance, operating days, etc.)
3. **Infrastructure Parameters**: Default infrastructure parameters for testing (charger cost, installation cost, etc.)
4. **Vehicle Parameters**: Default vehicle parameters for both BET and diesel vehicles
5. **Scenario Fixtures**: Complete scenario inputs for different vehicle types and edge cases

## Running Tests

### Basic Test Commands

To run all tests:

```bash
pytest
```

To run specific test modules:

```bash
pytest tests/unit/test_models.py
```

To run specific test classes or methods:

```bash
pytest tests/unit/test_models.py::TestVehicleParametersValidation
pytest tests/unit/test_models.py::TestVehicleParametersValidation::test_bet_parameters_valid
```

### Running Tests with Coverage

To run tests with coverage reporting:

```bash
pytest --cov=tco_model
```

For more detailed reports:

```bash
pytest --cov=tco_model --cov-report=term-missing --cov-report=html
```

This generates an HTML report in the `htmlcov/` directory that can be viewed in a web browser.

### Using the Test Script

For convenience, a test script is provided to run tests with coverage reporting:

```bash
./scripts/run_tests.sh
```

This script:
1. Installs pytest and pytest-cov if not already installed
2. Runs tests with coverage
3. Generates HTML and terminal coverage reports
4. Provides a summary of test results

## Test Strategy

### 1. Prioritize Critical Code Paths

Tests prioritize critical code paths and edge cases, including:

- Validation of input parameters
- Core calculation logic (especially financial calculations)
- Strategy pattern implementation
- Error handling and edge cases
- Interpolation and projections

### 2. Test Isolation

Tests are designed to be isolated and independent:

- Unit tests mock external dependencies
- Tests avoid shared mutable state
- Each test cleans up after itself

### 3. Comprehensive Assertions

Tests use comprehensive assertions to verify:

- Correct output values 
- Correct types and structures
- Correct behavior in error conditions
- Correct function calls and interactions

### 4. Parameterized Testing

Where appropriate, tests use parameterized testing to test multiple scenarios with a single test method.

## Guidelines for Writing Tests

1. **Test Names**: Use descriptive names that communicate the purpose and expected behavior (e.g., `test_bet_parameters_negative_price`)
2. **Test Documentation**: Include docstrings that explain what aspect of functionality is being tested
3. **Arrange-Act-Assert**: Structure tests according to the Arrange-Act-Assert pattern
4. **Mock External Dependencies**: Use mocks to isolate the component being tested
5. **Test Edge Cases**: Include tests for boundary conditions and error cases
6. **Keep Tests Small**: Each test should focus on a specific aspect of functionality

## Current Test Coverage

Current test coverage focuses on:

1. **Model Validation**: Tests for validating Pydantic models and their constraints
2. **Cost Functions**: Tests for individual cost component calculations
3. **Strategy Pattern**: Tests for the strategy pattern implementations
4. **Calculator Integration**: Tests for the TCO calculator's integration with cost functions and strategies
5. **Payback Calculation**: Tests for the payback period calculation functionality
6. **YearlyValue Interpolation**: Tests for the interpolation of values over time
7. **Edge Cases**: Tests for extreme input values and special cases 