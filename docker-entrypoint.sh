#!/bin/bash

# Docker entry point script for XSD Visualizer
# Processes XSD files from input directory and outputs to output directory

set -e

INPUT_DIR="/input"
OUTPUT_DIR="/output"

# Default values for customization
FORMATS="${FORMATS:-html json text}"
VERBOSE="${VERBOSE:-0}"

echo "XSD Visualizer Docker Container"
echo "==============================="

# Check if input directory is mounted
if [ ! -d "$INPUT_DIR" ]; then
    echo "Error: Input directory $INPUT_DIR not found."
    echo "Please mount your XSD files directory to $INPUT_DIR"
    exit 1
fi

# Check if output directory is mounted
if [ ! -d "$OUTPUT_DIR" ]; then
    echo "Error: Output directory $OUTPUT_DIR not found."
    echo "Please mount your output directory to $OUTPUT_DIR"
    exit 1
fi

# Find all XSD files in input directory (recursive)
echo "Searching for XSD files in $INPUT_DIR..."
XSD_FILES=$(find "$INPUT_DIR" -name "*.xsd" -type f | sort)

if [ -z "$XSD_FILES" ]; then
    echo "No XSD files found in $INPUT_DIR"
    echo "Make sure your directory contains files with .xsd extension"
    exit 1
fi

echo "Found XSD files:"
echo "$XSD_FILES" | while read -r file; do
    echo "  - $(basename "$file")"
done
echo

# Prepare command arguments
ARGS=""
if [ "$VERBOSE" = "1" ]; then
    ARGS="$ARGS --verbose"
fi

# Process XSD files
cd /app
echo "Running analysis with formats: $FORMATS"
echo "Command: python3 xsd_analyzer.py --output-dir $OUTPUT_DIR --formats $FORMATS $ARGS [XSD files]"
echo

# Convert newline-separated list to space-separated for command line
XSD_FILES_ARGS=$(echo "$XSD_FILES" | tr '\n' ' ')

# Run the analyzer
python3 xsd_analyzer.py $XSD_FILES_ARGS --output-dir "$OUTPUT_DIR" --formats $FORMATS $ARGS

echo
echo "Generating SVG tree diagrams with cross-file dependencies..."
echo "$XSD_FILES" | while read -r xsd_file; do
    if [ -n "$xsd_file" ]; then
        filename=$(basename "$xsd_file" .xsd)
        echo "  Creating SVG for $(basename "$xsd_file")..."
        
        # Try multi-file parsing first for cross-file dependencies
        python3 -c "
import sys
sys.path.insert(0, '/app/utils')
from tree_visualizer import TreeVisualizer
from multi_file_xsd_parser import MultiFileXSDParser

try:
    # Use multi-file parser to capture cross-file relationships
    parser = MultiFileXSDParser('$xsd_file')
    visualizer = TreeVisualizer('$xsd_file')
    visualizer.parser = parser
    visualizer.structure = parser.parse()
    visualizer.export_svg('$OUTPUT_DIR/${filename}_tree.svg')
except Exception as e:
    print(f'Multi-file parsing failed, falling back to single-file: {e}')
    # Fallback to regular tree visualizer
    visualizer = TreeVisualizer('$xsd_file')
    visualizer.load_schema()
    visualizer.export_svg('$OUTPUT_DIR/${filename}_tree.svg')
" || echo "    Warning: SVG generation failed for $xsd_file"
    fi
done

echo
echo "Processing complete! Check the output directory for results."
echo

# Show generated files
FILE_COUNT=$(find "$OUTPUT_DIR" -type f | wc -l)
echo "Generated $FILE_COUNT files:"

if [ "$FILE_COUNT" -le 20 ]; then
    find "$OUTPUT_DIR" -type f | while read -r file; do
        echo "  - ${file#$OUTPUT_DIR/}"
    done
else
    find "$OUTPUT_DIR" -type f | head -15 | while read -r file; do
        echo "  - ${file#$OUTPUT_DIR/}"
    done
    echo "  ... and $((FILE_COUNT - 15)) more files"
fi

# Show main entry points
echo
if [ -f "$OUTPUT_DIR/html/index.html" ]; then
    echo "📄 Main HTML documentation: output/html/index.html"
fi
if [ -f "$OUTPUT_DIR/structure.json" ]; then
    echo "📊 JSON structure: output/structure.json"
fi
if [ -f "$OUTPUT_DIR/summary.txt" ]; then
    echo "📋 Text summary: output/summary.txt"
fi

# Show SVG files
SVG_COUNT=$(find "$OUTPUT_DIR" -name "*.svg" -type f | wc -l)
if [ "$SVG_COUNT" -gt 0 ]; then
    echo "🎨 SVG diagrams created:"
    find "$OUTPUT_DIR" -name "*.svg" -type f | while read -r svg_file; do
        echo "   - ${svg_file#$OUTPUT_DIR/}"
    done
fi
