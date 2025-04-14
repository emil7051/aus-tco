# Refactoring Phase 2 Part 1: Base CSS Architecture and Variables

This document outlines the first part of Phase 2 of the UI refactoring process for the Australian Heavy Vehicle TCO Modeller, focusing on implementing the foundational CSS architecture and variable system.

## Scope of Part 1

Part 1 of Phase 2 focuses specifically on:
1. Creating the core CSS file structure (following the directory structure from Phase 1)
2. Implementing the essential base CSS files:
   - CSS reset
   - Typography system
   - CSS variables
   - Layout utilities

This part provides the foundation for all subsequent CSS components in Parts 2 and 3.

## Prerequisites

- Phase 1 (Terminology Standardization and UI Utilities) must be completed
- The directory structure `/static/css/{base,components,themes}` should already exist

## Implementation Tasks

### 1. Create CSS File Structure

Using the directory structure created in Phase 1, create the following files:

```
/static
  /css
    /base
      reset.css            # CSS reset and normalization
      typography.css       # Typography definitions
      variables.css        # CSS variables including component colours
      layout.css           # Layout structures
    main.css               # Main CSS file importing others
```

### 2. Create Main CSS File (main.css)

Create a main CSS file that will import all other CSS files:

```css
/* ==========================================================================
   Australian Heavy Vehicle TCO Modeller - Main CSS File
   ========================================================================== */

/* Base styles */
@import url('./base/reset.css');
@import url('./base/variables.css');
@import url('./base/typography.css');
@import url('./base/layout.css');

/* This file will later import component and theme CSS files */
```

### 3. Create CSS Reset File (reset.css)

```css
/* ==========================================================================
   Reset and base styles
   ========================================================================== */

/* Box sizing rules */
*,
*::before,
*::after {
  box-sizing: border-box;
}

/* Remove default margin and padding */
body,
h1,
h2,
h3,
h4,
h5,
h6,
p,
ul,
ol,
li,
figure,
figcaption,
blockquote,
dl,
dd {
  margin: 0;
  padding: 0;
}

/* Set core body defaults */
body {
  min-height: 100vh;
  scroll-behavior: smooth;
  text-rendering: optimizeSpeed;
  line-height: 1.5;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen-Sans, Ubuntu, Cantarell, "Helvetica Neue", sans-serif;
}

/* Remove list styles */
ul,
ol {
  list-style: none;
}

/* Make images easier to work with */
img {
  max-width: 100%;
  display: block;
}

/* Inherit fonts for inputs and buttons */
input,
button,
textarea,
select {
  font: inherit;
}

/* Remove all animations and transitions for people that prefer not to see them */
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}

/* Streamlit-specific overrides */
.stApp {
  background-color: var(--bg-primary, #ffffff);
  color: var(--text-primary, #333333);
}

.stMarkdown, .stText {
  color: var(--text-primary, #333333);
}

/* Hide development menu by default */
#MainMenu {
  visibility: hidden;
}

/* Adjust header spacing */
header {
  background-color: var(--bg-primary, #ffffff);
}

/* Style scrollbars for better visual consistency */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: var(--bg-secondary, #f5f5f5);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: var(--border-color, #dddddd);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #c1c1c1;
}
```

### 4. Create Variables CSS File (variables.css)

Implement CSS variables that align with the terminology definitions from Phase 1:

```css
/* ==========================================================================
   CSS Variables - defining global design tokens
   ========================================================================== */

:root {
  /* Component colors - aligned with UI_COMPONENT_MAPPING from terminology.py */
  --acquisition-color: #1f77b4;
  --energy-color: #ff7f0e;
  --maintenance-color: #2ca02c;
  --infrastructure-color: #d62728;
  --battery-color: #9467bd;
  --insurance-color: #8c564b;
  --taxes-color: #e377c2;
  --residual-color: #7f7f7f;
  
  /* Vehicle type colors */
  --bet-primary: #26A69A;
  --diesel-primary: #FB8C00;
  
  /* Australian-themed accents */
  --aus-green: #00843D;
  --aus-gold: #FFCD00;
  
  /* Base theme colors - will be overridden by theme CSS files */
  --bg-primary: #ffffff;
  --bg-secondary: #f5f5f5;
  --bg-tertiary: #eaeaea;
  --text-primary: #333333;
  --text-secondary: #666666;
  --border-color: #dddddd;
  --divider-color: #eeeeee;
  
  /* UI element colors */
  --card-bg: #ffffff;
  --card-border: #dddddd;
  --card-shadow: rgba(0, 0, 0, 0.05);
  --input-bg: #ffffff;
  --input-border: #cccccc;
  --input-focus-border: #26A69A;
  --input-placeholder: #999999;

  /* Status and feedback colors */
  --success-color: #2ca02c;
  --warning-color: #ff7f0e;
  --error-color: #d62728;
  --info-color: #1f77b4;
  
  /* Spacing variables */
  --spacing-xs: 0.25rem;   /* 4px */
  --spacing-sm: 0.5rem;    /* 8px */
  --spacing-md: 1rem;      /* 16px */
  --spacing-lg: 1.5rem;    /* 24px */
  --spacing-xl: 2rem;      /* 32px */
  --spacing-2xl: 2.5rem;   /* 40px */
  --spacing-3xl: 3rem;     /* 48px */
  
  /* Border radius */
  --border-radius-sm: 4px;
  --border-radius-md: 8px;
  --border-radius-lg: 12px;
  --border-radius-full: 9999px;
  
  /* Shadows */
  --shadow-sm: 0 1px 3px rgba(0,0,0,0.1);
  --shadow-md: 0 2px 5px rgba(0,0,0,0.1);
  --shadow-lg: 0 4px 8px rgba(0,0,0,0.15);
  --shadow-inset: inset 0 2px 4px rgba(0,0,0,0.05);
  
  /* Transitions */
  --transition-fast: 150ms ease;
  --transition-normal: 300ms ease;
  --transition-slow: 500ms ease;
  
  /* Z-index layers */
  --z-index-dropdown: 1000;
  --z-index-sticky: 1020;
  --z-index-fixed: 1030;
  --z-index-modal-backdrop: 1040;
  --z-index-modal: 1050;
  --z-index-tooltip: 1060;
  
  /* Sidebar specific */
  --sidebar-width: 330px;
  --sidebar-item-spacing: 0.5rem;
  --sidebar-label-size: 0.85rem;
  --sidebar-value-size: 0.9rem;
  
  /* Chart colors */
  --chart-grid-color: rgba(0, 0, 0, 0.1);
  --chart-axis-color: rgba(0, 0, 0, 0.5);
  --chart-tooltip-bg: rgba(255, 255, 255, 0.95);
}

/* Utility color classes */
.color-acquisition { color: var(--acquisition-color); }
.color-energy { color: var(--energy-color); }
.color-maintenance { color: var(--maintenance-color); }
.color-infrastructure { color: var(--infrastructure-color); }
.color-battery { color: var(--battery-color); }
.color-insurance { color: var(--insurance-color); }
.color-taxes { color: var(--taxes-color); }
.color-residual { color: var(--residual-color); }

.color-bet { color: var(--bet-primary); }
.color-diesel { color: var(--diesel-primary); }

.color-success { color: var(--success-color); }
.color-warning { color: var(--warning-color); }
.color-error { color: var(--error-color); }
.color-info { color: var(--info-color); }

/* Background color utilities */
.bg-acquisition { background-color: var(--acquisition-color); }
.bg-energy { background-color: var(--energy-color); }
.bg-maintenance { background-color: var(--maintenance-color); }
.bg-infrastructure { background-color: var(--infrastructure-color); }
.bg-battery { background-color: var(--battery-color); }
.bg-insurance { background-color: var(--insurance-color); }
.bg-taxes { background-color: var(--taxes-color); }
.bg-residual { background-color: var(--residual-color); }

.bg-bet { background-color: var(--bet-primary); }
.bg-diesel { background-color: var(--diesel-primary); }

.bg-primary { background-color: var(--bg-primary); }
.bg-secondary { background-color: var(--bg-secondary); }
.bg-tertiary { background-color: var(--bg-tertiary); }
```

### 5. Create Typography CSS File (typography.css)

```css
/* ==========================================================================
   Typography styles
   ========================================================================== */

/* Base typography variables */
:root {
  --font-primary: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen-Sans, Ubuntu, Cantarell, "Helvetica Neue", sans-serif;
  --font-monospace: SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
  
  --font-size-xs: 0.75rem;   /* 12px */
  --font-size-sm: 0.875rem;  /* 14px */
  --font-size-base: 1rem;    /* 16px */
  --font-size-md: 1.125rem;  /* 18px */
  --font-size-lg: 1.25rem;   /* 20px */
  --font-size-xl: 1.5rem;    /* 24px */
  --font-size-2xl: 1.875rem; /* 30px */
  --font-size-3xl: 2.25rem;  /* 36px */
  
  --line-height-tight: 1.25;
  --line-height-normal: 1.5;
  --line-height-relaxed: 1.75;
  
  --font-weight-light: 300;
  --font-weight-normal: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;
}

/* Base elements */
body {
  font-family: var(--font-primary);
  font-size: var(--font-size-base);
  line-height: var(--line-height-normal);
  color: var(--text-primary);
}

/* Headings */
h1, h2, h3, h4, h5, h6 {
  margin-bottom: 0.5rem;
  font-weight: var(--font-weight-semibold);
  line-height: var(--line-height-tight);
  color: var(--text-primary);
}

h1 {
  font-size: var(--font-size-3xl);
}

h2 {
  font-size: var(--font-size-2xl);
}

h3 {
  font-size: var(--font-size-xl);
}

h4 {
  font-size: var(--font-size-lg);
}

h5 {
  font-size: var(--font-size-md);
}

h6 {
  font-size: var(--font-size-base);
}

/* Paragraphs */
p {
  margin-bottom: 1rem;
}

/* Links */
a {
  color: var(--aus-green);
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}

/* Labels */
label {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  margin-bottom: 0.25rem;
  display: block;
}

/* Code */
code, pre {
  font-family: var(--font-monospace);
  font-size: var(--font-size-sm);
  background-color: var(--bg-secondary);
  border-radius: 4px;
}

code {
  padding: 0.125rem 0.25rem;
}

pre {
  padding: 1rem;
  overflow-x: auto;
  margin-bottom: 1rem;
}

/* Special text treatments */
.text-small {
  font-size: var(--font-size-sm);
}

.text-muted {
  color: var(--text-secondary);
}

.text-bold {
  font-weight: var(--font-weight-bold);
}

.text-center {
  text-align: center;
}

.text-right {
  text-align: right;
}

/* Specialized UI text components */
.metric-label {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--text-secondary);
}

.metric-value {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-bold);
}

.group-label {
  font-size: var(--font-size-md);
  font-weight: var(--font-weight-semibold);
  margin-bottom: 0.5rem;
  color: var(--text-primary);
}

/* Sidebar specific typography */
.sidebar .stMarkdown h1 {
  font-size: var(--font-size-xl);
}

.sidebar .stMarkdown h2, 
.sidebar .stMarkdown h3 {
  font-size: var(--font-size-lg);
}

.sidebar label {
  font-size: var(--font-size-xs);
}

/* Validation message text */
.validation-message {
  font-size: var(--font-size-xs);
  color: var(--error-color);
  margin-top: 0.25rem;
}
```

### 6. Create Layout CSS File (layout.css)

```css
/* ==========================================================================
   Layout styles - base grid system and layout utilities
   ========================================================================== */

/* Grid system */
.grid {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: var(--spacing-md);
}

/* Responsive grid */
.grid-1 { grid-template-columns: 1fr; }
.grid-2 { grid-template-columns: repeat(2, 1fr); }
.grid-3 { grid-template-columns: repeat(3, 1fr); }
.grid-4 { grid-template-columns: repeat(4, 1fr); }

/* Container */
.container {
  width: 100%;
  padding-right: var(--spacing-md);
  padding-left: var(--spacing-md);
  margin-right: auto;
  margin-left: auto;
}

/* Flexbox utilities */
.flex {
  display: flex;
}

.flex-col {
  flex-direction: column;
}

.items-center {
  align-items: center;
}

.justify-center {
  justify-content: center;
}

.justify-between {
  justify-content: space-between;
}

.justify-end {
  justify-content: flex-end;
}

.flex-wrap {
  flex-wrap: wrap;
}

.flex-1 {
  flex: 1;
}

/* Spacing utilities */
.m-0 { margin: 0; }
.mt-0 { margin-top: 0; }
.mr-0 { margin-right: 0; }
.mb-0 { margin-bottom: 0; }
.ml-0 { margin-left: 0; }

.m-xs { margin: var(--spacing-xs); }
.mt-xs { margin-top: var(--spacing-xs); }
.mr-xs { margin-right: var(--spacing-xs); }
.mb-xs { margin-bottom: var(--spacing-xs); }
.ml-xs { margin-left: var(--spacing-xs); }

.m-sm { margin: var(--spacing-sm); }
.mt-sm { margin-top: var(--spacing-sm); }
.mr-sm { margin-right: var(--spacing-sm); }
.mb-sm { margin-bottom: var(--spacing-sm); }
.ml-sm { margin-left: var(--spacing-sm); }

.m-md { margin: var(--spacing-md); }
.mt-md { margin-top: var(--spacing-md); }
.mr-md { margin-right: var(--spacing-md); }
.mb-md { margin-bottom: var(--spacing-md); }
.ml-md { margin-left: var(--spacing-md); }

.m-lg { margin: var(--spacing-lg); }
.mt-lg { margin-top: var(--spacing-lg); }
.mr-lg { margin-right: var(--spacing-lg); }
.mb-lg { margin-bottom: var(--spacing-lg); }
.ml-lg { margin-left: var(--spacing-lg); }

.m-xl { margin: var(--spacing-xl); }
.mt-xl { margin-top: var(--spacing-xl); }
.mr-xl { margin-right: var(--spacing-xl); }
.mb-xl { margin-bottom: var(--spacing-xl); }
.ml-xl { margin-left: var(--spacing-xl); }

.p-0 { padding: 0; }
.pt-0 { padding-top: 0; }
.pr-0 { padding-right: 0; }
.pb-0 { padding-bottom: 0; }
.pl-0 { padding-left: 0; }

.p-xs { padding: var(--spacing-xs); }
.pt-xs { padding-top: var(--spacing-xs); }
.pr-xs { padding-right: var(--spacing-xs); }
.pb-xs { padding-bottom: var(--spacing-xs); }
.pl-xs { padding-left: var(--spacing-xs); }

.p-sm { padding: var(--spacing-sm); }
.pt-sm { padding-top: var(--spacing-sm); }
.pr-sm { padding-right: var(--spacing-sm); }
.pb-sm { padding-bottom: var(--spacing-sm); }
.pl-sm { padding-left: var(--spacing-sm); }

.p-md { padding: var(--spacing-md); }
.pt-md { padding-top: var(--spacing-md); }
.pr-md { padding-right: var(--spacing-md); }
.pb-md { padding-bottom: var(--spacing-md); }
.pl-md { padding-left: var(--spacing-md); }

.p-lg { padding: var(--spacing-lg); }
.pt-lg { padding-top: var(--spacing-lg); }
.pr-lg { padding-right: var(--spacing-lg); }
.pb-lg { padding-bottom: var(--spacing-lg); }
.pl-lg { padding-left: var(--spacing-lg); }

.p-xl { padding: var(--spacing-xl); }
.pt-xl { padding-top: var(--spacing-xl); }
.pr-xl { padding-right: var(--spacing-xl); }
.pb-xl { padding-bottom: var(--spacing-xl); }
.pl-xl { padding-left: var(--spacing-xl); }

/* Display utilities */
.block { display: block; }
.inline-block { display: inline-block; }
.inline { display: inline; }
.hidden { display: none; }

/* Position utilities */
.relative { position: relative; }
.absolute { position: absolute; }
.fixed { position: fixed; }
.sticky { position: sticky; }
.top-0 { top: 0; }
.right-0 { right: 0; }
.bottom-0 { bottom: 0; }
.left-0 { left: 0; }

/* Visibility utilities */
.visible { visibility: visible; }
.invisible { visibility: hidden; }

/* Generic layout components */
.divider {
  height: 1px;
  background-color: var(--divider-color);
  margin: var(--spacing-md) 0;
}

.divider-vertical {
  width: 1px;
  height: 100%;
  background-color: var(--divider-color);
  margin: 0 var(--spacing-md);
}

/* Responsive breakpoints */
@media (min-width: 640px) {
  .sm\:hidden { display: none; }
  .sm\:block { display: block; }
  .sm\:flex { display: flex; }
  .sm\:grid-2 { grid-template-columns: repeat(2, 1fr); }
  .sm\:grid-3 { grid-template-columns: repeat(3, 1fr); }
  .sm\:grid-4 { grid-template-columns: repeat(4, 1fr); }
}

@media (min-width: 768px) {
  .md\:hidden { display: none; }
  .md\:block { display: block; }
  .md\:flex { display: flex; }
  .md\:grid-2 { grid-template-columns: repeat(2, 1fr); }
  .md\:grid-3 { grid-template-columns: repeat(3, 1fr); }
  .md\:grid-4 { grid-template-columns: repeat(4, 1fr); }
}

@media (min-width: 1024px) {
  .lg\:hidden { display: none; }
  .lg\:block { display: block; }
  .lg\:flex { display: flex; }
  .lg\:grid-2 { grid-template-columns: repeat(2, 1fr); }
  .lg\:grid-3 { grid-template-columns: repeat(3, 1fr); }
  .lg\:grid-4 { grid-template-columns: repeat(4, 1fr); }
}

/* Layout adjustments for streamlit */
.stApp > header {
  position: sticky;
  top: 0;
  z-index: var(--z-index-sticky);
}

.main .block-container {
  padding-top: var(--spacing-lg);
  padding-bottom: var(--spacing-xl);
}
```

### 7. Create CSS Loader Utility

Create a new file `utils/css_loader.py` to load the CSS files in Streamlit:

```python
"""
CSS Loader Utility

This module provides functions to load CSS files and apply them to the Streamlit application.
"""

import streamlit as st
import os
from pathlib import Path
from typing import List, Optional


def load_css_file(css_file_path: str) -> str:
    """
    Load a CSS file and return its contents.
    
    Args:
        css_file_path: Path to the CSS file
        
    Returns:
        The CSS file contents as a string
    """
    with open(css_file_path, 'r') as f:
        return f'<style>{f.read()}</style>'


def apply_css(css: str) -> None:
    """
    Apply CSS to the Streamlit app.
    
    Args:
        css: CSS content to apply
    """
    st.markdown(css, unsafe_allow_html=True)


def load_base_css() -> None:
    """
    Load and apply the base CSS files.
    """
    # Get the path to the static/css directory
    css_dir = Path(__file__).parent.parent / 'static' / 'css'
    
    # Load the main CSS file which imports all other base CSS files
    css_file = css_dir / 'main.css'
    
    if css_file.exists():
        css = load_css_file(str(css_file))
        apply_css(css)
    else:
        st.warning(f"CSS file not found: {css_file}")


def set_theme(theme_name: str = "light") -> None:
    """
    Set the theme by loading the appropriate theme CSS file.
    
    Args:
        theme_name: Theme name (light, dark, high-contrast)
    """
    # Validate theme name
    valid_themes = ["light", "dark", "high-contrast"]
    if theme_name not in valid_themes:
        st.warning(f"Invalid theme: {theme_name}. Using 'light' theme.")
        theme_name = "light"
    
    # Store theme name in session state
    st.session_state.theme = theme_name
    
    # Get the path to the theme CSS file
    css_dir = Path(__file__).parent.parent / 'static' / 'css' / 'themes'
    theme_file = css_dir / f"{theme_name}-theme.css"
    
    # Apply theme only if file exists (themes will be implemented in Part 3)
    if theme_file.exists():
        css = load_css_file(str(theme_file))
        apply_css(css)
```

### 8. Update App.py to Load CSS

Add code to the app.py file to load the CSS files:

```python
# Add this import
from utils.css_loader import load_base_css

# Add this near the beginning of app.py, before the UI is rendered
def load_app_styles():
    """Load application styles"""
    load_base_css()

# Call this function at app startup
load_app_styles()
```

## Test Impact Assessment

The CSS implementation in Part 1 of Phase 2 will have the following impacts on tests:

### UI Component Tests

1. **Visual Appearance Tests**: Any tests that check for specific CSS classes or visual properties will need to be updated to match the new styling system.
2. **Selector Tests**: If tests rely on specific CSS selectors to find elements, these may need to be updated to match the new class naming conventions.

### Test Fixtures

1. **CSS Loading Tests**: Add tests to verify that the CSS loader utility works correctly.
2. **Base Style Verification**: Add tests to verify that base styles are properly applied.

## Integration Steps

To implement Part 1 of Phase 2, follow these steps in order:

1. Create the base CSS files in the directory structure established in Phase 1
2. Implement the CSS loader utility
3. Update the application to load the CSS files
4. Test the base styling in the application

## Validation Steps

After implementing Part 1 of Phase 2, validate the following:

1. The CSS files are created in the correct locations
2. The CSS loader utility successfully loads the CSS files
3. Base styling (typography, spacing, colors) is applied to the application
4. No console errors are reported
5. The application functions correctly with the new styles

## Next Steps

After completing Part 1 of Phase 2, proceed to Part 2, which will implement the component-specific CSS styles. Part 2 will build upon the base CSS architecture established in Part 1. 