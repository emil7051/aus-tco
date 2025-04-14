# Refactoring Phase 1: Terminology Standardization and UI Utilities

This document outlines the first phase of the UI refactoring process for the Australian Heavy Vehicle TCO Modeller, focusing on terminology standardization and the creation of utility modules to support a consistent UI experience.

## Overview

Phase 1 establishes the foundation for all subsequent UI improvements by ensuring consistent terminology across the application and creating utility modules that will be used throughout the refactoring process. This phase creates minimal visual changes but establishes the underlying architecture needed for future enhancements.

## Implementation Tasks

### 1. Create UI Terminology Utility Module

Create a new file `utils/ui_terminology.py` that will centralize all terminology-related utilities and serve as a bridge between the `tco_model/terminology.py` and the UI components:

```python
"""
UI Terminology Utilities

This module provides utilities for consistent terminology usage in the UI layer,
drawing from the canonical definitions in tco_model/terminology.py. It includes
functions for formatting, labelling, and accessing standard terminology.
"""

from typing import Dict, List, Any, Optional, Union, Tuple
from tco_model.terminology import (
    UI_COMPONENT_LABELS,
    UI_COMPONENT_MAPPING,
    VEHICLE_TYPE_LABELS,
    VEHICLE_CATEGORY_LABELS,
    COST_COMPONENTS,
    UI_COMPONENT_KEYS,
    get_ui_component_label,
    get_component_description,
)


def get_formatted_label(key: str, include_units: bool = False, 
                       include_tooltip: bool = False) -> Union[str, Tuple[str, str]]:
    """
    Get a consistently formatted label for a UI element with optional units and tooltip.
    
    Args:
        key: The terminology key
        include_units: Whether to include units in the label
        include_tooltip: Whether to include a tooltip 
        
    Returns:
        The formatted label string, or a tuple of (label, tooltip) if include_tooltip is True
    """
    # Get the base label
    if key in UI_COMPONENT_LABELS:
        label = UI_COMPONENT_LABELS[key]
    elif key in VEHICLE_TYPE_LABELS:
        label = VEHICLE_TYPE_LABELS[key]
    elif key in VEHICLE_CATEGORY_LABELS:
        label = VEHICLE_CATEGORY_LABELS[key]
    else:
        # Use key as fallback with title casing and underscores replaced
        label = key.replace('_', ' ').title()
    
    # Add units if requested and available
    if include_units and key in UI_COMPONENT_MAPPING:
        units = UI_COMPONENT_MAPPING[key].get('units', '')
        if units:
            label = f"{label} ({units})"
    
    # Generate tooltip if requested
    if include_tooltip:
        tooltip = get_component_description(key) if key in UI_COMPONENT_KEYS else ''
        return label, tooltip
    
    return label


def create_impact_indicator(key: str) -> dict:
    """
    Create an impact indicator configuration for a parameter.
    
    Args:
        key: The parameter key
        
    Returns:
        A dictionary with impact level, icon, and tooltip
    """
    # Map component keys to impact levels
    impact_mapping = {
        # High impact components
        "acquisition": "high",
        "energy": "high",
        "battery_replacement": "high",
        
        # Medium impact components
        "maintenance": "medium",
        "infrastructure": "medium",
        "residual_value": "medium",
        
        # Low impact components
        "insurance_registration": "low",
        "taxes_levies": "low",
    }
    
    # Map operation parameters to impact levels
    operation_impact_mapping = {
        "annual_distance_km": "high",
        "analysis_period_years": "high",
        "discount_rate_real": "medium",
        "load_factor": "medium",
        "vehicle_life_years": "medium",
        "operating_days_per_year": "low",
    }
    
    # Combine mappings
    all_impacts = {**impact_mapping, **operation_impact_mapping}
    
    # Get impact level with fallback to medium
    impact_level = all_impacts.get(key, "medium")
    
    # Define icons and tooltips for each impact level
    impact_indicators = {
        "high": {
            "icon": "🔴",
            "tooltip": "High impact on TCO results",
            "class": "high"
        },
        "medium": {
            "icon": "🟠", 
            "tooltip": "Medium impact on TCO results",
            "class": "medium"
        },
        "low": {
            "icon": "🟢",
            "tooltip": "Low impact on TCO results",
            "class": "low"
        }
    }
    
    return impact_indicators[impact_level]


def get_component_color(component_key: str) -> str:
    """
    Get the standard color for a cost component.
    
    Args:
        component_key: The component key
        
    Returns:
        The hex color code for the component
    """
    if component_key in UI_COMPONENT_MAPPING:
        return UI_COMPONENT_MAPPING[component_key].get('color', '#7f7f7f')
    return '#7f7f7f'  # Default gray


def get_vehicle_type_color(vehicle_type: str) -> str:
    """
    Get the standard color for a vehicle type.
    
    Args:
        vehicle_type: The vehicle type string
        
    Returns:
        The hex color code for the vehicle type
    """
    vehicle_colors = {
        "battery_electric": "#26A69A",  # Teal
        "diesel": "#FB8C00",            # Orange
    }
    return vehicle_colors.get(vehicle_type, "#7f7f7f")


def get_australian_spelling(term: str) -> str:
    """
    Convert a term to Australian English spelling.
    
    Args:
        term: The term to convert
        
    Returns:
        The term with Australian English spelling
    """
    # Common US to Australian English spelling conversions
    spelling_map = {
        "color": "colour",
        "center": "centre", 
        "kilometer": "kilometre",
        "liter": "litre",
        "modeling": "modelling",
        "modeled": "modelled",
        "license": "licence",
        "analyze": "analyse",
        "analyzed": "analysed",
        "analyzing": "analysing",
        "customize": "customise",
        "customized": "customised",
        "customizing": "customising",
    }
    
    result = term
    
    # Apply each conversion
    for us_spelling, aus_spelling in spelling_map.items():
        # Case-insensitive replacement preserving case
        if us_spelling in result.lower():
            i = result.lower().find(us_spelling)
            orig_case = result[i:i+len(us_spelling)]
            if orig_case.isupper():
                replacement = aus_spelling.upper()
            elif orig_case[0].isupper():
                replacement = aus_spelling.capitalize()
            else:
                replacement = aus_spelling
                
            result = result.replace(orig_case, replacement)
    
    return result
```

### 2. Create UI Component Factory Module

Create a new file `utils/ui_components.py` to provide consistent UI component creation:

```python
"""
UI Component Factory

This module provides factory functions for creating consistent UI components
across the application. It centralizes styling, layout, and behavior of common
UI elements, ensuring a consistent user experience.
"""

import streamlit as st
from typing import Optional, Dict, Any, List, Tuple, Union, Callable
import uuid

from utils.ui_terminology import (
    get_formatted_label,
    get_component_color,
    get_vehicle_type_color,
    create_impact_indicator
)

from utils.helpers import get_safe_state_value, set_safe_state_value


class UIComponentFactory:
    """Factory class for creating consistent UI components"""
    
    @staticmethod
    def create_card(title: str, key: Optional[str] = None, 
                   vehicle_type: Optional[str] = None) -> st.container:
        """
        Create a styled card container
        
        Args:
            title: Card title text
            key: Optional unique key for the card
            vehicle_type: Optional vehicle type for styling
        
        Returns:
            The streamlit container object
        """
        # Create unique ID if key not provided
        component_id = key or f"card_{uuid.uuid4().hex[:8]}"
        
        # Apply vehicle-specific styling if vehicle type provided
        type_class = f" vehicle-{vehicle_type}" if vehicle_type else ""
        vehicle_color = get_vehicle_type_color(vehicle_type) if vehicle_type else None
        
        # Create style with optional vehicle color
        style = f"border-left-color: {vehicle_color};" if vehicle_color else ""
        
        # Create card container with styling
        st.markdown(f'<div class="card{type_class}" id="{component_id}" style="{style}">', 
                    unsafe_allow_html=True)
        st.markdown(f'<h3 class="card-title">{title}</h3>', unsafe_allow_html=True)
        
        # Create the container for content
        card_container = st.container()
        
        # Close the card div
        st.markdown('</div>', unsafe_allow_html=True)
        
        return card_container
    
    @staticmethod
    def create_input_group(label: str) -> st.container:
        """
        Create a styled input group
        
        Args:
            label: Group label text
            
        Returns:
            The streamlit container for input fields
        """
        st.markdown(f'<div class="input-group">', unsafe_allow_html=True)
        st.markdown(f'<p class="group-label">{label}</p>', unsafe_allow_html=True)
        
        container = st.container()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        return container
    
    @staticmethod
    def create_validated_input(
        label: str, 
        key: str, 
        min_value: Optional[Union[float, List]] = None,
        max_value: Optional[float] = None, 
        default: Optional[Any] = None,
        help_text: Optional[str] = None,
        required: bool = False,
        validate_fn: Optional[Callable] = None,
        impact_level: Optional[str] = None
    ) -> Any:
        """
        Create an input field with validation and visual feedback
        
        Args:
            label: Input field label
            key: Session state key 
            min_value: Minimum value or list of options for selectbox
            max_value: Maximum value
            default: Default value
            help_text: Help tooltip text
            required: Whether the field is required
            validate_fn: Custom validation function
            impact_level: Impact level (high/medium/low) for indicator
            
        Returns:
            The input value
        """
        # Validation state key
        validation_key = f"{key}_validation"
        
        # Check if field has been validated before
        is_valid = st.session_state.get(validation_key, {"valid": True, "message": ""})
        
        # Add impact indicator if specified
        if impact_level:
            impact_info = create_impact_indicator(key.split('.')[-1])
            col1, col2 = st.columns([0.9, 0.1])
            
            with col1:
                container_start = '<div class="input-container{}">'
                input_class = " invalid-input" if not is_valid["valid"] else ""
                st.markdown(container_start.format(input_class), unsafe_allow_html=True)
        else:
            # Create input container with conditional styling
            container_start = '<div class="input-container{}">'
            input_class = " invalid-input" if not is_valid["valid"] else ""
            st.markdown(container_start.format(input_class), unsafe_allow_html=True)
        
        # Get current value from session state or use default
        current_value = get_safe_state_value(key, default)
        
        # Create the appropriate input field
        if isinstance(default, bool):
            value = st.checkbox(label, value=current_value, key=f"{key}_input", help=help_text)
        elif isinstance(default, (int, float)):
            value = st.number_input(label, min_value=min_value, max_value=max_value,
                                value=float(current_value) if current_value is not None else 0.0, 
                                key=f"{key}_input", help=help_text)
        elif isinstance(min_value, list):
            # This is a select field
            index = 0
            if current_value in min_value:
                index = min_value.index(current_value)
            value = st.selectbox(label, options=min_value, index=index, 
                               key=f"{key}_input", help=help_text)
        else:
            value = st.text_input(label, value=current_value if current_value is not None else "", 
                                key=f"{key}_input", help=help_text)
        
        # Perform validation when the value changes
        if f"{key}_input" in st.session_state:
            # Simple required validation
            if required and not value:
                is_valid = {"valid": False, "message": "This field is required"}
            # Range validation for numbers
            elif isinstance(value, (int, float)) and (
                (min_value is not None and value < min_value) or 
                (max_value is not None and value > max_value)):
                is_valid = {"valid": False, "message": f"Value must be between {min_value} and {max_value}"}
            # Custom validation
            elif validate_fn:
                is_valid = validate_fn(value)
            else:
                is_valid = {"valid": True, "message": ""}
            
            # Store validation state
            st.session_state[validation_key] = is_valid
            
            # Update the value in session state if valid
            if is_valid["valid"]:
                set_safe_state_value(key, value)
        
        # Show validation message if invalid
        if not is_valid["valid"]:
            st.markdown(f'<div class="validation-message">{is_valid["message"]}</div>', 
                      unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Add impact indicator in second column if applicable
        if impact_level:
            with col2:
                st.markdown(f"""
                <div class="impact-indicator" title="{impact_info['tooltip']}">
                    {impact_info['icon']}
                </div>
                """, unsafe_allow_html=True)
        
        return value
    
    @staticmethod
    def create_parameter_with_impact(
        label: str, 
        key: str, 
        default: Any, 
        **input_args
    ) -> Any:
        """
        Create a parameter input with impact indicator
        
        Args:
            label: Parameter label
            key: Session state key
            default: Default value
            **input_args: Additional arguments for the input
            
        Returns:
            Input value
        """
        # Extract the parameter name from the key
        param_name = key.split('.')[-1]
        
        # Create the input with impact indicator
        return UIComponentFactory.create_validated_input(
            label=label,
            key=key,
            default=default,
            impact_level=param_name,
            **input_args
        )
    
    @staticmethod
    def create_metric_display(
        label: str, 
        value: Any, 
        delta: Optional[Any] = None, 
        help_text: Optional[str] = None,
        color: Optional[str] = None
    ) -> None:
        """
        Create a styled metric display
        
        Args:
            label: Metric label
            value: Metric value to display
            delta: Optional delta value
            help_text: Optional help text
            color: Optional color for the metric
        """
        # Apply custom styling with color if provided
        style = f"color: {color};" if color else ""
        
        # Create a styled metric container
        st.markdown(f'<div class="metric-container" style="{style}">', unsafe_allow_html=True)
        
        # Use Streamlit's metric component with our styling applied
        if delta is not None:
            st.metric(label=label, value=value, delta=delta, help=help_text)
        else:
            st.metric(label=label, value=value, help=help_text)
        
        st.markdown('</div>', unsafe_allow_html=True)
```

### 3. Update Utility Helpers Module

Update `utils/helpers.py` to add functions for working with the new terminology and component systems:

```python
# Add these imports to the top of the file
from tco_model.terminology import (
    UI_COMPONENT_LABELS,
    UI_COMPONENT_MAPPING,
    VEHICLE_TYPE_LABELS,
    COST_COMPONENTS
)

# Add these functions at an appropriate location in the file

def format_currency(value: float, include_cents: bool = False) -> str:
    """
    Format a value as Australian dollars.
    
    Args:
        value: The numeric value to format
        include_cents: Whether to include cents in the formatted output
        
    Returns:
        A formatted currency string
    """
    # Handle negative values
    is_negative = value < 0
    abs_value = abs(value)
    
    # Format with or without cents
    if include_cents:
        formatted = "${:,.2f}".format(abs_value)
    else:
        # Round to nearest dollar and format
        formatted = "${:,.0f}".format(round(abs_value))
    
    # Add negative sign if needed
    if is_negative:
        formatted = "-" + formatted
        
    return formatted


def format_percentage(value: float, decimal_places: int = 1) -> str:
    """
    Format a value as a percentage.
    
    Args:
        value: The value to format as percentage
        decimal_places: Number of decimal places to include
        
    Returns:
        A formatted percentage string
    """
    format_str = "{:." + str(decimal_places) + "f}%"
    return format_str.format(value)


def get_vehicle_type_label(vehicle_type: str) -> str:
    """
    Get the user-friendly label for a vehicle type.
    
    Args:
        vehicle_type: The vehicle type identifier
        
    Returns:
        The user-friendly label
    """
    return VEHICLE_TYPE_LABELS.get(vehicle_type, vehicle_type.replace('_', ' ').title())
```

### 4. Update UI Imports in Application and Components

Update the imports in `app.py` and key UI modules to use the new utilities:

1. In `app.py`:

```python
# Add these imports
from utils.ui_terminology import get_formatted_label, get_component_color
from utils.ui_components import UIComponentFactory
```

2. In `ui/sidebar.py`:

```python
# Update imports
from utils.ui_terminology import get_formatted_label, get_vehicle_type_color
from utils.ui_components import UIComponentFactory
```

3. In `ui/inputs/vehicle.py`:

```python
# Update imports
from utils.ui_terminology import get_formatted_label, get_component_description
from utils.ui_components import UIComponentFactory
```

### 5. Create CSS Directory Structure

Create a basic CSS directory structure for future implementation in Phase 2:

```
/static
  /css
    /base
    /components
    /themes
```

This structure will be populated with CSS files in Phase 2.

## Integration Steps

To implement Phase 1, follow these steps in order:

1. Create the directory structure for CSS files
2. Create the `utils/ui_terminology.py` module
3. Create the `utils/ui_components.py` module
4. Update `utils/helpers.py` with the new functions
5. Update imports in `app.py` and UI modules
6. Test the application to ensure there are no regressions

## Validation

The changes in Phase 1 should not cause any visual changes to the application but will establish the foundation for future phases. Verify that:

1. The application still functions correctly
2. The new utility modules can be imported without errors
3. Basic functionality like vehicle selection still works in the sidebar

## Test Impact

In Phase 1, the following test impacts should be anticipated:

1. **Unit Tests**: Tests for UI display functions may need updating to accommodate the new terminology functions
2. **Helper Function Tests**: Tests for utility functions will need to be extended to cover the new formatting functions
3. **Test Fixtures**: Some test fixtures may need updating to use the standardized terminology

## Next Steps

After completing Phase 1, proceed to Phase 2, which will implement the visual design system and improved styling for the application. Phase 2 will build upon the foundation established in Phase 1 by adding the actual CSS implementation. 