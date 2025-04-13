#!/bin/bash
# Type checking script for the Australian Heavy Vehicle TCO Modeller project

# Colors for prettier output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
CHECK_ALL=true
MODULE=""
STRICT=false
VERBOSE=false

# Help message
function print_help {
    echo -e "${BLUE}Type Checking Tool for Australian Heavy Vehicle TCO Modeller${NC}"
    echo ""
    echo "Usage: ./scripts/check_types.sh [options]"
    echo ""
    echo "Options:"
    echo "  -m, --module MODULE   Check only a specific module (e.g., tco_model, utils)"
    echo "  -s, --strict          Enable strict mode with additional checks"
    echo "  -v, --verbose         Show verbose output"
    echo "  -h, --help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./scripts/check_types.sh                    # Check all modules"
    echo "  ./scripts/check_types.sh -m tco_model       # Check only tco_model"
    echo "  ./scripts/check_types.sh -s                 # Enable strict mode"
    echo ""
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -m|--module)
            CHECK_ALL=false
            MODULE="$2"
            shift 2
            ;;
        -s|--strict)
            STRICT=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            print_help
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            print_help
            exit 1
            ;;
    esac
done

# Build mypy command based on options
MYPY_CMD="mypy"

if [ "$STRICT" = true ]; then
    MYPY_CMD="$MYPY_CMD --strict"
fi

if [ "$VERBOSE" = true ]; then
    MYPY_CMD="$MYPY_CMD -v"
fi

# Add color to output
MYPY_CMD="$MYPY_CMD --pretty"

# Determine which modules to check
if [ "$CHECK_ALL" = true ]; then
    echo -e "${BLUE}Checking types across the entire codebase...${NC}"
    MODULES=("app.py" "tco_model" "utils" "ui")
else
    echo -e "${BLUE}Checking types for module: ${MODULE}${NC}"
    MODULES=("$MODULE")
fi

# Count for summary
TOTAL_ERRORS=0
CHECK_COUNT=0

# Run mypy for each module
for module in "${MODULES[@]}"; do
    echo -e "${YELLOW}Checking $module...${NC}"
    
    # Run mypy and capture output and exit code
    OUTPUT=$(eval "$MYPY_CMD $module")
    EXIT_CODE=$?
    CHECK_COUNT=$((CHECK_COUNT + 1))
    
    # Display output and track errors
    if [ $EXIT_CODE -eq 0 ]; then
        echo -e "${GREEN}✓ No type errors in $module${NC}"
    else
        echo -e "$OUTPUT"
        echo -e "${RED}✗ Found type errors in $module${NC}"
        ERROR_COUNT=$(echo "$OUTPUT" | grep -c "error:")
        TOTAL_ERRORS=$((TOTAL_ERRORS + ERROR_COUNT))
    fi
    echo ""
done

# Print summary
echo -e "${BLUE}Type Check Summary:${NC}"
echo -e "Modules checked: $CHECK_COUNT"
if [ $TOTAL_ERRORS -eq 0 ]; then
    echo -e "${GREEN}Total errors: $TOTAL_ERRORS${NC}"
    echo -e "${GREEN}All checks passed!${NC}"
    exit 0
else
    echo -e "${RED}Total errors: $TOTAL_ERRORS${NC}"
    echo -e "${RED}Some type checks failed. Please fix the errors above.${NC}"
    exit 1
fi 