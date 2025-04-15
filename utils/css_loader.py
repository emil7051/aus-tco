"""
CSS Loader Utility Module

This module provides functions for loading and injecting CSS into the Streamlit
application, supporting theme switching and dynamic styling.
"""

import streamlit as st
import os
from pathlib import Path
from typing import List, Optional, Union, Dict

def get_css_dir() -> Path:
    """
    Get the path to the CSS directory.
    
    Returns:
        Path object to the CSS directory
    """
    # Get the directory of this file
    current_dir = Path(__file__).parent
    
    # Navigate to static/css directory
    # Assuming the structure is: repo_root/utils/css_loader.py
    # and CSS files are in: repo_root/static/css/
    return current_dir.parent / "static" / "css"

def load_css(theme: str = "light") -> None:
    """
    Load the application CSS with theme support.
    
    Args:
        theme: Theme name ('light', 'dark', or 'high-contrast')
    """
    # Get CSS directory path
    css_dir = get_css_dir()
    
    # Define the paths to CSS files
    base_files = [
        css_dir / "base" / "reset.css",
        css_dir / "base" / "variables.css",
        css_dir / "base" / "typography.css",
        css_dir / "base" / "layout.css"
    ]
    
    component_files = [
        css_dir / "components" / "cards.css",
        css_dir / "components" / "forms.css",
        css_dir / "components" / "navigation.css",
        css_dir / "components" / "metrics.css",
        css_dir / "components" / "sidebar.css",
        css_dir / "components" / "tables.css",
        css_dir / "components" / "parameter_indicators.css"
    ]
    
    # Theme-specific overrides
    theme_file = css_dir / "themes" / f"{theme}-theme.css"
    
    # Combine all CSS into a single string
    css_content = ""
    
    # Function to safely read CSS file
    def read_css_file(file_path: Path) -> str:
        if file_path.exists():
            with open(file_path, "r") as f:
                return f.read() + "\n"
        else:
            st.warning(f"CSS file not found: {file_path}")
            return ""
    
    # Add base files first
    for file_path in base_files:
        css_content += read_css_file(file_path)
    
    # Add component files
    for file_path in component_files:
        css_content += read_css_file(file_path)
    
    # Add theme-specific overrides last
    css_content += read_css_file(theme_file)
    
    # Inject the CSS into the Streamlit app
    st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)

def load_css_resources() -> str:
    """
    Load CSS resources for testing purposes.
    
    This is similar to load_css but returns the CSS as a string instead
    of injecting it into Streamlit.
    
    Returns:
        All CSS content as a single string
    """
    # Get CSS directory path
    css_dir = get_css_dir()
    
    # Define the paths to CSS files (same as in load_css)
    base_files = [
        css_dir / "base" / "reset.css",
        css_dir / "base" / "variables.css",
        css_dir / "base" / "typography.css",
        css_dir / "base" / "layout.css"
    ]
    
    component_files = [
        css_dir / "components" / "cards.css",
        css_dir / "components" / "forms.css",
        css_dir / "components" / "navigation.css",
        css_dir / "components" / "metrics.css",
        css_dir / "components" / "sidebar.css",
        css_dir / "components" / "tables.css",
        css_dir / "components" / "parameter_indicators.css"
    ]
    
    # Theme-specific overrides (use light theme as default)
    theme_file = css_dir / "themes" / "light-theme.css"
    
    # Combine all CSS into a single string
    css_content = ""
    
    # Function to safely read CSS file (same as in load_css)
    def read_css_file(file_path: Path) -> str:
        if file_path.exists():
            with open(file_path, "r") as f:
                return f.read() + "\n"
        else:
            return f"/* CSS file not found: {file_path} */\n"
    
    # Add base files first
    for file_path in base_files:
        css_content += read_css_file(file_path)
    
    # Add component files
    for file_path in component_files:
        css_content += read_css_file(file_path)
    
    # Add theme-specific overrides last
    css_content += read_css_file(theme_file)
    
    return css_content

def get_css_class(base_class: str, modifier: Optional[str] = None) -> str:
    """
    Get CSS class names following BEM naming convention.
    
    Args:
        base_class: The base class name
        modifier: Optional modifier for the class
        
    Returns:
        The complete class name string
    """
    if modifier:
        return f"{base_class} {base_class}--{modifier}"
    return base_class

def load_single_css_file(file_name: str) -> None:
    """
    Load a single CSS file and inject it into the Streamlit app.
    
    Args:
        file_name: The name of the CSS file to load (without directory)
    """
    css_dir = get_css_dir()
    file_path = None
    
    # Check if file exists in base directory
    if (css_dir / file_name).exists():
        file_path = css_dir / file_name
    # Check in base subdirectory
    elif (css_dir / "base" / file_name).exists():
        file_path = css_dir / "base" / file_name
    # Check in components subdirectory
    elif (css_dir / "components" / file_name).exists():
        file_path = css_dir / "components" / file_name
    # Check in themes subdirectory
    elif (css_dir / "themes" / file_name).exists():
        file_path = css_dir / "themes" / file_name
    
    if file_path and file_path.exists():
        with open(file_path, "r") as f:
            css_content = f.read()
            st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
    else:
        st.warning(f"CSS file not found: {file_name}")

def get_available_themes() -> List[str]:
    """
    Get a list of available themes.
    
    Returns:
        List of theme names
    """
    css_dir = get_css_dir()
    themes_dir = css_dir / "themes"
    
    if not themes_dir.exists():
        return ["light"]  # Default fallback
    
    # Find all CSS files in the themes directory
    theme_files = [f.stem.replace("-theme", "") 
                  for f in themes_dir.glob("*-theme.css")]
    
    # Ensure at least the light theme is available
    if not theme_files:
        return ["light"]
        
    return theme_files 