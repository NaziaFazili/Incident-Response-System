"""
Configuration module for the MCP Server
Handles environment variables and application settings
"""

import os
from pathlib import Path

# Server Configuration
PORT = int(os.getenv("PORT", "8080"))
HOST = os.getenv("HOST", "0.0.0.0")

DATA_DIR = Path(os.getenv("DATA_DIR", "data"))
