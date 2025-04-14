# Refactoring Phase 3: Navigation and Structure Improvements

This document outlines the third phase of the UI refactoring process for the Australian Heavy Vehicle TCO Modeller, focusing on improving the application's navigation structure and user flow.

## Overview

Phase 3 builds on the visual design system established in Phase 2 to create a more intuitive navigation experience. This phase enhances the application structure with step indicators, breadcrumb navigation, and configuration management features. These improvements will make the application more user-friendly and help users understand their current location within the application flow.

## Implementation Tasks

### 1. Create Navigation Utilities Module

Create a new file `utils/navigation.py` to handle navigation state and transitions:

```python
"""
Navigation Utilities

This module provides utilities for managing application navigation,
including step tracking, navigation history, and state transitions.
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
```

### 2. Implement Step-Based Navigation Structure

Create a new file `ui/navigation.py` to render navigation components:

```python
"""
Navigation UI Components

This module provides UI components for application navigation,
including step indicators, breadcrumb navigation, and section headers.
"""

import streamlit as st
from typing import List, Dict, Any, Optional, Tuple, Union

from utils.navigation import (
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
            css_classes = ["step-indicator"]
            if step.get("current", False):
                css_classes.append("current")
            if step.get("complete", False):
                css_classes.append("complete")
            
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
        
        # Add separator before items (except the first)
        if i > 0:
            st.markdown('<span class="separator">›</span>', unsafe_allow_html=True)
        
        # Get the step label
        step_label = steps_dict.get(step_id, {}).get("label", step_id.replace("_", " ").title())
        
        # Current item is not clickable
        if i == len(history) - 1:
            st.markdown(f'<span class="current">{step_label}</span>', unsafe_allow_html=True)
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
```

### 3. Implement Configuration Management Components

Create a new file `ui/config_management.py` to handle saving and loading configurations:

```python
"""
Configuration Management UI

This module provides UI components for managing vehicle configurations,
including saving, loading, and comparing configurations.
"""

import streamlit as st
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union

from utils.helpers import (
    load_default_scenario,
    update_state_from_model,
    update_model_from_state,
    get_safe_state_value
)
from tco_model.models import ScenarioInput, VehicleType


def get_config_directory() -> Path:
    """
    Get the directory for saved configurations.
    
    Returns:
        Path to the saved configurations directory
    """
    # Get the root directory of the application
    root_dir = Path(__file__).parent.parent
    
    # Create a directory for saved configurations if it doesn't exist
    config_dir = root_dir / "saved_configs"
    config_dir.mkdir(exist_ok=True)
    
    return config_dir


def save_current_config(name: str, vehicle_number: int = 1) -> bool:
    """
    Save the current vehicle configuration.
    
    Args:
        name: Name for the saved configuration
        vehicle_number: Which vehicle to save (1 or 2)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Get the configuration state
        state_key = f"vehicle_{vehicle_number}_input"
        
        if state_key not in st.session_state:
            st.error(f"No configuration data found for Vehicle {vehicle_number}")
            return False
        
        # Get the vehicle type
        vehicle_state = st.session_state[state_key]
        vehicle_type = vehicle_state.vehicle.type
        
        # Sanitize the name for use in a filename
        safe_name = name.replace(" ", "_").lower()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{safe_name}_{timestamp}.json"
        
        # Create separate directories for each vehicle type
        config_dir = get_config_directory()
        type_dir = config_dir / vehicle_type
        type_dir.mkdir(exist_ok=True)
        
        # Full path to the saved config file
        config_path = type_dir / filename
        
        # Convert the model to a dictionary for serialization
        config_data = {
            "name": name,
            "vehicle_type": vehicle_type,
            "timestamp": timestamp,
            "model": vehicle_state.dict()
        }
        
        # Save to file
        with open(config_path, "w") as f:
            json.dump(config_data, f, indent=2)
        
        st.success(f"Configuration '{name}' saved successfully")
        return True
        
    except Exception as e:
        st.error(f"Error saving configuration: {str(e)}")
        return False


def load_config(config_path: Union[str, Path], vehicle_number: int = 1) -> bool:
    """
    Load a saved configuration.
    
    Args:
        config_path: Path to the configuration file
        vehicle_number: Which vehicle to load into (1 or 2)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Convert string path to Path object if needed
        if isinstance(config_path, str):
            config_path = Path(config_path)
        
        # Check if the file exists
        if not config_path.exists():
            st.error(f"Configuration file not found: {config_path}")
            return False
        
        # Load the configuration data
        with open(config_path, "r") as f:
            config_data = json.load(f)
        
        # Create a ScenarioInput from the saved model
        model_data = config_data.get("model", {})
        scenario = ScenarioInput(**model_data)
        
        # Update the session state
        state_key = f"vehicle_{vehicle_number}_input"
        st.session_state[state_key] = scenario
        
        # Update nested state for UI components to reference
        update_state_from_model(state_key, scenario)
        
        st.success(f"Configuration '{config_data.get('name')}' loaded successfully")
        
        # Reset results when configuration changes
        if "results" in st.session_state:
            st.session_state.results = None
        
        if "show_results" in st.session_state:
            st.session_state.show_results = False
            
        return True
        
    except Exception as e:
        st.error(f"Error loading configuration: {str(e)}")
        return False


def get_saved_configs() -> Dict[str, List[Dict[str, Any]]]:
    """
    Get all saved configurations.
    
    Returns:
        Dictionary mapping vehicle types to lists of configuration metadata
    """
    configs = {}
    config_dir = get_config_directory()
    
    # Get configurations for each vehicle type
    for vehicle_type in [t.value for t in VehicleType]:
        type_dir = config_dir / vehicle_type
        
        if not type_dir.exists():
            continue
        
        # Find all JSON files in the directory
        config_files = list(type_dir.glob("*.json"))
        type_configs = []
        
        for file_path in config_files:
            try:
                with open(file_path, "r") as f:
                    config_data = json.load(f)
                
                # Extract metadata
                metadata = {
                    "name": config_data.get("name", file_path.stem),
                    "timestamp": config_data.get("timestamp", ""),
                    "path": str(file_path)
                }
                
                type_configs.append(metadata)
            except:
                # Skip files that can't be loaded
                continue
        
        # Sort by timestamp (newest first)
        type_configs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        configs[vehicle_type] = type_configs
    
    return configs


def render_config_management():
    """
    Render the configuration management UI.
    
    Provides interface for saving and loading vehicle configurations.
    """
    with st.expander("Configuration Management", expanded=False):
        # Create columns for save and load functionality
        save_col, load_col = st.columns(2)
        
        # Save configuration section
        with save_col:
            st.subheader("Save Configuration")
            
            # Select which vehicle to save
            vehicle_to_save = st.radio(
                "Select Vehicle",
                options=[1, 2],
                format_func=lambda x: f"Vehicle {x}",
                key="save_vehicle_selector",
                horizontal=True
            )
            
            # Input for configuration name
            config_name = st.text_input(
                "Configuration Name",
                value=get_safe_state_value(
                    f"vehicle_{vehicle_to_save}_input.vehicle.name", 
                    f"Vehicle {vehicle_to_save} Config"
                ),
                key="config_name_input"
            )
            
            # Save button
            st.button(
                "Save Configuration",
                on_click=save_current_config,
                args=(config_name, vehicle_to_save),
                key="save_config_button"
            )
        
        # Load configuration section
        with load_col:
            st.subheader("Load Configuration")
            
            # Get saved configurations
            saved_configs = get_saved_configs()
            
            # Vehicle type selector
            vehicle_types = list(saved_configs.keys())
            
            if vehicle_types:
                selected_type = st.selectbox(
                    "Vehicle Type",
                    options=vehicle_types,
                    format_func=lambda x: {"battery_electric": "Battery Electric", 
                                          "diesel": "Diesel"}[x],
                    key="load_type_selector"
                )
                
                # Configuration selector for the selected type
                type_configs = saved_configs.get(selected_type, [])
                
                if type_configs:
                    selected_config = st.selectbox(
                        "Select Configuration",
                        options=range(len(type_configs)),
                        format_func=lambda i: (
                            f"{type_configs[i]['name']} "
                            f"({datetime.strptime(type_configs[i]['timestamp'], '%Y%m%d_%H%M%S').strftime('%d %b %Y, %H:%M')})"
                        ),
                        key="load_config_selector"
                    )
                    
                    # Target vehicle selector
                    target_vehicle = st.radio(
                        "Load Into",
                        options=[1, 2],
                        format_func=lambda x: f"Vehicle {x}",
                        key="load_target_selector",
                        horizontal=True
                    )
                    
                    # Load button
                    if st.button(
                        "Load Selected",
                        key="load_config_button"
                    ):
                        config_path = type_configs[selected_config]["path"]
                        load_config(config_path, target_vehicle)
                        st.rerun()
                else:
                    st.info(f"No saved configurations found for {selected_type} vehicles")
            else:
                st.info("No saved configurations found")
```

### 4. Implement Progressive Disclosure Pattern

Create a progressive disclosure module in `ui/progressive_disclosure.py`:

```python
"""
Progressive Disclosure UI

This module implements the progressive disclosure pattern,
showing UI components based on the current navigation step.
"""

import streamlit as st
from typing import Dict, Any, Optional

from utils.navigation import get_current_step, set_step
from ui.navigation import render_step_navigation, render_breadcrumb_navigation
from ui.config_management import render_config_management
from ui.inputs.vehicle import render_vehicle_inputs
from ui.inputs.operational import render_operational_inputs
from ui.inputs.economic import render_economic_inputs
from ui.inputs.financing import render_financing_inputs
from ui.results.display import display_results
from ui.guide import render_guide


def implement_progressive_disclosure():
    """
    Implement progressive disclosure based on current step.
    
    This function renders different UI components based on the
    current navigation step, creating a guided user experience.
    """
    # Get current step
    current_step = get_current_step()
    
    # Always show step navigation at the top
    render_step_navigation()
    
    # Show breadcrumb navigation
    render_breadcrumb_navigation()
    
    # Render appropriate content for the current step
    if current_step == "config":
        render_configuration_step()
        
    elif current_step == "results":
        render_results_step()
        
    elif current_step == "export":
        render_export_step()
        
    elif current_step == "guide":
        render_guide_step()


def render_configuration_step():
    """
    Render the vehicle configuration step.
    """
    st.header("Vehicle Configuration")
    
    # Configuration management for saving/loading configs
    render_config_management()
    
    # Create columns for side-by-side vehicle inputs
    col1, col2 = st.columns(2)
    
    with col1:
        # Get vehicle type for display in header
        v1_type = st.session_state.get("vehicle_1_input", {}).vehicle.type
        v1_label = "BET" if v1_type == "battery_electric" else "ICE"
        
        st.subheader(f"Vehicle 1 ({v1_label})")
        render_vehicle_inputs(vehicle_number=1)
        render_operational_inputs(vehicle_number=1)
        render_economic_inputs(vehicle_number=1)
        render_financing_inputs(vehicle_number=1)
        
    with col2:
        # Get vehicle type for display in header
        v2_type = st.session_state.get("vehicle_2_input", {}).vehicle.type
        v2_label = "BET" if v2_type == "battery_electric" else "ICE"
        
        st.subheader(f"Vehicle 2 ({v2_label})")
        render_vehicle_inputs(vehicle_number=2)
        render_operational_inputs(vehicle_number=2)
        render_economic_inputs(vehicle_number=2)
        render_financing_inputs(vehicle_number=2)
    
    # Calculate button in a centered container
    _, center_col, _ = st.columns([1, 2, 1])
    with center_col:
        if st.button(
            "Calculate TCO", 
            on_click=calculate_and_show_results,
            key="calculate_button",
            use_container_width=True
        ):
            # Button callback will handle the calculation
            pass


def calculate_and_show_results():
    """
    Calculate TCO and show results.
    
    This function is called when the Calculate button is clicked.
    It performs the calculation and navigates to the results page.
    """
    from app import calculate_tco  # Import here to avoid circular imports
    
    # Calculate TCO
    calculate_tco()
    
    # Navigate to results page if calculation was successful
    if st.session_state.get("results") is not None:
        set_step("results")


def render_results_step():
    """
    Render the results step.
    """
    st.header("TCO Results")
    
    # Check if results are available
    if "results" in st.session_state and st.session_state.results is not None:
        results = st.session_state.results
        comparison = st.session_state.get("comparison")
        
        if results and comparison:
            # Display results
            display_results(results, comparison)
        else:
            st.warning("Results data is incomplete. Please recalculate TCO.")
            st.button(
                "Go to Configuration",
                on_click=set_step,
                args=("config",)
            )
    else:
        st.info("No results available. Please configure vehicles and calculate TCO.")
        st.button(
            "Go to Configuration",
            on_click=set_step,
            args=("config",)
        )


def render_export_step():
    """
    Render the export step.
    """
    st.header("Export & Share")
    
    # Check if results are available
    if "results" in st.session_state and st.session_state.results is not None:
        results = st.session_state.results
        comparison = st.session_state.get("comparison")
        
        if results and comparison:
            # Show export options
            render_export_options(results, comparison)
        else:
            st.warning("Results data is incomplete. Please recalculate TCO.")
            st.button(
                "Go to Configuration",
                on_click=set_step,
                args=("config",)
            )
    else:
        st.info("No results available to export. Please calculate TCO first.")
        st.button(
            "Go to Configuration",
            on_click=set_step,
            args=("config",)
        )


def render_export_options(results, comparison):
    """
    Render export options for TCO results.
    
    Args:
        results: Dictionary of TCO result objects
        comparison: Comparison result object
    """
    # TODO: Implement export functionality in Phase 4
    st.info("Export functionality will be implemented in future updates.")
    
    # Placeholder for export options
    export_type = st.radio(
        "Select Export Format",
        options=["Excel", "PDF", "CSV", "JSON"],
        horizontal=True
    )
    
    st.button("Generate Export", disabled=True)


def render_guide_step():
    """
    Render the user guide step.
    """
    render_guide()
``` 