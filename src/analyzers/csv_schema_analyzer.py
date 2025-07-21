#!/usr/bin/env python3
"""
CSV Schema Analyzer - Analyzes XSD files against CSV-defined schema requirements.
Supports dynamic depth paths (1-8 levels) with flexible element/attribute targeting.
"""

import argparse
import csv
import sys
import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Union
import logging
from dataclasses import dataclass, field
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import track
from rich import print as rprint
import json

# Add utils directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'utils'))

from src.parsers.multi_file_xsd_parser import MultiFileXSDParser

console = Console()
logger = logging.getLogger(__name__)

@dataclass
class SchemaRequirement:
    """Represents a single schema requirement from CSV."""
    id: str
    xpath: str
    description: str
    levels: List[str]  # level1 through level8, filtered to remove empty
    attribute: Optional[str] = None
    expected_type: Optional[str] = None
    required: bool = False
    validation_rules: Optional[str] = None
    business_purpose: Optional[str] = None
    
    def get_target_path(self) -> str:
        """Get the complete path as a string."""
        path = "/".join(filter(None, self.levels))
        if self.attribute:
            path += f"/@{self.attribute}"
        return path
    
    def get_depth(self) -> int:
        """Get the depth of this requirement."""
        return len([level for level in self.levels if level])
    
    def is_attribute_target(self) -> bool:
        """Check if this requirement targets an attribute."""
        return self.attribute is not None

@dataclass
class AnalysisResult:
    """Results of analyzing a requirement against XSD files."""
    requirement: SchemaRequirement
    status: str  # 'found', 'missing', 'mismatch', 'error'
    found_in_file: Optional[str] = None
    found_path: Optional[str] = None
    actual_type: Optional[str] = None
    actual_required: Optional[bool] = None
    issues: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)

class CSVSchemaAnalyzer:
    """
    Analyzes XSD files against CSV-defined schema requirements.
    """
    
    def __init__(self, xsd_files: List[str], csv_file: str):
        """
        Initialize the analyzer.
        
        Args:
            xsd_files: List of XSD file paths to analyze
            csv_file: Path to CSV file with schema requirements
        """
        self.xsd_files = [Path(f) for f in xsd_files]
        self.csv_file = Path(csv_file)
        self.requirements: List[SchemaRequirement] = []
        self.results: List[AnalysisResult] = []
        self.parser: Optional[MultiFileXSDParser] = None
        self.schema_data: Optional[Dict[str, Any]] = None
        
        # Validate input files
        for xsd_file in self.xsd_files:
            if not xsd_file.exists():
                raise FileNotFoundError(f"XSD file not found: {xsd_file}")
        
        if not self.csv_file.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_file}")
    
    def load_csv_requirements(self) -> None:
        """Load schema requirements from CSV file."""
        console.print(f"[bold blue]Loading CSV requirements from:[/bold blue] {self.csv_file}")
        
        self.requirements = []
        
        with open(self.csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row_num, row in enumerate(reader, start=2):  # Start at 2 for header
                try:
                    # Extract level columns
                    levels = []
                    for i in range(1, 9):  # level1 through level8
                        level_key = f"level{i}"
                        if level_key in row and row[level_key] and str(row[level_key]).strip():
                            levels.append(str(row[level_key]).strip())
                        else:
                            break  # Stop at first empty level for efficiency
                    
                    if not levels:
                        console.print(f"[yellow]Warning:[/yellow] Row {row_num} has no levels defined, skipping")
                        continue
                    
                    # Create requirement
                    requirement = SchemaRequirement(
                        id=str(row.get('id', f"req_{row_num}")).strip() if row.get('id') else f"req_{row_num}",
                        xpath=str(row.get('xpath', '')).strip() if row.get('xpath') else '',
                        description=str(row.get('description', '')).strip() if row.get('description') else '',
                        levels=levels,
                        attribute=str(row.get('attribute', '')).strip() if row.get('attribute') and str(row.get('attribute')).strip() else None,
                        expected_type=str(row.get('expected_type', '')).strip() if row.get('expected_type') and str(row.get('expected_type')).strip() else None,
                        required=str(row.get('required', '')).lower() in ('true', '1', 'yes') if row.get('required') else False,
                        validation_rules=str(row.get('validation_rules', '')).strip() if row.get('validation_rules') and str(row.get('validation_rules')).strip() else None,
                        business_purpose=str(row.get('business_purpose', '')).strip() if row.get('business_purpose') and str(row.get('business_purpose')).strip() else None
                    )
                    
                    self.requirements.append(requirement)
                    
                except Exception as e:
                    console.print(f"[red]Error processing CSV row {row_num}:[/red] {e}")
                    continue
        
        console.print(f"[bold green]✓[/bold green] Loaded {len(self.requirements)} requirements from CSV")
        
        # Show depth distribution
        depth_counts = {}
        for req in self.requirements:
            depth = req.get_depth()
            depth_counts[depth] = depth_counts.get(depth, 0) + 1
        
        console.print("[dim]Depth distribution:[/dim]")
        for depth in sorted(depth_counts.keys()):
            console.print(f"  [dim]Level {depth}: {depth_counts[depth]} requirement(s)[/dim]")
    
    def load_xsd_schemas(self) -> None:
        """Load and parse XSD schemas."""
        console.print(f"[bold blue]Loading {len(self.xsd_files)} XSD file(s)...[/bold blue]")
        
        # Use multi-file parser with the first file as main
        main_file = str(self.xsd_files[0])
        self.parser = MultiFileXSDParser(main_file)
        
        # For additional files, we'll need to process them separately or create individual parsers
        # Since MultiFileXSDParser handles imports/includes automatically, we'll use multiple parsers
        # if we have multiple unrelated XSD files
        
        with console.status("[bold green]Parsing XSD schemas..."):
            self.schema_data = self.parser.parse()
        
        # If we have multiple XSD files that aren't related via imports/includes,
        # we'll need to parse them separately and merge the data
        if len(self.xsd_files) > 1:
            all_files_data = {'files': {}}
            
            # Start with the main file data
            main_structure = self.parser.get_structure()
            all_files_data['files'][str(self.xsd_files[0])] = main_structure
            
            # Parse additional files
            for xsd_file in self.xsd_files[1:]:
                try:
                    additional_parser = MultiFileXSDParser(str(xsd_file))
                    additional_data = additional_parser.parse()
                    additional_structure = additional_parser.get_structure()
                    all_files_data['files'][str(xsd_file)] = additional_structure
                except Exception as e:
                    console.print(f"[yellow]Warning: Could not parse {xsd_file}: {e}[/yellow]")
                    continue
            
            # Update schema_data to include all files
            if 'files' not in self.schema_data:
                self.schema_data['files'] = {}
            self.schema_data['files'].update(all_files_data['files'])
        else:
            # Single file or related files - use the existing structure
            if 'files' not in self.schema_data:
                main_structure = self.parser.get_structure()
                self.schema_data['files'] = {str(self.xsd_files[0]): main_structure}
        
        console.print(f"[bold green]✓[/bold green] Loaded schema data from {len(self.xsd_files)} file(s)")
        
        # Show schema summary
        total_elements = 0
        total_complex_types = 0
        total_simple_types = 0
        
        for file_data in self.schema_data.get('files', {}).values():
            total_elements += len(file_data.get('elements', {}))
            total_complex_types += len(file_data.get('complex_types', {}))
            total_simple_types += len(file_data.get('simple_types', {}))
        
        console.print(f"[dim]Found {total_elements} elements, "
                     f"{total_complex_types} complex types, "
                     f"{total_simple_types} simple types[/dim]")
    
    def find_path_in_schema(self, requirement: SchemaRequirement) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """
        Find a path in the loaded schema data.
        
        Args:
            requirement: The requirement to search for
            
        Returns:
            Tuple of (found, file_name, element_data)
        """
        if not self.schema_data:
            return False, None, None
        
        target_path = requirement.levels
        target_attribute = requirement.attribute
        
        # Search through all parsed files
        for file_name, file_data in self.schema_data.get('files', {}).items():
            logger.debug(f"Searching in file: {file_name}")
            
            # Get elements and complex types
            elements = file_data.get('elements', {})
            if isinstance(elements, list):
                elements_dict = {}
                for elem in elements:
                    if isinstance(elem, dict) and 'name' in elem:
                        elements_dict[elem['name']] = elem
                elements = elements_dict
            
            global_elements = file_data.get('global_elements', {})
            if isinstance(global_elements, list):
                global_elements_dict = {}
                for elem in global_elements:
                    if isinstance(elem, dict) and 'name' in elem:
                        global_elements_dict[elem['name']] = elem
                global_elements = global_elements_dict
            
            complex_types = file_data.get('complex_types', {})
            
            # Try to find the path starting from root elements
            for element_name, element_data in elements.items():
                found_element = self._find_target_element(target_path, target_attribute, [element_name], element_data, complex_types, file_data)
                if found_element:
                    return True, file_name, found_element
            
            # Also search global elements
            for element_name, element_data in global_elements.items():
                found_element = self._find_target_element(target_path, target_attribute, [element_name], element_data, complex_types, file_data)
                if found_element:
                    return True, file_name, found_element
        
        return False, None, None
    
    def _find_target_element(self, target_path: List[str], target_attribute: Optional[str], 
                           current_path: List[str], element_data: Dict[str, Any], 
                           complex_types: Dict[str, Any], file_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find the target element and return its data."""
        logger.debug(f"Finding target element: {current_path} vs target: {target_path}")
        
        # If we've matched the full path
        if len(current_path) == len(target_path):
            # Check if all path components match
            path_matches = all(current_path[i] == target_path[i] for i in range(len(target_path)))
            
            if path_matches:
                # If we need an attribute, check if element has attributes
                if target_attribute:
                    logger.debug(f"Looking for attribute '{target_attribute}' in element")
                    
                    # Check element's direct attributes
                    if 'attributes' in element_data:
                        for attr in element_data.get('attributes', []):
                            if attr.get('name') == target_attribute:
                                logger.debug(f"Found attribute '{target_attribute}' in element attributes")
                                return attr  # Return the attribute data
                    
                    # If element has a complex type, check its attributes
                    element_type = element_data.get('type', '')
                    if element_type.startswith('tns:'):
                        type_name = element_type[4:]  # Remove 'tns:' prefix
                        if type_name in complex_types:
                            complex_type = complex_types[type_name]
                            for attr in complex_type.get('attributes', []):
                                if attr.get('name') == target_attribute:
                                    logger.debug(f"Found attribute '{target_attribute}' in complex type '{type_name}'")
                                    return attr  # Return the attribute data
                    
                    logger.debug(f"Attribute '{target_attribute}' not found")
                    return None
                else:
                    # No attribute required, return the element itself
                    logger.debug(f"Path matches exactly: {current_path}")
                    return element_data
        
        # If current path is longer than target, no match
        if len(current_path) >= len(target_path):
            return None
        
        # Check if current path matches so far
        for i in range(len(current_path)):
            if i >= len(target_path) or current_path[i] != target_path[i]:
                return None
        
        # We need to continue searching deeper
        # Get the element type and resolve it
        element_type = element_data.get('type', '')
        logger.debug(f"Element '{element_data.get('name')}' has type '{element_type}'")
        
        # If this is a complex type, search its children
        if element_type.startswith('tns:'):
            type_name = element_type[4:]  # Remove 'tns:' prefix
            if type_name in complex_types:
                complex_type = complex_types[type_name]
                logger.debug(f"Searching in complex type '{type_name}' with {len(complex_type.get('elements', []))} elements")
                
                # Search through elements in this complex type
                for child_element in complex_type.get('elements', []):
                    child_name = child_element.get('name')
                    if child_name:
                        new_path = current_path + [child_name]
                        logger.debug(f"Checking child element '{child_name}' -> path: {new_path}")
                        found_element = self._find_target_element(target_path, target_attribute, new_path, child_element, complex_types, file_data)
                        if found_element:
                            return found_element
        
        return None
    
    def _path_matches_with_types(self, target_path: List[str], target_attribute: Optional[str], 
                                current_path: List[str], element_data: Dict[str, Any], 
                                complex_types: Dict[str, Any], file_data: Dict[str, Any]) -> bool:
        """Check if current path matches target path, resolving complex types."""
        logger.debug(f"Checking path: {current_path} vs target: {target_path}")
        
        # If we've matched the full path
        if len(current_path) == len(target_path):
            # Check if all path components match
            path_matches = all(current_path[i] == target_path[i] for i in range(len(target_path)))
            
            if path_matches:
                # If we need an attribute, check if element has attributes
                if target_attribute:
                    logger.debug(f"Looking for attribute '{target_attribute}' in element")
                    
                    # Check element's direct attributes
                    if 'attributes' in element_data:
                        for attr in element_data.get('attributes', []):
                            if attr.get('name') == target_attribute:
                                logger.debug(f"Found attribute '{target_attribute}' in element attributes")
                                return True
                    
                    # If element has a complex type, check its attributes
                    element_type = element_data.get('type', '')
                    if element_type.startswith('tns:'):
                        type_name = element_type[4:]  # Remove 'tns:' prefix
                        if type_name in complex_types:
                            complex_type = complex_types[type_name]
                            for attr in complex_type.get('attributes', []):
                                if attr.get('name') == target_attribute:
                                    logger.debug(f"Found attribute '{target_attribute}' in complex type '{type_name}'")
                                    return True
                    
                    logger.debug(f"Attribute '{target_attribute}' not found")
                    return False
                else:
                    # No attribute required, path match is sufficient
                    logger.debug(f"Path matches exactly: {current_path}")
                    return True
        
        # If current path is longer than target, no match
        if len(current_path) >= len(target_path):
            return False
        
        # Check if current path matches so far
        for i in range(len(current_path)):
            if i >= len(target_path) or current_path[i] != target_path[i]:
                return False
        
        # We need to continue searching deeper
        # Get the element type and resolve it
        element_type = element_data.get('type', '')
        logger.debug(f"Element '{element_data.get('name')}' has type '{element_type}'")
        
        # If this is a complex type, search its children
        if element_type.startswith('tns:'):
            type_name = element_type[4:]  # Remove 'tns:' prefix
            if type_name in complex_types:
                complex_type = complex_types[type_name]
                logger.debug(f"Searching in complex type '{type_name}' with {len(complex_type.get('elements', []))} elements")
                
                # Search through elements in this complex type
                for child_element in complex_type.get('elements', []):
                    child_name = child_element.get('name')
                    if child_name:
                        new_path = current_path + [child_name]
                        logger.debug(f"Checking child element '{child_name}' -> path: {new_path}")
                        if self._path_matches_with_types(target_path, target_attribute, new_path, child_element, complex_types, file_data):
                            return True
        
        return False
    
    def analyze_requirement(self, requirement: SchemaRequirement) -> AnalysisResult:
        """Analyze a single requirement against the loaded schemas."""
        result = AnalysisResult(requirement=requirement, status='missing')
        
        try:
            found, file_name, element_data = self.find_path_in_schema(requirement)
            
            if found and element_data is not None:
                result.status = 'found'
                result.found_in_file = file_name
                result.found_path = requirement.get_target_path()
                
                # Extract type information
                if requirement.is_attribute_target():
                    # Find the specific attribute
                    attributes = element_data.get('attributes', []) if element_data else []
                    for attr in attributes:
                        if attr.get('name') == requirement.attribute:
                            result.actual_type = attr.get('type', 'unknown')
                            result.actual_required = attr.get('use') == 'required'
                            break
                else:
                    # Element type
                    result.actual_type = element_data.get('type', 'unknown') if element_data else 'unknown'
                    result.actual_required = element_data.get('min_occurs', '1') != '0' if element_data else False
                
                # Check for type mismatches
                if requirement.expected_type and result.actual_type:
                    if requirement.expected_type.lower() != result.actual_type.lower():
                        result.status = 'mismatch'
                        result.issues.append(f"Type mismatch: expected {requirement.expected_type}, found {result.actual_type}")
                
                # Check for required mismatches
                if requirement.required != result.actual_required:
                    if result.status != 'mismatch':
                        result.status = 'mismatch'
                    required_str = "required" if requirement.required else "optional"
                    actual_str = "required" if result.actual_required else "optional"
                    result.issues.append(f"Required mismatch: expected {required_str}, found {actual_str}")
                
            else:
                result.status = 'missing'
                result.suggestions.append(f"Consider adding {requirement.get_target_path()} to one of the XSD files")
                
                # Suggest which file might be most appropriate
                if self.xsd_files:
                    result.suggestions.append(f"Suggested location: {self.xsd_files[0].name}")
                
        except Exception as e:
            result.status = 'error'
            result.issues.append(f"Analysis error: {str(e)}")
            logger.error(f"Error analyzing requirement {requirement.id}: {e}")
        
        return result
    
    def analyze_all_requirements(self) -> None:
        """Analyze all loaded requirements against the schemas."""
        console.print("[bold blue]Analyzing requirements against schemas...[/bold blue]")
        
        self.results = []
        
        for requirement in track(self.requirements, description="Analyzing requirements..."):
            result = self.analyze_requirement(requirement)
            self.results.append(result)
        
        console.print(f"[bold green]✓[/bold green] Analysis complete")
    
    def generate_console_report(self) -> None:
        """Generate a detailed console report of the analysis."""
        if not self.results:
            console.print("[yellow]No analysis results to display[/yellow]")
            return
        
        # Summary statistics
        status_counts = {}
        for result in self.results:
            status_counts[result.status] = status_counts.get(result.status, 0) + 1
        
        # Create summary panel
        summary_text = []
        total = len(self.results)
        for status, count in status_counts.items():
            percentage = (count / total) * 100
            summary_text.append(f"{status.upper()}: {count} ({percentage:.1f}%)")
        
        summary_panel = Panel(
            "\n".join(summary_text),
            title="[bold cyan]Analysis Summary[/bold cyan]",
            border_style="cyan"
        )
        console.print(summary_panel)
        
        # Detailed results by status
        for status in ['found', 'mismatch', 'missing', 'error']:
            status_results = [r for r in self.results if r.status == status]
            if not status_results:
                continue
            
            console.print(f"\n[bold {self._get_status_color(status)}]{status.upper()} REQUIREMENTS ({len(status_results)})[/bold {self._get_status_color(status)}]")
            
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("ID", style="dim", width=8)
            table.add_column("Path", style="cyan")
            table.add_column("Description", style="white")
            
            if status == 'found':
                table.add_column("Found In", style="green")
                table.add_column("Type", style="yellow")
            elif status == 'mismatch':
                table.add_column("Found In", style="green")
                table.add_column("Issues", style="red")
            elif status == 'missing':
                table.add_column("Suggestions", style="blue")
            elif status == 'error':
                table.add_column("Error", style="red")
            
            for result in status_results:
                req = result.requirement
                
                if status == 'found':
                    table.add_row(
                        req.id,
                        req.get_target_path(),
                        req.description[:50] + "..." if len(req.description) > 50 else req.description,
                        result.found_in_file or "Unknown",
                        result.actual_type or "Unknown"
                    )
                elif status == 'mismatch':
                    table.add_row(
                        req.id,
                        req.get_target_path(),
                        req.description[:50] + "..." if len(req.description) > 50 else req.description,
                        result.found_in_file or "Unknown",
                        "; ".join(result.issues)
                    )
                elif status == 'missing':
                    table.add_row(
                        req.id,
                        req.get_target_path(),
                        req.description[:50] + "..." if len(req.description) > 50 else req.description,
                        "; ".join(result.suggestions) if result.suggestions else "No suggestions"
                    )
                elif status == 'error':
                    table.add_row(
                        req.id,
                        req.get_target_path(),
                        req.description[:50] + "..." if len(req.description) > 50 else req.description,
                        "; ".join(result.issues)
                    )
            
            console.print(table)
    
    def _get_status_color(self, status: str) -> str:
        """Get console color for status."""
        colors = {
            'found': 'green',
            'mismatch': 'yellow',
            'missing': 'red',
            'error': 'magenta'
        }
        return colors.get(status, 'white')
    
    def generate_json_report(self, output_path: str) -> None:
        """Generate a JSON report of the analysis."""
        report_data = {
            'analysis_summary': {
                'total_requirements': len(self.requirements),
                'xsd_files': [str(f) for f in self.xsd_files],
                'csv_file': str(self.csv_file),
                'status_counts': {}
            },
            'requirements': [],
            'detailed_results': []
        }
        
        # Calculate status counts
        for result in self.results:
            status = result.status
            report_data['analysis_summary']['status_counts'][status] = \
                report_data['analysis_summary']['status_counts'].get(status, 0) + 1
        
        # Add requirement details
        for result in self.results:
            req = result.requirement
            
            req_data = {
                'id': req.id,
                'xpath': req.xpath,
                'description': req.description,
                'target_path': req.get_target_path(),
                'depth': req.get_depth(),
                'is_attribute': req.is_attribute_target(),
                'expected_type': req.expected_type,
                'required': req.required,
                'validation_rules': req.validation_rules,
                'business_purpose': req.business_purpose
            }
            report_data['requirements'].append(req_data)
            
            result_data = {
                'requirement_id': req.id,
                'status': result.status,
                'found_in_file': result.found_in_file,
                'found_path': result.found_path,
                'actual_type': result.actual_type,
                'actual_required': result.actual_required,
                'issues': result.issues,
                'suggestions': result.suggestions
            }
            report_data['detailed_results'].append(result_data)
        
        # Write JSON report
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        console.print(f"[bold green]✓[/bold green] JSON report saved: {output_path}")
    
    def generate_text_report(self, output_path: str) -> None:
        """Generate a text report of the analysis."""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("CSV Schema Analysis Report\n")
            f.write("=" * 50 + "\n\n")
            
            f.write(f"XSD Files Analyzed: {', '.join(str(f) for f in self.xsd_files)}\n")
            f.write(f"CSV Requirements File: {self.csv_file}\n")
            f.write(f"Total Requirements: {len(self.requirements)}\n\n")
            
            # Status summary
            status_counts = {}
            for result in self.results:
                status_counts[result.status] = status_counts.get(result.status, 0) + 1
            
            f.write("Status Summary:\n")
            f.write("-" * 20 + "\n")
            for status, count in status_counts.items():
                percentage = (count / len(self.results)) * 100
                f.write(f"{status.upper()}: {count} ({percentage:.1f}%)\n")
            f.write("\n")
            
            # Detailed results
            for status in ['found', 'mismatch', 'missing', 'error']:
                status_results = [r for r in self.results if r.status == status]
                if not status_results:
                    continue
                
                f.write(f"{status.upper()} REQUIREMENTS ({len(status_results)})\n")
                f.write("-" * 40 + "\n")
                
                for result in status_results:
                    req = result.requirement
                    f.write(f"ID: {req.id}\n")
                    f.write(f"Path: {req.get_target_path()}\n")
                    f.write(f"Description: {req.description}\n")
                    
                    if result.found_in_file:
                        f.write(f"Found in: {result.found_in_file}\n")
                    if result.actual_type:
                        f.write(f"Actual type: {result.actual_type}\n")
                    if result.issues:
                        f.write(f"Issues: {'; '.join(result.issues)}\n")
                    if result.suggestions:
                        f.write(f"Suggestions: {'; '.join(result.suggestions)}\n")
                    f.write("\n")
        
        console.print(f"[bold green]✓[/bold green] Text report saved: {output_path}")

def main():
    """Main entry point for the CSV schema analyzer."""
    parser = argparse.ArgumentParser(
        description="Analyze XSD files against CSV-defined schema requirements",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s requirements.csv schema.xsd
  %(prog)s requirements.csv schema1.xsd schema2.xsd schema3.xsd --output-dir ./reports
  %(prog)s requirements.csv *.xsd --formats json text --verbose

CSV Format (Dynamic Depth Structure):
  id,xpath,description,level1,level2,level3,level4,level5,level6,level7,level8,attribute,expected_type,required,validation_rules,business_purpose
  1,"levelA/levelB/@attr","Sample attribute",levelA,levelB,,,,,,,attr,string,true,"pattern: [A-Z]{3}","Customer ID"
  2,"book/author/name","Author name",book,author,name,,,,,,string,false,,"Author full name"
        """
    )
    
    parser.add_argument('csv_file', help='CSV file with schema requirements')
    parser.add_argument('xsd_files', nargs='+', help='XSD file(s) to analyze')
    parser.add_argument(
        '--output-dir', '-o',
        default='./output',
        help='Output directory for reports (default: ./output)'
    )
    parser.add_argument(
        '--formats', '-f',
        nargs='+',
        choices=['console', 'json', 'text'],
        default=['console'],
        help='Output formats (default: console)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
        logger.setLevel(logging.DEBUG)
    
    try:
        console.print("[bold blue]Starting CSV Schema Analyzer...[/bold blue]")
        
        # Create output directory
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize analyzer
        console.print("[dim]Initializing analyzer...[/dim]")
        analyzer = CSVSchemaAnalyzer(args.xsd_files, args.csv_file)
        
        # Load data
        console.print("[dim]Loading CSV requirements...[/dim]")
        analyzer.load_csv_requirements()
        
        console.print("[dim]Loading XSD schemas...[/dim]")
        analyzer.load_xsd_schemas()
        
        # Perform analysis
        console.print("[dim]Performing analysis...[/dim]")
        analyzer.analyze_all_requirements()
        
        # Generate reports
        if 'console' in args.formats:
            analyzer.generate_console_report()
        
        if 'json' in args.formats:
            json_path = output_dir / 'csv_schema_analysis.json'
            analyzer.generate_json_report(str(json_path))
        
        if 'text' in args.formats:
            text_path = output_dir / 'csv_schema_analysis.txt'
            analyzer.generate_text_report(str(text_path))
        
        console.print(f"\n[bold green]✓ Analysis complete![/bold green]")
        if args.formats != ['console']:
            console.print(f"Reports saved to: {output_dir}")
            
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
