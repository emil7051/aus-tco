"""
Navigation State Management Utilities

This module provides utilities for managing application navigation state,
including step tracking, navigation history, and state transitions.
This is distinct from the UI components in ui/navigation.py which render
the navigation interface elements.
"""

import streamlit as st
from typing import List, Dict, Any, Optional, Tuple, Union

# Navigation step definitions
APP_STEPS = [
    {"id": "config", "label": "Vehicle Configuration", "icon": "🚚", "complete": False},
    {"id": "results", "label": "Results & Comparison", "icon": "📊", "complete": False},
    {"id": "export", "label": "Export & Share", "icon": "📤", "complete": False},
    {"id": "guide", "label": "User Guide", "icon": "📘", "complete": False}
]

def initialize_navigation():
    """
    Initialize navigation state in the session.
    """
    if "current_step" not in st.session_state:
        st.session_state.current_step = "config"
    
    if "nav_history" not in st.session_state:
        st.session_state.nav_history = ["config"]


def get_current_step():
    """
    Get the current navigation step.
    
    Returns:
        The current step ID
    """
    return st.session_state.get("current_step", "config")


def set_step(step_id: str, add_to_history: bool = True):
    """
    Set the current navigation step.
    
    Args:
        step_id: The step ID to navigate to
        add_to_history: Whether to add this step to navigation history
    """
    if step_id not in [step["id"] for step in APP_STEPS]:
        raise ValueError(f"Invalid step ID: {step_id}")
    
    st.session_state.current_step = step_id
    
    # Add to navigation history if requested
    if add_to_history:
        if "nav_history" not in st.session_state:
            st.session_state.nav_history = []
        
        # Avoid duplicate entries in sequence
        if not st.session_state.nav_history or st.session_state.nav_history[-1] != step_id:
            st.session_state.nav_history.append(step_id)


def get_navigation_history():
    """
    Get the navigation history.
    
    Returns:
        List of step IDs in navigation history
    """
    if "nav_history" not in st.session_state:
        st.session_state.nav_history = ["config"]
    
    return st.session_state.nav_history


def navigate_to_history_point(index: int):
    """
    Navigate to a specific point in history.
    
    Args:
        index: The index in the history list to navigate to
    """
    history = get_navigation_history()
    
    if 0 <= index < len(history):
        step_id = history[index]
        
        # Truncate history up to this point
        st.session_state.nav_history = history[:index + 1]
        
        # Set the current step
        st.session_state.current_step = step_id


def get_steps_with_status():
    """
    Get all application steps with their current status.
    
    Returns:
        List of step dictionaries with updated completion status
    """
    steps = APP_STEPS.copy()
    current_step = get_current_step()
    
    # Update completion status based on app state
    if "results" in st.session_state and st.session_state.results:
        # Mark configuration step as complete if results exist
        steps[0]["complete"] = True
    
    # Mark the current step
    for step in steps:
        step["current"] = (step["id"] == current_step)
    
    return steps


def can_proceed_to_step(step_id: str) -> bool:
    """
    Check if the user can proceed to a specific step.
    
    Args:
        step_id: The step ID to check
        
    Returns:
        True if the user can proceed to this step, False otherwise
    """
    if step_id == "config":
        # Always allow navigation to configuration
        return True
    
    elif step_id == "results":
        # Can only view results if they've been calculated
        return "results" in st.session_state and st.session_state.results is not None
    
    elif step_id == "export":
        # Can only export if results exist
        return "results" in st.session_state and st.session_state.results is not None
    
    elif step_id == "guide":
        # Anyone can view the guide
        return True
    
    # Default to False for unknown steps
    return False 