# Setup Guide for Australian Heavy Vehicle TCO Modeller

This guide will help you set up and run the Total Cost of Ownership (TCO) Modeller for Australian Heavy Vehicles.

## Prerequisites

- Python 3.9+ installed
- Git (optional, for cloning the repository)

## Installation

1. Clone or download the repository:
   ```
   git clone <repository-url>
   cd aus-tco
   ```

2. Create a virtual environment and install dependencies:
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - On macOS/Linux:
     ```
     source venv/bin/activate
     ```
   - On Windows:
     ```
     venv\Scripts\activate
     ```

4. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Running the Application

1. With the virtual environment activated, run:
   ```
   streamlit run app.py
   ```
   
   Alternatively, use the provided script:
   ```
   ./run.sh  # On macOS/Linux
   ```

2. The application will start and should automatically open in your web browser at `http://localhost:8501`

## Configuration

The application uses YAML configuration files located in the `config/` directory:

- `config/defaults/` - Default parameters for economic and operational scenarios
- `config/vehicles/` - Vehicle-specific configurations

## Troubleshooting

If you encounter any issues:

1. Make sure your virtual environment is activated
2. Try reinstalling the dependencies with `pip install -r requirements.txt`
3. Check the Python version with `python --version` (should be 3.9 or higher)
4. For Pydantic errors, ensure you have both `pydantic` and `pydantic-settings` installed 