import sys
import os
import traceback
import inspect
import builtins
import json
import datetime
from typing import Any, Optional, Dict, List
from .config import get_config

_config = get_config()
_original_print = builtins.print

def _is_json_like(obj: Any) -> bool:
    """Check if object is JSON-serializable"""
    try:
        json.dumps(obj)
        return isinstance(obj, (dict, list)) and obj
    except (TypeError, ValueError):
        return False

def _is_dataframe(obj: Any) -> bool:
    """Check if object is a pandas or polars DataFrame"""
    obj_type = type(obj).__name__
    module_name = getattr(type(obj), '__module__', '')
    
    return (obj_type == 'DataFrame' and 
            ('pandas' in module_name or 'polars' in module_name))

def _format_dataframe(df: Any) -> str:
    """Format DataFrame for terminal display with colors"""
    try:
        # Get the string representation
        df_str = str(df)
        
        # Apply basic coloring to DataFrame output
        if not sys.stdout.isatty():
            return df_str
        
        lines = df_str.split('\n')
        colored_lines = []
        
        for i, line in enumerate(lines):
            if i == 0:  # Header row
                colored_lines.append(Colors.BRIGHT_CYAN + line + Colors.RESET)
            elif line.strip() and not line.startswith(' '):  # Index column
                colored_lines.append(Colors.YELLOW + line + Colors.RESET)
            else:
                colored_lines.append(line)
        
        return '\n'.join(colored_lines)
    except Exception:
        return str(df)

class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    
    # Text colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'

def _is_error_or_warning(text: str) -> bool:
    """Check if the text appears to be an error, warning, or traceback"""
    text_lower = text.lower()
    error_indicators = [
        'error:', 'exception:', 'traceback', 'warning:', 
        'file "', 'line ', 'syntaxerror', 'typeerror',
        'valueerror', 'keyerror', 'indexerror'
    ]
    return any(indicator in text_lower for indicator in error_indicators)

def _is_user_code() -> bool:
    """Check if the print call is coming from user code (not system/library code)"""
    frame = inspect.currentframe()
    try:
        # Go up the call stack to find the caller
        for _ in range(10):  # Limit depth to avoid infinite loops
            frame = frame.f_back
            if frame is None:
                break
            
            filename = frame.f_code.co_filename
            
            # Skip our own package source files only (not user scripts that might have gleam in path)
            if 'gleam/src/' in filename or filename.endswith('/gleam/__init__.py'):
                continue
                
            # Skip built-in modules and site-packages
            if any(skip in filename for skip in [
                '<frozen', '<built-in', 'site-packages', 
                'importlib', '_bootstrap'
            ]):
                continue
                
            # This looks like user code
            return True
            
        return False
    finally:
        del frame

def _colorize_text(text: str, color: str = Colors.BRIGHT_CYAN) -> str:
    """Apply color to text if terminal supports it"""
    if not sys.stdout.isatty():
        return text
    return f"{color}{text}{Colors.RESET}"

def _log_to_file(*args, **kwargs) -> None:
    """Log print statements to file if configured"""
    if not _config.log_to_file or not _config.log_file_path:
        return
    
    try:
        # Convert args to string like print does
        text = ' '.join(str(arg) for arg in args)
        
        # Add timestamp and caller info
        frame = inspect.currentframe()
        filename = "unknown"
        lineno = 0
        
        # Safely navigate the call stack
        try:
            frame = frame.f_back  # _log_to_file caller
            if frame:
                frame = frame.f_back  # beautify_print caller
                if frame:
                    filename = frame.f_code.co_filename
                    lineno = frame.f_lineno
        except:
            pass
        finally:
            del frame
        
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {os.path.basename(filename)}:{lineno} - {text}\n"
        
        with open(_config.log_file_path, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    except Exception as e:
        # Silently fail to avoid breaking user code
        pass

def beautify_print(*args, **kwargs) -> None:
    """Enhanced print function with beautification and configuration"""
    
    # If environment is production and force_print is not enabled, skip
    if _config.environment == 'prod' and not kwargs.pop('force_print', False):
        if _config.log_to_file:
            _log_to_file(*args, **kwargs)
        return
    
    # Check if this is user code
    if not _is_user_code():
        _original_print(*args, **kwargs)
        return
    
    # Handle single argument special formatting
    if len(args) == 1 and not kwargs.get('sep') and not kwargs.get('end'):
        arg = args[0]
        
        # Check for DataFrame
        if _is_dataframe(arg):
            formatted = _format_dataframe(arg)
            if _config.log_to_file:
                _log_to_file(formatted)
                if _config.log_only_mode:
                    return
            _original_print(formatted)
            return
        
        # Check if string is JSON-parseable
        if isinstance(arg, str):
            try:
                parsed_json = json.loads(arg)
                # Only format as JSON if it's a dict or list (not just a string/number/bool)
                if isinstance(parsed_json, (dict, list)):
                    from .json_viewer import format_json_simple
                    formatted = format_json_simple(parsed_json)
                    if _config.log_to_file:
                        _log_to_file(formatted)
                        if _config.log_only_mode:
                            return
                    _original_print(formatted)
                    return
            except (json.JSONDecodeError, ValueError, TypeError):
                # Not valid JSON, continue with normal string processing
                pass
        
        # Check for JSON-like objects first (dicts and lists)
        if _is_json_like(arg):
            from .json_viewer import format_json_simple
            formatted = format_json_simple(arg)
            if _config.log_to_file:
                _log_to_file(formatted)
                if _config.log_only_mode:
                    return
            _original_print(formatted)
            return
        
        # Check for functions and other complex objects
        if callable(arg) or (hasattr(arg, '__class__') and 
                           not isinstance(arg, (str, int, float, bool, type(None), dict, list))):
            from .json_viewer import _format_object
            formatted = _format_object(arg)
            if _config.log_to_file:
                _log_to_file(formatted)
                if _config.log_only_mode:
                    return
            _original_print(formatted)
            return
    
    # Convert all arguments to strings for regular processing
    text_parts = []
    for arg in args:
        text_parts.append(str(arg))
    
    full_text = ' '.join(text_parts)
    
    # Check if this looks like an error/warning - if so, use original print
    if _is_error_or_warning(full_text):
        _original_print(*args, **kwargs)
        return
    
    # Log to file if configured
    if _config.log_to_file:
        _log_to_file(*args, **kwargs)
        
        # If only logging to file, don't print to terminal
        if _config.log_only_mode:
            return
    
    # Beautify the output
    if _config.use_colors and sys.stdout.isatty():
        colored_parts = []
        for part in text_parts:
            colored_parts.append(_colorize_text(part, _config.text_color))
        
        _original_print(*colored_parts, **kwargs)
    else:
        _original_print(*args, **kwargs)

def configure(**kwargs) -> None:
    """Configure the beautify print settings"""
    _config.update(**kwargs)

def print_with_timestamp(*args, **kwargs) -> None:
    """Print with timestamp prefix"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    timestamp_colored = _colorize_text(f"[{timestamp}]", Colors.BRIGHT_BLACK)
    
    # Convert args to string and colorize
    text_parts = [str(arg) for arg in args]
    full_text = ' '.join(text_parts)
    colored_text = _colorize_text(full_text, _config.text_color)
    
    _original_print(timestamp_colored, colored_text, **kwargs)

def print_separator(char: str = '=', length: int = 80, color: str = Colors.BRIGHT_BLACK) -> None:
    """Print a separator line for visual grouping"""
    separator = char * length
    _original_print(_colorize_text(separator, color))

def print_labeled(label: str, *args, **kwargs) -> None:
    """Print with a colored label prefix"""
    label_colored = _colorize_text(f"[{label}]", Colors.BOLD + Colors.CYAN)
    
    # Convert args to string and colorize
    text_parts = [str(arg) for arg in args]
    full_text = ' '.join(text_parts)
    colored_text = _colorize_text(full_text, _config.text_color)
    
    _original_print(label_colored, colored_text, **kwargs)

def format_table(data: List[Dict[str, Any]], headers: Optional[List[str]] = None) -> str:
    """Format a list of dictionaries as a colored table"""
    if not data:
        return ""
    
    # Get headers from first dict if not provided
    if headers is None:
        headers = list(data[0].keys()) if data else []
    
    if not headers:
        return ""
    
    # Calculate column widths
    col_widths = {h: len(str(h)) for h in headers}
    for row in data:
        for header in headers:
            value = str(row.get(header, ''))
            col_widths[header] = max(col_widths[header], len(value))
    
    # Build table
    lines = []
    
    # Header row
    header_parts = []
    for h in headers:
        header_parts.append(_colorize_text(str(h).ljust(col_widths[h]), Colors.BOLD + Colors.CYAN))
    lines.append(' | '.join(header_parts))
    
    # Separator
    separator_parts = ['-' * col_widths[h] for h in headers]
    lines.append(_colorize_text('-+-'.join(separator_parts), Colors.BRIGHT_BLACK))
    
    # Data rows
    for row in data:
        row_parts = []
        for h in headers:
            value = str(row.get(h, ''))
            row_parts.append(_colorize_text(value.ljust(col_widths[h]), Colors.BRIGHT_CYAN))
        lines.append(' | '.join(row_parts))
    
    return '\n'.join(lines)

def print_table(data: List[Dict[str, Any]], headers: Optional[List[str]] = None, **kwargs) -> None:
    """Print a list of dictionaries as a formatted table"""
    table = format_table(data, headers)
    if table:
        _original_print(table, **kwargs)

def print_diff(label: str, before: Any, after: Any) -> None:
    """Print a before/after comparison with color coding"""
    label_colored = _colorize_text(f"[{label}]", Colors.BOLD + Colors.YELLOW)
    before_colored = _colorize_text(f"Before: {before}", Colors.RED)
    after_colored = _colorize_text(f"After:  {after}", Colors.GREEN)
    
    _original_print(label_colored)
    _original_print("  " + before_colored)
    _original_print("  " + after_colored)

def print_success(message: str, **kwargs) -> None:
    """Print a success message in green"""
    icon = _colorize_text("✓", Colors.BOLD + Colors.GREEN)
    text = _colorize_text(message, Colors.GREEN)
    _original_print(icon, text, **kwargs)

def print_error(message: str, **kwargs) -> None:
    """Print an error message in red"""
    icon = _colorize_text("✗", Colors.BOLD + Colors.RED)
    text = _colorize_text(message, Colors.RED)
    _original_print(icon, text, **kwargs)

def print_warning(message: str, **kwargs) -> None:
    """Print a warning message in yellow"""
    icon = _colorize_text("⚠", Colors.BOLD + Colors.YELLOW)
    text = _colorize_text(message, Colors.YELLOW)
    _original_print(icon, text, **kwargs)

def print_info(message: str, **kwargs) -> None:
    """Print an info message in blue"""
    icon = _colorize_text("ℹ", Colors.BOLD + Colors.BLUE)
    text = _colorize_text(message, Colors.BLUE)
    _original_print(icon, text, **kwargs)

def write_to_log(obj: Any, filename: Optional[str] = None) -> str:
    """Write an object to a file in the logs folder
    
    Args:
        obj: The object to write to file
        filename: Optional filename (without extension). If not provided, 
                 a timestamp-based name will be generated.
    
    Returns:
        str: The absolute path to the created file
    
    Examples:
        >>> write_to_log({"key": "value"})
        '/path/to/project/logs/log_20251219_171650.json'
        
        >>> write_to_log(my_dataframe, "my_data")
        '/path/to/project/logs/my_data.csv'
    """
    # Find project root (go up from gleam/src to project root)
    current_file = os.path.abspath(__file__)
    # Go up from beautify.py -> src -> gleam -> project_root
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
    
    # Create logs folder if it doesn't exist
    logs_dir = os.path.join(project_root, "logs")
    os.makedirs(logs_dir, exist_ok=True)
    
    # Generate filename if not provided
    if filename is None:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"log_{timestamp}"
    
    # Detect data type and determine file extension
    file_extension = ".txt"
    content = ""
    
    # Check if it's a DataFrame
    if _is_dataframe(obj):
        file_extension = ".csv"
        try:
            # Try to convert to CSV
            content = obj.to_csv(index=False)
        except Exception as e:
            # Fallback to string representation
            file_extension = ".txt"
            content = str(obj)
    
    # Check if it's a dict or list (JSON-serializable)
    elif isinstance(obj, (dict, list)):
        file_extension = ".json"
        try:
            content = json.dumps(obj, indent=2, ensure_ascii=False)
        except (TypeError, ValueError):
            # If not JSON-serializable, fall back to string
            file_extension = ".txt"
            content = str(obj)
    
    # Check if it's a string that looks like JSON
    elif isinstance(obj, str):
        try:
            parsed = json.loads(obj)
            if isinstance(parsed, (dict, list)):
                file_extension = ".json"
                content = json.dumps(parsed, indent=2, ensure_ascii=False)
            else:
                content = obj
        except (json.JSONDecodeError, ValueError):
            content = obj
    
    # Everything else as text
    else:
        content = str(obj)
    
    # Construct full file path
    filepath = os.path.join(logs_dir, f"{filename}{file_extension}")
    
    # Write to file
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Print success message
        print_success(f"Logged to: {filepath}")
        
        return filepath
    except Exception as e:
        print_error(f"Failed to write log file: {e}")
        raise