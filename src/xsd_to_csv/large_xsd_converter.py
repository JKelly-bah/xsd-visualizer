"""
Large XSD to CSV Converter

Specialized converter for large XSD schemas with complex inheritance patterns,
multiple imports, and nested attribute structures.

Handles specific patterns like:
- Collection_ComplexType with restriction base types
- Large-scale attributes and attribute groups
- Cross-schema type references
- Complex documentation extraction
"""

import csv
import os
import sys
import logging
from typing import Dict, List, Any, Optional, Set, Tuple
from pathlib import Path
import xml.etree.ElementTree as ET

# Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from parsers.multi_file_xsd_parser import MultiFileXSDParser
from xsd_to_csv.xsd_csv_converter import XSDToCSVConverter


class LargeXSDToCSVConverter(XSDToCSVConverter):
    """
    Large-scale XSD to CSV converter that handles complex schema patterns
    commonly found in large environments.
    """
    
    def __init__(self, logger=None):
        """Initialize the large XSD to CSV converter."""
        super().__init__(logger)
        self.namespace_mappings = {}
        self.cross_schema_types = {}
        self.attribute_inheritance_chain = {}
        
    def convert_large_schema(self, main_xsd_file: str, output_file: str,
                                detailed_analysis: bool = True) -> Dict[str, Any]:
        """
        Convert large XSD schema with full analysis.
        
        Args:
            main_xsd_file: Main XSD file path
            output_file: Output CSV file path
            detailed_analysis: Include detailed inheritance and cross-reference analysis
            
        Returns:
            Dictionary with comprehensive conversion statistics
        """
        self.logger.info(f"Converting large schema: {main_xsd_file}")
        
        # Use multi-file parser for large schemas
        parser = MultiFileXSDParser(main_xsd_file)
        schema_data = parser.parse()
        
        # Build namespace and type registries
        self._build_type_registry(schema_data)
        
        # Extract comprehensive data
        csv_rows = []
        stats = {
            'total_rows': 0,
            'schema_files': 0,
            'root_elements': 0,
            'complex_types': 0,
            'simple_types': 0,
            'global_attributes': 0,
            'local_attributes': 0,
            'attribute_groups': 0,
            'inheritance_relationships': 0,
            'cross_schema_references': 0,
            'documented_items': 0
        }
        
        # Process schema metadata
        metadata_rows = self._extract_schema_metadata(schema_data)
        csv_rows.extend(metadata_rows)
        
        # Process root elements with full analysis
        root_element_rows = self._extract_root_elements_detailed(schema_data)
        csv_rows.extend(root_element_rows)
        stats['root_elements'] = len(root_element_rows)
        
        # Process complex types with inheritance analysis
        complex_type_rows = self._extract_complex_types_detailed(schema_data)
        csv_rows.extend(complex_type_rows)
        stats['complex_types'] = len(complex_type_rows)
        
        # Process simple types with restriction analysis
        simple_type_rows = self._extract_simple_types_detailed(schema_data)
        csv_rows.extend(simple_type_rows)
        stats['simple_types'] = len(simple_type_rows)
        
        # Process all attributes (global, local, inherited)
        attribute_rows = self._extract_all_attributes_detailed(schema_data)
        csv_rows.extend(attribute_rows)
        stats['global_attributes'] = len([r for r in attribute_rows if r.get('scope') == 'global'])
        stats['local_attributes'] = len([r for r in attribute_rows if r.get('scope') == 'local'])
        
        # Process attribute groups
        attr_group_rows = self._extract_attribute_groups_detailed(schema_data)
        csv_rows.extend(attr_group_rows)
        stats['attribute_groups'] = len(attr_group_rows)
        
        # Process inheritance and relationships
        if detailed_analysis:
            inheritance_rows = self._extract_inheritance_detailed(schema_data)
            csv_rows.extend(inheritance_rows)
            stats['inheritance_relationships'] = len(inheritance_rows)
            
            # Cross-schema reference analysis
            cross_ref_rows = self._extract_cross_schema_references(schema_data)
            csv_rows.extend(cross_ref_rows)
            stats['cross_schema_references'] = len(cross_ref_rows)
        
        # Count documented items
        stats['documented_items'] = len([r for r in csv_rows if r.get('description', '').strip()])
        
        # Write enhanced CSV
        self._write_large_csv(csv_rows, output_file)
        stats['total_rows'] = len(csv_rows)
        stats['schema_files'] = len(schema_data.get('multi_file_info', {}).get('processed_files', []))
        
        self.logger.info(f"Large CSV conversion complete. {stats['total_rows']} rows written")
        return stats
    
    def _build_type_registry(self, schema_data: Dict[str, Any]):
        """Build comprehensive type and namespace registries."""
        # Build namespace mappings
        for file_info in schema_data.get('multi_file_info', {}).get('processed_files', []):
            namespace = file_info.get('target_namespace', '')
            file_path = file_info.get('file_path', '')
            if namespace and file_path:
                self.namespace_mappings[namespace] = file_path
        
        # Build cross-schema type registry
        for type_name, type_info in schema_data.get('complex_types', {}).items():
            namespace = type_info.get('namespace', '')
            source_file = type_info.get('source_file', '')
            self.cross_schema_types[f"{namespace}:{type_name}"] = {
                'definition': type_info,
                'source_file': source_file
            }
    
    def _extract_schema_metadata(self, schema_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract schema-level metadata."""
        rows = []
        
        metadata = schema_data.get('metadata', {})
        target_namespace = metadata.get('target_namespace', '')
        version = metadata.get('version', '')
        
        # Main schema metadata
        row = {
            'category': 'schema_metadata',
            'name': 'Schema Information',
            'type': 'schema',
            'namespace': target_namespace,
            'version': version,
            'scope': 'schema',
            'description': f"Target namespace: {target_namespace}",
            'source_file': metadata.get('file_path', ''),
            'element_form_default': metadata.get('element_form_default', ''),
            'attribute_form_default': metadata.get('attribute_form_default', ''),
            'location': 'Schema Root',
            'documentation': self._extract_schema_documentation(schema_data)
        }
        rows.append(row)
        
        # Import/Include information
        multi_file_info = schema_data.get('multi_file_info', {})
        for file_info in multi_file_info.get('processed_files', []):
            if file_info.get('file_path') != metadata.get('file_path'):  # Skip main file
                row = {
                    'category': 'imported_schema',
                    'name': os.path.basename(file_info.get('file_path', '')),
                    'type': 'import/include',
                    'namespace': file_info.get('target_namespace', ''),
                    'version': file_info.get('version', ''),
                    'scope': 'import',
                    'description': f"Imported schema: {file_info.get('target_namespace', '')}",
                    'source_file': file_info.get('file_path', ''),
                    'location': 'Schema Import',
                    'import_type': file_info.get('import_type', 'import')
                }
                rows.append(row)
        
        return rows
    
    def _extract_root_elements_detailed(self, schema_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract root elements with detailed analysis."""
        rows = []
        
        for element_name, element_info in schema_data.get('elements', {}).items():
            element_type = element_info.get('type', '')
            
            # Resolve type information
            type_details = self._resolve_type_details(element_type, schema_data)
            
            row = {
                'category': 'root_element',
                'name': element_name,
                'type': element_type,
                'resolved_type': type_details.get('resolved_name', element_type),
                'namespace': self._extract_namespace_from_type(element_type),
                'type_namespace': type_details.get('namespace', ''),
                'scope': 'global',
                'use': 'root',
                'min_occurs': element_info.get('min_occurs', '1'),
                'max_occurs': element_info.get('max_occurs', '1'),
                'description': self._extract_documentation(element_info),
                'source_file': element_info.get('source_file', ''),
                'location': 'Root Element',
                'is_abstract': element_info.get('abstract', False),
                'substitution_group': element_info.get('substitution_group', ''),
                'type_category': type_details.get('category', ''),
                'has_children': type_details.get('has_children', False),
                'attribute_count': type_details.get('attribute_count', 0)
            }
            rows.append(row)
        
        return rows
    
    def _extract_simple_types_detailed(self, schema_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract simple types with detailed restriction analysis."""
        rows = []
        
        for type_name, type_info in schema_data.get('simple_types', {}).items():
            base_type = type_info.get('base_type', '')
            restriction_info = type_info.get('restrictions', {})
            
            row = {
                'category': 'simple_type',
                'name': type_name,
                'type': 'simpleType',
                'namespace': type_info.get('namespace', ''),
                'scope': 'global',
                'description': self._extract_documentation(type_info),
                'source_file': type_info.get('source_file', ''),
                'location': 'Type Definition',
                'base_type': base_type,
                'derivation_type': 'restriction' if restriction_info else 'direct',
                'restrictions': self._format_restrictions(type_info),
                'enumeration_values': ', '.join(restriction_info.get('enumeration', [])) if restriction_info.get('enumeration') else '',
                'pattern': restriction_info.get('pattern', ''),
                'min_length': restriction_info.get('minLength', ''),
                'max_length': restriction_info.get('maxLength', ''),
                'min_inclusive': restriction_info.get('minInclusive', ''),
                'max_inclusive': restriction_info.get('maxInclusive', ''),
                'min_exclusive': restriction_info.get('minExclusive', ''),
                'max_exclusive': restriction_info.get('maxExclusive', ''),
                'total_digits': restriction_info.get('totalDigits', ''),
                'fraction_digits': restriction_info.get('fractionDigits', ''),
                'white_space': restriction_info.get('whiteSpace', '')
            }
            rows.append(row)
        
        return rows
    
    def _extract_complex_types_detailed(self, schema_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract complex types with detailed inheritance and composition analysis."""
        rows = []
        
        for type_name, type_info in schema_data.get('complex_types', {}).items():
            base_type = type_info.get('base_type', '')
            derivation_type = type_info.get('derivation_type', '')
            
            # Analyze inheritance chain
            inheritance_chain = self._build_inheritance_chain(type_name, schema_data)
            
            # Count components
            elements = type_info.get('elements', [])
            attributes = type_info.get('attributes', [])
            
            row = {
                'category': 'complex_type',
                'name': type_name,
                'type': 'complexType',
                'namespace': type_info.get('namespace', ''),
                'scope': 'global',
                'description': self._extract_documentation(type_info),
                'source_file': type_info.get('source_file', ''),
                'location': 'Type Definition',
                'base_type': base_type,
                'derivation_type': derivation_type,
                'inheritance_depth': len(inheritance_chain),
                'inheritance_chain': ' -> '.join(inheritance_chain),
                'content_model': type_info.get('content_model', ''),
                'is_abstract': type_info.get('abstract', False),
                'is_mixed': type_info.get('mixed', False),
                'element_count': len(elements),
                'attribute_count': len(attributes),
                'has_restriction_attributes': self._has_restriction_attributes(type_info),
                'has_extension_attributes': self._has_extension_attributes(type_info),
                'complexity_score': self._calculate_complexity_score(type_info)
            }
            rows.append(row)
            
            # Add child elements as separate rows
            for element in elements:
                child_row = {
                    'category': 'child_element',
                    'name': element.get('name', ''),
                    'type': element.get('type', ''),
                    'namespace': self._extract_namespace_from_type(element.get('type', '')),
                    'scope': 'local',
                    'use': 'element',
                    'min_occurs': element.get('min_occurs', '1'),
                    'max_occurs': element.get('max_occurs', '1'),
                    'description': self._extract_documentation(element),
                    'source_file': type_info.get('source_file', ''),
                    'location': f"Complex Type: {type_name}",
                    'parent_type': type_name,
                    'is_reference': element.get('ref') is not None,
                    'reference_target': element.get('ref', ''),
                    'default_value': element.get('default', ''),
                    'fixed_value': element.get('fixed', '')
                }
                rows.append(child_row)
        
        return rows
    
    def _extract_all_attributes_detailed(self, schema_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract all attributes with inheritance tracking."""
        rows = []
        
        # Global attributes
        for attr_name, attr_info in schema_data.get('global_attributes', {}).items():
            row = {
                'category': 'global_attribute',
                'name': attr_name,
                'type': attr_info.get('type', ''),
                'namespace': self._extract_namespace_from_type(attr_info.get('type', '')),
                'scope': 'global',
                'use': attr_info.get('use', 'optional'),
                'description': self._extract_documentation(attr_info),
                'source_file': attr_info.get('source_file', ''),
                'location': 'Global Attribute',
                'default_value': attr_info.get('default', ''),
                'fixed_value': attr_info.get('fixed', ''),
                'restrictions': self._format_restrictions(attr_info),
                'is_qualified': attr_info.get('form', '') == 'qualified'
            }
            rows.append(row)
        
        # Local attributes from complex types (including inherited)
        for type_name, type_info in schema_data.get('complex_types', {}).items():
            attributes = type_info.get('attributes', [])
            
            for attribute in attributes:
                # Determine if attribute is inherited
                inherited_from = self._find_attribute_source(attribute, type_info, schema_data)
                
                row = {
                    'category': 'local_attribute',
                    'name': attribute.get('name', ''),
                    'type': attribute.get('type', ''),
                    'namespace': self._extract_namespace_from_type(attribute.get('type', '')),
                    'scope': 'local',
                    'use': attribute.get('use', 'optional'),
                    'description': self._extract_documentation(attribute),
                    'source_file': type_info.get('source_file', ''),
                    'location': f"Complex Type: {type_name}",
                    'parent_type': type_name,
                    'inherited_from': inherited_from,
                    'is_inherited': inherited_from != '',
                    'derivation_context': type_info.get('derivation_type', ''),
                    'default_value': attribute.get('default', ''),
                    'fixed_value': attribute.get('fixed', ''),
                    'restrictions': self._format_restrictions(attribute),
                    'attribute_source': self._determine_attribute_source(attribute, type_info)
                }
                rows.append(row)
        
        return rows
    
    def _extract_attribute_groups_detailed(self, schema_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract attribute groups with usage analysis."""
        rows = []
        
        for group_name, group_info in schema_data.get('attribute_groups', {}).items():
            attributes = group_info.get('attributes', [])
            
            # Group definition
            row = {
                'category': 'attribute_group',
                'name': group_name,
                'type': 'attributeGroup',
                'namespace': group_info.get('namespace', ''),
                'scope': 'global',
                'description': self._extract_documentation(group_info),
                'source_file': group_info.get('source_file', ''),
                'location': 'Attribute Group Definition',
                'attribute_count': len(attributes),
                'usage_count': self._count_attribute_group_usage(group_name, schema_data)
            }
            rows.append(row)
            
            # Individual attributes in group
            for attribute in attributes:
                attr_row = {
                    'category': 'attribute_group_member',
                    'name': attribute.get('name', ''),
                    'type': attribute.get('type', ''),
                    'namespace': self._extract_namespace_from_type(attribute.get('type', '')),
                    'scope': 'group_member',
                    'use': attribute.get('use', 'optional'),
                    'description': self._extract_documentation(attribute),
                    'source_file': group_info.get('source_file', ''),
                    'location': f"Attribute Group: {group_name}",
                    'parent_group': group_name,
                    'is_reference': attribute.get('ref') is not None,
                    'reference_target': attribute.get('ref', ''),
                    'default_value': attribute.get('default', ''),
                    'fixed_value': attribute.get('fixed', ''),
                    'restrictions': self._format_restrictions(attribute)
                }
                rows.append(attr_row)
        
        return rows
    
    def _extract_inheritance_detailed(self, schema_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract detailed inheritance relationships."""
        rows = []
        
        for type_name, type_info in schema_data.get('complex_types', {}).items():
            base_type = type_info.get('base_type')
            derivation_type = type_info.get('derivation_type')
            
            if base_type and derivation_type:
                # Resolve base type details
                base_type_info = self._resolve_type_details(base_type, schema_data)
                
                row = {
                    'category': 'inheritance_relationship',
                    'name': f"{type_name} {derivation_type} {base_type}",
                    'type': 'inheritance',
                    'derived_type': type_name,
                    'base_type': base_type,
                    'derivation_type': derivation_type,
                    'namespace': type_info.get('namespace', ''),
                    'base_namespace': base_type_info.get('namespace', ''),
                    'scope': 'relationship',
                    'description': f"{type_name} {derivation_type} from {base_type}",
                    'source_file': type_info.get('source_file', ''),
                    'location': 'Type Hierarchy',
                    'is_cross_schema': base_type_info.get('namespace', '') != type_info.get('namespace', ''),
                    'attribute_changes': self._analyze_attribute_changes(type_name, base_type, schema_data),
                    'element_changes': self._analyze_element_changes(type_name, base_type, schema_data)
                }
                rows.append(row)
        
        return rows
    
    def _extract_cross_schema_references(self, schema_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract cross-schema type references."""
        rows = []
        
        # Track all type references across schemas
        for type_name, type_info in schema_data.get('complex_types', {}).items():
            source_namespace = type_info.get('namespace', '')
            
            # Check base type references
            base_type = type_info.get('base_type', '')
            if base_type and ':' in base_type:
                target_namespace = base_type.split(':')[0]
                if target_namespace != source_namespace:
                    row = {
                        'category': 'cross_schema_reference',
                        'name': f"{type_name} -> {base_type}",
                        'type': 'base_type_reference',
                        'source_type': type_name,
                        'target_type': base_type,
                        'source_namespace': source_namespace,
                        'target_namespace': target_namespace,
                        'scope': 'cross_schema',
                        'description': f"Cross-schema base type reference",
                        'source_file': type_info.get('source_file', ''),
                        'reference_context': 'inheritance'
                    }
                    rows.append(row)
            
            # Check element type references
            for element in type_info.get('elements', []):
                element_type = element.get('type', '')
                if element_type and ':' in element_type:
                    target_namespace = element_type.split(':')[0]
                    if target_namespace != source_namespace:
                        row = {
                            'category': 'cross_schema_reference',
                            'name': f"{element.get('name', '')} : {element_type}",
                            'type': 'element_type_reference',
                            'source_type': type_name,
                            'target_type': element_type,
                            'source_namespace': source_namespace,
                            'target_namespace': target_namespace,
                            'scope': 'cross_schema',
                            'description': f"Cross-schema element type reference",
                            'source_file': type_info.get('source_file', ''),
                            'reference_context': f"element: {element.get('name', '')}"
                        }
                        rows.append(row)
        
        return rows
    
    def _extract_schema_documentation(self, schema_data: Dict[str, Any]) -> str:
        """Extract schema-level documentation."""
        metadata = schema_data.get('metadata', {})
        return metadata.get('documentation', '')
    
    def _resolve_type_details(self, type_ref: str, schema_data: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve detailed information about a type reference."""
        # Remove namespace prefix for lookup
        type_name = type_ref.split(':')[-1] if ':' in type_ref else type_ref
        namespace = type_ref.split(':')[0] if ':' in type_ref else ''
        
        # Look in complex types
        if type_name in schema_data.get('complex_types', {}):
            type_info = schema_data['complex_types'][type_name]
            return {
                'resolved_name': type_name,
                'namespace': namespace,
                'category': 'complex_type',
                'has_children': len(type_info.get('elements', [])) > 0,
                'attribute_count': len(type_info.get('attributes', []))
            }
        
        # Look in simple types
        if type_name in schema_data.get('simple_types', {}):
            return {
                'resolved_name': type_name,
                'namespace': namespace,
                'category': 'simple_type',
                'has_children': False,
                'attribute_count': 0
            }
        
        # Built-in type or unresolved
        return {
            'resolved_name': type_ref,
            'namespace': namespace,
            'category': 'builtin' if namespace == 'xsd' else 'unresolved',
            'has_children': False,
            'attribute_count': 0
        }
    
    def _extract_namespace_from_type(self, type_ref: str) -> str:
        """Extract namespace prefix from type reference."""
        return type_ref.split(':')[0] if ':' in type_ref else ''
    
    def _build_inheritance_chain(self, type_name: str, schema_data: Dict[str, Any]) -> List[str]:
        """Build complete inheritance chain for a type."""
        chain = [type_name]
        current_type = type_name
        
        while current_type in schema_data.get('complex_types', {}):
            type_info = schema_data['complex_types'][current_type]
            base_type = type_info.get('base_type', '')
            
            if not base_type:
                break
            
            # Remove namespace for lookup
            base_name = base_type.split(':')[-1] if ':' in base_type else base_type
            chain.append(base_type)
            current_type = base_name
            
            # Prevent infinite loops
            if len(chain) > 10:
                break
        
        return chain
    
    def _has_restriction_attributes(self, type_info: Dict[str, Any]) -> bool:
        """Check if type has attributes from restriction pattern."""
        return type_info.get('derivation_type') == 'restriction' and len(type_info.get('attributes', [])) > 0
    
    def _has_extension_attributes(self, type_info: Dict[str, Any]) -> bool:
        """Check if type has attributes from extension pattern."""
        return type_info.get('derivation_type') == 'extension' and len(type_info.get('attributes', [])) > 0
    
    def _calculate_complexity_score(self, type_info: Dict[str, Any]) -> int:
        """Calculate complexity score for a type."""
        score = 0
        score += len(type_info.get('elements', []))
        score += len(type_info.get('attributes', []))
        score += 2 if type_info.get('base_type') else 0
        score += 1 if type_info.get('mixed') else 0
        return score
    
    def _find_attribute_source(self, attribute: Dict[str, Any], type_info: Dict[str, Any], 
                             schema_data: Dict[str, Any]) -> str:
        """Find the source of an attribute (inheritance, attribute group, etc.)."""
        # Check if it's from base type
        base_type = type_info.get('base_type', '')
        if base_type:
            # This would require more complex analysis of base type attributes
            pass
        
        # Check if it's from attribute group reference
        if attribute.get('ref'):
            return f"Reference: {attribute['ref']}"
        
        return ''
    
    def _determine_attribute_source(self, attribute: Dict[str, Any], type_info: Dict[str, Any]) -> str:
        """Determine the source context of an attribute."""
        if type_info.get('derivation_type') == 'restriction':
            return 'restriction'
        elif type_info.get('derivation_type') == 'extension':
            return 'extension'
        elif attribute.get('ref'):
            return 'reference'
        else:
            return 'direct'
    
    def _count_attribute_group_usage(self, group_name: str, schema_data: Dict[str, Any]) -> int:
        """Count how many times an attribute group is used."""
        count = 0
        for type_info in schema_data.get('complex_types', {}).values():
            for attr in type_info.get('attributes', []):
                if attr.get('group_ref') == group_name:
                    count += 1
        return count
    
    def _analyze_attribute_changes(self, derived_type: str, base_type: str, 
                                 schema_data: Dict[str, Any]) -> str:
        """Analyze attribute changes in inheritance."""
        # This would require comparing attribute lists
        return "Analysis not implemented"
    
    def _analyze_element_changes(self, derived_type: str, base_type: str, 
                               schema_data: Dict[str, Any]) -> str:
        """Analyze element changes in inheritance."""
        # This would require comparing element lists
        return "Analysis not implemented"
    
    def _write_large_csv(self, rows: List[Dict[str, Any]], output_file: str):
        """Write large CSV with enhanced column ordering."""
        if not rows:
            self.logger.warning("No data to write to CSV")
            return
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Get all possible columns
        all_columns = set()
        for row in rows:
            all_columns.update(row.keys())
        
        # Define large-scale-specific column order
        large_order = [
            'category', 'name', 'type', 'namespace', 'scope', 'use',
            'description', 'source_file', 'location', 'parent_type',
            'base_type', 'derivation_type', 'inheritance_chain',
            'min_occurs', 'max_occurs', 'default_value', 'fixed_value',
            'restrictions', 'is_inherited', 'inherited_from', 'version',
            'complexity_score', 'attribute_count', 'element_count'
        ]
        
        # Order columns
        ordered_columns = []
        for col in large_order:
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
        
        self.logger.info(f"Large CSV file written: {output_file}")


def main():
    """Main function for large XSD to CSV conversion."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Convert large XSD schemas to CSV format')
    parser.add_argument('xsd_file', help='Main XSD file to convert')
    parser.add_argument('-o', '--output', required=True, help='Output CSV file path')
    parser.add_argument('--simple', action='store_true', help='Use simple analysis (faster)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Set up logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Create large converter and run conversion
    converter = LargeXSDToCSVConverter()
    stats = converter.convert_large_schema(
        main_xsd_file=args.xsd_file,
        output_file=args.output,
        detailed_analysis=not args.simple
    )
    
    print(f"Large XSD conversion complete!")
    print(f"Total rows: {stats['total_rows']}")
    print(f"Schema files processed: {stats['schema_files']}")
    print(f"Root elements: {stats['root_elements']}")
    print(f"Complex types: {stats['complex_types']}")
    print(f"Simple types: {stats['simple_types']}")
    print(f"Global attributes: {stats['global_attributes']}")
    print(f"Local attributes: {stats['local_attributes']}")
    print(f"Attribute groups: {stats['attribute_groups']}")
    print(f"Inheritance relationships: {stats['inheritance_relationships']}")
    print(f"Cross-schema references: {stats['cross_schema_references']}")
    print(f"Documented items: {stats['documented_items']}")


if __name__ == '__main__':
    main()
