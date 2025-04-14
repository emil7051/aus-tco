"""
Utils Package

This package contains utility functions for the
Australian Heavy Vehicle TCO Modeller application.
"""

# Import key utility functions for easier access
from .helpers import get_safe_state_value, set_safe_state_value
from .navigation_state import get_current_step, set_step, initialize_navigation
from .ui_terminology import get_formatted_label, get_component_color
from .css_loader import load_css