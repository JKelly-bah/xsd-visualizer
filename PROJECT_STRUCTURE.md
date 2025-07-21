# Project Structure

This project has been reorganized into a clean, modular structure:

## 📁 Directory Organization

```
xsd-visualizer/
├── 📋 docs/                          # All documentation
│   ├── README.md                     # Main project documentation  
│   ├── DOCKER_README.md             # Docker setup guide
│   ├── DEVELOPER.md                 # Developer guidelines
│   ├── RELATIONSHIP_ANALYZER.md     # Relationship analysis docs
│   ├── MULTIPLE_FILES_USAGE.md      # Multi-file analysis guide
│   └── CSV_IMPLEMENTATION_SUMMARY.md # CSV analysis documentation
│
├── 🐳 docker/                        # Docker containerization
│   ├── Dockerfile                   # Container definition
│   ├── docker-entrypoint.sh         # Container entry point
│   ├── run-xsd-visualizer.sh        # Shell script runner (Mac/Linux)
│   ├── run-xsd-visualizer.bat       # Batch script runner (Windows)  
│   └── test-docker.sh               # Docker testing script
│
├── 🐍 src/                           # Core application code
│   ├── analyzers/                   # Analysis tools
│   │   ├── xsd_analyzer.py          # Main XSD analysis engine
│   │   ├── tree_visualizer.py       # Tree visualization generator
│   │   ├── selective_analyzer.py    # Selective element analysis
│   │   ├── relationship_analyzer.py # Inter-schema relationships
│   │   ├── csv_schema_analyzer.py   # CSV-to-XSD analysis
│   │   └── element_inspector.py     # Element detail inspector
│   │
│   ├── parsers/                     # XSD parsing utilities  
│   │   ├── xsd_parser.py            # Core XSD parsing logic
│   │   ├── multi_file_xsd_parser.py # Multi-file XSD handling
│   │   └── selective_xsd_parser.py  # Selective parsing utilities
│   │
│   └── generators/                  # Output generation
│       └── html_generator.py        # HTML documentation generator
│
├── 🎨 templates/                     # HTML output templates
│   ├── index.html                   # Main documentation template
│   ├── element.html                 # Element page template
│   ├── dependencies.html            # Dependency graph template
│   ├── styles.css                   # CSS styling
│   └── script.js                    # Interactive JavaScript
│
├── 🧪 tests/                         # Test files and scripts
│   ├── data/                        # Sample XSD files
│   │   ├── test_bookstore.xsd       # Sample bookstore schema
│   │   ├── common-types.xsd         # Common type definitions
│   │   ├── library.xsd              # Library schema
│   │   └── publisher.xsd            # Publisher schema
│   │
│   └── scripts/                     # Test scripts
│       ├── test_multifile_parser.py # Multi-file parsing tests
│       ├── test_selective_*.py      # Selective analysis tests
│       └── debug_*.py               # Debugging utilities
│
├── 🎯 demos/                         # Demo scripts and sample data
│   ├── demo.py                      # Basic demonstration
│   ├── demo_selective.py            # Selective analysis demo
│   └── *.csv                        # Sample CSV files
│
├── ⚙️ config/                        # Configuration files
│   ├── requirements.txt             # Python dependencies
│   └── xsd-visualizer.code-workspace # VS Code workspace
│
├── 🚀 Root-level convenience scripts
│   ├── xsd_analyzer.py              # Main analyzer wrapper
│   ├── tree_visualizer.py           # Tree visualizer wrapper
│   └── selective_analyzer.py        # Selective analyzer wrapper
│
└── test_files/                      # Docker testing directory
    ├── input/                       # Test input files
    └── output/                      # Test output files
```

## 🔄 Import Structure

The new modular structure uses clean imports:

```python
# Analyzers import parsers and generators
from src.parsers.xsd_parser import XSDParser
from src.generators.html_generator import HTMLGenerator

# Parsers are self-contained
from lxml import etree

# Generators use templates
from pathlib import Path
```

## 🚀 Usage

You can run tools from the project root using the convenience wrappers:

```bash
python xsd_analyzer.py my_schema.xsd
python tree_visualizer.py my_schema.xsd  
python selective_analyzer.py my_schema.xsd --elements book,author
```

Or run them directly from the src directory:

```bash
python src/analyzers/xsd_analyzer.py my_schema.xsd
```

## 🐳 Docker

Docker files are now organized in the `docker/` directory, and the container automatically uses the new structure.

```bash
./docker/run-xsd-visualizer.sh /path/to/xsd/files
```
