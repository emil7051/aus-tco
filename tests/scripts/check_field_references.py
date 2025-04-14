#!/usr/bin/env python
"""
Field reference checker script.

This script scans the codebase for any remaining references to obsolete field names
that should be fully migrated to the new standardized field names.
"""

import os
import sys
import re
from pathlib import Path
import argparse
from typing import Dict, List, Set, Tuple

# Obsolete field names that should no longer be used anywhere in the codebase
OBSOLETE_FIELD_NAMES = [
    "npv_total",
    "lcod_per_km",
    "npv_difference",
    "npv_difference_percentage"
]

# Current canonical field names
CANONICAL_FIELD_NAMES = {
    "npv_total": "total_tco",
    "lcod_per_km": "lcod",
    "npv_difference": "tco_difference",
    "npv_difference_percentage": "tco_percentage"
}

# Exclude patterns for legitimate references in documentation/tests
EXCLUDE_PATTERNS = [
    r"test_.*\.py",
    r".*_test\.py",
    r"check_field_references\.py",  # Skip this script itself
    r"# Renamed from",
    r"# original name:",
    r"\"original name:",
    r"\*\*\*REMOVED\*\*\*"  # Marker for removed code
]

def find_field_references(
    directory: Path, 
    obsolete_fields: List[str],
    exclude_patterns: List[str]
) -> Dict[str, Dict[str, List[Tuple[int, str]]]]:
    """
    Find direct references to obsolete field names in Python files.
    
    Args:
        directory: Root directory to scan
        obsolete_fields: List of obsolete field names to search for
        exclude_patterns: Regex patterns to exclude from checking
        
    Returns:
        Dict mapping field names to file paths and line information
    """
    results = {field: {} for field in obsolete_fields}
    compiled_excludes = [re.compile(pattern) for pattern in exclude_patterns]
    
    for py_file in directory.glob("**/*.py"):
        # Skip files matching exclude patterns
        file_path_str = str(py_file)
        if any(pattern.search(file_path_str) for pattern in compiled_excludes):
            continue
            
        with open(py_file, 'r', encoding='utf-8') as f:
            try:
                lines = f.readlines()
                
                for i, line in enumerate(lines, 1):
                    # Skip lines matching exclude patterns
                    if any(pattern.search(line) for pattern in compiled_excludes):
                        continue
                        
                    for old_field in obsolete_fields:
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
        description="Check for any remaining references to obsolete field names"
    )
    parser.add_argument("directory", nargs="?", default=".",
                        help="Directory to scan (default: current directory)")
    args = parser.parse_args()
    
    directory = Path(args.directory)
    if not directory.exists() or not directory.is_dir():
        print(f"Error: {args.directory} is not a valid directory")
        sys.exit(1)
    
    print(f"Scanning for obsolete field references in {directory}...")
    print(f"The following field names should no longer be used anywhere in the codebase:")
    for old_field, new_field in CANONICAL_FIELD_NAMES.items():
        print(f"  - '{old_field}' has been replaced with '{new_field}'")
    
    references = find_field_references(directory, OBSOLETE_FIELD_NAMES, EXCLUDE_PATTERNS)
    
    found_references = False
    for old_field, files in references.items():
        if files:
            found_references = True
            new_field = CANONICAL_FIELD_NAMES.get(old_field)
            print(f"\nFound references to obsolete field '{old_field}' that should be '{new_field}':")
            
            for file_path, lines in files.items():
                print(f"  {file_path}:")
                for line_num, line_text in lines:
                    print(f"    Line {line_num}: {line_text}")
    
    if not found_references:
        print("\nNo references to obsolete field names found! Migration is complete.")
        sys.exit(0)
    else:
        print("\nFound references to obsolete field names that need to be updated.")
        print("Please replace all occurrences with their corresponding canonical names.")
        sys.exit(1)


if __name__ == "__main__":
    main() 