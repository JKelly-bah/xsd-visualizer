#!/usr/bin/env python3
"""
Selective XSD Analyzer - Cherry-pick specific elements from multiple XSD files.
Allows analyzing specific components from different schema files.
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import List, Optional

from utils.selective_xsd_parser import SelectiveXSDParser, SelectionCriteria
from utils.html_generator import HTMLGenerator
from rich.console import Console
from rich.table import Table
from rich.tree import Tree
from rich import print as rprint

console = Console()
logger = logging.getLogger(__name__)

class SelectiveAnalyzer:
    """
    Main analyzer for selective XSD component analysis.
    """
    
    def __init__(self, output_dir: str = "./output"):
        """Initialize the selective analyzer."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.parser = SelectiveXSDParser()
        self.structure = None
    
    def add_file_selection(self, 
                          file_path: str,
                          elements: Optional[List[str]] = None,
                          complex_types: Optional[List[str]] = None,
                          simple_types: Optional[List[str]] = None,
                          namespaces: Optional[List[str]] = None,
                          include_dependencies: bool = True) -> None:
        """Add a file selection to the analysis."""
        self.parser.add_file_selection(
            file_path=file_path,
            elements=elements,
            complex_types=complex_types,
            simple_types=simple_types,
            namespaces=namespaces,
            include_dependencies=include_dependencies
        )
        
        # Log what was added
        selections = []
        if elements: selections.append(f"{len(elements)} elements")
        if complex_types: selections.append(f"{len(complex_types)} complex types")
        if simple_types: selections.append(f"{len(simple_types)} simple types")
        if namespaces: selections.append(f"{len(namespaces)} namespaces")
        
        console.print(f"[green]✓[/green] Added selections from [bold]{file_path}[/bold]: {', '.join(selections)}")
    
    def analyze(self) -> dict:
        """Perform the selective analysis."""
        console.print("[bold blue]Starting selective XSD analysis...[/bold blue]")
        
        with console.status("[bold green]Parsing selected components..."):
            self.structure = self.parser.parse_selections()
        
        console.print("[bold green]✓[/bold green] Selective analysis complete")
        return self.structure
    
    def display_summary(self) -> None:
        """Display a summary of the selective analysis."""
        if not self.structure:
            console.print("[red]No analysis results available. Run analyze() first.[/red]")
            return
        
        console.print("\n[bold]Selective Analysis Summary[/bold]")
        
        # Main summary table
        summary_table = Table(title="Selected Components Summary")
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Count", justify="right", style="green")
        
        metadata = self.structure.get('metadata', {})
        summary_table.add_row("Source Files", str(metadata.get('total_files', 0)))
        summary_table.add_row("Selected Components", str(metadata.get('selected_components', 0)))
        summary_table.add_row("Elements", str(len(self.structure.get('elements', {}))))
        summary_table.add_row("Complex Types", str(len(self.structure.get('complex_types', {}))))
        summary_table.add_row("Simple Types", str(len(self.structure.get('simple_types', {}))))
        
        console.print(summary_table)
        
        # File breakdown
        selection_summary = self.structure.get('selection_summary', {})
        if selection_summary:
            console.print("\n[bold]Selection by File[/bold]")
            
            file_table = Table()
            file_table.add_column("File", style="cyan")
            file_table.add_column("Elements", justify="right", style="green")
            file_table.add_column("Complex Types", justify="right", style="blue")
            file_table.add_column("Simple Types", justify="right", style="yellow")
            
            for file_path, counts in selection_summary.items():
                file_table.add_row(
                    Path(file_path).name,
                    str(counts.get('elements', 0)),
                    str(counts.get('complex_types', 0)),
                    str(counts.get('simple_types', 0))
                )
            
            console.print(file_table)
        
        # Selection details
        parser_summary = self.parser.get_selection_summary()
        if parser_summary:
            console.print("\n[bold]Selection Details[/bold]")
            
            for file_path, details in parser_summary.items():
                console.print(f"\n[cyan]{Path(file_path).name}[/cyan]:")
                
                if details['elements']:
                    console.print(f"  [green]Elements:[/green] {', '.join(details['elements'])}")
                if details['complex_types']:
                    console.print(f"  [blue]Complex Types:[/blue] {', '.join(details['complex_types'])}")
                if details['simple_types']:
                    console.print(f"  [yellow]Simple Types:[/yellow] {', '.join(details['simple_types'])}")
                if details['namespaces']:
                    console.print(f"  [magenta]Namespaces:[/magenta] {', '.join(details['namespaces'])}")
    
    def generate_html_documentation(self) -> None:
        """Generate HTML documentation for selected components."""
        if not self.structure:
            raise ValueError("Must run analyze() first")
        
        console.print("[bold blue]Generating HTML documentation for selections...[/bold blue]")
        
        html_output_dir = self.output_dir / "html"
        generator = HTMLGenerator(self.structure)  # Don't pass template_dir to constructor
        generator.generate_documentation(str(html_output_dir))
        
        console.print(f"[bold green]✓[/bold green] HTML documentation created: {html_output_dir / 'index.html'}")
    
    def export_json(self) -> None:
        """Export the selective analysis results to JSON."""
        if not self.structure:
            raise ValueError("Must run analyze() first")
        
        json_path = self.output_dir / "selective_analysis.json"
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.structure, f, indent=2, default=str)
        
        console.print(f"[bold green]✓[/bold green] JSON export created: {json_path}")

def parse_component_list(value: str) -> List[str]:
    """Parse a comma-separated list of component names."""
    if not value:
        return []
    return [name.strip() for name in value.split(',') if name.strip()]

def main():
    """Main entry point for selective XSD analysis."""
    parser = argparse.ArgumentParser(
        description="Selective XSD Analyzer - Cherry-pick components from multiple XSD files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Select specific elements from a file
  %(prog)s file1.xsd --elements BookType,AuthorType
  
  # Select from multiple files
  %(prog)s file1.xsd --elements Book file2.xsd --complex-types PersonType
  
  # Select entire namespaces
  %(prog)s schema.xsd --namespaces "http://example.com/library"
  
  # Complex selection with HTML output
  %(prog)s main.xsd --elements Library --complex-types BookType \\
           other.xsd --namespaces "http://example.com/common" \\
           --output-dir ./selected --formats html
        """
    )
    
    parser.add_argument(
        'selections',
        nargs='+',
        help='XSD files and their selections (file.xsd --elements el1,el2 --types type1,type2)'
    )
    parser.add_argument(
        '--output-dir', '-o',
        default='./output',
        help='Output directory (default: ./output)'
    )
    parser.add_argument(
        '--formats', '-f',
        nargs='+',
        choices=['html', 'json', 'summary'],
        default=['summary'],
        help='Output formats to generate (default: summary)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    
    # Parse the complex command line arguments
    # This is a simplified version - in practice, you'd want more sophisticated parsing
    console.print("[yellow]Note: This is a demonstration tool. For complex selections, consider using the Python API directly.[/yellow]")
    console.print("[yellow]Example: See the demo script for detailed usage examples.[/yellow]")
    
    try:
        analyzer = SelectiveAnalyzer(args.output_dir)
        
        # For now, just analyze the first file completely as a demo
        if args.selections:
            first_file = args.selections[0]
            console.print(f"[yellow]Demo: Analyzing all components from {first_file}[/yellow]")
            analyzer.add_file_selection(first_file, namespaces=["*"])  # Select all
        
        # Perform analysis
        analyzer.analyze()
        
        # Generate requested outputs
        if 'summary' in args.formats:
            analyzer.display_summary()
        
        if 'html' in args.formats:
            analyzer.generate_html_documentation()
        
        if 'json' in args.formats:
            analyzer.export_json()
            
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        if args.verbose:
            console.print_exception()
        sys.exit(1)

if __name__ == "__main__":
    main()
