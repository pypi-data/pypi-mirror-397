"""Tree rendering with Rich for beautiful terminal output."""

from typing import List
from rich.console import Console
from rich.text import Text
from .scanner import FileNode


class TreeRenderer:
    """Renders file tree with Unicode box characters."""
    
    # Unicode box drawing characters
    PIPE = "│"
    TEE = "├──"
    ELBOW = "└──"
    SPACE = "    "
    
    def __init__(self, console: Console = None):
        self.console = console or Console()
        self.lines: List[Text] = []
    
    def _render_node(
        self,
        node: FileNode,
        prefix: str = "",
        is_last: bool = True,
        is_root: bool = True
    ) -> None:
        """Recursively render a node and its children."""
        
        if is_root:
            # Root node - just the name
            root_text = Text(f"{node.name}/", style="bold cyan")
            self.lines.append(root_text)
        else:
            # Connector
            connector = self.ELBOW if is_last else self.TEE
            line = Text(prefix + connector + " ")
            
            # File/folder name
            if node.is_dir:
                line.append(f"{node.name}/", style="bold cyan")
            else:
                line.append(node.name, style="default")
            
            # Description
            if node.description:
                line.append(f"  # {node.description}", style="dim")
            
            self.lines.append(line)
        
        # Render children
        if node.children:
            for i, child in enumerate(node.children):
                is_last_child = (i == len(node.children) - 1)
                
                # Calculate prefix for children
                if is_root:
                    child_prefix = ""
                else:
                    if is_last:
                        child_prefix = prefix + self.SPACE
                    else:
                        child_prefix = prefix + self.PIPE + "   "
                
                self._render_node(
                    child,
                    prefix=child_prefix,
                    is_last=is_last_child,
                    is_root=False
                )
    
    def render(self, tree: FileNode) -> None:
        """Render the tree to console."""
        self.lines = []
        self._render_node(tree)
        
        # Print all lines
        for line in self.lines:
            self.console.print(line)


def render_tree(tree: FileNode, console: Console = None) -> None:
    """
    Render a file tree to the terminal.
    
    Args:
        tree: Root FileNode to render
        console: Rich Console instance (optional)
    """
    renderer = TreeRenderer(console)
    renderer.render(tree)