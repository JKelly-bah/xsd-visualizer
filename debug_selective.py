#!/usr/bin/env python3
"""
Debug selective parser structure.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from utils.selective_xsd_parser import SelectiveXSDParser
from rich.console import Console
import json

console = Console()

def debug_structure():
    """Debug the structure of selective parser results."""
    console.print("[bold blue]Debugging Selective Parser Structure[/bold blue]")
    
    parser = SelectiveXSDParser()
    parser.add_file_selection(
        file_path="test_bookstore.xsd",
        elements=["bookstore"]
    )
    
    console.print("[yellow]Parsing...[/yellow]")
    
    # Just do the first part of parsing to see what we get
    for criteria in parser.selection_criteria:
        parser._parse_file_selection(criteria)
    
    console.print(f"[green]Selected {len(parser.selected_components)} components[/green]")
    
    # Show the structure of the first component
    if parser.selected_components:
        first_key = list(parser.selected_components.keys())[0]
        first_component = parser.selected_components[first_key]
        
        console.print(f"\nFirst component: {first_key}")
        console.print(f"Type: {type(first_component.component_data)}")
        console.print(f"Data keys: {list(first_component.component_data.keys()) if isinstance(first_component.component_data, dict) else 'Not a dict'}")
        
        if isinstance(first_component.component_data, dict):
            console.print("Sample data:")
            console.print(json.dumps(first_component.component_data, indent=2, default=str))

if __name__ == "__main__":
    debug_structure()
