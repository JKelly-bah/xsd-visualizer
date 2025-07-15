"""
Multi-file XSD parser that handles imports, includes, and redefines.
Extends the base XSD parser to work with schema spread across multiple files.
"""

import os
import urllib.parse
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass
from pathlib import Path
import logging
from lxml import etree
from lxml.etree import _Element

from .xsd_parser import XSDParser, XSDElement, XSDComplexType, XSDSimpleType

logger = logging.getLogger(__name__)

@dataclass
class SchemaReference:
    """Represents a reference to another schema file."""
    reference_type: str  # 'import', 'include', or 'redefine'
    namespace: Optional[str]
    schema_location: Optional[str]
    resolved_path: Optional[Path] = None

class MultiFileXSDParser(XSDParser):
    """
    Enhanced XSD parser that handles multi-file schemas with imports, includes, and redefines.
    """
    
    def __init__(self, xsd_path: str, base_dir: Optional[str] = None):
        """
        Initialize multi-file parser.
        
        Args:
            xsd_path: Path to the main XSD file
            base_dir: Base directory for resolving relative schema locations
        """
        self.base_dir = Path(base_dir) if base_dir else Path(xsd_path).parent
        self.processed_files: Set[Path] = set()
        self.schema_references: List[SchemaReference] = []
        self.imported_namespaces: Dict[str, str] = {}  # namespace -> file path
        self.all_roots: Dict[str, _Element] = {}  # file path -> root element
        self.file_dependencies: Dict[str, List[str]] = {}  # file -> list of dependent files
        
        # Initialize base parser
        super().__init__(xsd_path)
    
    def _load_schema(self) -> None:
        """Load and parse the main XSD file and all referenced files."""
        try:
            # Load main file
            main_path = Path(self.xsd_path)
            self._load_schema_file(main_path, is_main=True)
            
            # Process all referenced files
            self._process_schema_references()
            
            logger.info(f"Loaded {len(self.all_roots)} schema files")
            logger.info(f"Target namespace: {self.target_namespace}")
            logger.info(f"Total namespaces: {len(self.namespaces)}")
            
        except Exception as e:
            logger.error(f"Error loading multi-file XSD schema: {e}")
            raise
    
    def _load_schema_file(self, file_path: Path, is_main: bool = False) -> _Element:
        """
        Load a single schema file and extract references.
        
        Args:
            file_path: Path to the schema file
            is_main: Whether this is the main schema file
            
        Returns:
            Root element of the loaded schema
        """
        if file_path in self.processed_files:
            return self.all_roots[str(file_path)]
        
        logger.info(f"Loading schema file: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse with lxml
            parser = etree.XMLParser(recover=True)
            root = etree.fromstring(content.encode('utf-8'), parser)
            
            # Store root element
            self.all_roots[str(file_path)] = root
            self.processed_files.add(file_path)
            
            if is_main:
                self.root = root
                self.namespaces = root.nsmap or {}
                self.target_namespace = root.get('targetNamespace', None)
            else:
                # Merge namespaces from imported files
                file_namespaces = root.nsmap or {}
                self.namespaces.update(file_namespaces)
            
            # Extract schema references (import, include, redefine)
            self._extract_schema_references(root, file_path)
            
            return root
            
        except Exception as e:
            logger.error(f"Error loading schema file {file_path}: {e}")
            raise
    
    def _extract_schema_references(self, root: _Element, current_file: Path) -> None:
        """Extract import, include, and redefine references from a schema."""
        references = []
        
        # Extract imports
        imports = root.xpath('./xs:import', namespaces={'xs': 'http://www.w3.org/2001/XMLSchema'})
        for import_elem in imports:
            ref = SchemaReference(
                reference_type='import',
                namespace=import_elem.get('namespace'),
                schema_location=import_elem.get('schemaLocation')
            )
            if ref.schema_location:
                ref.resolved_path = self._resolve_schema_location(ref.schema_location, current_file)
                references.append(ref)
                
                # Track namespace mapping
                if ref.namespace and ref.resolved_path:
                    self.imported_namespaces[ref.namespace] = str(ref.resolved_path)
        
        # Extract includes
        includes = root.xpath('./xs:include', namespaces={'xs': 'http://www.w3.org/2001/XMLSchema'})
        for include_elem in includes:
            ref = SchemaReference(
                reference_type='include',
                namespace=None,  # includes inherit the target namespace
                schema_location=include_elem.get('schemaLocation')
            )
            if ref.schema_location:
                ref.resolved_path = self._resolve_schema_location(ref.schema_location, current_file)
                references.append(ref)
        
        # Extract redefines
        redefines = root.xpath('./xs:redefine', namespaces={'xs': 'http://www.w3.org/2001/XMLSchema'})
        for redefine_elem in redefines:
            ref = SchemaReference(
                reference_type='redefine',
                namespace=None,  # redefines inherit the target namespace
                schema_location=redefine_elem.get('schemaLocation')
            )
            if ref.schema_location:
                ref.resolved_path = self._resolve_schema_location(ref.schema_location, current_file)
                references.append(ref)
        
        # Store references
        self.schema_references.extend(references)
        
        # Track file dependencies
        file_key = str(current_file)
        if file_key not in self.file_dependencies:
            self.file_dependencies[file_key] = []
        
        for ref in references:
            if ref.resolved_path:
                self.file_dependencies[file_key].append(str(ref.resolved_path))
        
        logger.info(f"Found {len(references)} schema references in {current_file}")
    
    def _resolve_schema_location(self, schema_location: str, current_file: Path) -> Optional[Path]:
        """
        Resolve a schema location to an absolute path.
        
        Args:
            schema_location: The schemaLocation attribute value
            current_file: The file containing the reference
            
        Returns:
            Resolved absolute path or None if not resolvable
        """
        try:
            # Handle absolute URLs (skip for offline processing)
            if schema_location.startswith(('http://', 'https://', 'ftp://')):
                logger.warning(f"Skipping remote schema location: {schema_location}")
                return None
            
            # Handle absolute file paths
            if os.path.isabs(schema_location):
                resolved = Path(schema_location)
            else:
                # Resolve relative to current file's directory
                resolved = current_file.parent / schema_location
            
            # Normalize the path
            resolved = resolved.resolve()
            
            if not resolved.exists():
                logger.warning(f"Schema file not found: {resolved}")
                return None
            
            return resolved
            
        except Exception as e:
            logger.error(f"Error resolving schema location '{schema_location}': {e}")
            return None
    
    def _process_schema_references(self) -> None:
        """Process all discovered schema references recursively."""
        # Keep processing until no new references are found
        processed_count = 0
        
        while processed_count < len(self.schema_references):
            current_refs = self.schema_references[processed_count:]
            processed_count = len(self.schema_references)
            
            for ref in current_refs:
                if ref.resolved_path and ref.resolved_path not in self.processed_files:
                    self._load_schema_file(ref.resolved_path)
    
    def parse(self) -> Dict[str, Any]:
        """
        Parse the multi-file XSD schema and extract all components.
        
        Returns:
            Dictionary containing parsed structure and metadata
        """
        if not self.all_roots:
            raise ValueError("No schema files loaded")
        
        logger.info("Starting multi-file XSD parsing...")
        
        # Parse components from all loaded files
        self._parse_all_files()
        
        # Calculate dependencies across files
        self._calculate_cross_file_dependencies()
        
        # Calculate statistics
        self._calculate_statistics()
        
        logger.info(f"Multi-file parsing complete. Found {self.stats['total_elements']} elements, "
                   f"{self.stats['total_complex_types']} complex types, "
                   f"{self.stats['total_simple_types']} simple types across {len(self.all_roots)} files")
        
        return self.get_structure()
    
    def _parse_all_files(self) -> None:
        """Parse components from all loaded schema files."""
        for file_path, root in self.all_roots.items():
            logger.info(f"Parsing components from {file_path}")
            
            # Temporarily set root to parse this file
            original_root = self.root
            self.root = root
            
            try:
                # Parse components with file context
                self._parse_simple_types_from_file(file_path)
                self._parse_complex_types_from_file(file_path)
                self._parse_global_elements_from_file(file_path)
                
                # Only parse root elements from main file
                if root == original_root:
                    self._parse_root_elements()
                    
            finally:
                # Restore original root
                self.root = original_root
    
    def _parse_simple_types_from_file(self, file_path: str) -> None:
        """Parse simple types from a specific file."""
        if self.root is None:
            return
            
        xpath = './/xs:simpleType[@name]'
        simple_type_elements = self.root.xpath(xpath, namespaces={'xs': 'http://www.w3.org/2001/XMLSchema'})
        
        for elem in simple_type_elements:
            simple_type = self._extract_simple_type(elem)
            # TODO: Add file source information tracking
            self.simple_types[simple_type.name] = simple_type
    
    def _parse_complex_types_from_file(self, file_path: str) -> None:
        """Parse complex types from a specific file."""
        if self.root is None:
            return
            
        xpath = './/xs:complexType[@name]'
        complex_type_elements = self.root.xpath(xpath, namespaces={'xs': 'http://www.w3.org/2001/XMLSchema'})
        
        for elem in complex_type_elements:
            complex_type = self._extract_complex_type(elem)
            # TODO: Add file source information tracking
            self.complex_types[complex_type.name] = complex_type
    
    def _parse_global_elements_from_file(self, file_path: str) -> None:
        """Parse global elements from a specific file."""
        if self.root is None:
            return
            
        xpath = './/xs:element[@name and not(parent::xs:sequence or parent::xs:choice or parent::xs:all)]'
        global_elements = self.root.xpath(xpath, namespaces={'xs': 'http://www.w3.org/2001/XMLSchema'})
        
        for elem in global_elements:
            element = self._extract_element(elem)
            # TODO: Add file source information tracking
            self.global_elements[element.name] = element
    
    def _calculate_cross_file_dependencies(self) -> None:
        """Calculate dependencies that cross file boundaries."""
        # This extends the base dependency calculation to include file references
        super()._calculate_dependencies()
        
        # Add file-level dependencies
        for file_path, dependent_files in self.file_dependencies.items():
            file_key = f"file:{Path(file_path).name}"
            self.dependencies[file_key] = set(f"file:{Path(dep).name}" for dep in dependent_files)
    
    def get_structure(self) -> Dict[str, Any]:
        """Get the complete parsed structure with multi-file information."""
        structure = super().get_structure()
        
        # Add multi-file specific information
        structure['multi_file_info'] = {
            'total_files': len(self.all_roots),
            'processed_files': [str(f) for f in self.processed_files],
            'schema_references': [
                {
                    'type': ref.reference_type,
                    'namespace': ref.namespace,
                    'schema_location': ref.schema_location,
                    'resolved_path': str(ref.resolved_path) if ref.resolved_path else None
                }
                for ref in self.schema_references
            ],
            'file_dependencies': self.file_dependencies,
            'imported_namespaces': self.imported_namespaces
        }
        
        return structure
    
    def get_file_summary(self) -> Dict[str, Any]:
        """Get a summary of all processed files."""
        summary = {}
        
        for file_path, root in self.all_roots.items():
            file_name = Path(file_path).name
            
            # Count components in this file
            simple_types = len(root.xpath('.//xs:simpleType[@name]', 
                                       namespaces={'xs': 'http://www.w3.org/2001/XMLSchema'}))
            complex_types = len(root.xpath('.//xs:complexType[@name]', 
                                        namespaces={'xs': 'http://www.w3.org/2001/XMLSchema'}))
            global_elements = len(root.xpath('.//xs:element[@name and not(parent::xs:sequence or parent::xs:choice or parent::xs:all)]', 
                                           namespaces={'xs': 'http://www.w3.org/2001/XMLSchema'}))
            
            summary[file_name] = {
                'path': file_path,
                'target_namespace': root.get('targetNamespace', None),
                'simple_types': simple_types,
                'complex_types': complex_types,
                'global_elements': global_elements,
                'dependencies': self.file_dependencies.get(file_path, [])
            }
        
        return summary
