# Docstring Templates for Australian Heavy Vehicle TCO Modeller

This document provides standardized docstring templates for the Australian Heavy Vehicle TCO Modeller project. 
All new and updated code should follow these formats.

## Module Docstring

```python
"""
Module Name

Brief description of the module's purpose and functionality.
More detailed explanation if necessary spanning multiple lines.

This module implements/provides/contains...
"""
```

## Class Docstring

```python
class MyClass:
    """
    Brief description of the class.
    
    Detailed description of the class, its purpose, and behavior.
    May span multiple lines and provide more context about how to use it.
    
    Attributes:
        attr_name (type): Description of the attribute.
        another_attr (type): Description of another attribute.
    """
```

## Method/Function Docstring

```python
def function_name(param1: Type1, param2: Type2, param3: Optional[Type3] = None) -> ReturnType:
    """
    Brief description of the function's purpose.
    
    More detailed explanation of what the function does, how it works,
    and any notable behavior or edge cases worth mentioning.
    
    Args:
        param1: Description of first parameter.
        param2: Description of second parameter.
        param3: Description of optional parameter, defaults to None.
            Second line of description if needed.
    
    Returns:
        Description of return value and its type.
    
    Raises:
        ExceptionType: When and why this exception might be raised.
        
    Example:
        >>> result = function_name("value", 42)
        >>> print(result)
        Expected output
    """
```

## Property Docstring

```python
@property
def property_name(self) -> ReturnType:
    """
    Brief description of the property.
    
    Additional details about the property, when it's used,
    what it calculates, etc.
    
    Returns:
        Description of the return value.
    """
```

## Private Method Docstring

```python
def _private_method(self, param1: Type1) -> ReturnType:
    """
    Brief description of the private method.
    
    Note that private methods are still fully documented,
    especially when they contain complex logic.
    
    Args:
        param1: Description of the parameter.
    
    Returns:
        Description of the return value.
    """
```

## Constants and Enums

```python
# For module-level constants
CONSTANT_NAME: Type = value  # Description of the constant

# For Enums
class MyEnum(str, Enum):
    """Description of what this enum represents."""
    
    VALUE_ONE = "value_one"  # Description of this enum value
    VALUE_TWO = "value_two"  # Description of this enum value
```

## Example Full Class with Docstrings

```python
"""
Vehicle Module

This module contains classes to represent different types of vehicles
and their specific parameters, behaviors, and calculations.
"""

from typing import Optional, Dict, List
from enum import Enum


class VehicleType(str, Enum):
    """Type of vehicle powertrain."""
    
    DIESEL = "diesel"  # Traditional internal combustion engine
    BATTERY_ELECTRIC = "battery_electric"  # Battery electric vehicle


class Vehicle:
    """
    Base class for all vehicle types.
    
    Provides common attributes and methods for vehicles,
    with specific implementations provided by subclasses
    for different powertrain types.
    
    Attributes:
        name (str): The name/model of the vehicle.
        type (VehicleType): The powertrain type of the vehicle.
        purchase_price (float): The purchase price in AUD.
        range_km (float): The operational range in kilometers.
    """
    
    def __init__(
        self, 
        name: str, 
        vehicle_type: VehicleType,
        purchase_price: float,
        range_km: float
    ) -> None:
        """
        Initialize a new Vehicle instance.
        
        Args:
            name: The name/model of the vehicle.
            vehicle_type: The powertrain type of the vehicle.
            purchase_price: The purchase price in AUD.
            range_km: The operational range in kilometers.
        """
        self.name = name
        self.type = vehicle_type
        self.purchase_price = purchase_price
        self.range_km = range_km
        self._maintenance_history: List[Dict[str, Any]] = []
    
    @property
    def price_per_km_range(self) -> float:
        """
        Calculate the purchase price per kilometer of range.
        
        This metric helps compare the initial cost efficiency of vehicles
        in terms of how much range you get for your investment.
        
        Returns:
            float: The purchase price divided by range in km.
        
        Example:
            >>> vehicle = Vehicle("Model X", VehicleType.BATTERY_ELECTRIC, 200000, 500)
            >>> vehicle.price_per_km_range
            400.0
        """
        if self.range_km <= 0:
            return float('inf')
        return self.purchase_price / self.range_km
    
    def calculate_annual_costs(self, annual_distance_km: float) -> Dict[str, float]:
        """
        Calculate the annual costs for this vehicle.
        
        This is an abstract method that should be implemented by subclasses.
        
        Args:
            annual_distance_km: The annual distance traveled in kilometers.
        
        Returns:
            Dict[str, float]: Dictionary of annual costs by category.
        
        Raises:
            NotImplementedError: If called on the base class.
        """
        raise NotImplementedError("Subclasses must implement calculate_annual_costs")
    
    def _update_maintenance_history(self, service_type: str, cost: float, date: str) -> None:
        """
        Update the vehicle's maintenance history with a new service record.
        
        Args:
            service_type: The type of service performed.
            cost: The cost of the service in AUD.
            date: The date of service in ISO format (YYYY-MM-DD).
        """
        self._maintenance_history.append({
            "type": service_type,
            "cost": cost,
            "date": date
        })
```

## Type Hints

Always use type hints according to Python's typing module. Some common patterns:

```python
# Basic types
variable: int = 42
name: str = "value"
amount: float = 3.14
is_valid: bool = True

# Container types
items: List[int] = [1, 2, 3]
mappings: Dict[str, float] = {"key": 1.0}
pairs: Tuple[int, str] = (1, "value")
values: Set[int] = {1, 2, 3}

# Optional values (can be None)
maybe_value: Optional[str] = None

# Union types (can be one of several types)
id_or_name: Union[int, str] = "user123"

# Type variables and generics
T = TypeVar('T')
def first_item(items: List[T]) -> Optional[T]:
    return items[0] if items else None
```

## Inline Comments

Use inline comments sparingly and only for complex logic:

```python
# Good: Explains the "why" behind complex logic
adjusted_value = base_value * (1 + adjustment_factor)  # Apply adjustment factor to account for temperature effects

# Bad: States the obvious
count = count + 1  # Increment count
``` 