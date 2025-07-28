#!/usr/bin/env python3
"""
XSD to CSV Converter

Converts XSD schemas to CSV format with support for large patterns
including multiple files, complex inheritance, and cross-schema references.

Usage:
    python src/xsd_to_csv/csv_converter.py Collection.xsd -o output.csv
    python src/xsd_to_csv/csv_converter.py Collection.xsd -o output.csv --large
    python src/xsd_to_csv/csv_converter.py Collection.xsd -o output.csv --simple
"""

import sys
import os
import logging
from pathlib import Path

# Add parent directories to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
grandparent_dir = os.path.dirname(parent_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
if grandparent_dir not in sys.path:
    sys.path.insert(0, grandparent_dir)

from xsd_to_csv.xsd_csv_converter import XSDToCSVConverter
from xsd_to_csv.large_xsd_converter import LargeXSDToCSVConverter


def main():
    """Main entry point for CSV conversion."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Convert XSD schemas to CSV format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s test_schemas/Collection.xsd -o output/collection.csv
  %(prog)s test_schemas/Collection.xsd -o output/collection.csv --large
  %(prog)s test_schemas/Collection.xsd -o output/collection.csv --simple -v
        """
    )
    
    parser.add_argument('xsd_file', help='XSD file to convert to CSV')
    parser.add_argument('-o', '--output', required=True, 
                       help='Output CSV file path')
    parser.add_argument('--large', action='store_true',
                       help='Use large converter with detailed analysis')
    parser.add_argument('--simple', action='store_true',
                       help='Use simple analysis (faster, less detailed)')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Validate input file
    if not os.path.isfile(args.xsd_file):
        print(f"Error: XSD file not found: {args.xsd_file}", file=sys.stderr)
        sys.exit(1)
    
    # Set up logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Create output directory if needed
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        print(f"Created output directory: {output_dir}")
    
    try:
        # Choose converter based on arguments
        if args.large:
            print("Using Large XSD to CSV Converter...")
            converter = LargeXSDToCSVConverter()
            stats = converter.convert_large_schema(
                main_xsd_file=args.xsd_file,
                output_file=args.output,
                detailed_analysis=not args.simple
            )
            
            # Print large statistics
            print(f"\n✅ Large CSV conversion complete!")
            print(f"📊 Conversion Statistics:")
            print(f"   • Total rows: {stats['total_rows']}")
            print(f"   • Schema files processed: {stats['schema_files']}")
            print(f"   • Root elements: {stats['root_elements']}")
            print(f"   • Complex types: {stats['complex_types']}")
            print(f"   • Simple types: {stats['simple_types']}")
            print(f"   • Global attributes: {stats['global_attributes']}")
            print(f"   • Local attributes: {stats['local_attributes']}")
            print(f"   • Attribute groups: {stats['attribute_groups']}")
            print(f"   • Inheritance relationships: {stats['inheritance_relationships']}")
            print(f"   • Cross-schema references: {stats['cross_schema_references']}")
            print(f"   • Documented items: {stats['documented_items']}")
            
        else:
            print("Using Standard XSD to CSV Converter...")
            converter = XSDToCSVConverter()
            stats = converter.convert_schema_to_csv(
                xsd_files=[args.xsd_file],
                output_file=args.output
            )
            
            # Print standard statistics
            print(f"\n✅ CSV conversion complete!")
            print(f"📊 Conversion Statistics:")
            print(f"   • Total rows: {stats['total_rows']}")
            print(f"   • Elements: {stats['elements']}")
            print(f"   • Attributes: {stats['attributes']}")
            print(f"   • Types: {stats['types']}")
        
        print(f"📁 Output file: {args.output}")
        
        # Provide additional suggestions
        if stats.get('total_rows', 0) > 100:
            print(f"\n💡 Tips for large schemas:")
            print(f"   • Use --simple for faster processing")
            print(f"   • Open CSV in Excel or LibreOffice for better viewing")
            print(f"   • Use filters to focus on specific categories")
        
        if stats.get('schema_files', 0) > 1:
            print(f"\n🔗 Multi-file schema detected:")
            print(f"   • {stats['schema_files']} schema files were processed")
            print(f"   • Cross-schema references are included in the output")
        
    except Exception as e:
        print(f"❌ Error converting XSD to CSV: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
