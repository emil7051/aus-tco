"""
Standardized terminology for the TCO Model.

This module provides constants, mappings, and documentation for standardized terminology
used throughout the TCO model. It serves as a central reference for terms,
abbreviations, field names, and default values to ensure consistency.
"""

from typing import Dict, List, Tuple, Any, Optional, Union, Protocol, TypeVar, Callable
from enum import Enum

# Type variables for generic functions
T = TypeVar('T')

# Canonical Vehicle Type Enum
# 
# The canonical representation of vehicle types is through the VehicleType enum
# from tco_model.schemas. Always import VehicleType from schemas, not models:
#
# ```python
# # Correct usage:
# from tco_model.schemas import VehicleType
# 
# # Enum values:
# VehicleType.BATTERY_ELECTRIC  # Electric vehicle
# VehicleType.DIESEL            # Diesel vehicle
# 
# # String comparisons:
# if vehicle.type == VehicleType.BATTERY_ELECTRIC.value:
#     # Handle electric vehicle logic
# ```
#
# Do not use string literals like "bet", "ice", "battery_electric" or "diesel".
# The BET and ICE abbreviations are being phased out in favor of the full terms.

# Core Terminology

#: Total Cost of Ownership - The comprehensive sum of all costs associated
#: with acquiring and operating a vehicle over its lifetime, expressed in
#: present value terms
TCO = "Total Cost of Ownership"

#: Levelized Cost of Driving - The per-kilometer cost of ownership, calculated
#: by dividing the TCO by the total lifetime distance traveled
LCOD = "Levelized Cost of Driving"

#: Net Present Value - The current value of future cash flows, accounting for
#: the time value of money using a discount rate
NPV = "Net Present Value"

#: Battery Electric Truck - A heavy vehicle powered by electric batteries
BET = "Battery Electric Truck"

#: Internal Combustion Engine - A traditional engine powered by fossil fuels
ICE = "Internal Combustion Engine"

# Base year for all calculations
BASE_CALENDAR_YEAR = 2025

# Vehicle Type Mapping
VEHICLE_TYPE_LABELS: Dict[str, str] = {
    "battery_electric": "Battery Electric Truck (BET)",
    "diesel": "Diesel (ICE)",
}

# Vehicle Category Mapping
VEHICLE_CATEGORY_LABELS: Dict[str, str] = {
    "rigid": "Rigid Truck",
    "articulated": "Articulated Truck",
}

# Cost Component Terminology

#: Cost component definitions with descriptive text
COST_COMPONENTS: Dict[str, str] = {
    "acquisition": "Costs related to purchasing the vehicle (initial capital outlay or loan payments)",
    "energy": "Costs of fuel or electricity used to power the vehicle",
    "maintenance": "Regular and corrective maintenance expenses to keep the vehicle operational",
    "infrastructure": "Costs of supporting infrastructure (e.g., charging equipment for BETs)",
    "battery_replacement": "Costs associated with replacing batteries during the vehicle's lifetime",
    "insurance": "Costs of vehicle insurance",
    "registration": "Government registration and licensing fees",
    "carbon_tax": "Taxes or levies applied to carbon emissions",
    "other_taxes": "Additional taxes and government charges",
    "residual_value": "The remaining value of the vehicle at the end of the analysis period"
}

# UI-specific combined components
UI_COMPONENT_KEYS: List[str] = [
    "acquisition",
    "energy", 
    "maintenance",
    "infrastructure",
    "battery_replacement",
    "insurance_registration",  # Combined from insurance + registration
    "taxes_levies",            # Combined from carbon_tax + other_taxes
    "residual_value"
]

UI_COMPONENT_LABELS: Dict[str, str] = {
    "acquisition": "Acquisition Costs",
    "energy": "Energy Costs",
    "maintenance": "Maintenance, Tyres & Repair",
    "infrastructure": "Infrastructure",
    "battery_replacement": "Battery Replacement",
    "insurance_registration": "Insurance & Registration",
    "taxes_levies": "Taxes & Levies for Organisations",
    "residual_value": "Residual Value"
}

# UI Component to model components mapping
UI_TO_MODEL_COMPONENT_MAPPING: Dict[str, List[str]] = {
    "insurance_registration": ["insurance", "registration"],
    "taxes_levies": ["carbon_tax", "other_taxes"],
}

# Complete UI Component mapping - adds display order, description, etc.
UI_COMPONENT_MAPPING: Dict[str, Dict[str, Any]] = {
    "acquisition": {
        "npv_field": "acquisition",
        "annual_field": "acquisition",
        "description": "Costs related to vehicle purchase (loan payments or cash)",
        "display_order": 1,
        "applies_to_all_vehicles": True,
        "display_label": "Acquisition Costs",
        "color": "#1f77b4"  # Blue
    },
    "energy": {
        "npv_field": "energy",
        "annual_field": "energy",
        "description": "Energy costs (electricity or diesel fuel)",
        "display_order": 2,
        "applies_to_all_vehicles": True,
        "display_label": "Energy Costs",
        "color": "#ff7f0e"  # Orange
    },
    "maintenance": {
        "npv_field": "maintenance",
        "annual_field": "maintenance",
        "description": "Maintenance and repair costs",
        "display_order": 3,
        "applies_to_all_vehicles": True,
        "display_label": "Maintenance & Repair",
        "color": "#2ca02c"  # Green
    },
    "infrastructure": {
        "npv_field": "infrastructure",
        "annual_field": "infrastructure",
        "description": "Charging infrastructure costs (mainly for BETs)",
        "display_order": 4,
        "applies_to_all_vehicles": True,
        "display_label": "Infrastructure",
        "color": "#d62728"  # Red
    },
    "battery_replacement": {
        "npv_field": "battery_replacement",
        "annual_field": "battery_replacement",
        "description": "Battery replacement costs",
        "display_order": 5,
        "applies_to_bet_only": True,
        "display_label": "Battery Replacement",
        "color": "#9467bd"  # Purple
    },
    "insurance_registration": {
        "composite": True,
        "components": ["insurance", "registration"],
        "description": "Combined insurance and registration costs",
        "display_order": 6,
        "applies_to_all_vehicles": True,
        "display_label": "Insurance & Registration",
        "color": "#8c564b"  # Brown
    },
    "taxes_levies": {
        "composite": True,
        "components": ["carbon_tax", "other_taxes"],
        "description": "Combined taxes and carbon levies",
        "display_order": 7,
        "applies_to_all_vehicles": True,
        "display_label": "Taxes & Levies",
        "color": "#e377c2"  # Pink
    },
    "residual_value": {
        "npv_field": "residual_value",
        "annual_field": "residual_value",
        "description": "Residual value of the vehicle (negative cost)",
        "display_order": 8,
        "applies_to_all_vehicles": True,
        "display_label": "Residual Value",
        "color": "#7f7f7f"  # Gray
    }
}

# Standard Field Names

#: Standard field names for the TCO model
CANONICAL_FIELD_NAMES = {
    "total_tco": "Total cost of ownership (NPV)",
    "lcod": "Levelized cost of driving per km",
    "tco_difference": "Difference in TCO between scenarios",
    "tco_percentage": "Percentage difference in TCO"
}

# Comprehensive Config to Model Field Mapping by Vehicle Type
CONFIG_FIELD_MAPPINGS: Dict[str, Dict[str, str]] = {
    # BET configuration mappings
    "battery_electric": {
        "vehicle_info.type": "type",
        "vehicle_info.category": "category",
        "vehicle_info.name": "name",
        "purchase.base_price_2025": "purchase_price",
        "purchase.annual_price_decrease_real": "annual_price_decrease_real",
        "performance.max_payload_tonnes": "max_payload_tonnes",
        "performance.range_km": "range_km",
        
        # Battery parameters
        "battery.capacity_kwh": "battery.capacity_kwh",
        "battery.usable_capacity_percentage": "battery.usable_capacity_percentage",
        "battery.degradation_rate_annual": "battery.degradation_rate_annual",
        "battery.replacement_threshold": "battery.replacement_threshold",
        "battery.expected_lifecycle_years": "battery.expected_lifecycle_years",
        "battery.replacement_cost_factor": "battery.replacement_cost_factor",
        
        # Energy consumption parameters
        "energy_consumption.base_rate_kwh_per_km": "energy_consumption.base_rate",
        "energy_consumption.base_rate": "energy_consumption.base_rate",  # Legacy support
        "energy_consumption.min_rate": "energy_consumption.min_rate",
        "energy_consumption.max_rate": "energy_consumption.max_rate",
        "energy_consumption.load_adjustment_factor": "energy_consumption.load_adjustment_factor",
        "energy_consumption.temperature_adjustment.hot_weather": "energy_consumption.hot_weather_adjustment",
        "energy_consumption.temperature_adjustment.cold_weather": "energy_consumption.cold_weather_adjustment",
        "energy_consumption.regenerative_braking_efficiency": "energy_consumption.regenerative_braking_efficiency",
        "energy_consumption.regen_contribution_urban": "energy_consumption.regen_contribution_urban",
        
        # Charging parameters
        "charging.max_charging_power_kw": "charging.max_charging_power_kw",
        "charging.charging_efficiency": "charging.charging_efficiency",
        "charging.charging_strategy": "charging.strategy",
        "charging.strategies.overnight_depot.electricity_rate_type": "charging.electricity_rate_type",
        
        # Maintenance parameters
        "maintenance.cost_per_km": "maintenance.cost_per_km",
        "maintenance.detailed_costs.annual_fixed_min": "maintenance.annual_fixed_min",
        "maintenance.detailed_costs.annual_fixed_max": "maintenance.annual_fixed_max",
        "maintenance.scheduled_maintenance_interval_km": "maintenance.scheduled_maintenance_interval_km",
        "maintenance.major_service_interval_km": "maintenance.major_service_interval_km",
        
        # Residual value parameters
        "residual_values.year_5": "residual_value.year_5_range",
        "residual_values.year_10": "residual_value.year_10_range",
        "residual_values.year_15": "residual_value.year_15_range",
        
        # Infrastructure parameters
        "infrastructure.charger_hardware_cost": "infrastructure.charger_hardware_cost",
        "infrastructure.installation_cost": "infrastructure.installation_cost",
        "infrastructure.maintenance_annual_percentage": "infrastructure.maintenance_annual_percentage",
        "infrastructure.trucks_per_charger": "infrastructure.trucks_per_charger",
        "infrastructure.grid_upgrade_cost": "infrastructure.grid_upgrade_cost"
    },
    
    # Diesel configuration mappings
    "diesel": {
        "vehicle_info.type": "type",
        "vehicle_info.category": "category",
        "vehicle_info.name": "name",
        "purchase.base_price_2025": "purchase_price",
        "purchase.annual_price_decrease_real": "annual_price_decrease_real",
        "performance.max_payload_tonnes": "max_payload_tonnes",
        "performance.range_km": "range_km",
        
        # Engine parameters
        "engine.power_kw": "engine.power_kw",
        "engine.power": "engine.power_kw",  # Legacy support
        "engine.displacement_litres": "engine.displacement_litres",
        "engine.euro_emission_standard": "engine.euro_emission_standard",
        "engine.adblue_required": "engine.adblue_required",
        "engine.adblue_consumption_percent_of_diesel": "engine.adblue_consumption_percent_of_diesel",
        "engine.co2_per_liter": "engine.co2_per_liter",
        
        # Fuel consumption parameters
        "fuel_consumption.base_rate_l_per_km": "fuel_consumption.base_rate",
        "fuel_consumption.base_rate": "fuel_consumption.base_rate",  # Legacy support
        "fuel_consumption.min_rate": "fuel_consumption.min_rate",
        "fuel_consumption.max_rate": "fuel_consumption.max_rate",
        "fuel_consumption.load_adjustment_factor": "fuel_consumption.load_adjustment_factor",
        "fuel_consumption.temperature_adjustment.hot_weather": "fuel_consumption.hot_weather_adjustment",
        "fuel_consumption.temperature_adjustment.cold_weather": "fuel_consumption.cold_weather_adjustment",
        
        # Maintenance parameters
        "maintenance.cost_per_km": "maintenance.cost_per_km",
        "maintenance.detailed_costs.annual_fixed_min": "maintenance.annual_fixed_min",
        "maintenance.detailed_costs.annual_fixed_max": "maintenance.annual_fixed_max",
        "maintenance.scheduled_maintenance_interval_km": "maintenance.scheduled_maintenance_interval_km",
        "maintenance.major_service_interval_km": "maintenance.major_service_interval_km",
        
        # Residual value parameters
        "residual_values.year_5": "residual_value.year_5_range",
        "residual_values.year_10": "residual_value.year_10_range",
        "residual_values.year_15": "residual_value.year_15_range"
    }
}

# Economic parameter mappings
ECONOMIC_CONFIG_MAPPING: Dict[str, str] = {
    "general.discount_rate_real": "discount_rate_real",
    "general.inflation_rate": "inflation_rate",
    "general.analysis_period_years": "analysis_period_years",
    "financing.default_method": "financing.method",
    "financing.loan.term_years": "financing.loan_term_years",
    "financing.loan.interest_rate": "financing.loan_interest_rate",
    "financing.loan.down_payment_percentage": "financing.down_payment_percentage",
    "carbon_pricing.carbon_tax_rate_2025": "carbon_tax_rate_aud_per_tonne",
    "carbon_pricing.annual_increase_rate": "carbon_tax_annual_increase_rate",
    "energy_prices.electricity.rate_type": "electricity_price_type",
    "energy_prices.diesel.scenario": "diesel_price_scenario"
}

# Operational parameter mappings
OPERATIONAL_CONFIG_MAPPING: Dict[str, str] = {
    "annual_distance_km": "annual_distance_km",
    "operating_days_per_year": "operating_days_per_year",
    "vehicle_life_years": "vehicle_life_years",
    "daily_distance_km": "daily_distance_km",
    "charging_strategy": "requires_overnight_charging",  # Mapped based on value
    "vehicle_type": "is_urban_operation",  # Mapped based on value 
    "load_factor": "average_load_factor"
}

# Simplified Config to Model Field Mapping
CONFIG_TO_MODEL_MAPPING: Dict[str, str] = {
    # Combine mappings from battery_electric and diesel
    **{k: v for k, v in CONFIG_FIELD_MAPPINGS["battery_electric"].items() 
       if k in CONFIG_FIELD_MAPPINGS["diesel"] and 
       CONFIG_FIELD_MAPPINGS["battery_electric"][k] == CONFIG_FIELD_MAPPINGS["diesel"][k]},
    
    # Add general economic and operational mappings
    **{f"economic.{k}": f"economic.{v}" for k, v in ECONOMIC_CONFIG_MAPPING.items()},
    **{f"operational.{k}": f"operational.{v}" for k, v in OPERATIONAL_CONFIG_MAPPING.items()}
}

# Cost Calculation Function Mapping
COST_FUNCTION_TO_STRATEGY_MAPPING: Dict[str, str] = {
    "calculate_acquisition_costs": "FinancingStrategy",
    "calculate_energy_costs": "EnergyConsumptionStrategy",
    "calculate_maintenance_costs": "MaintenanceStrategy",
    "calculate_infrastructure_costs": "InfrastructureStrategy",
    "calculate_battery_replacement_costs": "BatteryReplacementStrategy",
    "calculate_insurance_registration_costs": "InsuranceStrategy/RegistrationStrategy",
    "calculate_taxes_levies": "CarbonTaxStrategy/TaxesStrategy",
    "calculate_residual_value": "ResidualValueStrategy"
}

# Strategy class naming conventions
STRATEGY_CLASS_NAMING_CONVENTIONS = {
    # Base strategy names by domain
    "base_strategies": {
        "energy": "EnergyConsumptionStrategy",
        "maintenance": "MaintenanceStrategy",
        "residual_value": "ResidualValueStrategy",
        "battery_replacement": "BatteryReplacementStrategy",
        "infrastructure": "InfrastructureStrategy",
        "financing": "FinancingStrategy",
        "insurance": "InsuranceStrategy",
        "registration": "RegistrationStrategy",
        "carbon_tax": "CarbonTaxStrategy"
    },
    
    # Vehicle-specific prefixes
    "vehicle_prefixes": {
        "battery_electric": "BET",
        "diesel": "Diesel"
    },
    
    # Implementation-specific patterns
    "implementation_patterns": {
        "distance_based": "DistanceBased",
        "value_based": "ValueBased",
        "degradation_based": "DegradationBased",
        "loan": "Loan",
        "cash": "Cash",
        "fuel_based": "FuelBased"
    },
    
    # Method name conventions
    "method_names": {
        "cost_calculation": "calculate_costs",
        "consumption_calculation": "calculate_consumption",
        "residual_value_calculation": "calculate_residual_value",
        "helper": "get_calendar_year"
    },
    
    # Strategy classes that need to be renamed
    "rename_mapping": {
        "BETPowerConsumptionStrategy": "BETEnergyConsumptionStrategy",
    }
}

# Default values for vehicle parameters

#: Default energy consumption rate for BETs in kWh/km
DEFAULT_BET_CONSUMPTION_RATE = 1.5

#: Default fuel consumption rate for diesel vehicles in L/km
DEFAULT_DIESEL_CONSUMPTION_RATE = 0.35

#: Default battery capacity for BETs in kWh
DEFAULT_BATTERY_CAPACITY_KWH = 400  

#: Default charging power for BETs in kW
DEFAULT_CHARGING_POWER_KW = 350

#: Default engine power for diesel vehicles in kW
DEFAULT_ENGINE_POWER_KW = 400

#: Default residual value percentage at 5 years for BETs
DEFAULT_BET_RESIDUAL_5YR = (0.5, 0.6)  # (min, max)

#: Default residual value percentage at 5 years for diesel vehicles
DEFAULT_DIESEL_RESIDUAL_5YR = (0.4, 0.5)  # (min, max)

#: Default vehicle price for BETs in AUD
DEFAULT_BET_PRICE = 400000

#: Default vehicle price for diesel vehicles in AUD
DEFAULT_DIESEL_PRICE = 200000

#: Default maintenance cost per km for BETs in AUD
DEFAULT_BET_MAINTENANCE_COST_PER_KM = 0.08

#: Default maintenance cost per km for diesel vehicles in AUD
DEFAULT_DIESEL_MAINTENANCE_COST_PER_KM = 0.12

# Comprehensive default values grouped by vehicle and parameter type

# Default values for BET parameters
BET_DEFAULTS = {
    "purchase_price": 400000,
    "annual_price_decrease_real": 0.02, 
    "max_payload_tonnes": 26,
    "range_km": 350,
    
    # Battery defaults
    "battery": {
        "capacity_kwh": 400,
        "usable_capacity_percentage": 0.9,
        "degradation_rate_annual": 0.02,
        "replacement_threshold": 0.7,
        "expected_lifecycle_years": 8,
        "replacement_cost_factor": 0.8
    },
    
    # Energy consumption defaults
    "energy_consumption": {
        "base_rate": 1.5,  # kWh/km
        "min_rate": 1.4,
        "max_rate": 1.6,
        "load_adjustment_factor": 0.15,
        "hot_weather_adjustment": 0.05,
        "cold_weather_adjustment": 0.15,
        "regenerative_braking_efficiency": 0.65,
        "regen_contribution_urban": 0.2
    },
    
    # Charging defaults
    "charging": {
        "max_charging_power_kw": 350,
        "charging_efficiency": 0.9,
        "strategy": "overnight_depot",
        "electricity_rate_type": "average_flat_rate"
    },
    
    # Maintenance defaults
    "maintenance": {
        "cost_per_km": 0.08,
        "annual_fixed_min": 700,
        "annual_fixed_max": 1500,
        "annual_fixed_default": 1100,
        "scheduled_maintenance_interval_km": 40000,
        "major_service_interval_km": 120000
    },
    
    # Residual value defaults
    "residual_value": {
        "year_5_range": [0.5, 0.6],
        "year_10_range": [0.3, 0.4],
        "year_15_range": [0.1, 0.15]
    },
    
    # Infrastructure defaults
    "infrastructure": {
        "charger_hardware_cost": 150000,
        "installation_cost": 50000,
        "maintenance_annual_percentage": 0.015,
        "trucks_per_charger": 1.0,
        "grid_upgrade_cost": 0
    }
}

# Default values for diesel parameters
DIESEL_DEFAULTS = {
    "purchase_price": 200000,
    "annual_price_decrease_real": 0.0,
    "max_payload_tonnes": 28,
    "range_km": 2200,
    
    # Engine defaults
    "engine": {
        "power_kw": 400,
        "displacement_litres": 13,
        "euro_emission_standard": "Euro 6",
        "adblue_required": True,
        "adblue_consumption_percent_of_diesel": 0.05,
        "co2_per_liter": 2.68
    },
    
    # Fuel consumption defaults
    "fuel_consumption": {
        "base_rate": 0.35,  # L/km
        "min_rate": 0.3,
        "max_rate": 0.4,
        "load_adjustment_factor": 0.25,
        "hot_weather_adjustment": 0.03,
        "cold_weather_adjustment": 0.05
    },
    
    # Maintenance defaults
    "maintenance": {
        "cost_per_km": 0.12,
        "annual_fixed_min": 2500,
        "annual_fixed_max": 5000,
        "annual_fixed_default": 3750,
        "scheduled_maintenance_interval_km": 25000,
        "major_service_interval_km": 100000
    },
    
    # Residual value defaults
    "residual_value": {
        "year_5_range": [0.4, 0.5],
        "year_10_range": [0.25, 0.35],
        "year_15_range": [0.1, 0.2]
    }
}

# Default economic parameters
ECONOMIC_DEFAULTS = {
    "discount_rate_real": 0.07,
    "inflation_rate": 0.025,
    "analysis_period_years": 15,
    "electricity_price_type": "average_flat_rate",
    "diesel_price_scenario": "medium_increase",
    "carbon_tax_rate_aud_per_tonne": 30.0,
    "carbon_tax_annual_increase_rate": 0.05
}

# Default operational parameters
OPERATIONAL_DEFAULTS = {
    "annual_distance_km": 100000,
    "operating_days_per_year": 280,
    "vehicle_life_years": 15,
    "requires_overnight_charging": True,
    "is_urban_operation": False,
    "average_load_factor": 0.8
}

# Default financing parameters
FINANCING_DEFAULTS = {
    "method": "loan",
    "loan_term_years": 5,
    "loan_interest_rate": 0.07,
    "down_payment_percentage": 0.2
}

# Standard Calculation Descriptions

TCO_CALCULATION = """
The TCO is calculated as the sum of all discounted costs over the analysis period:

total_tco = npv(acquisition_costs + energy_costs + maintenance_costs + 
                infrastructure_costs + battery_replacement_costs + 
                insurance_costs + registration_costs + 
                carbon_tax + other_taxes - residual_value)
"""

LCOD_CALCULATION = """
The LCOD is calculated by dividing the total TCO by the total distance traveled:

lcod = total_tco / total_distance_km

Where:
- total_tco is the TCO in present value terms
- total_distance_km is the total distance traveled over the analysis period
"""

# Standard access functions for component values
def get_component_description(component_name: str) -> str:
    """
    Get the description for a cost component.
    
    Args:
        component_name: The name of the cost component
        
    Returns:
        str: The description of the component, or a default message if not found
    """
    return COST_COMPONENTS.get(
        component_name, 
        f"No description available for {component_name}"
    )

def get_canonical_field_name(field_name: str) -> str:
    """
    Get the canonical field name.
    
    Args:
        field_name: The field name to check
        
    Returns:
        str: The same field name, since all fields are now using canonical names
    """
    return field_name

def get_ui_component_label(component_key: str) -> str:
    """
    Get the UI display label for a component key.
    
    Args:
        component_key: The component key from UI_COMPONENT_KEYS
        
    Returns:
        str: The display label for the component, or the original key if not found
    """
    return UI_COMPONENT_LABELS.get(component_key, component_key.replace('_', ' ').title())

def get_model_components_for_ui_component(ui_component: str) -> List[str]:
    """
    Get the list of model component names that map to a UI component.
    
    Args:
        ui_component: The UI component key
        
    Returns:
        List[str]: List of model component names that correspond to the UI component
    """
    if ui_component in UI_TO_MODEL_COMPONENT_MAPPING:
        return UI_TO_MODEL_COMPONENT_MAPPING[ui_component]
    return [ui_component]

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

def calculate_cost_difference(cost1: float, cost2: float) -> Tuple[float, float]:
    """
    Calculate absolute and percentage difference between two costs.
    
    Args:
        cost1: First cost value
        cost2: Second cost value
        
    Returns:
        Tuple[float, float]: Absolute difference (cost2 - cost1) and percentage difference
    """
    diff = cost2 - cost1
    if cost1 != 0:
        percentage = (diff / cost1) * 100
    else:
        percentage = float('inf') if diff > 0 else float('-inf') if diff < 0 else 0.0
    
    return diff, percentage

def get_config_field_path(model_field_path: str, vehicle_type: str = "battery_electric") -> Optional[str]:
    """
    Get the configuration file field path for a model field path.
    
    Args:
        model_field_path: The field path in the model (e.g., 'battery.capacity_kwh')
        vehicle_type: The vehicle type (battery_electric or diesel)
        
    Returns:
        Optional[str]: The configuration file field path, or None if not found
    """
    # Create reverse mapping for the specific vehicle type
    if vehicle_type not in CONFIG_FIELD_MAPPINGS:
        return None
        
    reverse_mapping = {v: k for k, v in CONFIG_FIELD_MAPPINGS[vehicle_type].items()}
    return reverse_mapping.get(model_field_path)

def get_model_field_path(config_field_path: str, vehicle_type: str = "battery_electric") -> Optional[str]:
    """
    Get the model field path for a configuration file field path.
    
    Args:
        config_field_path: The field path in the configuration file (e.g., 'battery.capacity_kwh')
        vehicle_type: The vehicle type (battery_electric or diesel)
        
    Returns:
        Optional[str]: The model field path, or None if not found
    """
    if vehicle_type not in CONFIG_FIELD_MAPPINGS:
        return None
        
    return CONFIG_FIELD_MAPPINGS[vehicle_type].get(config_field_path)

def get_default_value(field_path: str, vehicle_type: str = "battery_electric") -> Any:
    """
    Get the default value for a model field.
    
    Args:
        field_path: The field path in the model (e.g., 'battery.capacity_kwh')
        vehicle_type: The vehicle type (battery_electric or diesel)
        
    Returns:
        Any: The default value, or None if not found
    """
    # Determine which defaults dictionary to use
    if vehicle_type == "battery_electric":
        defaults = BET_DEFAULTS
    elif vehicle_type == "diesel":
        defaults = DIESEL_DEFAULTS
    else:
        return None
    
    # Parse the field path
    parts = field_path.split('.')
    current = defaults
    
    # Navigate to the field
    for part in parts:
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None
    
    return current

def get_strategy_class_name(domain: str, vehicle_type: Optional[str] = None, 
                           implementation: Optional[str] = None) -> str:
    """
    Get the standardized strategy class name for a given domain and type.
    
    Args:
        domain: The domain of the strategy (e.g., 'energy', 'maintenance')
        vehicle_type: Optional vehicle type (battery_electric or diesel)
        implementation: Optional implementation approach (e.g., 'distance_based')
        
    Returns:
        str: The standardized strategy class name
    """
    conventions = STRATEGY_CLASS_NAMING_CONVENTIONS
    
    # Get base strategy name
    if domain not in conventions["base_strategies"]:
        base_name = f"{domain.title()}Strategy"
    else:
        base_name = conventions["base_strategies"][domain]
    
    # Add vehicle type prefix if specified
    prefix = ""
    if vehicle_type:
        if vehicle_type in conventions["vehicle_prefixes"]:
            prefix = conventions["vehicle_prefixes"][vehicle_type]
        else:
            prefix = vehicle_type.title()
    
    # Add implementation pattern if specified
    implementation_pattern = ""
    if implementation:
        if implementation in conventions["implementation_patterns"]:
            implementation_pattern = conventions["implementation_patterns"][implementation]
        else:
            implementation_pattern = implementation.title()
    
    # Build the full name
    if implementation_pattern:
        return f"{prefix}{implementation_pattern}{base_name}"
    elif prefix:
        return f"{prefix}{base_name}"
    else:
        return base_name 