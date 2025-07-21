#!/usr/bin/env python3
"""
Simple test for selective XSD analysis.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from utils.selective_xsd_parser import SelectiveXSDParser
from rich.console import Console

console = Console()

def simple_test():
    """Simple test of selective parsing."""
    console.print("[bold blue]Testing Selective XSD Parser[/bold blue]")
    
    # Create parser
    parser = SelectiveXSDParser()
    
    # Add a simple selection
    parser.add_file_selection(
        file_path="test_bookstore.xsd",
        elements=["bookstore"]
    )
    
    console.print("[yellow]Parsing selection...[/yellow]")
    
    try:
        result = parser.parse_selections()
        console.print(f"[green]✓ Success! Selected {len(parser.selected_components)} components[/green]")
        
        summary = parser.get_selection_summary()
        console.print("\nSummary:")
        for file_path, details in summary.items():
            console.print(f"  {file_path}: {details['total_selected']} components")
            
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    simple_test()
