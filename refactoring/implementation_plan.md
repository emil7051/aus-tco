# Field Refactoring Implementation Plan

This document outlines the step-by-step implementation plan for standardizing field names across the TCO model codebase based on the analysis in `field_refactoring_analysis.md` and the conventions defined in `naming_conventions.md`.

## Phase 1: Core Model Updates

### Step 1: Update NPVCosts Class

Add combined properties to the NPVCosts class in `tco_model/models.py` to support UI requirements:

```python
class NPVCosts(BaseModel):
    """Net Present Value of costs over the analysis period."""
    acquisition: float = Field(0, description="NPV of acquisition costs")
    energy: float = Field(0, description="NPV of energy costs")
    maintenance: float = Field(0, description="NPV of maintenance costs")
    infrastructure: float = Field(0, description="NPV of infrastructure costs")
    battery_replacement: float = Field(0, description="NPV of battery replacement costs")
    insurance: float = Field(0, description="NPV of insurance costs")
    registration: float = Field(0, description="NPV of registration costs")
    carbon_tax: float = Field(0, description="NPV of carbon tax")
    other_taxes: float = Field(0, description="NPV of other taxes and levies")
    residual_value: float = Field(0, description="NPV of residual value (negative cost/income)")
    
    @property
    def total(self) -> float:
        """Calculate total NPV cost."""
        return (
            self.acquisition +
            self.energy +
            self.maintenance +
            self.infrastructure +
            self.battery_replacement +
            self.insurance +
            self.registration +
            self.carbon_tax +
            self.other_taxes +
            self.residual_value
        )
    
    # New combined properties to match UI components
    @property
    def insurance_registration(self) -> float:
        """Combined insurance and registration costs."""
        return self.insurance + self.registration
    
    @property
    def taxes_levies(self) -> float:
        """Combined carbon tax and other taxes."""
        return self.carbon_tax + self.other_taxes
```

### Step 2: Create AnnualCostsCollection Class

Create a new wrapper class in `tco_model/models.py` that will provide the expected interface for annual costs:

```python
class AnnualCostsCollection:
    """
    Wrapper for a list of AnnualCosts objects that provides both item access
    and attribute access to cost components across all years.
    """
    
    def __init__(self, costs: List[AnnualCosts]):
        self._costs = costs
        
    def __getitem__(self, index):
        """Allow direct indexing to get a specific year."""
        return self._costs[index]
    
    def __len__(self):
        """Return the number of years."""
        return len(self._costs)
    
    def __iter__(self):
        """Allow iteration over all years."""
        return iter(self._costs)
    
    @property
    def total(self) -> List[float]:
        """Get total costs for all years."""
        return [cost.total for cost in self._costs]
    
    @property
    def acquisition(self) -> List[float]:
        """Get acquisition costs for all years."""
        return [cost.acquisition for cost in self._costs]
    
    @property
    def energy(self) -> List[float]:
        """Get energy costs for all years."""
        return [cost.energy for cost in self._costs]
    
    @property
    def maintenance(self) -> List[float]:
        """Get maintenance costs for all years."""
        return [cost.maintenance for cost in self._costs]
    
    @property
    def infrastructure(self) -> List[float]:
        """Get infrastructure costs for all years."""
        return [cost.infrastructure for cost in self._costs]
    
    @property
    def battery_replacement(self) -> List[float]:
        """Get battery replacement costs for all years."""
        return [cost.battery_replacement for cost in self._costs]
    
    @property
    def insurance(self) -> List[float]:
        """Get insurance costs for all years."""
        return [cost.insurance for cost in self._costs]
    
    @property
    def registration(self) -> List[float]:
        """Get registration costs for all years."""
        return [cost.registration for cost in self._costs]
    
    @property
    def carbon_tax(self) -> List[float]:
        """Get carbon tax costs for all years."""
        return [cost.carbon_tax for cost in self._costs]
    
    @property
    def other_taxes(self) -> List[float]:
        """Get other taxes costs for all years."""
        return [cost.other_taxes for cost in self._costs]
    
    # Combined properties to match UI components
    @property
    def insurance_registration(self) -> List[float]:
        """Get combined insurance and registration costs for all years."""
        return [cost.insurance + cost.registration for cost in self._costs]
    
    @property
    def taxes_levies(self) -> List[float]:
        """Get combined taxes and levies for all years."""
        return [cost.carbon_tax + cost.other_taxes for cost in self._costs]
```

### Step 3: Update TCOOutput Class

Modify the TCOOutput class in `tco_model/models.py` to use the new field names and include the scenario reference:

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
    
    # Renamed from npv_total to total_tco
    total_tco: float = Field(..., description="Total cost of ownership (NPV)")
    
    # Renamed from lcod_per_km to lcod
    lcod: float = Field(..., description="Levelized Cost of Driving per km")
    
    total_nominal_cost: float = Field(..., description="Total nominal cost over analysis period")
    calculation_date: date = Field(default_factory=date.today, description="Date of calculation")
    
    # Store original scenario for testing purposes
    _scenario: Optional[ScenarioInput] = PrivateAttr(default=None)
    
    @property
    def scenario(self) -> Optional[ScenarioInput]:
        """Return the original scenario for testing purposes."""
        return self._scenario
    
    # Keep existing properties
    @property
    def total_acquisition_cost(self) -> float:
        """Calculate total nominal acquisition cost."""
        return sum(cost.acquisition for cost in self.annual_costs)
    
    @property
    def total_energy_cost(self) -> float:
        """Calculate total nominal energy cost."""
        return sum(cost.energy for cost in self.annual_costs)
    
    @property
    def total_maintenance_cost(self) -> float:
        """Calculate total nominal maintenance cost."""
        return sum(cost.maintenance for cost in self.annual_costs)
    
    @property
    def total_other_costs(self) -> float:
        """Calculate total of other costs."""
        return (self.total_nominal_cost - self.total_acquisition_cost - 
                self.total_energy_cost - self.total_maintenance_cost)
    
    # Temporary compatibility aliases (can be removed later)
    @property
    def npv_total(self) -> float:
        """Alias for total_tco (deprecated)."""
        warnings.warn("npv_total is deprecated, use total_tco instead", DeprecationWarning)
        return self.total_tco
    
    @property
    def lcod_per_km(self) -> float:
        """Alias for lcod (deprecated)."""
        warnings.warn("lcod_per_km is deprecated, use lcod instead", DeprecationWarning)
        return self.lcod
```

### Step 4: Update ComparisonResult Class

Modify the ComparisonResult class in `tco_model/models.py` to use the new field names and add missing properties:

```python
class ComparisonResult(BaseModel):
    """Comparison between two TCO results."""
    scenario_1: TCOOutput
    scenario_2: TCOOutput
    
    # Renamed from npv_difference
    tco_difference: float
    
    # Renamed from npv_difference_percentage
    tco_percentage: float
    
    lcod_difference: float
    lcod_difference_percentage: float
    payback_year: Optional[int] = None
    
    @property
    def component_differences(self) -> Dict[str, float]:
        """Calculate differences between cost components."""
        result = {}
        for attr in dir(self.scenario_1.npv_costs):
            if not attr.startswith('_') and not callable(getattr(self.scenario_1.npv_costs, attr)):
                val1 = getattr(self.scenario_1.npv_costs, attr)
                val2 = getattr(self.scenario_2.npv_costs, attr)
                if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                    result[attr] = val2 - val1
        return result
    
    @property
    def cheaper_option(self) -> int:
        """Return 1 if scenario_1 is cheaper, 2 if scenario_2 is cheaper."""
        return 1 if self.tco_difference > 0 else 2
    
    # Temporary compatibility aliases (can be removed later)
    @property
    def npv_difference(self) -> float:
        """Alias for tco_difference (deprecated)."""
        warnings.warn("npv_difference is deprecated, use tco_difference instead", DeprecationWarning)
        return self.tco_difference
    
    @property
    def npv_difference_percentage(self) -> float:
        """Alias for tco_percentage (deprecated)."""
        warnings.warn("npv_difference_percentage is deprecated, use tco_percentage instead", DeprecationWarning)
        return self.tco_percentage
    
    @classmethod
    def create(cls, scenario_1: TCOOutput, scenario_2: TCOOutput):
        """Create a comparison between two TCO results."""
        # Calculate differences using new field names
        tco_diff = scenario_2.total_tco - scenario_1.total_tco
        
        tco_diff_pct = 0
        if scenario_1.total_tco != 0:
            tco_diff_pct = (tco_diff / abs(scenario_1.total_tco)) * 100
            
        lcod_diff = scenario_2.lcod - scenario_1.lcod
        
        lcod_diff_pct = 0
        if scenario_1.lcod != 0:
            lcod_diff_pct = (lcod_diff / abs(scenario_1.lcod)) * 100
        
        # Calculate payback year
        payback_calculator = TCOCalculator()
        payback_year = payback_calculator._calculate_payback_year(scenario_1, scenario_2)
        
        return cls(
            scenario_1=scenario_1,
            scenario_2=scenario_2,
            tco_difference=tco_diff,
            tco_percentage=tco_diff_pct,
            lcod_difference=lcod_diff,
            lcod_difference_percentage=lcod_diff_pct,
            payback_year=payback_year
        )
```

## Phase 2: Calculator Logic Updates

### Step 1: Update TCOOutput Creation in Calculator

Modify the `calculate` method in `tco_model/calculator.py` to use the new field names and structures:

```python
def calculate(self, scenario: ScenarioInput) -> TCOOutput:
    """
    Calculate the TCO for a given scenario input.
    
    Args:
        scenario: The scenario input containing all parameters for the calculation.
        
    Returns:
        TCOOutput: The calculated TCO results.
    """
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
    # Calculate TCO difference (renamed from npv_difference)
    tco_difference = result2.total_tco - result1.total_tco
    
    # Calculate TCO difference percentage (renamed from npv_difference_percentage)
    tco_percentage = 0
    if result1.total_tco != 0:
        tco_percentage = (tco_difference / abs(result1.total_tco)) * 100
    
    # Calculate LCOD difference
    lcod_difference = result2.lcod - result1.lcod
    
    # Calculate LCOD difference percentage
    lcod_difference_percentage = 0
    if result1.lcod != 0:
        lcod_difference_percentage = (lcod_difference / abs(result1.lcod)) * 100
    
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
    return None
```

## Phase 3: UI Component Updates

### Step 1: Update UI Helper Functions

Modify the helper functions in `ui/results/utils.py` to use the new collection and property structure:

```python
def get_component_value(result: TCOOutput, component: str) -> float:
    """
    Get component NPV value from a result using the right structure.
    
    Handles special combined components like "insurance_registration" and
    "taxes_levies" by using the new properties directly.
    
    Args:
        result: TCO result object containing the cost data
        component: Component key to access (from COMPONENT_KEYS)
        
    Returns:
        float: The component value in AUD
    """
    if not result or not result.npv_costs:
        return 0.0
        
    try:
        # Use direct property access for all components including combined ones
        return getattr(result.npv_costs, component, 0.0)
    except (AttributeError, TypeError):
        return 0.0


def get_annual_component_value(result: TCOOutput, component: str, year: int) -> float:
    """
    Get component value for a specific year.
    
    Uses the new AnnualCostsCollection structure which provides direct access to
    combined components.
    
    Args:
        result: TCO result object containing the annual costs data
        component: Component key to access (from COMPONENT_KEYS)
        year: Year index (0-based)
        
    Returns:
        float: The component value for the specified year in AUD
    """
    if not result or not result.annual_costs or year >= len(result.annual_costs):
        return 0.0
        
    try:
        # Access the component values via the collection properties
        component_values = getattr(result.annual_costs, component, None)
        if component_values is not None:
            return component_values[year]
        return 0.0
    except (AttributeError, TypeError, IndexError):
        return 0.0
```

### Step 2: Update UI Display Components

Update references in display components to use the new field names:

```python
# In ui/results/summary.py for example
def display_comparison_summary(comparison: ComparisonResult):
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
```

## Phase 4: Configuration and Helper Updates

### Step 1: Update Config Loading in helpers.py

Update the config loading functions to use consistent terminology mappings:

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
    """
    from tco_model.terminology import CONFIG_TO_MODEL_MAPPING
    
    data = load_yaml_file(file_path)
    
    # Transform data keys using canonical mappings if needed
    # This is a simple implementation - in reality you'd need to handle nested paths
    transformed_data = {}
    for key, value in data.items():
        canonical_key = CONFIG_TO_MODEL_MAPPING.get(key, key)
        transformed_data[canonical_key] = value
    
    try:
        return model_class.parse_obj(transformed_data)
    except ValidationError as e:
        raise ValidationError(f"Validation error in {file_path}: {str(e)}", model_class)
```

### Step 2: Add Config Field Mapping Utilities

Add utility functions to helpers.py to map between config file keys and model fields:

```python
def map_config_key_to_model_field(config_key: str) -> str:
    """
    Map a configuration file key to the corresponding model field name.
    
    Args:
        config_key: The configuration file key to map
        
    Returns:
        str: The corresponding model field name
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
    """
    from tco_model.terminology import CONFIG_TO_MODEL_MAPPING
    
    # Create reverse mapping once
    if not hasattr(map_model_field_to_config_key, "reverse_mapping"):
        map_model_field_to_config_key.reverse_mapping = {
            v: k for k, v in CONFIG_TO_MODEL_MAPPING.items()
        }
    
    return map_model_field_to_config_key.reverse_mapping.get(model_field, model_field)
```

## Phase 5: Test Updates

### Step 1: Update Integration Test Assertions

Update the test assertions in `tests/integration/test_calculator.py` to use the new field names and structures:

```python
def test_calculate_bet_scenario(self, bet_scenario):
    """Test that the calculator produces valid results for a BET scenario."""
    calculator = TCOCalculator()
    
    result = calculator.calculate(bet_scenario)
    
    # Verify basic structure and properties of the result using new field names
    assert result.total_tco is not None
    assert result.lcod is not None
    assert result.scenario == bet_scenario
    
    # Verify annual costs using the new collection structure
    # Now accessing properties directly from the collection
    assert len(result.annual_costs) == bet_scenario.economic.analysis_period_years
    assert len(result.annual_costs.acquisition) == bet_scenario.economic.analysis_period_years
    assert len(result.annual_costs.energy) == bet_scenario.economic.analysis_period_years
    assert len(result.annual_costs.maintenance) == bet_scenario.economic.analysis_period_years
    
    # Check combined properties
    assert len(result.annual_costs.insurance_registration) == bet_scenario.economic.analysis_period_years
    assert len(result.annual_costs.taxes_levies) == bet_scenario.economic.analysis_period_years
    
    # Verify NPV costs and combined properties
    assert hasattr(result.npv_costs, 'acquisition')
    assert hasattr(result.npv_costs, 'insurance_registration')
    assert hasattr(result.npv_costs, 'taxes_levies')
    
    # Verify other assertions...
```

### Step 2: Update Test Mocks and Fixtures

Update the mock objects in `tests/integration/test_payback.py` to use the new field names and structures:

```python
# Convert the list of AnnualCosts to an AnnualCostsCollection
annual_costs_list = [
    AnnualCosts(year=0, calendar_year=2023, acquisition=100000, energy=10000, maintenance=5000, 
               infrastructure=20000, battery_replacement=0, insurance=5000, registration=1000, 
               carbon_tax=0, other_taxes=0, residual_value=0),
    # ... other annual costs
]

# Now we create the TCOOutput with the new field names and structure
result1 = TCOOutput(
    scenario_name="Scenario1",
    vehicle_name="Vehicle1",
    vehicle_type=VehicleType.BATTERY_ELECTRIC,
    analysis_period_years=5,
    total_distance_km=500000,
    annual_costs=AnnualCostsCollection(annual_costs_list),  # Use the collection
    npv_costs=npv_costs1,
    total_nominal_cost=189000,
    total_tco=172000,  # Renamed from npv_total
    lcod=0.344         # Renamed from lcod_per_km
)
```

### Step 3: Update conftest.py Fixtures

Check test fixture definitions in conftest.py to ensure they use the correct field patterns:

```python
@pytest.fixture
def mock_tco_output() -> TCOOutput:
    """
    Fixture providing a mock TCO output for tests.
    """
    npv_costs = NPVCosts(
        acquisition=85000,
        energy=30000,
        maintenance=15000,
        infrastructure=18000,
        battery_replacement=0,
        insurance=15000,
        registration=3000,
        carbon_tax=0,
        other_taxes=0,
        residual_value=-30000
    )
    
    annual_costs_list = [
        AnnualCosts(
            year=0, 
            calendar_year=2023, 
            acquisition=90000, 
            energy=10000, 
            maintenance=5000,
            infrastructure=20000, 
            battery_replacement=0, 
            insurance=5000, 
            registration=1000,
            carbon_tax=0, 
            other_taxes=0, 
            residual_value=0
        ),
        # ... other years
    ]
    
    return TCOOutput(
        scenario_name="Test Scenario",
        vehicle_name="Test Vehicle",
        vehicle_type=VehicleType.BATTERY_ELECTRIC,
        analysis_period_years=5,
        total_distance_km=500000,
        annual_costs=AnnualCostsCollection(annual_costs_list),
        npv_costs=npv_costs,
        total_nominal_cost=200000,
        total_tco=175000,  # Using new field name
        lcod=0.35          # Using new field name
    )
```

## Phase 6: Standardizing Strategy Pattern

### Step 1: Create Consistent Strategy Interface

Define a consistent strategy interface in `tco_model/strategies.py`:

```python
class CostCalculationStrategy(Protocol):
    """Protocol defining the interface for cost calculation strategies."""
    
    def calculate_costs(self, scenario: ScenarioInput, year: int) -> float:
        """
        Calculate costs for a specific year.
        
        Args:
            scenario: The scenario input
            year: The year to calculate costs for
            
        Returns:
            float: The calculated cost for the given year
        """
        ...


class ResidualValueStrategy(Protocol):
    """Protocol defining the interface for residual value strategies."""
    
    def calculate_residual_value(self, scenario: ScenarioInput, year: int) -> float:
        """
        Calculate residual value for a specific year.
        
        Args:
            scenario: The scenario input
            year: The year to calculate residual value for
            
        Returns:
            float: The calculated residual value for the given year
        """
        ...
```

### Step 2: Update Direct Functions to Use Strategy Pattern

Create strategy classes for the direct functions in `costs.py`:

```python
# Example for acquisition costs
class AcquisitionCostStrategy:
    """Strategy for calculating acquisition costs."""
    
    def calculate_costs(self, scenario: ScenarioInput, year: int) -> float:
        """
        Calculate acquisition costs for a given year.
        
        Args:
            scenario: The scenario input
            year: The year to calculate costs for
            
        Returns:
            float: The acquisition cost for the given year
        """
        return calculate_acquisition_costs(scenario, year)
```

### Step 3: Update Strategy Registration

Update the strategy registration functions in `tco_model/strategies.py`:

```python
def get_acquisition_cost_strategy() -> CostCalculationStrategy:
    """Get the appropriate acquisition cost calculation strategy."""
    return AcquisitionCostStrategy()

def get_energy_consumption_strategy(vehicle_type: VehicleType) -> CostCalculationStrategy:
    """Get the appropriate energy consumption strategy based on vehicle type."""
    if vehicle_type == VehicleType.BATTERY_ELECTRIC:
        return BETEnergyConsumptionStrategy()
    else:
        return DieselEnergyConsumptionStrategy()

# ... other strategy getters
```

## Phase 7: Final Documentation and Cleanup

### Step 1: Add Deprecation Warnings

Add deprecation warnings for old field names in key places:

```python
# In any function that returns a TCOOutput
def legacy_function_returning_tco_output() -> TCOOutput:
    result = calculate_tco()
    warnings.warn(
        "This function returns TCOOutput with renamed fields: " 
        "npv_total -> total_tco, lcod_per_km -> lcod", 
        DeprecationWarning
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
            - npv_costs: NPV breakdown of costs
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

1. `AnnualCostsCollection`: A wrapper for annual costs that provides both list-like access and attribute access
2. Combined properties in NPVCosts: `insurance_registration` and `taxes_levies`

## Usage Examples

### Before:
```python
result = calculator.calculate(scenario)
total_cost = result.npv_total
cost_per_km = result.lcod_per_km
```

### After:
```python
result = calculator.calculate(scenario)
total_cost = result.total_tco
cost_per_km = result.lcod
```
```

## Phase 8: Strategy Pattern and Vehicle Transformation Standardization

### Step 1: Rename Strategy Classes for Consistency

Update strategy class names in `tco_model/strategies.py` to follow consistent patterns:

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
    # [existing implementation...]
```

### Step 2: Standardize Strategy Method Names

Ensure all strategy classes use consistent method naming:

```python
class EnergyConsumptionStrategy(ABC):
    """
    Abstract base class for energy consumption calculation strategies.
    """
    
    @abstractmethod
    def calculate_consumption(self, scenario: ScenarioInput, year: int) -> float:
        """Calculate the energy consumption for a given year."""
        pass
    
    @abstractmethod
    def calculate_costs(self, scenario: ScenarioInput, year: int) -> float:
        """Calculate the energy costs for a given year."""
        pass
    
    def get_calendar_year(self, year: int) -> int:
        """Convert analysis year (0-based) to calendar year."""
        from tco_model.terminology import BASE_CALENDAR_YEAR
        return BASE_CALENDAR_YEAR + year


class ResidualValueStrategy(ABC):
    """
    Abstract base class for residual value calculation strategies.
    """
    
    @abstractmethod
    def calculate_residual_value(self, scenario: ScenarioInput, year: int) -> float:
        """Calculate the residual value for a given year."""
        pass
    
    def get_calendar_year(self, year: int) -> int:
        """Convert analysis year (0-based) to calendar year."""
        from tco_model.terminology import BASE_CALENDAR_YEAR
        return BASE_CALENDAR_YEAR + year


class StandardResidualValueStrategy(ResidualValueStrategy):
    """
    Standard strategy for residual value calculation.
    """
    
    def calculate_residual_value(self, scenario: ScenarioInput, year: int) -> float:
        """
        Calculate the residual value for a given year.
        
        Only the final year of the analysis period should have a residual value.
        """
        if year != scenario.economic.analysis_period_years - 1:
            return 0.0
            
        # Use the vehicle's residual value parameters to calculate
        # ... implementation ...
```

### Step 3: Standardize Vehicle Transformation Function Fields

Update the vehicle transformation functions to use consistent field names:

```python
def transform_bet_yaml_to_model(yaml_data: Dict[str, Any]) -> Dict[str, Any]:
    # Start with a new dictionary for the transformed data
    model_data = {}
    
    # Use canonical field names from terminology module
    from tco_model.terminology import CONFIG_TO_MODEL_MAPPING
    
    # Extract top-level fields
    vehicle_info = yaml_data.get('vehicle_info', {})
    
    # Map consumption parameters with standardized field names
    consumption_yaml = yaml_data.get('energy_consumption', {})
    consumption_model = {
        # Use standardized name without fallbacks
        'base_rate': consumption_yaml.get('base_rate_kwh_per_km', 1.5),
        # Other fields...
    }
    
    # Rest of function...
```

### Step 4: Create Constants for Default Values

Add constants for default values to terminology.py and use them in transformation functions:

```python
# In terminology.py
# Default values for vehicle parameters
DEFAULT_BET_CONSUMPTION_RATE = 1.5  # kWh/km
DEFAULT_DIESEL_CONSUMPTION_RATE = 0.35  # L/km
DEFAULT_BATTERY_CAPACITY = 400  # kWh
DEFAULT_CHARGING_POWER = 350  # kW

# In vehicles.py transformation functions
from tco_model.terminology import (
    DEFAULT_BET_CONSUMPTION_RATE,
    DEFAULT_DIESEL_CONSUMPTION_RATE,
    DEFAULT_BATTERY_CAPACITY,
    DEFAULT_CHARGING_POWER
)

# Use standardized defaults
consumption_model = {
    'base_rate': consumption_yaml.get('base_rate_kwh_per_km', DEFAULT_BET_CONSUMPTION_RATE),
    # Other fields...
}
```

### Step 5: Update Factory Functions for Strategies

Update the factory functions to use the renamed strategy classes:

```python
def get_energy_consumption_strategy(vehicle_type: VehicleType) -> EnergyConsumptionStrategy:
    """
    Factory function to get the appropriate energy consumption strategy
    for a given vehicle type.
    
    Args:
        vehicle_type: The vehicle type
        
    Returns:
        EnergyConsumptionStrategy: The appropriate strategy for the vehicle type
    """
    strategies = {
        VehicleType.BATTERY_ELECTRIC: BETEnergyConsumptionStrategy(),  # Renamed from BETPowerConsumptionStrategy
        VehicleType.DIESEL: DieselConsumptionStrategy(),
    }
    
    return strategies.get(vehicle_type, DieselConsumptionStrategy())
```

## Phase 9: Configuration File Standardization

### Step 1: Define Configuration File Schema Standards

Create standardized schema for all configuration files across the system:

```python
# In tco_model/schemas.py

from typing import Dict, Any, List
from pydantic import BaseModel, Field

class VehicleInfoSchema(BaseModel):
    """Schema for vehicle_info section in vehicle config files."""
    type: str = Field(..., description="Vehicle type (battery_electric or diesel)")
    category: str = Field(..., description="Vehicle category (rigid or articulated)")
    name: str = Field(..., description="Vehicle name/description")


class PurchaseSchema(BaseModel):
    """Schema for purchase section in vehicle config files."""
    base_price_2025: float = Field(..., gt=0, description="Base purchase price in 2025")
    annual_price_decrease_real: float = Field(0, ge=0, le=0.5, description="Annual real decrease in price")


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


class FuelConsumptionSchema(BaseModel):
    """Schema for fuel_consumption section in diesel config files."""
    base_rate_l_per_km: float = Field(..., gt=0, description="Base fuel consumption in L/km")
    min_rate: float = Field(..., gt=0, description="Minimum fuel consumption in L/km")
    max_rate: float = Field(..., gt=0, description="Maximum fuel consumption in L/km")
    load_adjustment_factor: float = Field(0.25, ge=0, description="Load adjustment factor")
    temperature_adjustment: Dict[str, float] = Field(default_factory=lambda: {
        "hot_weather": 0.03,
        "cold_weather": 0.05
    }, description="Temperature adjustments")


# Additional schemas for other sections...
```

### Step 2: Create Configuration Validation Utility

Add a utility to validate configuration files against the schemas:

```python
# In utils/config_utils.py

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
    
    # Load the file
    with open(file_path, 'r') as f:
        config_data = yaml.safe_load(f)
    
    # Determine vehicle type if not provided
    if not vehicle_type and 'vehicle_info' in config_data:
        vehicle_type = config_data['vehicle_info'].get('type')
    
    if not vehicle_type or vehicle_type not in CONFIG_FIELD_MAPPINGS:
        return config_data  # Return as-is if we can't determine mappings
    
    # Create a standardized version
    standardized_data = {}
    
    # Extract mappings for just this vehicle type
    for config_key, model_key in CONFIG_FIELD_MAPPINGS[vehicle_type].items():
        parts = config_key.split('.')
        current = standardized_data
        
        # Create nested dictionaries as needed
        for i, part in enumerate(parts[:-1]):
            if part not in current:
                current[part] = {}
            current = current[part]
        
        # Check if we have this field in the original data
        value = _get_nested_value(config_data, config_key)
        if value is not None:
            current[parts[-1]] = value
        else:
            # Try to find the field with legacy/alternative names
            for old_key, new_key in _get_field_alternatives(config_key, vehicle_type):
                value = _get_nested_value(config_data, old_key)
                if value is not None:
                    current[parts[-1]] = value
                    break
    
    return standardized_data


def _get_nested_value(data: Dict[str, Any], key_path: str) -> Any:
    """Get a value from nested dictionaries using dot notation."""
    parts = key_path.split('.')
    current = data
    
    for part in parts:
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None
    
    return current


def _get_field_alternatives(field_path: str, vehicle_type: str) -> List[Tuple[str, str]]:
    """Get alternative field paths that might contain the same data."""
    # Add specific field mapping alternatives based on known patterns
    alternatives = []
    
    if vehicle_type == "battery_electric":
        if field_path == "energy_consumption.base_rate_kwh_per_km":
            alternatives.append(("energy_consumption.base_rate", field_path))
    
    if vehicle_type == "diesel":
        if field_path == "fuel_consumption.base_rate_l_per_km":
            alternatives.append(("fuel_consumption.base_rate", field_path))
        if field_path == "engine.power_kw":
            alternatives.append(("engine.power", field_path))
    
    return alternatives
```

### Step 3: Update Config Loading Functions

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
    """
    from tco_model.terminology import CONFIG_FIELD_MAPPINGS
    
    data = load_yaml_file(file_path)
    
    # Get vehicle type for proper mapping
    vehicle_type = None
    if 'vehicle_info' in data and 'type' in data['vehicle_info']:
        vehicle_type = data['vehicle_info']['type']
    
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


def transform_vehicle_config(config: Dict[str, Any], vehicle_type: str) -> Dict[str, Any]:
    """
    Transform vehicle configuration to model format using standard mappings.
    
    Args:
        config: Configuration dictionary
        vehicle_type: Vehicle type to determine mappings
        
    Returns:
        Dict with model-compatible field structure
    """
    from tco_model.terminology import CONFIG_FIELD_MAPPINGS, BET_DEFAULTS, DIESEL_DEFAULTS
    
    # Choose the appropriate mappings and defaults
    mappings = CONFIG_FIELD_MAPPINGS.get(vehicle_type, {})
    defaults = BET_DEFAULTS if vehicle_type == "battery_electric" else DIESEL_DEFAULTS
    
    # Start with an empty result
    result = {}
    
    # Apply mappings from config to model
    for config_key, model_key in mappings.items():
        value = get_nested_config_value(config, config_key)
        if value is not None:
            set_nested_model_value(result, model_key, value)
    
    # Fill in missing values with defaults
    fill_missing_with_defaults(result, defaults)
    
    return result


def convert_config_to_model_format(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert a general configuration structure to match the model class structure.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Dict with model-compatible field structure
    """
    from tco_model.terminology import ECONOMIC_CONFIG_MAPPING, OPERATIONAL_CONFIG_MAPPING
    
    result = {}
    
    # Apply economic parameter mappings
    if 'general' in config or 'financing' in config or 'carbon_pricing' in config:
        for config_key, model_key in ECONOMIC_CONFIG_MAPPING.items():
            value = get_nested_config_value(config, config_key)
            if value is not None:
                set_nested_model_value(result, model_key, value)
    
    # Apply operational parameter mappings if present
    if any(k in config for k in ['annual_distance_km', 'operating_days_per_year']):
        for config_key, model_key in OPERATIONAL_CONFIG_MAPPING.items():
            value = get_nested_config_value(config, config_key)
            if value is not None:
                set_nested_model_value(result, model_key, value)
    
    return result


def get_nested_config_value(config: Dict[str, Any], key_path: str, default: Any = None) -> Any:
    """
    Get a value from nested configuration dictionaries using dot notation.
    
    Args:
        config: Configuration dictionary
        key_path: Dot-separated path to the value
        default: Default value if not found
        
    Returns:
        The value at the path or the default
    """
    parts = key_path.split('.')
    current = config
    
    try:
        for part in parts:
            current = current[part]
        return current
    except (KeyError, TypeError):
        return default


def set_nested_model_value(model_data: Dict[str, Any], key_path: str, value: Any) -> None:
    """
    Set a value in a nested model dictionary using dot notation.
    
    Args:
        model_data: Model data dictionary to modify
        key_path: Dot-separated path for the value
        value: Value to set
    """
    parts = key_path.split('.')
    current = model_data
    
    # Create nested dictionaries as needed
    for part in parts[:-1]:
        if part not in current:
            current[part] = {}
        current = current[part]
    
    # Set the final value
    current[parts[-1]] = value


def fill_missing_with_defaults(data: Dict[str, Any], defaults: Dict[str, Any]) -> None:
    """
    Fill missing values in a data dictionary with default values.
    
    Args:
        data: Data dictionary to fill
        defaults: Default values dictionary
    """
    for key, default_value in defaults.items():
        if key not in data:
            data[key] = default_value
        elif isinstance(default_value, dict) and isinstance(data[key], dict):
            # Recursively fill nested dictionaries
            fill_missing_with_defaults(data[key], default_value)
```

## Phase 10: Standardized Component Access

### Step 1: Create Component Access Utilities

Add standardized component access functions to `ui/results/utils.py`:

```python
from typing import Any, Dict, List, Optional, Union
from tco_model.models import TCOOutput, ComparisonResult, AnnualCostsCollection
from tco_model.terminology import (
    UI_COMPONENT_MAPPING, UI_COMPONENT_KEYS, UI_COMPONENT_LABELS,
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
    if component in UI_COMPONENT_MAPPING:
        return UI_COMPONENT_MAPPING[component].get("color", "#333333")
    return "#333333"  # Default gray


def get_component_display_order(component: str) -> int:
    """
    Get the standard display order for a component.
    
    Args:
        component: Component key
        
    Returns:
        int: Display order value (1-based)
    """
    if component in UI_COMPONENT_MAPPING:
        return UI_COMPONENT_MAPPING[component].get("display_order", 999)
    return 999  # Default to end
```

### Step 2: Update Component Display Logic

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

## Phase 11: Strategy Pattern Standardization

### Step 1: Create Strategy Factory

Add a strategy factory in `tco_model/strategies.py` to standardize strategy creation:

```python
from typing import Dict, Type, Optional
from abc import ABC
from enum import Enum
from tco_model.models import VehicleType, FinancingMethod
from tco_model.terminology import get_strategy_class_name

# Define protocol classes for strategies
class CostCalculationStrategy(ABC):
    """Protocol for cost calculation strategies."""
    
    def calculate_costs(self, scenario: ScenarioInput, year: int) -> float:
        """Calculate costs for a specific year."""
        pass

# Strategy factory for creating strategies with standardized naming
class StrategyFactory:
    """Factory for creating strategy instances with standardized naming."""
    
    # Registry of strategies by domain and type
    _strategies: Dict[str, Dict[str, Type[CostCalculationStrategy]]] = {}
    
    @classmethod
    def register_strategy(cls, domain: str, vehicle_type: Optional[str], 
                         implementation: Optional[str], strategy_class: Type[CostCalculationStrategy]) -> None:
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
                    implementation: Optional[str] = None) -> CostCalculationStrategy:
        """
        Get a strategy instance for a domain and type.
        
        Args:
            domain: Strategy domain (e.g., 'energy', 'maintenance')
            vehicle_type: Optional vehicle type (battery_electric or diesel)
            implementation: Optional implementation approach (e.g., 'distance_based')
            
        Returns:
            CostCalculationStrategy: Instance of the appropriate strategy
        """
        if domain not in cls._strategies:
            raise ValueError(f"No strategies registered for domain '{domain}'")
        
        # Try to find a strategy for this exact variant
        variant_key = f"{vehicle_type or ''}:{implementation or ''}"
        if variant_key in cls._strategies[domain]:
            return cls._strategies[domain][variant_key]()
        
        # Try with just vehicle type
        vehicle_variant = f"{vehicle_type or ''}:"
        if vehicle_variant in cls._strategies[domain]:
            return cls._strategies[domain][vehicle_variant]()
        
        # Try with just implementation
        impl_variant = f":{implementation or ''}"
        if impl_variant in cls._strategies[domain]:
            return cls._strategies[domain][impl_variant]()
        
        # Fall back to default strategy (empty key)
        if ":" in cls._strategies[domain]:
            return cls._strategies[domain][":"]()
        
        # If all else fails, raise an error
        raise ValueError(f"No suitable strategy found for domain '{domain}', vehicle type '{vehicle_type}', implementation '{implementation}'")


# Register existing strategies using standardized naming
def register_all_strategies():
    """Register all standard strategies with the factory."""
    # Energy consumption strategies
    StrategyFactory.register_strategy("energy", "battery_electric", None, BETEnergyConsumptionStrategy)
    StrategyFactory.register_strategy("energy", "diesel", None, DieselConsumptionStrategy)
    
    # Maintenance strategies
    StrategyFactory.register_strategy("maintenance", "battery_electric", None, BETMaintenanceStrategy)
    StrategyFactory.register_strategy("maintenance", "diesel", None, DieselMaintenanceStrategy)
    
    # Standard distance-based variants
    StrategyFactory.register_strategy("maintenance", None, "distance_based", DistanceBasedMaintenanceStrategy)
    
    # ... register other strategies ...


# Replace existing strategy getter functions with factory-based versions
def get_energy_consumption_strategy(vehicle_type: VehicleType) -> EnergyConsumptionStrategy:
    """Get the appropriate energy consumption strategy based on vehicle type."""
    return StrategyFactory.get_strategy("energy", vehicle_type.value)

def get_maintenance_strategy(vehicle_type: VehicleType) -> MaintenanceStrategy:
    """Get the appropriate maintenance strategy based on vehicle type."""
    return StrategyFactory.get_strategy("maintenance", vehicle_type.value)

def get_financing_strategy(financing_method: FinancingMethod) -> FinancingStrategy:
    """Get the appropriate financing strategy based on method."""
    implementation = financing_method.value  # 'loan' or 'cash'
    return StrategyFactory.get_strategy("financing", None, implementation)

# ... replace other strategy getter functions ...

# Initialize strategy registry
register_all_strategies()
```

### Step 2: Rename Strategy Classes for Consistency

Update existing strategy classes to follow the standardized naming convention:

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
    # ... unchanged implementation ...
```

### Step 3: Standardize Calculation Methods

Ensure all strategy classes follow the standard method naming convention:

```python
class EnergyConsumptionStrategy(ABC):
    """
    Abstract base class for energy consumption calculation strategies.
    """
    
    @abstractmethod
    def calculate_consumption(self, scenario: ScenarioInput, year: int) -> float:
        """Calculate the energy consumption for a given year."""
        pass
    
    @abstractmethod
    def calculate_costs(self, scenario: ScenarioInput, year: int) -> float:
        """Calculate the energy costs for a given year."""
        pass
    
    def get_calendar_year(self, year: int) -> int:
        """Convert analysis year (0-based) to calendar year."""
        from tco_model.terminology import BASE_CALENDAR_YEAR
        return BASE_CALENDAR_YEAR + year


class ResidualValueStrategy(ABC):
    """
    Abstract base class for residual value calculation strategies.
    """
    
    @abstractmethod
    def calculate_residual_value(self, scenario: ScenarioInput, year: int) -> float:
        """Calculate the residual value for a given year."""
        pass
    
    def get_calendar_year(self, year: int) -> int:
        """Convert analysis year (0-based) to calendar year."""
        from tco_model.terminology import BASE_CALENDAR_YEAR
        return BASE_CALENDAR_YEAR + year


class StandardResidualValueStrategy(ResidualValueStrategy):
    """
    Standard strategy for residual value calculation.
    """
    
    def calculate_residual_value(self, scenario: ScenarioInput, year: int) -> float:
        """
        Calculate the residual value for a given year.
        
        Only the final year of the analysis period should have a residual value.
        """
        if year != scenario.economic.analysis_period_years - 1:
            return 0.0
            
        # Use the vehicle's residual value parameters to calculate
        # ... implementation ...
```

## Phase 12: Testing and Documentation Improvements

### Step 1: Create Comprehensive Test Suite for Refactoring

Add specific tests for refactoring changes in `tests/refactoring/`:

```python
# tests/refactoring/test_naming_conventions.py

import pytest
import warnings
from tco_model.models import TCOOutput, ComparisonResult, NPVCosts, AnnualCosts, AnnualCostsCollection
from tco_model.terminology import (
    FIELD_NAME_MAPPING, get_canonical_field_name, get_component_value,
    UI_COMPONENT_KEYS, UI_COMPONENT_MAPPING
)

class TestFieldRenaming:
    """Tests for field renaming."""
    
    def test_deprecated_field_access(self):
        """Test that deprecated fields raise warnings but still work."""
        # Create a TCOOutput with new field names
        output = TCOOutput(
            scenario_name="Test Scenario",
            vehicle_name="Test Vehicle",
            vehicle_type=VehicleType.BATTERY_ELECTRIC,
            analysis_period_years=5,
            total_distance_km=500000,
            annual_costs=AnnualCostsCollection([]),
            npv_costs=NPVCosts(),
            total_nominal_cost=100000,
            total_tco=90000,  # New field name
            lcod=0.18,        # New field name
            calculation_date=date.today()
        )
        
        # Access deprecated fields with warning recording
        with pytest.warns(DeprecationWarning):
            npv_total = output.npv_total
            
        with pytest.warns(DeprecationWarning):
            lcod_per_km = output.lcod_per_km
            
        # Verify values are correct despite deprecation
        assert npv_total == 90000
        assert lcod_per_km == 0.18
    
    def test_canonical_field_names(self):
        """Test canonical field name mapping."""
        assert get_canonical_field_name("npv_total") == "total_tco"
        assert get_canonical_field_name("lcod_per_km") == "lcod"
        assert get_canonical_field_name("npv_difference") == "tco_difference"
        assert get_canonical_field_name("unchanged_field") == "unchanged_field"
    
    def test_component_access(self):
        """Test standard component access patterns."""
        # Create NPVCosts with some values
        npv_costs = NPVCosts(
            acquisition=50000,
            energy=20000,
            maintenance=10000,
            insurance=5000,
            registration=1000,
            carbon_tax=2000,
            other_taxes=1000,
            residual_value=-10000
        )
        
        # Test direct component access
        assert get_component_value(npv_costs, "acquisition") == 50000
        assert get_component_value(npv_costs, "energy") == 20000
        
        # Test combined component access
        assert get_component_value(npv_costs, "insurance_registration") == 6000
        assert get_component_value(npv_costs, "taxes_levies") == 3000


class TestAnnualCostsCollection:
    """Tests for the AnnualCostsCollection class."""
    
    def test_list_access(self):
        """Test list-like access to AnnualCostsCollection."""
        annual_costs = [
            AnnualCosts(year=0, calendar_year=2025, acquisition=50000, energy=10000),
            AnnualCosts(year=1, calendar_year=2026, acquisition=0, energy=10500)
        ]
        
        collection = AnnualCostsCollection(annual_costs)
        
        # Test indexing
        assert collection[0].acquisition == 50000
        assert collection[1].energy == 10500
        
        # Test length
        assert len(collection) == 2
        
        # Test iteration
        iterated = [cost.year for cost in collection]
        assert iterated == [0, 1]
    
    def test_attribute_access(self):
        """Test attribute access to component lists."""
        annual_costs = [
            AnnualCosts(year=0, calendar_year=2025, acquisition=50000, energy=10000),
            AnnualCosts(year=1, calendar_year=2026, acquisition=0, energy=10500)
        ]
        
        collection = AnnualCostsCollection(annual_costs)
        
        # Test component lists
        assert collection.acquisition == [50000, 0]
        assert collection.energy == [10000, 10500]
        
        # Test combined components
        assert collection.insurance_registration == [0, 0]  # Both zero by default
    
    def test_component_value_access(self):
        """Test standardized component value access."""
        annual_costs = [
            AnnualCosts(
                year=0, calendar_year=2025, 
                acquisition=50000, energy=10000, 
                insurance=2000, registration=1000,
                carbon_tax=500, other_taxes=300
            ),
            AnnualCosts(
                year=1, calendar_year=2026, 
                acquisition=0, energy=10500,
                insurance=2100, registration=1050,
                carbon_tax=550, other_taxes=330
            )
        ]
        
        collection = AnnualCostsCollection(annual_costs)
        
        # Test direct access to year's component
        assert get_component_value(collection, "acquisition", 0) == 50000
        assert get_component_value(collection, "energy", 1) == 10500
        
        # Test combined component access
        assert get_component_value(collection, "insurance_registration", 0) == 3000
        assert get_component_value(collection, "taxes_levies", 1) == 880
```

### Step 2: Create Automated Config File Checker

Add a script to check all configuration files for consistency:

```python
# scripts/check_config_files.py

import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Tuple
import yaml
import argparse

from utils.config_utils import validate_config_file
from tco_model.schemas import (
    VehicleInfoSchema, PurchaseSchema, EnergyConsumptionSchema, FuelConsumptionSchema
)

def check_vehicle_config_files(directory: Path) -> Tuple[List[str], List[str]]:
    """
    Check all vehicle config files in a directory for consistency.
    
    Args:
        directory: Directory containing vehicle config files
        
    Returns:
        Tuple containing (valid_files, invalid_files)
    """
    valid_files = []
    invalid_files = []
    
    for file_path in directory.glob("*.yaml"):
        try:
            # Load the file to check basic YAML validity
            with open(file_path, 'r') as f:
                config = yaml.safe_load(f)
            
            errors = []
            
            # Check for required top-level sections
            required_sections = ["vehicle_info", "purchase"]
            for section in required_sections:
                if section not in config:
                    errors.append(f"Missing required section: {section}")
            
            # Validate vehicle_info section
            if "vehicle_info" in config:
                is_valid, section_errors = validate_config_file(
                    {"vehicle_info": config["vehicle_info"]}, 
                    VehicleInfoSchema
                )
                if not is_valid:
                    errors.extend([f"vehicle_info: {e}" for e in section_errors])
            
            # Determine vehicle type for further validation
            vehicle_type = config.get("vehicle_info", {}).get("type")
            
            # Validate other sections based on vehicle type
            if vehicle_type == "battery_electric":
                if "energy_consumption" in config:
                    is_valid, section_errors = validate_config_file(
                        {"energy_consumption": config["energy_consumption"]},
                        EnergyConsumptionSchema
                    )
                    if not is_valid:
                        errors.extend([f"energy_consumption: {e}" for e in section_errors])
            elif vehicle_type == "diesel":
                if "fuel_consumption" in config:
                    is_valid, section_errors = validate_config_file(
                        {"fuel_consumption": config["fuel_consumption"]},
                        FuelConsumptionSchema
                    )
                    if not is_valid:
                        errors.extend([f"fuel_consumption: {e}" for e in section_errors])
            
            # Determine validity based on errors
            if errors:
                print(f"Invalid config file: {file_path}")
                for error in errors:
                    print(f"  - {error}")
                invalid_files.append(str(file_path))
            else:
                valid_files.append(str(file_path))
                
        except Exception as e:
            print(f"Error checking file {file_path}: {str(e)}")
            invalid_files.append(str(file_path))
    
    return valid_files, invalid_files


def main():
    parser = argparse.ArgumentParser(description="Check configuration files for consistency")
    parser.add_argument("directory", help="Directory containing configuration files")
    args = parser.parse_args()
    
    directory = Path(args.directory)
    if not directory.exists() or not directory.is_dir():
        print(f"Error: {args.directory} is not a valid directory")
        sys.exit(1)
    
    print(f"Checking vehicle config files in {directory}...")
    valid_files, invalid_files = check_vehicle_config_files(directory)
    
    print(f"\nSummary:")
    print(f"- Valid files: {len(valid_files)}")
    print(f"- Invalid files: {len(invalid_files)}")
    
    if invalid_files:
        print("\nFailed validation:")
        for file in invalid_files:
            print(f"- {file}")
        sys.exit(1)
    else:
        print("\nAll files are valid!")
        sys.exit(0)


if __name__ == "__main__":
    main()
```

### Step 3: Update Documentation for New Conventions

Add a new guide document for developers on using the standardized fields and patterns:

```markdown
# TCO Model Developer Guide

This guide explains how to work with the TCO model codebase following our standardized naming conventions and patterns.

## Working with Field Names

All field names now follow standardized conventions:

### Core Model Fields

The `TCOOutput` class has these canonical fields:
- `total_tco`: Total cost of ownership (NPV)
- `lcod`: Levelized cost of driving per km
- `annual_costs`: Annual breakdown of costs as an `AnnualCostsCollection`
- `npv_costs`: NPV breakdown of costs as `NPVCosts`

Older field names (`npv_total`, `lcod_per_km`) are still supported but deprecated. 

### Component Access

To access cost components from a TCO result:

```python
from tco_model.terminology import get_component_value

# NPV component access
acquisition_cost = get_component_value(result.npv_costs, "acquisition")
insurance_reg_cost = get_component_value(result.npv_costs, "insurance_registration")

# Annual cost access
year_2_energy = get_component_value(result.annual_costs, "energy", 2)
```

Or use the collection properties directly:

```python
# Get list of all years' values
acquisition_costs = result.annual_costs.acquisition
total_costs = result.annual_costs.total

# Get single year value
year_3_energy = result.annual_costs[3].energy
```

## Working with Configuration Files

All configuration files should follow standardized structure:

```yaml
vehicle_info:
  type: "battery_electric"
  category: "articulated"
  name: "Example BET"

purchase:
  base_price_2025: 400000
  annual_price_decrease_real: 0.02

energy_consumption:
  base_rate_kwh_per_km: 1.5
  min_rate: 1.4
  max_rate: 1.6
  load_adjustment_factor: 0.15
```

### Loading Configuration Files

To load configuration files with proper field mapping:

```python
from utils.helpers import load_config_as_model
from tco_model.models import BETParameters

# File will be transformed to match the model's field structure
bet_params = load_config_as_model("config/vehicles/example_bet.yaml", BETParameters)
```

## Using Strategies

Strategy classes follow a standardized naming pattern:
- `{VehiclePrefix}{Implementation}{Function}Strategy`

Examples:
- `BETEnergyConsumptionStrategy`
- `DistanceBasedMaintenanceStrategy`
- `ValueBasedInsuranceStrategy`

Get strategy instances using the factory:

```python
from tco_model.strategies import StrategyFactory

# Get vehicle-specific strategy
bet_energy_strategy = StrategyFactory.get_strategy("energy", "battery_electric")

# Get strategy with specific implementation
distance_maintenance = StrategyFactory.get_strategy("maintenance", implementation="distance_based")
```

## Working with UI Components

Standard UI component keys:
- `acquisition`
- `energy`
- `maintenance`
- `infrastructure`
- `battery_replacement`
- `insurance_registration` (combined)
- `taxes_levies` (combined)
- `residual_value`

Access UI-specific component info:

```python
from tco_model.terminology import UI_COMPONENT_MAPPING, get_ui_component_label

# Get display name
label = get_ui_component_label("insurance_registration")  # "Insurance & Registration"

# Get standard color
color = UI_COMPONENT_MAPPING["energy"].get("color", "#333333")
```
```

## Updated Implementation Schedule

| Phase | Description | Time Estimate | Dependencies |
|-------|-------------|---------------|-------------|
| 1 | Core Model Updates | 2 days | None |
| 2 | Calculator Logic Updates | 1 day | Phase 1 |
| 3 | UI Component Updates | 1 day | Phase 1 |
| 4 | Configuration and Helper Updates | 1 day | Phase 1 |
| 5 | Test Updates | 2 days | Phases 1, 2 |
| 6 | Standardizing Strategy Pattern | 2 days | Phase 1 |
| 7 | Final Documentation and Cleanup | 1 day | Phases 1-6 |
| 8 | Strategy Pattern and Vehicle Transformation Standardization | 2 days | Phase 6 |
| 9 | Configuration File Standardization | 2 days | Phases 4, 7 |
| 10 | Standardized Component Access | 1 day | Phases 1, 3 |
| 11 | Strategy Pattern Standardization | 2 days | Phases 6, 8 |
| 12 | Testing and Documentation Improvements | 2 days | All previous phases |

## Updated Risks and Mitigation

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Breaking API compatibility | High | High | Add temporary compatibility properties, thorough testing |
| Test failures | High | Medium | Update tests incrementally alongside model changes |
| UI display issues | Medium | Medium | Test UI components with comprehensive test data |
| Inconsistent field names in code | Medium | Medium | Use find-and-replace with regex to locate all references |
| Performance impact of new collection class | Low | Low | Profile and optimize if needed |
| Configuration file inconsistencies | High | Medium | Create automated config checker script |
| Strategy name collisions | Medium | Low | Use factory pattern to abstract strategy instantiation |
| Missing documentation updates | Medium | Medium | Create automated check for outdated docs |