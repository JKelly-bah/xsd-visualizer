#!/usr/bin/env python3
"""
Java UML Generator - Main Entry Point

This script provides a convenient way to run the Java UML generator from the project root.
"""

import sys
from pathlib import Path

# Add src directory to Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Import and run the Java UML generator
if __name__ == "__main__":
    from analyzers.java_uml_generator import main
    main()
