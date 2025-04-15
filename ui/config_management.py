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
        
        # Sanitise the name for use in a filename
        safe_name = name.replace(" ", "_").lower()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{safe_name}_{timestamp}.json"
        
        # Create separate directories for each vehicle type
        config_dir = get_config_directory()
        type_dir = config_dir / vehicle_type
        type_dir.mkdir(exist_ok=True)
        
        # Full path to the saved config file
        config_path = type_dir / filename
        
        # Convert the model to a dictionary for serialisation
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


def render_configuration_management():
    """
    Redirects to render_config_management for compatibility with UI module imports.
    """
    return render_config_management()


def save_navigation_state(session_id: str, navigation_state: Any) -> bool:
    """
    Save navigation state for a session.
    
    Args:
        session_id: Session identifier
        navigation_state: Navigation state object
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Get the directory for saved navigation states
        config_dir = get_config_directory()
        nav_dir = config_dir / "navigation"
        nav_dir.mkdir(exist_ok=True)
        
        # Create a file for the session
        nav_path = nav_dir / f"{session_id}.json"
        
        # Convert navigation state to a dictionary
        nav_data = {
            "current_step": navigation_state.current_step,
            "completed_steps": navigation_state.completed_steps,
            "breadcrumb_history": navigation_state.breadcrumb_history,
            "can_proceed": navigation_state.can_proceed,
            "can_go_back": navigation_state.can_go_back,
            "next_step": navigation_state.next_step,
            "previous_step": navigation_state.previous_step
        }
        
        # Save to file
        with open(nav_path, "w") as f:
            json.dump(nav_data, f, indent=2)
        
        return True
        
    except Exception as e:
        if hasattr(st, "error"):
            st.error(f"Error saving navigation state: {str(e)}")
        return False


def load_navigation_state(session_id: str) -> Optional[Any]:
    """
    Load navigation state for a session.
    
    Args:
        session_id: Session identifier
        
    Returns:
        Navigation state object or None if not found
    """
    try:
        # Get the directory for saved navigation states
        config_dir = get_config_directory()
        nav_dir = config_dir / "navigation"
        
        # Check if navigation directory exists
        if not nav_dir.exists():
            return None
        
        # Path to the session file
        nav_path = nav_dir / f"{session_id}.json"
        
        # Check if session file exists
        if not nav_path.exists():
            return None
        
        # Load from file
        with open(nav_path, "r") as f:
            nav_data = json.load(f)
        
        # Create a NavigationState object
        from tests.conftest import NavigationState
        navigation_state = NavigationState(
            current_step=nav_data.get("current_step"),
            completed_steps=nav_data.get("completed_steps", []),
            breadcrumb_history=nav_data.get("breadcrumb_history", []),
            can_proceed=nav_data.get("can_proceed", True),
            can_go_back=nav_data.get("can_go_back", False),
            next_step=nav_data.get("next_step"),
            previous_step=nav_data.get("previous_step")
        )
        
        return navigation_state
        
    except Exception as e:
        if hasattr(st, "error"):
            st.error(f"Error loading navigation state: {str(e)}")
        return None


def save_scenario(session_id: str, vehicle_key: str, scenario: ScenarioInput) -> bool:
    """
    Save a scenario to the session state.
    
    Args:
        session_id: Session identifier
        vehicle_key: Vehicle key (e.g. "vehicle_1" or "vehicle_2")
        scenario: Scenario input object
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Update the session state
        st.session_state[vehicle_key] = scenario
        
        # Update nested state for UI components to reference
        update_state_from_model(vehicle_key, scenario)
        
        return True
        
    except Exception as e:
        if hasattr(st, "error"):
            st.error(f"Error saving scenario: {str(e)}")
        return False


def load_scenario(session_id: str, vehicle_key: str) -> Optional[ScenarioInput]:
    """
    Load a scenario from the session state.
    
    Args:
        session_id: Session identifier
        vehicle_key: Vehicle key (e.g. "vehicle_1" or "vehicle_2")
        
    Returns:
        Scenario input object or None if not found
    """
    try:
        # Get from session state
        if vehicle_key not in st.session_state:
            return None
        
        return st.session_state[vehicle_key]
        
    except Exception as e:
        if hasattr(st, "error"):
            st.error(f"Error loading scenario: {str(e)}")
        return None


def save_results(session_id: str, results: Dict[str, Any], comparison: Any) -> bool:
    """
    Save results to the session state.
    
    Args:
        session_id: Session identifier
        results: Dictionary of TCO results
        comparison: Comparison result object
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Create a results key using the session_id
        results_key = f"results_{session_id}"
        comparison_key = f"comparison_{session_id}"
        
        # Save to session state
        st.session_state[results_key] = results
        st.session_state[comparison_key] = comparison
        st.session_state["show_results"] = True
        
        # Also save to the original keys for backward compatibility
        st.session_state["results"] = results
        st.session_state["comparison"] = comparison
        
        return True
        
    except Exception as e:
        if hasattr(st, "error"):
            st.error(f"Error saving results: {str(e)}")
        return False


def load_results(session_id: str) -> Tuple[Optional[Dict[str, Any]], Optional[Any]]:
    """
    Load results from the session state.
    
    Args:
        session_id: Session identifier
    
    Returns:
        Tuple of (results, comparison) or (None, None) if not found
    """
    try:
        # Create keys using the session_id
        results_key = f"results_{session_id}"
        comparison_key = f"comparison_{session_id}"
        
        # Get from session state
        results = st.session_state.get(results_key)
        comparison = st.session_state.get(comparison_key)
        
        return results, comparison
        
    except Exception as e:
        if hasattr(st, "error"):
            st.error(f"Error loading results: {str(e)}")
        return None, None 