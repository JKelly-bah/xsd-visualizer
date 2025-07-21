# XSD Relationship Analyzer

The **Relationship Analyzer** (`relationship_analyzer.py`) is a powerful tool that analyzes and explains the relationships between multiple XSD files. It identifies imports, includes, dependencies, namespace relationships, and cross-references to help you understand complex schema architectures.

## Features

### 🔍 **Comprehensive Analysis**
- **File Relationships**: Identifies imports, includes, and redefines between XSD files
- **Component Dependencies**: Tracks type references and dependencies across files
- **Namespace Analysis**: Maps namespace usage and prefixes across all files
- **Dependency Graph**: Visual representation of file dependencies

### 📊 **Rich Console Output**
- Color-coded relationship displays
- Interactive tree views of dependencies
- Detailed tables with namespace information
- Summary statistics and overview

### 📁 **Detailed Reports**
- JSON report for programmatic use
- Human-readable text report
- Complete analysis data export

## Usage

### Basic Analysis
```bash
python relationship_analyzer.py schema1.xsd schema2.xsd schema3.xsd
```

### Analyze All XSD Files in Directory
```bash
python relationship_analyzer.py *.xsd
```

### Custom Output Directory
```bash
python relationship_analyzer.py *.xsd --output-dir ./analysis
```

### Report Only (No Console Output)
```bash
python relationship_analyzer.py main.xsd imports/*.xsd --report-only
```

### Verbose Logging
```bash
python relationship_analyzer.py library/*.xsd --verbose
```

## What It Analyzes

### 1. **File Relationships**
- **Imports**: `<xs:import>` declarations and their target namespaces
- **Includes**: `<xs:include>` declarations for same-namespace files
- **Redefines**: `<xs:redefine>` declarations for schema modifications

### 2. **Component Dependencies**
- **Type References**: Elements that reference types from other files
- **Base Types**: Complex/simple types that extend types from other files
- **Element References**: References to global elements in other files

### 3. **Namespace Analysis**
- **Target Namespaces**: Which files define which namespaces
- **Namespace Usage**: Which files use which namespaces
- **Prefix Mappings**: How namespaces are prefixed in different files
- **Cross-Namespace References**: Dependencies across namespace boundaries

### 4. **Dependency Graph**
- **Root Files**: Files that aren't imported by others
- **Dependency Chains**: How files depend on each other
- **Circular Dependencies**: Detection of circular references

## Console Output Sections

### **Analysis Overview**
```
Analysis Overview
┌─────────────────────┬───────┐
│ Metric              │ Count │
├─────────────────────┼───────┤
│ Total Files         │ 4     │
│ File Relationships  │ 2     │
│ Component Dependencies │ 0  │
│ Unique Namespaces   │ 7     │
└─────────────────────┴───────┘
```

### **File Relationships**
Shows direct relationships between files:
- Import relationships with target namespaces
- Include relationships for same-namespace files
- Schema locations and resolved paths

### **Component Dependencies**
Details component-level dependencies:
- Type references across files
- Base type inheritance chains
- Element references between schemas

### **Namespace Analysis**
Comprehensive namespace mapping:
- Which files use each namespace
- Target namespace declarations
- Common prefixes and their usage

### **Dependency Graph**
Visual tree representation:
```
XSD Files Dependency Graph
├── main.xsd
└── library.xsd
    ├── publisher.xsd (import)
    └── common-types.xsd (include)
```

## Generated Reports

### **JSON Report** (`relationship_analysis.json`)
Complete machine-readable analysis including:
```json
{
  "analysis_summary": {
    "total_files": 4,
    "file_relationships": 2,
    "component_dependencies": 0,
    "unique_namespaces": 7
  },
  "files_analyzed": [...],
  "file_relationships": [...],
  "component_dependencies": [...],
  "namespaces": {...}
}
```

### **Text Report** (`relationship_analysis.txt`)
Human-readable summary with:
- Analysis overview
- Files analyzed
- Detailed relationship listings
- Component dependencies
- Namespace analysis

## Use Cases

### **Multi-File Schema Projects**
- Understanding how schemas are organized across files
- Identifying import/include relationships
- Mapping namespace boundaries

### **Schema Refactoring**
- Finding all dependencies before moving components
- Understanding impact of namespace changes
- Identifying circular dependencies

### **Documentation Generation**
- Creating architectural overviews
- Explaining schema relationships to stakeholders
- Generating dependency diagrams

### **Validation & Quality Assurance**
- Ensuring all imports are properly resolved
- Checking for missing dependencies
- Validating namespace consistency

## Integration with Other Tools

### **VS Code Task**
The analyzer is integrated as a VS Code task:
- **"Analyze Relationships"**: Run analysis on selected files

### **Workflow Integration**
Works well with other XSD visualizer tools:
1. **Relationship Analyzer**: Understand overall architecture
2. **XSD Analyzer**: Detailed analysis of individual files
3. **Tree Visualizer**: Visual representation of structures
4. **Selective Analyzer**: Focus on specific components

## Example Output

When analyzing the test files:

```
XSD Relationship Analyzer
Analyzing 4 XSD files...

╭─────────────────────────────╮
│ XSD Relationship Analysis   │
╰─────────────────────────────╯

File Relationships:
• library.xsd --import--> publisher.xsd
  - Namespace: http://example.com/publisher
• library.xsd --include--> common-types.xsd

Dependency Graph:
├── test_bookstore.xsd (standalone)
└── library.xsd
    ├── publisher.xsd (import)
    └── common-types.xsd (include)
```

## Benefits

1. **Architectural Understanding**: Get a clear picture of how schemas relate
2. **Impact Analysis**: Understand consequences of changes
3. **Documentation**: Generate comprehensive relationship documentation
4. **Quality Assurance**: Validate schema organization and dependencies
5. **Refactoring Support**: Safely restructure multi-file schemas

The Relationship Analyzer is essential for working with complex, multi-file XSD projects where understanding the relationships between files is crucial for maintenance and development.
