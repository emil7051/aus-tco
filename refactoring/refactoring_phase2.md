# Phase 2: Calculator Logic and Strategy Pattern Standardization

This document outlines the implementation steps for Phase 2 of the field refactoring project, focusing on standardizing the calculator logic and implementing a consistent strategy pattern.

## Goals

- Update calculator logic to use standardized field names
- Standardize the Strategy Pattern implementation across the codebase
- Implement a factory pattern for strategy creation
- Ensure consistent strategy class and method naming

## Implementation Steps

### Step 1: Update TCOOutput Creation in Calculator

Modify the `calculate` method in `tco_model/calculator.py` to use the new field names and structures:

```python
def calculate(self, scenario: ScenarioInput) -> TCOOutput:
    """
    Calculate the TCO for a given scenario input.
    
    Args:
        scenario: The scenario input containing all parameters for the calculation.
        
    Returns:
        TCOOutput: The calculated TCO results with the following key fields:
            - total_tco: Total cost of ownership (NPV)
            - lcod: Levelized cost of driving per km
            - annual_costs: Annual breakdown of costs as AnnualCostsCollection
            - npv_costs: NPV breakdown of costs
    """
    # Constants for readability
    FIRST_YEAR = 0
    
    # [All existing calculation logic remains the same]
    
    # Convert annual costs dataframe to list of AnnualCosts objects
    annual_costs_list = []
    for _, row in annual_costs_df.iterrows():
        annual_costs_list.append(
            AnnualCosts(
                year=int(row['year']),
                calendar_year=int(row['calendar_year']),
                acquisition=float(row['acquisition']),
                energy=float(row['energy']),
                maintenance=float(row['maintenance']),
                infrastructure=float(row['infrastructure']),
                battery_replacement=float(row['battery_replacement']),
                insurance=float(row['insurance']),
                registration=float(row['registration']),
                carbon_tax=float(row['carbon_tax']),
                other_taxes=float(row['other_taxes']),
                residual_value=float(row['residual_value'])
            )
        )
    
    # Create NPVCosts object
    npv_costs_obj = NPVCosts(
        acquisition=npv_costs['acquisition'],
        energy=npv_costs['energy'],
        maintenance=npv_costs['maintenance'],
        infrastructure=npv_costs['infrastructure'],
        battery_replacement=npv_costs['battery_replacement'],
        insurance=npv_costs['insurance'],
        registration=npv_costs['registration'],
        carbon_tax=npv_costs['carbon_tax'],
        other_taxes=npv_costs['other_taxes'],
        residual_value=npv_costs['residual_value']
    )
    
    # Wrap annual costs with the collection class
    annual_costs_collection = AnnualCostsCollection(annual_costs_list)
    
    # Create and return the TCO output with new field names
    result = TCOOutput(
        scenario_name=scenario.scenario_name,
        vehicle_name=scenario.vehicle.name,
        vehicle_type=scenario.vehicle.type,
        analysis_period_years=analysis_period,
        total_distance_km=total_distance_km,
        annual_costs=annual_costs_collection,
        npv_costs=npv_costs_obj,
        total_nominal_cost=total_nominal_cost,
        total_tco=npv_costs['total'],  # Renamed from npv_total
        lcod=lcod_per_km,              # Renamed from lcod_per_km
        calculation_date=date.today()
    )
    
    # Store original scenario for testing
    result._scenario = scenario
    
    return result
```

### Step 2: Update ComparisonResult Creation in Calculator

Modify the `compare_results` method in `tco_model/calculator.py`:

```python
def compare_results(self, result1: TCOOutput, result2: TCOOutput) -> ComparisonResult:
    """
    Compare two TCO results and generate a comparison result.
    
    Args:
        result1: First TCO result
        result2: Second TCO result
        
    Returns:
        ComparisonResult: The comparison between the two TCO results
    """
    # Use utility functions from terminology module for consistency
    from tco_model.terminology import calculate_cost_difference
    
    # Calculate TCO difference and percentage (renamed from npv_difference)
    tco_difference, tco_percentage = calculate_cost_difference(
        result1.total_tco, result2.total_tco
    )
    
    # Calculate LCOD difference and percentage
    lcod_difference, lcod_difference_percentage = calculate_cost_difference(
        result1.lcod, result2.lcod
    )
    
    # Calculate payback year (if applicable)
    payback_year = self._calculate_payback_year(result1, result2)
    
    # Return comparison result with new field names
    return ComparisonResult(
        scenario_1=result1,
        scenario_2=result2,
        tco_difference=tco_difference,  # Renamed from npv_difference
        tco_percentage=tco_percentage,  # Renamed from npv_difference_percentage
        lcod_difference=lcod_difference,
        lcod_difference_percentage=lcod_difference_percentage,
        payback_year=payback_year
    )
```

### Step 3: Update Payback Calculation Method

Modify the `_calculate_payback_year` method in `tco_model/calculator.py`:

```python
def _calculate_payback_year(self, result1: TCOOutput, result2: TCOOutput) -> Optional[int]:
    """
    Calculate the payback year between two scenarios.
    
    The payback year is the year in which the cumulative costs of scenario 1
    become less than the cumulative costs of scenario 2.
    
    Args:
        result1: First TCO result
        result2: Second TCO result
        
    Returns:
        Optional[int]: The payback year, or None if there is no payback
    """
    # Constants for readability
    NO_PAYBACK = None
    
    # Get annual costs using the new collection structure
    costs1 = result1.annual_costs.total  # This now returns a list directly
    costs2 = result2.annual_costs.total
    
    # Calculate cumulative costs
    cumulative1 = np.cumsum(costs1)
    cumulative2 = np.cumsum(costs2)
    
    # Find the year where cumulative costs of scenario 1 become less than scenario 2
    for year, (cum1, cum2) in enumerate(zip(cumulative1, cumulative2)):
        if cum1 < cum2:
            return year
    
    # No payback within the analysis period
    return NO_PAYBACK
```

### Step 4: Create Consistent Strategy Interface

Define a consistent strategy interface in `tco_model/strategies.py`:

```python
from abc import ABC, abstractmethod
from typing import Dict, Type, Protocol, Optional, Callable, Any, List, Union

class CostCalculationStrategy(ABC):
    """
    Abstract base class defining the interface for cost calculation strategies.
    All cost calculation strategies should inherit from this class.
    """
    
    @abstractmethod
    def calculate_costs(self, scenario: ScenarioInput, year: int) -> float:
        """
        Calculate costs for a specific year.
        
        Args:
            scenario: The scenario input
            year: The year to calculate costs for (0-based index)
            
        Returns:
            float: The calculated cost for the given year
        """
        pass
    
    def get_calendar_year(self, year: int) -> int:
        """
        Convert analysis year (0-based) to calendar year.
        
        Args:
            year: Analysis year (0-based)
            
        Returns:
            int: Calendar year
        """
        from tco_model.terminology import BASE_CALENDAR_YEAR
        return BASE_CALENDAR_YEAR + year


class ResidualValueStrategy(ABC):
    """
    Abstract base class defining the interface for residual value strategies.
    All residual value strategies should inherit from this class.
    """
    
    @abstractmethod
    def calculate_residual_value(self, scenario: ScenarioInput, year: int) -> float:
        """
        Calculate residual value for a specific year.
        
        Args:
            scenario: The scenario input
            year: The year to calculate residual value for (0-based index)
            
        Returns:
            float: The calculated residual value for the given year
        """
        pass
    
    def get_calendar_year(self, year: int) -> int:
        """
        Convert analysis year (0-based) to calendar year.
        
        Args:
            year: Analysis year (0-based)
            
        Returns:
            int: Calendar year
        """
        from tco_model.terminology import BASE_CALENDAR_YEAR
        return BASE_CALENDAR_YEAR + year
```

### Step 5: Create Strategy Factory

Add a strategy factory in `tco_model/strategies.py` to standardize strategy creation:

```python
class StrategyFactory:
    """
    Factory for creating strategy instances with standardized naming.
    
    This factory manages the registration and retrieval of strategy classes,
    providing a consistent interface for obtaining strategy instances.
    """
    
    # Constants for default keys
    DEFAULT_STRATEGY_KEY = ":"
    
    # Registry of strategies by domain and type
    _strategies: Dict[str, Dict[str, Type[Any]]] = {}
    
    @classmethod
    def register_strategy(cls, domain: str, vehicle_type: Optional[str], 
                         implementation: Optional[str], strategy_class: Type[Any]) -> None:
        """
        Register a strategy class for a domain and type.
        
        Args:
            domain: Strategy domain (e.g., 'energy', 'maintenance')
            vehicle_type: Optional vehicle type ('battery_electric' or 'diesel')
            implementation: Optional implementation approach (e.g., 'distance_based')
            strategy_class: Strategy class to register
        """
        if domain not in cls._strategies:
            cls._strategies[domain] = {}
        
        # Create a key for this strategy variant
        variant_key = f"{vehicle_type or ''}:{implementation or ''}"
        cls._strategies[domain][variant_key] = strategy_class
    
    @classmethod
    def get_strategy(cls, domain: str, vehicle_type: Optional[str] = None,
                    implementation: Optional[str] = None) -> Any:
        """
        Get a strategy instance for a domain and type.
        
        Args:
            domain: Strategy domain (e.g., 'energy', 'maintenance')
            vehicle_type: Optional vehicle type (battery_electric or diesel)
            implementation: Optional implementation approach (e.g., 'distance_based')
            
        Returns:
            Instance of the appropriate strategy
            
        Raises:
            ValueError: If no suitable strategy is found
        """
        if domain not in cls._strategies:
            raise ValueError(f"No strategies registered for domain '{domain}'")
        
        # Try to find a strategy using progressively less specific keys
        # 1. Exact match with both vehicle_type and implementation
        variant_key = f"{vehicle_type or ''}:{implementation or ''}"
        if variant_key in cls._strategies[domain]:
            return cls._strategies[domain][variant_key]()
        
        # 2. Match with just vehicle type
        vehicle_variant = f"{vehicle_type or ''}:"
        if vehicle_variant in cls._strategies[domain]:
            return cls._strategies[domain][vehicle_variant]()
        
        # 3. Match with just implementation
        impl_variant = f":{implementation or ''}"
        if impl_variant in cls._strategies[domain]:
            return cls._strategies[domain][impl_variant]()
        
        # 4. Default strategy (empty key)
        if cls.DEFAULT_STRATEGY_KEY in cls._strategies[domain]:
            return cls._strategies[domain][cls.DEFAULT_STRATEGY_KEY]()
        
        # If all else fails, raise an error
        raise ValueError(
            f"No suitable strategy found for domain '{domain}', "
            f"vehicle type '{vehicle_type}', implementation '{implementation}'"
        )
```

### Step 6: Update Strategy Classes for Consistency

Rename strategy classes to follow the standardized naming convention:

```python
# Rename BETPowerConsumptionStrategy to BETEnergyConsumptionStrategy
class BETEnergyConsumptionStrategy(EnergyConsumptionStrategy):
    """
    Energy consumption strategy for Battery Electric Trucks (BETs).
    
    Calculates electricity consumption and costs based on:
    - Base energy consumption rate (kWh/km)
    - Vehicle load and operational adjustments
    - Charging efficiency
    - Electricity price with optional demand charges
    """
    
    def calculate_consumption(self, scenario: ScenarioInput, year: int) -> float:
        """
        Calculate the energy consumption for a given year.
        
        Args:
            scenario: The scenario input
            year: The year to calculate consumption for
            
        Returns:
            float: Energy consumption in kWh
        """
        # [existing implementation...]
    
    def calculate_costs(self, scenario: ScenarioInput, year: int) -> float:
        """
        Calculate the energy costs for a given year.
        
        Args:
            scenario: The scenario input
            year: The year to calculate costs for
            
        Returns:
            float: Energy costs in AUD
        """
        # [existing implementation...]
```

### Step 7: Register All Strategies with Factory

Create a function to register all standard strategies with the factory:

```python
def register_all_strategies():
    """
    Register all standard strategies with the factory.
    
    This function should be called once at module initialization to 
    register all available strategies with the StrategyFactory.
    """
    # Use naming utility from terminology module
    from tco_model.terminology import get_strategy_class_name
    
    # Energy consumption strategies
    StrategyFactory.register_strategy("energy", "battery_electric", None, BETEnergyConsumptionStrategy)
    StrategyFactory.register_strategy("energy", "diesel", None, DieselConsumptionStrategy)
    
    # Maintenance strategies
    StrategyFactory.register_strategy("maintenance", "battery_electric", None, BETMaintenanceStrategy)
    StrategyFactory.register_strategy("maintenance", "diesel", None, DieselMaintenanceStrategy)
    
    # Standard distance-based variants
    StrategyFactory.register_strategy("maintenance", None, "distance_based", DistanceBasedMaintenanceStrategy)
    
    # Residual value strategies
    StrategyFactory.register_strategy("residual_value", None, None, StandardResidualValueStrategy)
    
    # Financing strategies
    StrategyFactory.register_strategy("financing", None, "loan", LoanFinancingStrategy)
    StrategyFactory.register_strategy("financing", None, "cash", CashFinancingStrategy)
    
    # Infrastructure strategies
    StrategyFactory.register_strategy("infrastructure", "battery_electric", None, BETInfrastructureStrategy)
    StrategyFactory.register_strategy("infrastructure", "diesel", None, DieselInfrastructureStrategy)
    
    # Insurance strategies
    StrategyFactory.register_strategy("insurance", None, None, StandardInsuranceStrategy)
    
    # Registration strategies
    StrategyFactory.register_strategy("registration", None, None, StandardRegistrationStrategy)
    
    # Carbon tax strategies
    StrategyFactory.register_strategy("carbon_tax", None, None, StandardCarbonTaxStrategy)
    
    # Battery replacement strategies
    StrategyFactory.register_strategy(
        "battery_replacement", 
        "battery_electric", 
        None, 
        BETBatteryReplacementStrategy
    )
```

### Step 8: Replace Strategy Getter Functions

Update all strategy getter functions to use the factory pattern:

```python
def get_energy_consumption_strategy(vehicle_type: VehicleType) -> EnergyConsumptionStrategy:
    """
    Get the appropriate energy consumption strategy based on vehicle type.
    
    Args:
        vehicle_type: The vehicle type
        
    Returns:
        EnergyConsumptionStrategy: The appropriate strategy for the vehicle type
    """
    return StrategyFactory.get_strategy("energy", vehicle_type.value)

def get_maintenance_strategy(vehicle_type: VehicleType) -> MaintenanceStrategy:
    """
    Get the appropriate maintenance strategy based on vehicle type.
    
    Args:
        vehicle_type: The vehicle type
        
    Returns:
        MaintenanceStrategy: The appropriate strategy for the vehicle type
    """
    return StrategyFactory.get_strategy("maintenance", vehicle_type.value)

def get_financing_strategy(financing_method: FinancingMethod) -> FinancingStrategy:
    """
    Get the appropriate financing strategy based on method.
    
    Args:
        financing_method: The financing method
        
    Returns:
        FinancingStrategy: The appropriate strategy for the financing method
    """
    implementation = financing_method.value  # 'loan' or 'cash'
    return StrategyFactory.get_strategy("financing", None, implementation)

# Replace other strategy getter functions similarly
```

### Step 9: Initialize Strategy Registry

Initialize the strategy registry in the module's init section:

```python
# Initialize strategy registry
register_all_strategies()
```

## Results and Benefits

- Consistent field naming across the calculator logic
- Standardized strategy pattern implementation
- Single registration point for strategies
- Consistent strategy naming conventions
- Clean interface definitions for strategies
- Elimination of direct strategy class instantiation
- Improved testability with factory pattern

## Acceptance Criteria

- [ ] Calculator methods use the new field names
- [ ] Strategy classes follow the standardized naming conventions
- [ ] Strategy factory correctly instantiates strategies
- [ ] Strategy methods have consistent naming and signatures
- [ ] All strategy getter functions use the factory pattern
- [ ] No direct strategy instantiation in the codebase 