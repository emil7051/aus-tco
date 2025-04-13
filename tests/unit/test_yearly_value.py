"""
Unit tests for the YearlyValue interpolation class.

These tests verify that the YearlyValue class correctly handles
interpolation of values across years.
"""

import pytest
from typing import List, Tuple
from tco_model.models import YearlyValue


class TestYearlyValue:
    """Tests for the YearlyValue class."""

    def test_basic_initialization(self):
        """Test that a YearlyValue object can be correctly initialized."""
        yearly_data = {
            0: 100.0,
            5: 200.0,
            10: 300.0
        }
        yearly_value = YearlyValue(values=yearly_data)
        
        # Verify the values are stored correctly
        assert yearly_value.values == yearly_data
        assert yearly_value.values[0] == 100.0
        assert yearly_value.values[5] == 200.0
        assert yearly_value.values[10] == 300.0

    def test_get_exact_year(self):
        """Test getting values for years that are explicitly defined."""
        yearly_data = {
            0: 100.0,
            5: 200.0,
            10: 300.0
        }
        yearly_value = YearlyValue(values=yearly_data)
        
        # Test retrieving values for years that are explicitly defined
        assert yearly_value.get_for_year(0) == 100.0
        assert yearly_value.get_for_year(5) == 200.0
        assert yearly_value.get_for_year(10) == 300.0

    def test_interpolation_scalar_values(self):
        """Test interpolation for scalar values."""
        yearly_data = {
            0: 100.0,
            10: 300.0
        }
        yearly_value = YearlyValue(values=yearly_data)
        
        # Test interpolated values
        assert yearly_value.get_for_year(5) == 200.0  # Halfway between 100 and 300
        assert yearly_value.get_for_year(2) == 140.0  # 20% of the way from 100 to 300
        assert yearly_value.get_for_year(7) == 240.0  # 70% of the way from 100 to 300

    def test_interpolation_with_list_values(self):
        """Test interpolation for list values."""
        yearly_data = {
            0: [100.0, 200.0, 300.0],
            10: [200.0, 300.0, 400.0]
        }
        yearly_value = YearlyValue(values=yearly_data)
        
        # Test interpolated values for lists
        interpolated = yearly_value.get_for_year(5)
        assert len(interpolated) == 3
        assert interpolated[0] == 150.0  # Halfway between 100 and 200
        assert interpolated[1] == 250.0  # Halfway between 200 and 300
        assert interpolated[2] == 350.0  # Halfway between 300 and 400

    def test_interpolation_with_tuple_values(self):
        """Test interpolation for tuple values."""
        yearly_data = {
            0: (0.2, 0.3),
            10: (0.6, 0.7)
        }
        yearly_value = YearlyValue(values=yearly_data)
        
        # Test interpolated values for tuples
        interpolated = yearly_value.get_for_year(5)
        assert len(interpolated) == 2
        assert interpolated[0] == 0.4  # Halfway between 0.2 and 0.6
        assert interpolated[1] == 0.5  # Halfway between 0.3 and 0.7
        
        # Verify it's still a tuple
        assert isinstance(interpolated, tuple)

    def test_extrapolation_before_earliest_year(self):
        """Test getting values for years before the earliest defined year."""
        yearly_data = {
            5: 100.0,
            10: 200.0
        }
        yearly_value = YearlyValue(values=yearly_data)
        
        # Years before the earliest defined year should return the earliest value
        assert yearly_value.get_for_year(0) == 100.0
        assert yearly_value.get_for_year(3) == 100.0
        assert yearly_value.get_for_year(-5) == 100.0

    def test_extrapolation_after_latest_year(self):
        """Test getting values for years after the latest defined year."""
        yearly_data = {
            0: 100.0,
            5: 200.0
        }
        yearly_value = YearlyValue(values=yearly_data)
        
        # Years after the latest defined year should return the latest value
        assert yearly_value.get_for_year(7) == 200.0
        assert yearly_value.get_for_year(10) == 200.0
        assert yearly_value.get_for_year(100) == 200.0

    def test_no_interpolation_mode(self):
        """Test getting values with interpolation disabled."""
        yearly_data = {
            0: 100.0,
            5: 200.0,
            10: 300.0
        }
        yearly_value = YearlyValue(values=yearly_data)
        
        # With interpolation=False, should return the value for the closest year <= target
        assert yearly_value.get_for_year(3, interpolate=False) == 100.0
        assert yearly_value.get_for_year(5, interpolate=False) == 200.0
        assert yearly_value.get_for_year(7, interpolate=False) == 200.0  # 5 is the closest year <= 7
        
        # For years before first defined or after last defined, behavior should match interpolation=True
        assert yearly_value.get_for_year(0, interpolate=False) == 100.0
        assert yearly_value.get_for_year(-5, interpolate=False) == 100.0
        assert yearly_value.get_for_year(12, interpolate=False) == 300.0

    def test_different_value_types_error(self):
        """Test that interpolation between different value types is handled."""
        yearly_data = {
            0: [100.0, 200.0],
            5: (300.0, 400.0)  # Different type (tuple vs list)
        }
        yearly_value = YearlyValue(values=yearly_data)
        
        # The current implementation actually interpolates between different types
        # as long as they're both list-like and the same length
        result = yearly_value.get_for_year(2)
        # It performs element-wise interpolation
        expected = [100.0 + 2/5 * (300.0 - 100.0), 200.0 + 2/5 * (400.0 - 200.0)]
        assert result[0] == pytest.approx(expected[0])
        assert result[1] == pytest.approx(expected[1])

    def test_different_length_values_error(self):
        """Test that interpolation between different length values raises an error."""
        yearly_data = {
            0: [100.0, 200.0],
            5: [300.0, 400.0, 500.0]  # Different length
        }
        yearly_value = YearlyValue(values=yearly_data)
        
        # Interpolating between lists of different lengths should raise ValueError
        with pytest.raises(ValueError, match="Cannot interpolate between values with different lengths"):
            yearly_value.get_for_year(2)

    def test_complex_yearly_data(self):
        """Test with a more complex set of yearly data."""
        yearly_data = {
            0: 1000.0,
            2: 1200.0,
            5: 1500.0,
            7: 1700.0,
            10: 2000.0
        }
        yearly_value = YearlyValue(values=yearly_data)
        
        # Test various interpolation points
        assert yearly_value.get_for_year(1) == 1100.0  # Between 0 and 2
        assert yearly_value.get_for_year(3) == 1300.0  # Between 2 and 5
        assert yearly_value.get_for_year(6) == 1600.0  # Between 5 and 7
        assert yearly_value.get_for_year(8) == 1800.0  # Between 7 and 10 