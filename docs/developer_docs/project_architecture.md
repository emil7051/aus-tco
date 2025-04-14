#Australian Heavy Vehicle TCO Modeller - Project Documentation
- Version: 1.0
- Date: 2025-04-12

##1. Introduction

###1.1. Purpose
This document provides a comprehensive guide for the development and architecture of the Australian Heavy Vehicle Total Cost of Ownership (TCO) Modeller. It serves as the primary reference for developers, outlining the project's goals, features, technical design, implementation strategy, and best practices.

###1.2. Project Goal
To develop a robust, user-friendly, and extensible web application using Python and Streamlit that allows users to accurately model and compare the TCO of different heavy vehicle types (initially Battery Electric Trucks (BETs) and Internal Combustion Engine (ICE) diesel trucks) within the specific economic and operational context of Australia.

###1.3. Target Audience
Policymakers, transport industry analysts, researchers, vehicle manufacturers, and energy providers.

##2. Key Features
The TCO Modeller will offer the following core functionalities:

    * Scenario Definition: Allow users to define detailed operational and economic scenarios, including:
    * Vehicle parameters (type, purchase price, payload, efficiency, etc.)
    * Operational parameters (annual distance, operating days, lifespan)
    * Economic parameters (discount rate, inflation, energy prices, carbon tax)
    * Financing options (loan terms, interest rates, or cash purchase)
    * Infrastructure costs (charging installation, upgrades)
    * Vehicle Comparison: Enable side-by-side comparison of TCO for at least two vehicles (e.g., BET vs. ICE).
    * Detailed Cost Breakdown: Provide a year-by-year breakdown of all relevant cost components:
    * Acquisition Costs (including purchase price, subsidies, financing)
    * Energy Costs (diesel, electricity, including demand charges)
    * Maintenance & Repair Costs
    * Charging/Refuelling Infrastructure Costs
    * Battery Replacement Costs (for BETs)
    * Insurance & Registration
    * Taxes & Levies (Carbon Tax, Road User Charges)
    * Residual Value (as a negative cost/income at end-of-life)
    * TCO Calculation: Calculate the Net Present Value (NPV) of the TCO over the specified analysis period (15 years)
    * Key Metrics: Calculate and display relevant metrics like Levelized Cost of Driving (LCOD) in AUD/km.
    * Interactive Visualizations: Present results using clear and interactive charts (e.g., cumulative TCO, annual cost breakdown, cost component comparison) via Plotly.
    * Interactive User Guide: Provide comprehensive documentation, tooltips, and example scenarios to help users understand both how to use the tool and interpret the results.
    * Sensitivity Analysis/Simulations: Allow users to vary key parameters (e.g., energy price, discount rate) to see the impact on TCO results.
    * Data Export (Future Goal): Enable users to export scenario inputs and calculated results (e.g., to CSV or Excel).
    * Example Scenarios: Provide pre-configured default parameters for common Australian heavy vehicle types, operational contexts, and use cases (urban delivery, regional distribution, etc.).

##3. Architecture Overview

###3.1. High-Level Design

The application follows a modular, layered architecture to promote separation of concerns, testability, and maintainability.
+---------------------+      +-----------------------+      +---------------------+
|    Streamlit UI     | ---> | Controller / Services | ---> | TCO Model & Engine  |
| (ui/ modules)       |      | (app.py / ui helpers) |      | (tco_model/ modules)|
+---------------------+      +-----------------------+      +---------------------+
       |                                                           |
       | Loads/Displays                                            | Uses
       V                                                           V
+---------------------+                                   +---------------------+
| Pydantic Data Models| <---------------------------------| Configuration Files |
| (tco_model.models)  |                                   | (config/ *.yaml)    |
+---------------------+                                   +---------------------+

    * Presentation Layer (Streamlit UI): Handles user interaction, displays inputs and outputs. Built   using Streamlit widgets and organised into modules within the ui/ directory.
    * Controller/Service Layer: Acts as an intermediary between the UI and the core model. Resides partly in app.py and potentially helper functions called by UI modules. Manages application state (st.session_state) and orchestrates calls to the TCO calculation engine.
    * Core Model Layer (TCO Model & Engine): Contains the business logic, calculation engine, data structures, and strategy implementations. Resides within the tco_model/ directory. This layer is designed to be independent of the Streamlit UI.
    * Data Models (Pydantic): Defines the structure, types, and validation rules for all data used in the application (inputs, configurations, outputs). Located in tco_model/models.py.
    * Configuration: External files (YAML) defining default parameters, vehicle specifications, and potentially environment-specific settings. Managed via Pydantic BaseSettings.

###3.2. Technology Stack

    * Language: Python 3.9+
    * Web Framework: Streamlit
    * Data Validation & Settings: Pydantic V2
    * Numerical Computation: Pandas, NumPy, NumPy-Financial
    * Plotting: Plotly
    * Configuration Files: YAML
    * Testing: Pytest
    * Dependency Management: Poetry (Recommended) or PDM

###3.3. Project Structure

aus-heavy-vehicle-tco/
├── .env                  # Environment variables (for Pydantic BaseSettings)
├── .gitignore
├── app.py                # Main Streamlit application entry point, controller logic
├── pyproject.toml        # Project metadata and dependencies (Poetry/PDM)
├── README.md
├── config/               # Configuration files
│   ├── defaults/
│   │   ├── economic_parameters.yaml
│   │   └── operational_parameters.yaml
│   └── vehicles/
│       ├── default_bet.yaml
│       ├── default_ice.yaml
│       ├── default_bet_urban.yaml      # Urban delivery BET configuration
│       ├── default_ice_urban.yaml      # Urban delivery diesel configuration
│       ├── default_bet_regional.yaml   # Regional distribution BET configuration
│       ├── default_ice_regional.yaml   # Regional distribution diesel configuration
│       ├── default_bet_longhaul.yaml   # Long-haul BET configuration (planned)
│       ├── default_ice_longhaul.yaml   # Long-haul diesel configuration (planned)
│       ├── default_bet_financed.yaml   # Financing example - loan (planned)
│       └── default_bet_cash.yaml       # Financing example - cash purchase (planned)
├── tco_model/            # Core TCO calculation logic and data models
│   ├── __init__.py
│   ├── calculator.py     # Main TCO calculation engine
│   ├── models.py         # Pydantic models for inputs, outputs, configs
│   ├── strategies.py     # Calculation strategies (Energy, Maintenance, etc.)
│   ├── costs.py          # Functions for calculating individual cost components
│   └── vehicles.py       # Vehicle-specific data loading/handling
├── ui/                   # Streamlit UI modules/components
│   ├── __init__.py
│   ├── guide.py          # Interactive user guide, tooltips, and tutorials
│   ├── inputs/           # Input UI modules
│   │   ├── __init__.py
│   │   ├── vehicle.py    # Vehicle parameters input UI
│   │   ├── operational.py # Operational parameters input UI
│   │   ├── economic.py   # Economic parameters input UI
│   │   └── financing.py  # Financing parameters input UI
│   ├── results/          # Results display modules
│   │   ├── __init__.py
│   │   ├── summary.py    # Summary tables and key metrics
│   │   ├── charts.py     # Interactive visualizations
│   │   ├── detailed.py   # Detailed results breakdown
│   │   ├── display.py    # Helper functions for results display
│   │   └── utils.py      # Result formatting utilities
│   └── sidebar.py        # Sidebar configuration/elements
├── utils/                # Utility functions (e.g., data loading, formatting)
│   ├── __init__.py
│   └── helpers.py
└── tests/                # Automated tests
   ├── __init__.py
   ├── fixtures/         # Test data/fixtures
   ├── unit/             # Unit tests for individual functions/classes
   └── integration/      # Integration tests for component interactions

##4. Core Components Deep Dive

###4.1. Pydantic Models (tco_model/models.py)

Purpose: Define all data structures, enforce type hints, and perform validation. Ensures data integrity throughout the application.

    * Key Models:
        * VehicleParameters: Defines attributes specific to a vehicle (price, efficiency, battery capacity, etc.). Nested models for components like Battery.
        * OperationalParameters: Annual distance, operating days, analysis period, payload.
        * EconomicParameters: Discount rate, inflation, energy prices (potentially nested model for year-on-year variations), carbon tax.
        * FinancingOptions: Loan terms, interest rate, deposit percentage.
        * InfrastructureParameters: Charger cost, installation cost, grid upgrade cost.
        * ScenarioInput: Top-level model aggregating all user inputs for a single vehicle scenario (contains instances of the above models).
        * TCOOutput: Structure for storing calculated results (annual breakdowns, totals, NPV, LCOD). Use Pandas DataFrames internally where appropriate for time-series data, but define the structure clearly.
        * AppSettings (inheriting from Pydantic BaseSettings): Model for loading application settings from .env or environment variables.
        * VehicleConfig, EconomicConfig, etc.: Models for loading default parameters from YAML files.

    * Best Practices: Use descriptive names, leverage Field for validation rules (min/max values, descriptions), use NewType for specific units (e.g., AUD, kWh_per_km), define specific models for projections (e.g., EnergyPriceProjection) instead of generic Dict or List[float].

###4.2. TCO Calculator (tco_model/calculator.py)

Purpose: Orchestrates the TCO calculation process. Takes validated ScenarioInput data and produces TCOOutput.

* Logic:
   1. Initialize cost components based on input parameters.
   2. Iterate through each year of the analysis period.
   3. For each year, calculate individual cost components using functions from tco_model.costs.py and selected strategies from tco_model.strategies.py.
   4. Account for inflation where applicable.
   5. Calculate annual totals.
   6. After iterating through all years, calculate the Net Present Value (NPV) of each cost component and the total TCO using numpy-financial.
   7. Calculate LCOD.
   8. Package results into the TCOOutput model.

* Implementation: Use Pandas DataFrames for managing year-by-year calculations where vectorization benefits performance. Implement clear error handling. Consider caching (@functools.lru_cache or Streamlit caching) for pure calculation functions if performance becomes an issue.

###4.3. Cost Components & Strategies (tco_model/costs.py, tco_model/strategies.py)

Purpose: Encapsulate the logic for calculating each specific cost component (Energy, Maintenance, etc.). The Strategy Pattern allows for interchangeable calculation methods.

    * costs.py: Contains functions calculating costs that don't typically require complex strategies (e.g., Insurance, Registration based on simple inputs).
    * strategies.py:
     * Define base abstract classes (e.g., EnergyConsumptionStrategy, MaintenanceStrategy) using abc.ABC.
     * Implement concrete strategies (e.g., BasicDieselConsumption, BETEnergyConsumptionWithDemandCharge, DistanceBasedMaintenance, AgeBasedMaintenance).
    * The TCOCalculator will select and use the appropriate strategy based on vehicle type or user selection.

###4.4. UI Modules (ui/)

Purpose: Render Streamlit widgets for inputs and display results.
    * Structure: Break down the UI into logical sections (e.g., ui/inputs/vehicle.py, ui/inputs/economic.py, ui/results/summary.py, ui/results/charts.py).
    * Interaction:
        * UI modules read default/current values from st.session_state.
        * Widgets update st.session_state using unique keys (following a structured naming convention, e.g., vehicle_1.parameters.purchase_price) and potentially on_change callbacks.
        * Buttons trigger calculations by calling functions (likely defined in app.py or helper modules) that retrieve data from st.session_state, pass it to the TCOCalculator, and store the results back in st.session_state.
        * Result modules read output data from st.session_state and render tables/charts.

    * Best Practices: Use st.form for related inputs to batch updates. Employ st.tabs or st.expander to organize inputs logically. Provide clear labels and help text for all widgets. Use st.spinner during calculations. Display user-friendly error messages.

###4.5. Configuration Management (config/, tco_model/models.py)

Purpose: Manage default values, vehicle specifications, and application settings.
    * Mechanism:
        1. Use Pydantic BaseSettings in tco_model.models.py to define application settings (e.g., logging level, API keys if needed) loadable from .env or environment variables.
        2. Define Pydantic models corresponding to the structure of YAML files in config/ (e.g., VehicleConfig, EconomicConfig).
        3. Use a utility function (utils/helpers.py) to load YAML files into these Pydantic models, performing validation.
        4. The application loads these defaults when initializing or when the user selects a default vehicle/scenario.

###4.6. State Management (app.py, ui/)

Challenge: Streamlit reruns the entire script on interaction. State must be preserved explicitly.

* Strategy:
   1. Initialize st.session_state on the first run with default structures (e.g., nested dictionaries mirroring ScenarioInput for each vehicle being compared, plus a key for results).

# Example initialization in app.py
if 'initialized' not in st.session_state:
   st.session_state.initialized = True
   st.session_state.vehicle_1_input = load_default_scenario('default_bet') # Returns ScenarioInput model
   st.session_state.vehicle_2_input = load_default_scenario('default_ice') # Returns ScenarioInput model
   st.session_state.results = None

   2. Use consistent, structured keys for all widgets accessing state (e.g., f"vehicle_{n}_input.operational.annual_km").

   3. Use on_change callbacks attached to widgets to trigger specific state update logic or validation functions, rather than relying solely on the script rerun.

   4. Develop utility functions to safely get/set potentially nested values within st.session_state to avoid KeyError.

###4.7. Interactive User Guide (ui/guide.py)

Purpose: Provide comprehensive documentation, tooltips, and example scenarios to help users understand the tool and interpret results.

* Components:
   1. Main Guide Content: Structured into tabs covering getting started, example scenarios, step-by-step tutorials, and results interpretation.
   2. Example Scenarios: Predefined configurations demonstrating different use cases:
      * Urban Delivery: Short-haul operations with frequent stops and lower daily distances
      * Regional Distribution: Medium-haul routes between regional centers
      * Long-Haul Transport: Long-distance interstate transport operations
      * Financing Options Comparison: Different financing methods for the same vehicle type
   3. Tooltips System: Contextual help for input fields, providing definitions and explanations without cluttering the UI
   4. Step-by-Step Tutorial: Walkthrough explaining how to use each section of the application

* Implementation: 
   * Modular design with separate rendering functions for each guide section
   * Example scenarios linked to vehicle configuration files in config/vehicles/
   * Tooltips accessible via a dictionary mapping field keys to help text
   * Tutorial steps structured as expandable sections with visual indicators

* Integration: 
   * Guide accessible via a dedicated tab in the main application
   * Tooltips integrated with input fields across the UI
   * Example scenarios loadable via buttons that update the application state

##5. Testing Strategy (tests/)
   * Framework: pytest
   * Unit Tests (tests/unit/):
        * Test Pydantic model validation (valid and invalid data).
        * Test individual cost calculation functions (tco_model/costs.py).
        * Test strategy implementations (tco_model/strategies.py).
        * Test utility functions (utils/helpers.py).
        * Generate test cases for validation rules and calculation logic edge cases.

   * Integration Tests (tests/integration/):
        * Test the main TCOCalculator with sample ScenarioInput data, verifying the overall TCOOutput structure and key values.
        * Test the interaction between different cost components and strategies.
        * Test configuration loading and default scenario instantiation.
        * Data Validation Tests: Include tests that load all YAML configuration files to ensure they parse correctly and conform to their Pydantic models.
    
    * E2E Tests: Use tools like pytest-playwright or streamlit-E2E-testing for basic checks of the UI flow (e.g., ensuring inputs exist, calculation button works, results appear). These are more brittle with Streamlit.
   
   * Fixtures (tests/fixtures/): Use pytest fixtures to provide reusable test data (e.g., sample ScenarioInput objects, mock configuration data).

6. Deployment
   * Streamlit Community Cloud: Easiest for public-facing apps. Requires code on GitHub. Manage secrets via Streamlit interface.
   * Configuration: Use environment variables for sensitive data or deployment-specific settings, loaded via Pydantic BaseSettings.

7. Implementation Guidance & Roadmap
This provides a high-level plan, incorporating best practices and leveraging AI assistance.

Phase 1: Foundation & Core Models (Est. 3-5 days)
   1. Setup Project: Initialize project structure, Git repository, pyproject.toml (using Poetry/PDM), virtual environment. Install initial dependencies. (AI: Can generate .gitignore, basic pyproject.toml).
   2. Define Core Pydantic Models: Implement all models in tco_model/models.py (Inputs, Configs, Outputs, Settings). Focus on structure, types, and basic validation. (AI: Generate models based on specifications, add docstrings).
   3. Setup Configuration: Create initial YAML files in config/ and implement loading/validation logic using Pydantic models and utility functions. Implement BaseSettings for environment variables.
   4. Basic App Skeleton: Create app.py with basic Streamlit title and structure. Implement initial st.session_state setup.
   5. Unit Testing Setup: Configure pytest. Write initial unit tests for Pydantic models and config loading. (AI: Generate basic test structures and validation test cases).

Phase 2: TCO Calculation Engine (Est. 4-6 days)
   1. Implement Cost Functions: Develop core calculation functions in tco_model/costs.py for simpler components.
   2. Implement Strategy Pattern: Define base strategy classes and initial concrete strategies in tco_model/strategies.py.
   3. Build TCOCalculator: Implement the main calculation logic in tco_model/calculator.py, integrating cost functions and strategies. Focus on generating the year-by-year breakdown and NPV totals. Use Pandas where appropriate.
   4. Testing: Write comprehensive unit tests for cost functions, strategies, and integration tests for the TCOCalculator. (AI: Generate test cases for calculations, edge cases, strategy variations).

Phase 3: Streamlit UI - Inputs (Est. 3-5 days)
   1. Develop Input Modules: Create UI modules in ui/inputs/ for each section (Vehicle, Operational, Economic, etc.).
   2. Connect UI to State: Use structured keys to link Streamlit widgets to the corresponding fields in the ScenarioInput models stored in st.session_state.
   3. Implement State Updates: Use on_change callbacks and forms (st.form) for robust state handling. Implement logic to load default scenarios into the state.
   4. Refine State Management: Develop utility functions for safe state access. Ensure state structure is logical.
   5. Testing (Manual/Optional E2E): Manually test input interactions. Implement basic E2E checks if desired. (AI: Generate boilerplate Streamlit widget code based on Pydantic models).

Phase 4: Streamlit UI - Results & Visualization (Est. 3-4 days)
   1. Trigger Calculation: Implement the "Calculate TCO" button logic in app.py or helpers, calling the TCOCalculator and storing results in st.session_state. Add user feedback (st.spinner).
   2. Develop Results Modules: Create UI modules in ui/results/ to display tabular data (annual breakdowns, summary) and Plotly charts (TCO comparison, cost components).
   3. Refine Visualizations: Ensure charts are clear, well-labelled, interactive, and effectively communicate insights.
   4. Error Handling: Implement user-friendly display of validation or calculation errors.

Phase 5: Refinement, Documentation & Deployment (Est. 2-4 days)
   1. Code Review & Refactoring: Review code for clarity, consistency, and performance. Refactor where needed. (AI: Suggest refactoring improvements, identify potential bugs).
   2. Documentation: Write comprehensive docstrings for all functions and classes. Update README.md with setup, usage, and contribution guidelines. (AI: Generate docstrings, summarize modules).
   3. Final Testing: Perform thorough manual testing of all features and edge cases. Ensure all automated tests pass.
   4. Deployment: Choose a deployment method, create Dockerfile if needed, configure environment variables, and deploy.

AI Integration Notes (Cursor/LLMs)
   * Prompting: Provide clear context, including relevant Pydantic models, existing code snippets, and specific requirements.
   * Code Generation: Use for boilerplate (models, UI widgets, test structures), standard algorithms (e.g., simple file I/O), and implementing well-defined functions based on docstrings/specs.
   * Refactoring & Optimization: Ask for suggestions to improve code structure, apply patterns (like simplifying state access), or optimize calculations (e.g., vectorization).
   * Debugging: Paste error messages and relevant code snippets to get explanations and potential fixes.
   * Documentation: Generate docstrings and README sections, but always review and refine for accuracy and clarity.
   * Testing: Generate test cases, especially for edge conditions and validation rules.

This detailed documentation should provide a strong foundation for rebuilding the TCO modeller effectively. Remember to keep it updated as the project evolves.


Naming Conventions
General Naming Conventions

Files and Directories: Use lowercase with underscores for spaces (snake_case)

Examples: economic_parameters.yaml, models.py, tco_model/


Classes: Use PascalCase (CapitalizedWords)

Examples: BETParameters, EconomicParameters, ScenarioInput


Functions and Variables: Use snake_case

Examples: load_yaml_file(), discount_rate_real, annual_distance_km


Constants: Use UPPER_SNAKE_CASE

Not currently used in the codebase



Specific Naming Patterns
Pydantic Models

Parameter Models: Use suffix Parameters for models representing input parameters

Examples: BatteryParameters, OperationalParameters, FinancingParameters


Output Models: Use descriptive names for output models

Examples: TCOOutput, AnnualCosts, NPVCosts, ComparisonResult


Utility Models: Use descriptive names for utility models

Examples: RangeValue, YearlyValue



Configuration Files

Default Config Files: Use descriptive names with parameters suffix

Examples: economic_parameters.yaml, operational_parameters.yaml


Vehicle Config Files: Use prefix default_ followed by vehicle type abbreviation

Examples: default_bet.yaml, default_ice.yaml



Functions

Loader Functions: Use prefix load_ for functions that load data

Examples: load_yaml_file(), load_economic_parameters(), load_default_scenario()


Format Functions: Use prefix format_ for functions that format data for display

Examples: format_currency(), format_percentage()

Calculator Functions: Use prefix calculate_ for functions that compute values

Examples: calculate_consumption(), calculate_npv(), calculate_annual_cost()

Session State Keys

Vehicle Input Keys: Use pattern vehicle_N_input where N is the vehicle number

Examples: vehicle_1_input, vehicle_2_input

Nested State Access: Use dot notation for accessing nested state

Examples: vehicle_1.parameters.purchase_price, vehicle_1.operational.annual_km

Key Components
Pydantic Data Models (tco_model/models.py)
The models.py file contains a comprehensive set of Pydantic models that define the data structures, validation rules, and business logic for all components of the TCO modeller:

Utility Types and Enums

VehicleType: Enum for vehicle powertrain types (diesel, battery_electric)
VehicleCategory: Enum for vehicle categories (rigid, articulated)
ChargingStrategy: Enum for EV charging strategies
FinancingMethod: Enum for vehicle financing methods
ElectricityRateType: Enum for electricity rate structures
DieselPriceScenario: Enum for diesel price projection scenarios


Parameter Models

RangeValue: Represents values with min/max range and default
YearlyValue: Represents values that change by year with interpolation
BatteryParameters: Battery specifications and degradation modeling
EngineParameters: Diesel engine specifications
EnergyConsumptionParameters: Base class for energy consumption
BETConsumptionParameters: BET-specific energy consumption modeling
DieselConsumptionParameters: Diesel-specific fuel consumption modeling
ChargingParameters: Charging specifications and calculations
MaintenanceParameters: Maintenance cost modeling
InfrastructureParameters: Charging infrastructure costs
ResidualValueParameters: Residual value calculations
FinancingParameters: Financing options and calculations
EconomicParameters: Economic assumptions and NPV calculations
OperationalParameters: Vehicle operation parameters


Vehicle Models

VehicleBaseParameters: Common parameters for all vehicles
BETParameters: Battery Electric Truck specifications
DieselParameters: Diesel truck specifications


Input and Output Models

ScenarioInput: Top-level input model for TCO scenarios
AnnualCosts: Yearly cost breakdown structure
NPVCosts: Net Present Value of all cost components
TCOOutput: Complete TCO calculation results
ComparisonResult: Comparison between two TCO results


App Settings

AppSettings: Application configuration using Pydantic's BaseSettings



Configuration Management (utils/helpers.py)
The helpers.py file provides utilities for loading and managing configuration:

YAML Loading

load_yaml_file(): Loads and parses YAML files
load_config_as_model(): Loads YAML into Pydantic models


Parameter Loading

load_economic_parameters(): Loads economic defaults
load_operational_parameters(): Loads operational defaults
load_financing_parameters(): Loads financing defaults
load_vehicle_parameters(): Loads vehicle parameters based on type
load_bet_parameters(): Loads BET-specific parameters
load_diesel_parameters(): Loads diesel-specific parameters
load_default_scenario(): Creates complete default scenarios


State Management

get_safe_state_value(): Safely accesses Streamlit session state with nested keys
set_safe_state_value(): Safely updates Streamlit session state with nested keys


Formatting Utilities

format_currency(): Formats values as Australian currency
format_percentage(): Formats decimal values as percentages


Config Discovery

find_available_vehicle_configs(): Finds available vehicle configurations



Configuration Files (config/)
The configuration files use YAML format with a consistent structure:

Economic Parameters (config/defaults/economic_parameters.yaml)

General economic parameters (discount rate, inflation, analysis period)
Financing options (loan terms, interest rates)
Energy prices (electricity, diesel) with time projections
Carbon pricing parameters


Operational Parameters (config/defaults/operational_parameters.yaml)

Annual mileage profiles for different operation types
Standard operational profiles (urban, regional, long-haul)
Infrastructure costs (chargers, installation, maintenance)
Insurance and registration costs
Residual value projections by vehicle type and age


Vehicle Parameters (config/vehicles/)

BET (default_bet.yaml)

Vehicle information (type, category, name)
Purchase price and price trends
Battery specifications (capacity, degradation)
Energy consumption parameters with adjustment factors
Charging specifications and strategies
Performance specifications
Maintenance cost structure
Reference to available models


Diesel (default_ice.yaml)

Vehicle information (type, category, name)
Purchase price and price trends
Engine specifications (power, emissions)
Fuel consumption parameters with adjustment factors
Refueling specifications
Performance specifications
Maintenance cost structure
Emissions data and carbon tax implications



Implementation Notes

Model Methods

Most models include calculation methods to encapsulate business logic
Examples: calculate_consumption(), capacity_at_year(), calculate_residual_value()


Validation and Defaults

Extensive use of Pydantic's validation features
Field validation ensures data consistency
Root validators set default values based on other fields


Interpolation and Projections

The YearlyValue class handles time-based interpolation of values
Supports both scalar and vector interpolation


Strategy Pattern

The architecture is designed to support the Strategy pattern for calculations
Different strategies can be implemented for energy consumption, maintenance, etc.


Streamlit Integration

State management helpers handle Streamlit's unique execution model
Safe access to nested state values enables a structured approach to UI state



