import json
import sys
from typing import Any, List
from .config import get_config

_config = get_config()

class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    # Colors for JSON elements
    INTEGER = '\033[34m'      # Blue
    STRING = '\033[32m'       # Green  
    BRACKET = '\033[37m'      # White
    BOOL = '\033[1;32m'       # Bold green
    NULL = '\033[90m'         # Gray
    KEY = '\033[36m'          # Cyan
    CLASS_FUNC = '\033[1;35m' # Bold magenta/pink

def _colorize(text: str, color: str) -> str:
    """Apply color to text if terminal supports it"""
    if not sys.stdout.isatty():
        return text
    return f"{color}{text}{Colors.RESET}"

def _format_object(obj: Any) -> str:
    """Format non-JSON objects with appropriate colors"""
    if callable(obj) or hasattr(obj, '__class__'):
        obj_type = type(obj).__name__
        if callable(obj):
            return _colorize(f"<{obj_type}: {getattr(obj, '__name__', str(obj))}>", Colors.CLASS_FUNC)
        else:
            return _colorize(f"<{obj_type} object>", Colors.CLASS_FUNC)
    return str(obj)

def format_json_simple(obj: Any, indent: int = 0) -> str:
    """Format JSON in a clean, readable way with colors"""
    indent_str = "  " * indent
    
    if obj is None:
        return _colorize("null", Colors.NULL)
    elif isinstance(obj, bool):
        return _colorize(str(obj).lower(), Colors.BOOL)
    elif isinstance(obj, int):
        return _colorize(str(obj), Colors.INTEGER)
    elif isinstance(obj, float):
        return _colorize(str(obj), Colors.INTEGER)
    elif isinstance(obj, str):
        return _colorize(f'"{obj}"', Colors.STRING)
    elif isinstance(obj, dict):
        if not obj:
            return _colorize("{}", Colors.BRACKET)
        
        lines = [_colorize("{", Colors.BRACKET)]
        items = list(obj.items())
        for i, (key, value) in enumerate(items):
            is_last = i == len(items) - 1
            comma = "" if is_last else ","
            formatted_value = format_json_simple(value, indent + 1)
            colored_key = _colorize(f'"{key}"', Colors.KEY)
            
            lines.append(f'{indent_str}  {colored_key}: {formatted_value}{comma}')
        
        lines.append(f"{indent_str}" + _colorize("}", Colors.BRACKET))
        return "\n".join(lines)
    
    elif isinstance(obj, list):
        if not obj:
            return _colorize("[]", Colors.BRACKET)
        
        lines = [_colorize("[", Colors.BRACKET)]
        for i, item in enumerate(obj):
            is_last = i == len(obj) - 1
            comma = "" if is_last else ","
            formatted_item = format_json_simple(item, indent + 1)
            lines.append(f"{indent_str}  {formatted_item}{comma}")
        
        lines.append(f"{indent_str}" + _colorize("]", Colors.BRACKET))
        return "\n".join(lines)
    
    else:
        return _format_object(obj)

class InteractiveJsonViewer:
    """Interactive JSON viewer with collapsible functionality"""
    
    def __init__(self, data: Any, max_depth: int = 10):
        self.data = data
        self.max_depth = max_depth
        self.collapsed_paths = set()
        self.colors = {
            'key': '\033[94m',      # Blue
            'string': '\033[92m',   # Green
            'number': '\033[93m',   # Yellow
            'bool': '\033[95m',     # Magenta
            'null': '\033[90m',     # Bright black
            'bracket': '\033[97m',  # White
            'arrow': '\033[96m',    # Cyan
            'reset': '\033[0m'
        }
    
    def _colorize(self, text: str, color_type: str) -> str:
        """Apply color to text if terminal supports it"""
        if not sys.stdout.isatty():
            return text
        color = self.colors.get(color_type, '')
        return f"{color}{text}{self.colors['reset']}"
    
    def _format_value(self, value: Any) -> str:
        """Format a JSON value with appropriate colors"""
        if value is None:
            return self._colorize('null', 'null')
        elif isinstance(value, bool):
            return self._colorize(str(value).lower(), 'bool')
        elif isinstance(value, (int, float)):
            return self._colorize(str(value), 'number')
        elif isinstance(value, str):
            return self._colorize(f'"{value}"', 'string')
        else:
            return str(value)
    
    def _is_collapsed(self, path: str) -> bool:
        """Check if a path is collapsed"""
        return path in self.collapsed_paths
    
    def _render_json(self, obj: Any, indent: int = 0, path: str = "", depth: int = 0) -> List[str]:
        """Render JSON with collapsible functionality"""
        if depth > self.max_depth:
            return [" " * indent + "..."]
        
        lines = []
        indent_str = " " * indent
        
        if isinstance(obj, dict):
            if not obj:
                lines.append(indent_str + self._colorize("{}", 'bracket'))
                return lines
            
            lines.append(indent_str + self._colorize("{", 'bracket'))
            
            items = list(obj.items())
            for i, (key, value) in enumerate(items):
                current_path = f"{path}.{key}" if path else key
                is_last = i == len(items) - 1
                comma = "" if is_last else ","
                
                if isinstance(value, (dict, list)) and value:
                    # Check if this path is collapsed
                    if self._is_collapsed(current_path):
                        arrow = self._colorize("▶", 'arrow')
                        preview = "..." if isinstance(value, dict) else f"[{len(value)}]"
                        key_colored = self._colorize(f'"{key}"', 'key')
                        lines.append(f"{indent_str}  {arrow} {key_colored}: {preview}{comma}")
                    else:
                        arrow = self._colorize("▼", 'arrow')
                        key_colored = self._colorize(f'"{key}"', 'key')
                        lines.append(f"{indent_str}  {arrow} {key_colored}: ")
                        lines.extend(self._render_json(value, indent + 4, current_path, depth + 1))
                        if not is_last:
                            lines[-1] += comma
                else:
                    key_colored = self._colorize(f'"{key}"', 'key')
                    lines.append(f"{indent_str}  {key_colored}: {self._format_value(value)}{comma}")
            
            lines.append(indent_str + self._colorize("}", 'bracket'))
            
        elif isinstance(obj, list):
            if not obj:
                lines.append(indent_str + self._colorize("[]", 'bracket'))
                return lines
            
            lines.append(indent_str + self._colorize("[", 'bracket'))
            
            for i, item in enumerate(obj):
                current_path = f"{path}[{i}]"
                is_last = i == len(obj) - 1
                comma = "" if is_last else ","
                
                if isinstance(item, (dict, list)) and item:
                    if self._is_collapsed(current_path):
                        arrow = self._colorize("▶", 'arrow')
                        preview = "..." if isinstance(item, dict) else f"[{len(item)}]"
                        lines.append(f"{indent_str}  {arrow} [{i}]: {preview}{comma}")
                    else:
                        arrow = self._colorize("▼", 'arrow')
                        lines.append(f"{indent_str}  {arrow} [{i}]: ")
                        lines.extend(self._render_json(item, indent + 4, current_path, depth + 1))
                        if not is_last:
                            lines[-1] += comma
                else:
                    lines.append(f"{indent_str}  [{i}]: {self._format_value(item)}{comma}")
            
            lines.append(indent_str + self._colorize("]", 'bracket'))
        
        else:
            lines.append(indent_str + self._format_value(obj))
        
        return lines
    
    def display(self) -> None:
        """Display the JSON with interactive functionality"""
        try:
            import termios
            import tty
            interactive_mode = True
        except ImportError:
            interactive_mode = False
        
        if not interactive_mode or not sys.stdin.isatty():
            # Fall back to static display
            lines = self._render_json(self.data)
            for line in lines:
                print(line)
            print(self._colorize("\n[Non-interactive mode - arrows for navigation not available]", 'arrow'))
            return
        
        print(self._colorize("Interactive JSON Viewer", 'arrow'))
        print(self._colorize("Use arrow keys to navigate, Enter/Space to toggle collapse, 'q' to quit", 'arrow'))
        print()
        
        current_line = 0
        while True:
            # Clear screen and render
            print('\033[2J\033[H', end='')  # Clear screen and move to top
            
            lines = self._render_json(self.data)
            
            for i, line in enumerate(lines):
                if i == current_line:
                    print(self._colorize("→ ", 'arrow') + line)
                else:
                    print("  " + line)
            
            print(f"\nLine {current_line + 1}/{len(lines)} - (↑/↓: navigate, Enter/Space: toggle, q: quit)")
            
            # Get user input
            try:
                old_settings = termios.tcgetattr(sys.stdin)
                tty.setraw(sys.stdin.fileno())
                ch = sys.stdin.read(1)
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
                
                if ch == 'q':
                    break
                elif ch == '\x1b':  # Arrow key sequence
                    ch2 = sys.stdin.read(2)
                    if ch2 == '[A' and current_line > 0:  # Up arrow
                        current_line -= 1
                    elif ch2 == '[B' and current_line < len(lines) - 1:  # Down arrow
                        current_line += 1
                elif ch in ['\r', ' ']:  # Enter or Space
                    # Toggle collapse for current line if it has an arrow
                    line_content = lines[current_line]
                    if '▶' in line_content or '▼' in line_content:
                        # Extract path from line by looking at the structure
                        # This is a simplified implementation
                        import re
                        key_match = re.search(r'"([^"]+)":', line_content)
                        if key_match:
                            key = key_match.group(1)
                            # Toggle the path in collapsed_paths
                            if key in self.collapsed_paths:
                                self.collapsed_paths.remove(key)
                            else:
                                self.collapsed_paths.add(key)
                        
            except (KeyboardInterrupt, EOFError):
                break
            except:
                continue
        
        print('\033[2J\033[H', end='')  # Clear screen
        lines = self._render_json(self.data)
        for line in lines:
            print(line)

def print_json(obj: Any, **kwargs) -> None:
    """Print JSON in a clean, simple format"""
    
    # Check environment settings
    if hasattr(_config, 'environment') and _config.environment == 'prod' and not kwargs.pop('force_print', False):
        return
    
    try:
        # Try to parse as JSON if it's a string
        if isinstance(obj, str):
            try:
                obj = json.loads(obj)
            except json.JSONDecodeError:
                # If it's not valid JSON, treat as regular string
                import builtins
                builtins.print(obj, **kwargs)
                return
        
        formatted = format_json_simple(obj)
        import builtins
        builtins.print(formatted, **kwargs)
        
    except Exception as e:
        # Fall back to regular print if anything goes wrong
        import builtins
        builtins.print(f"Error displaying JSON: {obj}", **kwargs)

def json_viewer(obj: Any, **kwargs) -> None:
    """Interactive JSON viewer (advanced mode)"""
    
    # Check environment settings
    if hasattr(_config, 'environment') and _config.environment == 'prod' and not kwargs.pop('force_print', False):
        return
    
    try:
        # Try to parse as JSON if it's a string
        if isinstance(obj, str):
            try:
                obj = json.loads(obj)
            except json.JSONDecodeError:
                import builtins
                builtins.print(obj, **kwargs)
                return
        
        viewer = InteractiveJsonViewer(obj)
        viewer.display()
        
    except Exception as e:
        import builtins
        builtins.print(f"Error displaying JSON: {obj}", **kwargs)