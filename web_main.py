#!/usr/bin/env python3
"""
GoCart Web Application Launcher
Runs the GoCart system as a web application using Flet
"""

import sys
import os

# Add the parent directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import and run the main application
from gocart_system.main import main

if __name__ == "__main__":
    # Run the Flet app
    import flet as ft
    ft.app(target=main)