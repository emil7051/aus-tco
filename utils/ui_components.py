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
                   vehicle_type: Optional[str] = None,
                   card_type: Optional[str] = None) -> st.container:
        """
        Create a styled card container
        
        Args:
            title: Card title text
            key: Optional unique key for the card
            vehicle_type: Optional vehicle type for styling
            card_type: Optional card type (info, warning, error, success)
        
        Returns:
            The streamlit container object
        """
        # Create unique ID if key not provided
        component_id = key or f"card_{uuid.uuid4().hex[:8]}"
        
        # Apply vehicle-specific styling if vehicle type provided
        type_class = ""
        if vehicle_type:
            type_class += f" vehicle-{vehicle_type}"
        if card_type:
            type_class += f" {card_type}-card"
        
        # Create card container with styling
        st.markdown(f'<div class="card{type_class}" id="{component_id}">', 
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