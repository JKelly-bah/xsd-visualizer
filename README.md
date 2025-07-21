# XSD Visualization and Analysis Tools

A comprehensive offline toolkit for visualizing and analyzing large, complex XSD (XML Schema Definition) files. This workspace provides powerful tools for understanding schema structure, generating documentation, and creating visual representations without requiring any online services.

## 🚀 Quick Start with Docker (Recommended)

The easiest way to get started is using Docker - no local installation required!

### Prerequisites
- Docker Desktop installed and running

### Build & Run
```bash
# Build the Docker image
docker build -t xsd-visualizer .

# Analyze XSD files (replace paths with your actual directories)
docker run --rm \
  -v "/path/to/your/xsd/files:/input" \
  -v "/path/to/output:/output" \
  xsd-visualizer

# Example: Analyze test files
docker run --rm \
  -v "$(pwd)/test_input:/input" \
  -v "$(pwd)/docker_output:/output" \
  xsd-visualizer
```

### Windows Users
```cmd
# Build
docker build -t xsd-visualizer .

# Run (use forward slashes for Windows paths)
docker run --rm -v "/c/path/to/xsd:/input" -v "/c/path/to/output:/output" xsd-visualizer
```

## 📦 What You Get

After running the Docker container, your output directory will contain:

```
output/
├── java_classes.puml         # PlantUML class diagram
├── java_classes.mmd          # Mermaid class diagram  
├── java/                     # Generated Java source code
│   └── [package-structure]/  # Java classes from XSD
├── html/                     # HTML documentation
│   ├── index.html           # Interactive documentation
│   ├── elements/            # Element details
│   └── types/               # Type definitions
├── structure.json           # JSON schema analysis
└── summary.txt              # Analysis summary
```

## 🎨 View Your Diagrams

### PlantUML Diagrams
Copy the content of `java_classes.puml` and paste it into:
- **https://www.plantuml.com/plantuml/uml/** (PlantUML Online Editor)

### Mermaid Diagrams  
Copy the content of `java_classes.mmd` and paste it into:
- **https://mermaid.live/** (Mermaid Live Editor)

## ✨ Features

- **🏗️ Java UML Generator** - Convert XSD to Java class diagrams and source code
- **📊 Multiple Output Formats** - PlantUML, Mermaid, HTML, JSON, Java code
- **🔍 Multi-File Schema Support** - Handle imports, includes, and redefines
- **📱 Interactive HTML Documentation** - Browse your schema structure
- **🐳 Docker Ready** - Complete containerized environment
- **⚡ Offline First** - No internet required for analysis

## 🛠️ Local Development (Optional)

If you prefer to run locally instead of Docker:

```bash
# Install Python dependencies
pip install -r config/requirements.txt

# Analyze XSD files
python xsd_analyzer.py your_schema.xsd --formats html json

# Generate Java UML
python src/analyzers/java_uml_generator.py schema.xsd --formats plantuml mermaid java
```

## 📚 Documentation

- **[Docker Setup Guide](docs/DOCKER_README.md)** - Detailed Docker instructions
- **[Complete Documentation](docs/README.md)** - Full feature documentation  
- **[Project Structure](PROJECT_STRUCTURE.md)** - Code organization
- **[Diagram Viewing Guide](DIAGRAM_VIEWING_GUIDE.md)** - How to view generated diagrams

## 🧪 Test with Sample Data

The project includes test XSD files to try immediately:

```bash
# Test with included samples
docker run --rm \
  -v "$(pwd)/test_input:/input" \
  -v "$(pwd)/test_output:/output" \
  xsd-visualizer

# Check the results
ls test_output/
```

## 🤝 Contributing

This is a comprehensive XSD analysis toolkit. Contributions welcome!

## 📄 License

Open source project for XSD visualization and analysis.
