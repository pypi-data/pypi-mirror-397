#!/usr/bin/env python3
"""
Example usage of the Gleam package
Run this as: python3 -c "import sys; sys.path.append('.'); exec(open('example.py').read())"
"""

import sys
import os

# Add parent directory to path so we can import gleam
parent_dir = os.path.dirname(os.path.abspath(__file__))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import gleam
import json

# Initialize the package
gleam.setup()

print("=== Gleam Demo ===")
print()

# Basic colored prints
print("This is a beautiful colored print statement!")
print("Multiple", "arguments", "work", "perfectly")
print()

# JSON demonstration
sample_data = {
    "users": [
        {
            "id": 1,
            "name": "John Doe", 
            "email": "john@example.com",
            "profile": {
                "age": 30,
                "interests": ["coding", "music", "travel"],
                "settings": {
                    "theme": "dark",
                    "notifications": True
                }
            }
        },
        {
            "id": 2,
            "name": "Jane Smith",
            "email": "jane@example.com", 
            "profile": {
                "age": 25,
                "interests": ["design", "photography"],
                "settings": {
                    "theme": "light",
                    "notifications": False
                }
            }
        }
    ],
    "total_count": 2,
    "metadata": {
        "version": "1.0",
        "created_at": "2024-01-01T00:00:00Z"
    }
}

print("=== Interactive JSON Viewer Demo ===")
print("Use arrow keys to navigate, Enter/Space to toggle sections, 'q' to quit")
print()
gleam.print_json(sample_data)
print()

# Environment demonstration
print("=== Environment Configuration Demo ===")
print("Current environment:", gleam._config.environment)
print()

print("Setting environment to 'prod'...")
gleam.set_env('prod')
print("This print statement won't show in prod mode")
print("But this one will!", force_print=True)
print()

# Reset to dev mode
gleam.set_env('dev')
print("Back to dev mode - prints are visible again")
print()

# File logging demonstration  
print("=== File Logging Demo ===")
gleam._config.enable_file_logging('debug.log')
print("This will be logged to debug.log file")
print("Check debug.log file to see timestamped entries")
print()

# Test error handling (should not be beautified)
try:
    1/0
except Exception as e:
    print(f"Error: {e}")  # This should remain unmodified