# Developer Documentation - XSD Visualization Toolkit

## 📋 Table of Contents

- [Architecture Overview](#architecture-overview)
- [Core Libraries & Rationale](#core-libraries--rationale)
- [Module Structure](#module-structure)
- [Data Flow & Processing Pipeline](#data-flow--processing-pipeline)
- [Key Design Patterns](#key-design-patterns)
- [Performance Considerations](#performance-considerations)
- [Extension Points](#extension-points)
- [Testing Strategy](#testing-strategy)
- [Troubleshooting Development Issues](#troubleshooting-development-issues)

## 🏗️ Architecture Overview

The XSD Visualization Toolkit follows a **modular, pipeline-based architecture** designed for:
- **Extensibility**: Easy to add new parsers, generators, and output formats
- **Performance**: Efficient parsing and lazy loading for large schemas
- **Maintainability**: Clear separation of concerns between parsing, analysis, and output generation
- **Offline Operation**: Zero external dependencies for core functionality

### High-Level Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   XSD Files     │───▶│  Parser Layer    │───▶│ Analysis Layer  │
│                 │    │                  │    │                 │
│ • Single files  │    │ • XSDParser      │    │ • Structure     │
│ • Multi-file    │    │ • MultiFileXSD   │    │ • Dependencies  │
│ • Selective     │    │ • SelectiveXSD   │    │ • Relationships │
│ • Cross-schema  │    │ • RelationshipA  │    │ • Statistics    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                 │
                                 ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Output Layer    │◀───│  Generator Layer │◀───│  Data Models    │
│                 │    │                  │    │                 │
│ • HTML docs     │    │ • HTMLGenerator  │    │ • Elements      │
│ • Tree views    │    │ • TreeVisualizer │    │ • Types         │
│ • JSON export   │    │ • JSONExporter   │    │ • Namespaces    │
│ • Relationship  │    │ • RelationshipR  │    │ • File Links    │
│   reports       │    │   eporter        │    │ • Dependencies  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 📚 Core Libraries & Rationale

### XML Processing: `lxml`
**Why chosen over built-in `xml` module:**
- **Performance**: 5-10x faster parsing for large XSD files
- **XPath Support**: Advanced querying capabilities for complex schema navigation
- **Namespace Handling**: Robust namespace resolution and management
- **Memory Efficiency**: Lazy loading and streaming support for massive files
- **Error Recovery**: Better handling of malformed XML

```python
from lxml import etree
# XPath with namespace support
elements = tree.xpath('//xs:element[@name]', namespaces=ns_map)
```

### Template Engine: `Jinja2`
**Why chosen:**
- **Security**: Auto-escaping prevents XSS in generated HTML
- **Flexibility**: Template inheritance and macros for maintainable templates
- **Performance**: Compiled templates for faster rendering
- **Ecosystem**: Rich filter library and extensive documentation

```python
from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('templates'), autoescape=True)
```

### Terminal UI: `Rich`
**Why chosen over basic `print`:**
- **Professional Output**: Colors, tables, progress bars, and formatting
- **Cross-Platform**: Consistent appearance across operating systems
- **Performance**: Optimized rendering for large datasets
- **Interactive Elements**: Live displays and user input handling

```python
from rich.console import Console
from rich.table import Table
from rich.progress import track
```

### Tree Structures: `anytree`
**Why chosen:**
- **Intuitive API**: Natural tree building and traversal
- **Visualization**: Built-in ASCII tree rendering
- **Export Options**: Multiple output formats (DOT, JSON, etc.)
- **Memory Efficient**: Lightweight node structure

```python
from anytree import Node, RenderTree
from anytree.exporter import DotExporter
```

### Diagram Generation: `graphviz`
**Why chosen:**
- **Professional Quality**: Publication-ready diagrams
- **Layout Algorithms**: Automatic positioning and routing
- **Format Support**: SVG, PNG, PDF output options
- **Customization**: Extensive styling and layout controls

```python
from graphviz import Digraph
dot = Digraph(comment='XSD Structure')
dot.node('A', 'Element A')
dot.edge('A', 'B', label='contains')
```

## 🏗️ Module Structure

### Core Parsers (`utils/`)

#### `xsd_parser.py` - Base XSD Parser
**Purpose**: Foundation parser for single XSD files
**Key Components**:
- `XSDParser` class: Main parsing engine
- Namespace management and resolution
- Element and type extraction
- Dependency tracking

```python
class XSDParser:
    def __init__(self, xsd_file_path: str):
        self.xsd_file_path = xsd_file_path
        self.tree = None
        self.namespaces = {}
        self.elements = {}
        self.complex_types = {}
        self.simple_types = {}
```

#### `multifile_xsd_parser.py` - Multi-File Schema Parser
**Purpose**: Handle schemas with imports, includes, and redefines
**Key Features**:
- **Import Resolution**: Different namespace schema integration
- **Include Processing**: Same namespace component merging  
- **Redefine Handling**: Schema modification support
- **Circular Reference Detection**: Prevents infinite recursion

```python
class MultiFileXSDParser(XSDParser):
    def __init__(self, main_file: str):
        super().__init__(main_file)
        self.processed_files = set()
        self.file_dependencies = {}
        self.import_chain = []
```

#### `selective_xsd_parser.py` - Selective Component Parser
**Purpose**: Cherry-pick specific components from multiple files
**Architecture**:
- `SelectionCriteria`: Dataclass for selection parameters
- `SelectedComponent`: Tracking structure for chosen elements
- Dependency resolution for selected components

```python
@dataclass
class SelectionCriteria:
    elements: List[str] = field(default_factory=list)
    complex_types: List[str] = field(default_factory=list)
    simple_types: List[str] = field(default_factory=list)
    namespaces: List[str] = field(default_factory=list)
    include_dependencies: bool = True
```

#### `relationship_analyzer.py` - Multi-File Relationship Analyzer (NEW! 🔗)
**Purpose**: Analyze and explain relationships between multiple XSD files
**Key Features**:
- **File Relationship Mapping**: Detect imports, includes, and redefines between files
- **Component Dependency Analysis**: Track type dependencies across schema boundaries  
- **Namespace Cross-Reference**: Map namespace usage and definitions across files
- **Relationship Reporting**: Generate comprehensive JSON and text reports

**Core Data Structures**:
```python
@dataclass
class FileRelationship:
    source_file: str
    target_file: str
    relationship_type: str  # 'import', 'include', 'redefine'
    namespace: Optional[str] = None
    schema_location: Optional[str] = None

@dataclass  
class ComponentDependency:
    source_component: str
    target_component: str
    source_file: str
    target_file: str
    dependency_type: str  # 'type_reference', 'element_reference', 'group_reference'
    namespace: Optional[str] = None
```

**Analysis Capabilities**:
```python
class RelationshipAnalyzer:
    def analyze_file_relationships(self) -> List[FileRelationship]:
        """Detect import/include/redefine relationships between files"""
        
    def analyze_component_dependencies(self) -> List[ComponentDependency]:
        """Track type and element dependencies across files"""
        
    def analyze_namespace_usage(self) -> Dict[str, Dict[str, Any]]:
        """Map namespace definitions and usage across schema set"""
        
    def generate_relationship_report(self) -> Dict[str, Any]:
        """Create comprehensive relationship analysis report"""
```

### Output Generators (`utils/`)

#### `html_generator.py` - HTML Documentation Generator
**Purpose**: Create interactive, browsable documentation
**Features**:
- **Template-Based**: Jinja2 templates for customization
- **Cross-References**: Automatic linking between components
- **Search & Filter**: Client-side JavaScript functionality
- **Responsive Design**: Mobile-friendly layout

**Template Structure**:
```
templates/
├── index.html          # Main documentation page
├── element.html        # Element detail pages  
├── styles.css          # Visual styling
└── script.js          # Interactive features
```

#### `csv_schema_analyzer.py` - CSV Requirements Validator (NEW! 📊)
**Purpose**: Validate XSD files against CSV-defined business requirements with dynamic depth structure
**Key Features**:
- **Dynamic Path Structure**: 8-level depth columns (level1-level8) for flexible requirement definition
- **Multi-File XSD Support**: Validate against multiple related/unrelated XSD files
- **Complex Type Resolution**: Automatically resolve tns:ComplexType references to find nested elements
- **Attribute vs Element Analysis**: Distinguish between element paths and attribute paths using @attr syntax
- **Business-Friendly Interface**: CSV format accessible to non-technical stakeholders

**Core Data Structures**:
```python
@dataclass
class SchemaRequirement:
    id: str
    xpath: str
    description: str
    levels: List[str]  # Dynamic depth structure from level1-level8
    attribute: Optional[str] = None
    expected_type: Optional[str] = None
    required: bool = False
    validation_rules: Optional[str] = None
    business_purpose: Optional[str] = None

@dataclass
class AnalysisResult:
    requirement: SchemaRequirement
    status: str  # 'found', 'missing', 'mismatch', 'error'
    found_in_file: Optional[str] = None
    found_path: Optional[str] = None
    actual_type: Optional[str] = None
    actual_required: Optional[bool] = None
    issues: List[str] = field(default_factory=list)
```

**CSV Format Structure**:
```csv
id,xpath,description,level1,level2,level3,level4,level5,level6,level7,level8,attribute,expected_type,required,validation_rules,business_purpose
1,"bookstore/storeName","Store name",bookstore,storeName,,,,,,,xs:string,true,"maxLength: 100","Name of the bookstore"
2,"orders/items/@id","Deep attribute",orders,items,,,,,,,id,string,true,"pattern: ^[A-Z]{3}$","Item ID"
```

**Analysis Output Categories**:
- ✅ **FOUND**: Requirements perfectly matched in XSD with type validation
- ⚠️ **MISMATCH**: Element found but with type or requirement differences
- ❌ **MISSING**: Element not found in any XSD file with helpful suggestions

#### `tree_visualizer.py` - Tree Structure Visualizer (Enhanced for Multi-File)
**Purpose**: Generate hierarchical views of schema structure  
**Multi-File Capabilities** (NEW):
- **Multiple File Processing**: Accept and process multiple XSD files with `nargs='+'`
- **Combined Visualization**: Merge multiple schemas into single tree with `--combined` flag
- **Automatic File Numbering**: Generate separate outputs with `_1, _2` suffixes for multiple files
- **Cross-Schema Navigation**: Navigate relationships between different schema files

**Output Formats**:
- **Console**: Rich-formatted terminal display
- **Text**: Plain text for documentation  
- **DOT**: Graphviz input format
- **SVG**: Vector graphics for presentations

**Usage Examples**:
```bash
# Single file (traditional)
python tree_visualizer.py schema.xsd --format console

# Multiple files separately  
python tree_visualizer.py file1.xsd file2.xsd file3.xsd --format svg

# Combined multi-file visualization
python tree_visualizer.py *.xsd --combined --format svg --output combined_tree.svg
```

### Command-Line Interface Tools

#### `xsd_analyzer.py` - Main Analysis Tool (Enhanced for Multi-File)
**Purpose**: Comprehensive XSD schema analysis and documentation generation
**Multi-File Enhancements** (NEW):
- **Multiple File Input**: Process multiple XSD files with automatic file detection
- **Combined Analysis Mode**: Use `--combined` flag to merge multiple schemas  
- **Cross-File Dependency Tracking**: Detect and report dependencies across files
- **Unified Output Generation**: Create combined documentation from multiple sources

**Core Features**:
```python
# Single file analysis (traditional)
python xsd_analyzer.py schema.xsd --formats html json

# Multi-file analysis with separate outputs
python xsd_analyzer.py file1.xsd file2.xsd file3.xsd --formats html

# Combined multi-file analysis  
python xsd_analyzer.py *.xsd --combined --formats html json --output-dir ./docs
```

#### `csv_schema_analyzer.py` - CSV Requirements Validator (NEW! 📊)
**Purpose**: Business-friendly validation of XSD files against CSV-defined requirements
**Technical Architecture**:
- **Dynamic CSV Parser**: Handles 1-8 level depth structure with flexible column mapping
- **Type Resolution Engine**: Automatically resolves complex type hierarchies to find nested elements  
- **Multi-File Schema Support**: Validates requirements against multiple related/unrelated XSD files
- **Rich Analysis Reporting**: Console, JSON, and text output with detailed mismatch analysis

**Core Technical Features**:
```python
# Basic validation workflow
python csv_schema_analyzer.py requirements.csv schema.xsd

# Multi-file validation with comprehensive reporting
python csv_schema_analyzer.py business_rules.csv file1.xsd file2.xsd file3.xsd --formats json text --output-dir ./validation

# Advanced usage with verbose logging for development
python csv_schema_analyzer.py requirements.csv *.xsd --verbose --formats console json
```

**Key Technical Implementation Details**:
- **Path Resolution Algorithm**: Implements recursive type resolution to navigate complex schema hierarchies
- **Attribute vs Element Detection**: Uses `@attribute` syntax parsing to distinguish between XML attributes and elements
- **Dynamic Column Processing**: Supports variable-depth paths using level1-level8 columns with automatic null handling
- **Type Comparison Engine**: Sophisticated type matching including namespace prefix handling (xs: vs tns:)
- **Error Recovery**: Graceful handling of malformed CSV rows and missing XSD components

#### `selective_analyzer.py` - Selective Component Analyzer (Enhanced for Multi-File)
**Purpose**: Cherry-pick specific components from one or more XSD files
**Multi-File Capabilities** (NEW):
- **Cross-File Selection**: Select components from different files in single operation
- **Namespace-Based Selection**: Select all components from specific namespaces across files
- **Dependency Resolution**: Automatically include dependencies from other files
- **Mixed Selection Strategies**: Combine element, type, and namespace selections

**Advanced Usage**:
```python
# Select elements from multiple files
python selective_analyzer.py file1.xsd --elements Book,Author file2.xsd --complex-types PersonType

# Namespace-based selection across files
python selective_analyzer.py *.xsd --namespaces "http://example.com/common,http://example.com/library"

# Python API for complex selections
from utils.selective_xsd_parser import SelectiveXSDParser
parser = SelectiveXSDParser()
parser.add_file_selection("schema1.xsd", elements=["Customer", "Order"])
parser.add_file_selection("schema2.xsd", namespaces=["http://example.com/types"])
result = parser.parse_selections()
```

#### `relationship_analyzer.py` - Multi-File Relationship Analyzer (NEW! 🔗)
**Purpose**: Analyze and explain relationships between multiple XSD files
**Core Functionality**:
- **File Relationship Detection**: Identify import, include, and redefine relationships
- **Component Dependency Mapping**: Track type and element dependencies across schemas
- **Namespace Analysis**: Map namespace definitions and usage patterns
- **Comprehensive Reporting**: Generate detailed JSON and text reports

**Analysis Output**:
```python
# Basic relationship analysis
python relationship_analyzer.py schema1.xsd schema2.xsd schema3.xsd

# Generate detailed reports
python relationship_analyzer.py tests/data/*.xsd --output-dir ./reports

# Console-only analysis
python relationship_analyzer.py *.xsd --report-only

# Analysis results include:
{
    "file_relationships": [...],    # Import/include/redefine mappings  
    "component_dependencies": [...], # Cross-file type dependencies
    "namespace_analysis": {...},    # Namespace usage patterns
    "summary": {...}                # High-level statistics
}
```

#### `element_inspector.py` - Interactive Element Inspector
**Purpose**: Command-line tool for exploring schema components
**Capabilities**:
- Element and type detailed inspection
- Search functionality across schema
- Statistics and complexity analysis
- Interactive navigation

## 🔄 Data Flow & Processing Pipeline

### 1. **Parsing Phase**
```python
# File Input → XML Tree → Namespace Resolution
tree = etree.parse(xsd_file)
namespaces = self._extract_namespaces(tree)
root = tree.getroot()
```

### 2. **Component Extraction**
```python
# Extract different component types
elements = self._extract_elements(root, namespaces)
complex_types = self._extract_complex_types(root, namespaces)
simple_types = self._extract_simple_types(root, namespaces)
```

### 3. **Dependency Resolution**
```python
# Build dependency graph
dependencies = self._build_dependency_graph(elements, types)
resolved_order = self._topological_sort(dependencies)
```

### 4. **Data Structure Assembly**
```python
# Create unified data structure
structure = {
    'elements': elements,
    'complex_types': complex_types,
    'simple_types': simple_types,
    'dependencies': dependencies,
    'statistics': self._calculate_statistics()
}
```

### 5. **Output Generation**
```python
# Generate multiple output formats
html_generator.generate_documentation(structure, output_dir)
tree_visualizer.generate_tree(structure, format='svg')
json_exporter.export_structure(structure, 'schema.json')
```

## 🎯 Key Design Patterns

### 1. **Strategy Pattern** - Multiple Parsers
Different parsing strategies for different use cases:
```python
# Single file strategy
parser = XSDParser('schema.xsd')

# Multi-file strategy  
parser = MultiFileXSDParser('main.xsd')

# Selective strategy
parser = SelectiveXSDParser()
parser.add_file_selection('file1.xsd', elements=['Book'])

# Relationship analysis strategy (NEW)
analyzer = RelationshipAnalyzer(['schema1.xsd', 'schema2.xsd', 'schema3.xsd'])
relationships = analyzer.analyze_all_relationships()
```

### 2. **Factory Pattern** - Output Generation
Unified interface for different output formats:
```python
def create_generator(format_type: str, structure: dict):
    generators = {
        'html': HTMLGenerator,
        'json': JSONExporter,
        'tree': TreeVisualizer,
        'relationship': RelationshipReporter  # NEW
    }
    return generators[format_type](structure)

# Multi-file aware factory
def create_multi_file_analyzer(files: List[str], analysis_type: str):
    analyzers = {
        'comprehensive': MultiFileXSDParser,
        'selective': SelectiveXSDParser, 
        'relationship': RelationshipAnalyzer  # NEW
    }
    return analyzers[analysis_type](files)
```

### 3. **Observer Pattern** - Progress Tracking
Progress reporting during long operations:
```python
class ProgressTracker:
    def __init__(self):
        self.observers = []
    
    def notify_progress(self, completed: int, total: int):
        for observer in self.observers:
            observer.update_progress(completed, total)
```

### 4. **Template Method Pattern** - Parser Base Class
Consistent parsing workflow with customizable steps:
```python
class BaseParser:
    def parse(self):
        self._load_file()
        self._extract_namespaces()
        self._parse_components()  # Override in subclasses
        self._resolve_dependencies()
        return self._build_structure()
```

## ⚡ Performance Considerations

### Memory Management
- **Lazy Loading**: Parse components on-demand for large schemas
- **Streaming**: Process large files without loading entirely into memory
- **Caching**: Cache parsed components to avoid reprocessing

```python
class LazyElementLoader:
    def __init__(self, tree, namespaces):
        self.tree = tree
        self.namespaces = namespaces
        self._cache = {}
    
    def get_element(self, name: str):
        if name not in self._cache:
            self._cache[name] = self._parse_element(name)
        return self._cache[name]
```

### Processing Optimization
- **XPath Queries**: Use efficient XPath expressions instead of tree traversal
- **Batch Processing**: Group related operations to reduce overhead
- **Early Exit**: Stop processing when sufficient data is found

```python
# Efficient XPath vs manual traversal
# Good: Single XPath query
elements = tree.xpath('//xs:element[@name]', namespaces=ns)

# Avoid: Manual tree walking
# for node in tree.iter():
#     if node.tag.endswith('element') and 'name' in node.attrib:
```

### Output Generation Optimization
- **Template Compilation**: Pre-compile Jinja2 templates
- **Incremental Generation**: Generate only changed components
- **Parallel Processing**: Use threading for independent operations

## 🔌 Extension Points

### Adding New Parsers
```python
class CustomXSDParser(XSDParser):
    def _parse_components(self):
        # Custom parsing logic for specific XSD variants
        pass
    
    def _extract_custom_annotations(self):
        # Extract vendor-specific annotations
        pass
```

### Custom Output Formats
```python
class PDFGenerator:
    def __init__(self, structure: dict):
        self.structure = structure
    
    def generate(self, output_path: str):
        # Implement PDF generation logic
        pass
```

### Custom Requirement Validators
**Extending CSV Schema Analyzer**:
```python
class CustomRequirementValidator:
    def __init__(self, requirement_source: str):
        self.requirement_source = requirement_source
    
    def load_requirements(self) -> List[SchemaRequirement]:
        # Load from Excel, JSON, database, etc.
        pass
    
    def validate_custom_rules(self, element_data: Dict) -> List[str]:
        # Implement business-specific validation logic
        pass
```

**Adding New Analysis Categories**:
```python
# Extend AnalysisResult status types
ANALYSIS_STATUSES = ['found', 'missing', 'mismatch', 'error', 'deprecated', 'custom_warning']

class ExtendedAnalysisResult(AnalysisResult):
    compliance_score: float = 0.0
    business_impact: str = 'low'
    remediation_suggestions: List[str] = field(default_factory=list)
```

### Template Customization
```html
<!-- templates/custom_element.html -->
{% extends "base.html" %}
{% block content %}
    <!-- Custom element rendering -->
{% endblock %}
```

### Plugin Architecture
```python
class PluginManager:
    def __init__(self):
        self.plugins = {}
    
    def register_plugin(self, name: str, plugin_class):
        self.plugins[name] = plugin_class
    
    def execute_plugin(self, name: str, data):
        return self.plugins[name](data).execute()
```

## 🧪 Testing Strategy

### Unit Tests Structure
```
tests/
├── test_xsd_parser.py           # Core parser functionality
├── tests/data_parser.py     # Multi-file parsing (Enhanced)
├── test_selective_parser.py     # Selective parsing (Enhanced)
├── test_relationship_analyzer.py # Multi-file relationship analysis (NEW)
├── test_html_generator.py       # HTML output generation
├── test_tree_visualizer.py      # Tree visualization (Enhanced for multi-file)
├── test_cli_integration.py      # Command-line interface tests (NEW)
├── fixtures/                    # Test XSD files
│   ├── simple_schema.xsd
│   ├── complex_schema.xsd
│   ├── multi_file/              # Multi-file test schemas (Enhanced)
│   │   ├── main.xsd             # Schema with imports/includes
│   │   ├── imported.xsd         # Imported schema
│   │   ├── included.xsd         # Included schema
│   │   └── circular/            # Circular reference test cases
│   └── relationship_test_set/   # Relationship analysis test data (NEW)
│       ├── schema_a.xsd
│       ├── schema_b.xsd
│       └── schema_c.xsd
└── integration/                 # End-to-end tests
    ├── test_full_pipeline.py
    ├── test_multi_file_workflow.py    # Multi-file integration tests (NEW)
    └── test_relationship_workflow.py  # Relationship analysis workflow (NEW)
```

### Test Data Management
```python
class XSDTestFixtures:
    @classmethod
    def simple_bookstore(cls):
        return """<?xml version="1.0"?>
        <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
            <xs:element name="bookstore">
                <xs:complexType>
                    <xs:sequence>
                        <xs:element name="book" maxOccurs="unbounded">
                            <!-- Book definition -->
                        </xs:element>
                    </xs:sequence>
                </xs:complexType>
            </xs:element>
        </xs:schema>"""
```

### Performance Testing
```python
import pytest
import time
from utils.xsd_parser import XSDParser

def test_large_schema_performance():
    start_time = time.time()
    parser = XSDParser('large_schema.xsd')
    structure = parser.parse()
    end_time = time.time()
    
    # Assert parsing completes within reasonable time
    assert end_time - start_time < 30.0  # 30 seconds max
    assert len(structure['elements']) > 100
```

### Multi-File Relationship Testing (NEW)
```python
import pytest
from utils.relationship_analyzer import RelationshipAnalyzer

def test_file_relationship_detection():
    """Test detection of import/include relationships between files"""
    analyzer = RelationshipAnalyzer([
        'fixtures/multi_file/main.xsd',
        'fixtures/multi_file/imported.xsd', 
        'fixtures/multi_file/included.xsd'
    ])
    
    relationships = analyzer.analyze_file_relationships()
    
    # Verify import relationship detected
    import_rels = [r for r in relationships if r.relationship_type == 'import']
    assert len(import_rels) > 0
    assert any(r.target_file.endswith('imported.xsd') for r in import_rels)
    
    # Verify include relationship detected  
    include_rels = [r for r in relationships if r.relationship_type == 'include']
    assert len(include_rels) > 0
    assert any(r.target_file.endswith('included.xsd') for r in include_rels)

def test_component_dependency_analysis():
    """Test cross-file component dependency detection"""
    analyzer = RelationshipAnalyzer([
        'fixtures/relationship_test_set/schema_a.xsd',
        'fixtures/relationship_test_set/schema_b.xsd'
    ])
    
    dependencies = analyzer.analyze_component_dependencies()
    
    # Verify cross-file type dependencies detected
    cross_file_deps = [d for d in dependencies if d.source_file != d.target_file]
    assert len(cross_file_deps) > 0
    
    # Verify dependency types are properly classified
    type_refs = [d for d in dependencies if d.dependency_type == 'type_reference']
    element_refs = [d for d in dependencies if d.dependency_type == 'element_reference']
    assert len(type_refs) + len(element_refs) > 0

def test_namespace_cross_reference():
    """Test namespace usage analysis across multiple files"""
    analyzer = RelationshipAnalyzer([
        'fixtures/multi_file/main.xsd',
        'fixtures/multi_file/imported.xsd'
    ])
    
    namespace_analysis = analyzer.analyze_namespace_usage()
    
    # Verify namespace mapping detected
    assert len(namespace_analysis) > 1  # Multiple namespaces
    
    # Check for target namespace definitions
    for ns_uri, ns_data in namespace_analysis.items():
        assert 'defined_in_files' in ns_data
        assert 'used_in_files' in ns_data
        assert 'components' in ns_data

def test_relationship_report_generation():
    """Test comprehensive relationship report generation"""
    analyzer = RelationshipAnalyzer(['fixtures/multi_file/*.xsd'])
    
    report = analyzer.generate_relationship_report()
    
    # Verify report structure
    assert 'file_relationships' in report
    assert 'component_dependencies' in report  
    assert 'namespace_analysis' in report
    assert 'summary' in report
    
    # Verify summary statistics
    summary = report['summary']
    assert 'total_files' in summary
    assert 'total_relationships' in summary
    assert 'total_namespaces' in summary
```

## 🔧 Troubleshooting Development Issues

### Common Development Problems

#### 1. **Namespace Resolution Issues**
```python
# Problem: Elements not found due to namespace mismatch
# Solution: Always include namespace mapping
namespaces = {
    'xs': 'http://www.w3.org/2001/XMLSchema',
    'tns': target_namespace
}
elements = tree.xpath('//xs:element[@name]', namespaces=namespaces)
```

#### 2. **Memory Issues with Large Files**
```python
# Problem: OutOfMemoryError with large XSD files
# Solution: Use iterative parsing
def parse_large_file(file_path):
    context = etree.iterparse(file_path, events=('start', 'end'))
    for event, elem in context:
        if event == 'end' and elem.tag.endswith('element'):
            # Process element
            process_element(elem)
            elem.clear()  # Free memory
```

#### 3. **Circular Reference Detection**
```python
class CircularReferenceDetector:
    def __init__(self):
        self.visiting = set()
        self.visited = set()
    
    def has_cycle(self, node, dependencies):
        if node in self.visiting:
            return True  # Cycle detected
        if node in self.visited:
            return False
        
        self.visiting.add(node)
        for dep in dependencies.get(node, []):
            if self.has_cycle(dep, dependencies):
                return True
        self.visiting.remove(node)
        self.visited.add(node)
        return False
```

#### 4. **Template Rendering Issues**
```python
# Problem: Template not found or rendering errors
# Solution: Verify template paths and context
import os
from jinja2 import Environment, FileSystemLoader

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
if not os.path.exists(template_dir):
    raise FileNotFoundError(f"Template directory not found: {template_dir}")

env = Environment(
    loader=FileSystemLoader(template_dir),
    autoescape=True,
    trim_blocks=True,
    lstrip_blocks=True
)
```

#### 5. **Multi-File Import/Include Resolution Issues** (NEW)
```python
# Problem: Import/include files not found or incorrectly resolved
# Solution: Implement robust path resolution with fallback strategies

class FileResolver:
    def __init__(self, base_path: str):
        self.base_path = Path(base_path).parent
        self.search_paths = [
            self.base_path,                    # Same directory as main file
            self.base_path / 'schemas',        # schemas subdirectory  
            self.base_path / 'includes',       # includes subdirectory
            Path.cwd()                         # Current working directory
        ]
    
    def resolve_schema_location(self, schema_location: str) -> Optional[Path]:
        """Try multiple paths to resolve schema location"""
        for search_path in self.search_paths:
            candidate = search_path / schema_location
            if candidate.exists():
                return candidate
        
        # Log warning for debugging
        logger.warning(f"Could not resolve schema location: {schema_location}")
        return None

# Usage in parser
resolver = FileResolver(main_xsd_file)
resolved_path = resolver.resolve_schema_location(import_location)
if resolved_path:
    import_parser = XSDParser(str(resolved_path))
```

#### 6. **Circular Import Detection in Multi-File Schemas** (NEW)
```python
# Problem: Infinite recursion when schemas have circular imports
# Solution: Track import chain to detect cycles

class ImportChainTracker:
    def __init__(self):
        self.current_chain = []
        self.all_chains = set()
    
    def enter_file(self, file_path: str) -> bool:
        """Returns False if circular import detected"""
        abs_path = str(Path(file_path).resolve())
        
        if abs_path in self.current_chain:
            chain_str = " -> ".join(self.current_chain + [abs_path])
            raise CircularImportError(f"Circular import detected: {chain_str}")
        
        self.current_chain.append(abs_path)
        return True
    
    def exit_file(self, file_path: str):
        abs_path = str(Path(file_path).resolve())
        if abs_path in self.current_chain:
            self.current_chain.remove(abs_path)

# Usage in multi-file parser
tracker = ImportChainTracker()
try:
    tracker.enter_file(import_file)
    # Process imported file
finally:
    tracker.exit_file(import_file)
```

#### 7. **Namespace Collision Resolution** (NEW)
```python
# Problem: Multiple files define the same namespace with conflicting components
# Solution: Implement namespace collision detection and resolution

class NamespaceCollisionDetector:
    def __init__(self):
        self.namespace_definitions = {}  # namespace -> {file: components}
    
    def register_namespace_definition(self, namespace: str, file_path: str, components: List[str]):
        if namespace not in self.namespace_definitions:
            self.namespace_definitions[namespace] = {}
        
        # Check for component collisions
        for other_file, other_components in self.namespace_definitions[namespace].items():
            if other_file != file_path:
                collisions = set(components) & set(other_components)
                if collisions:
                    logger.warning(f"Namespace collision in {namespace}: {collisions} "
                                 f"defined in both {file_path} and {other_file}")
        
        self.namespace_definitions[namespace][file_path] = components

# Usage
detector = NamespaceCollisionDetector()
for file_path, parsed_data in file_data.items():
    for namespace, components in parsed_data['namespaces'].items():
        detector.register_namespace_definition(namespace, file_path, components)
```

### Debugging Tools

#### 1. **Parser Debug Mode**
```python
parser = XSDParser('schema.xsd', debug=True)
parser.set_log_level('DEBUG')
structure = parser.parse()
```

#### 2. **Memory Profiling**
```python
import tracemalloc

tracemalloc.start()
# Run parsing operation
current, peak = tracemalloc.get_traced_memory()
print(f"Current memory usage: {current / 1024 / 1024:.1f} MB")
print(f"Peak memory usage: {peak / 1024 / 1024:.1f} MB")
tracemalloc.stop()
```

#### 3. **Performance Profiling**
```python
import cProfile
import pstats

def profile_parsing():
    profiler = cProfile.Profile()
    profiler.enable()
    
    parser = XSDParser('large_schema.xsd')
    structure = parser.parse()
    
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(10)  # Top 10 functions
```

## 🚀 Enhancement Status & Future Ideas

### ✅ Recently Implemented (NEW!)
1. **Multi-File Schema Support**: ✅ Handle imports, includes, and redefines across multiple XSD files
2. **Selective Component Analysis**: ✅ Cherry-pick specific components from multiple files  
3. **Cross-Schema Relationship Analysis**: ✅ Analyze and visualize relationships between XSD files
4. **Enhanced Command-Line Tools**: ✅ All main tools now support multiple file inputs
5. **Comprehensive Dependency Tracking**: ✅ Track dependencies across file boundaries
6. **Advanced Namespace Management**: ✅ Handle complex namespace scenarios across files

### 🎯 Planned Features
1. **Web Interface**: Browser-based schema explorer with multi-file navigation
2. **REST API**: HTTP API for remote schema analysis and relationship queries
3. **Database Integration**: Store and query schema metadata with relationship indexing
4. **Version Comparison**: Diff schemas across versions with relationship change tracking
5. **Schema Validation**: Validate instances against multi-file schema sets
6. **Code Generation**: Generate classes from XSD definitions with cross-file imports
7. **Interactive Relationship Explorer**: Visual graph-based relationship navigation
8. **Schema Optimization Suggestions**: Recommend improvements based on relationship analysis

### 🏗️ Architecture Improvements
1. **Async Processing**: Non-blocking operations for large multi-file schema sets
2. **Distributed Processing**: Process complex schema hierarchies across multiple machines
3. **Enhanced Plugin System**: Third-party extensions for custom relationship analysis
4. **Advanced Configuration Management**: YAML/JSON configuration for multi-file processing rules
5. **Intelligent Caching Layer**: Redis/Memcached for parsed schemas with relationship caching
6. **Performance Optimization**: Parallel processing for independent schema files
7. **Memory Management**: Streaming support for massive multi-file schema sets

---

## 📞 Developer Support

For technical questions, bug reports, or contribution discussions:

1. **Code Review**: Follow existing patterns and add comprehensive tests
2. **Documentation**: Update both user README and this developer guide
3. **Performance**: Profile changes with large XSD files
4. **Compatibility**: Test across Python 3.8+ and all supported platforms

Happy coding! 🎉
