"""
UI Input Components Module

This module contains UI components for user inputs.
"""

from ui.inputs.vehicle import render_vehicle_inputs
from ui.inputs.operational import render_operational_inputs, render_operational_parameters
from ui.inputs.economic import render_economic_inputs, render_economic_parameters
from ui.inputs.financing import render_financing_inputs
from ui.inputs.validation import validate_parameter, create_validated_input
from ui.inputs.parameter_helpers import (
    render_parameter_with_impact,
    get_parameter_impact,
    render_parameter_comparison,
    format_parameter_value,
    get_vehicle_type,
    render_vehicle_header
)
from ui.inputs.parameter_comparison import (
    render_parameter_comparison_tool,
    render_comparison,
    add_parameter_comparison_css
)

"""
UI Inputs Subpackage

This subpackage contains UI modules for rendering input forms and widgets
for different aspects of the TCO model.
""" 