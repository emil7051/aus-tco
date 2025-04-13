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
        if scenario.vehicle.type == VehicleType.BATTERY_ELECTRIC:
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
                if battery_replacement_strategy and scenario.vehicle.type == VehicleType.BATTERY_ELECTRIC
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
        annual_costs_collection = AnnualCostsCollection(annual_costs_list)
        
        # Create and return the TCO output
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
        
        return result
    
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
        
        # Calculate TCO difference and percentage
        tco_difference, tco_percentage = calculate_cost_difference(
            result1.total_tco, result2.total_tco
        )
        
        # Calculate LCOD difference and percentage
        lcod_difference, lcod_difference_percentage = calculate_cost_difference(
            result1.lcod, result2.lcod
        )
        
        # Calculate payback year (if applicable)
        payback_year = self._calculate_payback_year(result1, result2)
        
        return ComparisonResult(
            scenario_1=result1,
            scenario_2=result2,
            tco_difference=tco_difference,
            tco_percentage=tco_percentage,
            lcod_difference=lcod_difference,
            lcod_difference_percentage=lcod_difference_percentage,
            payback_year=payback_year
        )
    
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