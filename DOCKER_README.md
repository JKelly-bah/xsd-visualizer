# XSD Visualizer Docker Setup

This document explains how to run the XSD Visualizer using Docker containers, making it easy to analyze XSD files without installing dependencies locally.

## Prerequisites

- Docker Desktop installed and running
- Git Bash (for Windows users) or a terminal

## Quick Start

### For Windows (Git Bash)

1. **Open Git Bash** in the project directory
2. **Run the analysis:**
   ```bash
   ./run-xsd-visualizer.sh "/c/path/to/your/xsd/files" "/c/path/to/output"
   ```

### For Windows (Command Prompt)

1. **Open Command Prompt** in the project directory
2. **Run the analysis:**
   ```cmd
   run-xsd-visualizer.bat "C:\path\to\your\xsd\files" "C:\path\to\output"
   ```

### Examples

```bash
# Analyze XSD files in the current directory, output to ./results
./run-xsd-visualizer.sh "." "./results"

# Analyze XSD files in a specific Windows directory
./run-xsd-visualizer.sh "/c/MyProject/schemas" "/c/MyProject/documentation"

# Using relative paths
./run-xsd-visualizer.sh "./test_multifile" "./output"
```

## What the Container Does

1. **Finds all XSD files** in your input directory
2. **Analyzes each file** using the XSD Visualizer tools
3. **Generates multiple output formats:**
   - HTML documentation with interactive navigation
   - JSON structure export
   - Text summaries
   - Tree visualizations
4. **Saves results** to your specified output directory on your computer

## Output Structure

After running, your output directory will contain:

```
output/
├── structure.json          # JSON export of schema structure
├── summary.txt            # Text summary of analysis
├── html/                  # HTML documentation
│   ├── index.html         # Main documentation page
│   ├── elements/          # Individual element pages
│   ├── types/            # Type definitions
│   └── static/           # CSS and JavaScript
└── [schema-name]/        # Individual schema results (if multiple files)
```

## Manual Docker Commands

If you prefer to run Docker commands manually:

### Build the Image
```bash
docker build -t xsd-visualizer:latest .
```

### Run Analysis
```bash
# Windows paths (use forward slashes)
docker run --rm \
  -v "/c/path/to/xsd/files:/input" \
  -v "/c/path/to/output:/output" \
  xsd-visualizer:latest

# Linux/macOS paths
docker run --rm \
  -v "/path/to/xsd/files:/input" \
  -v "/path/to/output:/output" \
  xsd-visualizer:latest
```

## Troubleshooting

### Docker Not Found
```
ERROR: Docker is not running or not installed.
```
**Solution:** Install Docker Desktop and make sure it's running.

### Path Issues on Windows
If you get path-related errors:
- Use forward slashes: `/c/MyFolder` instead of `C:\MyFolder`
- Make sure paths are absolute or properly relative
- Escape spaces in paths with quotes: `"C:/My Folder"`

### No XSD Files Found
```
No XSD files found in /input
```
**Solutions:**
- Check that your input directory contains `.xsd` files
- Verify the path is correct
- Make sure files have the `.xsd` extension

### Permission Issues
If you get permission errors:
- Make sure the output directory is writable
- On Windows, try running as Administrator
- Check that Docker has permission to access the directories

## Customizing Analysis

### Environment Variables

You can customize the analysis by setting environment variables:

```bash
# Run with verbose logging
docker run --rm \
  -e VERBOSE=1 \
  -v "/path/to/input:/input" \
  -v "/path/to/output:/output" \
  xsd-visualizer:latest

# Specify output formats
docker run --rm \
  -e FORMATS="html json" \
  -v "/path/to/input:/input" \
  -v "/path/to/output:/output" \
  xsd-visualizer:latest
```

### Advanced Usage

For more control, you can run specific tools:

```bash
# Run only tree visualization
docker run --rm \
  -v "/path/to/input:/input" \
  -v "/path/to/output:/output" \
  xsd-visualizer:latest \
  python3 tree_visualizer.py /input/*.xsd --format console

# Run selective analysis
docker run --rm \
  -v "/path/to/input:/input" \
  -v "/path/to/output:/output" \
  xsd-visualizer:latest \
  python3 selective_analyzer.py /input/*.xsd --elements "book,author"
```

## Performance Notes

- **Large files:** The container handles multi-megabyte XSD files efficiently
- **Multiple files:** All XSD files in the input directory are processed
- **Memory usage:** Complex schemas may require more memory; increase Docker memory limits if needed
- **Output size:** HTML documentation can be large for complex schemas

## Security

- The container runs as a non-root user for security
- Only the input and output directories are accessible to the container
- No network access is required (fully offline operation)

## Support

If you encounter issues:
1. Check the Docker logs for detailed error messages
2. Verify your paths are correct for your operating system
3. Ensure Docker has sufficient resources allocated
4. Try with a simple XSD file first to test the setup
