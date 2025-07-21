"""
Core XSD parsing utilities for extracting structure and metadata from XML Schema files.
"""

import os
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import logging
from lxml import etree
from lxml.etree import _Element

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class XSDElement:
    """Represents an XSD element with its properties and relationships."""
    name: str
    type: Optional[str] = None
    min_occurs: str = "1"
    max_occurs: str = "1"
    documentation: Optional[str] = None
    attributes: List[Dict[str, Any]] = field(default_factory=list)
    children: List['XSDElement'] = field(default_factory=list)
    parent: Optional['XSDElement'] = None
    namespace: Optional[str] = None
    is_complex_type: bool = False
    is_simple_type: bool = False
    restrictions: Dict[str, Any] = field(default_factory=dict)

@dataclass
class XSDComplexType:
    """Represents an XSD complex type definition."""
    name: str
    elements: List[XSDElement] = field(default_factory=list)
    attributes: List[Dict[str, Any]] = field(default_factory=list)
    documentation: Optional[str] = None
    base_type: Optional[str] = None
    is_extension: bool = False
    is_restriction: bool = False

@dataclass
class XSDSimpleType:
    """Represents an XSD simple type definition."""
    name: str
    base_type: Optional[str] = None
    restrictions: Dict[str, Any] = field(default_factory=dict)
    documentation: Optional[str] = None
    enumerations: List[str] = field(default_factory=list)

class XSDParser:
    """
    Parser for XSD files that extracts structure, types, and relationships.
    Optimized for handling large, complex schema files.
    """
    
    def __init__(self, xsd_path: str):
        """
        Initialize parser with XSD file path.
        
        Args:
            xsd_path: Path to the XSD file to parse
        """
        self.xsd_path = Path(xsd_path)
        self.root: Optional[_Element] = None
        self.namespaces: Dict[str, str] = {}
        self.target_namespace: Optional[str] = None
        
        # Parsed components
        self.elements: List[XSDElement] = []
        self.complex_types: Dict[str, XSDComplexType] = {}
        self.simple_types: Dict[str, XSDSimpleType] = {}
        self.global_elements: Dict[str, XSDElement] = {}
        self.global_attributes: Dict[str, Dict[str, Any]] = {}
        self.attribute_groups: Dict[str, Dict[str, Any]] = {}
        self.dependencies: Dict[str, Set[str]] = {}
        
        # Statistics
        self.stats = {
            'total_elements': 0,
            'total_complex_types': 0,
            'total_simple_types': 0,
            'max_depth': 0,
            'total_attributes': 0
        }
        
        self._load_schema()
    
    def _load_schema(self) -> None:
        """Load and parse the XSD file."""
        try:
            with open(self.xsd_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse with lxml for better performance
            parser = etree.XMLParser(recover=True)
            self.root = etree.fromstring(content.encode('utf-8'), parser)
            
            # Validate that parsing was successful
            if self.root is None:
                raise ValueError(f"Failed to parse XSD file: {self.xsd_path}")
            
            # Extract namespaces
            self.namespaces = self.root.nsmap or {}
            self.target_namespace = self.root.get('targetNamespace', None)
            
            logger.info(f"Loaded XSD file: {self.xsd_path}")
            logger.info(f"Target namespace: {self.target_namespace}")
            logger.info(f"Namespaces found: {len(self.namespaces)}")
            
        except Exception as e:
            logger.error(f"Error loading XSD file {self.xsd_path}: {e}")
            raise
    
    def parse(self) -> Dict[str, Any]:
        """
        Parse the XSD file and extract all components.
        
        Returns:
            Dictionary containing parsed structure and metadata
        """
        if self.root is None:
            raise ValueError("XSD file not loaded")
        
        logger.info("Starting XSD parsing...")
        
        # Parse in order of dependencies
        self._parse_simple_types()
        self._parse_global_attributes()
        self._parse_attribute_groups()
        self._parse_complex_types()
        self._parse_global_elements()
        self._parse_root_elements()
        self._calculate_dependencies()
        self._calculate_statistics()
        
        logger.info(f"Parsing complete. Found {self.stats['total_elements']} elements, "
                   f"{self.stats['total_complex_types']} complex types, "
                   f"{self.stats['total_simple_types']} simple types")
        
        return self.get_structure()
    
    def _parse_simple_types(self) -> None:
        """Parse all simple type definitions."""
        if self.root is None:
            return
            
        xpath = './/xs:simpleType[@name]'
        simple_type_elements = self.root.xpath(xpath, namespaces={'xs': 'http://www.w3.org/2001/XMLSchema'})
        
        for elem in simple_type_elements:
            simple_type = self._extract_simple_type(elem)
            self.simple_types[simple_type.name] = simple_type
        
        logger.info(f"Parsed {len(self.simple_types)} simple types")
    
    def _parse_complex_types(self) -> None:
        """Parse all complex type definitions."""
        if self.root is None:
            return
            
        xpath = './/xs:complexType[@name]'
        complex_type_elements = self.root.xpath(xpath, namespaces={'xs': 'http://www.w3.org/2001/XMLSchema'})
        
        for elem in complex_type_elements:
            complex_type = self._extract_complex_type(elem)
            self.complex_types[complex_type.name] = complex_type
        
        logger.info(f"Parsed {len(self.complex_types)} complex types")
    
    def _parse_global_elements(self) -> None:
        """Parse global element definitions."""
        if self.root is None:
            return
            
        xpath = './/xs:element[@name and not(parent::xs:sequence or parent::xs:choice or parent::xs:all)]'
        global_elements = self.root.xpath(xpath, namespaces={'xs': 'http://www.w3.org/2001/XMLSchema'})
        
        for elem in global_elements:
            element = self._extract_element(elem)
            self.global_elements[element.name] = element
        
        logger.info(f"Parsed {len(self.global_elements)} global elements")
    
    def _parse_global_attributes(self) -> None:
        """Parse global attribute definitions."""
        if self.root is None:
            return
            
        # Parse both xs:attribute and xsd:attribute
        for prefix in ['xs', 'xsd']:
            xpath = f'.//{prefix}:attribute[@name]'
            global_attrs = self.root.xpath(xpath, namespaces={prefix: 'http://www.w3.org/2001/XMLSchema'})
            
            for attr_elem in global_attrs:
                attr_name = attr_elem.get('name')
                if not attr_name:
                    continue
                    
                self.global_attributes[attr_name] = {
                    'name': attr_name,
                    'type': attr_elem.get('type', 'xsd:string'),
                    'use': attr_elem.get('use', 'optional'),
                    'default': attr_elem.get('default'),
                    'fixed': attr_elem.get('fixed'),
                    'documentation': self._extract_documentation_from_element(attr_elem)
                }
        
        logger.info(f"Parsed {len(self.global_attributes)} global attributes")
    
    def _parse_attribute_groups(self) -> None:
        """Parse attribute group definitions."""
        if self.root is None:
            return
            
        # Parse both xs:attributeGroup and xsd:attributeGroup
        for prefix in ['xs', 'xsd']:
            xpath = f'.//{prefix}:attributeGroup[@name]'
            attr_groups = self.root.xpath(xpath, namespaces={prefix: 'http://www.w3.org/2001/XMLSchema'})
            
            for group_elem in attr_groups:
                group_name = group_elem.get('name')
                if not group_name:
                    continue
                
                # Extract attributes within this group
                attributes = []
                attr_xpath = f'./{prefix}:attribute'
                attr_elements = group_elem.xpath(attr_xpath, namespaces={prefix: 'http://www.w3.org/2001/XMLSchema'})
                
                for attr_elem in attr_elements:
                    attr_info = self._extract_attribute_info(attr_elem, prefix)
                    if attr_info:
                        attributes.append(attr_info)
                
                self.attribute_groups[group_name] = {
                    'name': group_name,
                    'attributes': attributes,
                    'documentation': self._extract_documentation_from_element(group_elem)
                }
        
        logger.info(f"Parsed {len(self.attribute_groups)} attribute groups")
    
    def _parse_root_elements(self) -> None:
        """Parse root-level elements that can be document roots."""
        if self.root is None:
            return
            
        xpath = './xs:element'
        root_elements = self.root.xpath(xpath, namespaces={'xs': 'http://www.w3.org/2001/XMLSchema'})
        
        for elem in root_elements:
            element = self._extract_element(elem, depth=0)
            self.elements.append(element)
    
    def _extract_attribute_info(self, attr_elem: _Element, prefix: str = 'xs') -> Optional[Dict[str, Any]]:
        """Extract attribute information from an attribute element."""
        attr_name = attr_elem.get('name', None)
        attr_ref = attr_elem.get('ref', None)
        
        if attr_name:
            # Direct attribute definition
            return {
                'name': attr_name,
                'type': attr_elem.get('type', 'xsd:string'),
                'use': attr_elem.get('use', 'optional'),
                'default': attr_elem.get('default', None),
                'fixed': attr_elem.get('fixed', None),
                'documentation': self._extract_documentation_from_element(attr_elem)
            }
        elif attr_ref:
            # Reference to global attribute
            # Remove namespace prefix from ref if present
            ref_name = attr_ref.split(':')[-1] if ':' in attr_ref else attr_ref
            
            # Look up the global attribute
            if ref_name in self.global_attributes:
                attr_info = self.global_attributes[ref_name].copy()
                # Override use if specified in the reference
                use_override = attr_elem.get('use', None)
                if use_override:
                    attr_info['use'] = use_override
                return attr_info
            else:
                # Create a placeholder if global attribute not found
                return {
                    'name': ref_name,
                    'type': 'String',  # Default type
                    'use': attr_elem.get('use', 'optional'),
                    'default': attr_elem.get('default', None),
                    'documentation': f"Reference to global attribute: {attr_ref}"
                }
        
        return None
    
    def _extract_documentation_from_element(self, elem: _Element) -> str:
        """Extract documentation from an XSD element's annotation."""
        # Look for annotation/documentation
        for prefix in ['xs', 'xsd']:
            annotation_xpath = f'./{prefix}:annotation/{prefix}:documentation'
            doc_elements = elem.xpath(annotation_xpath, namespaces={prefix: 'http://www.w3.org/2001/XMLSchema'})
            
            if doc_elements:
                # Combine all documentation elements
                docs = []
                for doc_elem in doc_elements:
                    if doc_elem.text:
                        docs.append(doc_elem.text.strip())
                return ' '.join(docs)
        
        return ""
    
    def _extract_element(self, elem: _Element, parent: Optional[XSDElement] = None, depth: int = 0) -> XSDElement:
        """Extract an XSD element with all its properties and children."""
        name = elem.get('name', 'unnamed')
        element_type = elem.get('type', None)
        min_occurs = elem.get('minOccurs', '1')
        max_occurs = elem.get('maxOccurs', '1')
        
        # Extract documentation
        doc_elem = elem.find('.//xs:documentation', namespaces={'xs': 'http://www.w3.org/2001/XMLSchema'})
        documentation = doc_elem.text.strip() if doc_elem is not None and doc_elem.text else None
        
        # Create element
        xsd_element = XSDElement(
            name=name,
            type=element_type,
            min_occurs=min_occurs,
            max_occurs=max_occurs,
            documentation=documentation,
            parent=parent,
            namespace=self.target_namespace
        )
        
        # Extract attributes
        attr_elements = elem.xpath('.//xs:attribute', namespaces={'xs': 'http://www.w3.org/2001/XMLSchema'})
        for attr_elem in attr_elements:
            attr_info = {
                'name': attr_elem.get('name'),
                'type': attr_elem.get('type'),
                'use': attr_elem.get('use', 'optional'),
                'default': attr_elem.get('default')
            }
            xsd_element.attributes.append(attr_info)
        
        # Check for inline complex type
        complex_type_elem = elem.find('./xs:complexType', namespaces={'xs': 'http://www.w3.org/2001/XMLSchema'})
        if complex_type_elem is not None:
            xsd_element.is_complex_type = True
            self._extract_complex_type_children(complex_type_elem, xsd_element, depth + 1)
        
        # Update statistics
        self.stats['max_depth'] = max(self.stats['max_depth'], depth)
        self.stats['total_attributes'] += len(xsd_element.attributes)
        
        return xsd_element
    
    def _extract_complex_type(self, elem: _Element) -> XSDComplexType:
        """Extract a complex type definition."""
        name = elem.get('name', 'unnamed')
        
        # Extract documentation
        doc_elem = elem.find('.//xs:documentation', namespaces={'xs': 'http://www.w3.org/2001/XMLSchema'})
        documentation = doc_elem.text.strip() if doc_elem is not None and doc_elem.text else None
        
        complex_type = XSDComplexType(name=name, documentation=documentation)
        
        # Extract elements and attributes
        self._extract_complex_type_children(elem, None, 0, complex_type)
        
        return complex_type
    
    def _extract_simple_type(self, elem: _Element) -> XSDSimpleType:
        """Extract a simple type definition."""
        name = elem.get('name', 'unnamed')
        
        # Extract documentation
        doc_elem = elem.find('.//xs:documentation', namespaces={'xs': 'http://www.w3.org/2001/XMLSchema'})
        documentation = doc_elem.text.strip() if doc_elem is not None and doc_elem.text else None
        
        simple_type = XSDSimpleType(name=name, documentation=documentation)
        
        # Extract base type and restrictions
        restriction_elem = elem.find('./xs:restriction', namespaces={'xs': 'http://www.w3.org/2001/XMLSchema'})
        if restriction_elem is not None:
            simple_type.base_type = restriction_elem.get('base')
            
            # Extract enumerations
            enum_elements = restriction_elem.xpath('./xs:enumeration', namespaces={'xs': 'http://www.w3.org/2001/XMLSchema'})
            simple_type.enumerations = [e.get('value') for e in enum_elements if e.get('value')]
            
            # Extract other restrictions
            for restriction in ['minLength', 'maxLength', 'pattern', 'minInclusive', 'maxInclusive']:
                restriction_elem_found = restriction_elem.find(f'./xs:{restriction}', namespaces={'xs': 'http://www.w3.org/2001/XMLSchema'})
                if restriction_elem_found is not None:
                    simple_type.restrictions[restriction] = restriction_elem_found.get('value')
        
        return simple_type
    
    def _extract_complex_type_children(self, elem: _Element, parent_element: Optional[XSDElement], 
                                     depth: int, complex_type: Optional[XSDComplexType] = None) -> None:
        """Extract children of a complex type (sequence, choice, all)."""
        # Handle sequence, choice, all
        for container in ['sequence', 'choice', 'all']:
            container_elem = elem.find(f'./xs:{container}', namespaces={'xs': 'http://www.w3.org/2001/XMLSchema'})
            if container_elem is not None:
                child_elements = container_elem.xpath('./xs:element', namespaces={'xs': 'http://www.w3.org/2001/XMLSchema'})
                for child_elem in child_elements:
                    child_element = self._extract_element(child_elem, parent_element, depth + 1)
                    
                    if parent_element:
                        parent_element.children.append(child_element)
                    if complex_type:
                        complex_type.elements.append(child_element)
        
        # Handle attributes with support for both xs: and xsd: prefixes
        # Use a set to avoid duplicates when processing both prefixes
        processed_attributes = set()
        processed_attr_groups = set()
        
        for prefix in ['xs', 'xsd']:
            # Handle direct attributes
            attr_xpath = f'./{prefix}:attribute'
            attr_elements = elem.xpath(attr_xpath, namespaces={prefix: 'http://www.w3.org/2001/XMLSchema'})
            
            for attr_elem in attr_elements:
                # Create a unique key to avoid duplicates
                attr_key = (attr_elem.get('name', ''), attr_elem.get('ref', ''), attr_elem.get('type', ''))
                if attr_key not in processed_attributes:
                    processed_attributes.add(attr_key)
                    attr_info = self._extract_attribute_info(attr_elem, prefix)
                    if attr_info:
                        if parent_element:
                            parent_element.attributes.append(attr_info)
                        if complex_type:
                            complex_type.attributes.append(attr_info)
            
            # Handle attribute group references
            attr_group_xpath = f'./{prefix}:attributeGroup[@ref]'
            attr_group_refs = elem.xpath(attr_group_xpath, namespaces={prefix: 'http://www.w3.org/2001/XMLSchema'})
            
            for attr_group_ref in attr_group_refs:
                ref_name = attr_group_ref.get('ref', None)
                if ref_name and ref_name not in processed_attr_groups:
                    processed_attr_groups.add(ref_name)
                    # Remove namespace prefix from ref if present
                    group_name = ref_name.split(':')[-1] if ':' in ref_name else ref_name
                    
                    # Look up the attribute group and add its attributes
                    if group_name in self.attribute_groups:
                        group_attrs = self.attribute_groups[group_name]['attributes']
                        for attr_info in group_attrs:
                            if parent_element:
                                parent_element.attributes.append(attr_info.copy())
                            if complex_type:
                                complex_type.attributes.append(attr_info.copy())
    
    def _calculate_dependencies(self) -> None:
        """Calculate dependencies between schema components."""
        # This is a simplified dependency calculation
        # In practice, you'd want to track type references, imports, includes, etc.
        for element in self.elements:
            self._collect_element_dependencies(element)
    
    def _collect_element_dependencies(self, element: XSDElement) -> None:
        """Collect dependencies for a single element."""
        deps = set()
        
        if element.type:
            deps.add(element.type)
        
        for child in element.children:
            if child.type:
                deps.add(child.type)
            self._collect_element_dependencies(child)
        
        if deps:
            self.dependencies[element.name] = deps
    
    def _calculate_statistics(self) -> None:
        """Calculate parsing statistics."""
        self.stats['total_elements'] = len(self.elements) + len(self.global_elements)
        self.stats['total_complex_types'] = len(self.complex_types)
        self.stats['total_simple_types'] = len(self.simple_types)
        
        # Count all nested elements
        def count_nested_elements(element: XSDElement) -> int:
            count = 1
            for child in element.children:
                count += count_nested_elements(child)
            return count
        
        total_nested = sum(count_nested_elements(elem) for elem in self.elements)
        self.stats['total_elements'] += total_nested
    
    def get_structure(self) -> Dict[str, Any]:
        """
        Get the complete parsed structure.
        
        Returns:
            Dictionary containing all parsed components and metadata
        """
        return {
            'metadata': {
                'file_path': str(self.xsd_path),
                'target_namespace': self.target_namespace,
                'namespaces': self.namespaces,
                'statistics': self.stats
            },
            'elements': [self._element_to_dict(elem) for elem in self.elements],
            'global_elements': {name: self._element_to_dict(elem) for name, elem in self.global_elements.items()},
            'complex_types': {name: self._complex_type_to_dict(ct) for name, ct in self.complex_types.items()},
            'simple_types': {name: self._simple_type_to_dict(st) for name, st in self.simple_types.items()},
            'global_attributes': self.global_attributes,
            'attribute_groups': self.attribute_groups,
            'dependencies': {name: list(deps) for name, deps in self.dependencies.items()}
        }
    
    def _element_to_dict(self, element: XSDElement) -> Dict[str, Any]:
        """Convert XSDElement to dictionary."""
        return {
            'name': element.name,
            'type': element.type,
            'min_occurs': element.min_occurs,
            'max_occurs': element.max_occurs,
            'documentation': element.documentation,
            'attributes': element.attributes,
            'children': [self._element_to_dict(child) for child in element.children],
            'namespace': element.namespace,
            'is_complex_type': element.is_complex_type,
            'is_simple_type': element.is_simple_type,
            'restrictions': element.restrictions
        }
    
    def _complex_type_to_dict(self, complex_type: XSDComplexType) -> Dict[str, Any]:
        """Convert XSDComplexType to dictionary."""
        return {
            'name': complex_type.name,
            'documentation': complex_type.documentation,
            'elements': [self._element_to_dict(elem) for elem in complex_type.elements],
            'attributes': complex_type.attributes,
            'base_type': complex_type.base_type,
            'is_extension': complex_type.is_extension,
            'is_restriction': complex_type.is_restriction
        }
    
    def _simple_type_to_dict(self, simple_type: XSDSimpleType) -> Dict[str, Any]:
        """Convert XSDSimpleType to dictionary."""
        return {
            'name': simple_type.name,
            'base_type': simple_type.base_type,
            'documentation': simple_type.documentation,
            'restrictions': simple_type.restrictions,
            'enumerations': simple_type.enumerations
        }
    
    def find_element(self, name: str) -> Optional[XSDElement]:
        """Find an element by name in the schema."""
        # Check global elements first
        if name in self.global_elements:
            return self.global_elements[name]
        
        # Search in root elements and their children
        def search_element(element: XSDElement) -> Optional[XSDElement]:
            if element.name == name:
                return element
            for child in element.children:
                result = search_element(child)
                if result:
                    return result
            return None
        
        for element in self.elements:
            result = search_element(element)
            if result:
                return result
        
        return None
    
    def get_element_path(self, element_name: str) -> List[str]:
        """Get the path to an element from root."""
        def find_path(element: XSDElement, target: str, path: List[str]) -> Optional[List[str]]:
            current_path = path + [element.name]
            if element.name == target:
                return current_path
            
            for child in element.children:
                result = find_path(child, target, current_path)
                if result:
                    return result
            return None
        
        for root_element in self.elements:
            path = find_path(root_element, element_name, [])
            if path:
                return path
        
        return []
