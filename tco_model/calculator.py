"""
TCO Calculator Module

This module implements the core TCO calculation engine that orchestrates the calculation
of all cost components and produces the final TCO results.
"""

from typing import Dict, List, Optional, Union, Any
import pandas as pd
import numpy as np
import numpy_financial as npf
from datetime import date

from tco_model.models import (
    ScenarioInput,
    TCOOutput,
    AnnualCosts,
    NPVCosts,
    ComparisonResult,
    VehicleType,
    AnnualCostsCollection,
    EmissionsData,
    InvestmentAnalysis,
)
from tco_model.costs import (
    calculate_acquisition_costs,
    calculate_energy_costs,
    calculate_maintenance_costs,
    calculate_infrastructure_costs,
    calculate_battery_replacement_costs,
    calculate_insurance_registration_costs,
    calculate_taxes_levies,
    calculate_residual_value,
)
from tco_model.strategies import (
    get_energy_consumption_strategy,
    get_maintenance_strategy,
    get_residual_value_strategy,
    get_battery_replacement_strategy,
    get_infrastructure_strategy,
    get_financing_strategy,
    get_insurance_strategy,
    get_registration_strategy,
    get_carbon_tax_strategy,
)


class TCOCalculator:
    """
    TCO Calculator class responsible for calculating the Total Cost of Ownership
    for heavy vehicles based on the provided scenario inputs.
    """
    
    # Constants for emissions calculations using Australian spelling
    DIESEL_EMISSIONS_FACTOR = 2.68  # kg CO2 per litre of diesel
    DIESEL_ENERGY_DENSITY = 10.0  # kWh per litre of diesel
    TREES_PER_TONNE_CO2 = 45  # Trees needed to absorb 1 tonne of CO2 annually
    HOMES_PER_TONNE_CO2 = 0.12  # Average homes' annual energy use per tonne CO2
    CARS_PER_TONNE_CO2 = 0.22  # Passenger vehicles driven for one year per tonne CO2
    
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
                - npv_costs: NPV breakdown of costs by component
        """
        # Constants for readability
        FIRST_YEAR = 0
        
        # Extract key parameters
        analysis_period = scenario.economic.analysis_period_years
        discount_rate = scenario.economic.discount_rate_real
        annual_distance = scenario.operational.annual_distance_km
        base_year = date.today().year
        
        # Initialize dataframe to store annual costs
        # Using a DataFrame for efficient year-by-year calculations with vectorization benefits
        years = range(analysis_period)
        annual_costs_df = pd.DataFrame(index=years)
        annual_costs_df['year'] = years
        annual_costs_df['calendar_year'] = [base_year + year for year in years]
        
        # Get appropriate strategies based on vehicle type and characteristics
        energy_strategy = get_energy_consumption_strategy(scenario.vehicle.type)
        maintenance_strategy = get_maintenance_strategy(scenario.vehicle.type)
        residual_value_strategy = get_residual_value_strategy()
        infrastructure_strategy = get_infrastructure_strategy(scenario.vehicle.type)
        financing_strategy = get_financing_strategy(scenario.financing.method)
        insurance_strategy = get_insurance_strategy()
        registration_strategy = get_registration_strategy()
        carbon_tax_strategy = get_carbon_tax_strategy()
        
        # For BETs, get battery replacement strategy
        battery_replacement_strategy = None
        if scenario.vehicle.type == VehicleType.BET:
            battery_replacement_strategy = get_battery_replacement_strategy()
        
        # Calculate individual cost components for each year
        for year in years:
            # Calculate acquisition costs
            annual_costs_df.loc[year, 'acquisition'] = financing_strategy.calculate_costs(
                scenario, year
            )
            
            # Calculate energy costs
            annual_costs_df.loc[year, 'energy'] = energy_strategy.calculate_costs(
                scenario, year
            )
            
            # Calculate maintenance costs
            annual_costs_df.loc[year, 'maintenance'] = maintenance_strategy.calculate_costs(
                scenario, year
            )
            
            # Calculate infrastructure costs (mainly for BETs)
            annual_costs_df.loc[year, 'infrastructure'] = infrastructure_strategy.calculate_costs(
                scenario, year
            )
            
            # Calculate battery replacement costs (only for BETs)
            annual_costs_df.loc[year, 'battery_replacement'] = (
                battery_replacement_strategy.calculate_costs(scenario, year)
                if battery_replacement_strategy and scenario.vehicle.type == VehicleType.BET
                else 0
            )
            
            # Calculate insurance costs
            annual_costs_df.loc[year, 'insurance'] = insurance_strategy.calculate_costs(
                scenario, year
            )
            
            # Calculate registration costs
            annual_costs_df.loc[year, 'registration'] = registration_strategy.calculate_costs(
                scenario, year
            )
            
            # Calculate carbon tax
            annual_costs_df.loc[year, 'carbon_tax'] = carbon_tax_strategy.calculate_costs(
                scenario, year
            )
            
            # Calculate other taxes and levies (simplified, using direct function call)
            annual_costs_df.loc[year, 'other_taxes'] = calculate_taxes_levies(
                scenario, year
            )
            
            # Calculate residual value (only applied in the final year)
            annual_costs_df.loc[year, 'residual_value'] = (
                residual_value_strategy.calculate_residual_value(scenario, year)
                if year == analysis_period - 1
                else 0
            )
        
        # Calculate annual totals
        # This vectorized operation efficiently calculates the sum for each row
        annual_costs_df['total'] = annual_costs_df[[
            'acquisition', 'energy', 'maintenance', 'infrastructure',
            'battery_replacement', 'insurance', 'registration',
            'carbon_tax', 'other_taxes', 'residual_value'
        ]].sum(axis=1)
        
        # Calculate NPV for each cost component using numpy-financial
        # Extract cost streams for NPV calculation
        cost_components = [
            'acquisition', 'energy', 'maintenance', 'infrastructure',
            'battery_replacement', 'insurance', 'registration',
            'carbon_tax', 'other_taxes', 'residual_value', 'total'
        ]
        
        npv_costs = {}
        for component in cost_components:
            cash_flows = annual_costs_df[component].values
            npv_costs[component] = npf.npv(discount_rate, cash_flows)
        
        # Calculate nominal total (sum of all costs without discounting)
        total_nominal_cost = annual_costs_df['total'].sum()
        
        # Calculate levelized cost of driving (LCOD) per km
        total_distance_km = annual_distance * analysis_period
        lcod = npv_costs['total'] / total_distance_km if total_distance_km > 0 else 0
        
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
        annual_costs_collection = AnnualCostsCollection(costs=annual_costs_list)
        
        # Create TCO output
        result = TCOOutput(
            scenario_name=scenario.scenario_name,
            vehicle_name=scenario.vehicle.name,
            vehicle_type=scenario.vehicle.type,
            analysis_period_years=analysis_period,
            total_distance_km=total_distance_km,
            annual_costs=annual_costs_collection,
            npv_costs=npv_costs_obj,
            total_nominal_cost=total_nominal_cost,
            total_tco=npv_costs['total'],
            lcod=lcod,
            calculation_date=date.today()
        )
        
        # Store original scenario for testing
        result._scenario = scenario
        
        # Calculate and add emissions data
        result.emissions = self.calculate_emissions(scenario, result)
        
        return result
    
    def calculate_emissions(self, scenario: ScenarioInput, result: TCOOutput) -> EmissionsData:
        """
        Calculate emissions data for a scenario and TCO result.
        
        Args:
            scenario: Input scenario
            result: TCO result
        
        Returns:
            EmissionsData with emissions calculations
        """
        annual_co2 = []
        total_co2 = 0
        energy_consumption = 0
        
        if scenario.vehicle.type == VehicleType.BET:
            # Calculate BET emissions from electricity
            for year in range(scenario.economic.analysis_period_years):
                # Calculate based on electricity consumption and grid emissions intensity
                annual_energy_kwh = scenario.operational.annual_distance_km * scenario.vehicle.energy_consumption.base_rate
                annual_emissions = annual_energy_kwh * 0.8 / 1000  # tonnes (assuming 0.8 kg CO2/kWh grid intensity)
                annual_co2.append(annual_emissions)
                total_co2 += annual_emissions
                energy_consumption += annual_energy_kwh
        else:
            # Calculate diesel emissions
            for year in range(scenario.economic.analysis_period_years):
                # Calculate based on fuel consumption and diesel emissions factor
                annual_fuel_l = scenario.operational.annual_distance_km * scenario.vehicle.fuel_consumption.base_rate
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
            energy_per_km=energy_consumption / result.total_distance_km,
            co2_per_km=total_co2 * 1000000 / result.total_distance_km,  # g/km
            trees_equivalent=trees_equivalent,
            homes_equivalent=homes_equivalent,
            cars_equivalent=cars_equivalent
        )
    
    def compare(self, result1: TCOOutput, result2: TCOOutput) -> ComparisonResult:
        """
        Compare two TCO results and generate a comparison result.
        
        Args:
            result1: First TCO result
            result2: Second TCO result
            
        Returns:
            ComparisonResult: The comparison between the two TCO results
        """
        # Calculate TCO difference and percentage
        tco_difference = result2.total_tco - result1.total_tco
        
        # Calculate percentage differences
        if result1.total_tco != 0:
            tco_percentage = (tco_difference / result1.total_tco) * 100
        else:
            tco_percentage = 0
            
        if result1.lcod != 0:
            lcod_percentage = ((result2.lcod - result1.lcod) / result1.lcod) * 100
        else:
            lcod_percentage = 0
        
        # Determine which option is cheaper
        cheaper_option = 1 if tco_difference > 0 else 2 if tco_difference < 0 else 0
        
        # Calculate component differences
        component_differences = self.calculate_component_differences(result1, result2)
        
        # Create comparison result
        comparison = ComparisonResult(
            scenario_1=result1,
            scenario_2=result2,
            tco_difference=tco_difference,
            tco_percentage=tco_percentage,
            lcod_difference=result2.lcod - result1.lcod,
            lcod_difference_percentage=lcod_percentage,
            payback_year=self._calculate_payback_year(result1, result2),
        )
        
        # Add investment analysis
        comparison.investment_analysis = self.analyze_investment(result1, result2)
        
        return comparison
    
    def analyze_investment(self, result1: TCOOutput, result2: TCOOutput) -> InvestmentAnalysis:
        """
        Perform investment analysis between two vehicles.
        
        Args:
            result1: First TCO result
            result2: Second TCO result
            
        Returns:
            InvestmentAnalysis with financial metrics
        """
        # Determine which vehicle has higher upfront cost
        upfront_cost_1 = self.get_component_value(result1, "acquisition")
        upfront_cost_2 = self.get_component_value(result2, "acquisition")
        
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
            annual_diff = investment_vehicle.annual_costs[year].total - baseline_vehicle.annual_costs[year].total
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
            irr = npf.irr(cash_flows) * 100  # Convert to percentage
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
    
    def calculate_component_differences(self, result1: TCOOutput, result2: TCOOutput) -> Dict[str, float]:
        """
        Calculate differences in cost components between two TCO results.
        
        Args:
            result1: First TCO result
            result2: Second TCO result
            
        Returns:
            Dictionary of component differences
        """
        from tco_model.terminology import UI_COMPONENT_KEYS
        
        differences = {}
        
        for component in UI_COMPONENT_KEYS:
            value1 = self.get_component_value(result1, component)
            value2 = self.get_component_value(result2, component)
            differences[component] = value2 - value1
            
        return differences
    
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
            if result.vehicle_type == VehicleType.BET:
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
            if result.vehicle_type == VehicleType.BET:
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
    
    def perform_sensitivity_analysis(self, scenario: ScenarioInput, parameter: str, 
                                  variation_range: List[float]) -> Dict[str, Any]:
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
        original_value = None
        for attr_name in parameter.split('.'):
            if original_value is None:
                original_value = getattr(scenario, attr_name, None)
            else:
                original_value = getattr(original_value, attr_name, None)
                
        if original_value is None:
            raise ValueError(f"Parameter {parameter} not found in scenario")
            
        original_scenario = copy.deepcopy(scenario)
        original_result = self.calculate(original_scenario)
        
        # Determine unit based on parameter using Australian spelling
        parameter_units = {
            "economic.diesel_price_aud_per_l": "$/L",
            "economic.electricity_price_aud_per_kwh": "$/kWh",
            "operational.annual_distance_km": "km",
            "economic.analysis_period_years": "years",
            "economic.discount_rate_real": "%",
            "vehicle.fuel_consumption.base_rate": "L/100km",
            "vehicle.energy_consumption.base_rate": "kWh/km"
            # Add other parameters and units
        }
        
        unit = parameter_units.get(parameter, "")
        
        # Calculate TCO for each variation
        tco_values = []
        lcod_values = []
        
        for variation in variation_range:
            # Create a new scenario with the varied parameter
            test_scenario = copy.deepcopy(scenario)
            
            # Set the varied parameter
            current_obj = test_scenario
            attr_parts = parameter.split('.')
            
            # Navigate to the correct object
            for i, attr_name in enumerate(attr_parts):
                if i == len(attr_parts) - 1:
                    # This is the final attribute, set it
                    setattr(current_obj, attr_name, variation)
                else:
                    # Navigate to next object in chain
                    current_obj = getattr(current_obj, attr_name)
            
            # Calculate TCO
            test_result = self.calculate(test_scenario)
            
            # Store results
            tco_values.append(test_result.total_tco)
            lcod_values.append(test_result.lcod)
        
        # Create sensitivity result
        return {
            "parameter": parameter,
            "variation_values": variation_range,
            "tco_values": tco_values,
            "lcod_values": lcod_values,
            "original_value": original_value,
            "original_tco": original_result.total_tco,
            "original_lcod": original_result.lcod,
            "unit": unit
        }
    
    def analyze_multiple_parameters(self, scenario: ScenarioInput, 
                                  parameters: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Analyze sensitivity to multiple parameters.
        
        Args:
            scenario: Input scenario
            parameters: List of parameters to analyze
            
        Returns:
            Dictionary of sensitivity results for each parameter
        """
        results = {}
        
        # Define variation ranges using reasonable ranges
        variation_ranges = {
            "economic.diesel_price_aud_per_l": [p * 2.0 for p in [0.5, 0.75, 0.9, 1.0, 1.1, 1.25, 1.5]],
            "economic.electricity_price_aud_per_kwh": [p * 0.25 for p in [0.5, 0.75, 0.9, 1.0, 1.1, 1.25, 1.5]],
            "operational.annual_distance_km": [p * scenario.operational.annual_distance_km for p in [0.5, 0.75, 0.9, 1.0, 1.1, 1.25, 1.5]],
            "economic.analysis_period_years": [max(1, scenario.economic.analysis_period_years + y) for y in [-5, -3, -1, 0, 1, 3, 5]],
            "economic.discount_rate_real": [max(0.01, scenario.economic.discount_rate_real + p/100) for p in [-3, -2, -1, 0, 1, 2, 3]],
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
        
        return results
    
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