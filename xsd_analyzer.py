#!/usr/bin/env python3
"""
XSD Visualizer - Main Entry Point

This script provides a convenient way to run the XSD analyzer from the project root.
It imports and runs the main analyzer from the reorganized src/ directory structure.
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Import and run the main analyzer
if __name__ == "__main__":
    from analyzers.xsd_analyzer import main
    main()
