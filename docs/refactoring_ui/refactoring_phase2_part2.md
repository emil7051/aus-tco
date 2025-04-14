# Refactoring Phase 2 Part 2: Component CSS Styles

This document outlines the second part of Phase 2 of the UI refactoring process for the Australian Heavy Vehicle TCO Modeller, focusing on implementing CSS styles for the specific UI components.

## Scope of Part 2

Part 2 of Phase 2 focuses specifically on:
1. Creating CSS styles for individual UI components
2. Implementing styles that align with the base styles established in Part 1
3. Ensuring consistent styling across all UI elements

This part builds on the foundation established in Phase 2 Part 1, which implemented the base CSS architecture and variables.

## Prerequisites

- Phase 1 (Terminology Standardization and UI Utilities) must be completed
- Phase 2 Part 1 (Base CSS Architecture and Variables) must be completed
- The directory structure and base CSS files should be in place

## Implementation Tasks

### 1. Create Component CSS File Structure

Create the component CSS files in the structure established in Phase 2 Part 1:

```
/static
  /css
    /components
      cards.css            # Card component styling
      forms.css            # Form element styling
      navigation.css       # Navigation component styling
      metrics.css          # Metrics display styling
      sidebar.css          # Sidebar-specific styling
      tables.css           # Table component styling
```

### 2. Update Main CSS File (main.css)

Update the main CSS file to import the component CSS files:

```css
/* ==========================================================================
   Australian Heavy Vehicle TCO Modeller - Main CSS File
   ========================================================================== */

/* Base styles */
@import url('./base/reset.css');
@import url('./base/variables.css');
@import url('./base/typography.css');
@import url('./base/layout.css');

/* Component styles */
@import url('./components/cards.css');
@import url('./components/forms.css');
@import url('./components/navigation.css');
@import url('./components/metrics.css');
@import url('./components/sidebar.css');
@import url('./components/tables.css');

/* Theme styles will be imported in Part 3 */
```

### 3. Create Card Component Styles (cards.css)

```css
/* ==========================================================================
   Card Component Styles
   ========================================================================== */

.card {
  background-color: var(--card-bg);
  border: 1px solid var(--card-border);
  border-left: 4px solid var(--card-border);
  border-radius: var(--border-radius-md);
  padding: var(--spacing-md);
  margin-bottom: var(--spacing-md);
  box-shadow: var(--shadow-sm);
  transition: box-shadow var(--transition-normal);
}

.card:hover {
  box-shadow: var(--shadow-md);
}

.card-title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  margin-bottom: var(--spacing-sm);
  color: var(--text-primary);
}

/* Cards with vehicle-specific styling */
.card.vehicle-battery_electric {
  border-left-color: var(--bet-primary);
}

.card.vehicle-diesel {
  border-left-color: var(--diesel-primary);
}

/* Card content sections */
.card-section {
  margin-bottom: var(--spacing-md);
  padding-bottom: var(--spacing-sm);
  border-bottom: 1px solid var(--divider-color);
}

.card-section:last-child {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}

/* Small cards for summary metrics */
.metric-card {
  background-color: var(--card-bg);
  border-radius: var(--border-radius-sm);
  padding: var(--spacing-sm);
  box-shadow: var(--shadow-sm);
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.metric-card .metric-value {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  margin: var(--spacing-xs) 0;
}

.metric-card .metric-label {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
}

/* Special card types */
.info-card {
  background-color: rgba(var(--info-color), 0.05);
  border-left-color: var(--info-color);
}

.warning-card {
  background-color: rgba(var(--warning-color), 0.05);
  border-left-color: var(--warning-color);
}

.error-card {
  background-color: rgba(var(--error-color), 0.05);
  border-left-color: var(--error-color);
}

.success-card {
  background-color: rgba(var(--success-color), 0.05);
  border-left-color: var(--success-color);
}
```

### 4. Create Form Component Styles (forms.css)

```css
/* ==========================================================================
   Form Component Styles
   ========================================================================== */

/* Form containers */
.form-container {
  margin-bottom: var(--spacing-lg);
}

.form-section {
  margin-bottom: var(--spacing-md);
  padding-bottom: var(--spacing-sm);
  border-bottom: 1px solid var(--divider-color);
}

.form-section:last-child {
  border-bottom: none;
}

/* Form groups */
.input-group {
  margin-bottom: var(--spacing-md);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-md);
  padding: var(--spacing-md);
  background-color: var(--bg-secondary);
}

.input-container {
  margin-bottom: var(--spacing-sm);
  position: relative;
}

.input-container:last-child {
  margin-bottom: 0;
}

/* Input field styling */
.stTextInput input,
.stNumberInput input,
.stSelectbox select {
  border: 1px solid var(--input-border);
  border-radius: var(--border-radius-sm);
  padding: var(--spacing-xs) var(--spacing-sm);
  width: 100%;
  font-size: var(--font-size-base);
  transition: border-color var(--transition-fast);
  background-color: var(--input-bg);
}

.stTextInput input:focus,
.stNumberInput input:focus,
.stSelectbox select:focus {
  border-color: var(--input-focus-border);
  outline: none;
  box-shadow: 0 0 0 1px var(--input-focus-border);
}

/* Checkbox styling */
.stCheckbox label {
  display: flex;
  align-items: center;
  cursor: pointer;
}

/* Radio button styling */
.stRadio label {
  cursor: pointer;
}

/* Field validation styling */
.invalid-input input,
.invalid-input select {
  border-color: var(--error-color);
  background-color: rgba(var(--error-color), 0.05);
}

.validation-message {
  color: var(--error-color);
  font-size: var(--font-size-xs);
  margin-top: var(--spacing-xs);
}

/* Parameter impact indicator */
.impact-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  margin-left: auto;
  cursor: help;
}

.impact-indicator.high {
  color: var(--error-color);
}

.impact-indicator.medium {
  color: var(--warning-color);
}

.impact-indicator.low {
  color: var(--success-color);
}

/* Form buttons */
.form-buttons {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-sm);
  margin-top: var(--spacing-md);
}

/* Slider styling adjustments */
.stSlider {
  padding-top: var(--spacing-sm);
  padding-bottom: var(--spacing-sm);
}

/* Date input styling */
.stDateInput input {
  border: 1px solid var(--input-border);
  border-radius: var(--border-radius-sm);
  padding: var(--spacing-xs) var(--spacing-sm);
}
```

### 5. Create Navigation Component Styles (navigation.css)

```css
/* ==========================================================================
   Navigation Component Styles
   ========================================================================== */

/* Step navigation */
.step-navigation {
  display: flex;
  flex-wrap: wrap;
  margin-bottom: var(--spacing-md);
  border-bottom: 1px solid var(--border-color);
  padding-bottom: var(--spacing-sm);
}

.step-item {
  padding: var(--spacing-sm) var(--spacing-md);
  margin-right: var(--spacing-xs);
  border-radius: var(--border-radius-sm) var(--border-radius-sm) 0 0;
  cursor: pointer;
  transition: background-color var(--transition-fast), color var(--transition-fast);
  position: relative;
}

.step-item.active {
  background-color: var(--bg-primary);
  font-weight: var(--font-weight-medium);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  border-bottom: 1px solid var(--bg-primary);
  bottom: -1px;
}

.step-item:hover:not(.active) {
  background-color: var(--bg-secondary);
}

/* Progress indicator */
.progress-indicator {
  display: flex;
  align-items: center;
  margin-bottom: var(--spacing-md);
}

.progress-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
  position: relative;
}

.progress-step:not(:last-child)::after {
  content: '';
  position: absolute;
  top: 12px;
  left: 50%;
  width: 100%;
  height: 2px;
  background-color: var(--border-color);
  z-index: 0;
}

.progress-step.completed:not(:last-child)::after {
  background-color: var(--success-color);
}

.step-number {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background-color: var(--border-color);
  color: var(--text-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  z-index: 1;
}

.progress-step.completed .step-number {
  background-color: var(--success-color);
  color: white;
}

.progress-step.active .step-number {
  background-color: var(--info-color);
  color: white;
}

.step-label {
  font-size: var(--font-size-xs);
  margin-top: var(--spacing-xs);
  text-align: center;
}

/* Breadcrumb navigation */
.breadcrumbs {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  margin-bottom: var(--spacing-md);
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
}

.breadcrumb-item {
  display: flex;
  align-items: center;
}

.breadcrumb-item:not(:last-child)::after {
  content: '›';
  margin: 0 var(--spacing-xs);
  color: var(--text-secondary);
}

.breadcrumb-item.active {
  color: var(--text-primary);
  font-weight: var(--font-weight-medium);
}

/* Tabs styling */
.stTabs [data-baseweb="tab-list"] {
  gap: 1px;
}

.stTabs [data-baseweb="tab"] {
  padding: var(--spacing-sm) var(--spacing-md);
  background-color: var(--bg-secondary);
}

.stTabs [aria-selected="true"] {
  background-color: var(--bg-primary);
  font-weight: var(--font-weight-medium);
}

/* Expandable sections */
.expandable-section {
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-md);
  margin-bottom: var(--spacing-sm);
}

.expandable-header {
  padding: var(--spacing-sm);
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: var(--bg-secondary);
  border-radius: var(--border-radius-md) var(--border-radius-md) 0 0;
}

.expandable-content {
  padding: var(--spacing-md);
  border-top: 1px solid var(--border-color);
}
```

### 6. Create Metrics Component Styles (metrics.css)

```css
/* ==========================================================================
   Metrics Component Styles
   ========================================================================== */

.metric-container {
  padding: var(--spacing-sm);
  margin-bottom: var(--spacing-md);
  border-radius: var(--border-radius-sm);
  background-color: var(--bg-primary);
}

/* Override Streamlit's metric styling */
[data-testid="stMetric"] {
  background-color: transparent;
  padding: 0;
}

[data-testid="stMetricLabel"] {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  font-weight: var(--font-weight-medium);
}

[data-testid="stMetricValue"] {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-bold);
}

[data-testid="stMetricDelta"] {
  font-size: var(--font-size-sm);
}

/* Metrics panel */
.metrics-panel {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
}

.metric-card {
  flex: 1;
  min-width: 200px;
  background-color: var(--bg-primary);
  padding: var(--spacing-md);
  border-radius: var(--border-radius-md);
  box-shadow: var(--shadow-sm);
  text-align: center;
}

.metric-card.comparison {
  border-top: 3px solid var(--info-color);
}

.metric-card.lcod {
  border-top: 3px solid var(--energy-color);
}

.metric-card.payback {
  border-top: 3px solid var(--success-color);
}

.metric-insight {
  margin-top: var(--spacing-sm);
  font-size: var(--font-size-sm);
  padding: var(--spacing-sm);
  background-color: var(--bg-secondary);
  border-radius: var(--border-radius-sm);
}

.metric-insight .highlight {
  font-weight: var(--font-weight-bold);
}

/* Key metrics in sidebar */
.sidebar-metric {
  font-size: var(--font-size-sm);
  margin-bottom: var(--spacing-sm);
}

.sidebar-metric .label {
  color: var(--text-secondary);
  font-size: var(--font-size-xs);
}

.sidebar-metric .value {
  font-weight: var(--font-weight-semibold);
}

/* Comparison indicators */
.comparison-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-xs);
}

.comparison-indicator .comparison-value {
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
}

.comparison-indicator .comparison-arrow {
  font-size: var(--font-size-xl);
}

.higher {
  color: var(--error-color);
}

.lower {
  color: var(--success-color);
}
```

### 7. Create Sidebar Component Styles (sidebar.css)

```css
/* ==========================================================================
   Sidebar Component Styles
   ========================================================================== */

/* Sidebar header */
.sidebar .sidebar-header {
  margin-bottom: var(--spacing-md);
  padding-bottom: var(--spacing-sm);
  border-bottom: 1px solid var(--divider-color);
}

.sidebar .sidebar-header h1 {
  font-size: var(--font-size-xl);
  margin-bottom: var(--spacing-xs);
}

/* Sidebar sections */
.sidebar-section {
  margin-bottom: var(--spacing-md);
  padding-bottom: var(--spacing-sm);
  border-bottom: 1px solid var(--divider-color);
}

.sidebar-section:last-child {
  border-bottom: none;
}

.sidebar-section-title {
  font-size: var(--font-size-md);
  font-weight: var(--font-weight-semibold);
  margin-bottom: var(--spacing-sm);
}

/* Sidebar items */
.sidebar-item {
  margin-bottom: var(--spacing-sm);
  font-size: var(--font-size-sm);
}

/* Vehicle selector */
.vehicle-selector {
  margin-bottom: var(--spacing-md);
}

.vehicle-option {
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-sm);
  padding: var(--spacing-sm);
  margin-bottom: var(--spacing-sm);
  cursor: pointer;
  transition: background-color var(--transition-fast), border-color var(--transition-fast);
}

.vehicle-option:hover {
  background-color: var(--bg-secondary);
}

.vehicle-option.selected {
  border-color: var(--input-focus-border);
  background-color: rgba(var(--input-focus-border), 0.05);
}

.vehicle-option.bet {
  border-left: 3px solid var(--bet-primary);
}

.vehicle-option.diesel {
  border-left: 3px solid var(--diesel-primary);
}

/* Quick summary card in sidebar */
.quick-summary-card {
  background-color: var(--bg-secondary);
  border-radius: var(--border-radius-md);
  padding: var(--spacing-sm);
  margin-bottom: var(--spacing-md);
}

.quick-summary-card .card-header {
  font-weight: var(--font-weight-semibold);
  margin-bottom: var(--spacing-sm);
  padding-bottom: var(--spacing-xs);
  border-bottom: 1px solid var(--divider-color);
}

.vehicle-comparison {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--spacing-sm);
}

.vehicle-item {
  text-align: center;
  padding: var(--spacing-xs);
}

.vehicle-name {
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
}

.vehicle-tco {
  font-size: var(--font-size-md);
  font-weight: var(--font-weight-semibold);
}

.vehicle-lcod {
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
}

.key-insight {
  font-size: var(--font-size-xs);
  padding: var(--spacing-xs);
  background-color: var(--bg-tertiary);
  border-radius: var(--border-radius-sm);
  margin-top: var(--spacing-xs);
}

/* Theme selector in sidebar */
.theme-selector {
  display: flex;
  gap: var(--spacing-xs);
  margin-bottom: var(--spacing-sm);
}

.theme-option {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  cursor: pointer;
  border: 2px solid transparent;
}

.theme-option.selected {
  border-color: var(--input-focus-border);
}

.theme-option.light {
  background-color: #ffffff;
  border: 1px solid #dddddd;
}

.theme-option.dark {
  background-color: #1f1f1f;
}

.theme-option.high-contrast {
  background: linear-gradient(135deg, #ffffff 50%, #000000 50%);
}
```

### 8. Create Table Component Styles (tables.css)

```css
/* ==========================================================================
   Table Component Styles
   ========================================================================== */

/* Standard table */
.styled-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: var(--spacing-md);
  font-size: var(--font-size-sm);
}

.styled-table th,
.styled-table td {
  padding: var(--spacing-sm);
  text-align: left;
  border-bottom: 1px solid var(--border-color);
}

.styled-table th {
  background-color: var(--bg-secondary);
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
}

.styled-table tr:nth-child(even) {
  background-color: var(--bg-secondary);
}

.styled-table tr:hover {
  background-color: rgba(var(--info-color), 0.05);
}

/* Compact table */
.compact-table th,
.compact-table td {
  padding: var(--spacing-xs);
  font-size: var(--font-size-xs);
}

/* Bordered table */
.bordered-table th,
.bordered-table td {
  border: 1px solid var(--border-color);
}

/* Responsive table container */
.table-container {
  width: 100%;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

/* Table with row highlights */
.highlight-table .highlight-row {
  background-color: rgba(var(--info-color), 0.1);
}

/* Data table */
.data-table {
  font-family: var(--font-monospace);
  font-size: var(--font-size-xs);
}

.data-table th {
  font-weight: var(--font-weight-bold);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Numeric columns */
.numeric-cell {
  text-align: right;
  font-variant-numeric: tabular-nums;
}

/* Cell emphasis */
.cell-emphasis {
  font-weight: var(--font-weight-bold);
}

/* Row separator for section grouping */
.row-separator td {
  border-bottom: 2px solid var(--divider-color);
}

/* Table caption */
.table-caption {
  margin-top: var(--spacing-xs);
  margin-bottom: var(--spacing-sm);
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
  text-align: center;
}

/* Table footnotes */
.table-footnotes {
  margin-top: var(--spacing-sm);
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
}
```

### 9. Add Component CSS to Existing UI Components

Update the UIComponentFactory class in utils/ui_components.py to use the new component styles:

```python
# Update the existing create_card method to use the new card styles
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
```

## Test Impact Assessment

The component CSS implementation in Part 2 of Phase 2 will have the following impacts on tests:

### UI Component Tests

1. **Component Tests**: Tests for UI components will need to be updated to account for the new CSS classes and structure.
2. **Visual Tests**: Visual regression tests will need to be updated for the new component appearances.

### Test Fixtures

1. **Component Rendering Tests**: Update tests that verify component rendering with the new styles.
2. **Behavior Tests**: Tests that check for component behavior (hover, focus, etc.) should be updated.

## Integration Steps

To implement Part 2 of Phase 2, follow these steps in order:

1. Create the component CSS files in the structure established in Phase 2 Part 1
2. Update the main CSS file to import component styles
3. Update the UIComponentFactory to use the new component styles
4. Test all UI components with the new styles

## Validation Steps

After implementing Part 2 of Phase 2, validate the following:

1. The component CSS files are created in the correct locations
2. The CSS styles are properly applied to UI components
3. Components are visually consistent with the base styling from Part 1
4. Interactive elements (forms, navigation) function correctly with the new styles
5. The application maintains its functionality with the new component styling

## Next Steps

After completing Part 2 of Phase 2, proceed to Part 3, which will implement the theme system for the application. Part 3 will build upon the component styles established in Part 2 to provide alternate visual themes.