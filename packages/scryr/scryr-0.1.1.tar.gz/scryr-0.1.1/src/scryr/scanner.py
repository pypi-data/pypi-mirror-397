"""File system scanner for project exploration."""

from pathlib import Path
from typing import List, Set

# Default ignore patterns
DEFAULT_IGNORE = {
    'venv', '.venv', '__pycache__', '.git', '.idea', '.vscode',
    'node_modules', '.pytest_cache', '.mypy_cache', 'dist', 'build',
    '.egg-info', '.eggs', '.tox', 'htmlcov', '.coverage'
}


class FileNode:
    """Represents a file or directory in the project tree."""
    
    def __init__(self, path: Path, is_dir: bool = False):
        self.path = path
        self.name = path.name
        self.is_dir = is_dir
        self.children: List['FileNode'] = []
        self.description: str = ""
    
    def add_child(self, node: 'FileNode') -> None:
        self.children.append(node)
    
    def sort_children(self) -> None:
        """Sort children: directories first, then files alphabetically."""
        self.children.sort(key=lambda n: (not n.is_dir, n.name.lower()))
        for child in self.children:
            if child.is_dir:
                child.sort_children()


def should_ignore(path: Path, ignore_patterns: Set[str]) -> bool:
    """Check if path should be ignored."""
    return path.name in ignore_patterns


def scan_directory(
    root_path: Path,
    ignore_patterns: Set[str] = None,
    max_depth: int = None,
    current_depth: int = 0
) -> FileNode:
    """
    Recursively scan directory and build file tree.
    
    Args:
        root_path: Root directory to scan
        ignore_patterns: Set of folder/file names to ignore
        max_depth: Maximum recursion depth (None for unlimited)
        current_depth: Current recursion depth (internal use)
    
    Returns:
        FileNode representing the root of the scanned tree
    """
    if ignore_patterns is None:
        ignore_patterns = DEFAULT_IGNORE
    
    if not root_path.exists():
        raise FileNotFoundError(f"Path does not exist: {root_path}")
    
    if not root_path.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {root_path}")
    
    root_node = FileNode(root_path, is_dir=True)
    
    if max_depth is not None and current_depth >= max_depth:
        return root_node
    
    try:
        items = sorted(root_path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
    except PermissionError:
        return root_node
    
    for item in items:
        if should_ignore(item, ignore_patterns):
            continue
        
        if item.is_dir():
            child_node = scan_directory(
                item,
                ignore_patterns,
                max_depth,
                current_depth + 1
            )
            root_node.add_child(child_node)
        elif item.is_file():
            file_node = FileNode(item, is_dir=False)
            root_node.add_child(file_node)
    
    root_node.sort_children()
    return root_node