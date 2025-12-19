import os
from pathlib import Path
from typing import List, Generator
import pathspec
from .ignore import get_default_ignore_spec

def collect_files(root_path: Path, ignore_spec: pathspec.PathSpec = None) -> List[Path]:
    """
    Recursively scans the directory and returns a list of file paths to include.
    Respects .gitignore rules if provided.
    """
    if ignore_spec is None:
        ignore_spec = get_default_ignore_spec()
    
    collected_files = []

    # Using os.walk for better control over directory pruning
    for dirpath, dirnames, filenames in os.walk(root_path):
        # 1. Prune ignored directories
        # We need to modify dirnames in-place to prevent os.walk from recursing into them
        # We check each dirname against the ignore spec
        
        # Calculate relative path for the current directory
        rel_dir = Path(dirpath).relative_to(root_path)
        
        # Filter directories
        # We must iterate over a copy of the list because we're modifying it
        for dirname in list(dirnames):
            full_dir_path = rel_dir / dirname
            # gitignore patterns usually need a trailing slash to match directories strictly, 
            # but pathspec often handles it. We'll pass the name as is.
            # However, pathspec matches against the relative path.
            
            # Use match_file for checking logic. 
            # Note: pathspec 'match_file' usually checks if a file matches. 
            # For directories, we often verify if the directory itself is excluded.
            
            # Heuristic: Check if the directory path + '/' matches
            check_path = str(full_dir_path) + "/"
            if ignore_spec.match_file(check_path):
                dirnames.remove(dirname)
                continue
            
            # Special check for .git directory, just in case it's not in the spec (though it should be)
            if dirname == ".git":
                if dirname in dirnames:
                    dirnames.remove(dirname)

        # 2. Filter files
        for filename in filenames:
            rel_file = rel_dir / filename
            if not ignore_spec.match_file(str(rel_file)):
                collected_files.append(root_path / rel_file)
                
    return sorted(collected_files)
