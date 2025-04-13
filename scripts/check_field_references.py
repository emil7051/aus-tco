#!/usr/bin/env python
"""
Field reference checker script.

This script scans the codebase for direct references to renamed fields
and reports any remaining usages.
"""

import os
import sys
import re
from pathlib import Path
import argparse
from typing import Dict, List, Set, Tuple

# Constants
RENAMED_FIELDS = {
    "npv_total": "total_tco",
    "lcod_per_km": "lcod",
    "npv_difference": "tco_difference",
    "npv_difference_percentage": "tco_percentage"
}

# Exclude patterns (e.g., tests, compatibility aliases)
EXCLUDE_PATTERNS = [
    r"test_.*\.py",
    r".*_test\.py",
    r"@property\s+def\s+(npv_total|lcod_per_km|npv_difference|npv_difference_percentage)",
    r"warnings\.warn\("
]

def find_field_references(
    directory: Path, 
    renamed_fields: Dict[str, str],
    exclude_patterns: List[str]
) -> Dict[str, Dict[str, List[Tuple[int, str]]]]:
    """
    Find direct references to renamed fields in Python files.
    
    Args:
        directory: Root directory to scan
        renamed_fields: Dictionary mapping old field names to new ones
        exclude_patterns: Regex patterns to exclude from checking
        
    Returns:
        Dict mapping field names to file paths and line information
    """
    results = {field: {} for field in renamed_fields}
    compiled_excludes = [re.compile(pattern) for pattern in exclude_patterns]
    
    for py_file in directory.glob("**/*.py"):
        # Skip files matching exclude patterns
        if any(pattern.search(str(py_file)) for pattern in compiled_excludes):
            continue
            
        with open(py_file, 'r', encoding='utf-8') as f:
            try:
                lines = f.readlines()
                
                for i, line in enumerate(lines, 1):
                    # Skip lines matching exclude patterns
                    if any(pattern.search(line) for pattern in compiled_excludes):
                        continue
                        
                    for old_field, new_field in renamed_fields.items():
                        # Look for direct references to old field names
                        # Avoid false positives by checking for word boundaries
                        pattern = fr'\b{re.escape(old_field)}\b'
                        if re.search(pattern, line):
                            rel_path = str(py_file.relative_to(directory))
                            if rel_path not in results[old_field]:
                                results[old_field][rel_path] = []
                            results[old_field][rel_path].append((i, line.strip()))
            except UnicodeDecodeError:
                # Skip binary files
                continue
    
    return results


def main():
    """Main entry point for the field reference checker script."""
    parser = argparse.ArgumentParser(
        description="Check for direct references to renamed fields"
    )
    parser.add_argument("directory", nargs="?", default=".",
                        help="Directory to scan (default: current directory)")
    args = parser.parse_args()
    
    directory = Path(args.directory)
    if not directory.exists() or not directory.is_dir():
        print(f"Error: {args.directory} is not a valid directory")
        sys.exit(1)
    
    print(f"Scanning for field references in {directory}...")
    references = find_field_references(directory, RENAMED_FIELDS, EXCLUDE_PATTERNS)
    
    found_references = False
    for old_field, files in references.items():
        if files:
            found_references = True
            new_field = RENAMED_FIELDS[old_field]
            print(f"\nFound references to '{old_field}' (renamed to '{new_field}'):")
            
            for file_path, lines in files.items():
                print(f"  {file_path}:")
                for line_num, line_text in lines:
                    print(f"    Line {line_num}: {line_text}")
    
    if not found_references:
        print("\nNo direct references to renamed fields found!")
        sys.exit(0)
    else:
        print("\nFound references to renamed fields. These should be updated.")
        sys.exit(1)


if __name__ == "__main__":
    main() 