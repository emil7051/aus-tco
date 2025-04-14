# Phase 5 Implementation Plan

## Overview

This plan outlines the approach for fully implementing the enhanced results visualization and side-by-side layout from Phase 5 of the UI refactoring, focusing on proper integration with the TCO model and removal of all placeholder/dummy data.

## Completed Components from Refactoring Phase 5

The following components have been implemented as part of the refactoring process but need integration with the actual TCO model:

1. **Side-by-Side Layout (`ui/layout.py`)**
   - Created `create_live_preview_layout()` function for side-by-side viewing
   - Implemented toggling between standard and live preview modes
   - Added layout state persistence in session state

2. **Modular Results Dashboard (`ui/results/display.py`)**
   - Implemented `display_results()` with dashboard layout options
   - Created layout switching between Standard, Detailed, and Executive view
   - Added dashboard toolbar with controls

3. **Key Metrics Panel (`ui/results/metrics.py`)**
   - Implemented `render_key_metrics_panel()` with visual emphasis
   - Created interactive metric cards for TCO, cost per km, and payback period
   - Added visualisations for key metrics with insights

4. **Multi-Perspective Analysis (`ui/results/dashboard.py`)**
   - Created `render_standard_dashboard()` with tabbed analysis
   - Implemented Financial Overview, Cost Breakdown, Timeline, and Environmental tabs
   - Added interactive controls for each analysis perspective

5. **Environmental Impact Analysis (`ui/results/environmental.py`)**
   - Implemented `render_environmental_impact()` with CO2 emissions comparison
   - Created Energy Consumption and Sustainability Metrics tabs
   - Added contextual environmental impact equivalents

6. **Enhanced Sidebar Tools (`ui/sidebar.py`)**
   - Added `render_quick_comparison_tools()` for snapshot analysis
   - Implemented key differences highlighting
   - Created quick sensitivity check controls

7. **Live Preview Mode (`ui/results/live_preview.py`)**
   - Implemented `display_results_in_live_mode()` for side-by-side layout
   - Created optimised views for the side panel
   - Added parameter impact analysis interface

8. **Results Export (`ui/results/utils.py`)**
   - Implemented `generate_results_export()` for Excel generation
   - Added structured data export with multiple sheets
   - Included metadata and formatting for reports

## Implementation Stages

### Stage 1: TCO Model Enhancement (Foundation)

#### 1.1 Add Environmental Impact Calculations
- **Tasks:**
  - Add CO2 emissions tracking to the TCO calculator
  - Implement energy consumption metrics for both vehicle types
  - Add environmental equivalence calculations (trees, cars, etc.)
- **Files to modify:**
  - `tco_model/calculator.py` - Add emissions calculation methods
  - `tco_model/models.py` - Add emissions data to TCO output structure
- **Builds upon:**
  - `ui/results/environmental.py` - Uses the placeholder emissions data structure

#### 1.2 Enhance Component Breakdown Access
- **Tasks:**
  - Create standardised methods to extract component costs
  - Ensure consistent component categorisation across vehicle types
  - Add methods to calculate component percentages of total TCO
- **Files to modify:**
  - `tco_model/models.py` - Add component categorisation methods
  - `tco_model/calculator.py` - Standardise component calculation
- **Builds upon:**
  - `ui/results/dashboard.py` - Uses component breakdown for visualisations
  - `ui/results/utils.py` - Contains component access utilities

#### 1.3 Implement Sensitivity Analysis Engine
- **Tasks:**
  - Create a parameter sensitivity analysis module
  - Implement parameter variation and recalculation logic
  - Add methods to generate sensitivity curves
- **Files to modify:**
  - `tco_model/calculator.py` - Add sensitivity analysis methods
  - `tco_model/models.py` - Add sensitivity results data structures
- **Builds upon:**
  - `ui/sidebar.py` - Contains quick sensitivity check functionality
  - `ui/results/live_preview.py` - Has parameter impact analysis interface

#### 1.4 Add Payback and Investment Analysis
- **Tasks:**
  - Implement proper payback period calculation
  - Add ROI and other investment metrics
  - Calculate lifetime saving projections
- **Files to modify:**
  - `tco_model/calculator.py` - Add investment analysis methods
  - `tco_model/models.py` - Enhance comparison results with investment metrics
- **Builds upon:**
  - `ui/results/metrics.py` - Contains investment analysis card
  - `ui/results/display.py` - Shows investment analysis in executive summary

### Stage 2: UI Integration (Connection Layer)

#### 2.1 Results Dashboard Integration
- **Tasks:**
  - Connect dashboard views to actual TCO model data
  - Remove all placeholder data in the dashboard module
  - Ensure consistent data access patterns
- **Files to modify:**
  - `ui/results/dashboard.py` - Remove placeholder data, connect to model
  - `ui/results/display.py` - Ensure proper data flow
- **Builds upon:**
  - The existing tabbed dashboard implementation with cost breakdown, financial overview,
    annual timeline and environmental impact tabs

#### 2.2 Metrics Panel Integration
- **Tasks:**
  - Connect key metrics panel to TCO model data
  - Implement proper insight generation based on model results
  - Replace placeholder visualisations with data-driven charts
- **Files to modify:**
  - `ui/results/metrics.py` - Remove dummy implementations, connect to model data
- **Builds upon:**
  - The existing metrics panel with TCO, LCOD, and investment cards

#### 2.3 Environmental Analysis Integration
- **Tasks:**
  - Connect environmental module to TCO emissions data
  - Implement actual emissions timeline charts from model data
  - Replace placeholder sustainability metrics with calculated values
- **Files to modify:**
  - `ui/results/environmental.py` - Remove dummy implementations, connect to emissions data
- **Builds upon:**
  - Existing CO2 emissions, energy consumption, and sustainability metrics tabs

#### 2.4 Component Analysis Integration
- **Tasks:**
  - Connect component breakdown to TCO component data
  - Implement actual component insights from model analysis
  - Replace placeholder component charts with model-based charts
- **Files to modify:**
  - `ui/results/dashboard.py` - Update component analysis functions
  - `ui/results/utils.py` - Ensure proper component access methods
- **Builds upon:**
  - Existing cost breakdown analysis with stacked, grouped, and pie chart views

#### 2.5 Parameter Impact Analysis Integration
- **Tasks:**
  - Connect parameter impact view to sensitivity analysis engine
  - Implement real-time sensitivity calculation
  - Replace placeholder impact charts with actual sensitivity curves
- **Files to modify:**
  - `ui/results/live_preview.py` - Update parameter impact functions
  - `ui/sidebar.py` - Connect quick sensitivity check to the model
- **Builds upon:**
  - Parameter impact interface in live preview mode
  - Quick sensitivity check in sidebar

### Stage 3: Export and Data Sharing (Output Layer)

#### 3.1 Excel Export Enhancement
- **Tasks:**
  - Connect Excel report generation to actual TCO model data
  - Add formatted tables and embedded charts
  - Include all TCO model data in structured format
- **Files to modify:**
  - `ui/results/utils.py` - Enhance Excel export functionality
- **Builds upon:**
  - Basic Excel export functionality already implemented in `generate_results_export()`

#### 3.2 PDF Report Generation
- **Tasks:**
  - Implement PDF report generation
  - Design professional report layout
  - Include all visualisations and insights
- **Files to modify:**
  - Create new `ui/results/export.py` module for PDF generation
- **Builds upon:**
  - Executive dashboard view which already formats data for reporting

#### 3.3 Data Persistence and Sharing
- **Tasks:**
  - Implement configuration saving and loading
  - Add results sharing functionality
  - Enable comparison between saved analyses
- **Files to modify:**
  - `ui/config_management.py` - Enhance configuration management
  - Create new `ui/results/sharing.py` module
- **Builds upon:**
  - Existing result structure in session state

### Stage 4: User Experience Enhancement (Presentation Layer)

#### 4.1 Side-by-Side Layout Refinement
- **Tasks:**
  - Enhance layout switching with animation
  - Implement automatic layout adaptation
  - Add layout preferences persistence
- **Files to modify:**
  - `ui/layout.py` - Refine layout switching
  - `ui/sidebar.py` - Enhance layout controls
- **Builds upon:**
  - Existing side-by-side layout implementation in `create_live_preview_layout()`

#### 4.2 Performance Optimisation
- **Tasks:**
  - Optimise chart rendering for large datasets
  - Implement data caching for frequently accessed results
  - Add progressive loading for complex visualisations
- **Files to modify:**
  - `ui/results/charts.py` - Optimise chart rendering
  - `ui/results/utils.py` - Implement caching
- **Builds upon:**
  - Existing chart implementations for each view

#### 4.3 Insight Generation Enhancement
- **Tasks:**
  - Implement advanced insight generation algorithms
  - Add context-aware recommendations
  - Enhance explanatory text based on analysis results
- **Files to modify:**
  - Create new `ui/results/insights.py` module
  - Update all insight-related functions across modules
- **Builds upon:**
  - Basic insight text in metrics panel and executive summary

### Stage 5: Testing and Documentation (Quality Assurance)

#### 5.1 Unit and Integration Testing
- **Tasks:**
  - Write unit tests for all new model functions
  - Implement integration tests for UI-model interaction
  - Create visual regression tests for charts
- **Files to modify:**
  - Create test files in `tests/` directory
- **Builds upon:**
  - Existing test framework and utilities

#### 5.2 Comprehensive Documentation
- **Tasks:**
  - Document all new functions and modules
  - Create user guide for new features
  - Update API documentation
- **Files to modify:**
  - Update docstrings in all modified files
  - Create/update documentation in `docs/` directory
- **Builds upon:**
  - Existing documentation structure and style

#### 5.3 Performance Profiling
- **Tasks:**
  - Profile application performance
  - Identify and fix bottlenecks
  - Optimise for responsiveness
- **Files to modify:**
  - Potentially any file based on profiling results
- **Builds upon:**
  - Current application performance baseline

## Integration Strategy

To ensure a smooth integration between the refactored UI components and the TCO model, we'll implement a systematic approach that minimizes disruption while ensuring data consistency.

### Model-UI Interface Layer

#### 1. Create Data Transformation Utilities

We need to create utilities that transform TCO model outputs into formats expected by the UI components:

**File: `ui/results/data_adapters.py`**

```python
def adapt_tco_results_for_dashboard(results: Dict[str, TCOOutput], 
                                  comparison: ComparisonResult) -> Dict[str, Any]:
    """
    Transform TCO model outputs into the format expected by the dashboard components.
    
    Args:
        results: Dictionary of TCO result objects
        comparison: Comparison result object
        
    Returns:
        Dictionary with all data needed by the dashboard in the expected format
    """
    # Extract and transform data for key metrics
    key_metrics = {
        "vehicle_1": {
            "name": results["vehicle_1"].vehicle_name,
            "total_tco": results["vehicle_1"].total_tco,
            "lcod": results["vehicle_1"].lcod,
            # Other metrics...
        },
        "vehicle_2": {
            "name": results["vehicle_2"].vehicle_name,
            "total_tco": results["vehicle_2"].total_tco,
            "lcod": results["vehicle_2"].lcod,
            # Other metrics...
        },
        "comparison": {
            "tco_difference": comparison.tco_difference,
            "tco_percentage": comparison.tco_percentage,
            "lcod_difference": comparison.lcod_difference,
            "cheaper_option": comparison.cheaper_option,
            # Other comparison metrics...
        }
    }
    
    # Extract and transform data for component breakdown
    components = extract_component_breakdown(results, comparison)
    
    # Extract and transform data for timeline analysis
    timeline = extract_timeline_data(results, comparison)
    
    # Extract and transform data for environmental analysis
    environmental = extract_environmental_data(results, comparison)
    
    return {
        "key_metrics": key_metrics,
        "components": components,
        "timeline": timeline,
        "environmental": environmental,
        "sensitivity": extract_sensitivity_data(results, comparison)
    }

def extract_component_breakdown(results: Dict[str, TCOOutput], 
                              comparison: ComparisonResult) -> Dict[str, Any]:
    """Extract component breakdown data from TCO results."""
    # Implementation...

def extract_timeline_data(results: Dict[str, TCOOutput], 
                       comparison: ComparisonResult) -> Dict[str, Any]:
    """Extract timeline data from TCO results."""
    # Implementation...

def extract_environmental_data(results: Dict[str, TCOOutput], 
                            comparison: ComparisonResult) -> Dict[str, Any]:
    """Extract environmental data from TCO results."""
    # Implementation...

def extract_sensitivity_data(results: Dict[str, TCOOutput], 
                          comparison: ComparisonResult) -> Dict[str, Any]:
    """Extract sensitivity analysis data from TCO results."""
    # Implementation...
```

#### 2. Create Result Cache Management

To improve performance and manage state between UI components:

**File: `ui/results/cache_manager.py`**

```python
class ResultCacheManager:
    """
    Manages caching and access to analysis results and derived data.
    Ensures consistent data access across UI components and improves performance.
    """
    
    def __init__(self):
        """Initialize the cache manager."""
        self.last_update_time = None
        self.derived_data = {}
        
    def update_results(self, results: Dict[str, TCOOutput], 
                     comparison: ComparisonResult):
        """
        Update cached results and regenerate all derived data.
        
        Args:
            results: Dictionary of TCO result objects
            comparison: Comparison result object
        """
        from ui.results.data_adapters import adapt_tco_results_for_dashboard
        
        # Update timestamp
        import datetime
        self.last_update_time = datetime.datetime.now()
        
        # Generate and cache derived data
        self.derived_data = adapt_tco_results_for_dashboard(results, comparison)
        
    def get_data_for_component(self, component_name: str) -> Dict[str, Any]:
        """
        Get data specifically formatted for a UI component.
        
        Args:
            component_name: Name of the UI component (e.g., "key_metrics", "timeline")
            
        Returns:
            Dictionary with data for the specified component
        """
        if component_name in self.derived_data:
            return self.derived_data[component_name]
        return {}
```

### Integration Approach for UI Components

#### 1. Gradual Module-by-Module Integration

Instead of attempting to integrate all components at once, we'll follow a gradual approach:

1. **Start with the Key Metrics Panel**:
   - This is the highest-level summary component
   - Integration here will establish patterns for other components
   - Successful integration will provide immediate value

2. **Integrate Core Dashboard Next**:
   - After metrics panel, integrate the main dashboard tabs
   - Focus on financial data before environmental data

3. **Environmental Analysis Third**:
   - Once financial components are working, add environmental integration
   - This depends on the emissions calculation enhancements to the model

4. **Live Preview Mode Last**:
   - This is the most complex integration point
   - It requires all other components to be working first

#### 2. Parallel Development Strategy

To maintain steady progress, we'll adopt a parallel development strategy:

1. **TCO Model Enhancements**:
   - One team member focuses on extending the TCO model with emissions and sensitivity analysis
   - This work can proceed independently of the UI integration

2. **Interface Layer Development**:
   - Another team member develops the data transformation utilities
   - Creates tests to ensure data is correctly transformed

3. **UI Component Integration**:
   - A third team member integrates the UI components with the interface layer
   - Works closely with the interface layer developer

#### 3. Testing Strategy 

For each integration point:

1. **Create Test Fixtures**:
   - Generate sample TCO model data for testing
   - Define expected output after transformation

2. **Unit Test the Interface Layer**:
   - Ensure data transformation works correctly
   - Verify performance with large datasets

3. **Integration Test the UI Components**:
   - Verify UI components render correctly with real data
   - Test edge cases (zero values, negative values, etc.)

### Component-Specific Integration Steps

#### 1. Key Metrics Panel Integration

1. Extend `render_key_metrics_panel()` to use actual TCO data:
   - Replace placeholder metrics with data from TCO results
   - Update visualizations to use actual data
   - Implement real insight generation based on comparison

2. Key files to modify:
   - `ui/results/metrics.py`
   - `ui/results/charts.py` (for metrics visualizations)

#### 2. Dashboard Integration

1. Update dashboard tabs to use actual data:
   - Connect financial overview to TCO results
   - Connect cost breakdown to component data
   - Connect timeline to annual costs data

2. Key files to modify:
   - `ui/results/dashboard.py`
   - `ui/results/charts.py` (for dashboard visualizations)

#### 3. Environmental Analysis Integration

1. Connect environmental analysis to emissions data:
   - Update CO2 emissions comparisons
   - Connect energy consumption analysis
   - Implement actual sustainability metrics

2. Key files to modify:
   - `ui/results/environmental.py`
   - `ui/results/charts.py` (for environmental visualizations)

#### 4. Live Preview Integration

1. Update live preview mode:
   - Connect parameter impact analysis to sensitivity engine
   - Implement real-time recalculation
   - Update visualizations for parameter changes

2. Key files to modify:
   - `ui/results/live_preview.py`
   - `ui/layout.py` (for side-by-side layout)

### Implementation Schedule with Dependencies

| Week | Task | Dependencies |
|------|------|-------------|
| 1 | TCO Model Extension (Emissions) | None |
| 1 | Interface Layer Development (Metrics) | None |
| 2 | Key Metrics Panel Integration | Interface Layer (Metrics) |
| 2 | TCO Model Extension (Sensitivity) | None |
| 3 | Dashboard Integration | Interface Layer, Metrics Integration |
| 3 | Interface Layer Development (Environmental) | TCO Model (Emissions) |
| 4 | Environmental Analysis Integration | Interface Layer (Environmental) |
| 4 | Interface Layer Development (Sensitivity) | TCO Model (Sensitivity) |
| 5 | Live Preview Integration | All previous integrations |
| 6 | Export Enhancement | All previous integrations |
| 7 | Testing and Documentation | All implementations |

This schedule accounts for dependencies between components and ensures steady progress throughout the integration process.

## Transition Management

To ensure a smooth transition from placeholder data to real model data without breaking the application, we'll implement the following strategies:

### 1. Dual-Mode Data Source Configuration

Create a system that can transparently switch between placeholder data and real model data:

**File: `ui/results/data_source.py`**

```python
class ResultDataSource:
    """
    Manages data sources for UI components, allowing transparent switching
    between placeholder data and real model data.
    """
    
    def __init__(self, use_real_data=True):
        """
        Initialize the data source manager.
        
        Args:
            use_real_data: Flag to use real TCO model data (True) or placeholder data (False)
        """
        self.use_real_data = use_real_data
        self.cache_manager = None
        
        if use_real_data:
            from ui.results.cache_manager import ResultCacheManager
            self.cache_manager = ResultCacheManager()
    
    def get_key_metrics_data(self, results=None, comparison=None):
        """
        Get data for key metrics panel.
        
        Args:
            results: Dictionary of TCO result objects (only used in real data mode)
            comparison: Comparison result object (only used in real data mode)
            
        Returns:
            Dictionary with data formatted for key metrics panel
        """
        if self.use_real_data and results and comparison:
            # Update cache with latest results
            self.cache_manager.update_results(results, comparison)
            return self.cache_manager.get_data_for_component("key_metrics")
        else:
            # Return placeholder data
            from ui.results.placeholder_data import generate_key_metrics_placeholder
            return generate_key_metrics_placeholder()
    
    # Similar methods for other components...
```

### 2. Placeholder Data Preservation

Maintain the placeholder data functionality as a fallback mechanism:

**File: `ui/results/placeholder_data.py`**

```python
def generate_key_metrics_placeholder():
    """Generate placeholder data for key metrics panel."""
    return {
        "vehicle_1": {
            "name": "BET Truck",
            "total_tco": 850000,
            "lcod": 1.25,
            # Other metrics...
        },
        "vehicle_2": {
            "name": "Diesel Truck",
            "total_tco": 950000,
            "lcod": 1.40,
            # Other metrics...
        },
        "comparison": {
            "tco_difference": -100000,
            "tco_percentage": -10.5,
            "lcod_difference": -0.15,
            "cheaper_option": 1,
            # Other comparison metrics...
        }
    }

# Similar functions for other components...
```

### 3. Feature Flags for Component Integration

Implement feature flags to control integration at a component level:

**File: `ui/feature_flags.py`**

```python
class FeatureFlags:
    """
    Manages feature flags for controlled rollout of integrated components.
    """
    
    def __init__(self):
        """Initialize default feature flags."""
        self.flags = {
            "use_real_metrics_data": False,
            "use_real_dashboard_data": False,
            "use_real_environmental_data": False,
            "use_real_live_preview": False,
            "enable_sensitivity_analysis": False,
            "enable_enhanced_export": False
        }
    
    def set_flag(self, flag_name, value):
        """Set a feature flag."""
        if flag_name in self.flags:
            self.flags[flag_name] = value
    
    def get_flag(self, flag_name):
        """Get the value of a feature flag."""
        return self.flags.get(flag_name, False)
    
    def enable_all_real_data(self):
        """Enable all real data flags."""
        for flag_name in self.flags:
            if flag_name.startswith("use_real_"):
                self.flags[flag_name] = True
    
    def disable_all_real_data(self):
        """Disable all real data flags (use placeholder data)."""
        for flag_name in self.flags:
            if flag_name.startswith("use_real_"):
                self.flags[flag_name] = False
```

### 4. Progressive Integration Strategy

Implement an approach that gradually integrates real data:

1. **Testing Mode Toggle**:
   - Add a developer toggle in the app to switch between real and placeholder data
   - Enable development and testing without affecting production users

2. **Component-by-Component Rollout**:
   - Start with one component (Key Metrics Panel)
   - Verify integration works correctly
   - Enable next component only after successful validation

3. **Data Consistency Validation**:
   - Implement validation layers that compare placeholder data structure with real data
   - Ensure UI components receive consistent data structure regardless of source

4. **Fallback Mechanisms**:
   - Add error handling that falls back to placeholder data if real data fails
   - Log issues for debugging without breaking the user experience

### 5. Integration Adapter Pattern

Create adapter functions to ensure consistent data structure:

**File: `ui/results/integration_adapters.py`**

```python
def adapt_real_metrics_to_placeholder_format(real_metrics_data):
    """
    Adapt real metrics data to match the placeholder data structure.
    This ensures consistent data structure for UI components.
    
    Args:
        real_metrics_data: Metrics data from the TCO model
        
    Returns:
        Adapted data matching placeholder structure
    """
    # Implementation...

def adapt_real_dashboard_to_placeholder_format(real_dashboard_data):
    """
    Adapt real dashboard data to match the placeholder data structure.
    
    Args:
        real_dashboard_data: Dashboard data from the TCO model
        
    Returns:
        Adapted data matching placeholder structure
    """
    # Implementation...

# Similar adapters for other components...
```

### 6. Rollback Strategy

Plan for potential rollback if integration issues are discovered:

1. **Version Management**:
   - Maintain clear version markers for each integration milestone
   - Enable selective rollback of specific components

2. **Isolated Deployments**:
   - Test integrated components in an isolated environment
   - Verify functionality before production deployment

3. **Dual-Maintenance Period**:
   - Maintain both placeholder and real data paths for a period
   - Allow quick switching between them if issues arise

### 7. User Impact Minimization

Reduce disruption to users during the transition:

1. **Transparent Switching**:
   - Switch data sources without affecting UI functionality
   - Maintain consistent UI experience throughout transition

2. **Performance Monitoring**:
   - Track performance metrics during the transition
   - Ensure real data integration doesn't impact responsiveness

3. **Incremental UX Improvements**:
   - After successful integration, enhance UI components
   - Add new insights and visualizations enabled by real data

### Implementation Timeline for Transition

| Week | Transition Task | Description |
|------|----------------|-------------|
| 1-2 | Development Environment Setup | Configure feature flags and dual-mode data sources |
| 2 | Key Metrics Testing | Test Key Metrics Panel with both data sources |
| 3 | Key Metrics Production | Deploy Key Metrics with real data integration |
| 3-4 | Dashboard Testing | Test Dashboard with both data sources |
| 4 | Dashboard Production | Deploy Dashboard with real data integration |
| 5 | Environmental Testing | Test Environmental Analysis with both data sources |
| 5-6 | Environmental Production | Deploy Environmental Analysis with real data integration |
| 6-7 | Live Preview Testing | Test Live Preview with both data sources |
| 7 | Live Preview Production | Deploy Live Preview with real data integration |
| 8 | Cleanup | Remove placeholder data and transition code |

This transition approach ensures that at each stage, we have a fallback option if integration issues are discovered, while minimizing disruption to users and allowing for incremental improvements.

## Technical Implementation Example: Key Metrics Panel Integration

To illustrate the integration process, here's a detailed example of integrating the Key Metrics Panel with real TCO model data:

### 1. Current Placeholder Implementation

The current implementation in `ui/results/metrics.py` uses placeholder data:

```python
def render_key_metrics_panel(results, comparison):
    """
    Render an interactive key metrics panel with insights
    
    Args:
        results: Dictionary of TCO result objects (currently using placeholder data)
        comparison: Comparison result object (currently using placeholder data)
    """
    # Get results for each vehicle
    result1 = results["vehicle_1"]
    result2 = results["vehicle_2"]
    
    # Format metrics
    total_tco_1 = format_currency(result1.total_tco)
    total_tco_2 = format_currency(result2.total_tco)
    lcod_1 = f"{format_currency(result1.lcod)}/km"
    lcod_2 = f"{format_currency(result2.lcod)}/km"
    
    # Determine which vehicle is cheaper
    cheaper_vehicle = result1.vehicle_name if comparison.cheaper_option == 1 else result2.vehicle_name
    saving_amount = format_currency(abs(comparison.tco_difference))
    saving_percent = f"{abs(comparison.tco_percentage):.1f}%"
    
    # Calculate payback information
    payback_info = get_payback_information(result1, result2, comparison)
    
    # Render metrics panel...
```

### 2. Integration Step 1: Data Adapter Function

Create adapter functions in `ui/results/data_adapters.py`:

```python
def adapt_tco_results_for_metrics(results: Dict[str, TCOOutput], 
                                comparison: ComparisonResult) -> Dict[str, Any]:
    """
    Adapt TCO results for the key metrics panel.
    
    Args:
        results: Dictionary with actual TCO model results
        comparison: Actual TCO model comparison result
        
    Returns:
        Formatted data for the metrics panel
    """
    # Extract vehicle 1 data
    vehicle_1 = {
        "name": results["vehicle_1"].vehicle_name,
        "total_tco": results["vehicle_1"].total_tco,
        "lcod": results["vehicle_1"].lcod,
        "annual_costs": results["vehicle_1"].annual_costs,
        "analysis_period": results["vehicle_1"].analysis_period_years,
        "lifetime_distance": results["vehicle_1"].lifetime_distance
    }
    
    # Extract vehicle 2 data
    vehicle_2 = {
        "name": results["vehicle_2"].vehicle_name,
        "total_tco": results["vehicle_2"].total_tco,
        "lcod": results["vehicle_2"].lcod,
        "annual_costs": results["vehicle_2"].annual_costs,
        "analysis_period": results["vehicle_2"].analysis_period_years,
        "lifetime_distance": results["vehicle_2"].lifetime_distance
    }
    
    # Extract comparison data
    comparison_data = {
        "tco_difference": comparison.tco_difference,
        "tco_percentage": comparison.tco_percentage,
        "lcod_difference": comparison.lcod_difference,
        "lcod_difference_percentage": comparison.lcod_difference_percentage,
        "cheaper_option": comparison.cheaper_option
    }
    
    # Calculate investment analysis if available
    investment_analysis = None
    if hasattr(comparison, "investment_analysis") and comparison.investment_analysis:
        investment_analysis = {
            "payback_years": comparison.investment_analysis.payback_years,
            "roi": comparison.investment_analysis.roi,
            "npv_difference": comparison.investment_analysis.npv_difference,
            "has_payback": comparison.investment_analysis.payback_years is not None
        }
    else:
        # Create placeholder investment analysis using existing data
        upfront_diff = abs(
            get_component_value(results["vehicle_1"], "acquisition") - 
            get_component_value(results["vehicle_2"], "acquisition")
        )
        annual_savings = 0
        for year in range(min(len(results["vehicle_1"].annual_costs), 
                            len(results["vehicle_2"].annual_costs))):
            annual_savings += (results["vehicle_2"].annual_costs[year] - 
                             results["vehicle_1"].annual_costs[year])
        
        # Only calculate payback if there are savings
        payback_years = None
        if annual_savings > 0 and upfront_diff > 0:
            payback_years = upfront_diff / (annual_savings / 
                                          results["vehicle_1"].analysis_period_years)
        
        # Only include payback if it occurs within analysis period
        if payback_years and payback_years <= results["vehicle_1"].analysis_period_years:
            roi = (annual_savings - upfront_diff) / upfront_diff * 100
            investment_analysis = {
                "payback_years": payback_years,
                "roi": roi,
                "npv_difference": comparison.tco_difference,
                "has_payback": True
            }
        else:
            investment_analysis = {
                "payback_years": None,
                "roi": None,
                "npv_difference": comparison.tco_difference,
                "has_payback": False
            }
    
    return {
        "vehicle_1": vehicle_1,
        "vehicle_2": vehicle_2,
        "comparison": comparison_data,
        "investment_analysis": investment_analysis
    }
```

### 3. Integration Step 2: Data Source Manager

Update the `ResultDataSource` class in `ui/results/data_source.py`:

```python
def get_metrics_data(self, results=None, comparison=None):
    """
    Get data for key metrics panel.
    
    Args:
        results: Dictionary of TCO result objects
        comparison: Comparison result object
        
    Returns:
        Dictionary with formatted data for metrics panel
    """
    from ui.feature_flags import get_feature_flag
    
    if get_feature_flag("use_real_metrics_data") and results and comparison:
        # Use real data
        from ui.results.data_adapters import adapt_tco_results_for_metrics
        return adapt_tco_results_for_metrics(results, comparison)
    else:
        # Use placeholder data
        from ui.results.placeholder_data import generate_metrics_placeholder
        return generate_metrics_placeholder()
```

### 4. Integration Step 3: Update Metrics Panel

Modify the `render_key_metrics_panel()` function to use the data adapter:

```python
def render_key_metrics_panel(results, comparison):
    """
    Render an interactive key metrics panel with insights
    
    Args:
        results: Dictionary of TCO result objects
        comparison: Comparison result object
    """
    # Get data through the data source
    from ui.results.data_source import ResultDataSource
    data_source = ResultDataSource()
    metrics_data = data_source.get_metrics_data(results, comparison)
    
    # Extract data for rendering
    vehicle_1 = metrics_data["vehicle_1"]
    vehicle_2 = metrics_data["vehicle_2"]
    comparison_data = metrics_data["comparison"]
    investment_analysis = metrics_data["investment_analysis"]
    
    # Format metrics for display
    total_tco_1 = format_currency(vehicle_1["total_tco"])
    total_tco_2 = format_currency(vehicle_2["total_tco"])
    lcod_1 = f"{format_currency(vehicle_1['lcod'])}/km"
    lcod_2 = f"{format_currency(vehicle_2['lcod'])}/km"
    
    # Determine which vehicle is cheaper
    cheaper_vehicle = vehicle_1["name"] if comparison_data["cheaper_option"] == 1 else vehicle_2["name"]
    saving_amount = format_currency(abs(comparison_data["tco_difference"]))
    saving_percent = f"{abs(comparison_data['tco_percentage']):.1f}%"
    
    # Rest of the function remains the same, but using the data from metrics_data
    # ...
```

### 5. Integration Step 4: Update Charts

Modify the chart creation functions to use the adapted data:

```python
def create_tco_comparison_visualization(metrics_data):
    """
    Create TCO comparison visualization using the adapted data.
    
    Args:
        metrics_data: Dictionary with metrics data from data adapter
        
    Returns:
        Plotly figure object
    """
    # Extract data
    vehicle_1 = metrics_data["vehicle_1"]
    vehicle_2 = metrics_data["vehicle_2"]
    comparison = metrics_data["comparison"]
    
    # Create visualization using the data
    # ...
```

### 6. Integration Step 5: Testing Logic

Add test functions to verify the integration:

```python
def test_metrics_data_integration():
    """Test that TCO model data is correctly integrated with metrics panel."""
    # Create test TCO results
    from tco_model.calculator import TCOCalculator
    from tco_model.models import ScenarioInput
    
    calculator = TCOCalculator()
    
    # Create test scenarios
    scenario1 = ScenarioInput(
        vehicle_type="BET",
        name="Test BET",
        # Other parameters...
    )
    
    scenario2 = ScenarioInput(
        vehicle_type="diesel",
        name="Test Diesel",
        # Other parameters...
    )
    
    # Calculate results
    result1 = calculator.calculate(scenario1)
    result2 = calculator.calculate(scenario2)
    comparison = calculator.compare(result1, result2)
    
    results = {
        "vehicle_1": result1,
        "vehicle_2": result2
    }
    
    # Adapt data
    from ui.results.data_adapters import adapt_tco_results_for_metrics
    metrics_data = adapt_tco_results_for_metrics(results, comparison)
    
    # Verify data structure
    assert "vehicle_1" in metrics_data
    assert "vehicle_2" in metrics_data
    assert "comparison" in metrics_data
    assert "investment_analysis" in metrics_data
    
    # Verify specific data points
    assert metrics_data["vehicle_1"]["name"] == "Test BET"
    assert metrics_data["vehicle_2"]["name"] == "Test Diesel"
    assert "tco_difference" in metrics_data["comparison"]
    
    # Test rendering
    # ...
```

### 7. Integration Step 6: Feature Flag Management

Add a UI for managing feature flags during development:

```python
def render_dev_feature_flags():
    """Render developer feature flag controls (only in development mode)."""
    import streamlit as st
    from ui.feature_flags import FeatureFlags
    
    if st.session_state.get("dev_mode", False):
        st.sidebar.markdown("## Developer Controls")
        
        # Get feature flags instance
        flags = FeatureFlags()
        
        # Create toggles for each flag
        st.sidebar.markdown("### Feature Flags")
        
        for flag_name in flags.flags:
            current_value = flags.get_flag(flag_name)
            new_value = st.sidebar.checkbox(
                flag_name,
                value=current_value,
                key=f"dev_flag_{flag_name}"
            )
            
            if new_value != current_value:
                flags.set_flag(flag_name, new_value)
        
        # Quick toggle buttons
        col1, col2 = st.sidebar.columns(2)
        
        with col1:
            if st.button("All Real Data"):
                flags.enable_all_real_data()
                st.experimental_rerun()
        
        with col2:
            if st.button("All Placeholder"):
                flags.disable_all_real_data()
                st.experimental_rerun()
```

### 8. Integration Step 7: Error Handling

Add error handling to gracefully fall back to placeholder data:

```python
def get_metrics_data_with_fallback(results=None, comparison=None):
    """
    Get metrics data with fallback to placeholder data if real data fails.
    
    Args:
        results: Dictionary of TCO result objects
        comparison: Comparison result object
        
    Returns:
        Dictionary with metrics data
    """
    from ui.feature_flags import get_feature_flag
    
    if get_feature_flag("use_real_metrics_data") and results and comparison:
        try:
            # Try to use real data
            from ui.results.data_adapters import adapt_tco_results_for_metrics
            return adapt_tco_results_for_metrics(results, comparison)
        except Exception as e:
            # Log the error
            import logging
            logging.error(f"Error using real metrics data: {str(e)}")
            
            # Fall back to placeholder data
            from ui.results.placeholder_data import generate_metrics_placeholder
            return generate_metrics_placeholder()
    else:
        # Use placeholder data
        from ui.results.placeholder_data import generate_metrics_placeholder
        return generate_metrics_placeholder()
```

### 9. Integration Step 8: Gradual Rollout

Update the application initialization to gradually enable features:

```python
def initialize_app():
    """Initialize the application with appropriate feature flags."""
    import streamlit as st
    from ui.feature_flags import FeatureFlags
    
    # Initialize feature flags
    if "feature_flags" not in st.session_state:
        flags = FeatureFlags()
        
        # Start with just metrics panel using real data
        flags.set_flag("use_real_metrics_data", True)
        
        # Store in session state
        st.session_state["feature_flags"] = flags
```

This technical implementation example illustrates the step-by-step approach to integrating one component (Key Metrics Panel) with real data from the TCO model. The same pattern can be applied to each component, following the phased integration approach outlined in the transition plan.

## File Structure of Implemented Components

The following shows the file structure with implementation status:

```
ui/
├── layout.py                        [IMPLEMENTED - Needs integration]
├── sidebar.py                       [UPDATED - Needs integration]
├── results/
│   ├── display.py                   [UPDATED - Needs integration]
│   ├── metrics.py                   [IMPLEMENTED - Needs integration]
│   ├── dashboard.py                 [IMPLEMENTED - Needs integration]
│   ├── environmental.py             [IMPLEMENTED - Needs integration]
│   ├── live_preview.py              [IMPLEMENTED - Needs integration]
│   ├── charts.py                    [EXISTING - Needs enhancement]
│   ├── utils.py                     [UPDATED - Needs integration]
│   ├── detailed.py                  [EXISTING - Needs updates]
│   └── summary.py                   [EXISTING - Needs updates]
├── inputs/                          [EXISTING - No changes needed]
└── progressive_disclosure.py        [EXISTING - No changes needed]

tco_model/                           [NEEDS ENHANCEMENT]
├── calculator.py                    [Needs extension]
├── models.py                        [Needs extension]
├── terminology.py                   [Exists]
└── other model files...             [Exist]
```

## Implementation Details by File

### tco_model/calculator.py
1. Add methods for emissions calculation
2. Implement sensitivity analysis
3. Enhance component breakdown methods
4. Add investment analysis functions

```python
class TCOCalculator:
    # Existing methods...
    
    def calculate_emissions(self, result: TCOOutput) -> Dict[str, Any]:
        """Calculate emissions data for a TCO result."""
        # Implementation...
    
    def perform_sensitivity_analysis(self, scenario: ScenarioInput, 
                                   parameter: str, variation: float) -> Dict[str, Any]:
        """Perform sensitivity analysis for a given parameter."""
        # Implementation...
    
    def calculate_component_breakdown(self, result: TCOOutput) -> Dict[str, Dict[str, float]]:
        """Calculate detailed component breakdown."""
        # Implementation...
    
    def analyze_investment(self, result1: TCOOutput, result2: TCOOutput) -> Dict[str, Any]:
        """Perform investment analysis between two vehicles."""
        # Implementation...
```

### tco_model/models.py
1. Enhance TCOOutput with emissions data
2. Add sensitivity analysis result structures
3. Enhance ComparisonResult with investment metrics

```python
@dataclass
class EmissionsData:
    """Emissions data for a vehicle."""
    annual_co2_tonnes: List[float]
    total_co2_tonnes: float
    energy_consumption_kwh: float
    # Other emissions metrics...

@dataclass
class TCOOutput:
    # Existing fields...
    emissions: Optional[EmissionsData] = None
    
@dataclass
class SensitivityResult:
    """Result of a sensitivity analysis."""
    parameter: str
    variations: List[float]
    tco_values: List[float]
    lcod_values: List[float]
    # Other sensitivity metrics...

@dataclass
class InvestmentAnalysis:
    """Investment analysis between two vehicles."""
    payback_years: Optional[float]
    roi: Optional[float]
    npv_difference: float
    # Other investment metrics...

@dataclass
class ComparisonResult:
    # Existing fields...
    investment_analysis: Optional[InvestmentAnalysis] = None
```

### ui/results/dashboard.py
1. Connect to TCO model data
2. Remove placeholder implementations
3. Enhance analysis functions

```python
def render_cost_breakdown(results: Dict[str, TCOOutput], comparison: ComparisonResult):
    """Render cost breakdown analysis from actual model data."""
    # Real implementation using model data...
    
def render_annual_timeline(results: Dict[str, TCOOutput], comparison: ComparisonResult):
    """Render annual timeline using actual annual costs from model."""
    # Real implementation using model data...
```

### ui/results/environmental.py
1. Connect to TCO emissions data
2. Remove placeholder implementations
3. Implement actual environmental calculations

```python
def render_environmental_impact(results: Dict[str, TCOOutput]):
    """Render environmental impact using actual emissions data from model."""
    # Real implementation using emissions data from model...
    
def calculate_emissions_data(result1: TCOOutput, result2: TCOOutput) -> Dict[str, Any]:
    """Use actual emissions data from TCO model."""
    return {
        "annual_co2_vehicle_1": result1.emissions.annual_co2_tonnes,
        "annual_co2_vehicle_2": result2.emissions.annual_co2_tonnes,
        "total_co2_vehicle_1": result1.emissions.total_co2_tonnes,
        "total_co2_vehicle_2": result2.emissions.total_co2_tonnes,
        # Other actual emissions data...
    }
```

### ui/results/metrics.py
1. Connect to TCO model data
2. Generate insights from actual results
3. Use real payback and investment data

```python
def render_key_metrics_panel(results, comparison):
    """
    Render an interactive key metrics panel with insights
    
    Args:
        results: Dictionary of TCO result objects
        comparison: Comparison result object
    """
    # Get data through the data source
    from ui.results.data_source import ResultDataSource
    data_source = ResultDataSource()
    metrics_data = data_source.get_metrics_data(results, comparison)
    
    # Extract data for rendering
    vehicle_1 = metrics_data["vehicle_1"]
    vehicle_2 = metrics_data["vehicle_2"]
    comparison_data = metrics_data["comparison"]
    investment_analysis = metrics_data["investment_analysis"]
    
    # Format metrics for display
    total_tco_1 = format_currency(vehicle_1["total_tco"])
    total_tco_2 = format_currency(vehicle_2["total_tco"])
    lcod_1 = f"{format_currency(vehicle_1['lcod'])}/km"
    lcod_2 = f"{format_currency(vehicle_2['lcod'])}/km"
    
    # Determine which vehicle is cheaper
    cheaper_vehicle = vehicle_1["name"] if comparison_data["cheaper_option"] == 1 else vehicle_2["name"]
    saving_amount = format_currency(abs(comparison_data["tco_difference"]))
    saving_percent = f"{abs(comparison_data['tco_percentage']):.1f}%"
    
    # Rest of the function remains the same, but using the data from metrics_data
    # ...
```

### ui/results/live_preview.py
1. Connect to sensitivity analysis engine
2. Replace placeholder parameter impact analysis
3. Use actual model data for all visualisations

```python
def show_parameter_impact(parameter: str, results: Dict[str, TCOOutput], 
                         comparison: ComparisonResult):
    """Show parameter impact using actual sensitivity analysis."""
    # Get calculator instance
    from tco_model.calculator import TCOCalculator
    calculator = TCOCalculator()
    
    # Get parameters and perform analysis
    scenario1 = results["vehicle_1"].scenario
    scenario2 = results["vehicle_2"].scenario
    
    # Display actual sensitivity results
    # ...
```

## Integration Approach

To properly integrate the UI components with the TCO model:

1. **Start with Model Extensions**
   - First implement all model enhancements in `tco_model/`
   - Test each extension independently before UI integration
   - Ensure data structures align with UI expectations

2. **Use Progressive Integration**
   - Integrate one component at a time, starting with core metrics
   - Test each integration before moving to the next component
   - Keep the current UI functioning while integrating new components

3. **Refactor UI Components as Needed**
   - Adjust UI components to match actual model data structures
   - Ensure consistent data access patterns throughout the application
   - Update visualisations to work with real data formats

4. **Maintain Clear Interfaces**
   - Define clear interfaces between the model and UI
   - Create utility functions for common data transformations
   - Document data flow patterns for future maintenance

## Implementation Timeline

1. **Stage 1 (TCO Model Enhancement)**: 2 weeks
   - Focus on extending the model first to expose all required data

2. **Stage 2 (UI Integration)**: 2 weeks
   - Replace all placeholder implementations with actual model integrations

3. **Stage 3 (Export and Data Sharing)**: 1 week
   - Enhance report generation and data management

4. **Stage 4 (User Experience Enhancement)**: 1 week
   - Refine layouts and optimise performance

5. **Stage 5 (Testing and Documentation)**: 1 week
   - Ensure quality and provide proper documentation

Total estimated timeline: 7 weeks

## Success Criteria

The implementation will be considered successful when:

1. All placeholder/dummy data implementations are removed
2. All visualisations use actual TCO model data
3. Sensitivity analysis works with real-time recalculation
4. Environmental impact analysis uses actual emissions data
5. Side-by-side layout provides immediate accurate feedback
6. Reports and exports contain comprehensive model data
7. All components perform efficiently with large datasets
8. Complete documentation and tests are in place

## Risks and Mitigation

1. **Risk**: TCO model may not expose all required data
   - **Mitigation**: Start with model enhancement first, align data structures

2. **Risk**: Performance issues with complex visualisations
   - **Mitigation**: Implement progressive loading and data caching

3. **Risk**: Integration complexity between UI and model
   - **Mitigation**: Create clear data access patterns and transformation utilities

4. **Risk**: Excessive dependencies between components
   - **Mitigation**: Establish modular architecture with clear interfaces

5. **Risk**: Scope creep during implementation
   - **Mitigation**: Prioritise core functionality first, add enhancements later 