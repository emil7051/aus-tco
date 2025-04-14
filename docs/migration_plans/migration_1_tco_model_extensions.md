# Migration 1: TCO Model Extensions

## Overview

This first migration phase focuses on extending the TCO model to support all the functionality required by the enhanced UI components. No UI integration happens in this phase - the goal is to prepare the model layer with all necessary data and calculations.

## Implementation Tasks

### 1. Add Environmental Impact Calculations

Extend the TCO calculator to include emissions and environmental impact data:

```python
# In tco_model/models.py

@dataclass
class EmissionsData:
    """Emissions data for a vehicle."""
    annual_co2_tonnes: List[float]  # CO2 emissions per year
    total_co2_tonnes: float  # Total lifetime CO2 emissions
    energy_consumption_kwh: float  # Total energy consumption in kWh
    energy_per_km: float  # Energy consumption per km
    co2_per_km: float  # CO2 emissions per km
    trees_equivalent: int  # Number of trees needed to offset emissions
    homes_equivalent: float  # Equivalent to homes' annual energy use
    cars_equivalent: float  # Equivalent to passenger vehicles for a year

@dataclass
class TCOOutput:
    # Existing fields...
    vehicle_name: str
    vehicle_type: str
    total_tco: float
    lcod: float
    annual_costs: List[float]
    analysis_period_years: int
    lifetime_distance: float
    scenario: Any  # Reference to original input scenario
    cost_components: Dict[str, float]  # Component costs
    
    # New field for emissions data
    emissions: Optional[EmissionsData] = None
```

```python
# In tco_model/calculator.py

def calculate(self, scenario: ScenarioInput) -> TCOOutput:
    """Calculate TCO for a given scenario."""
    # Existing calculation code...
    
    # Create TCO output
    result = TCOOutput(
        vehicle_name=scenario.name,
        vehicle_type=scenario.vehicle_type,
        total_tco=total_tco,
        lcod=lcod,
        annual_costs=annual_costs,
        analysis_period_years=scenario.analysis_period,
        lifetime_distance=lifetime_distance,
        scenario=scenario,
        cost_components=component_costs
    )
    
    # Calculate and add emissions data
    result.emissions = self.calculate_emissions(scenario, result)
    
    return result

def calculate_emissions(self, scenario: ScenarioInput, result: TCOOutput) -> EmissionsData:
    """Calculate emissions data for a scenario and TCO result."""
    annual_co2 = []
    total_co2 = 0
    energy_consumption = 0
    
    if scenario.vehicle_type == "battery_electric":
        # Calculate BET emissions from electricity
        for year in range(scenario.analysis_period):
            # Calculate based on electricity consumption and grid emissions intensity
            annual_energy_kwh = scenario.annual_distance * scenario.energy_consumption
            annual_emissions = annual_energy_kwh * scenario.grid_emissions_intensity / 1000  # tonnes
            annual_co2.append(annual_emissions)
            total_co2 += annual_emissions
            energy_consumption += annual_energy_kwh
    else:
        # Calculate diesel emissions
        for year in range(scenario.analysis_period):
            # Calculate based on fuel consumption and diesel emissions factor
            annual_fuel_l = scenario.annual_distance * scenario.fuel_consumption / 100
            annual_emissions = annual_fuel_l * self.DIESEL_EMISSIONS_FACTOR / 1000  # tonnes
            annual_co2.append(annual_emissions)
            total_co2 += annual_emissions
            # Convert diesel to energy equivalent
            energy_consumption += annual_fuel_l * self.DIESEL_ENERGY_DENSITY
    
    # Calculate equivalents
    trees_equivalent = int(total_co2 * self.TREES_PER_TONNE_CO2)
    homes_equivalent = total_co2 * self.HOMES_PER_TONNE_CO2
    cars_equivalent = total_co2 * self.CARS_PER_TONNE_CO2
    
    return EmissionsData(
        annual_co2_tonnes=annual_co2,
        total_co2_tonnes=total_co2,
        energy_consumption_kwh=energy_consumption,
        energy_per_km=energy_consumption / result.lifetime_distance,
        co2_per_km=total_co2 * 1000000 / result.lifetime_distance,  # g/km
        trees_equivalent=trees_equivalent,
        homes_equivalent=homes_equivalent,
        cars_equivalent=cars_equivalent
    )
```

### 2. Implement Investment Analysis

Add support for financial investment analysis:

```python
# In tco_model/models.py

@dataclass
class InvestmentAnalysis:
    """Investment analysis between two vehicles."""
    payback_years: Optional[float]  # Years to payback initial investment
    roi: Optional[float]  # Return on investment percentage
    npv_difference: float  # Net present value difference
    irr: Optional[float]  # Internal rate of return
    has_payback: bool  # Whether payback occurs within analysis period

@dataclass
class ComparisonResult:
    # Existing fields...
    vehicle_1_id: int
    vehicle_2_id: int
    tco_difference: float
    tco_percentage: float
    lcod_difference: float
    lcod_difference_percentage: float
    cheaper_option: int
    component_differences: Dict[str, float]
    
    # New field for investment analysis
    investment_analysis: Optional[InvestmentAnalysis] = None
```

```python
# In tco_model/calculator.py

def compare(self, result1: TCOOutput, result2: TCOOutput) -> ComparisonResult:
    """Compare two TCO results."""
    # Existing comparison code...
    
    # Calculate cost differences
    tco_difference = result2.total_tco - result1.total_tco
    lcod_difference = result2.lcod - result1.lcod
    
    # Calculate percentage differences
    if result1.total_tco != 0:
        tco_percentage = (tco_difference / result1.total_tco) * 100
    else:
        tco_percentage = 0
        
    if result1.lcod != 0:
        lcod_percentage = (lcod_difference / result1.lcod) * 100
    else:
        lcod_percentage = 0
    
    # Determine which option is cheaper
    cheaper_option = 1 if tco_difference > 0 else 2 if tco_difference < 0 else 0
    
    # Calculate component differences
    component_differences = calculate_component_differences(result1, result2)
    
    # Create comparison result
    comparison = ComparisonResult(
        vehicle_1_id=1,
        vehicle_2_id=2,
        tco_difference=tco_difference,
        tco_percentage=tco_percentage,
        lcod_difference=lcod_difference,
        lcod_difference_percentage=lcod_percentage,
        cheaper_option=cheaper_option,
        component_differences=component_differences
    )
    
    # Add investment analysis
    comparison.investment_analysis = self.analyze_investment(result1, result2)
    
    return comparison

def analyze_investment(self, result1: TCOOutput, result2: TCOOutput) -> InvestmentAnalysis:
    """Perform investment analysis between two vehicles."""
    # Determine which vehicle has higher upfront cost
    from tco_model.terminology import get_component_value
    
    upfront_cost_1 = get_component_value(result1, "acquisition")
    upfront_cost_2 = get_component_value(result2, "acquisition")
    
    # Only do investment analysis if one has higher upfront cost and lower total cost
    if upfront_cost_1 == upfront_cost_2:
        return InvestmentAnalysis(
            payback_years=None,
            roi=None,
            npv_difference=result2.total_tco - result1.total_tco,
            irr=None,
            has_payback=False
        )
    
    # Configure the high upfront cost vehicle as the investment
    if upfront_cost_1 > upfront_cost_2:
        # Vehicle 1 is the investment
        investment_vehicle = result1
        baseline_vehicle = result2
        upfront_diff = upfront_cost_1 - upfront_cost_2
        # Investment makes sense if total TCO is less despite higher upfront
        if result1.total_tco >= result2.total_tco:
            # Not a good investment
            return InvestmentAnalysis(
                payback_years=None,
                roi=None,
                npv_difference=result1.total_tco - result2.total_tco,
                irr=None,
                has_payback=False
            )
    else:
        # Vehicle 2 is the investment
        investment_vehicle = result2
        baseline_vehicle = result1
        upfront_diff = upfront_cost_2 - upfront_cost_1
        # Investment makes sense if total TCO is less despite higher upfront
        if result2.total_tco >= result1.total_tco:
            # Not a good investment
            return InvestmentAnalysis(
                payback_years=None,
                roi=None,
                npv_difference=result2.total_tco - result1.total_tco,
                irr=None,
                has_payback=False
            )
    
    # Calculate annual cash flows (negative means investment saves money)
    cash_flows = [upfront_diff]  # Initial investment
    for year in range(min(len(investment_vehicle.annual_costs), len(baseline_vehicle.annual_costs))):
        annual_diff = investment_vehicle.annual_costs[year] - baseline_vehicle.annual_costs[year]
        cash_flows.append(-annual_diff)  # Negative because saving money is positive cash flow
    
    # Calculate payback period
    cumulative_flow = cash_flows[0]  # Start with initial investment (positive)
    payback_years = None
    
    for year in range(1, len(cash_flows)):
        cumulative_flow += cash_flows[year]
        if cumulative_flow <= 0:
            # Fractional payback calculation
            previous_cumulative = cumulative_flow - cash_flows[year]
            fraction = -previous_cumulative / cash_flows[year]
            payback_years = year - 1 + fraction
            break
    
    # Calculate IRR
    irr = None
    try:
        import numpy as np
        irr = np.irr(cash_flows) * 100  # Convert to percentage
    except:
        pass  # IRR calculation may fail if no solution
    
    # Calculate ROI
    total_benefit = sum(cash_flows[1:])
    roi = (total_benefit - upfront_diff) / upfront_diff * 100 if upfront_diff > 0 else None
    
    # Calculate NPV difference
    npv_difference = baseline_vehicle.total_tco - investment_vehicle.total_tco
    
    return InvestmentAnalysis(
        payback_years=payback_years,
        roi=roi,
        npv_difference=npv_difference,
        irr=irr,
        has_payback=payback_years is not None
    )
```

### 3. Enhance Component Breakdown Access

Ensure consistent component categorization and access, aligning with terminology standards:

```python
# In tco_model/calculator.py

def get_component_value(self, result: TCOOutput, component: str) -> float:
    """
    Get value for a specific cost component from TCO result.
    
    Args:
        result: TCO result object
        component: Component name from UI_COMPONENT_KEYS
        
    Returns:
        Component value
    """
    from tco_model.terminology import UI_TO_MODEL_COMPONENT_MAPPING
    
    # Use explicit cost_components attribute
    if not hasattr(result, 'cost_components'):
        return 0
    
    # Handle combined UI components
    if component in UI_TO_MODEL_COMPONENT_MAPPING:
        # Get list of model components that make up this UI component
        model_components = UI_TO_MODEL_COMPONENT_MAPPING[component]
        value = 0.0
        for model_component in model_components:
            value += result.cost_components.get(model_component, 0)
        return value
    
    # Direct component access
    return result.cost_components.get(component, 0)

def get_component_percentage(self, result: TCOOutput, component: str) -> float:
    """
    Get percentage of total TCO for a specific component.
    
    Args:
        result: TCO result object
        component: Component name from UI_COMPONENT_KEYS
        
    Returns:
        Component percentage (0-100)
    """
    component_value = self.get_component_value(result, component)
    if result.total_tco == 0:
        return 0
    return component_value / result.total_tco * 100

def calculate_component_breakdown(self, result: TCOOutput) -> Dict[str, Dict[str, float]]:
    """
    Calculate detailed component breakdown with sub-components.
    
    Args:
        result: TCO result object
        
    Returns:
        Dictionary of component breakdowns with sub-components
    """
    from tco_model.terminology import UI_COMPONENT_KEYS
    
    if not hasattr(result, 'cost_components'):
        return {}
    
    breakdown = {}
    
    # Energy breakdown
    if "energy" in result.cost_components:
        energy_subcomponents = {}
        if result.vehicle_type == "battery_electric":
            # Electricity breakdown 
            energy_subcomponents["electricity_base"] = result.cost_components.get("energy", 0) * 0.7
            energy_subcomponents["electricity_demand"] = result.cost_components.get("energy", 0) * 0.3
        else:
            # Diesel breakdown
            energy_subcomponents["fuel_cost"] = result.cost_components.get("energy", 0) * 0.9
            energy_subcomponents["fuel_taxes"] = result.cost_components.get("energy", 0) * 0.1
        breakdown["energy"] = energy_subcomponents
    
    # Maintenance breakdown
    if "maintenance" in result.cost_components:
        maintenance_subcomponents = {}
        if result.vehicle_type == "battery_electric":
            maintenance_subcomponents["scheduled_maintenance"] = result.cost_components.get("maintenance", 0) * 0.4
            maintenance_subcomponents["unscheduled_repairs"] = result.cost_components.get("maintenance", 0) * 0.3
            maintenance_subcomponents["battery_maintenance"] = result.cost_components.get("maintenance", 0) * 0.3
        else:
            maintenance_subcomponents["scheduled_maintenance"] = result.cost_components.get("maintenance", 0) * 0.3
            maintenance_subcomponents["unscheduled_repairs"] = result.cost_components.get("maintenance", 0) * 0.4
            maintenance_subcomponents["engine_maintenance"] = result.cost_components.get("maintenance", 0) * 0.3
        breakdown["maintenance"] = maintenance_subcomponents
    
    # Add other component breakdowns according to terminology standards
    if "insurance" in result.cost_components and "registration" in result.cost_components:
        breakdown["insurance_registration"] = {
            "insurance": result.cost_components.get("insurance", 0),
            "registration": result.cost_components.get("registration", 0)
        }
    
    if "carbon_tax" in result.cost_components and "other_taxes" in result.cost_components:
        breakdown["taxes_levies"] = {
            "carbon_tax": result.cost_components.get("carbon_tax", 0),
            "other_taxes": result.cost_components.get("other_taxes", 0)
        }
    
    # Add acquisition, infrastructure, battery_replacement and residual_value
    # as single component breakdowns
    for component in ["acquisition", "infrastructure", "battery_replacement", "residual_value"]:
        if component in result.cost_components:
            breakdown[component] = {component: result.cost_components.get(component, 0)}
    
    return breakdown
```

### 4. Implement Sensitivity Analysis Engine

Add support for sensitivity analysis:

```python
# In tco_model/models.py

@dataclass
class SensitivityResult:
    """Result of sensitivity analysis."""
    parameter: str  # Parameter that was varied
    variation_values: List[float]  # List of parameter values
    tco_values: List[float]  # Resulting TCO values
    lcod_values: List[float]  # Resulting LCOD values
    original_value: float  # Original parameter value
    original_tco: float  # Original TCO value
    original_lcod: float  # Original LCOD value
    unit: str  # Unit of the parameter
    
@dataclass
class MultiParameterSensitivity:
    """Container for multiple sensitivity analyses."""
    results: Dict[str, SensitivityResult]  # Key is parameter name
```

```python
# In tco_model/calculator.py

def perform_sensitivity_analysis(self, scenario: ScenarioInput, parameter: str, 
                               variation_range: List[float]) -> SensitivityResult:
    """
    Perform sensitivity analysis for a given parameter.
    
    Args:
        scenario: Input scenario
        parameter: Parameter to vary
        variation_range: List of parameter values to test
        
    Returns:
        SensitivityResult with TCO values for each variation
    """
    import copy
    
    # Store original values
    original_value = getattr(scenario, parameter)
    original_scenario = copy.deepcopy(scenario)
    original_result = self.calculate(original_scenario)
    
    # Determine unit based on parameter using Australian spelling
    from utils.ui_terminology import get_australian_spelling
    
    parameter_units = {
        "diesel_price": "$/L",
        "electricity_price": "$/kWh",
        "annual_distance": "km",
        "analysis_period": "years",
        "discount_rate": "%",
        "fuel_consumption": "L/100km",
        "energy_consumption": "kWh/km"
        # Add other parameters and units
    }
    
    unit = parameter_units.get(parameter, "")
    
    # Calculate TCO for each variation
    tco_values = []
    lcod_values = []
    
    for variation in variation_range:
        # Create a new scenario with the varied parameter
        test_scenario = copy.deepcopy(scenario)
        setattr(test_scenario, parameter, variation)
        
        # Calculate TCO
        test_result = self.calculate(test_scenario)
        
        # Store results
        tco_values.append(test_result.total_tco)
        lcod_values.append(test_result.lcod)
    
    # Create sensitivity result
    return SensitivityResult(
        parameter=parameter,
        variation_values=variation_range,
        tco_values=tco_values,
        lcod_values=lcod_values,
        original_value=original_value,
        original_tco=original_result.total_tco,
        original_lcod=original_result.lcod,
        unit=get_australian_spelling(unit)
    )

def analyze_multiple_parameters(self, scenario: ScenarioInput, 
                              parameters: List[str]) -> MultiParameterSensitivity:
    """
    Analyze sensitivity to multiple parameters.
    
    Args:
        scenario: Input scenario
        parameters: List of parameters to analyze
        
    Returns:
        MultiParameterSensitivity with results for each parameter
    """
    results = {}
    
    # Define variation ranges using reasonable ranges
    variation_ranges = {
        "diesel_price": [p * scenario.diesel_price for p in [0.5, 0.75, 0.9, 1.0, 1.1, 1.25, 1.5]],
        "electricity_price": [p * scenario.electricity_price for p in [0.5, 0.75, 0.9, 1.0, 1.1, 1.25, 1.5]],
        "annual_distance": [p * scenario.annual_distance for p in [0.5, 0.75, 0.9, 1.0, 1.1, 1.25, 1.5]],
        "analysis_period": [max(1, scenario.analysis_period + y) for y in [-5, -3, -1, 0, 1, 3, 5]],
        "discount_rate": [max(1, scenario.discount_rate + p) for p in [-3, -2, -1, 0, 1, 2, 3]],
        # Add other parameters
    }
    
    # Analyze each parameter
    for parameter in parameters:
        if parameter in variation_ranges:
            results[parameter] = self.perform_sensitivity_analysis(
                scenario, 
                parameter, 
                variation_ranges[parameter]
            )
    
    return MultiParameterSensitivity(results=results)
```

### 5. Define Constants and Reference Data

Add constants and reference data needed for calculations:

```python
# In tco_model/calculator.py

# Add at class level or in __init__ method
# Using Australian spelling
DIESEL_EMISSIONS_FACTOR = 2.68  # kg CO2 per litre of diesel
DIESEL_ENERGY_DENSITY = 10.0  # kWh per litre of diesel
TREES_PER_TONNE_CO2 = 45  # Trees needed to absorb 1 tonne of CO2 annually
HOMES_PER_TONNE_CO2 = 0.12  # Average homes' annual energy use per tonne CO2
CARS_PER_TONNE_CO2 = 0.22  # Passenger vehicles driven for one year per tonne CO2
```

## Testing Implementation

Create tests for the new functionality:

```python
# In tests/test_calculator.py

def test_emissions_calculation():
    """Test emissions calculations for both vehicle types."""
    calculator = TCOCalculator()
    
    # Create BET scenario
    bet_scenario = ScenarioInput(
        vehicle_type="battery_electric",
        name="Test BET",
        annual_distance=80000,
        analysis_period=10,
        energy_consumption=1.2,  # kWh/km
        grid_emissions_intensity=0.8,  # kg CO2/kWh
        # Other parameters...
    )
    
    # Create diesel scenario
    diesel_scenario = ScenarioInput(
        vehicle_type="diesel",
        name="Test Diesel",
        annual_distance=80000,
        analysis_period=10,
        fuel_consumption=35,  # L/100km
        # Other parameters...
    )
    
    # Calculate results
    bet_result = calculator.calculate(bet_scenario)
    diesel_result = calculator.calculate(diesel_scenario)
    
    # Test BET emissions
    assert bet_result.emissions is not None
    assert len(bet_result.emissions.annual_co2_tonnes) == 10
    assert bet_result.emissions.total_co2_tonnes > 0
    
    # Test diesel emissions
    assert diesel_result.emissions is not None
    assert len(diesel_result.emissions.annual_co2_tonnes) == 10
    assert diesel_result.emissions.total_co2_tonnes > 0
    
    # Test that diesel has higher emissions using correct terminology
    assert diesel_result.emissions.total_co2_tonnes > bet_result.emissions.total_co2_tonnes

def test_investment_analysis():
    """Test investment analysis calculations."""
    calculator = TCOCalculator()
    
    # Create scenarios where BET has higher upfront but lower TCO
    bet_scenario = ScenarioInput(
        vehicle_type="battery_electric",
        name="Test BET",
        annual_distance=100000,
        analysis_period=8,
        acquisition_cost=500000,  # Higher upfront
        # Other parameters for lower operating costs...
    )
    
    diesel_scenario = ScenarioInput(
        vehicle_type="diesel",
        name="Test Diesel",
        annual_distance=100000,
        analysis_period=8,
        acquisition_cost=300000,  # Lower upfront
        # Other parameters for higher operating costs...
    )
    
    # Calculate and compare
    bet_result = calculator.calculate(bet_scenario)
    diesel_result = calculator.calculate(diesel_scenario)
    comparison = calculator.compare(bet_result, diesel_result)
    
    # Test investment analysis
    assert comparison.investment_analysis is not None
    assert comparison.investment_analysis.payback_years is not None
    assert comparison.investment_analysis.has_payback
    assert comparison.investment_analysis.roi is not None
    assert comparison.investment_analysis.roi > 0

def test_component_breakdown():
    """Test component breakdown calculations."""
    calculator = TCOCalculator()
    
    # Create BET scenario
    bet_scenario = ScenarioInput(
        vehicle_type="battery_electric",
        name="Test BET",
        # Other parameters...
    )
    
    # Calculate result
    bet_result = calculator.calculate(bet_scenario)
    
    # Get component values using terminology-compliant methods
    for component in UI_COMPONENT_KEYS:
        value = calculator.get_component_value(bet_result, component)
        percentage = calculator.get_component_percentage(bet_result, component)
        
        # Verify basic constraints
        assert percentage >= 0
        assert percentage <= 100 if component != "residual_value" else True
    
    # Get breakdown
    breakdown = calculator.calculate_component_breakdown(bet_result)
    
    # Verify energy breakdown for BET
    assert "energy" in breakdown
    assert "electricity_base" in breakdown["energy"]
    assert "electricity_demand" in breakdown["energy"]
    
    # Verify consistency with UI component mapping
    for component in UI_COMPONENT_KEYS:
        if component in breakdown:
            assert isinstance(breakdown[component], dict)

def test_sensitivity_analysis():
    """Test sensitivity analysis engine."""
    calculator = TCOCalculator()
    
    # Create test scenario
    scenario = ScenarioInput(
        vehicle_type="battery_electric",
        name="Test BET",
        annual_distance=100000,
        analysis_period=8,
        electricity_price=0.25,  # $/kWh
        # Other parameters...
    )
    
    # Define variations to test
    electricity_variations = [0.15, 0.20, 0.25, 0.30, 0.35]
    
    # Perform sensitivity analysis
    sensitivity = calculator.perform_sensitivity_analysis(
        scenario, 
        "electricity_price", 
        electricity_variations
    )
    
    # Test sensitivity result
    assert sensitivity is not None
    assert sensitivity.parameter == "electricity_price"
    assert len(sensitivity.variation_values) == 5
    assert len(sensitivity.tco_values) == 5
    assert len(sensitivity.lcod_values) == 5
    assert sensitivity.original_value == 0.25
    assert sensitivity.original_tco > 0
    assert sensitivity.unit == "$/kWh"
    
    # Verify that higher electricity price increases TCO
    assert sensitivity.tco_values[0] < sensitivity.tco_values[4]
    
    # Test multi-parameter analysis
    multi_sensitivity = calculator.analyze_multiple_parameters(
        scenario,
        ["electricity_price", "annual_distance"]
    )
    
    # Verify multi-parameter results
    assert "electricity_price" in multi_sensitivity.results
    assert "annual_distance" in multi_sensitivity.results
```

## Expected Outputs

After implementing the tasks in this migration:

1. The TCO model will be able to calculate emissions and environmental impact data for both vehicle types
2. Investment analysis will be available for comparing vehicles with different cost profiles
3. Detailed component breakdowns will be available for all cost categories following terminology standards
4. Sensitivity analysis will be supported for key input parameters
5. All tests will pass, verifying the correctness of the new functionality

These enhancements to the TCO model lay the foundation for the UI integration in the subsequent migration phases. 