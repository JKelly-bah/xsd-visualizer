#!/usr/bin/env python3
"""
Debug selective parser final structure.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from utils.selective_xsd_parser import SelectiveXSDParser
from rich.console import Console
import json

console = Console()

def debug_final_structure():
    """Debug the final structure from selective parser."""
    console.print("[bold blue]Debugging Final Selective Parser Structure[/bold blue]")
    
    parser = SelectiveXSDParser()
    parser.add_file_selection(
        file_path="test_bookstore.xsd",
        elements=["bookstore"],
        complex_types=["BookType"]
    )
    
    console.print("[yellow]Parsing selections...[/yellow]")
    result = parser.parse_selections()
    
    console.print(f"[green]Result keys: {list(result.keys())}[/green]")
    
    # Check elements structure
    if 'elements' in result:
        console.print(f"\nElements: {len(result['elements'])}")
        for name, element in result['elements'].items():
            console.print(f"  {name}: {type(element)}")
            if isinstance(element, dict):
                console.print(f"    Keys: {list(element.keys())}")
            else:
                console.print(f"    Value: {element}")
    
    # Check global_elements structure  
    if 'global_elements' in result:
        console.print(f"\nGlobal Elements: {len(result['global_elements'])}")
        for name, element in result['global_elements'].items():
            console.print(f"  {name}: {type(element)}")
            if isinstance(element, dict):
                console.print(f"    Keys: {list(element.keys())}")
    
    # Check complex_types structure
    if 'complex_types' in result:
        console.print(f"\nComplex Types: {len(result['complex_types'])}")
        for name, ctype in result['complex_types'].items():
            console.print(f"  {name}: {type(ctype)}")
            if isinstance(ctype, dict):
                console.print(f"    Keys: {list(ctype.keys())}")

if __name__ == "__main__":
    debug_final_structure()
