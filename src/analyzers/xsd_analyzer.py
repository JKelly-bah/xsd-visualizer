#!/usr/bin/env python3
"""
Main XSD Analyzer - Comprehensive analysis tool for XSD files.
Generates multiple output formats including HTML documentation, tree visualizations, and dependency maps.
"""

import argparse
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
import sys
import os

# Add utils directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'utils'))

from src.parsers.xsd_parser import XSDParser
from src.parsers.multi_file_xsd_parser import MultiFileXSDParser
from src.generators.html_generator import HTMLGenerator
from rich.console import Console
from rich.progress import track
from rich.table import Table
from rich import print as rprint

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

console = Console()

class XSDAnalyzer:
    """
    Main analyzer class that coordinates parsing and output generation.
    """
    
    def __init__(self, xsd_path: str, output_dir: str = "./output", multi_file: bool = False):
        """
        Initialize analyzer.
        
        Args:
            xsd_path: Path to XSD file to analyze
            output_dir: Directory for output files
            multi_file: Whether to use multi-file parser for imports/includes
        """
        self.xsd_path = Path(xsd_path)
        self.output_dir = Path(output_dir)
        self.multi_file = multi_file
        self.structure: Optional[Dict[str, Any]] = None
        self.parser: Optional[XSDParser] = None
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        if not self.xsd_path.exists():
            raise FileNotFoundError(f"XSD file not found: {xsd_path}")
    
    def analyze(self) -> Dict[str, Any]:
        """
        Perform complete analysis of the XSD file.
        
        Returns:
            Parsed structure dictionary
        """
        parser_type = "multi-file" if self.multi_file else "single-file"
        console.print(f"[bold blue]Analyzing XSD file ({parser_type}):[/bold blue] {self.xsd_path}")
        
        # Parse XSD file with appropriate parser
        with console.status("[bold green]Parsing XSD file..."):
            if self.multi_file:
                self.parser = MultiFileXSDParser(str(self.xsd_path))
                console.print("[yellow]Using multi-file parser for imports/includes[/yellow]")
            else:
                self.parser = XSDParser(str(self.xsd_path))
                console.print("[yellow]Using single-file parser[/yellow]")
                
            self.structure = self.parser.parse()
        
        console.print("[bold green]✓[/bold green] XSD parsing complete")
        
        # Show multi-file info if available
        if self.multi_file and isinstance(self.parser, MultiFileXSDParser):
            summary = self.parser.get_file_summary()
            console.print(f"[dim]Processed {len(summary)} schema files[/dim]")
            
        return self.structure
    
    def generate_html_documentation(self) -> None:
        """Generate comprehensive HTML documentation."""
        if not self.structure:
            raise ValueError("Must run analyze() first")
        
        console.print("[bold blue]Generating HTML documentation...[/bold blue]")
        
        html_output_dir = self.output_dir / "html"
        
        with console.status("[bold green]Creating HTML documentation..."):
            generator = HTMLGenerator(self.structure)
            generator.generate_documentation(str(html_output_dir))
        
        index_path = html_output_dir / "index.html"
        console.print(f"[bold green]✓[/bold green] HTML documentation created: {index_path}")
    
    def generate_json_export(self) -> None:
        """Export structure as JSON for programmatic use."""
        if not self.structure:
            raise ValueError("Must run analyze() first")
        
        console.print("[bold blue]Exporting JSON structure...[/bold blue]")
        
        json_path = self.output_dir / "structure.json"
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.structure, f, indent=2, ensure_ascii=False)
        
        console.print(f"[bold green]✓[/bold green] JSON export created: {json_path}")
    
    def generate_text_summary(self) -> None:
        """Generate a text-based summary of the schema."""
        if not self.structure:
            raise ValueError("Must run analyze() first")
        
        console.print("[bold blue]Generating text summary...[/bold blue]")
        
        summary_path = self.output_dir / "summary.txt"
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            self._write_text_summary(f)
        
        console.print(f"[bold green]✓[/bold green] Text summary created: {summary_path}")
    
    def _write_text_summary(self, file) -> None:
        """Write detailed text summary to file."""
        if self.structure is None:
            file.write("ERROR: No structure data available\n")
            return
        
        # Validate structure has required keys
        required_keys = ['metadata', 'elements', 'global_elements', 'complex_types', 'simple_types']
        for key in required_keys:
            if key not in self.structure:
                file.write(f"ERROR: Missing required structure key: {key}\n")
                return
            
        metadata = self.structure['metadata']
        if 'statistics' not in metadata:
            file.write("ERROR: Missing statistics in metadata\n")
            return
            
        stats = metadata['statistics']
        
        file.write("XSD SCHEMA ANALYSIS SUMMARY\n")
        file.write("=" * 50 + "\n\n")
        
        file.write(f"File: {metadata['file_path']}\n")
        if metadata['target_namespace']:
            file.write(f"Target Namespace: {metadata['target_namespace']}\n")
        file.write(f"Namespaces: {len(metadata['namespaces'])}\n\n")
        
        file.write("STATISTICS\n")
        file.write("-" * 20 + "\n")
        file.write(f"Total Elements: {stats['total_elements']}\n")
        file.write(f"Complex Types: {stats['total_complex_types']}\n")
        file.write(f"Simple Types: {stats['total_simple_types']}\n")
        file.write(f"Maximum Depth: {stats['max_depth']}\n")
        file.write(f"Total Attributes: {stats['total_attributes']}\n\n")
        
        # Root elements
        if self.structure['elements']:
            file.write("ROOT ELEMENTS\n")
            file.write("-" * 20 + "\n")
            for element in self.structure['elements']:
                self._write_element_summary(file, element, 0)
            file.write("\n")
        
        # Global elements
        if self.structure['global_elements']:
            file.write("GLOBAL ELEMENTS\n")
            file.write("-" * 20 + "\n")
            for name, element in self.structure['global_elements'].items():
                self._write_element_summary(file, element, 0)
            file.write("\n")
        
        # Complex types
        if self.structure['complex_types']:
            file.write("COMPLEX TYPES\n")
            file.write("-" * 20 + "\n")
            for name, complex_type in self.structure['complex_types'].items():
                file.write(f"Type: {name}\n")
                if complex_type['documentation']:
                    file.write(f"  Documentation: {complex_type['documentation']}\n")
                file.write(f"  Elements: {len(complex_type['elements'])}\n")
                file.write(f"  Attributes: {len(complex_type['attributes'])}\n")
                file.write("\n")
        
        # Simple types
        if self.structure['simple_types']:
            file.write("SIMPLE TYPES\n")
            file.write("-" * 20 + "\n")
            for name, simple_type in self.structure['simple_types'].items():
                file.write(f"Type: {name}\n")
                if simple_type['base_type']:
                    file.write(f"  Base Type: {simple_type['base_type']}\n")
                if simple_type['enumerations']:
                    file.write(f"  Enumerations: {len(simple_type['enumerations'])}\n")
                if simple_type['documentation']:
                    file.write(f"  Documentation: {simple_type['documentation']}\n")
                file.write("\n")
    
    def _write_element_summary(self, file, element: Dict[str, Any], depth: int) -> None:
        """Write element summary with proper indentation."""
        indent = "  " * depth
        
        file.write(f"{indent}{element['name']}")
        if element['type']:
            file.write(f" : {element['type']}")
        
        occurs = ""
        if element['min_occurs'] != "1" or element['max_occurs'] != "1":
            occurs = f" [{element['min_occurs']}..{element['max_occurs']}]"
        file.write(f"{occurs}\n")
        
        if element['documentation']:
            file.write(f"{indent}  Documentation: {element['documentation']}\n")
        
        if element['attributes']:
            file.write(f"{indent}  Attributes: {len(element['attributes'])}\n")
        
        # Recursively write children
        for child in element['children']:
            self._write_element_summary(file, child, depth + 1)
    
    def display_summary_table(self) -> None:
        """Display a summary table in the console."""
        if not self.structure:
            raise ValueError("Must run analyze() first")
        
        stats = self.structure['metadata']['statistics']
        
        table = Table(title="XSD Analysis Summary")
        table.add_column("Metric", style="cyan", no_wrap=True)
        table.add_column("Count", style="magenta")
        
        table.add_row("Total Elements", str(stats['total_elements']))
        table.add_row("Complex Types", str(stats['total_complex_types']))
        table.add_row("Simple Types", str(stats['total_simple_types']))
        table.add_row("Maximum Depth", str(stats['max_depth']))
        table.add_row("Total Attributes", str(stats['total_attributes']))
        
        console.print(table)
    
    def run_complete_analysis(self, formats: Optional[List[str]] = None) -> None:
        """
        Run complete analysis with all requested output formats.
        
        Args:
            formats: List of output formats ('html', 'json', 'text', 'summary')
        """
        if formats is None:
            formats = ['html', 'json', 'text', 'summary']
        
        # Analyze XSD
        self.analyze()
        
        # Generate requested outputs
        if formats:  # Check that formats is not None
            for format_type in track(formats, description="Generating outputs..."):
                if format_type == 'html':
                    self.generate_html_documentation()
                elif format_type == 'json':
                    self.generate_json_export()
                elif format_type == 'text':
                    self.generate_text_summary()
                elif format_type == 'summary':
                    self.display_summary_table()
        
        console.print(f"\n[bold green]✓ Analysis complete![/bold green] Output directory: {self.output_dir}")

def main():
    """Main entry point for the XSD analyzer."""
    parser = argparse.ArgumentParser(
        description="Analyze XSD files and generate comprehensive documentation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s schema.xsd
  %(prog)s schema1.xsd schema2.xsd schema3.xsd
  %(prog)s *.xsd --output-dir ./docs
  %(prog)s schema1.xsd schema2.xsd --combined
  %(prog)s schema.xsd --formats html json
  %(prog)s schema.xsd --summary-only
        """
    )
    
    parser.add_argument('xsd_files', nargs='+', help='Path(s) to XSD file(s) to analyze')
    parser.add_argument(
        '--output-dir', '-o', 
        default='./output',
        help='Output directory (default: ./output)'
    )
    parser.add_argument(
        '--formats', '-f',
        nargs='+',
        choices=['html', 'json', 'text', 'summary'],
        default=['html', 'json', 'text'],
        help='Output formats to generate (default: html json text)'
    )
    parser.add_argument(
        '--summary-only', '-s',
        action='store_true',
        help='Only display summary table, no file output'
    )
    parser.add_argument(
        '--multi-file', '-m',
        action='store_true',
        help='Enable multi-file parsing for schemas with imports/includes'
    )
    parser.add_argument(
        '--combined', '-c',
        action='store_true',
        help='Combine multiple XSD files into a single analysis output'
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
            # Process all files together as a combined analysis
            console.print(f"[bold blue]Processing {len(args.xsd_files)} XSD files as combined analysis[/bold blue]")
            
            # For combined analysis, we'll use the multi-file parser on the first file
            # and let it discover the others through imports/includes
            analyzer = XSDAnalyzer(args.xsd_files[0], args.output_dir, multi_file=True)
            
            if args.summary_only:
                analyzer.analyze()
                analyzer.display_summary_table()
            else:
                analyzer.run_complete_analysis(args.formats)
                
        else:
            # Process each XSD file separately
            for i, xsd_file in enumerate(args.xsd_files):
                if len(args.xsd_files) > 1:
                    console.print(f"\n[bold blue]Processing file {i+1}/{len(args.xsd_files)}:[/bold blue] {xsd_file}")
                
                # Create output directory for each file if multiple files
                if len(args.xsd_files) > 1 and not args.combined:
                    file_output_dir = Path(args.output_dir) / Path(xsd_file).stem
                else:
                    file_output_dir = args.output_dir
                    
                analyzer = XSDAnalyzer(xsd_file, str(file_output_dir), multi_file=args.multi_file)
                
                if args.summary_only:
                    analyzer.analyze()
                    analyzer.display_summary_table()
                else:
                    analyzer.run_complete_analysis(args.formats)
                    
        if len(args.xsd_files) > 1:
            console.print(f"\n[bold green]✓ Successfully processed {len(args.xsd_files)} XSD files[/bold green]")
            console.print(f"[dim]Output written to: {args.output_dir}[/dim]")
            
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
