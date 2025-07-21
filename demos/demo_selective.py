#!/usr/bin/env python3
"""
Demo script for Selective XSD Analysis
Shows how to cherry-pick specific elements from multiple XSD files.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.selective_xsd_parser import SelectiveXSDParser
from selective_analyzer import SelectiveAnalyzer
from rich.console import Console
from rich.panel import Panel
from rich import print as rprint

console = Console()

def demo_basic_selection():
    """Demo: Select specific elements from our multi-file schema."""
    console.print(Panel(
        "[bold blue]Demo 1: Basic Element Selection[/bold blue]\n"
        "Selecting specific elements from our multi-file schema",
        title="🎯 Selective Analysis Demo"
    ))
    
    analyzer = SelectiveAnalyzer("./output/selective_demo1")
    
    # Select specific elements from library.xsd
    analyzer.add_file_selection(
        file_path="test_multifile/library.xsd",
        elements=["library", "LibraryType", "BookType"]
    )
    
    # Select publisher types from publisher.xsd
    analyzer.add_file_selection(
        file_path="test_multifile/publisher.xsd",
        complex_types=["PublisherType"]
    )
    
    # Analyze and show results
    result = analyzer.analyze()
    analyzer.display_summary()
    
    console.print("\n[green]✓ Demo 1 complete![/green]")
    return result

def demo_namespace_selection():
    """Demo: Select entire namespaces from different files."""
    console.print(Panel(
        "[bold blue]Demo 2: Namespace Selection[/bold blue]\n"
        "Selecting all components from specific namespaces",
        title="🌐 Namespace-Based Selection"
    ))
    
    analyzer = SelectiveAnalyzer("./output/selective_demo2")
    
    # Select everything from the publisher namespace
    analyzer.add_file_selection(
        file_path="test_multifile/publisher.xsd",
        namespaces=["http://example.com/publisher"]
    )
    
    # Select common types from library namespace
    analyzer.add_file_selection(
        file_path="test_multifile/common-types.xsd",
        namespaces=["http://example.com/library"]
    )
    
    # Analyze and show results
    result = analyzer.analyze()
    analyzer.display_summary()
    
    console.print("\n[green]✓ Demo 2 complete![/green]")
    return result

def demo_mixed_selection():
    """Demo: Mix different selection types from multiple files."""
    console.print(Panel(
        "[bold blue]Demo 3: Mixed Selection Strategy[/bold blue]\n"
        "Combining elements, types, and namespaces from different files",
        title="🎭 Advanced Selection"
    ))
    
    analyzer = SelectiveAnalyzer("./output/selective_demo3")
    
    # From library.xsd: select specific elements
    analyzer.add_file_selection(
        file_path="test_multifile/library.xsd",
        elements=["library"],
        complex_types=["BooksType"]
    )
    
    # From common-types.xsd: select specific types
    analyzer.add_file_selection(
        file_path="test_multifile/common-types.xsd",
        complex_types=["AddressType", "PriceType"],
        simple_types=["ISBNType"]
    )
    
    # From publisher.xsd: select by namespace (everything)
    analyzer.add_file_selection(
        file_path="test_multifile/publisher.xsd",
        namespaces=["http://example.com/publisher"]
    )
    
    # Analyze and show results
    result = analyzer.analyze()
    analyzer.display_summary()
    
    # Generate HTML documentation for this selection
    console.print("\n[yellow]Generating HTML documentation...[/yellow]")
    analyzer.generate_html_documentation()
    
    console.print("\n[green]✓ Demo 3 complete with HTML documentation![/green]")
    return result

def demo_api_usage():
    """Demo: Direct API usage for advanced scenarios."""
    console.print(Panel(
        "[bold blue]Demo 4: Direct API Usage[/bold blue]\n"
        "Using the SelectiveXSDParser API directly for custom scenarios",
        title="⚙️ Advanced API"
    ))
    
    # Create parser directly
    parser = SelectiveXSDParser()
    
    # Add multiple selections
    parser.add_file_selection(
        file_path="test_multifile/library.xsd",
        elements=["library"],
        include_dependencies=True
    )
    
    parser.add_file_selection(
        file_path="test_bookstore.xsd",  # Our original test file
        elements=["bookstore"],
        complex_types=["BookType"],
        include_dependencies=False
    )
    
    # Parse selections
    console.print("[yellow]Parsing selections...[/yellow]")
    result = parser.parse_selections()
    
    # Show summary
    summary = parser.get_selection_summary()
    
    console.print("\n[bold]Selection Summary:[/bold]")
    for file_path, details in summary.items():
        console.print(f"\n[cyan]{Path(file_path).name}:[/cyan]")
        console.print(f"  Total selected: {details['total_selected']}")
        if details['elements']:
            console.print(f"  Elements: {', '.join(details['elements'])}")
        if details['complex_types']:
            console.print(f"  Complex types: {', '.join(details['complex_types'])}")
    
    console.print(f"\n[green]✓ Demo 4 complete! Selected {len(parser.selected_components)} components total.[/green]")
    return result

def main():
    """Run all selective analysis demos."""
    console.print(Panel(
        "[bold white]🎯 Selective XSD Analysis - Feature Demo[/bold white]\n\n"
        "This demo shows how to cherry-pick specific elements, types, or entire\n"
        "namespaces from multiple XSD files - perfect for focused analysis!",
        title="✨ New Feature Showcase",
        border_style="bright_blue"
    ))
    
    # Check if our test files exist
    test_files = [
        Path("test_multifile/library.xsd"),
        Path("test_multifile/publisher.xsd"),
        Path("test_multifile/common-types.xsd"),
        Path("test_bookstore.xsd")
    ]
    
    missing_files = [f for f in test_files if not f.exists()]
    if missing_files:
        console.print(f"[red]Missing test files: {[str(f) for f in missing_files]}[/red]")
        console.print("[yellow]Please run the multi-file tests first to create sample schemas.[/yellow]")
        return
    
    try:
        # Run demos
        console.print("\n" + "="*60)
        demo_basic_selection()
        
        console.print("\n" + "="*60)
        demo_namespace_selection()
        
        console.print("\n" + "="*60)
        demo_mixed_selection()
        
        console.print("\n" + "="*60)
        demo_api_usage()
        
        # Final summary
        console.print(Panel(
            "[bold green]🎉 All demos completed successfully![/bold green]\n\n"
            "[white]You can now:[/white]\n"
            "• Use [cyan]selective_analyzer.py[/cyan] for command-line analysis\n"
            "• Import [cyan]SelectiveXSDParser[/cyan] for custom Python scripts\n"
            "• Check [cyan]./output/selective_demo3/html/[/cyan] for generated docs\n"
            "• Mix and match elements from any combination of XSD files!",
            title="🚀 Selective Analysis Ready!",
            border_style="bright_green"
        ))
        
    except Exception as e:
        console.print(f"[red]Demo error: {e}[/red]")
        console.print_exception()

if __name__ == "__main__":
    main()
