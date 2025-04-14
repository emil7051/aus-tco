# Refactoring Phase 4: Enhanced Input Forms and Parameter Feedback

This document outlines the fourth phase of the UI refactoring process for the Australian Heavy Vehicle TCO Modeller, focusing on improving input forms with visual hierarchy, validation, and parameter impact indicators.

## Overview

Phase 4 builds on the navigation and structure improvements from Phase 3 to enhance the input forms with better visual organization, immediate validation feedback, and parameter impact indicators. These improvements will make the application more user-friendly and help users understand how different parameters affect the TCO results.

## Implementation Tasks

### 1. Enhance Vehicle Input Forms

**File: `ui/inputs/vehicle.py`**

Key enhancements:
- Restructure input forms with logical grouping and visual hierarchy
- Add tabbed interface for different parameter categories
- Use card components for visual organization
- Add parameter impact indicators
- Implement responsive grid layout
- Include visual cues based on vehicle type

```python
def render_vehicle_inputs(vehicle_number: int) -> None:
    """
    Render improved vehicle input forms with visual hierarchy
    
    Args:
        vehicle_number: Vehicle number (1 or 2)
    """
    # Get vehicle type for styling
    state_prefix = f"vehicle_{vehicle_number}_input"
    vehicle_type = get_vehicle_type(state_prefix)
    
    # Add vehicle type visual indicator
    render_vehicle_header(vehicle_number, vehicle_type)
    
    # Create tabbed interface for parameter categories
    param_tabs = st.tabs([
        "Basic Parameters",
        "Performance",
        "Economics", 
        "Advanced Settings"
    ])
    
    # Implement each tab with properly grouped inputs
    with param_tabs[0]:
        render_basic_parameters(vehicle_number, state_prefix, vehicle_type)
        
    with param_tabs[1]:
        render_performance_parameters(vehicle_number, state_prefix, vehicle_type)
        
    with param_tabs[2]:
        render_economic_parameters(vehicle_number, state_prefix, vehicle_type)
        
    with param_tabs[3]:
        render_advanced_parameters(vehicle_number, state_prefix, vehicle_type)
```

### 2. Implement Parameter Impact Indicators

**File: `ui/inputs/parameter_helpers.py`**

Create a new helper module for parameter-specific UI components:

```python
def render_parameter_with_impact(label: str, key: str, default_value: Any, 
                               impact_level: str = "medium", help_text: str = None,
                               **input_args) -> Any:
    """
    Render a parameter input with impact indicator
    
    Args:
        label: Parameter label
        key: State key
        default_value: Default value
        impact_level: Impact level (high/medium/low)
        help_text: Help text to display
        **input_args: Additional input arguments
        
    Returns:
        Parameter value
    """
    # Create layout with impact indicator
    col1, col2 = st.columns([0.95, 0.05])
    
    with col1:
        # Create the input field
        value = create_validated_input(label, key, default=default_value, 
                                     help_text=help_text, **input_args)
    
    with col2:
        # Get impact details
        impact_info = get_parameter_impact(key)
        
        # Display impact indicator
        st.markdown(f"""
        <div class="impact-indicator {impact_info['class']}" 
             title="{impact_info['tooltip']}">
            {impact_info['icon']}
        </div>
        """, unsafe_allow_html=True)
    
    return value
```

### 3. Enhance Validation System

**File: `ui/inputs/validation.py`**

Create a comprehensive validation system:

```python
def validate_parameter(key: str, value: Any) -> Dict[str, Any]:
    """
    Validate a parameter value based on its key
    
    Args:
        key: Parameter key
        value: Parameter value
        
    Returns:
        Dictionary with validation result and message
    """
    # Extract parameter name from key
    param_name = key.split('.')[-1]
    
    # Define validation rules for specific parameters
    validation_rules = {
        "annual_distance_km": {
            "min": 1000, 
            "max": 500000,
            "message": "Annual distance must be between 1,000 and 500,000 km"
        },
        "analysis_period_years": {
            "min": 1,
            "max": 30,
            "message": "Analysis period must be between 1 and 30 years"
        },
        "purchase_price": {
            "min": 1000,
            "max": 10000000,
            "message": "Purchase price must be between $1,000 and $10,000,000"
        },
        # Add more parameter validation rules here
    }
    
    # Check if parameter has specific validation rules
    if param_name in validation_rules:
        rule = validation_rules[param_name]
        
        # Numeric validation
        if isinstance(value, (int, float)):
            if "min" in rule and value < rule["min"]:
                return {"valid": False, "message": rule["message"]}
            if "max" in rule and value > rule["max"]:
                return {"valid": False, "message": rule["message"]}
    
    # Default to valid if no specific rules or all rules pass
    return {"valid": True, "message": ""}
```

### 4. Create Parameter Comparison Tool

**File: `ui/inputs/parameter_comparison.py`**

Add a utility for comparing parameter values between vehicles:

```python
def render_parameter_comparison(param_path: str) -> None:
    """
    Render side-by-side comparison of a parameter between vehicles
    
    Args:
        param_path: Parameter path to compare
    """
    # Get values from both vehicles
    v1_value = get_safe_state_value(f"vehicle_1_input.{param_path}")
    v2_value = get_safe_state_value(f"vehicle_2_input.{param_path}")
    
    # Skip if either value is missing
    if v1_value is None or v2_value is None:
        return
    
    # Create comparison UI
    st.markdown('<div class="parameter-comparison">', unsafe_allow_html=True)
    
    # Parameter name/label
    param_name = param_path.split('.')[-1]
    label = get_formatted_label(param_name)
    st.markdown(f'<div class="param-label">{label}</div>', unsafe_allow_html=True)
    
    # Value comparison
    cols = st.columns([2, 2, 3])
    
    with cols[0]:
        st.markdown(f'<div class="param-vehicle">Vehicle 1</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="param-value v1">{format_parameter_value(param_name, v1_value)}</div>', 
                   unsafe_allow_html=True)
    
    with cols[1]:
        st.markdown(f'<div class="param-vehicle">Vehicle 2</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="param-value v2">{format_parameter_value(param_name, v2_value)}</div>', 
                   unsafe_allow_html=True)
    
    with cols[2]:
        # Calculate the difference
        if isinstance(v1_value, (int, float)) and isinstance(v2_value, (int, float)):
            diff = v2_value - v1_value
            diff_pct = (diff / v1_value * 100) if v1_value != 0 else 0
            
            # Format difference text
            if abs(diff) < 0.001:
                diff_text = "No difference"
                diff_class = "neutral"
            else:
                diff_text = f"{diff:+.3g} ({diff_pct:+.1f}%)"
                diff_class = "positive" if diff > 0 else "negative"
            
            st.markdown(f'<div class="param-diff {diff_class}">{diff_text}</div>', 
                       unsafe_allow_html=True)
        else:
            # Non-numeric comparison
            diff_class = "neutral" if v1_value == v2_value else "different"
            diff_text = "Same" if v1_value == v2_value else "Different"
            st.markdown(f'<div class="param-diff {diff_class}">{diff_text}</div>', 
                       unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
```

### 5. Create Enhanced Economic Parameters Form

**File: `ui/inputs/economic.py`**

Improve the economic parameters input form:

```python
def render_economic_parameters(vehicle_number: int, state_prefix: str, vehicle_type: str) -> None:
    """
    Render enhanced economic parameter inputs
    
    Args:
        vehicle_number: Vehicle number
        state_prefix: State key prefix
        vehicle_type: Vehicle type
    """
    # Create a card for economic parameters
    with UIComponentFactory.create_card("Economic Parameters", 
                                      f"v{vehicle_number}_economic", 
                                      vehicle_type):
        # Create responsive grid
        col1, col2 = st.columns(2)
        
        with col1:
            # Discount rate input with impact indicator
            discount_rate = render_parameter_with_impact(
                "Discount Rate (%)",
                f"{state_prefix}.economic.discount_rate_real",
                default_value=0.07,
                min_value=0.0,
                max_value=0.20,
                impact_level="high",
                step=0.01,
                format="%.2f",
                help_text="Real discount rate used for NPV calculations"
            )
            
            # Inflation rate
            inflation_rate = render_parameter_with_impact(
                "Inflation Rate (%)",
                f"{state_prefix}.economic.inflation_rate",
                default_value=0.025,
                min_value=0.0,
                max_value=0.10,
                impact_level="medium",
                step=0.005,
                format="%.3f",
                help_text="Annual inflation rate"
            )
        
        with col2:
            # Analysis period
            analysis_period = render_parameter_with_impact(
                "Analysis Period (years)",
                f"{state_prefix}.economic.analysis_period_years",
                default_value=10,
                min_value=1,
                max_value=30,
                impact_level="high",
                step=1,
                help_text="Time horizon for TCO analysis"
            )
            
            # Carbon tax rate
            carbon_tax_rate = render_parameter_with_impact(
                "Carbon Tax Rate ($/tonne)",
                f"{state_prefix}.economic.carbon_tax_rate_aud_per_tonne",
                default_value=25.0,
                min_value=0.0,
                max_value=200.0,
                impact_level="low",
                step=5.0,
                help_text="Carbon tax rate in AUD per tonne of CO2"
            )
```

### 6. Refactor Operational Parameters Input

**File: `ui/inputs/operational.py`**

Enhanced operational parameters input with appropriate visual hierarchy:

```python
def render_operational_parameters(vehicle_number: int, state_prefix: str, vehicle_type: str) -> None:
    """
    Render enhanced operational parameter inputs
    
    Args:
        vehicle_number: Vehicle number
        state_prefix: State key prefix
        vehicle_type: Vehicle type
    """
    # Create a card for operational parameters
    with UIComponentFactory.create_card("Operational Parameters", 
                                      f"v{vehicle_number}_operational", 
                                      vehicle_type):
        # Usage parameters section
        st.markdown("### Usage Parameters")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Annual distance
            annual_distance = render_parameter_with_impact(
                "Annual Distance (km)",
                f"{state_prefix}.operational.annual_distance_km",
                default_value=80000,
                min_value=1000,
                max_value=500000,
                impact_level="high",
                step=1000,
                help_text="Annual driving distance"
            )
            
            # Operating days
            operating_days = render_parameter_with_impact(
                "Operating Days per Year",
                f"{state_prefix}.operational.operating_days_per_year",
                default_value=240,
                min_value=1,
                max_value=365,
                impact_level="low",
                step=1,
                help_text="Number of operating days per year"
            )
        
        with col2:
            # Vehicle life
            vehicle_life = render_parameter_with_impact(
                "Vehicle Life (years)",
                f"{state_prefix}.operational.vehicle_life_years",
                default_value=12,
                min_value=1,
                max_value=30,
                impact_level="medium",
                step=1,
                help_text="Expected operational life of the vehicle"
            )
            
            # Load factor
            load_factor = render_parameter_with_impact(
                "Average Load Factor",
                f"{state_prefix}.operational.average_load_factor",
                default_value=0.7,
                min_value=0.0,
                max_value=1.0,
                impact_level="medium",
                step=0.05,
                format="%.2f",
                help_text="Average fraction of maximum payload capacity utilized"
            )
        
        # Add divider for logical separation
        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
        
        # Route characteristics
        st.markdown("### Route Characteristics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Urban operation toggle
            urban_operation = st.toggle(
                "Urban Operation",
                value=get_safe_state_value(f"{state_prefix}.operational.is_urban_operation", True),
                key=f"{state_prefix}.operational.is_urban_operation_input",
                help="Whether the vehicle operates primarily in urban environments"
            )
            
            # Set the value in session state
            set_safe_state_value(f"{state_prefix}.operational.is_urban_operation", urban_operation)
        
        with col2:
            # Daily distance
            daily_distance = render_parameter_with_impact(
                "Daily Distance (km)",
                f"{state_prefix}.operational.daily_distance_km",
                default_value=annual_distance / operating_days if operating_days > 0 else 300,
                min_value=1,
                max_value=2000,
                impact_level="medium",
                step=10,
                help_text="Average daily driving distance"
            )
```

## Integration Steps

To implement Phase 4, follow these steps:

1. Create the validation and parameter helper modules first
2. Update the input form components to use the new helper functions
3. Apply the changes to vehicle inputs, then operational and economic forms
4. Ensure proper integration with existing CSS
5. Test the enhanced forms with various inputs and validation cases

## Validation

After implementing Phase 4, verify:

1. Input forms have a clear visual hierarchy with logical grouping
2. Validation provides immediate feedback for invalid inputs
3. Parameter impact indicators are visible and convey their meaning
4. Form components are responsive and adapt to different screen sizes
5. Tabbed interfaces work correctly and maintain state between tabs
6. Vehicle type-specific styling is applied consistently

## Next Steps

After completing Phase 4, proceed to Phase 5, which will implement enhanced results visualization and side-by-side comparison features. 