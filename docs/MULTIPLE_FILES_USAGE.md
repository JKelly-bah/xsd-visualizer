# Multiple Files Usage Guide

Your XSD visualizer now supports analyzing multiple XSD files across all tools! Here are the different ways to use this feature:

## 1. Main XSD Analyzer (xsd_analyzer.py)

### Usage Options

#### Single File (Original Behavior)
```bash
python xsd_analyzer.py schema.xsd
```

#### Multiple Files Separately
Process each file independently with separate output directories:
```bash
python xsd_analyzer.py schema1.xsd schema2.xsd schema3.xsd
```
- Creates output directories: `output/schema1/`, `output/schema2/`, `output/schema3/`

#### Multiple Files with Wildcards
```bash
python xsd_analyzer.py *.xsd
python xsd_analyzer.py schemas/*.xsd
```

#### Combined Analysis
Analyze multiple files together as a single project:
```bash
python xsd_analyzer.py schema1.xsd schema2.xsd --combined
```
- Uses multi-file parser to handle relationships between schemas
- Creates single output in `output/` directory

#### Summary Only (Multiple Files)
```bash
python xsd_analyzer.py schema1.xsd schema2.xsd --summary-only
```

## 2. Tree Visualizer (tree_visualizer.py)

### Usage Options

#### Visualize Multiple Files Separately
```bash
python tree_visualizer.py schema1.xsd schema2.xsd --format console
python tree_visualizer.py *.xsd --format svg
```
- Each file gets its own visualization
- Output files are numbered: `schema1_tree_1.svg`, `schema2_tree_2.svg`

#### Combined Tree Visualization
```bash
python tree_visualizer.py schema1.xsd schema2.xsd --combined --format svg
```
- Creates a single combined visualization
- Uses the first file as the base structure

#### Console Output for Multiple Files
```bash
python tree_visualizer.py schema1.xsd schema2.xsd --format console
```
- Shows tree structure for each file in sequence

#### Export Multiple Trees to Files
```bash
python tree_visualizer.py schema1.xsd schema2.xsd --format text
```
- Creates: `schema1_tree_1.txt`, `schema2_tree_2.txt`

## 3. Selective Analyzer (selective_analyzer.py)

### Usage Options

#### Select Components from Multiple Files
```bash
python selective_analyzer.py file1.xsd file2.xsd --elements Book,Author
```
- Applies the same selection criteria to all files
- Combines results into a single analysis

#### Select Specific Elements
```bash
python selective_analyzer.py schema1.xsd schema2.xsd --elements "BookType,AuthorType"
```

#### Select Complex Types
```bash
python selective_analyzer.py *.xsd --complex-types "PersonType,AddressType"
```

#### Select by Namespace
```bash
python selective_analyzer.py schema1.xsd schema2.xsd --namespaces "http://example.com/library"
```

#### Combined Selection with Multiple Criteria
```bash
python selective_analyzer.py main.xsd other.xsd \
  --elements Library,Book \
  --complex-types BookType,PersonType \
  --namespaces "http://example.com/common" \
  --formats html json
```

## VS Code Tasks

New tasks have been added to `.vscode/tasks.json`:

### Main Analyzer
- **Analyze Multiple XSD Files**: Process multiple files separately
- **Analyze Multiple XSD Files (Combined)**: Process multiple files together

### Tree Visualizer
- **Visualize Tree (Multiple Files)**: Create tree visualizations for multiple files

### Selective Analyzer
- **Selective Analysis (Multiple Files)**: Select specific components from multiple files

## Use Cases

### Separate Analysis
Use when you have:
- Independent schemas that don't reference each other
- Different projects or modules
- Want individual documentation for each schema

### Combined Analysis
Use when you have:
- Related schemas with imports/includes
- A single project split across multiple XSD files
- Want unified documentation showing relationships

### Selective Analysis
Use when you want to:
- Extract specific components from large schemas
- Create focused documentation on particular elements
- Analyze only certain namespaces across multiple files

## Examples with Your Test Files

### Main Analyzer
```bash
# Analyze both test schemas separately
python xsd_analyzer.py test_bookstore.xsd tests/data/library.xsd

# Analyze as combined project
python xsd_analyzer.py test_bookstore.xsd tests/data/library.xsd --combined

# Quick summary of multiple files
python xsd_analyzer.py test_bookstore.xsd tests/data/library.xsd --summary-only
```

### Tree Visualizer
```bash
# Console trees for both files
python tree_visualizer.py test_bookstore.xsd tests/data/library.xsd

# SVG exports for each file
python tree_visualizer.py test_bookstore.xsd tests/data/library.xsd --format svg

# Combined visualization
python tree_visualizer.py test_bookstore.xsd tests/data/library.xsd --combined --format svg
```

### Selective Analyzer
```bash
# Select specific elements from both files
python selective_analyzer.py test_bookstore.xsd tests/data/library.xsd --elements book,library

# Select all components (useful for filtering large schemas)
python selective_analyzer.py test_bookstore.xsd tests/data/library.xsd --namespaces "*"

# Generate HTML documentation for selected components
python selective_analyzer.py test_bookstore.xsd tests/data/library.xsd \
  --elements book,library --formats html summary
```

## Output Structures

### Multiple Files (Separate Analysis)
```
output/
├── test_bookstore/
│   ├── html/
│   ├── structure.json
│   └── summary.txt
└── library/
    ├── html/
    ├── structure.json
    └── summary.txt
```

### Combined Analysis
```
output/
├── html/
├── structure.json
└── summary.txt
```

### Tree Visualizations (Multiple Files)
```
test_bookstore_tree_1.svg
library_tree_2.svg
```

### Tree Visualizations (Combined)
```
combined_tree.svg
```

## Benefits of Multiple File Support

1. **Batch Processing**: Analyze entire directories of XSD files at once
2. **Comparative Analysis**: See differences and similarities across schemas
3. **Project-wide Documentation**: Generate unified documentation for related schemas
4. **Selective Extraction**: Pick specific components across multiple files
5. **Flexible Output**: Choose between separate or combined analysis results
6. **Workflow Integration**: Enhanced VS Code tasks for seamless development

All tools now maintain backward compatibility while offering powerful new multi-file capabilities!
