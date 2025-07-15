<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# XSD Visualization Project Instructions

This project focuses on offline analysis and visualization of XML Schema Definition (XSD) files. 

## Key Guidelines:

- **Offline-First**: All tools must work without internet connectivity
- **Large File Support**: Optimize for handling complex, multi-megabyte XSD files
- **Multiple Output Formats**: Support HTML, SVG, text, and interactive visualizations
- **Modular Design**: Keep parsers, generators, and visualizers as separate, reusable components
- **Error Handling**: Robust handling of malformed or incomplete XSD files
- **Performance**: Use efficient parsing and lazy loading for large schemas

## Code Patterns:

- Use `lxml` for XML parsing (faster than built-in xml module)
- Implement caching for parsed schema components
- Provide progress indicators for long-running operations
- Include detailed logging for debugging complex schemas
- Use type hints and docstrings for all functions
- Follow PEP 8 style guidelines

## Common Tasks:

- Parsing XSD files and extracting schema structure
- Generating HTML documentation with cross-references
- Creating tree visualizations of element hierarchies
- Mapping dependencies between schema components
- Converting between different output formats
