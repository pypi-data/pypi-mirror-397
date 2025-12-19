"""Command-line interface for ProjectMapper."""

import sys
from pathlib import Path
from typing import Optional, Set
import argparse

from rich.console import Console

from .scanner import scan_directory, DEFAULT_IGNORE
from .analyzer import analyze_file
from .renderer import render_tree


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        prog="scryr",
        description="A minimal yet intelligent project structure mapper",
        epilog="Example: scryr . --depth 3"
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
        help="Maximum depth to traverse (default: unlimited)"
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
        "--version",
        action="version",
        version="%(prog)s 0.1.0"
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
    
    # Resolve target path
    target_path = Path(args.path).resolve()
    
    # Validate path
    if not target_path.exists():
        console.print(f"[red]Error:[/red] Path does not exist: {target_path}", style="bold")
        return 1
    
    if not target_path.is_dir():
        console.print(f"[red]Error:[/red] Path is not a directory: {target_path}", style="bold")
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
        console.print()  # Empty line for spacing
        render_tree(tree, console)
        console.print()  # Empty line for spacing
        
        return 0
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
        return 130
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        return 1


if __name__ == "__main__":
    sys.exit(main())