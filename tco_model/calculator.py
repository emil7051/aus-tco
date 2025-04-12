"""
TCO Calculator Module

This module implements the core TCO calculation engine that orchestrates the calculation
of all cost components and produces the final TCO results.
"""

from typing import Dict, List, Optional, Union
import pandas as pd
import numpy as np
import numpy_financial as npf

from tco_model.models import (
    ScenarioInput,
    TCOOutput,
    AnnualCosts,
    NPVCosts,
    ComparisonResult,
    VehicleType,
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
            TCOOutput: The calculated TCO results.
        """
        # Extract key parameters
        years = range(scenario.operational.analysis_period)
        discount_rate = scenario.economic.discount_rate
        
        # Initialize dataframe to store annual costs
        annual_costs_df = pd.DataFrame(index=years)
        
        # Get appropriate strategies based on vehicle type
        energy_strategy = get_energy_consumption_strategy(scenario.vehicle.type)
        maintenance_strategy = get_maintenance_strategy(scenario.vehicle.type)
        
        # Calculate individual cost components for each year
        for year in years:
            # Calculate acquisition costs
            annual_costs_df.loc[year, 'acquisition'] = calculate_acquisition_costs(
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
            annual_costs_df.loc[year, 'infrastructure'] = calculate_infrastructure_costs(
                scenario, year
            )
            
            # Calculate battery replacement costs (only for BETs)
            annual_costs_df.loc[year, 'battery_replacement'] = calculate_battery_replacement_costs(
                scenario, year
            ) if scenario.vehicle.type == VehicleType.BATTERY_ELECTRIC else 0
            
            # Calculate insurance and registration costs
            annual_costs_df.loc[year, 'insurance_registration'] = calculate_insurance_registration_costs(
                scenario, year
            )
            
            # Calculate taxes and levies
            annual_costs_df.loc[year, 'taxes_levies'] = calculate_taxes_levies(
                scenario, year
            )
            
            # Calculate residual value (only applied in the final year)
            annual_costs_df.loc[year, 'residual_value'] = calculate_residual_value(
                scenario, year
            ) if year == scenario.operational.analysis_period - 1 else 0
        
        # Calculate annual totals
        annual_costs_df['total'] = annual_costs_df.sum(axis=1)
        
        # Calculate NPV for each cost component
        npv_costs = {}
        for column in annual_costs_df.columns:
            npv_costs[column] = npf.npv(discount_rate, annual_costs_df[column])
        
        # Calculate the TCO per kilometer
        total_km = scenario.operational.annual_distance * scenario.operational.analysis_period
        lcod = npv_costs['total'] / total_km if total_km > 0 else 0
        
        # Create and return the TCO output
        return TCOOutput(
            annual_costs=AnnualCosts(**annual_costs_df.to_dict()),
            npv_costs=NPVCosts(**npv_costs),
            total_tco=npv_costs['total'],
            lcod=lcod,
            scenario=scenario,
        )
    
    def compare_results(self, result1: TCOOutput, result2: TCOOutput) -> ComparisonResult:
        """
        Compare two TCO results and generate a comparison result.
        
        Args:
            result1: First TCO result
            result2: Second TCO result
            
        Returns:
            ComparisonResult: The comparison between the two TCO results
        """
        # Calculate differences
        tco_difference = result2.total_tco - result1.total_tco
        tco_percentage = (tco_difference / result1.total_tco) * 100 if result1.total_tco != 0 else 0
        lcod_difference = result2.lcod - result1.lcod
        
        # Calculate component differences
        component_differences = {}
        for component in result1.npv_costs.__dict__.keys():
            component_differences[component] = (
                getattr(result2.npv_costs, component) - getattr(result1.npv_costs, component)
            )
        
        # Return comparison result
        return ComparisonResult(
            tco_difference=tco_difference,
            tco_percentage=tco_percentage,
            lcod_difference=lcod_difference,
            component_differences=component_differences,
            cheaper_option=1 if tco_difference > 0 else 2,
        ) 