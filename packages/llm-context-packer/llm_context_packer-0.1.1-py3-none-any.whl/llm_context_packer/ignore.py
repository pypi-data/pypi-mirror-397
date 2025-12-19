import pathspec
from pathlib import Path
from typing import List, Optional

def load_gitignore(root_dir: Path) -> Optional[pathspec.PathSpec]:
    """
    Loads .gitignore from the root directory and returns a PathSpec object.
    If no .gitignore exists, returns None.
    """
    gitignore_path = root_dir / ".gitignore"
    if not gitignore_path.exists():
        return None

    with open(gitignore_path, "r", encoding="utf-8") as f:
        spec = pathspec.PathSpec.from_lines("gitwildmatch", f)
    return spec

def get_default_ignore_spec() -> pathspec.PathSpec:
    """
    Returns a default PathSpec for common patterns to ignore if no .gitignore is found.
    """
    patterns = [
        ".git/",
        "__pycache__/",
        "node_modules/",
        "venv/",
        ".env",
        ".venv/",
        "dist/",
        "build/",
        "*.pyc",
        "*.egg-info/",
    ]
    return pathspec.PathSpec.from_lines("gitwildmatch", patterns)
