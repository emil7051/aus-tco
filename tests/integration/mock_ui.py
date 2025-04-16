"""
Mock UI Components for Testing

This module provides mock implementations of UI components that can be used in tests
without requiring a Streamlit runtime context.
"""

from typing import Dict, Any, Optional
import streamlit as st

class MockUIComponentFactory:
    """Mock UI Component Factory for testing purposes."""
    
    @staticmethod
    def create_card(title: str, key: Optional[str] = None, 
                   vehicle_type: Optional[str] = None,
                   card_type: Optional[str] = None) -> str:
        """
        Create a mock card for testing.
        
        Args:
            title: Card title
            key: Optional key
            vehicle_type: Optional vehicle type
            card_type: Optional card type
            
        Returns:
            Mock HTML string
        """
        return f'<div class="card" id="{key}">{title}</div>'


def mock_render_layout(config: Dict[str, Any], content: Dict[str, Any] = None, current_step: str = None) -> str:
    """
    Mock implementation of render_layout for testing.
    
    Args:
        config: Layout configuration
        content: Optional content dictionary
        current_step: Optional current step
        
    Returns:
        Mock HTML string with layout information
    """
    mode = config.get("mode", "step_by_step")
    
    # Extract vehicle names if present
    vehicle_names = []
    if content and isinstance(content, dict):
        if "vehicle_1" in content and hasattr(content["vehicle_1"], "vehicle_name"):
            vehicle_names.append(content["vehicle_1"].vehicle_name)
        if "vehicle_2" in content and hasattr(content["vehicle_2"], "vehicle_name"):
            vehicle_names.append(content["vehicle_2"].vehicle_name)
    
    # Create a mock layout string
    layout_html = f'<div class="layout" data-mode="{mode}" data-step="{current_step or ""}">'
    
    # Add vehicle information if available
    for name in vehicle_names:
        layout_html += f'<div class="vehicle">{name}</div>'
    
    layout_html += '</div>'
    
    return layout_html


def mock_render_vehicle_inputs(vehicle_number: int, compact: bool = False) -> str:
    """
    Mock implementation of render_vehicle_inputs for testing.
    
    Args:
        vehicle_number: Vehicle number
        compact: Whether to use compact mode
        
    Returns:
        Mock HTML string
    """
    return f'<div class="vehicle-inputs" data-vehicle="{vehicle_number}" data-compact="{compact}"></div>'


# Replace the actual UI components with mocks for testing
import ui.layout
import ui.inputs.vehicle
import utils.ui_components

# Store original implementations
_original_render_layout = getattr(ui.layout, "render_layout", None)
_original_render_vehicle_inputs = getattr(ui.inputs.vehicle, "render_vehicle_inputs", None)
_original_UIComponentFactory = getattr(utils.ui_components, "UIComponentFactory", None)

def enable_mock_ui():
    """Enable mock UI components for testing."""
    ui.layout.render_layout = mock_render_layout
    ui.inputs.vehicle.render_vehicle_inputs = mock_render_vehicle_inputs
    utils.ui_components.UIComponentFactory = MockUIComponentFactory

def disable_mock_ui():
    """Restore original UI components."""
    if _original_render_layout:
        ui.layout.render_layout = _original_render_layout
    if _original_render_vehicle_inputs:
        ui.inputs.vehicle.render_vehicle_inputs = _original_render_vehicle_inputs
    if _original_UIComponentFactory:
        utils.ui_components.UIComponentFactory = _original_UIComponentFactory 