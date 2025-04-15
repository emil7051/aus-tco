#!/bin/bash
# TCO Modeller Test Suite - Enhanced output for better terminal viewing
# Shows all test names, pass/fail status, and detailed error reports directly in terminal

# Define colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Define symbols for better visualization
CHECK="✓"
CROSS="✗"
INFO="ℹ"
WARNING="⚠"
ARROW="→"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                   TCO Modeller Test Suite                  ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"

# Create directory for test reports if it doesn't exist
mkdir -p test_reports

# Check for pytest and install if needed
if ! command -v pytest &> /dev/null; then
    echo -e "${YELLOW}${WARNING} pytest not found. Installing pytest and pytest-cov...${NC}"
    pip install pytest pytest-cov
fi

# Function to format test names for better readability
format_test_name() {
    local test_path=$1
    # Format: tests/path/file.py::TestClass::test_name
    local file_path=$(echo "$test_path" | cut -d':' -f1)
    local class_name=""
    local test_name=""
    
    # Extract the file name without the path
    local file_name=$(basename "$file_path" .py)
    
    # Handle the double-colon format from pytest output
    if [[ $test_path == *"::"* ]]; then
        # Extract class name (might be empty if no class)
        if [[ $(echo "$test_path" | grep -o "::" | wc -l) -eq 2 ]]; then
            # Format with class: tests/path/file.py::TestClass::test_name
            class_name=$(echo "$test_path" | cut -d':' -f3)
            test_name=$(echo "$test_path" | cut -d':' -f4)
        else
            # Format without class: tests/path/file.py::test_name
            class_name=""
            test_name=$(echo "$test_path" | cut -d':' -f3)
        fi
    else
        # Fallback for different format
        test_name=$(basename "$file_path" | sed 's/test_//g' | sed 's/\.py//g')
    fi
    
    # Format without test_ prefix and use better spacing
    test_name=${test_name#test_}
    test_name=$(echo "$test_name" | sed 's/_/ /g')
    
    # Capitalize first letter of test name
    if [[ -n "$test_name" ]]; then
        test_name="$(tr '[:lower:]' '[:upper:]' <<< ${test_name:0:1})${test_name:1}"
    fi
    
    # Return properly formatted name
    if [[ -n "$class_name" ]]; then
        echo "$class_name: $test_name"
    else
        echo "$file_name: $test_name"
    fi
}

# Function to extract and format error messages
format_error_message() {
    local error_text=$1
    # Extract the actual error message, removing stack trace
    local message=$(echo "$error_text" | grep -A 2 "E " | head -3 | sed 's/^E\s*//' | tr '\n' ' ')
    if [[ -z "$message" ]]; then
        # Try a different approach if first method finds nothing
        message=$(echo "$error_text" | grep -A 1 "FAILED" | tail -1 | sed 's/^[^:]*://')
    fi
    echo "$message"
}

echo -e "\n${CYAN}${INFO} Running test discovery...${NC}"

# Define common pytest arguments for consistency
PYTEST_ARGS="--cov=tco_model --cov=utils --cov=ui"

# Use a simpler approach to count tests that will be run
TEST_COUNT=$(python -m pytest $PYTEST_ARGS --collect-only | tail -1 | grep -o '[0-9]\+ items' | grep -o '[0-9]\+')
if [[ -z "$TEST_COUNT" ]]; then
    # Fallback method if the above doesn't work
    TEST_COUNT=$(python -m pytest $PYTEST_ARGS --collect-only | grep -o 'collected [0-9]\+ item' | grep -o '[0-9]\+')
fi
# Default to showing "?" if we couldn't determine the count
if [[ -z "$TEST_COUNT" ]]; then
    TEST_COUNT="?"
fi

echo -e "${CYAN}${INFO} Found ${BOLD}${TEST_COUNT}${NC}${CYAN} tests to run${NC}"

# Run tests with detailed output format but filter through processing
echo -e "\n${BLUE}${BOLD}▶ Running all tests with detailed reporting...${NC}\n"

# Create a temporary file for raw output
TEMP_OUTPUT=$(mktemp)

# Run the tests and capture both stdout and stderr
python -m pytest \
  $PYTEST_ARGS \
  --no-header \
  --no-summary \
  -v 2>&1 | tee $TEMP_OUTPUT > test_reports/all_tests_output.txt

# Process output to make it more readable
PASSED=0
FAILED=0
SKIPPED=0
FAILED_TESTS=()
FAILED_MESSAGES=()

# Process the output file
{
    current_test=""
    while IFS= read -r line; do
        # Skip streamlit warnings and other noise
        if [[ $line == *"missing ScriptRunContext"* ]] || [[ $line == *"WARNING streamlit"* ]]; then
            continue
        fi

        # Extract test information - revised regex to match various test output formats
        if [[ $line =~ ^tests/.*\ (PASSED|FAILED|SKIPPED|XFAIL|XPASS).*$ ]]; then
            current_test=$(echo "$line" | cut -d' ' -f1)
            result=$(echo "$line" | grep -o -E '(PASSED|FAILED|SKIPPED|XFAIL|XPASS)')
            
            # Extract test name part
            test_name=$(echo "$current_test" | grep -o -E 'test_[^:]*$' | sed 's/^test_//')
            test_name=$(echo "$test_name" | sed 's/_/ /g')
            test_name="$(tr '[:lower:]' '[:upper:]' <<< ${test_name:0:1})${test_name:1}"
            
            # Get class name if present
            if [[ $current_test == *"::"*"::"* ]]; then
                class_name=$(echo "$current_test" | grep -o -E '::([^:]+)::' | sed 's/:://g')
                formatted_name="${class_name}: ${test_name}"
            else
                file_base=$(basename "$(echo "$current_test" | cut -d':' -f1)" .py)
                formatted_name="${file_base}: ${test_name}"
            fi
            
            if [[ "$result" == "PASSED" ]] || [[ "$result" == "XPASS" ]]; then
                echo -e "${GREEN}${CHECK} ${NC}${formatted_name}"
                ((PASSED++))
            elif [[ "$result" == "FAILED" ]]; then
                echo -e "${RED}${CROSS} ${NC}${formatted_name}"
                ((FAILED++))
                FAILED_TESTS+=("$formatted_name::::$current_test")
            elif [[ "$result" == "SKIPPED" ]] || [[ "$result" == "XFAIL" ]]; then
                echo -e "${YELLOW}- ${NC}${formatted_name} ${YELLOW}(skipped)${NC}"
                ((SKIPPED++))
            fi
        # Capture assertion errors and error messages with better pattern matching
        elif [[ $line == *"E       assert"* ]] || [[ $line == *"E       "* ]] || [[ $line == *"FAILED"*": "*  ]]; then
            if [[ ! -z "$current_test" ]]; then
                # Store the error message for later display
                FAILED_MESSAGES+=("$current_test::::$line")
            fi
        fi
    done 
} < $TEMP_OUTPUT

# Save coverage details to file and extract summary
echo -e "\n${BLUE}${BOLD}▶ Coverage Summary${NC}"
pytest $PYTEST_ARGS --cov-report=term-missing --cov-report=html:test_reports/coverage -q > /dev/null

# Show coverage summary in a cleaner format
coverage_info=$(coverage report | grep TOTAL)
statements=$(echo "$coverage_info" | awk '{print $2}')
missing=$(echo "$coverage_info" | awk '{print $3}')
covered=$(echo "$coverage_info" | awk '{print $4}')
echo -e "${CYAN}${INFO} Code coverage: ${statements} statements, ${missing} missing, ${covered}% covered${NC}"

echo -e "\n${BLUE}${BOLD}▶ Test Results Summary${NC}"
echo -e "${GREEN}${CHECK} Passed: ${PASSED}${NC}"
echo -e "${RED}${CROSS} Failed: ${FAILED}${NC}"
if [[ $SKIPPED -gt 0 ]]; then
    echo -e "${YELLOW}- Skipped: ${SKIPPED}${NC}"
fi
echo -e "${CYAN}${INFO} Total:  $((PASSED + FAILED + SKIPPED))${NC}"

if [ ${#FAILED_TESTS[@]} -gt 0 ]; then
    echo -e "\n${RED}${BOLD}▶ Failed Tests Details${NC}"
    
    # Group failures by test module/class - without using associative arrays
    # Create arrays for group names and values
    GROUP_NAMES=()
    GROUP_VALUES=()
    
    for failed_item in "${FAILED_TESTS[@]}"; do
        # Split the stored test info
        test_display=$(echo "$failed_item" | cut -d':' -f1-2)
        test_path=$(echo "$failed_item" | cut -d':' -f3-)
        
        # Extract the class name for grouping
        if [[ $test_display == *":"* ]]; then
            class_name=$(echo "$test_display" | cut -d':' -f1)
        else
            class_name=$(basename "$(echo "$test_path" | cut -d':' -f1)" .py)
        fi
        
        # Check if class_name already exists in GROUP_NAMES
        found=0
        idx=0
        for j in "${!GROUP_NAMES[@]}"; do
            if [[ "${GROUP_NAMES[$j]}" == "$class_name" ]]; then
                found=1
                idx=$j
                break
            fi
        done
        
        if [[ $found -eq 0 ]]; then
            GROUP_NAMES+=("$class_name")
            GROUP_VALUES+=("$test_display::::$test_path")
        else
            GROUP_VALUES[$idx]="${GROUP_VALUES[$idx]};;;;$test_display::::$test_path"
        fi
    done
    
    # Display failures by group
    for i in "${!GROUP_NAMES[@]}"; do
        group="${GROUP_NAMES[$i]}"
        echo -e "\n${RED}${BOLD}$group${NC}"
        IFS=';;;;' read -ra GROUP_TESTS <<< "${GROUP_VALUES[$i]}"
        
        # Counter for unique identifiers for tests with blank names
        blank_counter=1
        
        for test_entry in "${GROUP_TESTS[@]}"; do
            test_display=$(echo "$test_entry" | cut -d':' -f1-2)
            test_path=$(echo "$test_entry" | cut -d':' -f3-)
            
            # Display the test name (everything after the class name+colon)
            if [[ "$test_display" == *":"* ]]; then
                test_name="${test_display#*: }"
                if [[ -n "$test_name" ]]; then  # Only display if there's a name
                    echo -e "${RED}${ARROW} ${test_name}${NC}"
                else
                    # Extract the test name from the path if possible
                    func_name=$(echo "$test_path" | grep -o 'test_[a-zA-Z0-9_]*$')
                    if [[ -n "$func_name" ]]; then
                        # Format the function name properly
                        formatted_func=${func_name#test_}
                        formatted_func=$(echo "$formatted_func" | sed 's/_/ /g')
                        formatted_func="$(tr '[:lower:]' '[:upper:]' <<< ${formatted_func:0:1})${formatted_func:1}"
                        echo -e "${RED}${ARROW} ${formatted_func}${NC}"
                    else
                        # Last resort - give a number
                        echo -e "${RED}${ARROW} Test #${blank_counter}${NC}"
                        ((blank_counter++))
                    fi
                fi
            else
                echo -e "${RED}${ARROW} ${test_display}${NC}"
            fi
            
            # Find and display the corresponding error message
            error_found=0
            for error_msg in "${FAILED_MESSAGES[@]}"; do
                error_test_path=$(echo "$error_msg" | cut -d':' -f1)
                if [[ "$error_test_path" == "$test_path" ]]; then
                    error_content=$(echo "$error_msg" | cut -d':' -f2-)
                    formatted_error=$(format_error_message "$error_content")
                    if [[ -n "$formatted_error" ]]; then
                        echo -e "   ${YELLOW}Error: ${formatted_error}${NC}"
                        error_found=1
                        break
                    fi
                fi
            done
            
            # If no specific error message found, provide a generic message
            if [[ $error_found -eq 0 ]]; then
                echo -e "   ${YELLOW}Error: Test failed, check logs for details${NC}"
            fi
        done
    done
    
    echo -e "\n${YELLOW}${WARNING} Full test output saved to: test_reports/all_tests_output.txt${NC}"
    echo -e "${YELLOW}${WARNING} Detailed coverage report: test_reports/coverage/index.html${NC}"
else
    echo -e "\n${GREEN}${BOLD}All tests passed successfully!${NC}"
fi

echo -e "\n${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                      Test run complete                      ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"

# Clean up temporary file
rm $TEMP_OUTPUT 