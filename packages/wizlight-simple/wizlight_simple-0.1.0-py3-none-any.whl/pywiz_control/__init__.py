from .client import SimpleWizDevice
from .discovery import SimpleWizScanner

# Wir machen den Listener direkt über die Klasse oder als Alias verfügbar
start_push_listener = SimpleWizDevice.start_push_listener

__all__ = ["SimpleWizDevice", "SimpleWizScanner", "start_push_listener"]
__version__ = "0.1.0"
