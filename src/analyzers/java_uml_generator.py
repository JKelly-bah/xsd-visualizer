#!/usr/bin/env python3
"""
XSD to Java UML Generator

This tool analyzes XSD files and generates Java UML class diagrams, showing:
- Classes derived from XSD complex types
- Relationships between classes (composition, inheritance)
- Attributes from XSD elements and attributes
- Package structure based on namespaces
- PlantUML and Mermaid diagram formats
"""

import argparse
import sys
import os
import json
from pathlib import Path
from typing import Dict, List, Set, Any, Optional, Tuple
import logging
from dataclasses import dataclass, field

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.parsers.multi_file_xsd_parser import MultiFileXSDParser
from src.parsers.xsd_parser import XSDParser
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import track
from rich import print as rprint

@dataclass
class JavaClass:
    """Represents a Java class derived from XSD complex type"""
    name: str
    package: str
    namespace: str
    attributes: List[Dict[str, Any]] = field(default_factory=list)
    methods: List[str] = field(default_factory=list)
    extends: Optional[str] = None
    implements: List[str] = field(default_factory=list)
    is_abstract: bool = False
    documentation: str = ""
    xsd_type: str = "complex"  # complex, simple, element

@dataclass
class Relationship:
    """Represents relationships between Java classes"""
    from_class: str
    to_class: str
    relationship_type: str  # composition, aggregation, inheritance, association
    multiplicity: str = "1"
    label: str = ""

class JavaUMLGenerator:
    """Generates Java UML diagrams from XSD schemas"""
    
    def __init__(self, output_dir: str = "./output", custom_package: Optional[str] = None):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.console = Console()
        self.custom_package = custom_package
        
        # Java UML model
        self.classes: Dict[str, JavaClass] = {}
        self.relationships: List[Relationship] = []
        self.packages: Set[str] = set()
        
        # Type mappings - support both xs: and xsd: prefixes
        base_types = {
            'string': 'String',
            'int': 'int',
            'integer': 'Integer',
            'long': 'long',
            'double': 'double',
            'float': 'float',
            'boolean': 'boolean',
            'date': 'LocalDate',
            'dateTime': 'LocalDateTime',
            'time': 'LocalTime',
            'decimal': 'BigDecimal',
            'byte': 'byte',
            'short': 'short',
            'anyURI': 'URI',
            'base64Binary': 'byte[]',
            'hexBinary': 'byte[]',
        }
        
        # Create mappings for both xs: and xsd: prefixes
        self.xsd_to_java_types = {}
        for type_name, java_type in base_types.items():
            self.xsd_to_java_types[f'xs:{type_name}'] = java_type
            self.xsd_to_java_types[f'xsd:{type_name}'] = java_type
        
    def analyze_xsd_files(self, xsd_files: List[str]) -> Dict[str, Any]:
        """Analyze XSD files and build Java UML model"""
        
        self.console.print(f"\n🏗️ Generating Java UML from {len(xsd_files)} XSD files...")
        
        # Parse all XSD files
        structures = {}
        for xsd_file in xsd_files:
            try:
                parser = XSDParser(str(xsd_file))
                structure = parser.parse()
                structures[str(xsd_file)] = structure
            except Exception as e:
                self.console.print(f"⚠️ Warning: Could not parse {xsd_file}: {e}")
                continue
            
        # Extract Java classes from XSD structure
        for xsd_file, structure in structures.items():
            self._extract_classes_from_structure(structure, xsd_file)
            
        # Build relationships
        for xsd_file, structure in structures.items():
            self._extract_relationships_from_structure(structure, xsd_file)
            
        return self._build_summary()
        
    def _extract_classes_from_structure(self, structure: Dict[str, Any], xsd_file: str):
        """Extract Java classes from XSD structure"""
        
        target_namespace = structure.get('target_namespace', '')
        package_name = self._namespace_to_package(target_namespace)
        self.packages.add(package_name)
        
        # Process complex types
        for type_name, type_info in structure.get('complex_types', {}).items():
            java_class = JavaClass(
                name=self._to_java_class_name(type_name),
                package=package_name,
                namespace=target_namespace,
                documentation=self._extract_documentation(type_info),
                xsd_type='complex'
            )
            
            # Extract attributes from complex type
            self._extract_attributes_from_type(java_class, type_info)
            
            # Check for inheritance (extension)
            if 'base_type' in type_info and type_info['base_type']:
                java_class.extends = self._to_java_class_name(type_info['base_type'])
                
            self.classes[java_class.name] = java_class
            
        # Process global elements that could become classes
        elements = structure.get('elements', [])
        if isinstance(elements, list):
            for element_info in elements:
                element_name = element_info.get('name', '')
                element_type = element_info.get('type') or ''
                has_attributes = len(element_info.get('attributes', [])) > 0
                
                # Create class for elements that:
                # 1. Have a type ending in 'Type', OR
                # 2. Have a complex_type, OR  
                # 3. Have attributes directly (inline complex types)
                if (element_type.endswith('Type') or 
                    element_info.get('complex_type') or 
                    has_attributes):
                    
                    java_class = JavaClass(
                        name=self._to_java_class_name(element_name),
                        package=package_name,
                        namespace=target_namespace,
                        documentation=self._extract_documentation(element_info),
                        xsd_type='element'
                    )
                    
                    # Extract attributes from element
                    if 'complex_type' in element_info:
                        self._extract_attributes_from_type(java_class, element_info['complex_type'])
                    
                    # Also extract direct attributes from the element itself
                    if 'attributes' in element_info:
                        for attr_info in element_info['attributes']:
                            # Skip attributes without names (unresolved references)
                            if not attr_info.get('name'):
                                continue
                                
                            # Convert to the format expected by the Java generator
                            java_type = self._xsd_type_to_java(attr_info.get('type', 'String'))
                            
                            # Check for duplicates by name to avoid processing the same attribute twice
                            attr_name = self._to_java_field_name(attr_info.get('name', ''))
                            if not any(existing_attr['name'] == attr_name for existing_attr in java_class.attributes):
                                java_class.attributes.append({
                                    'name': attr_name,
                                    'type': java_type,
                                    'visibility': 'private',
                                    'documentation': attr_info.get('documentation', ''),
                                    'is_attribute': True,
                                    'required': attr_info.get('use') == 'required'
                                })
                    
                    # Always add the class now (we know it has content if we reached here)
                    self.classes[java_class.name] = java_class
        else:
            # Handle case where elements is a dict (older format)
            for element_name, element_info in elements.items():
                element_type = element_info.get('type') or ''
                has_attributes = len(element_info.get('attributes', [])) > 0
                
                # Create class for elements that have type ending in 'Type', complex_type, or direct attributes
                if (element_type.endswith('Type') or 
                    element_info.get('complex_type') or 
                    has_attributes):
                    
                    java_class = JavaClass(
                        name=self._to_java_class_name(element_name),
                        package=package_name,
                        namespace=target_namespace,
                        documentation=self._extract_documentation(element_info),
                        xsd_type='element'
                    )
                    
                    # Extract attributes from element
                    if 'complex_type' in element_info:
                        self._extract_attributes_from_type(java_class, element_info['complex_type'])
                    
                    # Also extract direct attributes from the element itself
                    if 'attributes' in element_info:
                        for attr_info in element_info['attributes']:
                            # Skip attributes without names (unresolved references)
                            if not attr_info.get('name'):
                                continue
                                
                            # Convert to the format expected by the Java generator
                            java_type = self._xsd_type_to_java(attr_info.get('type', 'String'))
                            
                            # Check for duplicates by name to avoid processing the same attribute twice
                            attr_name = self._to_java_field_name(attr_info.get('name', ''))
                            if not any(existing_attr['name'] == attr_name for existing_attr in java_class.attributes):
                                java_class.attributes.append({
                                    'name': attr_name,
                                    'type': java_type,
                                    'visibility': 'private',
                                    'documentation': attr_info.get('documentation', ''),
                                    'is_attribute': True,
                                    'required': attr_info.get('use') == 'required'
                                })
                    
                    # Always add the class now (we know it has content if we reached here)
                    self.classes[java_class.name] = java_class
                
        # Process simple types as enums or constants
        for type_name, type_info in structure.get('simple_types', {}).items():
            # Handle direct enumeration
            if 'enumeration' in type_info:
                java_class = JavaClass(
                    name=self._to_java_class_name(type_name),
                    package=package_name,
                    namespace=target_namespace,
                    documentation=self._extract_documentation(type_info),
                    xsd_type='enum'
                )
                
                # Add enum values as constants
                for enum_value in type_info.get('enumeration', []):
                    java_class.attributes.append({
                        'name': enum_value.upper().replace('-', '_'),
                        'type': java_class.name,
                        'visibility': 'public',
                        'is_static': True,
                        'is_final': True
                    })
                    
                self.classes[java_class.name] = java_class
                
            # Handle xsd:restriction with xsd:enumeration
            elif 'restriction' in type_info or 'xsd:restriction' in type_info:
                restriction_info = type_info.get('restriction') or type_info.get('xsd:restriction', {})
                
                # Look for enumeration values in the restriction
                enum_values = []
                
                # Check various possible structures for enumerations
                if 'enumeration' in restriction_info:
                    enum_values = restriction_info['enumeration']
                elif 'xsd:enumeration' in restriction_info:
                    enum_values = restriction_info['xsd:enumeration']
                elif isinstance(restriction_info, list):
                    # Sometimes restrictions are stored as lists of constraint objects
                    for constraint in restriction_info:
                        if isinstance(constraint, dict):
                            if 'enumeration' in constraint:
                                if isinstance(constraint['enumeration'], list):
                                    enum_values.extend(constraint['enumeration'])
                                else:
                                    enum_values.append(constraint['enumeration'])
                            elif 'xsd:enumeration' in constraint:
                                if isinstance(constraint['xsd:enumeration'], list):
                                    enum_values.extend(constraint['xsd:enumeration'])
                                else:
                                    enum_values.append(constraint['xsd:enumeration'])
                
                # Create enum class if we found enumeration values
                if enum_values:
                    java_class = JavaClass(
                        name=self._to_java_class_name(type_name),
                        package=package_name,
                        namespace=target_namespace,
                        documentation=self._extract_documentation(type_info),
                        xsd_type='enum'
                    )
                    
                    # Add enum values as constants
                    for enum_value in enum_values:
                        # Handle different formats of enum values
                        if isinstance(enum_value, dict) and 'value' in enum_value:
                            value = enum_value['value']
                        elif isinstance(enum_value, str):
                            value = enum_value
                        else:
                            value = str(enum_value)
                            
                        java_class.attributes.append({
                            'name': value.upper().replace('-', '_').replace(' ', '_'),
                            'type': java_class.name,
                            'visibility': 'public',
                            'is_static': True,
                            'is_final': True
                        })
                        
                    self.classes[java_class.name] = java_class
                
    def _extract_attributes_from_type(self, java_class: JavaClass, type_info: Dict[str, Any]):
        """Extract attributes from XSD type information"""
        
        # Process elements within the type
        elements = type_info.get('elements', [])
        if isinstance(elements, list):
            for element_info in elements:
                element_name = element_info.get('name', '')
                
                # Check if element has restriction/enumeration
                if ('restriction' in element_info or 'xsd:restriction' in element_info or 
                    'simpleType' in element_info):
                    java_type = self._handle_restriction_type(element_info)
                else:
                    java_type = self._xsd_type_to_java(element_info.get('type', 'String'))
                
                # Handle multiplicity
                max_occurs = element_info.get('max_occurs', '1')
                if max_occurs == 'unbounded' or (max_occurs.isdigit() and int(max_occurs) > 1):
                    java_type = f"List<{java_type}>"
                    
                java_class.attributes.append({
                    'name': self._to_java_field_name(element_name),
                    'type': java_type,
                    'visibility': 'private',
                'documentation': element_info.get('documentation', ''),
                'min_occurs': element_info.get('min_occurs', '1'),
                'max_occurs': max_occurs
            })
            
        # Process XSD attributes
        attributes = type_info.get('attributes', [])
        if isinstance(attributes, list):
            for attr_info in attributes:
                attr_name = attr_info.get('name', '')
                
                # Check if attribute has restriction/enumeration
                if ('restriction' in attr_info or 'xsd:restriction' in attr_info or 
                    'simpleType' in attr_info):
                    java_type = self._handle_restriction_type(attr_info)
                else:
                    java_type = self._xsd_type_to_java(attr_info.get('type', 'String'))
                
                java_class.attributes.append({
                    'name': self._to_java_field_name(attr_name),
                    'type': java_type,
                    'visibility': 'private',
                    'documentation': attr_info.get('documentation', ''),
                    'is_attribute': True,
                    'required': attr_info.get('use') == 'required'
                })
        else:
            # Handle dict format for backwards compatibility
            for attr_name, attr_info in attributes.items():
                # Check if attribute has restriction/enumeration
                if ('restriction' in attr_info or 'xsd:restriction' in attr_info or 
                    'simpleType' in attr_info):
                    java_type = self._handle_restriction_type(attr_info)
                else:
                    java_type = self._xsd_type_to_java(attr_info.get('type', 'String'))
                
                java_class.attributes.append({
                    'name': self._to_java_field_name(attr_name),
                    'type': java_type,
                    'visibility': 'private',
                    'documentation': attr_info.get('documentation', ''),
                    'is_attribute': True,
                    'required': attr_info.get('use') == 'required'
                })
            
    def _extract_relationships_from_structure(self, structure: Dict[str, Any], xsd_file: str):
        """Extract relationships between classes from XSD structure"""
        
        for type_name, type_info in structure.get('complex_types', {}).items():
            from_class = self._to_java_class_name(type_name)
            
            # Inheritance relationships
            if 'base_type' in type_info and type_info['base_type']:
                to_class = self._to_java_class_name(type_info['base_type'])
                if to_class and to_class in self.classes:  # Only add if target class exists
                    self.relationships.append(Relationship(
                        from_class=from_class,
                        to_class=to_class,
                        relationship_type='inheritance',
                        label='extends'
                    ))
                
            # Composition/Association relationships
            elements = type_info.get('elements', [])
            if isinstance(elements, list):
                for element_info in elements:
                    element_name = element_info.get('name', '')
                    element_type = element_info.get('type', '')
                    if element_type and element_type.endswith('Type'):
                        to_class = self._to_java_class_name(element_type)
                        if to_class in self.classes:
                            max_occurs = element_info.get('max_occurs', '1')
                            relationship_type = 'composition' if element_info.get('min_occurs', '1') != '0' else 'association'
                            multiplicity = '1' if max_occurs == '1' else f"1..*" if max_occurs == 'unbounded' else f"1..{max_occurs}"
                            
                            self.relationships.append(Relationship(
                                from_class=from_class,
                                to_class=to_class,
                                relationship_type=relationship_type,
                                multiplicity=multiplicity,
                                label=element_name
                            ))
            else:
                # Handle dict format for backwards compatibility
                for element_name, element_info in elements.items():
                    element_type = element_info.get('type', '')
                    if element_type and element_type.endswith('Type'):
                        to_class = self._to_java_class_name(element_type)
                        if to_class in self.classes:
                            max_occurs = element_info.get('max_occurs', '1')
                            relationship_type = 'composition' if element_info.get('min_occurs', '1') != '0' else 'association'
                            multiplicity = '1' if max_occurs == '1' else f"1..*" if max_occurs == 'unbounded' else f"1..{max_occurs}"
                            
                            self.relationships.append(Relationship(
                                from_class=from_class,
                                to_class=to_class,
                                relationship_type=relationship_type,
                                multiplicity=multiplicity,
                                label=element_name
                            ))
                        
    def _namespace_to_package(self, namespace: str) -> str:
        """Convert XSD namespace to Java package name"""
        # Use custom package if provided
        if self.custom_package:
            return self.custom_package
            
        if not namespace:
            return 'com.example.schema'
            
        # Extract domain from namespace
        if '://' in namespace:
            namespace = namespace.split('://', 1)[1]
            
        # Convert to package format
        parts = namespace.replace('/', '.').split('.')
        # Reverse domain parts
        if len(parts) > 1:
            parts = list(reversed(parts[:2])) + parts[2:]
            
        return '.'.join(part.lower().replace('-', '') for part in parts if part)
        
    def _extract_documentation(self, element_info: Dict[str, Any]) -> str:
        """Extract documentation from XSD element info, handling various formats"""
        doc_sources = [
            'documentation',  # Standard field
            'doc',           # Alternative field name
            'description',   # Another alternative
        ]
        
        # Try standard documentation fields first
        for field in doc_sources:
            if field in element_info and element_info[field]:
                return str(element_info[field]).strip()
                
        # Look for annotation/documentation structure
        if 'annotation' in element_info:
            annotation = element_info['annotation']
            if isinstance(annotation, dict):
                if 'documentation' in annotation:
                    return str(annotation['documentation']).strip()
                if 'doc' in annotation:
                    return str(annotation['doc']).strip()
                    
        # Look for nested structures that might contain documentation
        if 'xsd:annotation' in element_info:
            return self._extract_documentation({'annotation': element_info['xsd:annotation']})
            
        # Look in restriction for documentation
        if 'restriction' in element_info:
            restriction_doc = self._extract_documentation(element_info['restriction'])
            if restriction_doc:
                return restriction_doc
                
        if 'xsd:restriction' in element_info:
            restriction_doc = self._extract_documentation(element_info['xsd:restriction'])
            if restriction_doc:
                return restriction_doc
            
        return ""
        
    def _to_java_class_name(self, xsd_name: str) -> str:
        """Convert XSD type name to Java class name"""
        if not xsd_name or xsd_name.strip() == "":
            return f"UnnamedType{len(self.classes) + 1}"
            
        # Remove namespace prefix
        if ':' in xsd_name:
            xsd_name = xsd_name.split(':', 1)[1]
            
        # Handle empty name after prefix removal
        if not xsd_name or xsd_name.strip() == "":
            return f"UnnamedType{len(self.classes) + 1}"
            
        # Convert to PascalCase
        parts = xsd_name.replace('-', '_').split('_')
        result = ''.join(part.capitalize() for part in parts if part.strip())
        
        # Final fallback for empty result
        return result if result else f"UnnamedType{len(self.classes) + 1}"
        
    def _to_java_field_name(self, xsd_name: str) -> str:
        """Convert XSD element name to Java field name"""
        if not xsd_name:
            return 'unnamed'
            
        # Remove namespace prefix
        if ':' in xsd_name:
            xsd_name = xsd_name.split(':', 1)[1]
            
        if not xsd_name:
            return 'unnamed'
            
        # Convert to camelCase
        parts = xsd_name.replace('-', '_').split('_')
        return parts[0].lower() + ''.join(part.capitalize() for part in parts[1:])
        
    def _xsd_type_to_java(self, xsd_type: str) -> str:
        """Convert XSD type to Java type"""
        if not xsd_type:
            return 'String'
            
        # Remove namespace prefix
        if ':' in xsd_type:
            prefix, local_type = xsd_type.split(':', 1)
            if not local_type:  # Handle case where local_type is empty
                return 'String'
            if prefix in ['xs', 'xsd']:  # Handle both standard XSD prefixes
                xsd_type = f'{prefix}:{local_type}'
            else:
                # Custom type - convert to class name for types ending with 'Type'
                if local_type and (local_type.endswith('Type') or local_type.endswith('type')):
                    return self._to_java_class_name(local_type)
                else:
                    # Unknown custom type, default to String
                    return 'String'
        
        # Check for direct type ending in 'Type' (no namespace)
        if xsd_type and (xsd_type.endswith('Type') or xsd_type.endswith('type')):
            return self._to_java_class_name(xsd_type)
            
        return self.xsd_to_java_types.get(xsd_type, 'String')
        
    def _handle_restriction_type(self, element_info: Dict[str, Any]) -> str:
        """Handle restricted types that might be enums or constrained types"""
        
        # Look for restriction information
        restriction_info = None
        if 'restriction' in element_info:
            restriction_info = element_info['restriction']
        elif 'xsd:restriction' in element_info:
            restriction_info = element_info['xsd:restriction']
        elif 'simpleType' in element_info:
            simple_type = element_info['simpleType']
            if 'restriction' in simple_type:
                restriction_info = simple_type['restriction']
            elif 'xsd:restriction' in simple_type:
                restriction_info = simple_type['xsd:restriction']
                
        if restriction_info:
            # Check if this is an enumeration
            enum_values = []
            
            if 'enumeration' in restriction_info:
                enum_values = restriction_info['enumeration']
            elif 'xsd:enumeration' in restriction_info:
                enum_values = restriction_info['xsd:enumeration']
                
            # If we found enumeration values, this should be treated as an enum type
            if enum_values:
                # Generate a name for this inline enum type
                base_name = element_info.get('name', 'InlineEnum')
                return f"{self._to_java_class_name(base_name)}Enum"
                
            # Check for other restrictions like pattern, length, etc.
            # For now, just return String for other restriction types
            base_type = restriction_info.get('base', 'xs:string')
            if not base_type:
                base_type = 'xs:string'
            return self._xsd_type_to_java(base_type)
            
        return 'String'
        
    def generate_plantuml(self) -> str:
        """Generate PlantUML class diagram"""
        
        # Debug: Show all classes found
        self.console.print(f"Debug: Found {len(self.classes)} classes total:")
        for name, cls in self.classes.items():
            self.console.print(f"  - {name}: {len(cls.attributes)} attributes, type: {cls.xsd_type}")
        
        # Include all classes, not just those with attributes
        # Some classes might be important for relationships even without attributes
        valid_classes = self.classes.copy()
        
        # But for display purposes, we'll show a note if a class has no attributes
        uml = ['@startuml XSD_Java_Classes', '']
        
        # Add packages
        for package in sorted(self.packages):
            # Check if this package has any classes
            package_classes = [cls for cls in valid_classes.values() if cls.package == package]
            if not package_classes:
                continue
                
            uml.append(f'package "{package}" {{')
            
            # Add classes in this package
            for class_name, java_class in valid_classes.items():
                if java_class.package == package:
                    uml.extend(self._class_to_plantuml(java_class))
                    uml.append('')
                    
            uml.append('}')
            uml.append('')
            
        # Add relationships - only for valid classes
        relationships_added = False
        for rel in self.relationships:
            if (rel.from_class in valid_classes and 
                rel.to_class in valid_classes):
                if not relationships_added:
                    uml.append('/' + '* Relationships *' + '/')
                    relationships_added = True
                uml.append(self._relationship_to_plantuml(rel))
            
        uml.append('')
        uml.append('@enduml')
        
        return '\n'.join(uml)
        
    def _class_to_plantuml(self, java_class: JavaClass) -> List[str]:
        """Convert Java class to PlantUML format"""
        
        lines = []
        
        # Class declaration
        class_type = 'enum' if java_class.xsd_type == 'enum' else 'class'
        class_line = f'{class_type} {java_class.name}'
        
        if java_class.extends:
            class_line += f' extends {java_class.extends}'
            
        if java_class.is_abstract:
            class_line = 'abstract ' + class_line
            
        lines.append(class_line + ' {')
        
        # Add attributes
        if java_class.attributes:
            for attr in java_class.attributes:
                visibility = '+' if attr['visibility'] == 'public' else '-'
                static_final = ''
                if attr.get('is_static') and attr.get('is_final'):
                    static_final = ' {static}'
                    
                lines.append(f'  {visibility}{attr["name"]} : {attr["type"]}{static_final}')
        else:
            # Add a placeholder comment for empty classes
            lines.append('  // No attributes found in XSD')
            
        # Add methods (getters/setters)
        if java_class.attributes and java_class.xsd_type != 'enum':
            lines.append('  --')
            for attr in java_class.attributes:
                if not (attr.get('is_static') and attr.get('is_final')):
                    # Getter
                    getter_name = f'get{attr["name"].capitalize()}'
                    lines.append(f'  +{getter_name}() : {attr["type"]}')
                    # Setter
                    setter_name = f'set{attr["name"].capitalize()}'
                    lines.append(f'  +{setter_name}({attr["name"]}: {attr["type"]}) : void')
                    
        lines.append('}')
        
        # Add note if there's documentation
        if java_class.documentation:
            lines.append(f'note right of {java_class.name}')
            lines.append(f'  {java_class.documentation[:100]}{"..." if len(java_class.documentation) > 100 else ""}')
            lines.append('end note')
            
        return lines
        
    def _relationship_to_plantuml(self, rel: Relationship) -> str:
        """Convert relationship to PlantUML format"""
        
        arrow_map = {
            'inheritance': '--|>',
            'composition': '*--',
            'aggregation': 'o--',
            'association': '-->'
        }
        
        arrow = arrow_map.get(rel.relationship_type, '-->')
        label = f' : {rel.label}' if rel.label else ''
        multiplicity = f' "{rel.multiplicity}"' if rel.multiplicity != '1' else ''
        
        return f'{rel.from_class} {arrow} {rel.to_class}{label}{multiplicity}'
        
    def generate_mermaid(self) -> str:
        """Generate Mermaid class diagram"""
        
        mermaid = ['classDiagram']
        
        # Include all classes, not just those with attributes
        valid_classes = self.classes.copy()
        
        # Add classes
        for class_name, java_class in valid_classes.items():
            mermaid.extend(self._class_to_mermaid(java_class))
            
        # Add relationships - filter out empty relationship strings
        for rel in self.relationships:
            relationship_str = self._relationship_to_mermaid(rel)
            if relationship_str.strip():  # Only add non-empty relationships
                mermaid.append(relationship_str)
            
        return '\n'.join(mermaid)
        
    def _class_to_mermaid(self, java_class: JavaClass) -> List[str]:
        """Convert Java class to Mermaid format"""
        
        lines = []
        
        # Class declaration
        lines.append(f'  class {java_class.name} {{')
        
        # Add attributes
        for attr in java_class.attributes:
            visibility = '+' if attr['visibility'] == 'public' else '-'
            lines.append(f'    {visibility}{attr["type"]} {attr["name"]}')
            
        # Add methods
        if java_class.attributes and java_class.xsd_type != 'enum':
            for attr in java_class.attributes:
                if not (attr.get('is_static') and attr.get('is_final')):
                    getter_name = f'get{attr["name"].capitalize()}'
                    setter_name = f'set{attr["name"].capitalize()}'
                    lines.append(f'    +{getter_name}() {attr["type"]}')
                    lines.append(f'    +{setter_name}({attr["type"]}) void')
                    
        lines.append('  }')
        
        return lines
        
    def _relationship_to_mermaid(self, rel: Relationship) -> str:
        """Convert relationship to Mermaid format"""
        
        # Only include relationships where both classes exist and have content
        if (rel.from_class not in self.classes or 
            rel.to_class not in self.classes or
            not self.classes[rel.from_class].attributes or
            not self.classes[rel.to_class].attributes):
            return ""
        
        arrow_map = {
            'inheritance': '<|--',
            'composition': '*--',
            'aggregation': 'o--',
            'association': '-->'
        }
        
        arrow = arrow_map.get(rel.relationship_type, '-->')
        label = f' : {rel.label}' if rel.label else ''
        
        return f'  {rel.to_class} {arrow} {rel.from_class}{label}'
        
    def generate_java_code(self) -> Dict[str, str]:
        """Generate Java source code for all classes"""
        
        java_files = {}
        
        for class_name, java_class in self.classes.items():
            java_code = self._class_to_java_code(java_class)
            package_dir = java_class.package.replace('.', '/')
            file_path = f'{package_dir}/{class_name}.java'
            java_files[file_path] = java_code
            
        return java_files
        
    def _class_to_java_code(self, java_class: JavaClass) -> str:
        """Convert Java class to actual Java code"""
        
        lines = []
        
        # Package declaration
        lines.append(f'package {java_class.package};')
        lines.append('')
        
        # Imports
        imports = set()
        for attr in java_class.attributes:
            if attr['type'].startswith('List<'):
                imports.add('import java.util.List;')
                imports.add('import java.util.ArrayList;')
            elif attr['type'] in ['LocalDate', 'LocalDateTime', 'LocalTime']:
                imports.add(f'import java.time.{attr["type"]};')
            elif attr['type'] == 'BigDecimal':
                imports.add('import java.math.BigDecimal;')
            elif attr['type'] == 'URI':
                imports.add('import java.net.URI;')
                
        for imp in sorted(imports):
            lines.append(imp)
            
        if imports:
            lines.append('')
            
        # Class documentation
        if java_class.documentation:
            lines.append('/**')
            lines.append(f' * {java_class.documentation}')
            lines.append(' * Generated from XSD schema')
            lines.append(' */')
            
        # Class declaration
        class_decl = 'public '
        if java_class.is_abstract:
            class_decl += 'abstract '
            
        if java_class.xsd_type == 'enum':
            class_decl += f'enum {java_class.name}'
        else:
            class_decl += f'class {java_class.name}'
            
        if java_class.extends:
            class_decl += f' extends {java_class.extends}'
            
        lines.append(class_decl + ' {')
        
        # Enum values (for enum classes)
        if java_class.xsd_type == 'enum':
            enum_values = [attr['name'] for attr in java_class.attributes if attr.get('is_static') and attr.get('is_final')]
            if enum_values:
                lines.append(f'    {", ".join(enum_values)};')
                lines.append('')
        else:
            # Fields
            for attr in java_class.attributes:
                if not (attr.get('is_static') and attr.get('is_final')):
                    lines.append(f'    private {attr["type"]} {attr["name"]};')
                    
            lines.append('')
            
            # Constructor
            lines.append(f'    public {java_class.name}() {{')
            lines.append('    }')
            lines.append('')
            
            # Getters and Setters
            for attr in java_class.attributes:
                if not (attr.get('is_static') and attr.get('is_final')):
                    # Getter
                    getter_name = f'get{attr["name"].capitalize()}'
                    lines.append(f'    public {attr["type"]} {getter_name}() {{')
                    lines.append(f'        return {attr["name"]};')
                    lines.append('    }')
                    lines.append('')
                    
                    # Setter
                    setter_name = f'set{attr["name"].capitalize()}'
                    lines.append(f'    public void {setter_name}({attr["type"]} {attr["name"]}) {{')
                    lines.append(f'        this.{attr["name"]} = {attr["name"]};')
                    lines.append('    }')
                    lines.append('')
                    
        lines.append('}')
        
        return '\n'.join(lines)
        
    def _build_summary(self) -> Dict[str, Any]:
        """Build summary of generated Java UML model"""
        
        return {
            'classes': len(self.classes),
            'packages': len(self.packages),
            'relationships': len(self.relationships),
            'class_details': {name: {
                'package': cls.package,
                'attributes': len(cls.attributes),
                'type': cls.xsd_type
            } for name, cls in self.classes.items()},
            'package_list': sorted(self.packages),
            'relationship_types': {
                rel_type: len([r for r in self.relationships if r.relationship_type == rel_type])
                for rel_type in set(r.relationship_type for r in self.relationships)
            }
        }
        
    def save_outputs(self, formats: List[str] = ['plantuml', 'mermaid', 'java']):
        """Save generated UML and code to files"""
        
        results = {}
        
        if 'plantuml' in formats:
            plantuml_content = self.generate_plantuml()
            plantuml_file = self.output_dir / 'java_classes.puml'
            with open(plantuml_file, 'w', encoding='utf-8') as f:
                f.write(plantuml_content)
            results['plantuml'] = str(plantuml_file)
            
        if 'mermaid' in formats:
            mermaid_content = self.generate_mermaid()
            mermaid_file = self.output_dir / 'java_classes.mmd'
            with open(mermaid_file, 'w', encoding='utf-8') as f:
                f.write(mermaid_content)
            results['mermaid'] = str(mermaid_file)
            
        if 'java' in formats:
            java_files = self.generate_java_code()
            java_dir = self.output_dir / 'java'
            java_dir.mkdir(exist_ok=True)
            
            for file_path, java_code in java_files.items():
                full_path = java_dir / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(java_code)
                    
            results['java'] = str(java_dir)
            
        # Save summary
        summary = self._build_summary()
        summary_file = self.output_dir / 'java_uml_summary.json'
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        results['summary'] = str(summary_file)
        
        return results
        
    def print_summary(self, summary: Dict[str, Any]):
        """Print analysis summary"""
        
        self.console.print("\n📊 Java UML Generation Summary")
        
        # Main statistics table
        table = Table(title="Java Classes Generated")
        table.add_column("Metric", style="cyan")
        table.add_column("Count", style="magenta", justify="right")
        
        table.add_row("Java Classes", str(summary['classes']))
        table.add_row("Packages", str(summary['packages']))
        table.add_row("Relationships", str(summary['relationships']))
        
        self.console.print(table)
        
        # Package breakdown
        if summary['package_list']:
            self.console.print("\n📦 Packages Created:")
            for package in summary['package_list']:
                class_count = len([c for c in summary['class_details'].values() if c['package'] == package])
                self.console.print(f"  • {package} ({class_count} classes)")
                
        # Relationship breakdown
        if summary['relationship_types']:
            self.console.print("\n🔗 Relationships:")
            for rel_type, count in summary['relationship_types'].items():
                self.console.print(f"  • {rel_type.title()}: {count}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Generate Java UML class diagrams from XSD files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate from single XSD file
  python java_uml_generator.py schema.xsd
  
  # Generate from multiple XSD files
  python java_uml_generator.py schema1.xsd schema2.xsd schema3.xsd
  
  # Generate from directory of XSD files
  python java_uml_generator.py *.xsd
  
  # Specify output formats and directory
  python java_uml_generator.py schema.xsd --formats plantuml mermaid java --output-dir ./uml_output
        """
    )
    
    parser.add_argument('xsd_files', nargs='+', 
                       help='XSD files to analyze')
    parser.add_argument('--output-dir', '-o', default='./output',
                       help='Output directory for generated files (default: ./output)')
    parser.add_argument('--formats', '-f', nargs='+', 
                       choices=['plantuml', 'mermaid', 'java', 'all'],
                       default=['plantuml', 'mermaid', 'java'],
                       help='Output formats to generate (default: all)')
    parser.add_argument('--java-package', 
                       help='Java package name for generated classes (default: derived from namespace)')
    parser.add_argument('--combined', action='store_true',
                       help='Combine multiple XSD files into single output')
    parser.add_argument('--summary-only', '-s', action='store_true',
                       help='Only show summary, don\'t generate files')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Setup logging
    if args.verbose:
        logging.basicConfig(level=logging.INFO)
        
    # Handle 'all' format selection
    if 'all' in args.formats:
        args.formats = ['plantuml', 'mermaid', 'java']
        
    try:
        # Initialize generator
        generator = JavaUMLGenerator(args.output_dir, args.java_package)
        
        # Analyze XSD files
        summary = generator.analyze_xsd_files(args.xsd_files)
        
        # Print summary
        generator.print_summary(summary)
        
        if not args.summary_only:
            # Generate and save outputs
            rprint(f"\n💾 Generating files in formats: {', '.join(args.formats)}")
            results = generator.save_outputs(args.formats)
            
            rprint("\n✅ Files generated:")
            for format_name, file_path in results.items():
                rprint(f"  📄 {format_name.title()}: {file_path}")
                
            rprint(f"\n🎯 All outputs saved to: {args.output_dir}")
            
    except Exception as e:
        rprint(f"\n❌ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
