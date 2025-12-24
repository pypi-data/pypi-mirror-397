"""
Gleam - A lightweight Python package for enhanced print statements
"""

from .src.beautify import (
    beautify_print, 
    configure,
    print_with_timestamp,
    print_separator,
    print_labeled,
    print_table,
    format_table,
    print_diff,
    print_success,
    print_error,
    print_warning,
    print_info,
    write_to_log
)
from .src.json_viewer import print_json, json_viewer
from ._version import __version__

# Create aliases for easier imports
print = beautify_print

__all__ = [
    "beautify_print", 
    "print", 
    "print_json", 
    "json_viewer", 
    "configure", 
    "setup",
    "print_with_timestamp",
    "print_separator",
    "print_labeled",
    "print_table",
    "format_table",
    "print_diff",
    "print_success",
    "print_error",
    "print_warning",
    "print_info",
    "write_to_log"
]

def setup(env: str = 'dev'):
    """Initialize the package by monkey-patching the built-in print function
    
    Args:
        env: Environment mode ('dev' or 'prod'). Defaults to 'dev'.
    """
    import builtins
    from .src.config import get_config
    
    builtins.print = beautify_print
    
    # Set environment
    config = get_config()
    config.environment = env