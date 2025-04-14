# Refactoring Phase 2: Visual Design System (Continued)

## Implementation Tasks (Continued)

### 3. Sidebar and Theme Components

#### A. Create Sidebar CSS (sidebar.css)

```css
/* ==========================================================================
   Sidebar Components
   ========================================================================== */

/* Sidebar container */
[data-testid="stSidebar"] {
  background-color: var(--bg-primary);
  border-right: 1px solid var(--border-color);
}

[data-testid="stSidebar"] > div:first-child {
  padding: var(--spacing-md);
}

/* Sidebar titles */
[data-testid="stSidebar"] .stMarkdown h1 {
  font-size: var(--font-size-xl);
  margin-bottom: var(--spacing-md);
}

[data-testid="stSidebar"] .stMarkdown h2, 
[data-testid="stSidebar"] .stMarkdown h3 {
  font-size: var(--font-size-md);
  margin-bottom: var(--spacing-sm);
}

/* Sidebar form elements */
[data-testid="stSidebar"] .stTextInput, 
[data-testid="stSidebar"] .stSelectbox, 
[data-testid="stSidebar"] .stSlider,
[data-testid="stSidebar"] .stTextInput {
  margin-bottom: var(--sidebar-item-spacing);
}

[data-testid="stSidebar"] label {
  font-size: var(--sidebar-label-size);
  margin-bottom: 2px;
}

/* Sidebar expandable sections */
[data-testid="stSidebar"] [data-testid="stExpander"] {
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-sm);
  margin-bottom: var(--spacing-md);
}

[data-testid="stSidebar"] .streamlit-expanderHeader {
  padding: var(--spacing-xs) var(--spacing-sm);
  font-size: 0.95rem;
  background-color: var(--bg-secondary);
}

[data-testid="stSidebar"] .streamlit-expanderContent {
  padding: var(--spacing-sm);
}

/* Vehicle selector in sidebar */
.sidebar-vehicle-selector {
  display: flex;
  align-items: center;
  border-radius: var(--border-radius-md);
  padding: var(--spacing-xs) var(--spacing-sm);
  margin-bottom: var(--spacing-sm);
  background-color: var(--bg-secondary);
  border-left: 4px solid transparent;
}

.sidebar-vehicle-selector.bet {
  border-left-color: var(--bet-primary);
}

.sidebar-vehicle-selector.diesel {
  border-left-color: var(--diesel-primary);
}

.vehicle-selector {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-xs) var(--spacing-sm);
  background-color: var(--bg-secondary);
  border-radius: var(--border-radius-sm);
  margin-bottom: var(--spacing-sm);
  border-left: 4px solid transparent;
}

.vehicle-selector .vehicle-number {
  font-weight: var(--font-weight-semibold);
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
}

.vehicle-selector .vehicle-name {
  font-weight: var(--font-weight-medium);
  font-size: var(--font-size-sm);
}

.vehicle-selector.vehicle-battery_electric {
  border-left-color: var(--bet-primary);
}

.vehicle-selector.vehicle-diesel {
  border-left-color: var(--diesel-primary);
}

/* Configuration preview in sidebar */
.config-preview {
  font-size: var(--font-size-xs);
  background-color: var(--bg-tertiary);
  border-radius: var(--border-radius-sm);
  padding: var(--spacing-xs) var(--spacing-sm);
  margin-top: var(--spacing-xs);
  margin-bottom: var(--spacing-sm);
}

.config-preview .preview-title {
  font-weight: var(--font-weight-medium);
  margin-bottom: var(--spacing-xs);
  color: var(--text-secondary);
}

.config-preview .preview-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 2px;
}

.config-preview .preview-label {
  color: var(--text-secondary);
}

.config-preview .preview-value {
  font-weight: var(--font-weight-medium);
}

/* Calculation status indicator */
.calculation-status {
  display: inline-flex;
  align-items: center;
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--border-radius-sm);
  font-size: var(--font-size-xs);
  margin-top: var(--spacing-xs);
}

.calculation-status.calculating {
  background-color: rgba(var(--warning-color-rgb), 0.1);
  color: var(--warning-color);
}

.calculation-status.done {
  background-color: rgba(var(--success-color-rgb), 0.1);
  color: var(--success-color);
}

.last-calculation-time {
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
  text-align: center;
  margin-top: var(--spacing-xs);
}

/* Theme preview */
.theme-preview {
  width: 100%;
  height: 80px;
  border-radius: var(--border-radius-sm);
  margin-bottom: var(--spacing-md);
  padding: var(--spacing-sm);
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
}

.theme-preview .preview-header {
  font-size: var(--font-size-xs);
  margin-bottom: var(--spacing-xs);
}

.theme-preview .preview-chart {
  height: 30px;
  margin-bottom: var(--spacing-xs);
  background: linear-gradient(90deg, var(--bet-primary) 0%, var(--diesel-primary) 100%);
  border-radius: var(--border-radius-sm);
}

.theme-preview .preview-text {
  font-size: var(--font-size-xs);
}

.theme-preview.theme-light {
  background-color: #ffffff;
  color: #333333;
  border: 1px solid #dddddd;
}

.theme-preview.theme-dark {
  background-color: #1e1e1e;
  color: #f1f1f1;
  border: 1px solid #444444;
}

.theme-preview.theme-high-contrast {
  background-color: #000000;
  color: #ffffff;
  border: 1px solid #777777;
}

/* Toggle group */
.toggle-group {
  display: flex;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-md);
}

/* Chart preview */
.chart-preview {
  width: 100%;
  background-color: var(--bg-secondary);
  border-radius: var(--border-radius-sm);
  margin-top: var(--spacing-sm);
  position: relative;
  overflow: hidden;
}

.chart-grid {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: linear-gradient(var(--chart-grid-color) 1px, transparent 1px),
                    linear-gradient(90deg, var(--chart-grid-color) 1px, transparent 1px);
  background-size: 20px 20px;
}

.chart-breakeven {
  position: absolute;
  top: 0;
  left: 50%;
  height: 100%;
  width: 2px;
  background-color: var(--success-color);
}

.chart-annotations {
  position: absolute;
  top: 10px;
  left: 10px;
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
}

.chart-annotations::before {
  content: 'Annotations';
}
```

#### B. Create Light Theme CSS (light-theme.css)

```css
/* ==========================================================================
   Light Theme
   ========================================================================== */

:root {
  /* Base theme colors */
  --bg-primary: #ffffff;
  --bg-secondary: #f5f5f5;
  --bg-tertiary: #eaeaea;
  --text-primary: #333333;
  --text-secondary: #666666;
  --border-color: #dddddd;
  --divider-color: #eeeeee;
  
  /* Light theme specific RGB values for opacity usage */
  --bet-primary-rgb: 38, 166, 154;
  --diesel-primary-rgb: 251, 140, 0;
  --error-color-rgb: 214, 39, 40;
  --warning-color-rgb: 255, 127, 14;
  --success-color-rgb: 44, 160, 44;
  
  /* UI element colors */
  --card-bg: #ffffff;
  --card-border: #dddddd;
  --card-shadow: rgba(0, 0, 0, 0.05);
  --input-bg: #ffffff;
  --input-border: #cccccc;
  --input-focus-border: #26A69A;
  --input-placeholder: #999999;
  
  /* Chart colors */
  --chart-grid-color: rgba(0, 0, 0, 0.1);
  --chart-axis-color: rgba(0, 0, 0, 0.5);
  --chart-tooltip-bg: rgba(255, 255, 255, 0.95);
}

/* Light theme specific adjustments */
.stApp {
  background-color: var(--bg-primary);
}

.sidebar .stButton > button {
  background-color: var(--bet-primary);
  color: white;
}

.stTabs [aria-selected="true"] {
  background-color: var(--bet-primary);
  color: white;
}

/* Table striping for better readability */
.table-striped tr:nth-child(even) td {
  background-color: var(--bg-secondary);
}
```

#### C. Create Dark Theme CSS (dark-theme.css)

```css
/* ==========================================================================
   Dark Theme
   ========================================================================== */

:root {
  /* Base theme colors */
  --bg-primary: #1e1e1e;
  --bg-secondary: #2d2d2d;
  --bg-tertiary: #3a3a3a;
  --text-primary: #f1f1f1;
  --text-secondary: #cccccc;
  --border-color: #444444;
  --divider-color: #444444;
  
  /* Dark theme specific RGB values for opacity usage */
  --bet-primary-rgb: 38, 166, 154;
  --diesel-primary-rgb: 251, 140, 0;
  --error-color-rgb: 214, 39, 40;
  --warning-color-rgb: 255, 127, 14;
  --success-color-rgb: 44, 160, 44;
  
  /* Adjusted component colors for better visibility on dark backgrounds */
  --acquisition-color: #3498db;
  --energy-color: #ff9f43;
  --maintenance-color: #2ecc71;
  --infrastructure-color: #e74c3c;
  --battery-color: #a569bd;
  --insurance-color: #af7ac5;
  --taxes-color: #f5b7ce;
  --residual-color: #a4b0be;
  
  /* UI element colors */
  --card-bg: #252525;
  --card-border: #444444;
  --card-shadow: rgba(0, 0, 0, 0.3);
  --input-bg: #2d2d2d;
  --input-border: #555555;
  --input-focus-border: #26A69A;
  --input-placeholder: #888888;
  
  /* Chart colors */
  --chart-grid-color: rgba(255, 255, 255, 0.1);
  --chart-axis-color: rgba(255, 255, 255, 0.5);
  --chart-tooltip-bg: rgba(45, 45, 45, 0.95);
}

/* Dark theme specific adjustments */
.stApp {
  background-color: var(--bg-primary);
  color: var(--text-primary);
}

[data-testid="stSidebar"] {
  background-color: var(--bg-primary);
  border-right-color: var(--border-color);
}

.stTextInput input,
.stNumberInput input,
.stDateInput input {
  background-color: var(--input-bg);
  color: var(--text-primary);
  border-color: var(--input-border);
}

.stTextInput input:focus,
.stNumberInput input:focus,
.stDateInput input:focus {
  border-color: var(--input-focus-border);
}

.stSelectbox > div[data-baseweb="select"] > div {
  background-color: var(--input-bg);
  color: var(--text-primary);
  border-color: var(--input-border);
}

.stTabs [data-baseweb="tab-list"] {
  background-color: var(--bg-secondary);
}

.stTabs [data-baseweb="tab"] {
  color: var(--text-primary);
}

/* Card styling for dark theme */
.card {
  background-color: var(--card-bg);
  border-color: var(--card-border);
}

/* Improve contrast for metric cards */
.metric-card {
  background-color: var(--bg-secondary);
}

.metric-insight {
  background-color: var(--bg-primary);
}

/* Table adjustments */
table th {
  background-color: var(--bg-tertiary);
  color: var(--text-primary);
}

table td {
  border-color: var(--divider-color);
}

/* Chart preview */
.chart-grid {
  background-image: linear-gradient(var(--chart-grid-color) 1px, transparent 1px),
                    linear-gradient(90deg, var(--chart-grid-color) 1px, transparent 1px);
}
```

#### D. Create High Contrast Theme CSS (high-contrast.css)

```css
/* ==========================================================================
   High Contrast Theme for Accessibility
   ========================================================================== */

:root {
  /* Base theme colors - high contrast for accessibility */
  --bg-primary: #000000;
  --bg-secondary: #1a1a1a;
  --bg-tertiary: #2a2a2a;
  --text-primary: #ffffff;
  --text-secondary: #eeeeee;
  --border-color: #ffffff;
  --divider-color: #555555;
  
  /* High contrast specific RGB values for opacity usage */
  --bet-primary-rgb: 0, 230, 200;
  --diesel-primary-rgb: 255, 170, 0;
  --error-color-rgb: 255, 80, 80;
  --warning-color-rgb: 255, 190, 0;
  --success-color-rgb: 50, 220, 50;
  
  /* Adjusted component colors for better contrast */
  --acquisition-color: #0099ff;
  --energy-color: #ffaa00;
  --maintenance-color: #00cc00;
  --infrastructure-color: #ff5050;
  --battery-color: #cc66ff;
  --insurance-color: #ff66cc;
  --taxes-color: #ff99cc;
  --residual-color: #bbbbbb;
  
  /* Vehicle type colors with higher contrast */
  --bet-primary: #00E6C8;
  --diesel-primary: #FFAA00;
  
  /* Australian-themed accents with higher contrast */
  --aus-green: #00FF77;
  --aus-gold: #FFD700;
  
  /* Status colors with higher contrast */
  --success-color: #32DC32;
  --warning-color: #FFBE00;
  --error-color: #FF5050;
  --info-color: #0099FF;
  
  /* UI element colors */
  --card-bg: #1a1a1a;
  --card-border: #ffffff;
  --card-shadow: rgba(255, 255, 255, 0.2);
  --input-bg: #1a1a1a;
  --input-border: #ffffff;
  --input-focus-border: #00E6C8;
  --input-placeholder: #bbbbbb;
  
  /* Chart colors */
  --chart-grid-color: rgba(255, 255, 255, 0.3);
  --chart-axis-color: rgba(255, 255, 255, 0.8);
  --chart-tooltip-bg: rgba(0, 0, 0, 0.9);
}

/* High contrast theme specific adjustments */
body, .stApp {
  background-color: var(--bg-primary);
  color: var(--text-primary);
}

/* Thicker borders for better visibility */
.card, 
[data-testid="stExpander"], 
.stTextInput input,
.stNumberInput input,
.stDateInput input,
.stSelectbox > div[data-baseweb="select"] > div {
  border-width: 2px;
}

/* Higher contrast focus states */
.stTextInput input:focus,
.stNumberInput input:focus,
.stDateInput input:focus,
.stSelectbox > div[data-baseweb="select"] > div:focus,
.stButton > button:focus {
  outline: 2px solid var(--bet-primary);
  box-shadow: 0 0 0 4px rgba(var(--bet-primary-rgb), 0.4);
}

/* Buttons with higher contrast */
.stButton > button {
  background-color: var(--bet-primary);
  color: var(--bg-primary);
  font-weight: var(--font-weight-bold);
}

.stButton > button:hover {
  background-color: var(--text-primary);
  color: var(--bg-primary);
}

/* Form elements */
.stCheckbox label span[role="checkbox"],
.stRadio label span[role="radio"] {
  border-color: var(--text-primary);
  border-width: 2px;
}

.stCheckbox label span[role="checkbox"][data-checked="true"],
.stRadio label span[role="radio"][data-checked="true"] {
  background-color: var(--bet-primary);
  border-color: var(--bet-primary);
}

/* Improved contrast for tabs */
.stTabs [data-baseweb="tab-list"] {
  background-color: var(--bg-secondary);
  border: 2px solid var(--border-color);
}

.stTabs [data-baseweb="tab"] {
  color: var(--text-primary);
}

.stTabs [aria-selected="true"] {
  background-color: var(--bet-primary);
  color: var(--bg-primary) !important;
  font-weight: var(--font-weight-bold);
}

/* Tables with better contrast */
table th {
  background-color: var(--bg-tertiary);
  color: var(--text-primary);
  border: 2px solid var(--border-color);
}

table td {
  border: 1px solid var(--divider-color);
}

/* More pronounced impact indicators */
.impact-indicator.high {
  background-color: var(--error-color);
  color: var(--bg-primary);
}

.impact-indicator.medium {
  background-color: var(--warning-color);
  color: var(--bg-primary);
}

.impact-indicator.low {
  background-color: var(--success-color);
  color: var(--bg-primary);
}
```

#### E. Create Main CSS File (main.css)

```css
/* ==========================================================================
   Main CSS Entry Point
   ========================================================================== */

/* Import base styles */
@import url('base/reset.css');
@import url('base/typography.css');
@import url('base/variables.css');
@import url('base/layout.css');

/* Import component styles */
@import url('components/cards.css');
@import url('components/forms.css');
@import url('components/navigation.css');
@import url('components/metrics.css');
@import url('components/sidebar.css');
@import url('components/tables.css');

/* 
Theme is imported dynamically based on user selection.
The appropriate theme file is included via the load_css function.
*/

/* Global utility classes */
.text-center { text-align: center; }
.text-right { text-align: right; }
.text-left { text-align: left; }

.font-bold { font-weight: var(--font-weight-bold); }
.font-medium { font-weight: var(--font-weight-medium); }
.font-normal { font-weight: var(--font-weight-normal); }

.w-full { width: 100%; }
.h-full { height: 100%; }

.rounded { border-radius: var(--border-radius-sm); }
.rounded-md { border-radius: var(--border-radius-md); }
.rounded-lg { border-radius: var(--border-radius-lg); }
.rounded-full { border-radius: var(--border-radius-full); }

.shadow { box-shadow: var(--shadow-sm); }
.shadow-md { box-shadow: var(--shadow-md); }
.shadow-lg { box-shadow: var(--shadow-lg); }

/* Australian-specific branding elements */
.aus-branding {
  border-left: 4px solid var(--aus-green);
  border-right: 4px solid var(--aus-gold);
}

.aus-accent-top {
  position: relative;
}

.aus-accent-top::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(to right, var(--aus-green) 0%, var(--aus-gold) 100%);
}

/* Australian flag colors */
.aus-flag-blue { background-color: #00008B; }
.aus-flag-red { background-color: #FF0000; }
.aus-flag-white { background-color: #FFFFFF; }
```

### 4. Implement CSS Loading Functionality

Create a new file `utils/css_loader.py` for loading and injecting CSS:

```python
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
        css_dir / "components" / "tables.css"
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
```

### 5. Update App Startup to Load CSS

Update `app.py` to load the CSS at startup by adding the following changes:

```python
# Import CSS loader
from utils.css_loader import load_css

def main():
    """Main application entry point."""
    # Page configuration
    st.set_page_config(
        page_title="Australian Heavy Vehicle TCO Modeller",
        page_icon="🚚",
        layout="wide",
    )
    
    # Initialize session state
    initialize_session_state()
    
    # Get selected theme from session state or default to light
    selected_theme = st.session_state.get("ui_theme", "light")
    
    # Load CSS with theme
    load_css(selected_theme)
    
    # Render the application title
    st.title("Australian Heavy Vehicle TCO Modeller")
    st.markdown("Compare the Total Cost of Ownership for different heavy vehicle types.")
    
    # Render sidebar
    render_sidebar()
    
    # ... rest of the function remains unchanged
```

## Integration Steps

To implement Phase 2, follow these steps in order:

1. Create the directory structure for CSS files as outlined in this document
2. Create all the CSS files according to the provided code snippets
3. Create the CSS loader utility module
4. Update `app.py` to load the CSS at startup
5. Update sidebar component to include theme selection if desired
6. Test the application with different themes to ensure proper styling

## Validation

After implementing Phase 2, verify the following:

1. The application has a consistent visual design with proper spacing, colors, and typography
2. The light, dark, and high-contrast themes can be switched correctly
3. Form elements, cards, and other UI components have the proper styling
4. The sidebar displays correctly with improved styling
5. The application is responsive and works well on different screen sizes
6. Australian-themed colors and accents are applied appropriately

## Next Steps

After completing Phase 2, proceed to Phase 3, which will implement improved navigation and structure for the application. 