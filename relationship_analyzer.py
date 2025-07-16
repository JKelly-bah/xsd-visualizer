#!/usr/bin/env python3
"""
XSD Relationship Analyzer - Analyzes and explains relationships between multiple XSD files.
Identifies imports, includes, dependencies, namespace relationships, and cross-references.
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from collections import defaultdict

# Add utils directory to path
sys.path.insert(0, str(Path(__file__).parent / 'utils'))

from utils.multi_file_xsd_parser import MultiFileXSDParser, SchemaReference
from rich.console import Console
from rich.table import Table
from rich.tree import Tree
from rich.panel import Panel
from rich.columns import Columns
from rich import print as rprint

console = Console()
logger = logging.getLogger(__name__)

@dataclass
class FileRelationship:
    """Represents a relationship between two XSD files."""
    source_file: str
    target_file: str
    relationship_type: str  # 'import', 'include', 'redefine'
    namespace: Optional[str]
    schema_location: Optional[str]
    resolved_path: Optional[str]

@dataclass
class ComponentDependency:
    """Represents a dependency between schema components."""
    source_file: str
    source_component: str
    source_type: str  # 'element', 'complexType', 'simpleType'
    target_file: str
    target_component: str
    target_type: str
    dependency_type: str  # 'type_reference', 'base_type', 'element_ref'

@dataclass
class NamespaceInfo:
    """Information about a namespace across files."""
    namespace_uri: str
    files: Set[str]
    is_target_namespace: Set[str]  # Files where this is the target namespace
    prefixes: Dict[str, Set[str]]  # prefix -> files using this prefix

class XSDRelationshipAnalyzer:
    """
    Analyzes relationships between multiple XSD files.
    """
    
    def __init__(self, xsd_files: List[str], output_dir: str = "./output"):
        """
        Initialize the relationship analyzer.
        
        Args:
            xsd_files: List of XSD file paths to analyze
            output_dir: Directory for output files
        """
        self.xsd_files = [Path(f) for f in xsd_files]
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Analysis results
        self.file_relationships: List[FileRelationship] = []
        self.component_dependencies: List[ComponentDependency] = []
        self.namespaces: Dict[str, NamespaceInfo] = {}
        self.parsers: Dict[str, MultiFileXSDParser] = {}
        self.structures: Dict[str, Dict[str, Any]] = {}
        
        # Verify all files exist
        for file_path in self.xsd_files:
            if not file_path.exists():
                raise FileNotFoundError(f"XSD file not found: {file_path}")
    
    def analyze_relationships(self) -> None:
        """Perform comprehensive relationship analysis."""
        console.print("[bold blue]Analyzing XSD file relationships...[/bold blue]")
        
        # Parse all files
        with console.status("[bold green]Parsing XSD files..."):
            self._parse_all_files()
        
        # Analyze different types of relationships
        with console.status("[bold green]Analyzing file relationships..."):
            self._analyze_file_relationships()
        
        with console.status("[bold green]Analyzing component dependencies..."):
            self._analyze_component_dependencies()
        
        with console.status("[bold green]Analyzing namespaces..."):
            self._analyze_namespaces()
        
        console.print("[bold green]✓[/bold green] Relationship analysis complete")
    
    def _parse_all_files(self) -> None:
        """Parse all XSD files using multi-file parser."""
        for i, xsd_file in enumerate(self.xsd_files):
            console.print(f"[dim]Parsing {i+1}/{len(self.xsd_files)}:[/dim] {xsd_file.name}")
            
            try:
                parser = MultiFileXSDParser(str(xsd_file))
                structure = parser.parse()
                
                self.parsers[str(xsd_file)] = parser
                self.structures[str(xsd_file)] = structure
                
            except Exception as e:
                logger.warning(f"Failed to parse {xsd_file}: {e}")
                console.print(f"[yellow]Warning:[/yellow] Could not parse {xsd_file}: {e}")
    
    def _analyze_file_relationships(self) -> None:
        """Analyze direct file relationships (imports, includes, redefines)."""
        for file_path, parser in self.parsers.items():
            for ref in parser.schema_references:
                relationship = FileRelationship(
                    source_file=file_path,
                    target_file=ref.resolved_path.name if ref.resolved_path else (ref.schema_location or "Unknown"),
                    relationship_type=ref.reference_type,
                    namespace=ref.namespace,
                    schema_location=ref.schema_location,
                    resolved_path=str(ref.resolved_path) if ref.resolved_path else None
                )
                self.file_relationships.append(relationship)
    
    def _analyze_component_dependencies(self) -> None:
        """Analyze dependencies between schema components across files."""
        # This is a simplified version - a full implementation would track all type references
        for file_path, structure in self.structures.items():
            self._find_dependencies_in_elements(file_path, structure.get('elements', []))
            self._find_dependencies_in_complex_types(file_path, structure.get('complex_types', {}))
            self._find_dependencies_in_simple_types(file_path, structure.get('simple_types', {}))
    
    def _find_dependencies_in_elements(self, file_path: str, elements: List[Dict[str, Any]]) -> None:
        """Find dependencies in element definitions."""
        for element in elements:
            if element.get('type') and ':' in element['type']:
                # This is a namespaced type reference
                prefix, local_name = element['type'].split(':', 1)
                target_file = self._resolve_type_reference(file_path, prefix, local_name)
                
                if target_file and target_file != file_path:
                    dependency = ComponentDependency(
                        source_file=Path(file_path).name,
                        source_component=element['name'],
                        source_type='element',
                        target_file=Path(target_file).name,
                        target_component=local_name,
                        target_type='complexType',  # Simplified assumption
                        dependency_type='type_reference'
                    )
                    self.component_dependencies.append(dependency)
            
            # Recursively check children
            if element.get('children'):
                self._find_dependencies_in_elements(file_path, element['children'])
    
    def _find_dependencies_in_complex_types(self, file_path: str, complex_types: Dict[str, Any]) -> None:
        """Find dependencies in complex type definitions."""
        for type_name, type_def in complex_types.items():
            # Check base type
            if type_def.get('base_type') and ':' in type_def['base_type']:
                prefix, local_name = type_def['base_type'].split(':', 1)
                target_file = self._resolve_type_reference(file_path, prefix, local_name)
                
                if target_file and target_file != file_path:
                    dependency = ComponentDependency(
                        source_file=Path(file_path).name,
                        source_component=type_name,
                        source_type='complexType',
                        target_file=Path(target_file).name,
                        target_component=local_name,
                        target_type='complexType',
                        dependency_type='base_type'
                    )
                    self.component_dependencies.append(dependency)
            
            # Check elements within the complex type
            if type_def.get('elements'):
                self._find_dependencies_in_elements(file_path, type_def['elements'])
    
    def _find_dependencies_in_simple_types(self, file_path: str, simple_types: Dict[str, Any]) -> None:
        """Find dependencies in simple type definitions."""
        for type_name, type_def in simple_types.items():
            if type_def.get('base_type') and ':' in type_def['base_type']:
                prefix, local_name = type_def['base_type'].split(':', 1)
                target_file = self._resolve_type_reference(file_path, prefix, local_name)
                
                if target_file and target_file != file_path:
                    dependency = ComponentDependency(
                        source_file=Path(file_path).name,
                        source_component=type_name,
                        source_type='simpleType',
                        target_file=Path(target_file).name,
                        target_component=local_name,
                        target_type='simpleType',
                        dependency_type='base_type'
                    )
                    self.component_dependencies.append(dependency)
    
    def _resolve_type_reference(self, source_file: str, prefix: str, local_name: str) -> Optional[str]:
        """Resolve a type reference to the file where it's defined."""
        # This is a simplified implementation
        # In practice, you'd need to track namespace mappings more carefully
        
        if source_file in self.parsers:
            parser = self.parsers[source_file]
            
            # Check if this prefix maps to an imported namespace
            for ref in parser.schema_references:
                if ref.reference_type == 'import' and ref.resolved_path:
                    # Check if the target file contains this type
                    target_file = str(ref.resolved_path)
                    if target_file in self.structures:
                        target_structure = self.structures[target_file]
                        
                        # Check in complex types
                        if local_name in target_structure.get('complex_types', {}):
                            return target_file
                        
                        # Check in simple types
                        if local_name in target_structure.get('simple_types', {}):
                            return target_file
        
        return None
    
    def _analyze_namespaces(self) -> None:
        """Analyze namespace usage across files."""
        for file_path, structure in self.structures.items():
            metadata = structure.get('metadata', {})
            
            # Target namespace
            target_ns = metadata.get('target_namespace')
            if target_ns:
                if target_ns not in self.namespaces:
                    self.namespaces[target_ns] = NamespaceInfo(
                        namespace_uri=target_ns,
                        files=set(),
                        is_target_namespace=set(),
                        prefixes=defaultdict(set)
                    )
                self.namespaces[target_ns].files.add(Path(file_path).name)
                self.namespaces[target_ns].is_target_namespace.add(Path(file_path).name)
            
            # All namespaces (including imported ones)
            for ns_uri, prefix in metadata.get('namespaces', {}).items():
                if ns_uri not in self.namespaces:
                    self.namespaces[ns_uri] = NamespaceInfo(
                        namespace_uri=ns_uri,
                        files=set(),
                        is_target_namespace=set(),
                        prefixes=defaultdict(set)
                    )
                self.namespaces[ns_uri].files.add(Path(file_path).name)
                self.namespaces[ns_uri].prefixes[prefix].add(Path(file_path).name)
    
    def display_relationship_summary(self) -> None:
        """Display a comprehensive summary of relationships."""
        console.print("\n" + "="*80)
        console.print(Panel.fit("[bold cyan]XSD Relationship Analysis Summary[/bold cyan]", border_style="cyan"))
        
        # Overview table
        overview_table = Table(title="Analysis Overview")
        overview_table.add_column("Metric", style="cyan")
        overview_table.add_column("Count", style="magenta")
        
        overview_table.add_row("Total Files", str(len(self.xsd_files)))
        overview_table.add_row("File Relationships", str(len(self.file_relationships)))
        overview_table.add_row("Component Dependencies", str(len(self.component_dependencies)))
        overview_table.add_row("Unique Namespaces", str(len(self.namespaces)))
        
        console.print(overview_table)
        console.print()
        
        # File relationships
        self._display_file_relationships()
        
        # Component dependencies
        self._display_component_dependencies()
        
        # Namespace analysis
        self._display_namespace_analysis()
        
        # Dependency graph
        self._display_dependency_graph()
    
    def _display_file_relationships(self) -> None:
        """Display file-level relationships."""
        if not self.file_relationships:
            console.print("[yellow]No direct file relationships found.[/yellow]\n")
            return
        
        console.print(Panel.fit("[bold green]File Relationships[/bold green]", border_style="green"))
        
        # Group by relationship type
        by_type = defaultdict(list)
        for rel in self.file_relationships:
            by_type[rel.relationship_type].append(rel)
        
        for rel_type, relationships in by_type.items():
            console.print(f"\n[bold]{rel_type.upper()} Relationships:[/bold]")
            
            table = Table()
            table.add_column("Source File", style="cyan")
            table.add_column("Target File", style="green") 
            table.add_column("Namespace", style="yellow")
            table.add_column("Schema Location", style="dim")
            
            for rel in relationships:
                table.add_row(
                    Path(rel.source_file).name,
                    rel.target_file or "N/A",
                    rel.namespace or "N/A",
                    rel.schema_location or "N/A"
                )
            
            console.print(table)
        
        console.print()
    
    def _display_component_dependencies(self) -> None:
        """Display component-level dependencies."""
        if not self.component_dependencies:
            console.print("[yellow]No component dependencies found.[/yellow]\n")
            return
        
        console.print(Panel.fit("[bold green]Component Dependencies[/bold green]", border_style="green"))
        
        # Group by dependency type
        by_type = defaultdict(list)
        for dep in self.component_dependencies:
            by_type[dep.dependency_type].append(dep)
        
        for dep_type, dependencies in by_type.items():
            console.print(f"\n[bold]{dep_type.replace('_', ' ').title()}s:[/bold]")
            
            table = Table()
            table.add_column("Source", style="cyan")
            table.add_column("Source Type", style="dim cyan")
            table.add_column("→", style="bold white")
            table.add_column("Target", style="green")
            table.add_column("Target Type", style="dim green")
            
            for dep in dependencies:
                table.add_row(
                    f"{dep.source_file}::{dep.source_component}",
                    dep.source_type,
                    "→",
                    f"{dep.target_file}::{dep.target_component}",
                    dep.target_type
                )
            
            console.print(table)
        
        console.print()
    
    def _display_namespace_analysis(self) -> None:
        """Display namespace analysis."""
        if not self.namespaces:
            console.print("[yellow]No namespaces found.[/yellow]\n")
            return
        
        console.print(Panel.fit("[bold green]Namespace Analysis[/bold green]", border_style="green"))
        
        table = Table()
        table.add_column("Namespace", style="cyan")
        table.add_column("Files Using", style="green")
        table.add_column("Target NS In", style="yellow")
        table.add_column("Common Prefixes", style="magenta")
        
        for ns_uri, info in self.namespaces.items():
            # Display namespace (truncated if too long)
            display_ns = ns_uri
            if len(display_ns) > 50:
                display_ns = display_ns[:47] + "..."
            
            files_using = ", ".join(sorted(info.files))
            target_files = ", ".join(sorted(info.is_target_namespace)) if info.is_target_namespace else "None"
            
            # Get most common prefixes
            prefix_list = []
            for prefix, files in info.prefixes.items():
                if prefix:  # Skip empty prefixes
                    prefix_list.append(f"{prefix} ({len(files)})")
            prefixes_str = ", ".join(prefix_list) if prefix_list else "None"
            
            table.add_row(display_ns, files_using, target_files, prefixes_str)
        
        console.print(table)
        console.print()
    
    def _display_dependency_graph(self) -> None:
        """Display a tree view of file dependencies."""
        console.print(Panel.fit("[bold green]Dependency Graph[/bold green]", border_style="green"))
        
        # Build dependency tree
        tree = Tree("[bold magenta]XSD Files Dependency Graph[/bold magenta]")
        
        # Find root files (files that are not imported by others)
        imported_files = {rel.target_file for rel in self.file_relationships}
        root_files = [f for f in self.xsd_files if f.name not in imported_files]
        
        if not root_files:
            root_files = self.xsd_files[:1]  # If circular dependencies, start with first file
        
        # Add each root file and its dependencies
        for root_file in root_files:
            self._add_file_to_tree(tree, str(root_file), set())
        
        console.print(tree)
        console.print()
    
    def _add_file_to_tree(self, parent_tree: Tree, file_path: str, visited: Set[str]) -> None:
        """Recursively add file and its dependencies to tree."""
        file_name = Path(file_path).name
        
        if file_path in visited:
            parent_tree.add(f"[dim]{file_name} (circular reference)[/dim]")
            return
        
        visited.add(file_path)
        
        # Find relationships from this file
        file_relationships = [rel for rel in self.file_relationships if rel.source_file == file_path]
        
        if not file_relationships:
            parent_tree.add(f"[green]{file_name}[/green]")
        else:
            file_branch = parent_tree.add(f"[green]{file_name}[/green]")
            
            for rel in file_relationships:
                rel_type_color = {
                    'import': 'cyan',
                    'include': 'yellow',
                    'redefine': 'red'
                }.get(rel.relationship_type, 'white')
                
                target_display = f"[{rel_type_color}]{rel.target_file}[/{rel_type_color}] ({rel.relationship_type})"
                if rel.namespace:
                    target_display += f" [dim]({rel.namespace})[/dim]"
                
                rel_branch = file_branch.add(target_display)
                
                # Recursively add target file if it exists in our file list
                if rel.resolved_path:
                    self._add_file_to_tree(rel_branch, rel.resolved_path, visited.copy())
    
    def generate_relationship_report(self) -> None:
        """Generate a detailed relationship report."""
        console.print("[bold blue]Generating relationship report...[/bold blue]")
        
        report_data = {
            'analysis_summary': {
                'total_files': len(self.xsd_files),
                'file_relationships': len(self.file_relationships),
                'component_dependencies': len(self.component_dependencies),
                'unique_namespaces': len(self.namespaces)
            },
            'files_analyzed': [str(f) for f in self.xsd_files],
            'file_relationships': [asdict(rel) for rel in self.file_relationships],
            'component_dependencies': [asdict(dep) for dep in self.component_dependencies],
            'namespaces': {
                ns_uri: {
                    'files': list(info.files),
                    'is_target_namespace': list(info.is_target_namespace),
                    'prefixes': {prefix: list(files) for prefix, files in info.prefixes.items()}
                }
                for ns_uri, info in self.namespaces.items()
            }
        }
        
        # Export JSON report
        json_path = self.output_dir / "relationship_analysis.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        console.print(f"[bold green]✓[/bold green] JSON report created: {json_path}")
        
        # Export text report
        self._generate_text_report(report_data)
    
    def _generate_text_report(self, report_data: Dict[str, Any]) -> None:
        """Generate a human-readable text report."""
        text_path = self.output_dir / "relationship_analysis.txt"
        
        with open(text_path, 'w', encoding='utf-8') as f:
            f.write("XSD RELATIONSHIP ANALYSIS REPORT\n")
            f.write("=" * 50 + "\n\n")
            
            # Summary
            f.write("ANALYSIS SUMMARY\n")
            f.write("-" * 20 + "\n")
            summary = report_data['analysis_summary']
            f.write(f"Total Files Analyzed: {summary['total_files']}\n")
            f.write(f"File Relationships: {summary['file_relationships']}\n")
            f.write(f"Component Dependencies: {summary['component_dependencies']}\n")
            f.write(f"Unique Namespaces: {summary['unique_namespaces']}\n\n")
            
            # Files analyzed
            f.write("FILES ANALYZED\n")
            f.write("-" * 20 + "\n")
            for file_path in report_data['files_analyzed']:
                f.write(f"• {file_path}\n")
            f.write("\n")
            
            # File relationships
            if report_data['file_relationships']:
                f.write("FILE RELATIONSHIPS\n")
                f.write("-" * 20 + "\n")
                for rel in report_data['file_relationships']:
                    f.write(f"{Path(rel['source_file']).name} --{rel['relationship_type']}--> {rel['target_file']}\n")
                    if rel['namespace']:
                        f.write(f"  Namespace: {rel['namespace']}\n")
                    if rel['schema_location']:
                        f.write(f"  Location: {rel['schema_location']}\n")
                    f.write("\n")
            
            # Component dependencies
            if report_data['component_dependencies']:
                f.write("COMPONENT DEPENDENCIES\n")
                f.write("-" * 20 + "\n")
                for dep in report_data['component_dependencies']:
                    f.write(f"{dep['source_file']}::{dep['source_component']} ({dep['source_type']}) ")
                    f.write(f"--{dep['dependency_type']}--> ")
                    f.write(f"{dep['target_file']}::{dep['target_component']} ({dep['target_type']})\n")
                f.write("\n")
            
            # Namespaces
            if report_data['namespaces']:
                f.write("NAMESPACE ANALYSIS\n")
                f.write("-" * 20 + "\n")
                for ns_uri, info in report_data['namespaces'].items():
                    f.write(f"Namespace: {ns_uri}\n")
                    f.write(f"  Used in files: {', '.join(info['files'])}\n")
                    if info['is_target_namespace']:
                        f.write(f"  Target namespace in: {', '.join(info['is_target_namespace'])}\n")
                    if info['prefixes']:
                        f.write("  Prefixes:\n")
                        for prefix, files in info['prefixes'].items():
                            if prefix:
                                f.write(f"    {prefix}: {', '.join(files)}\n")
                    f.write("\n")
        
        console.print(f"[bold green]✓[/bold green] Text report created: {text_path}")

def main():
    """Main entry point for the relationship analyzer."""
    parser = argparse.ArgumentParser(
        description="Analyze relationships between multiple XSD files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s schema1.xsd schema2.xsd schema3.xsd
  %(prog)s *.xsd --output-dir ./analysis
  %(prog)s main.xsd imports/*.xsd --report-only
  %(prog)s library/*.xsd --verbose
        """
    )
    
    parser.add_argument(
        'xsd_files',
        nargs='+',
        help='XSD files to analyze relationships between'
    )
    parser.add_argument(
        '--output-dir', '-o',
        default='./output',
        help='Output directory for reports (default: ./output)'
    )
    parser.add_argument(
        '--report-only', '-r',
        action='store_true',
        help='Generate reports only, skip console display'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    else:
        logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
    
    try:
        console.print(f"[bold cyan]XSD Relationship Analyzer[/bold cyan]")
        console.print(f"Analyzing {len(args.xsd_files)} XSD files...\n")
        
        analyzer = XSDRelationshipAnalyzer(args.xsd_files, args.output_dir)
        analyzer.analyze_relationships()
        
        if not args.report_only:
            analyzer.display_relationship_summary()
        
        analyzer.generate_relationship_report()
        
        console.print(f"\n[bold green]✓ Analysis complete![/bold green] Reports saved to: {args.output_dir}")
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        if args.verbose:
            console.print_exception()
        sys.exit(1)

if __name__ == "__main__":
    main()
