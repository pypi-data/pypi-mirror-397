import pathspec
from pathlib import Path
from llm_context_packer.ignore import get_default_ignore_spec, load_gitignore

def test_default_ignore_spec():
    spec = get_default_ignore_spec()
    assert spec.match_file("venv/")
    assert spec.match_file("__pycache__/")
    assert spec.match_file(".git/")
    assert not spec.match_file("src/main.py")

def test_load_gitignore_valid(tmp_path):
    gitignore = tmp_path / ".gitignore"
    gitignore.write_text("*.log\n/secret")
    
    spec = load_gitignore(tmp_path)
    assert spec is not None
    assert spec.match_file("error.log")
    assert spec.match_file("secret")
    assert not spec.match_file("main.py")

def test_load_gitignore_missing(tmp_path):
    spec = load_gitignore(tmp_path)
    assert spec is None
