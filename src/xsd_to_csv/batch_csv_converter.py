#!/usr/bin/env python3
"""
Batch XSD to CSV Converter

Processes multiple XSD files and creates comprehensive CSV reports.
Works autonomously without user input.
"""

import os
import sys
import glob
import json
from pathlib import Path
import subprocess


def run_csv_conversion(xsd_file: str, output_dir: str) -> dict:
    """Run CSV conversion for a single XSD file."""
    base_name = Path(xsd_file).stem
    output_file = os.path.join(output_dir, f"{base_name}.csv")
    
    print(f"🔄 Converting {xsd_file} -> {output_file}")
    
    # Run the simple CSV converter
    simple_converter_path = os.path.join(os.path.dirname(__file__), 'simple_csv_converter.py')
    cmd = [
        'python3', simple_converter_path,
        xsd_file,
        '-o', output_file,
        '-v'
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # Parse statistics from output
        stats = {'success': True, 'output': result.stdout, 'error': ''}
        
        # Extract statistics from stdout
        for line in result.stdout.split('\n'):
            if 'Total rows:' in line:
                stats['total_rows'] = int(line.split(':')[1].strip())
            elif 'Elements:' in line:
                stats['elements'] = int(line.split(':')[1].strip())
            elif 'Complex types:' in line:
                stats['complex_types'] = int(line.split(':')[1].strip())
            elif 'Simple types:' in line:
                stats['simple_types'] = int(line.split(':')[1].strip())
            elif 'Attributes:' in line:
                stats['attributes'] = int(line.split(':')[1].strip())
            elif 'Documented items:' in line:
                stats['documented_items'] = int(line.split(':')[1].strip())
        
        return stats
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error converting {xsd_file}: {e}")
        return {
            'success': False,
            'output': e.stdout,
            'error': e.stderr
        }


def main():
    """Main batch processing function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Batch convert XSD files to CSV')
    parser.add_argument('--schema-dir', default='test_schemas', 
                       help='Directory containing XSD files (default: test_schemas)')
    parser.add_argument('--output-dir', default='output/csv_batch',
                       help='Output directory for CSV files (default: output/csv_batch)')
    
    args = parser.parse_args()
    
    print("🚀 Starting Batch XSD to CSV Conversion")
    print("=" * 50)
    
    # Configuration
    schema_dir = args.schema_dir
    output_dir = args.output_dir
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Find all XSD files
    xsd_pattern = os.path.join(schema_dir, "*.xsd")
    xsd_files = glob.glob(xsd_pattern)
    
    if not xsd_files:
        print(f"❌ No XSD files found in {schema_dir}")
        sys.exit(1)
    
    print(f"📁 Found {len(xsd_files)} XSD files:")
    for xsd_file in xsd_files:
        print(f"   • {xsd_file}")
    print()
    
    # Process each file
    results = {}
    total_stats = {
        'files_processed': 0,
        'files_successful': 0,
        'files_failed': 0,
        'total_rows': 0,
        'total_elements': 0,
        'total_complex_types': 0,
        'total_simple_types': 0,
        'total_attributes': 0,
        'total_documented_items': 0
    }
    
    for xsd_file in sorted(xsd_files):
        base_name = Path(xsd_file).stem
        stats = run_csv_conversion(xsd_file, output_dir)
        results[base_name] = stats
        
        total_stats['files_processed'] += 1
        
        if stats.get('success', False):
            total_stats['files_successful'] += 1
            total_stats['total_rows'] += stats.get('total_rows', 0)
            total_stats['total_elements'] += stats.get('elements', 0)
            total_stats['total_complex_types'] += stats.get('complex_types', 0)
            total_stats['total_simple_types'] += stats.get('simple_types', 0)
            total_stats['total_attributes'] += stats.get('attributes', 0)
            total_stats['total_documented_items'] += stats.get('documented_items', 0)
            print(f"   ✅ Success: {stats.get('total_rows', 0)} rows")
        else:
            total_stats['files_failed'] += 1
            print(f"   ❌ Failed")
        
        print()
    
    # Save detailed results
    results_file = os.path.join(output_dir, "batch_conversion_results.json")
    with open(results_file, 'w') as f:
        json.dump({
            'total_stats': total_stats,
            'file_results': results
        }, f, indent=2)
    
    # Create summary report
    summary_file = os.path.join(output_dir, "batch_summary.txt")
    with open(summary_file, 'w') as f:
        f.write("XSD to CSV Batch Conversion Summary\n")
        f.write("=" * 40 + "\n\n")
        f.write(f"Files processed: {total_stats['files_processed']}\n")
        f.write(f"Successful conversions: {total_stats['files_successful']}\n")
        f.write(f"Failed conversions: {total_stats['files_failed']}\n\n")
        f.write("Aggregate Statistics:\n")
        f.write(f"Total CSV rows: {total_stats['total_rows']}\n")
        f.write(f"Total elements: {total_stats['total_elements']}\n")
        f.write(f"Total complex types: {total_stats['total_complex_types']}\n")
        f.write(f"Total simple types: {total_stats['total_simple_types']}\n")
        f.write(f"Total attributes: {total_stats['total_attributes']}\n")
        f.write(f"Total documented items: {total_stats['total_documented_items']}\n\n")
        
        f.write("Individual File Results:\n")
        f.write("-" * 25 + "\n")
        for base_name, stats in results.items():
            f.write(f"\n{base_name}.xsd:\n")
            if stats.get('success', False):
                f.write(f"  Status: SUCCESS\n")
                f.write(f"  Rows: {stats.get('total_rows', 0)}\n")
                f.write(f"  Elements: {stats.get('elements', 0)}\n")
                f.write(f"  Complex types: {stats.get('complex_types', 0)}\n")
                f.write(f"  Simple types: {stats.get('simple_types', 0)}\n")
                f.write(f"  Attributes: {stats.get('attributes', 0)}\n")
                f.write(f"  Documented: {stats.get('documented_items', 0)}\n")
            else:
                f.write(f"  Status: FAILED\n")
                f.write(f"  Error: {stats.get('error', 'Unknown error')}\n")
    
    # Print final summary
    print("🎉 Batch Processing Complete!")
    print("=" * 30)
    print(f"📊 Summary Statistics:")
    print(f"   • Files processed: {total_stats['files_processed']}")
    print(f"   • Successful: {total_stats['files_successful']}")
    print(f"   • Failed: {total_stats['files_failed']}")
    print(f"   • Total CSV rows: {total_stats['total_rows']}")
    print(f"   • Total elements: {total_stats['total_elements']}")
    print(f"   • Total complex types: {total_stats['total_complex_types']}")
    print(f"   • Total simple types: {total_stats['total_simple_types']}")
    print(f"   • Total attributes: {total_stats['total_attributes']}")
    print(f"   • Total documented items: {total_stats['total_documented_items']}")
    print()
    print(f"📁 Output directory: {output_dir}")
    print(f"📄 Summary report: {summary_file}")
    print(f"📋 Detailed results: {results_file}")
    
    # List all generated CSV files
    csv_files = glob.glob(os.path.join(output_dir, "*.csv"))
    if csv_files:
        print(f"\n📑 Generated CSV Files:")
        for csv_file in sorted(csv_files):
            file_size = os.path.getsize(csv_file)
            print(f"   • {os.path.basename(csv_file)} ({file_size:,} bytes)")
    
    print(f"\n✅ All processing complete - ready for your other computer!")


if __name__ == '__main__':
    main()
