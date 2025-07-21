# XSD Visualization and Analysis Tools

A comprehensive offline toolkit for visualizing and analyzing large, complex XSD (XML Schema Definition) files. This workspace provides powerful tools for understanding schema structure, generating documentation, and creating visual representations without requiring any online services.

**🆕 Latest Updates:**
- **🏗️ MAJOR REORGANIZATION** - Clean modular `src/` structure for better maintainability
- **CSV Schema Analyzer** - Validate XSD files against CSV-defined business requirements with dynamic depth structure
- **Relationship Analyzer** - Analyze and explain relationships between multiple XSD files
- **Multi-File Schema Support** - Handle imports, includes, and redefines across multiple XSD files
- **Selective Analysis** - Cherry-pick specific elements, types, or namespaces from different files
- **Docker Containerization** - Complete Docker setup for easy deployment and usage

## 📁 Project Structure

This project is now organized with a clean, modular structure:
- **`src/`** - Core source code organized by function (analyzers, parsers, generators)
- **`docs/`** - All documentation consolidated in one place
- **`docker/`** - Docker containerization files and scripts
- **`tests/`** - Test data and scripts for validation
- **`demos/`** - Example scripts and sample data
- **`config/`** - Configuration files and dependencies

📖 **[See PROJECT_STRUCTURE.md for detailed layout](../PROJECT_STRUCTURE.md)**

## 🚀 Quick Commands

**Unix/macOS/Linux:**
```bash
# Analyze any XSD file
python xsd_analyzer.py your_schema.xsd --summary-only

# Validate XSD against business requirements (NEW!)
python csv_schema_analyzer.py requirements.csv schema.xsd --formats json

# Multi-file schemas with imports/includes  
python xsd_analyzer.py main_schema.xsd --multi-file --formats html

# Cherry-pick specific components (NEW!)
python demos/demo_selective.py

# Analyze relationships between files (NEW!)
python relationship_analyzer.py schema1.xsd schema2.xsd schema3.xsd

# Tree visualization
python tree_visualizer.py schema.xsd --format console

# Generate Java UML from XSD schemas (NEW!)
python java_uml_generator.py schema.xsd --formats plantuml mermaid java

# Interactive element inspection
python element_inspector.py schema.xsd
```

**Windows PowerShell:**
```powershell
# Analyze any XSD file
python xsd_analyzer.py your_schema.xsd --summary-only

# Validate XSD against business requirements (NEW!)
python csv_schema_analyzer.py requirements.csv schema.xsd --formats json

# Multi-file schemas with imports/includes  
python xsd_analyzer.py main_schema.xsd --multi-file --formats html

# Cherry-pick specific components (NEW!)
python demos/demo_selective.py

# Analyze relationships between files (NEW!)
python relationship_analyzer.py schema1.xsd schema2.xsd schema3.xsd

# Tree visualization
python tree_visualizer.py schema.xsd --format console

# Generate Java UML from XSD schemas (NEW!)
python java_uml_generator.py schema.xsd --formats plantuml mermaid java

# Interactive element inspection
python element_inspector.py schema.xsd
```

## ✅ Current Status

The toolkit is **fully functional** with all core features implemented:

- ✅ XSD Parser with full schema analysis
- ✅ **Selective Analysis** (NEW: cherry-pick components from multiple files)
- ✅ **Multi-File Schema Support** (NEW: imports, includes, redefines)
- ✅ **Java UML Generator** (NEW: convert XSD to Java UML diagrams and source code)
- ✅ HTML documentation generator with interactive features  
- ✅ Tree visualization (console, text, SVG formats)
- ✅ Element and type inspection tools
- ✅ VS Code integration with tasks and extensions
- ✅ Sample XSD files for testing (single and multi-file)
- ✅ Comprehensive error handling and logging

## 🚀 Quick Start

1. **Test with the included samples:**
   
   **Unix/macOS/Linux:**
   ```bash
   # Single file analysis
   python demos/demo.py
   python xsd_analyzer.py tests/data/test_bookstore.xsd --summary-only
   
   # Multi-file schema analysis (NEW!)
   python xsd_analyzer.py tests/data/library.xsd --multi-file --summary-only
   ```
   
   **Windows PowerShell:**
   ```powershell
   # Single file analysis
   python demos/demo.py
   python xsd_analyzer.py tests/data/test_bookstore.xsd --summary-only
   
   # Multi-file schema analysis (NEW!)
   python xsd_analyzer.py tests/data/library.xsd --multi-file --summary-only
   ```

2. **Generate HTML documentation:**
   
   **Unix/macOS/Linux:**
   ```bash
   # Single file
   python xsd_analyzer.py your_schema.xsd --formats html
   
   # Multi-file schema
   python xsd_analyzer.py main_schema.xsd --multi-file --formats html
   ```
   
   **Windows PowerShell:**
   ```powershell
   # Single file
   python xsd_analyzer.py your_schema.xsd --formats html
   
   # Multi-file schema
   python xsd_analyzer.py main_schema.xsd --multi-file --formats html
   ```

3. **View tree structure:**
   
   **Unix/macOS/Linux:**
   ```bash
   python tree_visualizer.py your_schema.xsd --format console
   ```
   
   **Windows PowerShell:**
   ```powershell
   python tree_visualizer.py your_schema.xsd --format console
   ```

## 🛠️ Features

### Core Analysis Tools

- **XSD Parser**: Extract structure and relationships from XSD files
- **Multi-File Parser** (NEW): Handle schemas with imports, includes, and redefines
- **Relationship Analyzer** (NEW): Analyze and explain relationships between multiple XSD files
- **Java UML Generator** (NEW): Convert XSD schemas to Java UML class diagrams (PlantUML, Mermaid) and Java source code
- **HTML Documentation Generator**: Create browsable documentation with hyperlinks
- **Tree Visualization**: Generate hierarchical views of schema structures
- **Element Inspector**: Interactive tool for examining specific elements and types
- **Dependency Analysis**: Map relationships between schema components
- **Multiple Output Formats**: HTML, SVG, text trees, JSON, and more

### Selective Analysis Features (NEW! 🎯)

- **Element Selection**: Choose specific elements from any XSD file
- **Type Selection**: Pick individual complex or simple types
- **Namespace Selection**: Select all components from specific namespaces  
- **Mixed Selection**: Combine different selection strategies
- **Cross-File Selection**: Cherry-pick from multiple different XSD files
- **Dependency Tracking**: Optionally include dependent types automatically
- **Focused Documentation**: Generate documentation for only selected components

### Multi-File Schema Features

- **Import Support**: Parse `xs:import` statements with different namespaces
- **Include Support**: Process `xs:include` statements for same-namespace components
- **Redefine Support**: Handle `xs:redefine` statements for schema modifications
- **Cross-File Dependencies**: Track relationships across schema files
- **Namespace Resolution**: Proper handling of multiple namespaces
- **File Summary Reports**: Overview of all processed files in the schema

### VS Code Integration

- **XML Language Support**: Syntax highlighting and validation for XSD files
- **Custom Tasks**: Quick access to common operations via Command Palette
- **Python Environment**: Pre-configured with all required packages
- **Simple Browser**: View generated HTML documentation within VS Code

### Output Formats

- **HTML**: Interactive documentation with navigation and search
- **SVG**: Scalable vector graphics for diagrams and presentations
- **Text**: Console-friendly tree structures and reports
- **JSON**: Machine-readable structure data for programmatic use

## 📁 Project Structure

```
XSD_Visualizations/
├── utils/
│   ├── xsd_parser.py              # Core XSD parsing functionality
│   ├── multi_file_xsd_parser.py   # Multi-file schema parser (NEW)
│   ├── selective_xsd_parser.py    # Selective component parser (NEW)
│   └── html_generator.py          # HTML documentation templates
├── templates/                     # Jinja2 templates for HTML output
│   ├── index.html                # Main documentation page
│   ├── element.html              # Element detail pages
│   ├── complex_type.html         # Complex type pages
│   ├── simple_type.html          # Simple type pages
│   ├── dependencies.html         # Dependency visualization
│   ├── styles.css               # CSS styling
│   └── script.js                # Interactive JavaScript
├── src/                          # Core source code (NEW STRUCTURE)
│   ├── analyzers/               # Analysis tools
│   │   ├── xsd_analyzer.py      # Main analysis engine
│   │   ├── tree_visualizer.py   # Tree visualization
│   │   ├── selective_analyzer.py # Selective analysis
│   │   ├── relationship_analyzer.py # Multi-file relationships
│   │   ├── csv_schema_analyzer.py # CSV validation
│   │   ├── java_uml_generator.py # Java UML generation (NEW)
│   │   └── element_inspector.py # Element inspection
│   ├── parsers/                 # XSD parsing utilities
│   │   ├── xsd_parser.py        # Core XSD parsing
│   │   ├── multi_file_xsd_parser.py # Multi-file handling
│   │   └── selective_xsd_parser.py # Selective parsing
│   └── generators/              # Output generation
│       └── html_generator.py    # HTML documentation generator
├── tests/                       # Test files and scripts
│   ├── data/                    # Test XSD files
│   │   ├── test_bookstore.xsd   # Sample bookstore schema
│   │   ├── library.xsd          # Library schema with imports
│   │   ├── common-types.xsd     # Common type definitions
│   │   └── publisher.xsd        # Publisher schema
│   └── scripts/                 # Test scripts
│       ├── tests/data_parser.py # Multi-file parser tests
│       └── debug_*.py           # Debug utilities
├── demos/                       # Demo scripts and samples
│   ├── demo.py                  # Basic usage examples
│   ├── demo_selective.py        # Selective analysis demo
│   ├── demo_requirements.csv    # Sample CSV requirements
│   └── sample_requirements.csv  # Additional CSV samples
├── docs/                        # Documentation
│   ├── README.md                # Main documentation
│   ├── DOCKER_README.md         # Docker setup guide
│   └── *.md                     # Additional documentation
├── docker/                      # Docker containerization
│   ├── Dockerfile               # Container definition
│   ├── docker-entrypoint.sh     # Container entry point
│   └── run-xsd-visualizer.*     # Convenience scripts
├── config/                      # Configuration files
│   ├── requirements.txt         # Python dependencies
│   └── xsd-visualizer.code-workspace # VS Code workspace
├── xsd_analyzer.py              # Main analysis wrapper (root convenience)
├── tree_visualizer.py           # Tree visualization wrapper
├── selective_analyzer.py        # Selective analysis wrapper
├── java_uml_generator.py        # Java UML generator wrapper (NEW)
└── PROJECT_STRUCTURE.md         # Detailed structure documentation
```

## 🎯 Usage Examples

### Basic Analysis

**Unix/macOS/Linux:**
```bash
# Quick summary
python xsd_analyzer.py schema.xsd --summary-only

# Complete analysis with all formats
python xsd_analyzer.py schema.xsd --formats html json text

# Generate only HTML documentation
python xsd_analyzer.py schema.xsd --formats html --output-dir ./docs
```

**Windows PowerShell:**
```powershell
# Quick summary
python xsd_analyzer.py schema.xsd --summary-only

# Complete analysis with all formats
python xsd_analyzer.py schema.xsd --formats html json text

# Generate only HTML documentation
python xsd_analyzer.py schema.xsd --formats html --output-dir ./docs
```

### Multi-File Schema Analysis

**Unix/macOS/Linux:**
```bash
# Analyze schema with imports/includes
python xsd_analyzer.py main_schema.xsd --multi-file --summary-only

# Generate HTML docs for multi-file schema
python xsd_analyzer.py main_schema.xsd --multi-file --formats html

# Complete multi-file analysis
python xsd_analyzer.py main_schema.xsd --multi-file --formats html json text --output-dir ./docs

# Test with included sample
python xsd_analyzer.py tests/data/library.xsd --multi-file --summary-only
```

**Windows PowerShell:**
```powershell
# Analyze schema with imports/includes
python xsd_analyzer.py main_schema.xsd --multi-file --summary-only

# Generate HTML docs for multi-file schema
python xsd_analyzer.py main_schema.xsd --multi-file --formats html

# Complete multi-file analysis
python xsd_analyzer.py main_schema.xsd --multi-file --formats html json text --output-dir ./docs

# Test with included sample
python xsd_analyzer.py tests/data/library.xsd --multi-file --summary-only
```

### Tree Visualization

**Unix/macOS/Linux:**
```bash
# Console tree display
python tree_visualizer.py schema.xsd --format console

# Generate SVG diagram
python tree_visualizer.py schema.xsd --format svg --output schema_tree.svg

# Focus on specific element
python tree_visualizer.py schema.xsd --element BookType --format console
```

**Windows PowerShell:**
```powershell
# Console tree display
python tree_visualizer.py schema.xsd --format console

# Generate SVG diagram
python tree_visualizer.py schema.xsd --format svg --output schema_tree.svg

# Focus on specific element
python tree_visualizer.py schema.xsd --element BookType --format console
```

### Java UML Generation (NEW! ☕)

Generate Java UML class diagrams and source code from XSD schemas:

**Unix/macOS/Linux:**
```bash
# Generate PlantUML, Mermaid, and Java code
python java_uml_generator.py schema.xsd --formats plantuml mermaid java

# Multiple XSD files with combined output
python java_uml_generator.py schema1.xsd schema2.xsd --combined

# Specific output directory and Java package
python java_uml_generator.py schema.xsd --output-dir ./generated --java-package com.example.model

# Generate only PlantUML diagrams
python java_uml_generator.py schema.xsd --formats plantuml --output-dir ./diagrams
```

**Windows PowerShell:**
```powershell
# Generate PlantUML, Mermaid, and Java code
python java_uml_generator.py schema.xsd --formats plantuml mermaid java

# Multiple XSD files with combined output
python java_uml_generator.py schema1.xsd schema2.xsd --combined

# Specific output directory and Java package
python java_uml_generator.py schema.xsd --output-dir ./generated --java-package com.example.model

# Generate only PlantUML diagrams
python java_uml_generator.py schema.xsd --formats plantuml --output-dir ./diagrams
```

### Element Inspection

**Unix/macOS/Linux:**
```bash
# Inspect specific element
python element_inspector.py schema.xsd --element bookstore

# Interactive mode
python element_inspector.py schema.xsd

# Search for elements
python element_inspector.py schema.xsd --search "book"
```

**Windows PowerShell:**
```powershell
# Inspect specific element
python element_inspector.py schema.xsd --element bookstore

# Interactive mode
python element_inspector.py schema.xsd

# Search for elements
python element_inspector.py schema.xsd --search "book"
```

### Relationship Analysis (NEW! 🔗)

**Unix/macOS/Linux:**
```bash
# Analyze relationships between multiple XSD files
python relationship_analyzer.py schema1.xsd schema2.xsd schema3.xsd

# Generate JSON and text reports
python relationship_analyzer.py *.xsd --output-dir ./reports

# Quick analysis with reports only
python relationship_analyzer.py schemas/*.xsd --report-only
```

**Windows PowerShell:**
```powershell
# Analyze relationships between multiple XSD files
python relationship_analyzer.py schema1.xsd schema2.xsd schema3.xsd

# Generate JSON and text reports
python relationship_analyzer.py *.xsd --output-dir ./reports

# Quick analysis with reports only
python relationship_analyzer.py schemas/*.xsd --report-only
```

### Selective Analysis (NEW! 🎯)

**Unix/macOS/Linux:**
```bash
# Cherry-pick specific components from multiple files
python demos/demo_selective.py
```

**Windows PowerShell:**
```powershell
# Cherry-pick specific components from multiple files
python demos/demo_selective.py
```

**Python API for custom selections:**
```python
from utils.selective_xsd_parser import SelectiveXSDParser

parser = SelectiveXSDParser()
parser.add_file_selection(
    file_path="schema1.xsd", 
    elements=["Customer", "Order"]
)
parser.add_file_selection(
    file_path="schema2.xsd",
    complex_types=["AddressType"],
    namespaces=["http://example.com/common"]
)
result = parser.parse_selections()
```

### VS Code Tasks

Use `Ctrl+Shift+P` → "Tasks: Run Task" to access:
- **Analyze XSD File** - Complete analysis with all formats
- **Generate HTML Documentation** - HTML docs only  
- **Visualize Tree (Console)** - Console tree display
- **Quick Summary** - Statistics overview
- **Analyze Relationships** - Multi-file relationship analysis (NEW!)

## 📋 Command Line Reference

### Main Analysis Tool - `xsd_analyzer.py`

**Unix/macOS/Linux:**
```bash
# Basic usage
python xsd_analyzer.py schema.xsd [options]

# Options:
--output-dir, -o DIR     Output directory (default: ./output)
--formats, -f FORMAT     Output formats: html, json, text, summary 
--summary-only, -s       Only show summary, no file output
--multi-file, -m         Enable multi-file parsing (imports/includes)
--verbose, -v           Enable verbose logging

# Examples:
python xsd_analyzer.py schema.xsd
python xsd_analyzer.py schema.xsd --output-dir ./docs
python xsd_analyzer.py schema.xsd --formats html json
python xsd_analyzer.py schema.xsd --multi-file --summary-only
```

**Windows PowerShell:**
```powershell
# Basic usage
python xsd_analyzer.py schema.xsd [options]

# Options:
--output-dir, -o DIR     Output directory (default: ./output)
--formats, -f FORMAT     Output formats: html, json, text, summary 
--summary-only, -s       Only show summary, no file output
--multi-file, -m         Enable multi-file parsing (imports/includes)
--verbose, -v           Enable verbose logging

# Examples:
python xsd_analyzer.py schema.xsd
python xsd_analyzer.py schema.xsd --output-dir ./docs
python xsd_analyzer.py schema.xsd --formats html json
python xsd_analyzer.py schema.xsd --multi-file --summary-only
```

### Tree Visualization - `tree_visualizer.py`

**Unix/macOS/Linux:**
```bash
# Basic usage
python tree_visualizer.py schema.xsd [options]

# Options:
--format, -f FORMAT      Output format: console, text, dot, svg
--output, -o FILE        Output file path
--element, -e ELEMENT    Specific element to visualize
--list-elements, -l      List all available elements
--verbose, -v           Enable verbose logging

# Examples:
python tree_visualizer.py schema.xsd --format console
python tree_visualizer.py schema.xsd --format svg --output tree.svg
python tree_visualizer.py schema.xsd --element BookType --format text
python tree_visualizer.py schema.xsd --list-elements
```

**Windows PowerShell:**
```powershell
# Basic usage
python tree_visualizer.py schema.xsd [options]

# Options:
--format, -f FORMAT      Output format: console, text, dot, svg
--output, -o FILE        Output file path
--element, -e ELEMENT    Specific element to visualize
--list-elements, -l      List all available elements
--verbose, -v           Enable verbose logging

# Examples:
python tree_visualizer.py schema.xsd --format console
python tree_visualizer.py schema.xsd --format svg --output tree.svg
python tree_visualizer.py schema.xsd --element BookType --format text
python tree_visualizer.py schema.xsd --list-elements
```

### Element Inspector - `element_inspector.py`

**Unix/macOS/Linux:**
```bash
# Basic usage
python element_inspector.py schema.xsd [options]

# Options:
--element, -e ELEMENT    Element to inspect
--type, -t TYPE         Type to inspect
--search, -s SEARCH     Search for elements
--stats                 Show schema statistics

# Examples:
python element_inspector.py schema.xsd
python element_inspector.py schema.xsd --element bookstore
python element_inspector.py schema.xsd --type BookType
python element_inspector.py schema.xsd --search "book"
python element_inspector.py schema.xsd --stats
```

**Windows PowerShell:**
```powershell
# Basic usage
python element_inspector.py schema.xsd [options]

# Options:
--element, -e ELEMENT    Element to inspect
--type, -t TYPE         Type to inspect
--search, -s SEARCH     Search for elements
--stats                 Show schema statistics

# Examples:
python element_inspector.py schema.xsd
python element_inspector.py schema.xsd --element bookstore
python element_inspector.py schema.xsd --type BookType
python element_inspector.py schema.xsd --search "book"
python element_inspector.py schema.xsd --stats
```

### Java UML Generator - `java_uml_generator.py` (NEW! ☕)

**Unix/macOS/Linux:**
```bash
# Basic usage
python java_uml_generator.py schema.xsd [options]

# Options:
--output-dir, -o DIR       Output directory (default: ./output)
--formats, -f FORMAT       Output formats: plantuml, mermaid, java (default: all)
--java-package PACKAGE     Java package name for generated classes
--combined                 Combine multiple XSD files into single output
--verbose, -v              Enable verbose logging

# Examples:
# Generate all formats (PlantUML, Mermaid, Java code)
python java_uml_generator.py schema.xsd

# Generate only PlantUML diagrams
python java_uml_generator.py schema.xsd --formats plantuml

# Multiple files with custom package
python java_uml_generator.py schema1.xsd schema2.xsd --java-package com.example.model

# Combined analysis of multiple related schemas
python java_uml_generator.py main.xsd types.xsd --combined --output-dir ./uml
```

**Windows PowerShell:**
```powershell
# Basic usage
python java_uml_generator.py schema.xsd [options]

# Options:
--output-dir, -o DIR       Output directory (default: ./output)
--formats, -f FORMAT       Output formats: plantuml, mermaid, java (default: all)
--java-package PACKAGE     Java package name for generated classes
--combined                 Combine multiple XSD files into single output
--verbose, -v              Enable verbose logging

# Examples:
# Generate all formats (PlantUML, Mermaid, Java code)
python java_uml_generator.py schema.xsd

# Generate only PlantUML diagrams
python java_uml_generator.py schema.xsd --formats plantuml

# Multiple files with custom package
python java_uml_generator.py schema1.xsd schema2.xsd --java-package com.example.model

# Combined analysis of multiple related schemas
python java_uml_generator.py main.xsd types.xsd --combined --output-dir ./uml
```

### Selective Analyzer - `selective_analyzer.py` (NEW! 🎯)

**Unix/macOS/Linux:**
```bash
# Basic usage
python selective_analyzer.py file.xsd [selections...] [options]

# Options:
--output-dir, -o DIR     Output directory (default: ./output)
--formats, -f FORMAT     Output formats: html, json, summary
--verbose, -v           Enable verbose logging

# Examples:
# Select specific elements
python selective_analyzer.py file1.xsd --elements BookType,AuthorType

# Select from multiple files  
python selective_analyzer.py file1.xsd --elements Book file2.xsd --complex-types PersonType

# Select entire namespaces
python selective_analyzer.py schema.xsd --namespaces "http://example.com/library"

# Note: For complex selections, use the Python API (see demo_selective.py)
```

**Windows PowerShell:**
```powershell
# Basic usage
python selective_analyzer.py file.xsd [selections...] [options]

# Options:
--output-dir, -o DIR     Output directory (default: ./output)
--formats, -f FORMAT     Output formats: html, json, summary
--verbose, -v           Enable verbose logging

# Examples:
# Select specific elements
python selective_analyzer.py file1.xsd --elements BookType,AuthorType

# Select from multiple files  
python selective_analyzer.py file1.xsd --elements Book file2.xsd --complex-types PersonType

# Select entire namespaces
python selective_analyzer.py schema.xsd --namespaces "http://example.com/library"

# Note: For complex selections, use the Python API (see demo_selective.py)
```

### CSV Schema Analyzer - `csv_schema_analyzer.py` (NEW! 📊)

**Validate XSD files against CSV-defined business requirements with dynamic depth structure (1-8 levels)**

**Unix/macOS/Linux:**
```bash
# Basic usage
python csv_schema_analyzer.py requirements.csv schema.xsd [more_schemas...] [options]

# Options:
--output-dir, -o DIR     Output directory (default: ./output)
--formats, -f FORMAT     Output formats: console, json, text (default: console)
--verbose, -v           Enable verbose logging

# Examples:
# Validate single XSD against CSV requirements
python csv_schema_analyzer.py demo_requirements.csv test_bookstore.xsd

# Validate multiple XSD files with JSON output
python csv_schema_analyzer.py requirements.csv schema1.xsd schema2.xsd --formats json text

# Generate comprehensive reports
python csv_schema_analyzer.py business_rules.csv *.xsd --output-dir ./validation_reports
```

**Windows PowerShell:**
```powershell
# Basic usage
python csv_schema_analyzer.py requirements.csv schema.xsd [more_schemas...] [options]

# Examples:
# Validate single XSD against CSV requirements
python csv_schema_analyzer.py demo_requirements.csv test_bookstore.xsd

# Validate multiple XSD files with JSON output
python csv_schema_analyzer.py requirements.csv schema1.xsd schema2.xsd --formats json text

# Generate comprehensive reports
python csv_schema_analyzer.py business_rules.csv *.xsd --output-dir ./validation_reports
```

**CSV Format Structure (Dynamic Depth - 8 Levels):**
```csv
id,xpath,description,level1,level2,level3,level4,level5,level6,level7,level8,attribute,expected_type,required,validation_rules,business_purpose
1,"bookstore/storeName","Store name",bookstore,storeName,,,,,,,xs:string,true,"maxLength: 100","Name of the bookstore"
2,"bookstore/book/title","Book title",bookstore,book,title,,,,,,,xs:string,true,,"Book identifier"
3,"orders/items/@id","Deep attribute",orders,items,,,,,,,id,string,true,"pattern: ^[A-Z]{3}$","Item ID"
```

**Analysis Results Categories:**
- ✅ **FOUND**: Requirements perfectly matched in XSD
- ⚠️ **MISMATCH**: Found but with type/requirement differences  
- ❌ **MISSING**: Not found in any XSD file with suggestions

### Relationship Analyzer - `relationship_analyzer.py` (NEW! 🔗)

**Unix/macOS/Linux:**
```bash
# Basic usage
python relationship_analyzer.py file1.xsd file2.xsd [more_files...] [options]

# Options:
--output-dir, -o DIR     Output directory (default: ./output/relationships)
--verbose, -v           Enable verbose logging
--report-only           Show analysis in console and save reports (no interactive display)

# Examples:
# Analyze relationships between multiple files
python relationship_analyzer.py schema1.xsd schema2.xsd schema3.xsd

# Generate comprehensive reports
python relationship_analyzer.py tests/data/*.xsd --output-dir ./reports

# Quick analysis with reports only
python relationship_analyzer.py *.xsd --report-only
```

**Windows PowerShell:**
```powershell
# Basic usage
python relationship_analyzer.py file1.xsd file2.xsd [more_files...] [options]

# Options:
--output-dir, -o DIR     Output directory (default: ./output/relationships)
--verbose, -v           Enable verbose logging
--report-only           Show analysis in console and save reports (no interactive display)

# Examples:
# Analyze relationships between multiple files
python relationship_analyzer.py schema1.xsd schema2.xsd schema3.xsd

# Generate comprehensive reports
python relationship_analyzer.py tests/data/*.xsd --output-dir ./reports

# Quick analysis with reports only
python relationship_analyzer.py *.xsd --report-only
```

### Demo Scripts

**Unix/macOS/Linux:**
```bash
# Basic demo with single file
python demos/demo.py

# Selective analysis demo (NEW!)
python demos/demo_selective.py

# Multi-file parser test
python tests/data_parser.py
```

**Windows PowerShell:**
```powershell
# Basic demo with single file
python demos/demo.py

# Selective analysis demo (NEW!)
python demos/demo_selective.py

# Multi-file parser test
python tests/data_parser.py
```

## 📋 Requirements

- **Python 3.8+**
- **System Dependencies**: `graphviz` (for SVG generation)
  ```bash
  # macOS
  brew install graphviz
  
  # Ubuntu/Debian
  sudo apt-get install graphviz
  
  # Windows (PowerShell as Administrator)
  winget install graphviz
  # OR download from: https://graphviz.org/download/
  ```

- **Python Dependencies**: All automatically installed via `requirements.txt`
  - lxml (fast XML parsing)
  - jinja2 (HTML template engine)
  - rich (terminal formatting)
  - anytree (tree structures)
  - graphviz (diagram generation)
  - And more...

## 🔧 Setup Instructions

### First-Time Setup

**Unix/macOS/Linux:**
```bash
# Clone or download the project
cd XSD_Visualizations

# Create virtual environment
python -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Test installation
python demos/demo.py
```

**Windows PowerShell (run as Administrator for graphviz):**
```powershell
# Clone or download the project
cd XSD_Visualizations

# Install graphviz system dependency
winget install graphviz

# Create virtual environment
python -m venv .venv

# Activate virtual environment
.venv\Scripts\Activate.ps1

# Install Python dependencies
pip install -r requirements.txt

# Test installation
python demos/demo.py
```

**Windows Command Prompt:**
```cmd
# Clone or download the project
cd XSD_Visualizations

# Create virtual environment
python -m venv .venv

# Activate virtual environment
.venv\Scripts\activate.bat

# Install Python dependencies
pip install -r requirements.txt

# Test installation
python demos/demo.py
```

### VS Code Setup (Optional)
1. Open the `xsd-visualizer.code-workspace` file in VS Code
2. Install recommended extensions when prompted
3. Python interpreter should auto-detect the virtual environment
4. Use built-in tasks (Ctrl/Cmd+Shift+P → "Tasks: Run Task")

## 🎨 Output Examples

### HTML Documentation
- **Interactive navigation** with breadcrumbs and cross-links
- **Responsive design** that works on desktop and mobile
- **Search and filtering** capabilities
- **Dependency visualization** with D3.js diagrams
- **Syntax highlighting** for code examples

### Tree Visualizations
- **Console**: Colored tree display with Rich formatting
- **SVG**: Professional diagrams for presentations
- **Text**: Plain text for documentation and reports

### Data Export
- **JSON**: Complete schema structure for programmatic access
- **Statistics**: Element counts, depth analysis, complexity metrics

## 🔧 Advanced Usage

### Custom Templates
Modify templates in the `templates/` directory to customize HTML output:
- `index.html` - Main page layout
- `element.html` - Element detail pages
- `styles.css` - Visual styling
- `script.js` - Interactive features

### Programmatic Usage
```python
from utils.xsd_parser import XSDParser
from utils.html_generator import HTMLGenerator

# Parse XSD
parser = XSDParser("schema.xsd")
structure = parser.parse()

# Generate documentation
generator = HTMLGenerator(structure)
generator.generate_documentation("./output")

# Access parsed data
print(f"Found {len(structure['elements'])} root elements")
```

## ⚠️ Troubleshooting

### Common Issues

1. **"graphviz not found"** when generating SVG
   - Install system graphviz package (see Requirements)

2. **Template not found errors**
   - Ensure all files in `templates/` directory exist
   - Check file permissions

3. **Import errors**
   - Activate virtual environment:
     - Unix/macOS/Linux: `source .venv/bin/activate`
     - Windows PowerShell: `.venv\Scripts\Activate.ps1`
     - Windows Command Prompt: `.venv\Scripts\activate.bat`
   - Install dependencies: `pip install -r requirements.txt`

### Performance Tips

- **Large XSD files**: Use `--summary-only` for quick analysis
- **Memory usage**: Generate specific formats rather than all at once
- **Complex schemas**: Focus on specific elements with `--element` option

## 🎯 What This Toolkit Can Do

### ✅ Single File Analysis
- Parse any XSD file and extract its complete structure
- Generate interactive HTML documentation
- Create tree visualizations (console, SVG, text)
- Inspect specific elements and types
- Export to multiple formats (JSON, HTML, text)

### ✅ Multi-File Schema Analysis (NEW!)
- Handle schemas split across multiple files
- Support `xs:import`, `xs:include`, and `xs:redefine` statements
- Track dependencies between files
- Maintain namespace integrity across files
- Generate unified documentation from all files

### ✅ Selective Component Analysis (NEW! 🎯)
- **Cherry-pick specific elements** from any XSD file
- **Select individual types** (complex or simple) from different files
- **Choose entire namespaces** to include all components
- **Mix selection strategies** in a single analysis
- **Generate focused documentation** for only selected components
- **Perfect for large enterprise schemas** where you only need specific parts

### ✅ Output Formats
- **HTML**: Interactive documentation with navigation and search
- **JSON**: Machine-readable structure data
- **SVG**: Professional tree diagrams
- **Text**: Console-friendly reports and trees
- **Summary Tables**: Quick overviews with Rich formatting

### ✅ VS Code Integration
- Syntax highlighting for XSD files
- Custom tasks for common operations
- Built-in Simple Browser for viewing HTML output
- Python environment pre-configured

## 📝 Example Output

The toolkit successfully analyzes the included `test_bookstore.xsd` sample:

```
XSD Analysis Summary
┏━━━━━━━━━━━━━━━━━━┳━━━━━━━┓
┃ Metric           ┃ Count ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━┩
│ Total Elements   │ 9     │
│ Complex Types    │ 3     │
│ Simple Types     │ 2     │
│ Maximum Depth    │ 1     │
│ Total Attributes │ 0     │
└──────────────────┴───────┘
```

The generated HTML documentation provides a complete interactive view of the schema structure with navigation, search, and dependency analysis.

## 🤝 Contributing

This is a complete, working toolkit ready for analyzing XSD files offline. Feel free to extend it with additional features:

- Custom output formats
- Integration with other tools
- Enhanced visualization options
- Additional analysis metrics

## 📄 License

This project provides tools for XSD analysis and visualization. Use responsibly and in accordance with your organization's policies.
