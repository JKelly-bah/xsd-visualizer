"""
HTML documentation generator for XSD files.
Creates comprehensive, navigable documentation with cross-references.
"""

import os
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
import logging

logger = logging.getLogger(__name__)

class HTMLGenerator:
    """
    Generates comprehensive HTML documentation from parsed XSD structure.
    """
    
    def __init__(self, xsd_structure: Dict[str, Any], template_dir: Optional[str] = None):
        """
        Initialize HTML generator.
        
        Args:
            xsd_structure: Parsed XSD structure from XSDParser
            template_dir: Directory containing Jinja2 templates
        """
        self.structure = xsd_structure
        self.template_dir = template_dir or self._get_default_template_dir()
        
        # Initialize Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(self.template_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )
        
        # Add custom filters
        self.env.filters['format_occurs'] = self._format_occurs
        self.env.filters['get_type_link'] = self._get_type_link
        self.env.filters['format_documentation'] = self._format_documentation
        self.env.filters['basename'] = lambda path: Path(str(path)).name
    
    def _get_default_template_dir(self) -> str:
        """Get the default template directory."""
        current_dir = Path(__file__).parent.parent.parent  # Go up to project root
        return str(current_dir / "templates")
    
    def generate_documentation(self, output_dir: str) -> None:
        """
        Generate complete HTML documentation.
        
        Args:
            output_dir: Directory to write HTML files
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Generating HTML documentation in {output_dir}")
        
        # Generate main index page
        self._generate_index(output_path)
        
        # Generate element pages
        self._generate_element_pages(output_path)
        
        # Generate type pages
        self._generate_type_pages(output_path)
        
        # Generate dependency diagram
        self._generate_dependency_diagram(output_path)
        
        # Copy static assets
        self._copy_static_assets(output_path)
        
        logger.info("HTML documentation generation complete")
    
    def _generate_index(self, output_path: Path) -> None:
        """Generate the main index page."""
        template = self.env.get_template('index.html')
        
        content = template.render(
            metadata=self.structure['metadata'],
            elements=self.structure['elements'],
            global_elements=self.structure['global_elements'],
            complex_types=self.structure['complex_types'],
            simple_types=self.structure['simple_types'],
            statistics=self.structure['metadata']['statistics']
        )
        
        with open(output_path / 'index.html', 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _generate_element_pages(self, output_path: Path) -> None:
        """Generate individual pages for each element."""
        elements_dir = output_path / 'elements'
        elements_dir.mkdir(exist_ok=True)
        
        template = self.env.get_template('element.html')
        
        # Generate pages for root elements
        elements = self.structure['elements']
        if isinstance(elements, dict):
            # Handle selective parser format (dict)
            for element_name, element in elements.items():
                self._generate_element_page(template, element, elements_dir)
        else:
            # Handle regular parser format (list)
            for element in elements:
                self._generate_element_page(template, element, elements_dir)
        
        # Generate pages for global elements
        global_elements = self.structure.get('global_elements', {})
        if isinstance(global_elements, dict):
            for name, element in global_elements.items():
                if name not in (elements.keys() if isinstance(elements, dict) else [e.get('name', '') for e in elements]):
                    self._generate_element_page(template, element, elements_dir, is_global=True)
    
    def _generate_element_page(self, template, element: Dict[str, Any], 
                              output_dir: Path, is_global: bool = False) -> None:
        """Generate a single element page."""
        # Handle case where element might be a string (shouldn't happen but safety check)
        if isinstance(element, str):
            logger.warning(f"Element is string instead of dict: {element}")
            return
            
        element_name = element.get('name', 'unknown')
        filename = f"{element_name}.html"
        
        # Find dependencies and dependents
        dependencies = self._find_element_dependencies(element)
        dependents = self._find_element_dependents(element_name)
        
        content = template.render(
            element=element,
            dependencies=dependencies,
            dependents=dependents,
            is_global=is_global,
            metadata=self.structure['metadata']
        )
        
        with open(output_dir / filename, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _generate_type_pages(self, output_path: Path) -> None:
        """Generate pages for complex and simple types."""
        types_dir = output_path / 'types'
        types_dir.mkdir(exist_ok=True)
        
        # Complex types
        complex_template = self.env.get_template('complex_type.html')
        for name, complex_type in self.structure['complex_types'].items():
            content = complex_template.render(
                complex_type=complex_type,
                metadata=self.structure['metadata']
            )
            
            with open(types_dir / f"{name}.html", 'w', encoding='utf-8') as f:
                f.write(content)
        
        # Simple types
        simple_template = self.env.get_template('simple_type.html')
        for name, simple_type in self.structure['simple_types'].items():
            content = simple_template.render(
                simple_type=simple_type,
                metadata=self.structure['metadata']
            )
            
            with open(types_dir / f"{name}.html", 'w', encoding='utf-8') as f:
                f.write(content)
    
    def _generate_dependency_diagram(self, output_path: Path) -> None:
        """Generate dependency diagram page."""
        template = self.env.get_template('dependencies.html')
        
        # Convert dependencies to a format suitable for visualization
        dependencies_data = []
        for source, targets in self.structure['dependencies'].items():
            for target in targets:
                dependencies_data.append({
                    'source': source,
                    'target': target,
                    'type': self._get_dependency_type(source, target)
                })
        
        content = template.render(
            dependencies=dependencies_data,
            metadata=self.structure['metadata']
        )
        
        with open(output_path / 'dependencies.html', 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _copy_static_assets(self, output_path: Path) -> None:
        """Copy CSS, JS, and other static assets."""
        static_dir = output_path / 'static'
        static_dir.mkdir(exist_ok=True)
        
        # Generate CSS
        css_template = self.env.get_template('styles.css')
        css_content = css_template.render()
        
        with open(static_dir / 'styles.css', 'w', encoding='utf-8') as f:
            f.write(css_content)
        
        # Generate JavaScript
        js_template = self.env.get_template('script.js')
        js_content = js_template.render()
        
        with open(static_dir / 'script.js', 'w', encoding='utf-8') as f:
            f.write(js_content)
    
    def _find_element_dependencies(self, element: Dict[str, Any]) -> List[str]:
        """Find what this element depends on."""
        dependencies = []
        
        if element.get('type'):
            dependencies.append(element['type'])
        
        for child in element.get('children', []):
            if child.get('type'):
                dependencies.append(child['type'])
        
        return list(set(dependencies))
    
    def _find_element_dependents(self, element_name: str) -> List[str]:
        """Find what depends on this element."""
        dependents = []
        
        # Search through all elements and types
        def check_dependencies(item: Dict[str, Any]) -> None:
            if item.get('type') == element_name:
                dependents.append(item.get('name', 'unknown'))
            
            for child in item.get('children', []):
                check_dependencies(child)
        
        # Check root elements
        elements = self.structure['elements']
        if isinstance(elements, dict):
            for element in elements.values():
                check_dependencies(element)
        else:
            for element in elements:
                check_dependencies(element)
        
        # Check global elements
        for element in self.structure['global_elements'].values():
            check_dependencies(element)
        
        # Check complex types
        for complex_type in self.structure['complex_types'].values():
            for element in complex_type.get('elements', []):
                check_dependencies(element)
        
        return list(set(dependents))
    
    def _get_dependency_type(self, source: str, target: str) -> str:
        """Determine the type of dependency relationship."""
        # This is a simplified classification
        if target in self.structure['simple_types']:
            return 'simple_type'
        elif target in self.structure['complex_types']:
            return 'complex_type'
        else:
            return 'element'
    
    def _format_occurs(self, min_occurs: str, max_occurs: str) -> str:
        """Format occurrence constraints for display."""
        if min_occurs == "1" and max_occurs == "1":
            return "required"
        elif min_occurs == "0" and max_occurs == "1":
            return "optional"
        elif min_occurs == "0" and max_occurs == "unbounded":
            return "optional, multiple"
        elif min_occurs == "1" and max_occurs == "unbounded":
            return "required, multiple"
        else:
            return f"min: {min_occurs}, max: {max_occurs}"
    
    def _get_type_link(self, type_name: str) -> str:
        """Generate a link to a type page."""
        if not type_name:
            return ""
        
        # Remove namespace prefix for cleaner links
        clean_name = type_name.split(':')[-1]
        
        if type_name in self.structure['complex_types'] or type_name in self.structure['simple_types']:
            return f"types/{clean_name}.html"
        else:
            return f"elements/{clean_name}.html"
    
    def _format_documentation(self, doc: Optional[str]) -> str:
        """Format documentation text for HTML display."""
        if not doc:
            return ""
        
        # Basic text formatting
        formatted = doc.strip()
        formatted = formatted.replace('\n\n', '</p><p>')
        formatted = f"<p>{formatted}</p>"
        
        return formatted
