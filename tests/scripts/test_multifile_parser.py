#!/usr/bin/env python3
"""
Test script for multi-file XSD parsing capabilities.
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from utils.multi_file_xsd_parser import MultiFileXSDParser
from rich.console import Console
from rich.table import Table
from rich.tree import Tree
from rich import print

def test_multi_file_parsing():
    """Test parsing a schema spread across multiple files."""
    console = Console()
    
    # Path to our test multi-file schema
    main_schema = project_root / "test_multifile" / "library.xsd"
    
    if not main_schema.exists():
        console.print("[red]Error: Test schema not found![/red]")
        return
    
    console.print(f"[bold blue]Testing Multi-File XSD Parser[/bold blue]")
    console.print(f"Main schema: {main_schema}")
    console.print()
    
    try:
        # Initialize the multi-file parser
        parser = MultiFileXSDParser(str(main_schema))
        
        # Parse the main schema and all referenced files
        console.print("[yellow]Parsing schema and dependencies...[/yellow]")
        result = parser.parse()
        
        # Display summary of all parsed files
        console.print("\n[bold green]✓ Parsing completed successfully![/bold green]")
        
        summary = parser.get_file_summary()
        
        # Create a table showing all parsed files
        file_table = Table(title="Parsed Schema Files")
        file_table.add_column("File", style="cyan")
        file_table.add_column("Target Namespace", style="magenta")
        file_table.add_column("Elements", justify="right", style="green")
        file_table.add_column("Complex Types", justify="right", style="blue")
        file_table.add_column("Simple Types", justify="right", style="yellow")
        
        for file_name, info in summary.items():
            file_table.add_row(
                file_name,
                info['target_namespace'] or "[dim]None[/dim]",
                str(info['global_elements']),
                str(info['complex_types']),
                str(info['simple_types'])
            )
        
        console.print(file_table)
        
        # Show dependency tree
        console.print("\n[bold]Schema Dependencies:[/bold]")
        
        # Build dependency tree
        tree = Tree("📁 library.xsd (main)")
        for file_name, info in summary.items():
            if file_name != "library.xsd" and info['dependencies']:
                tree.add(f"📄 {file_name}")
        
        console.print(tree)
        
        # Show some details from the main result
        console.print(f"\n[bold]Main Schema Analysis:[/bold]")
        console.print(f"Total elements: {len(result['elements'])}")
        console.print(f"Total complex types: {len(result['complex_types'])}")
        console.print(f"Total simple types: {len(result['simple_types'])}")
        
        # Show cross-references
        if hasattr(parser, 'schema_references') and parser.schema_references:
            console.print(f"\n[bold]Schema References Found:[/bold]")
            ref_table = Table()
            ref_table.add_column("Type", style="yellow")
            ref_table.add_column("Namespace", style="cyan")
            ref_table.add_column("Schema Location", style="green")
            ref_table.add_column("Resolved Path", style="dim")
            
            for ref in parser.schema_references:
                ref_table.add_row(
                    ref.reference_type,
                    ref.namespace or "[dim]None[/dim]",
                    ref.schema_location or "[dim]None[/dim]",
                    str(ref.resolved_path) if ref.resolved_path else "[dim]Not resolved[/dim]"
                )
            
            console.print(ref_table)
        
        return True
        
    except Exception as e:
        console.print(f"[red]Error during parsing: {e}[/red]")
        return False

if __name__ == "__main__":
    success = test_multi_file_parsing()
    if success:
        print("\n[bold green]✓ Multi-file XSD parsing test completed successfully![/bold green]")
    else:
        print("\n[bold red]✗ Multi-file XSD parsing test failed![/bold red]")
        sys.exit(1)
