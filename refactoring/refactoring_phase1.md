# Phase 1: Core Model Updates and Component Standardization

This document outlines the implementation steps for Phase 1 of the field refactoring project, focusing on standardizing the core model classes and component access patterns.

## Goals

- Standardize field names in core model classes
- Create consistent component access patterns
- Implement combined property access for UI components
- Establish a single source of truth for field naming

## Implementation Steps

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

Create a new wrapper class in `tco_model/models.py` that provides a consistent interface for annual costs:

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
    
    @property
    def residual_value(self) -> List[float]:
        """Get residual values for all years."""
        return [cost.residual_value for cost in self._costs]
    
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
        # Use consistent naming from terminology module
        from tco_model.terminology import UI_COMPONENT_KEYS, get_component_value
        
        result = {}
        # Loop through standardized component keys from terminology
        for component in UI_COMPONENT_KEYS:
            val1 = get_component_value(self.scenario_1.npv_costs, component)
            val2 = get_component_value(self.scenario_2.npv_costs, component)
            result[component] = val2 - val1
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
        
        # Use helper function from terminology to calculate percentage difference
        from tco_model.terminology import calculate_cost_difference
        _, tco_diff_pct = calculate_cost_difference(scenario_1.total_tco, scenario_2.total_tco)
            
        lcod_diff = scenario_2.lcod - scenario_1.lcod
        
        # Use same helper function for consistency
        _, lcod_diff_pct = calculate_cost_difference(scenario_1.lcod, scenario_2.lcod)
        
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

### Step 5: Standardize Component Access Utilities

Create standardized component access utilities in `tco_model/terminology.py`:

```python
def get_component_value(model: Any, component_name: str, year: Optional[int] = None) -> float:
    """
    Get a component value from a model object, handling composite components.
    
    Provides a standardized way to access component values from different model 
    objects (NPVCosts, AnnualCosts, AnnualCostsCollection) with support for 
    combined components.
    
    Args:
        model: The model object to get the component from
        component_name: The name of the component
        year: Optional year index for annual costs
        
    Returns:
        float: The component value
        
    Example:
        >>> # Get NPV energy costs
        >>> energy_cost = get_component_value(result.npv_costs, "energy")
        >>> # Get combined insurance and registration for year 2
        >>> insurance_reg = get_component_value(result.annual_costs, "insurance_registration", 2)
    """
    # Use constants for component mappings
    from tco_model.terminology import UI_TO_MODEL_COMPONENT_MAPPING
    
    # Handle combined components
    if component_name in UI_TO_MODEL_COMPONENT_MAPPING:
        # Get list of model components that make up this UI component
        model_components = UI_TO_MODEL_COMPONENT_MAPPING[component_name]
        value = 0.0
        for model_component in model_components:
            value += get_component_value(model, model_component, year)
        return value
    
    # Handle direct property access to combined components
    if hasattr(model, component_name):
        value = getattr(model, component_name)
        
        # Handle callable properties
        if callable(value):
            value = value()
            
        # Use helper function to check if we need to access a specific year
        if _is_year_access_needed(value, year):
            return value[year]
            
        # Handle case where property is a direct value
        if not isinstance(value, (list, dict)) or year is None:
            return value
    
    # Handle annual costs with year index
    if _is_valid_year_index(model, year):
        annual_cost = model[year]
        if hasattr(annual_cost, component_name):
            return getattr(annual_cost, component_name)
    
    # Default fallback
    return 0.0


def _is_year_access_needed(value, year):
    """
    Determine if we need to access a specific year from a list property.
    
    Args:
        value: The property value
        year: The year index to access
        
    Returns:
        bool: True if we should access a specific year, False otherwise
    """
    return isinstance(value, list) and year is not None and year < len(value)


def _is_valid_year_index(model, year):
    """
    Check if the model supports indexing and the year is valid.
    
    Args:
        model: The model to check
        year: The year index to check
        
    Returns:
        bool: True if the year index is valid, False otherwise
    """
    return year is not None and hasattr(model, "__getitem__") and year < len(model)
```

## Results and Benefits

- Consistent field naming across all models
- Single source of truth for component access
- Support for UI-specific combined components
- Backward compatibility during transition
- Clean encapsulation of access patterns
- Improved documentation with examples
- Elimination of duplicated component mapping code

## Acceptance Criteria

- [ ] All model classes use standardized field names
- [ ] Backward compatibility properties are implemented with deprecation warnings
- [ ] Component access patterns work consistently for all component types
- [ ] All helper functions have clear documentation with examples
- [ ] No duplicated mapping logic across the codebase 