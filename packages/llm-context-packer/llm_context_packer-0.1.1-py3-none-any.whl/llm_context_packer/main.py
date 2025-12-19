import typer
import pyperclip
from pathlib import Path
from typing import Optional
from typing_extensions import Annotated
from .ignore import load_gitignore
from .core import collect_files
from .utils import count_tokens, format_file_to_markdown, generate_tree_structure

app = typer.Typer(help="Turn your entire codebase into a single prompt-ready text file.")

@app.command()
def pack(
    path: Annotated[Path, typer.Argument(exists=True, help="Path to the project directory")] = Path("."),
    copy: bool = typer.Option(True, "--copy/--no-copy", help="Copy the output to clipboard automatically."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed output."),
    output_file: Optional[Path] = typer.Option(None, "--output", "-o", help="Write output to a file instead of stdout/clipboard."),
):
    """
    Pack the codebase into a single context string.
    """
    root_path = path.resolve()
    
    if verbose:
        typer.echo(f"Scanning directory: {root_path}")
    
    # Load .gitignore
    ignore_spec = load_gitignore(root_path)
    if ignore_spec and verbose:
        typer.echo("Loaded .gitignore rules.")
    
    # Collect files
    files = collect_files(root_path, ignore_spec)
    
    if not files:
        typer.echo(f"No files found in {root_path} (check your .gitignore?)", err=True)
        raise typer.Exit(code=1)
    
    if verbose:
        typer.echo(f"Found {len(files)} files.")

    # Generate content
    full_content = []
    
    # Add project overview/tree
    full_content.append(generate_tree_structure(files, root_path))
    
    # Add file contents
    for file_path in files:
        if verbose:
            typer.echo(f"Packing: {file_path.relative_to(root_path)}")
        full_content.append(format_file_to_markdown(file_path, root_path))
    
    final_output = "".join(full_content)
    
    # Count tokens
    token_count = count_tokens(final_output)
    
    typer.echo(f"\n--- Packing Complete ---")
    typer.echo(f"Total Files: {len(files)}")
    typer.echo(f"Total Tokens: {token_count}")
    
    # Handle Output
    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(final_output)
        typer.echo(f"Output written to: {output_file}")
    
    if copy:
        try:
            pyperclip.copy(final_output)
            typer.echo("✅ Copied to clipboard!")
        except Exception as e:
            typer.echo(f"⚠️ Could not copy to clipboard: {e}")
            if not output_file:
                 typer.echo("Printing output to stdout instead:")
                 print(final_output)

if __name__ == "__main__":
    app()
