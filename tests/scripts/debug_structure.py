#!/usr/bin/env python3
"""Debug script to explore XSD structure."""

import json
from utils.multi_file_xsd_parser import MultiFileXSDParser

def explore_structure():
    """Explore the structure of the test XSD file."""
    parser = MultiFileXSDParser('test_bookstore.xsd')
    data = parser.parse()
    structure = parser.get_structure()
    
    print("=== Schema Data Keys ===")
    print(json.dumps(list(data.keys()), indent=2))
    
    print("\n=== Structure Keys ===")
    print(json.dumps(list(structure.keys()), indent=2))
    
    print("\n=== Elements ===")
    if 'elements' in structure:
        print(f"Elements type: {type(structure['elements'])}")
        if isinstance(structure['elements'], list):
            for i, elem in enumerate(structure['elements']):
                print(f"Element {i}: {json.dumps(elem, indent=2)}")
        else:
            print(json.dumps(structure['elements'], indent=2))
    
    print("\n=== Global Elements ===")
    if 'global_elements' in structure:
        print(f"Global elements type: {type(structure['global_elements'])}")
        if isinstance(structure['global_elements'], list):
            for i, elem in enumerate(structure['global_elements']):
                print(f"Global Element {i}: {json.dumps(elem, indent=2)}")
        else:
            print(json.dumps(structure['global_elements'], indent=2))

    print("\n=== Complex Types ===")
    if 'complex_types' in structure:
        print(f"Complex types type: {type(structure['complex_types'])}")
        if isinstance(structure['complex_types'], dict):
            for name, ct in structure['complex_types'].items():
                print(f"\nComplex Type: {name}")
                print(json.dumps(ct, indent=2)[:1000] + "..." if len(json.dumps(ct, indent=2)) > 1000 else json.dumps(ct, indent=2))
        else:
            print(json.dumps(structure['complex_types'], indent=2)[:2000] + "..." if len(json.dumps(structure['complex_types'], indent=2)) > 2000 else json.dumps(structure['complex_types'], indent=2))

if __name__ == '__main__':
    explore_structure()
