"""
Unit tests for the strategy pattern implementation.

These tests verify:
1. Strategy factory registration and retrieval
2. Strategy fallback mechanism
3. Specific energy consumption strategies
"""

import pytest

from tco_model.models import VehicleType
from tco_model.strategies import (
    StrategyFactory,
    get_energy_consumption_strategy,
)


class TestStrategyPattern:
    """Tests for the standardized strategy pattern."""
    
    def test_strategy_factory_registration(self):
        """Test that strategies can be registered and retrieved from the factory."""
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
        # Get strategies for different vehicle types
        bet_strategy = get_energy_consumption_strategy(VehicleType.BATTERY_ELECTRIC)
        diesel_strategy = get_energy_consumption_strategy(VehicleType.DIESEL)
        
        # Verify they are of the correct type
        assert bet_strategy.__class__.__name__ == "BETEnergyConsumptionStrategy"
        assert diesel_strategy.__class__.__name__ == "DieselConsumptionStrategy"
        
        # Verify the strategies have the expected methods
        assert hasattr(bet_strategy, 'calculate_consumption')
        assert hasattr(diesel_strategy, 'calculate_consumption') 