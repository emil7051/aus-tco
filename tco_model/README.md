# TCO Model Package

This package contains the core calculation logic for the Australian Heavy Vehicle Total Cost of Ownership (TCO) Modeller.

## Overview

The TCO Model package implements the business logic and calculation engine for computing the Total Cost of Ownership (TCO) of heavy vehicles, with a particular focus on comparing Battery Electric Trucks (BETs) and conventional Internal Combustion Engine (ICE) diesel trucks in the Australian context.

## Core Components

The package is organized into several modules:

- `models.py`: Pydantic data models that define the structure and validation rules for all inputs and outputs
- `costs.py`: Functions that calculate individual cost components
- `strategies.py`: Strategy pattern implementations for different calculation methods
- `calculator.py`: Main calculation engine that orchestrates the TCO calculation process
- `vehicles.py`: Vehicle-specific data loading and handling

## Cost Components (costs.py)

The `costs.py` module contains pure functions that calculate individual cost components for the TCO model. Each function takes a scenario input and a year parameter, and returns the cost for that specific component in that year.

### Acquisition Costs

```python
def calculate_acquisition_costs(scenario: ScenarioInput, year: int) -> float
```

Calculates vehicle acquisition costs, including:
- Purchase price (minus any subsidies)
- Financing costs (down payment, loan repayments)

For cash purchases, the full amount is applied in year 0. For financed purchases, the down payment is applied in year 0, and loan repayments are distributed across subsequent years based on the loan term.

### Energy Costs

```python
def calculate_energy_costs(scenario: ScenarioInput, year: int) -> float
```

Calculates energy costs based on vehicle type:
- For BETs: Electricity consumption (kWh/km × annual distance), accounting for charging efficiency and electricity prices
- For Diesel: Fuel consumption (L/km × annual distance), accounting for diesel prices and potentially AdBlue costs

This function provides a direct calculation approach that can be used when the strategy pattern implementation in `strategies.py` is not needed (e.g., for unit testing).

### Maintenance Costs

```python
def calculate_maintenance_costs(scenario: ScenarioInput, year: int) -> float
```

Calculates maintenance costs based on:
- Fixed annual costs (scheduled services, inspections)
- Variable costs based on distance (per-km rate)
- Adjustments for vehicle type and age
- Inflation for subsequent years

BETs typically have lower maintenance costs due to fewer mechanical components and features like regenerative braking.

### Infrastructure Costs

```python
def calculate_infrastructure_costs(scenario: ScenarioInput, year: int) -> float
```

Calculates infrastructure costs:
- For BETs: Charging equipment, installation, grid upgrades (in year 0) and ongoing maintenance
- For Diesel: Typically zero, as refueling infrastructure is assumed to be available

Infrastructure costs are distributed across trucks if shared (using the `trucks_per_charger` parameter).

### Battery Replacement Costs

```python
def calculate_battery_replacement_costs(scenario: ScenarioInput, year: int) -> float
```

Calculates battery replacement costs for BETs:
- Only applies when battery capacity has degraded below the replacement threshold
- Takes into account projected battery prices (which typically decrease over time)
- Accounts for the battery replacement cost factor (replacement might cost less than a new battery)

### Insurance and Registration Costs

```python
def calculate_insurance_registration_costs(scenario: ScenarioInput, year: int) -> float
```

Calculates insurance and registration costs:
- Insurance based on vehicle value (which decreases over time due to depreciation)
- Registration costs (which may include road user charges for diesel vehicles)
- Adjustments for vehicle type
- Inflation for subsequent years

### Taxes and Levies

```python
def calculate_taxes_levies(scenario: ScenarioInput, year: int) -> float
```

Calculates applicable taxes and levies:
- Carbon tax for diesel vehicles (based on fuel consumption and emissions)
- Road user charges for electric vehicles (where applicable)
- Other taxes/levies specific to vehicle type

### Residual Value

```python
def calculate_residual_value(scenario: ScenarioInput, year: int) -> float
```

Calculates the residual (salvage) value of the vehicle:
- Only applies in the final year of the analysis period
- Returned as a negative value (representing income)
- Takes into account vehicle type, age, and initial purchase price
- Can use a dedicated residual value model if available, or fallback to a simplified calculation

## Integration with the TCO Calculator

These cost component functions are used by the `TCOCalculator` class in `calculator.py`, which:
1. Iterates through each year of the analysis period
2. Calls each cost component function for that year
3. Aggregates the results into annual totals
4. Calculates the Net Present Value (NPV) of all costs
5. Computes key metrics like Levelized Cost of Driving (LCOD)

## Usage Example

```python
from tco_model.calculator import TCOCalculator
from tco_model.models import ScenarioInput
from utils.helpers import load_default_scenario

# Load a default scenario
bet_scenario = load_default_scenario('default_bet')
diesel_scenario = load_default_scenario('default_ice')

# Initialize the calculator
calculator = TCOCalculator()

# Calculate TCO for both scenarios
bet_results = calculator.calculate(bet_scenario)
diesel_results = calculator.calculate(diesel_scenario)

# Compare the results
comparison = calculator.compare_results(bet_results, diesel_results)

# Access the results
print(f"BET Total TCO: ${bet_results.total_tco:,.2f}")
print(f"Diesel Total TCO: ${diesel_results.total_tco:,.2f}")
print(f"TCO difference: ${comparison.tco_difference:,.2f}")
print(f"LCOD (BET): ${bet_results.lcod:.4f}/km")
print(f"LCOD (Diesel): ${diesel_results.lcod:.4f}/km")
``` 