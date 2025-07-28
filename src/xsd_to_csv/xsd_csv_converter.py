"""
XSD to CSV Converter

This module provides comprehensive XSD schema analysis and CSV export functionality.
It handles complex multi-file schemas with imports, includes, and nested inheritance patterns.

Author: XSD Visualizer Project
Date: 2025
"""

import csv
import os
import sys
import logging
from typing import Dict, List, Any, Optional, Set
from pathlib import Path
import xml.etree.ElementTree as ET

# Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import our enhanced parsers
from parsers.multi_file_xsd_parser import MultiFileXSDParser
from parsers.xsd_parser import XSDParser


class XSDToCSVConverter:
    """
    Converts XSD schema files to comprehensive CSV reports.
    
    Handles:
    - Complex multi-file schemas with imports/includes
    - Nested restriction/extension patterns
    - Attribute groups and global attributes
    - Cross-schema type references
    - Documentation extraction
    - Inheritance hierarchies
    """
    
    def __init__(self, logger=None):
        """Initialize the XSD to CSV converter."""
        self.logger = logger or logging.getLogger(__name__)
        self.processed_files = set()
        self.type_registry = {}
        self.element_registry = {}
        self.attribute_registry = {}
        
    def convert_schema_to_csv(self, xsd_files: List[str], output_file: str, 
                             include_elements: bool = True,
                             include_attributes: bool = True,
                             include_types: bool = True,
                             include_inheritance: bool = True) -> Dict[str, Any]:
        """
        Convert XSD schema(s) to CSV format with comprehensive information.
        
        Args:
            xsd_files: List of XSD file paths
            output_file: Output CSV file path
            include_elements: Include element information
            include_attributes: Include attribute information  
            include_types: Include type definitions
            include_inheritance: Include inheritance relationships
            
        Returns:
            Dictionary with conversion statistics and metadata
        """
        self.logger.info(f"Converting {len(xsd_files)} XSD files to CSV: {output_file}")
        
        # Determine if we need multi-file parsing
        if len(xsd_files) > 1 or self._has_imports_or_includes(xsd_files[0]):
            parser = MultiFileXSDParser(xsd_files[0])
            schema_data = parser.parse()
            self.logger.info("Using multi-file parser for complex schema structure")
        else:
            parser = XSDParser(xsd_files[0])
            schema_data = parser.parse()
            self.logger.info("Using single-file parser")
        
        # Extract comprehensive schema information
        csv_rows = []
        stats = {
            'total_rows': 0,
            'elements': 0,
            'attributes': 0,
            'complex_types': 0,
            'simple_types': 0,
            'files_processed': len(xsd_files)
        }
        
        # Process elements
        if include_elements:
            element_rows = self._extract_elements(schema_data)
            csv_rows.extend(element_rows)
            stats['elements'] = len(element_rows)
            
        # Process attributes (both global and from complex types)
        if include_attributes:
            attribute_rows = self._extract_attributes(schema_data)
            csv_rows.extend(attribute_rows)
            stats['attributes'] = len(attribute_rows)
            
        # Process complex types
        if include_types:
            type_rows = self._extract_types(schema_data)
            csv_rows.extend(type_rows)
            stats['complex_types'] = len([r for r in type_rows if r.get('category') == 'complex_type'])
            stats['simple_types'] = len([r for r in type_rows if r.get('category') == 'simple_type'])
        
        # Process inheritance relationships
        if include_inheritance:
            inheritance_rows = self._extract_inheritance(schema_data)
            csv_rows.extend(inheritance_rows)
        
        # Write to CSV
        self._write_csv(csv_rows, output_file)
        stats['total_rows'] = len(csv_rows)
        
        self.logger.info(f"CSV conversion complete. {stats['total_rows']} rows written to {output_file}")
        return stats
    
    def _has_imports_or_includes(self, xsd_file: str) -> bool:
        """Check if XSD file has imports or includes."""
        try:
            tree = ET.parse(xsd_file)
            root = tree.getroot()
            ns = {'xsd': 'http://www.w3.org/2001/XMLSchema'}
            
            imports = root.findall('.//xsd:import', ns)
            includes = root.findall('.//xsd:include', ns)
            redefines = root.findall('.//xsd:redefine', ns)
            
            return len(imports) > 0 or len(includes) > 0 or len(redefines) > 0
        except Exception as e:
            self.logger.warning(f"Could not check imports/includes in {xsd_file}: {e}")
            return False
    
    def _extract_elements(self, schema_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract element information from schema data."""
        rows = []
        
        # Global elements
        for element_name, element_info in schema_data.get('elements', {}).items():
            row = {
                'category': 'element',
                'name': element_name,
                'type': element_info.get('type', ''),
                'namespace': self._extract_namespace(element_info.get('type', '')),
                'use': 'global',
                'min_occurs': element_info.get('min_occurs', '1'),
                'max_occurs': element_info.get('max_occurs', '1'),
                'description': self._extract_documentation(element_info),
                'source_file': element_info.get('source_file', ''),
                'location': element_info.get('location', ''),
                'base_type': '',
                'derivation_type': '',
                'restrictions': '',
                'default_value': element_info.get('default', ''),
                'fixed_value': element_info.get('fixed', '')
            }
            rows.append(row)
        
        # Elements from complex types
        for type_name, type_info in schema_data.get('complex_types', {}).items():
            elements = type_info.get('elements', [])
            for element in elements:
                row = {
                    'category': 'element',
                    'name': element.get('name', ''),
                    'type': element.get('type', ''),
                    'namespace': self._extract_namespace(element.get('type', '')),
                    'use': 'local',
                    'min_occurs': element.get('min_occurs', '1'),
                    'max_occurs': element.get('max_occurs', '1'),
                    'description': self._extract_documentation(element),
                    'source_file': type_info.get('source_file', ''),
                    'location': f"Complex Type: {type_name}",
                    'base_type': type_info.get('base_type', ''),
                    'derivation_type': type_info.get('derivation_type', ''),
                    'restrictions': self._format_restrictions(element),
                    'default_value': element.get('default', ''),
                    'fixed_value': element.get('fixed', '')
                }
                rows.append(row)
        
        return rows
    
    def _extract_attributes(self, schema_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract attribute information from schema data."""
        rows = []
        
        # Global attributes
        for attr_name, attr_info in schema_data.get('global_attributes', {}).items():
            row = {
                'category': 'attribute',
                'name': attr_name,
                'type': attr_info.get('type', ''),
                'namespace': self._extract_namespace(attr_info.get('type', '')),
                'use': attr_info.get('use', 'optional'),
                'min_occurs': '',
                'max_occurs': '',
                'description': self._extract_documentation(attr_info),
                'source_file': attr_info.get('source_file', ''),
                'location': 'Global Attribute',
                'base_type': '',
                'derivation_type': '',
                'restrictions': self._format_restrictions(attr_info),
                'default_value': attr_info.get('default', ''),
                'fixed_value': attr_info.get('fixed', '')
            }
            rows.append(row)
        
        # Attributes from complex types (including nested restriction/extension)
        for type_name, type_info in schema_data.get('complex_types', {}).items():
            attributes = type_info.get('attributes', [])
            for attribute in attributes:
                row = {
                    'category': 'attribute',
                    'name': attribute.get('name', ''),
                    'type': attribute.get('type', ''),
                    'namespace': self._extract_namespace(attribute.get('type', '')),
                    'use': attribute.get('use', 'optional'),
                    'min_occurs': '',
                    'max_occurs': '',
                    'description': self._extract_documentation(attribute),
                    'source_file': type_info.get('source_file', ''),
                    'location': f"Complex Type: {type_name}",
                    'base_type': type_info.get('base_type', ''),
                    'derivation_type': type_info.get('derivation_type', ''),
                    'restrictions': self._format_restrictions(attribute),
                    'default_value': attribute.get('default', ''),
                    'fixed_value': attribute.get('fixed', ''),
                    'inherited_from': attribute.get('inherited_from', '')
                }
                rows.append(row)
        
        # Attribute groups
        for group_name, group_info in schema_data.get('attribute_groups', {}).items():
            attributes = group_info.get('attributes', [])
            for attribute in attributes:
                row = {
                    'category': 'attribute_group_member',
                    'name': attribute.get('name', ''),
                    'type': attribute.get('type', ''),
                    'namespace': self._extract_namespace(attribute.get('type', '')),
                    'use': attribute.get('use', 'optional'),
                    'min_occurs': '',
                    'max_occurs': '',
                    'description': self._extract_documentation(attribute),
                    'source_file': group_info.get('source_file', ''),
                    'location': f"Attribute Group: {group_name}",
                    'base_type': '',
                    'derivation_type': '',
                    'restrictions': self._format_restrictions(attribute),
                    'default_value': attribute.get('default', ''),
                    'fixed_value': attribute.get('fixed', '')
                }
                rows.append(row)
        
        return rows
    
    def _extract_types(self, schema_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract type definitions from schema data."""
        rows = []
        
        # Complex types
        for type_name, type_info in schema_data.get('complex_types', {}).items():
            row = {
                'category': 'complex_type',
                'name': type_name,
                'type': 'complexType',
                'namespace': type_info.get('namespace', ''),
                'use': 'definition',
                'min_occurs': '',
                'max_occurs': '',
                'description': self._extract_documentation(type_info),
                'source_file': type_info.get('source_file', ''),
                'location': 'Type Definition',
                'base_type': type_info.get('base_type', ''),
                'derivation_type': type_info.get('derivation_type', ''),
                'restrictions': self._format_type_restrictions(type_info),
                'default_value': '',
                'fixed_value': '',
                'content_model': type_info.get('content_model', ''),
                'is_abstract': type_info.get('abstract', False),
                'element_count': len(type_info.get('elements', [])),
                'attribute_count': len(type_info.get('attributes', []))
            }
            rows.append(row)
        
        # Simple types
        for type_name, type_info in schema_data.get('simple_types', {}).items():
            row = {
                'category': 'simple_type',
                'name': type_name,
                'type': 'simpleType',
                'namespace': type_info.get('namespace', ''),
                'use': 'definition',
                'min_occurs': '',
                'max_occurs': '',
                'description': self._extract_documentation(type_info),
                'source_file': type_info.get('source_file', ''),
                'location': 'Type Definition',
                'base_type': type_info.get('base_type', ''),
                'derivation_type': type_info.get('restriction_type', 'restriction'),
                'restrictions': self._format_simple_type_restrictions(type_info),
                'default_value': '',
                'fixed_value': '',
                'enumeration_values': self._format_enumerations(type_info)
            }
            rows.append(row)
        
        return rows
    
    def _extract_inheritance(self, schema_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract inheritance relationships from schema data."""
        rows = []
        
        for type_name, type_info in schema_data.get('complex_types', {}).items():
            base_type = type_info.get('base_type')
            derivation_type = type_info.get('derivation_type')
            
            if base_type and derivation_type:
                row = {
                    'category': 'inheritance',
                    'name': f"{type_name} -> {base_type}",
                    'type': 'inheritance_relationship',
                    'namespace': type_info.get('namespace', ''),
                    'use': derivation_type,
                    'min_occurs': '',
                    'max_occurs': '',
                    'description': f"{type_name} {derivation_type} {base_type}",
                    'source_file': type_info.get('source_file', ''),
                    'location': 'Type Hierarchy',
                    'base_type': base_type,
                    'derivation_type': derivation_type,
                    'derived_type': type_name,
                    'restrictions': '',
                    'default_value': '',
                    'fixed_value': ''
                }
                rows.append(row)
        
        return rows
    
    def _extract_namespace(self, type_ref: str) -> str:
        """Extract namespace from type reference."""
        if ':' in type_ref:
            return type_ref.split(':')[0]
        return ''
    
    def _extract_documentation(self, item_info: Dict[str, Any]) -> str:
        """Extract documentation/annotation from item info."""
        doc = item_info.get('documentation', '')
        if isinstance(doc, list):
            return ' | '.join(doc)
        return str(doc).strip() if doc else ''
    
    def _format_restrictions(self, item_info: Dict[str, Any]) -> str:
        """Format restrictions for an item."""
        restrictions = []
        
        if 'min_length' in item_info:
            restrictions.append(f"minLength={item_info['min_length']}")
        if 'max_length' in item_info:
            restrictions.append(f"maxLength={item_info['max_length']}")
        if 'pattern' in item_info:
            restrictions.append(f"pattern={item_info['pattern']}")
        if 'min_inclusive' in item_info:
            restrictions.append(f"minInclusive={item_info['min_inclusive']}")
        if 'max_inclusive' in item_info:
            restrictions.append(f"maxInclusive={item_info['max_inclusive']}")
        if 'enumeration' in item_info:
            enums = item_info['enumeration']
            if isinstance(enums, list):
                restrictions.append(f"enumeration=[{','.join(enums)}]")
        
        return ' | '.join(restrictions)
    
    def _format_type_restrictions(self, type_info: Dict[str, Any]) -> str:
        """Format restrictions for complex types."""
        restrictions = []
        
        if type_info.get('mixed'):
            restrictions.append("mixed=true")
        if type_info.get('abstract'):
            restrictions.append("abstract=true")
        if type_info.get('final'):
            restrictions.append(f"final={type_info['final']}")
        if type_info.get('block'):
            restrictions.append(f"block={type_info['block']}")
            
        return ' | '.join(restrictions)
    
    def _format_simple_type_restrictions(self, type_info: Dict[str, Any]) -> str:
        """Format restrictions for simple types."""
        restrictions = []
        
        facets = type_info.get('facets', {})
        for facet_name, facet_value in facets.items():
            restrictions.append(f"{facet_name}={facet_value}")
        
        return ' | '.join(restrictions)
    
    def _format_enumerations(self, type_info: Dict[str, Any]) -> str:
        """Format enumeration values for simple types."""
        enums = type_info.get('enumeration', [])
        if isinstance(enums, list):
            return ','.join(enums)
        return str(enums) if enums else ''
    
    def _write_csv(self, rows: List[Dict[str, Any]], output_file: str):
        """Write rows to CSV file."""
        if not rows:
            self.logger.warning("No data to write to CSV")
            return
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Get all possible columns from all rows
        all_columns = set()
        for row in rows:
            all_columns.update(row.keys())
        
        # Define preferred column order
        preferred_order = [
            'category', 'name', 'type', 'namespace', 'use', 
            'min_occurs', 'max_occurs', 'description', 'source_file', 
            'location', 'base_type', 'derivation_type', 'restrictions',
            'default_value', 'fixed_value'
        ]
        
        # Order columns with preferred first, then remaining
        ordered_columns = []
        for col in preferred_order:
            if col in all_columns:
                ordered_columns.append(col)
                all_columns.remove(col)
        ordered_columns.extend(sorted(all_columns))
        
        # Write CSV
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=ordered_columns)
            writer.writeheader()
            
            for row in rows:
                # Ensure all columns exist in row (fill missing with empty string)
                complete_row = {col: row.get(col, '') for col in ordered_columns}
                writer.writerow(complete_row)
        
        self.logger.info(f"CSV file written successfully: {output_file}")


def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Convert XSD schemas to CSV format')
    parser.add_argument('xsd_files', nargs='+', help='XSD file(s) to convert')
    parser.add_argument('-o', '--output', required=True, help='Output CSV file path')
    parser.add_argument('--no-elements', action='store_true', help='Exclude elements')
    parser.add_argument('--no-attributes', action='store_true', help='Exclude attributes')
    parser.add_argument('--no-types', action='store_true', help='Exclude type definitions')
    parser.add_argument('--no-inheritance', action='store_true', help='Exclude inheritance relationships')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Set up logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Create converter and run conversion
    converter = XSDToCSVConverter()
    stats = converter.convert_schema_to_csv(
        xsd_files=args.xsd_files,
        output_file=args.output,
        include_elements=not args.no_elements,
        include_attributes=not args.no_attributes,
        include_types=not args.no_types,
        include_inheritance=not args.no_inheritance
    )
    
    print(f"Conversion complete!")
    print(f"Total rows: {stats['total_rows']}")
    print(f"Elements: {stats['elements']}")
    print(f"Attributes: {stats['attributes']}")
    print(f"Complex types: {stats['complex_types']}")
    print(f"Simple types: {stats['simple_types']}")
    print(f"Files processed: {stats['files_processed']}")


if __name__ == '__main__':
    main()
