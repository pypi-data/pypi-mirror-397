"""Command-line interface for Scryr."""

import sys
from pathlib import Path
from typing import Optional, Set
import argparse

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table

from .scanner import scan_directory, DEFAULT_IGNORE
from .analyzer import analyze_file
from .renderer import render_tree


class RichHelpFormatter(argparse.HelpFormatter):
    """Custom formatter for rich help output."""
    
    def __init__(self, prog):
        super().__init__(prog, max_help_position=35, width=100)


def print_help(console: Console) -> None:
    """Print beautiful help message using Rich."""
    
    # Header
    title = Text("scryr", style="bold cyan")
    subtitle = Text("A minimal yet intelligent project structure mapper", style="dim")
    
    header = Text()
    header.append(title)
    header.append("\n")
    header.append(subtitle)
    
    console.print(Panel(header, border_style="cyan", padding=(1, 2)))
    console.print()
    
    # Usage
    console.print("[bold]USAGE[/bold]")
    console.print("  scryr [PATH] [OPTIONS]", style="dim")
    console.print()
    
    # Arguments table
    args_table = Table(show_header=False, box=None, padding=(0, 2))
    args_table.add_column(style="cyan", width=25)
    args_table.add_column(style="dim")
    
    args_table.add_row("PATH", "Project directory (default: current)")
    
    console.print("[bold]ARGUMENTS[/bold]")
    console.print(args_table)
    console.print()
    
    # Options table
    opts_table = Table(show_header=False, box=None, padding=(0, 2))
    opts_table.add_column(style="cyan", width=25)
    opts_table.add_column(style="dim")
    
    opts_table.add_row("-d, --depth N", "Maximum depth to traverse")
    opts_table.add_row("-i, --ignore PATTERN", "Add patterns to ignore")
    opts_table.add_row("--no-description", "Hide file descriptions")
    opts_table.add_row("-h, --help", "Show this help message")
    opts_table.add_row("--version", "Show version number")
    
    console.print("[bold]OPTIONS[/bold]")
    console.print(opts_table)
    console.print()
    
    # Examples
    console.print("[bold]EXAMPLES[/bold]")
    examples = [
        ("scryr", "Map current directory"),
        ("scryr /path/to/project", "Map specific directory"),
        ("scryr . --depth 3", "Limit tree depth"),
        ("scryr . --no-description", "Show structure only"),
        ("scryr . -i logs -i temp", "Ignore custom patterns"),
    ]
    
    for cmd, desc in examples:
        console.print(f"  [cyan]{cmd:<35}[/cyan] [dim]{desc}[/dim]")
    
    console.print()


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        prog="scryr",
        add_help=False,  # We'll handle help ourselves
        description="A minimal yet intelligent project structure mapper",
    )
    
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to project directory (default: current directory)"
    )
    
    parser.add_argument(
        "-d", "--depth",
        type=int,
        default=None,
        metavar="N",
        help="Maximum depth to traverse"
    )
    
    parser.add_argument(
        "-i", "--ignore",
        action="append",
        default=[],
        metavar="PATTERN",
        help="Additional patterns to ignore (can be used multiple times)"
    )
    
    parser.add_argument(
        "--no-description",
        action="store_true",
        help="Hide file descriptions"
    )
    
    parser.add_argument(
        "-h", "--help",
        action="store_true",
        help="Show this help message"
    )
    
    parser.add_argument(
        "--version",
        action="store_true",
        help="Show version number"
    )
    
    return parser.parse_args()


def analyze_tree(node, show_descriptions: bool = True) -> None:
    """Recursively analyze all files in the tree."""
    if not node.is_dir and show_descriptions:
        node.description = analyze_file(node.path)
    
    for child in node.children:
        analyze_tree(child, show_descriptions)


def main() -> int:
    """Main entry point for the CLI."""
    args = parse_args()
    console = Console()
    
    # Handle help
    if args.help:
        print_help(console)
        return 0
    
    # Handle version
    if args.version:
        console.print("scryr [cyan]0.1.0[/cyan]")
        return 0
    
    # Resolve target path
    target_path = Path(args.path).resolve()
    
    # Validate path
    if not target_path.exists():
        console.print(f"[red]✗[/red] Path does not exist: [dim]{target_path}[/dim]")
        return 1
    
    if not target_path.is_dir():
        console.print(f"[red]✗[/red] Path is not a directory: [dim]{target_path}[/dim]")
        return 1
    
    # Build ignore set
    ignore_patterns: Set[str] = DEFAULT_IGNORE.copy()
    if args.ignore:
        ignore_patterns.update(args.ignore)
    
    try:
        # Scan directory
        tree = scan_directory(
            target_path,
            ignore_patterns=ignore_patterns,
            max_depth=args.depth
        )
        
        # Analyze files
        analyze_tree(tree, show_descriptions=not args.no_description)
        
        # Render tree
        console.print()
        render_tree(tree, console)
        console.print()
        
        return 0
        
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠[/yellow] Interrupted by user")
        return 130
    except Exception as e:
        console.print(f"[red]✗[/red] {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())