#!/bin/bash
# Run tests with coverage reporting

# Make sure script stops on errors
set -e

# Define colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Running tests with coverage reporting...${NC}"
echo ""

# Make sure pytest and pytest-cov are installed
pip install pytest pytest-cov

# Run tests with coverage
python -m pytest --cov=tco_model tests/ -v

# Generate HTML report
echo ""
echo -e "${YELLOW}Generating HTML coverage report...${NC}"
python -m pytest --cov=tco_model tests/ --cov-report=html --cov-report=term-missing

echo ""
echo -e "${GREEN}Coverage report generated successfully.${NC}"
echo -e "HTML report available in htmlcov/ directory."
echo ""
echo -e "${YELLOW}Test summary:${NC}"
python -m pytest tests/ -v --no-cov 