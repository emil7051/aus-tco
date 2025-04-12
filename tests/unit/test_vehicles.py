"""
Unit tests for the vehicles module in the TCO Modeller.

These tests verify the functionality related to vehicle data loading and handling.
"""

import pytest
from unittest.mock import patch, mock_open, MagicMock
from pathlib import Path

from tco_model.vehicles import (
    get_vehicle_parameters,
    get_bet_parameters,
    get_diesel_parameters,
    list_available_vehicle_configurations,
)
from tco_model.models import VehicleType, BETParameters, DieselParameters


class TestVehicleParameterLoading:
    """Tests for vehicle parameter loading functions."""

    @patch('tco_model.vehicles.get_bet_parameters')
    def test_get_vehicle_parameters_bet(self, mock_get_bet):
        """Test that get_vehicle_parameters calls the correct function for BETs."""
        mock_bet_params = MagicMock(spec=BETParameters)
        mock_get_bet.return_value = mock_bet_params
        
        # Call with BET type
        result = get_vehicle_parameters(VehicleType.BATTERY_ELECTRIC, 'test_config')
        
        # Verify the correct function was called
        mock_get_bet.assert_called_once_with('test_config')
        assert result == mock_bet_params

    @patch('tco_model.vehicles.get_diesel_parameters')
    def test_get_vehicle_parameters_diesel(self, mock_get_diesel):
        """Test that get_vehicle_parameters calls the correct function for diesel trucks."""
        mock_diesel_params = MagicMock(spec=DieselParameters)
        mock_get_diesel.return_value = mock_diesel_params
        
        # Call with diesel type
        result = get_vehicle_parameters(VehicleType.DIESEL, 'test_config')
        
        # Verify the correct function was called
        mock_get_diesel.assert_called_once_with('test_config')
        assert result == mock_diesel_params

    def test_get_vehicle_parameters_unsupported(self):
        """Test that get_vehicle_parameters raises for unsupported vehicle types."""
        with pytest.raises(ValueError):
            get_vehicle_parameters('unsupported_type', 'test_config')

    @patch('tco_model.vehicles.load_yaml_file')
    def test_get_bet_parameters(self, mock_load_yaml):
        """Test that get_bet_parameters loads the correct configuration file."""
        # Mock the YAML data
        mock_yaml_data = {
            'type': 'battery_electric',
            'category': 'articulated',
            'name': 'Test BET',
            'purchase_price': 500000.0,
            'battery': {
                'capacity': 400.0,
                'degradation_rate': 0.02,
                'replacement_threshold': 0.8,
                'price_per_kwh': 800.0,
            },
            'consumption': {
                'base_rate': 1.5,
                'adjustment_factors': {
                    'load': 0.2,
                    'terrain': 0.1,
                    'temperature': 0.05,
                },
            },
            'charging': {
                'power': 150.0,
                'efficiency': 0.9,
                'time_per_session': 1.0,
            },
            'maintenance': {
                'base_rate': 0.15,
                'annual_increase': 0.05,
            },
            'residual_value': {
                'initial_percentage': 0.5,
                'annual_depreciation': 0.1,
            },
        }
        
        mock_load_yaml.return_value = mock_yaml_data
        
        # Call the function with a specific config name
        result = get_bet_parameters('test_bet')
        
        # Verify the YAML file was loaded with the correct path
        expected_path = Path('config/vehicles/test_bet.yaml')
        mock_load_yaml.assert_called_once_with(expected_path)
        
        # Verify the result was created with the right data
        assert isinstance(result, BETParameters)
        assert result.type == VehicleType.BATTERY_ELECTRIC
        assert result.name == 'Test BET'
        assert result.purchase_price == 500000.0

    @patch('tco_model.vehicles.load_yaml_file')
    def test_get_bet_parameters_default(self, mock_load_yaml):
        """Test that get_bet_parameters uses the default configuration when none is specified."""
        # Mock the YAML data (simplified)
        mock_yaml_data = {
            'type': 'battery_electric',
            'category': 'articulated',
            'name': 'Default BET',
            'purchase_price': 500000.0,
            'battery': {
                'capacity': 400.0,
                'degradation_rate': 0.02,
                'replacement_threshold': 0.8,
                'price_per_kwh': 800.0,
            },
            'consumption': {
                'base_rate': 1.5,
                'adjustment_factors': {
                    'load': 0.2,
                    'terrain': 0.1,
                    'temperature': 0.05,
                },
            },
            'charging': {
                'power': 150.0,
                'efficiency': 0.9,
                'time_per_session': 1.0,
            },
            'maintenance': {
                'base_rate': 0.15,
                'annual_increase': 0.05,
            },
            'residual_value': {
                'initial_percentage': 0.5,
                'annual_depreciation': 0.1,
            },
        }
        
        mock_load_yaml.return_value = mock_yaml_data
        
        # Call the function without a config name
        result = get_bet_parameters()
        
        # Verify the default YAML file was loaded
        expected_path = Path('config/vehicles/default_bet.yaml')
        mock_load_yaml.assert_called_once_with(expected_path)
        
        # Verify the result has the right name
        assert result.name == 'Default BET'

    @patch('tco_model.vehicles.load_yaml_file')
    def test_get_diesel_parameters(self, mock_load_yaml):
        """Test that get_diesel_parameters loads the correct configuration file."""
        # Mock the YAML data
        mock_yaml_data = {
            'type': 'diesel',
            'category': 'articulated',
            'name': 'Test Diesel',
            'purchase_price': 400000.0,
            'engine': {
                'power': 350,
                'emissions_standard': 'Euro VI',
            },
            'consumption': {
                'base_rate': 35.0,
                'adjustment_factors': {
                    'load': 0.15,
                    'terrain': 0.1,
                    'temperature': 0.03,
                },
            },
            'emissions': {
                'co2_per_liter': 2.7,
            },
            'maintenance': {
                'base_rate': 0.2,
                'annual_increase': 0.05,
            },
            'residual_value': {
                'initial_percentage': 0.4,
                'annual_depreciation': 0.12,
            },
        }
        
        mock_load_yaml.return_value = mock_yaml_data
        
        # Call the function with a specific config name
        result = get_diesel_parameters('test_diesel')
        
        # Verify the YAML file was loaded with the correct path
        expected_path = Path('config/vehicles/test_diesel.yaml')
        mock_load_yaml.assert_called_once_with(expected_path)
        
        # Verify the result was created with the right data
        assert isinstance(result, DieselParameters)
        assert result.type == VehicleType.DIESEL
        assert result.name == 'Test Diesel'
        assert result.purchase_price == 400000.0

    @patch('tco_model.vehicles.Path.glob')
    @patch('tco_model.vehicles.load_yaml_file')
    def test_list_available_vehicle_configurations(self, mock_load_yaml, mock_glob):
        """Test that list_available_vehicle_configurations correctly lists available configs."""
        # Mock the glob results
        mock_path1 = MagicMock()
        mock_path1.stem = 'default_bet'
        mock_path2 = MagicMock()
        mock_path2.stem = 'default_ice'
        mock_path3 = MagicMock()
        mock_path3.stem = 'custom_bet'
        mock_glob.return_value = [mock_path1, mock_path2, mock_path3]
        
        # Mock the YAML loading results
        mock_load_yaml.side_effect = [
            {'type': 'battery_electric'},  # default_bet
            {'type': 'diesel'},            # default_ice
            {'type': 'battery_electric'},  # custom_bet
        ]
        
        # Call the function
        result = list_available_vehicle_configurations()
        
        # Verify the glob was called with the right pattern
        mock_glob.assert_called_once_with('*.yaml')
        
        # Verify YAML files were loaded
        assert mock_load_yaml.call_count == 3
        
        # Verify the result contains the expected configurations
        assert len(result[VehicleType.BATTERY_ELECTRIC]) == 2
        assert 'default_bet' in result[VehicleType.BATTERY_ELECTRIC]
        assert 'custom_bet' in result[VehicleType.BATTERY_ELECTRIC]
        
        assert len(result[VehicleType.DIESEL]) == 1
        assert 'default_ice' in result[VehicleType.DIESEL]

    @patch('tco_model.vehicles.Path.glob')
    @patch('tco_model.vehicles.load_yaml_file')
    def test_list_available_vehicle_configurations_invalid_yaml(self, mock_load_yaml, mock_glob):
        """Test that list_available_vehicle_configurations handles invalid YAML files."""
        # Mock the glob results
        mock_path1 = MagicMock()
        mock_path1.stem = 'default_bet'
        mock_path2 = MagicMock()
        mock_path2.stem = 'invalid_yaml'
        mock_glob.return_value = [mock_path1, mock_path2]
        
        # Mock the YAML loading results
        mock_load_yaml.side_effect = [
            {'type': 'battery_electric'},  # default_bet
            {},                           # invalid_yaml (missing type)
        ]
        
        # Call the function
        result = list_available_vehicle_configurations()
        
        # Verify the glob was called with the right pattern
        mock_glob.assert_called_once_with('*.yaml')
        
        # Verify YAML files were loaded
        assert mock_load_yaml.call_count == 2
        
        # Verify the result contains only the valid configuration
        assert len(result[VehicleType.BATTERY_ELECTRIC]) == 1
        assert 'default_bet' in result[VehicleType.BATTERY_ELECTRIC] 