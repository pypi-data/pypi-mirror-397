import tiktoken
from pathlib import Path

def count_tokens(text: str, model: str = "gpt-4") -> int:
    """
    Counts the number of tokens in the given text string using tiktoken.
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        # Fallback to cl100k_base (used by gpt-4, gpt-3.5-turbo, text-embedding-ada-002)
        encoding = tiktoken.get_encoding("cl100k_base")
    
    return len(encoding.encode(text))

def format_file_to_markdown(file_path: Path, root_path: Path) -> str:
    """
    Reads a file and formats it into a Markdown code block.
    """
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            
        rel_path = file_path.relative_to(root_path)
        ext = file_path.suffix.lstrip(".")
        if not ext:
            ext = "txt"
            
        # Basic fence guard: if the content contains ```, we might need to escape or increase fence length
        # For MVP, we'll keep it simple.
        
        return f"# File: {rel_path}\n" \
               f"```{ext}\n" \
               f"{content}\n" \
               f"```\n\n"
    except Exception as e:
        return f"# File: {file_path.name} (Error reading file: {e})\n\n"

def generate_tree_structure(files: list[Path], root_path: Path) -> str:
    """
    Generates a simple tree structure string of the included files.
    """
    # Simply listing them for now, tree view is a nice-to-have visual
    rel_paths = [str(f.relative_to(root_path)) for f in files]
    return "<file_structure>\n" + "\n".join(rel_paths) + "\n</file_structure>\n\n"
