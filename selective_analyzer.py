#!/usr/bin/env python3
"""
Selective Analyzer - Main Entry Point

This script provides a convenient way to run the selective analyzer from the project root.
"""

import sys
from pathlib import Path

# Add src directory to Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Import and run the selective analyzer
if __name__ == "__main__":
    from analyzers.selective_analyzer import main
    main()
