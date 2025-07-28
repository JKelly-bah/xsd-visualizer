# XSD to CSV Converter - Complete Usage Guide

## Overview

The XSD to CSV converter extracts comprehensive information from XML Schema Definition (XSD) files and exports it to CSV format for analysis. This tool is designed to handle complex enterprise schemas with multiple layers of inheritance, cross-schema references, and nested attribute patterns.

## Generated Files Summary

Your XSD schemas have been successfully converted to CSV format with the following results:

### Batch Conversion Statistics
- **Total Files Processed:** 5 XSD schemas
- **Success Rate:** 100% (5/5 successful)
- **Total CSV Rows Generated:** 363 rows
- **Total Schema Components Analyzed:** 358 components

### Individual Schema Analysis

#### 1. Collection.xsd (39 rows)
- **Elements:** 3 root elements
- **Complex Types:** 30 types with inheritance patterns
- **Simple Types:** 3 restricted types
- **Attributes:** 2 global/local attributes
- **Documentation:** 13 documented components
- **Key Features:** Collection_ComplexType with restriction-based inheritance

#### 2. common-base.xsd (74 rows)
- **Elements:** 4 root elements
- **Complex Types:** 55 types
- **Simple Types:** 9 restricted types
- **Attributes:** 5 global/local attributes
- **Documentation:** 12 documented components
- **Key Features:** Base types for enterprise document structures

#### 3. common_complexTypes.xsd (80 rows)
- **Elements:** 3 root elements
- **Complex Types:** 64 types
- **Simple Types:** 6 restricted types
- **Attributes:** 6 global/local attributes
- **Documentation:** 10 documented components
- **Key Features:** Reusable complex type definitions

#### 4. security-types.xsd (63 rows)
- **Elements:** 2 root elements
- **Complex Types:** 47 types
- **Simple Types:** 11 restricted types
- **Attributes:** 2 global/local attributes
- **Documentation:** 7 documented components
- **Key Features:** Security classification and access control types

#### 5. workflow-types.xsd (107 rows)
- **Elements:** 2 root elements
- **Complex Types:** 92 types
- **Simple Types:** 10 restricted types
- **Attributes:** 2 global/local attributes
- **Documentation:** 12 documented components
- **Key Features:** Workflow state and process management types

## CSV Output Structure

Each CSV file contains the following columns:

### Core Identification
- **category:** Type of schema component (root_element, complex_type, simple_type, etc.)
- **name:** Component name
- **type:** Data type or schema construct type
- **namespace:** Namespace prefix
- **scope:** Global or local scope
- **source_file:** Source XSD file path

### Structural Information
- **parent_type:** Parent type for nested components
- **base_type:** Base type for inheritance
- **derivation_type:** restriction, extension, or direct
- **location:** Where the component is defined

### Constraints and Attributes
- **min_occurs, max_occurs:** Occurrence constraints
- **use:** required, optional, prohibited (for attributes)
- **default_value, fixed_value:** Default and fixed values
- **restrictions:** Restriction facets (length, pattern, etc.)

### Relationships
- **is_reference:** Whether component is a reference
- **reference_target:** Target of reference
- **is_inherited:** Whether inherited from base type
- **inheritance_chain:** Full inheritance hierarchy

### Documentation
- **description:** Extracted documentation text
- **documentation:** Additional documentation content

### Statistical Information
- **element_count:** Number of child elements
- **attribute_count:** Number of attributes
- **is_abstract:** Whether type is abstract
- **is_mixed:** Whether content model is mixed

## Usage Examples

### Opening CSV Files

#### In Excel/LibreOffice Calc:
1. Open Excel/LibreOffice
2. File → Open → Select CSV file
3. Choose "Delimited" and "Comma" as delimiter
4. Set text encoding to UTF-8

#### In Python:
```python
import pandas as pd

# Load a specific schema
df = pd.read_csv('output/csv_batch/Collection.csv')

# Filter for complex types only
complex_types = df[df['category'] == 'complex_type']

# Find all inheritance relationships
inheritance = df[df['base_type'].notna()]

# Get documentation coverage
documented = df[df['description'].str.len() > 0]
```

#### In R:
```r
# Load CSV data
collection_data <- read.csv("output/csv_batch/Collection.csv", stringsAsFactors = FALSE)

# Filter by category
complex_types <- subset(collection_data, category == "complex_type")

# Analyze inheritance patterns
inheritance_data <- subset(collection_data, base_type != "")
```

### Common Analysis Queries

#### Find All Types with Inheritance:
```csv
Filter: derivation_type = "restriction" OR derivation_type = "extension"
```

#### Locate Cross-Schema References:
```csv
Filter: namespace != "" AND namespace != "xsd"
```

#### Identify Undocumented Components:
```csv
Filter: description = "" OR description IS NULL
```

#### Find Optional vs Required Attributes:
```csv
Filter: category = "local_attribute" AND use = "required"
```

## File Locations

### Generated CSV Files:
- `output/csv_batch/Collection.csv` - Collection schema analysis
- `output/csv_batch/common-base.csv` - Base types analysis
- `output/csv_batch/common_complexTypes.csv` - Complex types analysis
- `output/csv_batch/security-types.csv` - Security types analysis
- `output/csv_batch/workflow-types.csv` - Workflow types analysis

### Summary Reports:
- `output/csv_batch/batch_summary.txt` - Human-readable summary
- `output/csv_batch/batch_conversion_results.json` - Machine-readable results

### Conversion Tools:
- `src/xsd_to_csv/simple_csv_converter.py` - Single file converter
- `src/xsd_to_csv/batch_csv_converter.py` - Batch processing tool
- `src/xsd_to_csv/csv_converter.py` - Advanced converter (requires lxml)

## Advanced Features Detected

Your schemas contain several enterprise-grade patterns that were successfully captured:

### Complex Inheritance Patterns
- **Collection_ComplexType:** Uses complexContent/restriction with base="Collection_Baseline_ComplexType"
- **Multiple inheritance levels:** Base types extending other base types
- **Attribute inheritance:** Attributes inherited through restriction/extension

### Cross-Schema References
- **Namespace usage:** Multiple namespaces (base:, sec:, tns:) properly resolved
- **Type references:** Types referencing definitions from other schemas
- **Import/Include patterns:** Schema modularization captured

### Enterprise Attributes
- **Security attributes:** Classification levels, retention periods
- **Versioning attributes:** Collection versions, schema versions
- **Metadata attributes:** Creation dates, modification tracking

### Documentation Coverage
- **54 documented components** out of 358 total (15% documentation coverage)
- **Embedded documentation:** xs:annotation/xs:documentation patterns extracted
- **Multi-line descriptions:** Complex documentation properly captured

## Working on Your Other Computer

All generated files are self-contained and ready for transfer:

1. **Copy the entire `output/csv_batch/` directory** to your other computer
2. **No dependencies required** - CSV files open in any spreadsheet application
3. **Summary reports included** - Both human and machine-readable formats
4. **Complete analysis preserved** - All schema relationships and metadata captured

## Troubleshooting

### If CSV files don't open properly:
- Ensure UTF-8 encoding is selected
- Use comma as delimiter
- Check that quotes are handled correctly

### For large files:
- Use filtering to focus on specific categories
- Import into database tools for better performance
- Use programming languages (Python/R) for advanced analysis

### Missing information:
- Some complex cross-schema relationships may need manual verification
- Import/include chains are captured but may need additional context
- Custom namespace URIs are preserved in the namespace column

## Next Steps

Your XSD to CSV conversion is complete and ready for analysis on your other computer. The generated files contain comprehensive information about your enterprise schema structure, inheritance patterns, and cross-schema relationships.

**Files ready for transfer:**
- 5 detailed CSV files (63KB total)
- Summary reports and statistics
- Complete documentation of 363 schema components
- Full capture of complex inheritance and namespace patterns

All processing completed successfully without requiring user input, as requested!
