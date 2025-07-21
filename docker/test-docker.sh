#!/bin/bash

# Test script for Docker setup
# Uses the test_files directory with pre-configured test XSD files

echo "XSD Visualizer Docker Test"
echo "=========================="

# Use the test_files directory structure
INPUT_DIR="./test_files/input"
OUTPUT_DIR="./test_files/output"

# Clean output directory for fresh test
rm -rf "$OUTPUT_DIR"/*
mkdir -p "$OUTPUT_DIR"

# Check if test files exist
if [ ! -d "$INPUT_DIR" ] || [ -z "$(find "$INPUT_DIR" -name "*.xsd" -type f)" ]; then
    echo "❌ No test XSD files found in $INPUT_DIR"
    echo "Setting up test files..."
    
    mkdir -p "$INPUT_DIR"
    
    # Create a simple test XSD if none exist
    cat > "$INPUT_DIR/simple-test.xsd" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema" 
           targetNamespace="http://example.com/library" 
           xmlns:lib="http://example.com/library"
           elementFormDefault="qualified">
  
  <xs:element name="library">
    <xs:annotation>
      <xs:documentation>A library containing multiple books</xs:documentation>
    </xs:annotation>
    <xs:complexType>
      <xs:sequence>
        <xs:element name="book" type="lib:BookType" maxOccurs="unbounded"/>
      </xs:sequence>
      <xs:attribute name="name" type="xs:string" use="required"/>
    </xs:complexType>
  </xs:element>
  
  <xs:complexType name="BookType">
    <xs:annotation>
      <xs:documentation>A book with title, author, and metadata</xs:documentation>
    </xs:annotation>
    <xs:sequence>
      <xs:element name="title" type="xs:string"/>
      <xs:element name="author" type="lib:AuthorType"/>
      <xs:element name="isbn" type="lib:ISBNType"/>
      <xs:element name="publishedDate" type="xs:date" minOccurs="0"/>
      <xs:element name="genre" type="lib:GenreType" maxOccurs="unbounded"/>
    </xs:sequence>
    <xs:attribute name="id" type="xs:ID" use="required"/>
    <xs:attribute name="language" type="xs:language" default="en"/>
  </xs:complexType>
  
  <xs:complexType name="AuthorType">
    <xs:sequence>
      <xs:element name="firstName" type="xs:string"/>
      <xs:element name="lastName" type="xs:string"/>
      <xs:element name="biography" type="xs:string" minOccurs="0"/>
    </xs:sequence>
  </xs:complexType>
  
  <xs:simpleType name="ISBNType">
    <xs:restriction base="xs:string">
      <xs:pattern value="[0-9]{3}-[0-9]{1}-[0-9]{3}-[0-9]{5}-[0-9]{1}"/>
    </xs:restriction>
  </xs:simpleType>
  
  <xs:simpleType name="GenreType">
    <xs:restriction base="xs:string">
      <xs:enumeration value="Fiction"/>
      <xs:enumeration value="Non-Fiction"/>
      <xs:enumeration value="Science Fiction"/>
      <xs:enumeration value="Fantasy"/>
      <xs:enumeration value="Mystery"/>
      <xs:enumeration value="Romance"/>
      <xs:enumeration value="Thriller"/>
      <xs:enumeration value="Biography"/>
      <xs:enumeration value="History"/>
    </xs:restriction>
  </xs:simpleType>
  
</xs:schema>
EOF
    echo "✓ Created comprehensive test XSD file"
fi

echo "Test setup:"
echo "  Input: $INPUT_DIR"
echo "  Output: $OUTPUT_DIR"

# List available test files
echo "  Available XSD files:"
find "$INPUT_DIR" -name "*.xsd" -type f | while read -r file; do
    echo "    - $(basename "$file")"
done
echo

# Build Docker image
echo "Building Docker image..."
if docker build -t xsd-visualizer:latest .; then
    echo "✓ Docker image built successfully"
else
    echo "❌ Failed to build Docker image"
    exit 1
fi

echo

# Run the container
echo "Running XSD analysis..."
if docker run --rm \
    -v "$(pwd)/$INPUT_DIR":/input \
    -v "$(pwd)/$OUTPUT_DIR":/output \
    xsd-visualizer:latest; then
    echo "✓ Analysis completed successfully"
else
    echo "❌ Analysis failed"
    exit 1
fi

echo
echo "Test Results:"
echo "============="

# Check for expected output files
if [ -f "$OUTPUT_DIR/html/index.html" ]; then
    echo "✓ HTML documentation generated"
else
    echo "❌ HTML documentation missing"
fi

if [ -f "$OUTPUT_DIR/structure.json" ]; then
    echo "✓ JSON structure file generated"
else
    echo "❌ JSON structure file missing"
fi

if [ -f "$OUTPUT_DIR/summary.txt" ]; then
    echo "✓ Text summary generated"
else
    echo "❌ Text summary missing"
fi

FILE_COUNT=$(find "$OUTPUT_DIR" -type f | wc -l)
echo "Generated $FILE_COUNT output files total"

echo
echo "🎉 Docker test completed!"
echo "   Test files are in: ./test_files"
echo "   You can open: $OUTPUT_DIR/html/index.html"
echo
echo "To clean up test output, run: rm -rf $OUTPUT_DIR/*"
