import os
from typing import Optional

_config_instance = None

def get_config():
    """Get the singleton config instance"""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance

class Config:
    """Configuration class for beautify_print package"""
    
    def __init__(self):
        # Default configuration
        self.environment = os.environ.get('GLEAM_ENV', 'dev')
        self.use_colors = True
        self.text_color = '\033[96m'  # Bright cyan
        self.log_to_file = False
        self.log_file_path: Optional[str] = None
        self.log_only_mode = False  # If True, only log to file, don't print to terminal
        
        # JSON viewer settings
        self.json_indent = 2
        self.json_max_depth = 10
    
    def update(self, **kwargs) -> None:
        """Update configuration with provided keyword arguments"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise ValueError(f"Unknown configuration option: {key}")
    
    def enable_file_logging(self, file_path: str, log_only: bool = False) -> None:
        """Enable logging to file"""
        self.log_to_file = True
        self.log_file_path = file_path
        self.log_only_mode = log_only
        
        # Create directory if it doesn't exist
        dir_path = os.path.dirname(file_path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
    
    def disable_file_logging(self) -> None:
        """Disable logging to file"""
        self.log_to_file = False
        self.log_only_mode = False