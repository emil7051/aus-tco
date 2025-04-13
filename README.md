# Australian Heavy Vehicle TCO Modeller

A Python-based web application for modelling and comparing the Total Cost of Ownership (TCO) of different heavy vehicle types in the Australian context.

## Overview

The Australian Heavy Vehicle TCO Modeller allows users to accurately model and compare the TCO of different heavy vehicle types (initially Battery Electric Trucks and Internal Combustion Engine diesel trucks) within the specific economic and operational context of Australia.

The application provides a user-friendly interface for defining detailed scenarios, comparing vehicles side-by-side, and visualizing the results through interactive charts and tables.

## Key Changes

We've recently standardized field names and component access patterns throughout the codebase. Key changes include:

- Renamed `npv_total` to `total_tco` for clarity
- Renamed `lcod_per_km` to `lcod` to follow naming conventions
- Added an `AnnualCostsCollection` class with improved access patterns
- Implemented a consistent strategy pattern with a factory
- Standardized component access across the codebase

See the [Migration Guide](docs/migration_guide.md) for details on transitioning to the new field names and the [Developer Guide](docs/developer_guide.md) for best practices.

## Key Features

- **Comprehensive TCO Modelling**: Calculate all relevant cost components over the vehicle's lifecycle, including acquisition, energy, maintenance, infrastructure, and more.
- **Vehicle Comparison**: Side-by-side comparison of TCO for different vehicle types.
- **Detailed Cost Breakdown**: Year-by-year breakdown of all cost components.
- **Interactive Visualizations**: Clear and interactive charts for analyzing TCO results.
- **Interactive User Guide**: Comprehensive documentation, tooltips, and example scenarios to help users understand how to use the tool and interpret results.
- **Flexible Scenario Definition**: Customize operational and economic parameters to match specific use cases.
- **Example Scenarios**: Pre-configured scenarios for common use cases such as urban delivery, regional distribution, and long-haul operations.

## Project Structure

```
aus-tco/
├── .env                  # Environment variables (for Pydantic BaseSettings)
├── .gitignore            # Git ignore file
├── app.py                # Main Streamlit application entry point, controller logic
├── requirements.txt      # Python dependencies
├── run.sh                # Script to run the application in the virtual environment
├── SETUP.md              # Detailed setup instructions
├── README.md             # Project documentation
├── config/               # Configuration files
│   ├── defaults/         # Default economic and operational parameters
│   └── vehicles/         # Vehicle-specific configurations for different use cases
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
│   ├── sidebar.py        # Sidebar configuration/elements
│   ├── inputs/           # Input UI modules
│   └── results/          # Results UI modules
├── utils/                # Utility functions (e.g., data loading, formatting)
│   ├── __init__.py
│   └── helpers.py
└── tests/                # Automated tests
    ├── __init__.py
    ├── fixtures/         # Test data/fixtures
    ├── unit/             # Unit tests for individual functions/classes
    └── integration/      # Integration tests for component interactions
```

## Architecture

The application follows a modular, layered architecture to promote separation of concerns, testability, and maintainability:

### Presentation Layer (UI)
- **Streamlit UI**: Handles user interaction, displays inputs and outputs.
- **UI Modules**: Organized into logical sections for inputs and results.
- **User Guide**: Interactive documentation and tutorial to help users understand the tool.

### Controller/Service Layer
- **App Controller**: Acts as an intermediary between the UI and the core model.
- **State Management**: Manages application state and orchestrates calls to the TCO calculation engine.

### Core Model Layer
- **TCO Calculator**: Orchestrates the calculation of all cost components and produces the final TCO results.
- **Calculation Strategies**: Implements the Strategy pattern for different calculation methods.
- **Cost Components**: Functions for calculating individual cost components.
- **Data Models**: Defines the structure, types, and validation rules for all data using Pydantic.

### Configuration Management
- **YAML Configuration**: External files defining default parameters and vehicle specifications.
- **Example Scenarios**: Predefined configurations for different operational contexts.
- **Configuration Loading**: Utilities for loading and validating configuration data.

## Usage

### Basic TCO Calculation

```python
from tco_model.calculator import TCOCalculator
from tco_model.models import ScenarioInput

# Load scenario input
scenario = ScenarioInput.from_file("scenarios/example.yaml")

# Calculate TCO
calculator = TCOCalculator()
result = calculator.calculate(scenario)

# Access results
print(f"Total TCO: {result.total_tco}")
print(f"LCOD: {result.lcod} AUD/km")

# Access cost components
energy_cost = result.npv_costs.energy
maintenance_cost = result.npv_costs.maintenance
```

### Comparing Scenarios

```python
# Calculate two scenarios
bet_result = calculator.calculate(bet_scenario)
diesel_result = calculator.calculate(diesel_scenario)

# Compare results
comparison = calculator.compare_results(bet_result, diesel_result)

# Access comparison results
print(f"TCO difference: {comparison.tco_difference}")
print(f"Percentage difference: {comparison.tco_percentage}%")

# Identify cheaper option
cheaper_index = comparison.cheaper_option
cheaper_scenario = comparison.scenario_1 if cheaper_index == 1 else comparison.scenario_2
print(f"Cheaper option: {cheaper_scenario.vehicle_name}")

# Check if there's a payback period
if comparison.payback_year is not None:
    print(f"Payback in year {comparison.payback_year + 1}")
```

## Example Scenarios

The application includes several predefined scenarios to demonstrate various use cases:

- **Urban Delivery**: Short-haul delivery operations in urban areas with frequent stops and lower daily distances
- **Regional Distribution**: Medium-haul distribution routes between regional centers with higher daily distances
- **Long-Haul Transport**: Long-distance interstate transport operations with maximum daily distances
- **Financing Comparison**: Comparison of different financing methods for the same vehicle type

These scenarios can be loaded directly from the User Guide tab and used as starting points for customization.

## Getting Started

### Prerequisites

- Python 3.9 or higher

### Installation and Setup

For a complete guide on setting up the project, see [SETUP.md](SETUP.md).

Quick setup:

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/aus-tco.git
   cd aus-tco
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```

4. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

1. Use the provided script to run the application (this activates the virtual environment automatically):
   ```bash
   ./run.sh
   ```

   Or manually activate the environment and run:
   ```bash
   source venv/bin/activate
   streamlit run app.py
   ```

2. Open your web browser and navigate to the URL displayed in the terminal (typically http://localhost:8501).

3. For first-time users, navigate to the "User Guide" tab to get started with a tutorial and example scenarios.

## Documentation

- [Developer Guide](docs/developer_guide.md)
- [Migration Guide](docs/migration_guide.md)

## Development

### Running Tests

Run all tests:
```bash
python -m pytest
```

Run tests with coverage report:
```bash
python -m pytest --cov=tco_model
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- This project was inspired by the need for accurate TCO modelling for heavy vehicles in the Australian context.
- Special thanks to the developers of the libraries used in this project.