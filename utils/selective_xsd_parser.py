"""
Selective XSD Analysis - Extract and analyze specific elements from multiple XSD files.
Allows cherry-picking elements, types, or entire namespaces from different schemas.
"""

import os
import logging
from typing import Dict, List, Any, Optional, Set, Union
from pathlib import Path
from dataclasses import dataclass
from lxml import etree
from lxml.etree import _Element

from .multi_file_xsd_parser import MultiFileXSDParser
from .xsd_parser import XSDElement, XSDComplexType, XSDSimpleType

logger = logging.getLogger(__name__)

@dataclass
class SelectionCriteria:
    """Criteria for selecting specific components from XSD files."""
    file_path: str
    elements: Optional[List[str]] = None  # Specific element names
    complex_types: Optional[List[str]] = None  # Specific complex type names
    simple_types: Optional[List[str]] = None  # Specific simple type names
    namespaces: Optional[List[str]] = None  # Include all from these namespaces
    include_dependencies: bool = True  # Auto-include dependent types

@dataclass
class SelectedComponent:
    """A component selected from a specific file."""
    name: str
    component_type: str  # 'element', 'complex_type', 'simple_type'
    source_file: str
    namespace: Optional[str]
    component_data: Union[XSDElement, XSDComplexType, XSDSimpleType]
    dependencies: Set[str]

class SelectiveXSDParser:
    """
    Parser that can extract and analyze specific components from multiple XSD files.
    """
    
    def __init__(self, base_dir: Optional[str] = None):
        """
        Initialize selective parser.
        
        Args:
            base_dir: Base directory for resolving relative paths
        """
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
        self.selection_criteria: List[SelectionCriteria] = []
        self.selected_components: Dict[str, SelectedComponent] = {}
        self.parsers: Dict[str, MultiFileXSDParser] = {}  # file_path -> parser
        self.dependency_map: Dict[str, Set[str]] = {}
        
    def add_selection(self, criteria: SelectionCriteria) -> None:
        """Add selection criteria for a specific file."""
        self.selection_criteria.append(criteria)
        logger.info(f"Added selection criteria for {criteria.file_path}")
        
    def add_file_selection(self, 
                          file_path: str, 
                          elements: Optional[List[str]] = None,
                          complex_types: Optional[List[str]] = None,
                          simple_types: Optional[List[str]] = None,
                          namespaces: Optional[List[str]] = None,
                          include_dependencies: bool = True) -> None:
        """
        Convenience method to add selection criteria.
        
        Args:
            file_path: Path to XSD file
            elements: List of element names to include
            complex_types: List of complex type names to include
            simple_types: List of simple type names to include
            namespaces: List of namespaces to include (all components)
            include_dependencies: Whether to auto-include dependent types
        """
        criteria = SelectionCriteria(
            file_path=file_path,
            elements=elements,
            complex_types=complex_types,
            simple_types=simple_types,
            namespaces=namespaces,
            include_dependencies=include_dependencies
        )
        self.add_selection(criteria)
    
    def parse_selections(self) -> Dict[str, Any]:
        """
        Parse all selected components from specified files.
        
        Returns:
            Combined structure containing only selected components
        """
        logger.info(f"Starting selective parsing of {len(self.selection_criteria)} selections...")
        
        # Parse each file and extract selected components
        for criteria in self.selection_criteria:
            self._parse_file_selection(criteria)
        
        # Resolve dependencies if requested
        self._resolve_dependencies()
        
        # Build combined structure
        structure = self._build_combined_structure()
        
        logger.info(f"Selective parsing complete. Selected {len(self.selected_components)} components.")
        return structure
    
    def _parse_file_selection(self, criteria: SelectionCriteria) -> None:
        """Parse and extract selected components from a single file."""
        file_path = str(self.base_dir / criteria.file_path)
        
        if not Path(file_path).exists():
            logger.error(f"File not found: {file_path}")
            return
        
        logger.info(f"Parsing selections from {file_path}")
        
        # Create parser for this file
        parser = MultiFileXSDParser(file_path)
        self.parsers[file_path] = parser
        
        # Parse the file
        structure = parser.parse()
        
        # Extract selected elements
        if criteria.elements:
            self._extract_selected_elements(parser, criteria, structure)
        
        # Extract selected complex types
        if criteria.complex_types:
            self._extract_selected_complex_types(parser, criteria, structure)
            
        # Extract selected simple types
        if criteria.simple_types:
            self._extract_selected_simple_types(parser, criteria, structure)
        
        # Extract by namespace
        if criteria.namespaces:
            self._extract_by_namespace(parser, criteria, structure)
    
    def _extract_selected_elements(self, parser: MultiFileXSDParser, 
                                 criteria: SelectionCriteria, 
                                 structure: Dict[str, Any]) -> None:
        """Extract specific elements from parsed structure."""
        if not criteria.elements:
            return
            
        for element_name in criteria.elements:
            if element_name in structure.get('global_elements', {}):
                element_data = structure['global_elements'][element_name]
                
                selected = SelectedComponent(
                    name=element_name,
                    component_type='element',
                    source_file=criteria.file_path,
                    namespace=parser.target_namespace,
                    component_data=element_data,
                    dependencies=self._find_element_dependencies(element_data)
                )
                
                self.selected_components[f"element:{element_name}"] = selected
                logger.debug(f"Selected element: {element_name} from {criteria.file_path}")
    
    def _extract_selected_complex_types(self, parser: MultiFileXSDParser,
                                      criteria: SelectionCriteria,
                                      structure: Dict[str, Any]) -> None:
        """Extract specific complex types from parsed structure."""
        if not criteria.complex_types:
            return
            
        for type_name in criteria.complex_types:
            if type_name in structure.get('complex_types', {}):
                type_data = structure['complex_types'][type_name]
                
                selected = SelectedComponent(
                    name=type_name,
                    component_type='complex_type',
                    source_file=criteria.file_path,
                    namespace=parser.target_namespace,
                    component_data=type_data,
                    dependencies=self._find_type_dependencies(type_data)
                )
                
                self.selected_components[f"complex_type:{type_name}"] = selected
                logger.debug(f"Selected complex type: {type_name} from {criteria.file_path}")
    
    def _extract_selected_simple_types(self, parser: MultiFileXSDParser,
                                     criteria: SelectionCriteria,
                                     structure: Dict[str, Any]) -> None:
        """Extract specific simple types from parsed structure."""
        if not criteria.simple_types:
            return
            
        for type_name in criteria.simple_types:
            if type_name in structure.get('simple_types', {}):
                type_data = structure['simple_types'][type_name]
                
                selected = SelectedComponent(
                    name=type_name,
                    component_type='simple_type',
                    source_file=criteria.file_path,
                    namespace=parser.target_namespace,
                    component_data=type_data,
                    dependencies=set()  # Simple types typically have fewer dependencies
                )
                
                self.selected_components[f"simple_type:{type_name}"] = selected
                logger.debug(f"Selected simple type: {type_name} from {criteria.file_path}")
    
    def _extract_by_namespace(self, parser: MultiFileXSDParser,
                            criteria: SelectionCriteria,
                            structure: Dict[str, Any]) -> None:
        """Extract all components from specific namespaces."""
        if not criteria.namespaces:
            return
            
        for namespace in criteria.namespaces:
            # Handle wildcard for "all namespaces"
            if namespace == "*" or namespace == parser.target_namespace:
                # Include all components from this file/namespace
                for name, element in structure.get('global_elements', {}).items():
                    key = f"element:{name}"
                    if key not in self.selected_components:
                        selected = SelectedComponent(
                            name=name,
                            component_type='element',
                            source_file=criteria.file_path,
                            namespace=parser.target_namespace,
                            component_data=element,
                            dependencies=self._find_element_dependencies(element)
                        )
                        self.selected_components[key] = selected
                
                for name, ctype in structure.get('complex_types', {}).items():
                    key = f"complex_type:{name}"
                    if key not in self.selected_components:
                        selected = SelectedComponent(
                            name=name,
                            component_type='complex_type',
                            source_file=criteria.file_path,
                            namespace=parser.target_namespace,
                            component_data=ctype,
                            dependencies=self._find_type_dependencies(ctype)
                        )
                        self.selected_components[key] = selected
                
                for name, stype in structure.get('simple_types', {}).items():
                    key = f"simple_type:{name}"
                    if key not in self.selected_components:
                        selected = SelectedComponent(
                            name=name,
                            component_type='simple_type',
                            source_file=criteria.file_path,
                            namespace=parser.target_namespace,
                            component_data=stype,
                            dependencies=set()
                        )
                        self.selected_components[key] = selected
    
    def _find_element_dependencies(self, element: XSDElement) -> Set[str]:
        """Find dependencies for an element."""
        dependencies = set()
        if hasattr(element, 'type') and element.type:
            dependencies.add(element.type)
        # Add more dependency detection logic as needed
        return dependencies
    
    def _find_type_dependencies(self, complex_type: XSDComplexType) -> Set[str]:
        """Find dependencies for a complex type."""
        dependencies = set()
        if hasattr(complex_type, 'base_type') and complex_type.base_type:
            dependencies.add(complex_type.base_type)
        # Add more dependency detection logic as needed
        return dependencies
    
    def _resolve_dependencies(self) -> None:
        """Automatically include dependent types if requested."""
        # This would recursively find and include dependent types
        # Implementation depends on how detailed we want dependency resolution
        pass
    
    def _build_combined_structure(self) -> Dict[str, Any]:
        """Build a combined structure from all selected components."""
        combined = {
            'metadata': {
                'total_files': len(set(comp.source_file for comp in self.selected_components.values())),
                'selection_type': 'selective',
                'selected_components': len(self.selected_components),
                'statistics': {
                    'total_elements': len([c for c in self.selected_components.values() if c.component_type == 'element']),
                    'total_complex_types': len([c for c in self.selected_components.values() if c.component_type == 'complex_type']),
                    'total_simple_types': len([c for c in self.selected_components.values() if c.component_type == 'simple_type']),
                    'max_depth': 1,  # Could be calculated properly if needed
                    'total_attributes': 0  # Could be calculated from selected components
                }
            },
            'elements': {},
            'global_elements': {},
            'complex_types': {},
            'simple_types': {},
            'source_files': list(set(comp.source_file for comp in self.selected_components.values())),
            'namespaces': list(set(comp.namespace for comp in self.selected_components.values() if comp.namespace)),
            'selection_summary': {},
            'dependencies': {}  # Add empty dependencies for HTML generator compatibility
        }
        
        # Group components by type 
        for key, component in self.selected_components.items():
            component_data = component.component_data  # type: ignore
            if component.component_type == 'element':
                # component_data is already a dict from the parser
                element_dict = {**component_data, 'source_file': component.source_file}  # type: ignore
                combined['global_elements'][component.name] = element_dict
                combined['elements'][component.name] = element_dict
            elif component.component_type == 'complex_type':
                # component_data is already a dict from the parser  
                type_dict = {**component_data, 'source_file': component.source_file}  # type: ignore
                combined['complex_types'][component.name] = type_dict
            elif component.component_type == 'simple_type':
                # component_data is already a dict from the parser
                type_dict = {**component_data, 'source_file': component.source_file}  # type: ignore
                combined['simple_types'][component.name] = type_dict
        
        # Add selection summary
        for file_path in combined['source_files']:
            file_components = [comp for comp in self.selected_components.values() 
                             if comp.source_file == file_path]
            combined['selection_summary'][file_path] = {
                'elements': len([c for c in file_components if c.component_type == 'element']),
                'complex_types': len([c for c in file_components if c.component_type == 'complex_type']),
                'simple_types': len([c for c in file_components if c.component_type == 'simple_type'])
            }
        
        return combined
    
    def get_selection_summary(self) -> Dict[str, Any]:
        """Get a summary of all selections made."""
        summary = {}
        
        for file_path in set(comp.source_file for comp in self.selected_components.values()):
            file_components = [comp for comp in self.selected_components.values() 
                             if comp.source_file == file_path]
            
            summary[file_path] = {
                'total_selected': len(file_components),
                'elements': [c.name for c in file_components if c.component_type == 'element'],
                'complex_types': [c.name for c in file_components if c.component_type == 'complex_type'],
                'simple_types': [c.name for c in file_components if c.component_type == 'simple_type'],
                'namespaces': list(set(c.namespace for c in file_components if c.namespace))
            }
        
        return summary
