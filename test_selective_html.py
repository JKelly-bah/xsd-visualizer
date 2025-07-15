#!/usr/bin/env python3
"""
Test HTML generation for selective analysis.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from utils.selective_xsd_parser import SelectiveXSDParser
from utils.html_generator import HTMLGenerator
from rich.console import Console

console = Console()

def test_html_generation():
    """Test HTML generation for selective analysis."""
    console.print("[bold blue]Testing HTML Generation for Selective Analysis[/bold blue]")
    
    # Create parser and select some components
    parser = SelectiveXSDParser()
    parser.add_file_selection(
        file_path="test_bookstore.xsd",
        elements=["bookstore"],
        complex_types=["BookType"]
    )
    
    console.print("[yellow]Parsing selection...[/yellow]")
    result = parser.parse_selections()
    
    console.print("[yellow]Generating HTML...[/yellow]")
    
    try:
        output_dir = "./output/test_selective_html"
        generator = HTMLGenerator(result)
        generator.generate_documentation(output_dir)
        
        console.print(f"[green]✓ HTML generated successfully in {output_dir}[/green]")
        
    except Exception as e:
        console.print(f"[red]HTML generation error: {e}[/red]")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_html_generation()
