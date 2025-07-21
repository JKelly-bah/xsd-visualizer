#!/usr/bin/env python3
"""
XSD Visualization Examples - Demonstrates the capabilities of the toolkit.
"""

import os
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich import print as rprint

console = Console()

def show_welcome():
    """Display welcome message and overview."""
    welcome_text = """
[bold blue]XSD Visualization and Analysis Toolkit[/bold blue]

This toolkit provides comprehensive offline tools for analyzing and visualizing 
large, complex XSD (XML Schema Definition) files.

[bold]Key Features:[/bold]
• Parse and analyze XSD structure and relationships
• Generate interactive HTML documentation
• Create tree visualizations (console, text, SVG)
• Interactive element and type inspection
• Dependency analysis and mapping
• Multiple output formats for different use cases

[bold]Sample XSD File:[/bold]
A test bookstore schema (test_bookstore.xsd) is included to demonstrate the tools.
    """
    
    console.print(Panel(welcome_text, title="Welcome", expand=False))

def show_usage_examples():
    """Display usage examples."""
    examples = [
        {
            "title": "Quick Analysis",
            "description": "Get a quick overview of schema statistics",
            "command": "python xsd_analyzer.py test_bookstore.xsd --summary-only"
        },
        {
            "title": "Generate HTML Documentation",
            "description": "Create comprehensive interactive documentation",
            "command": "python xsd_analyzer.py test_bookstore.xsd --formats html"
        },
        {
            "title": "Console Tree View",
            "description": "Display schema structure as a tree in the terminal",
            "command": "python tree_visualizer.py test_bookstore.xsd --format console"
        },
        {
            "title": "Generate SVG Diagram",
            "description": "Create a visual diagram of the schema structure",
            "command": "python tree_visualizer.py test_bookstore.xsd --format svg --output schema_tree.svg"
        },
        {
            "title": "Inspect Specific Element",
            "description": "Examine a particular element in detail",
            "command": "python element_inspector.py test_bookstore.xsd --element bookstore"
        },
        {
            "title": "Interactive Element Inspector",
            "description": "Start interactive mode for exploring elements",
            "command": "python element_inspector.py test_bookstore.xsd"
        },
        {
            "title": "Complete Analysis",
            "description": "Generate all output formats",
            "command": "python xsd_analyzer.py test_bookstore.xsd --formats html json text"
        }
    ]
    
    console.print("\n[bold cyan]Usage Examples:[/bold cyan]\n")
    
    for i, example in enumerate(examples, 1):
        console.print(f"[bold]{i}. {example['title']}[/bold]")
        console.print(f"   {example['description']}")
        console.print(f"   [dim]{example['command']}[/dim]\n")

def show_vs_code_integration():
    """Show VS Code integration features."""
    vs_code_info = """
[bold]VS Code Integration:[/bold]

This workspace includes:
• XML Language Support extension for XSD editing
• Custom tasks for common operations (Ctrl+Shift+P → "Tasks: Run Task")
• Python environment with all required packages
• Rich terminal output with colors and progress bars

[bold]Available Tasks:[/bold]
• "Analyze XSD File" - Complete analysis with all formats
• "Generate HTML Documentation" - HTML docs only
• "Visualize Tree (Console)" - Console tree display
• "Quick Summary" - Statistics overview

[bold]File Navigation:[/bold]
• Use the Explorer panel to browse generated documentation
• Open HTML files in the Simple Browser for viewing
• XSD files get syntax highlighting and validation
    """
    
    console.print(Panel(vs_code_info, title="VS Code Integration", expand=False))

def show_output_formats():
    """Show available output formats."""
    formats_info = """
[bold]Output Formats:[/bold]

[bold blue]HTML Documentation[/bold blue]
• Interactive web-based documentation
• Cross-linked elements and types
• Search and filtering capabilities
• Mobile-responsive design
• Dependency visualization with D3.js

[bold green]Tree Visualizations[/bold green]
• Console: Colored tree display in terminal
• Text: Plain text tree for documentation
• SVG: Scalable vector graphics for presentations
• DOT: GraphViz format for custom processing

[bold yellow]Data Export[/bold yellow]
• JSON: Machine-readable structure data
• Text: Human-readable summary reports
• Statistics: Quick overview tables

[bold]Use Cases:[/bold]
• Documentation: HTML format for team sharing
• Analysis: JSON format for programmatic processing
• Presentations: SVG format for diagrams
• Debugging: Console format for quick inspection
    """
    
    console.print(Panel(formats_info, title="Output Formats", expand=False))

def main():
    """Main demo function."""
    show_welcome()
    show_usage_examples()
    show_vs_code_integration()
    show_output_formats()
    
    console.print("\n[bold green]Try running one of the example commands above![/bold green]")
    console.print("Start with: [bold]python xsd_analyzer.py test_bookstore.xsd --summary-only[/bold]")

if __name__ == "__main__":
    main()
