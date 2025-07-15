#!/usr/bin/env python3
"""
Quick XSD Inspector - Interactive tool for examining specific elements and types.
"""

import argparse
import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional

# Add utils directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'utils'))

from utils.xsd_parser import XSDParser
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

console = Console()

class XSDInspector:
    """Interactive inspector for XSD elements and types."""
    
    def __init__(self, xsd_path: str):
        self.xsd_path = Path(xsd_path)
        
        if not self.xsd_path.exists():
            raise FileNotFoundError(f"XSD file not found: {xsd_path}")
        
        # Load schema
        console.print(f"[bold blue]Loading schema:[/bold blue] {self.xsd_path}")
        self.parser = XSDParser(str(self.xsd_path))
        self.structure = self.parser.parse()
        console.print("[bold green]✓[/bold green] Schema loaded")
    
    def inspect_element(self, element_name: str) -> None:
        """Inspect a specific element."""
        element = self.parser.find_element(element_name)
        
        if not element:
            console.print(f"[bold red]Element '{element_name}' not found[/bold red]")
            return
        
        # Element overview
        title = f"Element: {element.name}"
        content = []
        
        if element.type:
            content.append(f"[bold]Type:[/bold] {element.type}")
        
        content.append(f"[bold]Occurrence:[/bold] {element.min_occurs}..{element.max_occurs}")
        
        if element.namespace:
            content.append(f"[bold]Namespace:[/bold] {element.namespace}")
        
        if element.documentation:
            content.append(f"\n[bold]Documentation:[/bold]\n{element.documentation}")
        
        console.print(Panel("\n".join(content), title=title, expand=False))
        
        # Attributes table
        if element.attributes:
            self._show_attributes_table(element.attributes)
        
        # Children
        if element.children:
            console.print(f"\n[bold]Children ({len(element.children)}):[/bold]")
            for child in element.children:
                child_info = f"  • {child.name}"
                if child.type:
                    child_info += f" : {child.type}"
                child_info += f" [{child.min_occurs}..{child.max_occurs}]"
                console.print(child_info)
        
        # Element path
        path = self.parser.get_element_path(element_name)
        if path:
            console.print(f"\n[bold]Path:[/bold] {' → '.join(path)}")
    
    def inspect_type(self, type_name: str) -> None:
        """Inspect a specific type (complex or simple)."""
        # Check complex types
        if type_name in self.structure['complex_types']:
            complex_type = self.structure['complex_types'][type_name]
            self._show_complex_type(complex_type)
            return
        
        # Check simple types
        if type_name in self.structure['simple_types']:
            simple_type = self.structure['simple_types'][type_name]
            self._show_simple_type(simple_type)
            return
        
        console.print(f"[bold red]Type '{type_name}' not found[/bold red]")
    
    def _show_complex_type(self, complex_type: Dict[str, Any]) -> None:
        """Display complex type information."""
        title = f"Complex Type: {complex_type['name']}"
        content = []
        
        if complex_type['base_type']:
            content.append(f"[bold]Base Type:[/bold] {complex_type['base_type']}")
        
        if complex_type['documentation']:
            content.append(f"\n[bold]Documentation:[/bold]\n{complex_type['documentation']}")
        
        console.print(Panel("\n".join(content), title=title, expand=False))
        
        # Elements
        if complex_type['elements']:
            console.print(f"\n[bold]Elements ({len(complex_type['elements'])}):[/bold]")
            for element in complex_type['elements']:
                element_info = f"  • {element['name']}"
                if element['type']:
                    element_info += f" : {element['type']}"
                element_info += f" [{element['min_occurs']}..{element['max_occurs']}]"
                console.print(element_info)
        
        # Attributes
        if complex_type['attributes']:
            self._show_attributes_table(complex_type['attributes'])
    
    def _show_simple_type(self, simple_type: Dict[str, Any]) -> None:
        """Display simple type information."""
        title = f"Simple Type: {simple_type['name']}"
        content = []
        
        if simple_type['base_type']:
            content.append(f"[bold]Base Type:[/bold] {simple_type['base_type']}")
        
        if simple_type['documentation']:
            content.append(f"\n[bold]Documentation:[/bold]\n{simple_type['documentation']}")
        
        console.print(Panel("\n".join(content), title=title, expand=False))
        
        # Restrictions
        if simple_type['restrictions']:
            console.print("\n[bold]Restrictions:[/bold]")
            for key, value in simple_type['restrictions'].items():
                console.print(f"  • {key}: {value}")
        
        # Enumerations
        if simple_type['enumerations']:
            console.print(f"\n[bold]Enumerations ({len(simple_type['enumerations'])}):[/bold]")
            for enum_val in simple_type['enumerations']:
                console.print(f"  • {enum_val}")
    
    def _show_attributes_table(self, attributes: list) -> None:
        """Display attributes in a table."""
        if not attributes:
            return
        
        table = Table(title="Attributes")
        table.add_column("Name", style="cyan")
        table.add_column("Type", style="yellow")
        table.add_column("Use", style="green")
        table.add_column("Default", style="dim")
        
        for attr in attributes:
            table.add_row(
                attr.get('name', ''),
                attr.get('type', ''),
                attr.get('use', 'optional'),
                attr.get('default', '')
            )
        
        console.print(table)
    
    def search_elements(self, pattern: str) -> None:
        """Search for elements matching a pattern."""
        matches = []
        
        # Search root elements
        for element in self.structure['elements']:
            if pattern.lower() in element['name'].lower():
                matches.append(('root', element['name']))
        
        # Search global elements
        for name in self.structure['global_elements']:
            if pattern.lower() in name.lower():
                matches.append(('global', name))
        
        # Search within complex types
        def search_in_elements(elements, path=""):
            for element in elements:
                full_name = f"{path}.{element['name']}" if path else element['name']
                if pattern.lower() in element['name'].lower():
                    matches.append(('nested', full_name))
                search_in_elements(element['children'], full_name)
        
        for complex_type in self.structure['complex_types'].values():
            search_in_elements(complex_type['elements'], complex_type['name'])
        
        if matches:
            console.print(f"[bold green]Found {len(matches)} matches:[/bold green]")
            for match_type, name in matches:
                console.print(f"  [{match_type}] {name}")
        else:
            console.print(f"[bold red]No elements found matching '{pattern}'[/bold red]")
    
    def show_statistics(self) -> None:
        """Display schema statistics."""
        stats = self.structure['metadata']['statistics']
        
        table = Table(title="Schema Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Count", style="magenta")
        
        table.add_row("Total Elements", str(stats['total_elements']))
        table.add_row("Root Elements", str(len(self.structure['elements'])))
        table.add_row("Global Elements", str(len(self.structure['global_elements'])))
        table.add_row("Complex Types", str(stats['total_complex_types']))
        table.add_row("Simple Types", str(stats['total_simple_types']))
        table.add_row("Maximum Depth", str(stats['max_depth']))
        table.add_row("Total Attributes", str(stats['total_attributes']))
        
        console.print(table)

def main():
    parser = argparse.ArgumentParser(description="Interactive XSD element and type inspector")
    parser.add_argument('xsd_file', help='Path to XSD file')
    parser.add_argument('--element', '-e', help='Element to inspect')
    parser.add_argument('--type', '-t', help='Type to inspect')
    parser.add_argument('--search', '-s', help='Search for elements')
    parser.add_argument('--stats', action='store_true', help='Show schema statistics')
    
    args = parser.parse_args()
    
    try:
        inspector = XSDInspector(args.xsd_file)
        
        if args.element:
            inspector.inspect_element(args.element)
        elif args.type:
            inspector.inspect_type(args.type)
        elif args.search:
            inspector.search_elements(args.search)
        elif args.stats:
            inspector.show_statistics()
        else:
            # Interactive mode
            console.print("\n[bold]XSD Inspector - Interactive Mode[/bold]")
            console.print("Commands: element <name>, type <name>, search <pattern>, stats, quit")
            
            while True:
                try:
                    command = console.input("\n[bold blue]> [/bold blue]").strip()
                    
                    if command.lower() in ['quit', 'exit', 'q']:
                        break
                    elif command.startswith('element '):
                        inspector.inspect_element(command[8:])
                    elif command.startswith('type '):
                        inspector.inspect_type(command[5:])
                    elif command.startswith('search '):
                        inspector.search_elements(command[7:])
                    elif command == 'stats':
                        inspector.show_statistics()
                    else:
                        console.print("[dim]Unknown command. Try: element <name>, type <name>, search <pattern>, stats, quit[/dim]")
                        
                except KeyboardInterrupt:
                    break
                except EOFError:
                    break
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
