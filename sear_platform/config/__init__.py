# Import the application configuration management components.
# 'Settings' defines the configuration structure, while 'get_settings' 
# provides a centralized and convenient way to retrieve the active configuration instance.
from .settings import Settings, get_settings

# Import all predefined global constants (e.g., regex patterns, default limits, API endpoints).
# This ensures consistent, magic-number-free usage across the entire application.
from .constants import *