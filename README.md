# Australian Heavy Vehicle TCO Modeller

A Python-based web application for modelling and comparing the Total Cost of Ownership (TCO) of different heavy vehicle types in the Australian context.

## Overview

The Australian Heavy Vehicle TCO Modeller allows users to accurately model and compare the TCO of different heavy vehicle types (initially Battery Electric Trucks and Internal Combustion Engine diesel trucks) within the specific economic and operational context of Australia.

The application provides a user-friendly interface for defining detailed scenarios, comparing vehicles side-by-side, and visualizing the results through interactive charts and tables.

## Key Features

- **Comprehensive TCO Modelling**: Calculate all relevant cost components over the vehicle's lifecycle, including acquisition, energy, maintenance, infrastructure, and more.
- **Vehicle Comparison**: Side-by-side comparison of TCO for different vehicle types.
- **Detailed Cost Breakdown**: Year-by-year breakdown of all cost components.
- **Interactive Visualizations**: Clear and interactive charts for analyzing TCO results.
- **Flexible Scenario Definition**: Customize operational and economic parameters to match specific use cases.
- **Default Configurations**: Pre-configured parameters for common Australian heavy vehicle types and operational contexts.

## Project Structure

```
aus-heavy-vehicle-tco/
├── .env                  # Environment variables (for Pydantic BaseSettings)
├── .gitignore            # Git ignore file
├── app.py                # Main Streamlit application entry point, controller logic
├── pyproject.toml        # Project metadata and dependencies (Poetry/PDM)
├── README.md             # Project documentation
├── config/               # Configuration files
│   ├── defaults/         # Default economic and operational parameters
│   └── vehicles/         # Vehicle-specific configurations
├── tco_model/            # Core TCO calculation logic and data models
│   ├── __init__.py
│   ├── calculator.py     # Main TCO calculation engine
│   ├── models.py         # Pydantic models for inputs, outputs, configs
│   ├── strategies.py     # Calculation strategies (Energy, Maintenance, etc.)
│   ├── costs.py          # Functions for calculating individual cost components
│   └── vehicles.py       # Vehicle-specific data loading/handling
├── ui/                   # Streamlit UI modules/components
│   ├── __init__.py
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
- **Configuration Loading**: Utilities for loading and validating configuration data.

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Poetry (recommended) or pip

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/aus-heavy-vehicle-tco.git
   cd aus-heavy-vehicle-tco
   ```

2. Install dependencies using Poetry:
   ```bash
   poetry install
   ```

   Or using pip:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

1. Start the Streamlit application:
   ```bash
   poetry run streamlit run app.py
   ```

   Or without Poetry:
   ```bash
   streamlit run app.py
   ```

2. Open your web browser and navigate to the URL displayed in the terminal (typically http://localhost:8501).

## Development

### Setting Up a Development Environment

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/aus-heavy-vehicle-tco.git
   cd aus-heavy-vehicle-tco
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   poetry install --with dev
   ```

### Running Tests

Run all tests:
```bash
poetry run pytest
```

Run tests with coverage report:
```bash
poetry run pytest --cov=tco_model
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