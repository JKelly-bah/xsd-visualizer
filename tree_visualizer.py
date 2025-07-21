#!/usr/bin/env python3
"""
Tree Visualizer - Main Entry Point

This script provides a convenient way to run the tree visualizer from the project root.
"""

import sys
from pathlib import Path

# Add src directory to Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Import and run the tree visualizer
if __name__ == "__main__":
    from analyzers.tree_visualizer import main
    main()
