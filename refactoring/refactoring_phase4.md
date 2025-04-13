# Phase 4: Testing and Validation

This document outlines the implementation steps for Phase 4 of the field refactoring project, focusing on updating the test suite to work with the new standardized field names and structures.

## Goals

- Update test assertions to use new field names
- Create comprehensive tests for new collection classes
- Test component access patterns
- Ensure backward compatibility during transition
- Validate standardized strategy pattern

## Implementation Steps

### Step 1: Update Integration Test Assertions

Update the test assertions in `tests/integration/test_calculator.py` to use the new field names and structures:

```python
def test_calculate_bet_scenario(self, bet_scenario):
    """Test that the calculator produces valid results for a BET scenario."""
    calculator = TCOCalculator()
    
    result = calculator.calculate(bet_scenario)
    
    # Verify basic structure and properties of the result using new field names
    assert result.total_tco is not None  # Changed from npv_total
    assert result.lcod is not None       # Changed from lcod_per_km
    assert result.scenario == bet_scenario  # New property
    
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
    
    # Verify result is reasonably close to expected values
    # These are just example assertions - actual values would be determined by test data
    assert result.total_tco > 0
    assert result.lcod > 0
    
    # Verify that the totals add up correctly
    component_sum = (
        result.npv_costs.acquisition +
        result.npv_costs.energy +
        result.npv_costs.maintenance +
        result.npv_costs.infrastructure +
        result.npv_costs.battery_replacement +
        result.npv_costs.insurance +
        result.npv_costs.registration +
        result.npv_costs.carbon_tax +
        result.npv_costs.other_taxes +
        result.npv_costs.residual_value
    )
    assert abs(result.total_tco - component_sum) < 0.01  # Allow for small rounding errors
```

### Step 2: Update Test Mocks and Fixtures

Update the mock objects in `tests/integration/test_payback.py` to use the new field names and structures:

```python
# Convert the list of AnnualCosts to an AnnualCostsCollection
annual_costs_list = [
    AnnualCosts(
        year=0, 
        calendar_year=2023, 
        acquisition=100000, 
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
    AnnualCosts(
        year=1,
        calendar_year=2024,
        acquisition=0,
        energy=11000,
        maintenance=5500,
        infrastructure=0,
        battery_replacement=0,
        insurance=5250,
        registration=1050,
        carbon_tax=0,
        other_taxes=0,
        residual_value=0
    ),
    # ... other annual costs
]

# Create NPVCosts object
npv_costs1 = NPVCosts(
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

Update test fixture definitions in conftest.py to ensure they use the correct field patterns:

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
        AnnualCosts(
            year=1,
            calendar_year=2024,
            acquisition=0,
            energy=10500,
            maintenance=5250,
            infrastructure=0,
            battery_replacement=0,
            insurance=5250,
            registration=1050,
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

### Step 4: Create Field Renaming Tests

Add specific tests for the field renaming to verify backward compatibility:

```python
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
        from tco_model.terminology import get_canonical_field_name
        
        assert get_canonical_field_name("npv_total") == "total_tco"
        assert get_canonical_field_name("lcod_per_km") == "lcod"
        assert get_canonical_field_name("npv_difference") == "tco_difference"
        assert get_canonical_field_name("unchanged_field") == "unchanged_field"
    
    def test_component_differences_property(self):
        """Test the component_differences property in ComparisonResult."""
        # Create two TCO outputs with different costs
        output1 = create_test_output(
            acquisition=100000,
            energy=50000,
            maintenance=25000
        )
        
        output2 = create_test_output(
            acquisition=120000,
            energy=40000,
            maintenance=30000
        )
        
        # Create comparison result
        comparison = ComparisonResult.create(output1, output2)
        
        # Test component differences
        diffs = comparison.component_differences
        assert diffs["acquisition"] == 20000  # 120000 - 100000
        assert diffs["energy"] == -10000      # 40000 - 50000
        assert diffs["maintenance"] == 5000   # 30000 - 25000
        
        # Test cheaper_option property
        assert comparison.cheaper_option == 1  # output1 is cheaper
```

### Step 5: Create AnnualCostsCollection Tests

Add specific tests for the new AnnualCostsCollection class:

```python
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
        # Since we didn't set insurance or registration, these would default to 0
        assert collection.insurance_registration == [0, 0]
    
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
        
        # Use the standardized component access function
        from tco_model.terminology import get_component_value
        
        # Test direct access to year's component
        assert get_component_value(collection, "acquisition", 0) == 50000
        assert get_component_value(collection, "energy", 1) == 10500
        
        # Test combined component access
        assert get_component_value(collection, "insurance_registration", 0) == 3000
        assert get_component_value(collection, "taxes_levies", 1) == 880
```

### Step 6: Test Strategy Factory

Create tests for the strategy factory and standardized strategy classes:

```python
class TestStrategyPattern:
    """Tests for the standardized strategy pattern."""
    
    def test_strategy_factory_registration(self):
        """Test that strategies can be registered and retrieved from the factory."""
        from tco_model.strategies import StrategyFactory
        
        # Create a test strategy class
        class TestStrategy:
            def calculate(self): 
                return "test result"
        
        # Register the strategy
        StrategyFactory.register_strategy(
            "test_domain", "test_vehicle", "test_implementation", TestStrategy
        )
        
        # Retrieve the strategy
        strategy = StrategyFactory.get_strategy(
            "test_domain", "test_vehicle", "test_implementation"
        )
        
        # Verify it's the right type and works
        assert isinstance(strategy, TestStrategy)
        assert strategy.calculate() == "test result"
    
    def test_strategy_fallback(self):
        """Test that the factory uses fallback strategies correctly."""
        from tco_model.strategies import StrategyFactory
        
        # Create test strategy classes
        class DefaultStrategy:
            def calculate(self): 
                return "default"
                
        class VehicleSpecificStrategy:
            def calculate(self): 
                return "vehicle specific"
        
        # Register strategies
        StrategyFactory.register_strategy(
            "test_domain2", None, None, DefaultStrategy
        )
        StrategyFactory.register_strategy(
            "test_domain2", "specific_vehicle", None, VehicleSpecificStrategy
        )
        
        # Test fallback to default
        default_strategy = StrategyFactory.get_strategy(
            "test_domain2", "unknown_vehicle", "unknown_implementation"
        )
        assert default_strategy.calculate() == "default"
        
        # Test specific match
        specific_strategy = StrategyFactory.get_strategy(
            "test_domain2", "specific_vehicle", "unknown_implementation"
        )
        assert specific_strategy.calculate() == "vehicle specific"
    
    def test_energy_consumption_strategy(self):
        """Test that energy consumption strategies are correctly renamed and work."""
        from tco_model.strategies import get_energy_consumption_strategy
        from tco_model.models import VehicleType
        
        # Get strategies for different vehicle types
        bet_strategy = get_energy_consumption_strategy(VehicleType.BATTERY_ELECTRIC)
        diesel_strategy = get_energy_consumption_strategy(VehicleType.DIESEL)
        
        # Verify they are of the correct type
        assert bet_strategy.__class__.__name__ == "BETEnergyConsumptionStrategy"
        assert diesel_strategy.__class__.__name__ == "DieselConsumptionStrategy"
```

### Step 7: Update Comparison Tests

Update tests for the comparison functionality:

```python
def test_compare_results(self, bet_scenario, diesel_scenario):
    """Test that the calculator correctly compares two results."""
    calculator = TCOCalculator()
    
    result1 = calculator.calculate(bet_scenario)
    result2 = calculator.calculate(diesel_scenario)
    
    comparison = calculator.compare_results(result1, result2)
    
    # Verify comparison uses new field names
    assert hasattr(comparison, 'tco_difference')  # Renamed from npv_difference
    assert hasattr(comparison, 'tco_percentage')  # Renamed from npv_difference_percentage
    assert hasattr(comparison, 'lcod_difference')
    assert hasattr(comparison, 'lcod_difference_percentage')
    assert hasattr(comparison, 'payback_year')
    
    # Test new component_differences property
    assert hasattr(comparison, 'component_differences')
    diffs = comparison.component_differences
    
    # Should have the standardized UI components
    assert "acquisition" in diffs
    assert "energy" in diffs
    assert "maintenance" in diffs
    assert "insurance_registration" in diffs
    assert "taxes_levies" in diffs
    
    # Test cheaper_option property
    assert comparison.cheaper_option in [1, 2]
    if comparison.tco_difference > 0:
        assert comparison.cheaper_option == 1
    else:
        assert comparison.cheaper_option == 2
```

### Step 8: Test Utility Functions

Add tests for the utility functions in terminology.py:

```python
class TestUtilityFunctions:
    """Tests for utility functions in terminology.py."""
    
    def test_get_component_value(self):
        """Test the get_component_value function."""
        from tco_model.terminology import get_component_value
        
        # Create test objects
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
        
        # Test default return
        assert get_component_value(npv_costs, "nonexistent_component") == 0.0
    
    def test_calculate_cost_difference(self):
        """Test the calculate_cost_difference function."""
        from tco_model.terminology import calculate_cost_difference
        
        # Test positive difference
        diff, pct = calculate_cost_difference(100, 150)
        assert diff == 50
        assert pct == 50.0
        
        # Test negative difference
        diff, pct = calculate_cost_difference(200, 150)
        assert diff == -50
        assert pct == -25.0
        
        # Test zero first value
        diff, pct = calculate_cost_difference(0, 100)
        assert diff == 100
        assert pct == 0.0  # Special case to avoid division by zero
```

## Results and Benefits

- Comprehensive test coverage for new field names
- Validation of backward compatibility
- Tests for new collection classes and access patterns
- Verification of strategy factory functionality
- Clear examples of how to use the new APIs

## Acceptance Criteria

- [ ] All tests pass with the new field names
- [ ] Backward compatibility is verified during transition
- [ ] Component access patterns are tested
- [ ] Strategy factory is tested
- [ ] Collection class functionality is verified
- [ ] Utility functions are tested 