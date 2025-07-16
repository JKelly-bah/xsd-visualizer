#!/usr/bin/env python3
"""
Tree Visualizer for XSD files - Creates hierarchical visualizations of schema structure.
Supports multiple output formats including text trees, SVG diagrams, and interactive HTML.
"""

import argparse
import sys
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

# Add utils directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'utils'))

from utils.xsd_parser import XSDParser
from rich.console import Console
from rich.tree import Tree
from rich import print as rprint
from anytree import Node, RenderTree
from anytree.exporter import DotExporter, UniqueDotExporter

console = Console()
logger = logging.getLogger(__name__)

class XSDTreeVisualizer:
    """
    Creates tree visualizations of XSD schema structure.
    """
    
    def __init__(self, xsd_path: str):
        """
        Initialize tree visualizer.
        
        Args:
            xsd_path: Path to XSD file
        """
        self.xsd_path = Path(xsd_path)
        self.parser: Optional[XSDParser] = None
        self.structure: Optional[Dict[str, Any]] = None
        
        if not self.xsd_path.exists():
            raise FileNotFoundError(f"XSD file not found: {xsd_path}")
    
    def load_schema(self) -> None:
        """Load and parse the XSD schema."""
        console.print(f"[bold blue]Loading XSD schema:[/bold blue] {self.xsd_path}")
        
        with console.status("[bold green]Parsing XSD..."):
            self.parser = XSDParser(str(self.xsd_path))
            self.structure = self.parser.parse()
        
        console.print("[bold green]✓[/bold green] Schema loaded successfully")
    
    def create_rich_tree(self, element_name: Optional[str] = None) -> Tree:
        """
        Create a Rich tree visualization for console display.
        
        Args:
            element_name: Specific element to visualize (None for all root elements)
            
        Returns:
            Rich Tree object
        """
        if not self.structure:
            raise ValueError("Must load schema first")
        
        if not self.parser:
            raise ValueError("Parser not initialized")
        
        if element_name:
            # Find specific element
            element = self.parser.find_element(element_name)
            if not element:
                raise ValueError(f"Element '{element_name}' not found")
            
            tree = Tree(f"[bold blue]{element.name}[/bold blue]")
            self._add_element_to_rich_tree(tree, element)
        else:
            # Show all root elements
            schema_name = self.xsd_path.stem
            tree = Tree(f"[bold magenta]Schema: {schema_name}[/bold magenta]")
            
            # Add root elements
            if self.structure['elements']:
                elements_branch = tree.add("[bold cyan]Root Elements[/bold cyan]")
                for element_data in self.structure['elements']:
                    self._add_element_data_to_rich_tree(elements_branch, element_data)
            
            # Add global elements
            if self.structure['global_elements']:
                global_branch = tree.add("[bold cyan]Global Elements[/bold cyan]")
                for name, element_data in self.structure['global_elements'].items():
                    self._add_element_data_to_rich_tree(global_branch, element_data)
        
        return tree
    
    def _add_element_to_rich_tree(self, parent_tree: Tree, element) -> None:
        """Add an XSDElement to Rich tree."""
        # Create element label
        label = f"[green]{element.name}[/green]"
        if element.type:
            label += f" : [yellow]{element.type}[/yellow]"
        
        # Add occurrence info
        if element.min_occurs != "1" or element.max_occurs != "1":
            label += f" [dim]\\[{element.min_occurs}..{element.max_occurs}][/dim]"
        
        element_tree = parent_tree.add(label)
        
        # Add documentation if present
        if element.documentation:
            doc_text = element.documentation[:100] + "..." if len(element.documentation) > 100 else element.documentation
            element_tree.add(f"[dim italic]{doc_text}[/dim italic]")
        
        # Add attributes
        if element.attributes:
            attr_tree = element_tree.add("[cyan]@attributes[/cyan]")
            for attr in element.attributes:
                attr_label = f"[cyan]{attr['name']}[/cyan]"
                if attr['type']:
                    attr_label += f" : [yellow]{attr['type']}[/yellow]"
                if attr['use'] == 'required':
                    attr_label += " [red]*[/red]"
                attr_tree.add(attr_label)
        
        # Add children recursively
        for child in element.children:
            self._add_element_to_rich_tree(element_tree, child)
    
    def _add_element_data_to_rich_tree(self, parent_tree: Tree, element_data: Dict[str, Any]) -> None:
        """Add element data dictionary to Rich tree."""
        # Create element label
        label = f"[green]{element_data['name']}[/green]"
        if element_data['type']:
            label += f" : [yellow]{element_data['type']}[/yellow]"
        
        # Add occurrence info
        if element_data['min_occurs'] != "1" or element_data['max_occurs'] != "1":
            label += f" [dim]\\[{element_data['min_occurs']}..{element_data['max_occurs']}][/dim]"
        
        element_tree = parent_tree.add(label)
        
        # Add documentation if present
        if element_data['documentation']:
            doc_text = element_data['documentation'][:100] + "..." if len(element_data['documentation']) > 100 else element_data['documentation']
            element_tree.add(f"[dim italic]{doc_text}[/dim italic]")
        
        # Add attributes
        if element_data['attributes']:
            attr_tree = element_tree.add("[cyan]@attributes[/cyan]")
            for attr in element_data['attributes']:
                attr_label = f"[cyan]{attr['name']}[/cyan]"
                if attr['type']:
                    attr_label += f" : [yellow]{attr['type']}[/yellow]"
                if attr['use'] == 'required':
                    attr_label += " [red]*[/red]"
                attr_tree.add(attr_label)
        
        # Add children recursively
        for child in element_data['children']:
            self._add_element_data_to_rich_tree(element_tree, child)
    
    def create_anytree_structure(self, element_name: Optional[str] = None) -> Node:
        """
        Create an anytree structure for export to various formats.
        
        Args:
            element_name: Specific element to visualize
            
        Returns:
            Root Node of the tree
        """
        if not self.structure:
            raise ValueError("Must load schema first")
        
        if not self.parser:
            raise ValueError("Parser not initialized")
        
        if element_name:
            element = self.parser.find_element(element_name)
            if not element:
                raise ValueError(f"Element '{element_name}' not found")
            
            root = Node(element.name)
            self._add_element_to_anytree(root, element)
        else:
            schema_name = self.xsd_path.stem
            root = Node(f"Schema: {schema_name}")
            
            # Add root elements
            if self.structure['elements']:
                for element_data in self.structure['elements']:
                    self._add_element_data_to_anytree(root, element_data)
            
            # Add global elements
            if self.structure['global_elements']:
                for name, element_data in self.structure['global_elements'].items():
                    self._add_element_data_to_anytree(root, element_data)
        
        return root
    
    def _add_element_to_anytree(self, parent: Node, element) -> None:
        """Add XSDElement to anytree structure."""
        # Create node name with type info
        node_name = element.name
        if element.type:
            node_name += f" : {element.type}"
        
        if element.min_occurs != "1" or element.max_occurs != "1":
            node_name += f" [{element.min_occurs}..{element.max_occurs}]"
        
        element_node = Node(node_name, parent=parent)
        
        # Add children
        for child in element.children:
            self._add_element_to_anytree(element_node, child)
    
    def _add_element_data_to_anytree(self, parent: Node, element_data: Dict[str, Any]) -> None:
        """Add element data to anytree structure."""
        # Create node name with type info
        node_name = element_data['name']
        if element_data['type']:
            node_name += f" : {element_data['type']}"
        
        if element_data['min_occurs'] != "1" or element_data['max_occurs'] != "1":
            node_name += f" [{element_data['min_occurs']}..{element_data['max_occurs']}]"
        
        element_node = Node(node_name, parent=parent)
        
        # Add children
        for child in element_data['children']:
            self._add_element_data_to_anytree(element_node, child)
    
    def export_text_tree(self, output_path: str, element_name: Optional[str] = None) -> None:
        """
        Export tree as text format.
        
        Args:
            output_path: Path for output file
            element_name: Specific element to visualize
        """
        tree = self.create_anytree_structure(element_name)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for pre, fill, node in RenderTree(tree):
                f.write(f"{pre}{node.name}\n")
        
        console.print(f"[bold green]✓[/bold green] Text tree exported: {output_path}")
    
    def export_dot_graph(self, output_path: str, element_name: Optional[str] = None) -> None:
        """
        Export tree as DOT graph format.
        
        Args:
            output_path: Path for output .dot file
            element_name: Specific element to visualize
        """
        tree = self.create_anytree_structure(element_name)
        
        # Use UniqueDotExporter to handle duplicate names
        exporter = UniqueDotExporter(tree)
        exporter.to_dotfile(output_path)
        
        console.print(f"[bold green]✓[/bold green] DOT graph exported: {output_path}")
    
    def export_svg(self, output_path: str, element_name: Optional[str] = None) -> None:
        """
        Export tree as SVG diagram (requires graphviz).
        
        Args:
            output_path: Path for output .svg file
            element_name: Specific element to visualize
        """
        try:
            import graphviz
        except ImportError:
            console.print("[bold red]Error:[/bold red] graphviz package not installed. Install with: pip install graphviz")
            return
        
        # First create DOT file
        dot_path = output_path.replace('.svg', '.dot')
        self.export_dot_graph(dot_path, element_name)
        
        # Convert DOT to SVG
        try:
            with open(dot_path, 'r') as f:
                dot_content = f.read()
            
            graph = graphviz.Source(dot_content)
            graph.format = 'svg'
            graph.render(output_path.replace('.svg', ''), cleanup=True)
            
            # Remove intermediate DOT file
            os.remove(dot_path)
            
            console.print(f"[bold green]✓[/bold green] SVG diagram exported: {output_path}")
            
        except Exception as e:
            console.print(f"[bold red]Error creating SVG:[/bold red] {e}")
    
    def display_console_tree(self, element_name: Optional[str] = None) -> None:
        """
        Display tree in the console using Rich.
        
        Args:
            element_name: Specific element to visualize
        """
        tree = self.create_rich_tree(element_name)
        console.print(tree)
    
    def list_elements(self) -> None:
        """List all available elements in the schema."""
        if not self.structure:
            raise ValueError("Must load schema first")
        
        console.print("[bold cyan]Available Elements:[/bold cyan]")
        
        # Root elements
        if self.structure['elements']:
            console.print("\n[bold]Root Elements:[/bold]")
            for element in self.structure['elements']:
                console.print(f"  • {element['name']}")
        
        # Global elements
        if self.structure['global_elements']:
            console.print("\n[bold]Global Elements:[/bold]")
            for name in self.structure['global_elements']:
                console.print(f"  • {name}")

def main():
    """Main entry point for the tree visualizer."""
    parser = argparse.ArgumentParser(
        description="Create tree visualizations of XSD schema structure",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s schema.xsd --console
  %(prog)s schema1.xsd schema2.xsd --format svg --output combined_tree.svg
  %(prog)s schema.xsd --format svg --output tree.svg
  %(prog)s schema.xsd --element RootElement --format text
  %(prog)s schema.xsd --list-elements
        """
    )
    
    parser.add_argument('xsd_files', nargs='+', help='Path(s) to XSD file(s)')
    parser.add_argument(
        '--format', '-f',
        choices=['console', 'text', 'dot', 'svg'],
        default='console',
        help='Output format (default: console)'
    )
    parser.add_argument(
        '--output', '-o',
        help='Output file path (auto-generated if not specified)'
    )
    parser.add_argument(
        '--element', '-e',
        help='Specific element to visualize (shows all if not specified)'
    )
    parser.add_argument(
        '--combined', '-c',
        action='store_true',
        help='Combine multiple XSD files into a single visualization'
    )
    parser.add_argument(
        '--list-elements', '-l',
        action='store_true',
        help='List all available elements and exit'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        if len(args.xsd_files) > 1 and args.combined:
            # Combined visualization - create a single tree from multiple files
            console.print(f"[bold blue]Creating combined visualization from {len(args.xsd_files)} XSD files[/bold blue]")
            
            # For combined visualization, we'll process the first file and show all files in the title
            visualizer = XSDTreeVisualizer(args.xsd_files[0])
            visualizer.load_schema()
            
            if args.list_elements:
                visualizer.list_elements()
                return
            
            # Create combined output filename
            if args.output is None and args.format != 'console':
                element_suffix = f"_{args.element}" if args.element else ""
                extension = {'text': '.txt', 'dot': '.dot', 'svg': '.svg'}[args.format]
                args.output = f"combined_tree{element_suffix}{extension}"
            
            # Generate visualization with combined title
            if args.format == 'console':
                console.print(f"[dim]Note: Showing structure from {args.xsd_files[0]} (first file)[/dim]")
                visualizer.display_console_tree(args.element)
            elif args.format == 'text':
                visualizer.export_text_tree(args.output, args.element)
            elif args.format == 'dot':
                visualizer.export_dot_graph(args.output, args.element)
            elif args.format == 'svg':
                visualizer.export_svg(args.output, args.element)
        else:
            # Process each XSD file separately
            for i, xsd_file in enumerate(args.xsd_files):
                if len(args.xsd_files) > 1:
                    console.print(f"\n[bold blue]Processing file {i+1}/{len(args.xsd_files)}:[/bold blue] {xsd_file}")
                
                visualizer = XSDTreeVisualizer(xsd_file)
                visualizer.load_schema()
                
                if args.list_elements:
                    visualizer.list_elements()
                    continue
                
                # Determine output path if not specified
                if args.output is None and args.format != 'console':
                    base_name = Path(xsd_file).stem
                    element_suffix = f"_{args.element}" if args.element else ""
                    file_suffix = f"_{i+1}" if len(args.xsd_files) > 1 else ""
                    extension = {'text': '.txt', 'dot': '.dot', 'svg': '.svg'}[args.format]
                    output_path = f"{base_name}_tree{element_suffix}{file_suffix}{extension}"
                else:
                    output_path = args.output
                    # For multiple files with specified output, append file index
                    if len(args.xsd_files) > 1 and args.output:
                        base_path = Path(args.output)
                        output_path = f"{base_path.stem}_{i+1}{base_path.suffix}"
                
                # Generate visualization
                if args.format == 'console':
                    visualizer.display_console_tree(args.element)
                elif args.format == 'text':
                    visualizer.export_text_tree(output_path, args.element)
                elif args.format == 'dot':
                    visualizer.export_dot_graph(output_path, args.element)
                elif args.format == 'svg':
                    visualizer.export_svg(output_path, args.element)
        
        if len(args.xsd_files) > 1 and not args.list_elements:
            console.print(f"\n[bold green]✓ Successfully processed {len(args.xsd_files)} XSD files[/bold green]")
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
