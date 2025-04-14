"""
Navigation UI Components

This module provides UI components for application navigation,
including step indicators, breadcrumb navigation, and section headers.
It renders the navigation interface based on state managed by utils/navigation_state.py.
"""

import streamlit as st
from typing import List, Dict, Any, Optional, Tuple, Union

from utils.navigation_state import (
    get_current_step,
    set_step,
    get_steps_with_status,
    get_navigation_history,
    navigate_to_history_point,
    can_proceed_to_step
)


def render_step_navigation():
    """
    Render the step-based navigation structure.
    
    Displays the main application steps as a horizontal navigation bar
    with visual indicators for current and completed steps.
    """
    # Get all steps with updated status
    steps = get_steps_with_status()
    
    # Render the step navigation container
    st.markdown('<div class="step-navigation">', unsafe_allow_html=True)
    
    # Create columns for each step
    cols = st.columns(len(steps))
    
    # Render each step
    for i, step in enumerate(steps):
        with cols[i]:
            # Determine the CSS classes for this step
            css_classes = ["step-item"]
            if step.get("current", False):
                css_classes.append("active")
            if step.get("complete", False):
                css_classes.append("completed")
            
            # Check if the user can navigate to this step
            is_disabled = not can_proceed_to_step(step["id"])
            
            # Create a unique ID for this step
            step_id = f"step_{step['id']}"
            
            # Render the step indicator with appropriate styling
            st.markdown(f"""
            <div class="{' '.join(css_classes)}" id="{step_id}" 
                 data-step="{step['id']}" 
                 {"disabled" if is_disabled else ""}>
                <div class="step-icon">{step['icon']}</div>
                <div class="step-label">{step['label']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Add a button to handle the click (hidden but functional)
            if not is_disabled and not step.get("current", False):
                st.button(
                    step["label"],
                    key=f"nav_step_{step['id']}",
                    on_click=set_step,
                    args=(step["id"],),
                    help=f"Navigate to {step['label']}",
                    label_visibility="collapsed"
                )
    
    st.markdown('</div>', unsafe_allow_html=True)


def render_progress_indicator():
    """
    Render a progress indicator showing the current position in the application flow.
    
    This component displays the steps as a numbered horizontal progress bar with
    connecting lines showing the flow between steps.
    """
    # Get all steps with updated status
    steps = get_steps_with_status()
    
    # Render the progress indicator container
    st.markdown('<div class="progress-indicator">', unsafe_allow_html=True)
    
    # Render each step
    for i, step in enumerate(steps):
        # Determine the CSS classes for this step
        css_classes = ["progress-step"]
        if step.get("current", False):
            css_classes.append("active")
        if step.get("complete", False):
            css_classes.append("completed")
        
        # Create step number
        step_number = i + 1
        
        # Render the progress step
        st.markdown(f"""
        <div class="{' '.join(css_classes)}">
            <div class="step-number">{step_number}</div>
            <div class="step-label">{step['label']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)


def render_breadcrumb_navigation():
    """
    Render breadcrumb navigation with history.
    
    Displays the navigation path the user has taken through the application,
    allowing them to go back to previous sections.
    """
    # Get the navigation history
    history = get_navigation_history()
    
    # Get all steps with labels
    steps_dict = {step["id"]: step for step in get_steps_with_status()}
    
    # Render the breadcrumbs container
    st.markdown('<div class="breadcrumbs">', unsafe_allow_html=True)
    
    # Process each item in the history
    for i, step_id in enumerate(history):
        # Skip duplicates in sequence
        if i > 0 and step_id == history[i-1]:
            continue
        
        # Add a breadcrumb item
        st.markdown(f'<div class="breadcrumb-item{" active" if i == len(history) - 1 else ""}">', unsafe_allow_html=True)
        
        # Get the step label
        step_label = steps_dict.get(step_id, {}).get("label", step_id.replace("_", " ").title())
        
        # Current item is not clickable
        if i == len(history) - 1:
            st.markdown(f'{step_label}', unsafe_allow_html=True)
        else:
            # Create a button for navigation
            st.button(
                step_label,
                key=f"breadcrumb_{i}_{step_id}",
                on_click=navigate_to_history_point,
                args=(i,),
                help=f"Go back to {step_label}"
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)


def render_section_header(title: str, subtitle: Optional[str] = None):
    """
    Render a consistent section header.
    
    Args:
        title: The section title
        subtitle: Optional subtitle text
    """
    st.markdown(f'<div class="section-header">', unsafe_allow_html=True)
    st.markdown(f'<h2 class="section-title">{title}</h2>', unsafe_allow_html=True)
    
    if subtitle:
        st.markdown(f'<p class="section-subtitle">{subtitle}</p>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)


def render_subsection_header(title: str, icon: Optional[str] = None):
    """
    Render a consistent subsection header.
    
    Args:
        title: The subsection title
        icon: Optional icon character (emoji)
    """
    icon_html = f'<span class="subsection-icon">{icon}</span>' if icon else ''
    
    st.markdown(f"""
    <div class="subsection-header">
        {icon_html}
        <h3 class="subsection-title">{title}</h3>
    </div>
    """, unsafe_allow_html=True)


def render_expandable_section(title: str, content_callable, expanded: bool = False, key: Optional[str] = None):
    """
    Render an expandable section with consistent styling.
    
    Args:
        title: The section title
        content_callable: A callable that renders the content
        expanded: Whether the section is initially expanded
        key: An optional key for streamlit state
    """
    section_key = key or f"expandable_{title.lower().replace(' ', '_')}"
    
    # Create a custom expandable section with our CSS
    st.markdown(f"""
    <div class="expandable-section">
        <div class="expandable-header" id="{section_key}_header">
            <span>{title}</span>
            <span class="expand-icon">▼</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Use streamlit's expander for the functionality
    with st.expander(title, expanded=expanded, label_visibility="collapsed"):
        content_callable() 