#!/usr/bin/env python3
"""
Simple XSD to CSV Converter (No External Dependencies)

A simplified version that works with just the Python standard library.
Converts XSD schemas to CSV format without requiring lxml.
"""

import csv
import os
import sys
import logging
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Any, Optional


class SimpleXSDToCSVConverter:
    """
    Simple XSD to CSV converter using only standard library.
    Handles basic XSD parsing without external dependencies.
    """
    
    def __init__(self, logger=None):
        """Initialize the converter."""
        self.logger = logger or logging.getLogger(__name__)
        self.namespace_map = {}
        self.processed_files = set()
        
    def convert_xsd_to_csv(self, xsd_file: str, output_file: str) -> Dict[str, Any]:
        """
        Convert XSD file to CSV format.
        
        Args:
            xsd_file: Path to XSD file
            output_file: Path to output CSV file
            
        Returns:
            Dictionary with conversion statistics
        """
        self.logger.info(f"Converting XSD to CSV: {xsd_file}")
        
        # Parse the XSD file
        tree = ET.parse(xsd_file)
        root = tree.getroot()
        
        # Build namespace map
        self._build_namespace_map(root)
        
        # Extract all schema components
        csv_rows = []
        stats = {
            'total_rows': 0,
            'elements': 0,
            'attributes': 0,
            'complex_types': 0,
            'simple_types': 0,
            'documented_items': 0
        }
        
        # Extract schema metadata
        metadata_rows = self._extract_schema_metadata(root, xsd_file)
        csv_rows.extend(metadata_rows)
        
        # Extract elements
        element_rows = self._extract_elements(root, xsd_file)
        csv_rows.extend(element_rows)
        stats['elements'] = len(element_rows)
        
        # Extract complex types
        complex_type_rows = self._extract_complex_types(root, xsd_file)
        csv_rows.extend(complex_type_rows)
        stats['complex_types'] = len(complex_type_rows)
        
        # Extract simple types
        simple_type_rows = self._extract_simple_types(root, xsd_file)
        csv_rows.extend(simple_type_rows)
        stats['simple_types'] = len(simple_type_rows)
        
        # Extract global attributes
        attribute_rows = self._extract_global_attributes(root, xsd_file)
        csv_rows.extend(attribute_rows)
        stats['attributes'] = len(attribute_rows)
        
        # Count documented items
        stats['documented_items'] = len([r for r in csv_rows if r.get('description', '').strip()])
        
        # Write CSV
        self._write_csv(csv_rows, output_file)
        stats['total_rows'] = len(csv_rows)
        
        self.logger.info(f"CSV conversion complete. {stats['total_rows']} rows written")
        return stats
    
    def _build_namespace_map(self, root):
        """Build namespace prefix to URI mapping."""
        for prefix, uri in root.attrib.items():
            if prefix.startswith('xmlns'):
                if prefix == 'xmlns':
                    self.namespace_map[''] = uri  # Default namespace
                else:
                    self.namespace_map[prefix[6:]] = uri  # Remove 'xmlns:' prefix
    
    def _get_local_name(self, tag: str) -> str:
        """Get local name from namespaced tag."""
        if '}' in tag:
            return tag.split('}')[1]
        return tag
    
    def _extract_documentation(self, element) -> str:
        """Extract documentation from an element."""
        # Look for annotation/documentation
        for child in element:
            if self._get_local_name(child.tag) == 'annotation':
                for doc in child:
                    if self._get_local_name(doc.tag) == 'documentation':
                        return doc.text or ''
        return ''
    
    def _extract_schema_metadata(self, root, file_path: str) -> List[Dict[str, Any]]:
        """Extract schema-level metadata."""
        rows = []
        
        target_namespace = root.attrib.get('targetNamespace', '')
        version = root.attrib.get('version', '')
        element_form_default = root.attrib.get('elementFormDefault', 'unqualified')
        attribute_form_default = root.attrib.get('attributeFormDefault', 'unqualified')
        
        row = {
            'category': 'schema_metadata',
            'name': 'Schema Information',
            'type': 'schema',
            'namespace': target_namespace,
            'version': version,
            'scope': 'schema',
            'description': f"Target namespace: {target_namespace}",
            'source_file': file_path,
            'element_form_default': element_form_default,
            'attribute_form_default': attribute_form_default,
            'location': 'Schema Root',
            'documentation': self._extract_documentation(root)
        }
        rows.append(row)
        
        return rows
    
    def _extract_elements(self, root, file_path: str) -> List[Dict[str, Any]]:
        """Extract root-level elements."""
        rows = []
        
        for element in root:
            if self._get_local_name(element.tag) == 'element':
                name = element.attrib.get('name', '')
                element_type = element.attrib.get('type', '')
                min_occurs = element.attrib.get('minOccurs', '1')
                max_occurs = element.attrib.get('maxOccurs', '1')
                default = element.attrib.get('default', '')
                fixed = element.attrib.get('fixed', '')
                abstract = element.attrib.get('abstract', 'false') == 'true'
                
                row = {
                    'category': 'root_element',
                    'name': name,
                    'type': element_type,
                    'namespace': self._extract_namespace_from_type(element_type),
                    'scope': 'global',
                    'use': 'root',
                    'min_occurs': min_occurs,
                    'max_occurs': max_occurs,
                    'description': self._extract_documentation(element),
                    'source_file': file_path,
                    'location': 'Root Element',
                    'is_abstract': abstract,
                    'default_value': default,
                    'fixed_value': fixed
                }
                rows.append(row)
        
        return rows
    
    def _extract_complex_types(self, root, file_path: str) -> List[Dict[str, Any]]:
        """Extract complex types and their children."""
        rows = []
        
        for complex_type in root:
            if self._get_local_name(complex_type.tag) == 'complexType':
                type_name = complex_type.attrib.get('name', '')
                abstract = complex_type.attrib.get('abstract', 'false') == 'true'
                mixed = complex_type.attrib.get('mixed', 'false') == 'true'
                
                # Analyze inheritance
                base_type, derivation_type = self._analyze_inheritance(complex_type)
                
                # Count child elements and attributes
                child_elements = self._count_child_elements(complex_type)
                child_attributes = self._count_child_attributes(complex_type)
                
                row = {
                    'category': 'complex_type',
                    'name': type_name,
                    'type': 'complexType',
                    'namespace': '',
                    'scope': 'global',
                    'description': self._extract_documentation(complex_type),
                    'source_file': file_path,
                    'location': 'Type Definition',
                    'base_type': base_type,
                    'derivation_type': derivation_type,
                    'is_abstract': abstract,
                    'is_mixed': mixed,
                    'element_count': child_elements,
                    'attribute_count': child_attributes
                }
                rows.append(row)
                
                # Extract child elements
                child_rows = self._extract_child_elements(complex_type, type_name, file_path)
                rows.extend(child_rows)
                
                # Extract attributes
                attr_rows = self._extract_type_attributes(complex_type, type_name, file_path)
                rows.extend(attr_rows)
        
        return rows
    
    def _extract_simple_types(self, root, file_path: str) -> List[Dict[str, Any]]:
        """Extract simple types."""
        rows = []
        
        for simple_type in root:
            if self._get_local_name(simple_type.tag) == 'simpleType':
                type_name = simple_type.attrib.get('name', '')
                
                # Analyze restriction
                base_type, restrictions = self._analyze_simple_type_restriction(simple_type)
                
                row = {
                    'category': 'simple_type',
                    'name': type_name,
                    'type': 'simpleType',
                    'namespace': '',
                    'scope': 'global',
                    'description': self._extract_documentation(simple_type),
                    'source_file': file_path,
                    'location': 'Type Definition',
                    'base_type': base_type,
                    'derivation_type': 'restriction' if base_type else 'direct',
                    'restrictions': restrictions
                }
                rows.append(row)
        
        return rows
    
    def _extract_global_attributes(self, root, file_path: str) -> List[Dict[str, Any]]:
        """Extract global attributes."""
        rows = []
        
        for attribute in root:
            if self._get_local_name(attribute.tag) == 'attribute':
                name = attribute.attrib.get('name', '')
                attr_type = attribute.attrib.get('type', '')
                use = attribute.attrib.get('use', 'optional')
                default = attribute.attrib.get('default', '')
                fixed = attribute.attrib.get('fixed', '')
                
                row = {
                    'category': 'global_attribute',
                    'name': name,
                    'type': attr_type,
                    'namespace': self._extract_namespace_from_type(attr_type),
                    'scope': 'global',
                    'use': use,
                    'description': self._extract_documentation(attribute),
                    'source_file': file_path,
                    'location': 'Global Attribute',
                    'default_value': default,
                    'fixed_value': fixed
                }
                rows.append(row)
        
        return rows
    
    def _analyze_inheritance(self, complex_type) -> tuple:
        """Analyze inheritance pattern in complex type."""
        for child in complex_type:
            if self._get_local_name(child.tag) == 'complexContent':
                for grandchild in child:
                    if self._get_local_name(grandchild.tag) == 'restriction':
                        base = grandchild.attrib.get('base', '')
                        return base, 'restriction'
                    elif self._get_local_name(grandchild.tag) == 'extension':
                        base = grandchild.attrib.get('base', '')
                        return base, 'extension'
            elif self._get_local_name(child.tag) == 'simpleContent':
                for grandchild in child:
                    if self._get_local_name(grandchild.tag) == 'restriction':
                        base = grandchild.attrib.get('base', '')
                        return base, 'restriction'
                    elif self._get_local_name(grandchild.tag) == 'extension':
                        base = grandchild.attrib.get('base', '')
                        return base, 'extension'
        return '', ''
    
    def _analyze_simple_type_restriction(self, simple_type) -> tuple:
        """Analyze simple type restrictions."""
        for child in simple_type:
            if self._get_local_name(child.tag) == 'restriction':
                base = child.attrib.get('base', '')
                restrictions = []
                
                for restriction in child:
                    restriction_name = self._get_local_name(restriction.tag)
                    value = restriction.attrib.get('value', '')
                    if restriction_name and value:
                        restrictions.append(f"{restriction_name}: {value}")
                
                return base, '; '.join(restrictions)
        return '', ''
    
    def _count_child_elements(self, complex_type) -> int:
        """Count child elements in a complex type."""
        count = 0
        for elem in complex_type.iter():
            if self._get_local_name(elem.tag) == 'element':
                count += 1
        return count
    
    def _count_child_attributes(self, complex_type) -> int:
        """Count attributes in a complex type."""
        count = 0
        for elem in complex_type.iter():
            if self._get_local_name(elem.tag) == 'attribute':
                count += 1
        return count
    
    def _extract_child_elements(self, complex_type, parent_type: str, file_path: str) -> List[Dict[str, Any]]:
        """Extract child elements from complex type."""
        rows = []
        
        for elem in complex_type.iter():
            if self._get_local_name(elem.tag) == 'element':
                name = elem.attrib.get('name', '')
                ref = elem.attrib.get('ref', '')
                element_type = elem.attrib.get('type', '')
                min_occurs = elem.attrib.get('minOccurs', '1')
                max_occurs = elem.attrib.get('maxOccurs', '1')
                
                if name or ref:  # Skip empty elements
                    row = {
                        'category': 'child_element',
                        'name': name or ref,
                        'type': element_type,
                        'namespace': self._extract_namespace_from_type(element_type),
                        'scope': 'local',
                        'use': 'element',
                        'min_occurs': min_occurs,
                        'max_occurs': max_occurs,
                        'description': self._extract_documentation(elem),
                        'source_file': file_path,
                        'location': f"Complex Type: {parent_type}",
                        'parent_type': parent_type,
                        'is_reference': bool(ref),
                        'reference_target': ref
                    }
                    rows.append(row)
        
        return rows
    
    def _extract_type_attributes(self, complex_type, parent_type: str, file_path: str) -> List[Dict[str, Any]]:
        """Extract attributes from complex type."""
        rows = []
        
        for attr in complex_type.iter():
            if self._get_local_name(attr.tag) == 'attribute':
                name = attr.attrib.get('name', '')
                ref = attr.attrib.get('ref', '')
                attr_type = attr.attrib.get('type', '')
                use = attr.attrib.get('use', 'optional')
                default = attr.attrib.get('default', '')
                fixed = attr.attrib.get('fixed', '')
                
                if name or ref:  # Skip empty attributes
                    row = {
                        'category': 'local_attribute',
                        'name': name or ref,
                        'type': attr_type,
                        'namespace': self._extract_namespace_from_type(attr_type),
                        'scope': 'local',
                        'use': use,
                        'description': self._extract_documentation(attr),
                        'source_file': file_path,
                        'location': f"Complex Type: {parent_type}",
                        'parent_type': parent_type,
                        'is_reference': bool(ref),
                        'reference_target': ref,
                        'default_value': default,
                        'fixed_value': fixed
                    }
                    rows.append(row)
        
        return rows
    
    def _extract_namespace_from_type(self, type_ref: str) -> str:
        """Extract namespace prefix from type reference."""
        return type_ref.split(':')[0] if ':' in type_ref else ''
    
    def _write_csv(self, rows: List[Dict[str, Any]], output_file: str):
        """Write data to CSV file."""
        if not rows:
            self.logger.warning("No data to write to CSV")
            return
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Get all possible columns
        all_columns = set()
        for row in rows:
            all_columns.update(row.keys())
        
        # Define column order
        preferred_order = [
            'category', 'name', 'type', 'namespace', 'scope', 'use',
            'description', 'source_file', 'location', 'parent_type',
            'base_type', 'derivation_type', 'min_occurs', 'max_occurs',
            'default_value', 'fixed_value', 'restrictions', 'is_reference',
            'reference_target', 'is_abstract', 'is_mixed', 'element_count',
            'attribute_count', 'documentation'
        ]
        
        # Order columns
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
                complete_row = {col: row.get(col, '') for col in ordered_columns}
                writer.writerow(complete_row)
        
        self.logger.info(f"CSV file written: {output_file}")


def main():
    """Main function for simple XSD to CSV conversion."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Convert XSD schemas to CSV format (simple version)')
    parser.add_argument('xsd_file', help='XSD file to convert')
    parser.add_argument('-o', '--output', required=True, help='Output CSV file path')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Validate input file
    if not os.path.isfile(args.xsd_file):
        print(f"Error: XSD file not found: {args.xsd_file}", file=sys.stderr)
        sys.exit(1)
    
    # Set up logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Create output directory if needed
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        print(f"Created output directory: {output_dir}")
    
    try:
        print("Using Simple XSD to CSV Converter...")
        converter = SimpleXSDToCSVConverter()
        stats = converter.convert_xsd_to_csv(
            xsd_file=args.xsd_file,
            output_file=args.output
        )
        
        print(f"\n✅ CSV conversion complete!")
        print(f"📊 Conversion Statistics:")
        print(f"   • Total rows: {stats['total_rows']}")
        print(f"   • Elements: {stats['elements']}")
        print(f"   • Complex types: {stats['complex_types']}")
        print(f"   • Simple types: {stats['simple_types']}")
        print(f"   • Attributes: {stats['attributes']}")
        print(f"   • Documented items: {stats['documented_items']}")
        print(f"📁 Output file: {args.output}")
        
    except Exception as e:
        print(f"❌ Error converting XSD to CSV: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
