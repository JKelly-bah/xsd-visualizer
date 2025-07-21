#!/bin/bash

# XSD Visualizer Docker Runner for Git Bash/Linux/macOS
# Usage: ./run-xsd-visualizer.sh "/path/to/xsd/files" "/path/to/output"

set -e

echo "XSD Visualizer Docker Runner"
echo "============================"

# Check if Docker is running
if ! docker version >/dev/null 2>&1; then
    echo "ERROR: Docker is not running or not installed."
    echo "Please start Docker and try again."
    exit 1
fi

# Check arguments
if [ $# -lt 2 ]; then
    echo "Usage: $0 <input_directory> <output_directory>"
    echo ""
    echo "Examples:"
    echo "  $0 \"/c/MyXSDFiles\" \"/c/MyOutput\""
    echo "  $0 \".\" \"./output\""
    echo "  $0 \"./xsd-files\" \"./results\""
    exit 1
fi

INPUT_DIR="$1"
OUTPUT_DIR="$2"

# Convert Windows paths for Git Bash if needed
if [[ "$INPUT_DIR" =~ ^[A-Za-z]: ]]; then
    INPUT_DIR=$(echo "$INPUT_DIR" | sed 's|\\|/|g' | sed 's|^\([A-Za-z]\):|/\L\1|')
fi

if [[ "$OUTPUT_DIR" =~ ^[A-Za-z]: ]]; then
    OUTPUT_DIR=$(echo "$OUTPUT_DIR" | sed 's|\\|/|g' | sed 's|^\([A-Za-z]\):|/\L\1|')
fi

# Convert to absolute paths if relative
if [[ "$INPUT_DIR" != /* ]]; then
    INPUT_DIR="$(pwd)/$INPUT_DIR"
fi

if [[ "$OUTPUT_DIR" != /* ]]; then
    OUTPUT_DIR="$(pwd)/$OUTPUT_DIR"
fi

# Check if input directory exists
if [ ! -d "$INPUT_DIR" ]; then
    echo "ERROR: Input directory does not exist: $INPUT_DIR"
    exit 1
fi

# Create output directory if it doesn't exist
if [ ! -d "$OUTPUT_DIR" ]; then
    echo "Creating output directory: $OUTPUT_DIR"
    mkdir -p "$OUTPUT_DIR"
fi

echo "Input directory: $INPUT_DIR"
echo "Output directory: $OUTPUT_DIR"
echo

# Check if XSD Visualizer image exists, build if not
echo "Checking for XSD Visualizer Docker image..."
if ! docker images xsd-visualizer:latest -q | grep -q .; then
    echo "Building XSD Visualizer Docker image..."
    docker build -t xsd-visualizer:latest .
    echo "Docker image built successfully!"
    echo
fi

# Run the container
echo "Running XSD analysis..."
echo
docker run --rm \
    -v "$INPUT_DIR":/input \
    -v "$OUTPUT_DIR":/output \
    xsd-visualizer:latest

echo
echo "SUCCESS: Analysis complete!"
echo "Results are available in: $OUTPUT_DIR"

# Try to open the output directory (works on Windows with Git Bash)
if command -v explorer.exe >/dev/null 2>&1; then
    echo "Opening output directory..."
    explorer.exe "$(echo "$OUTPUT_DIR" | sed 's|^/\([a-z]\)|\U\1:|' | sed 's|/|\\|g')"
elif command -v open >/dev/null 2>&1; then
    open "$OUTPUT_DIR"
elif command -v xdg-open >/dev/null 2>&1; then
    xdg-open "$OUTPUT_DIR"
fi
