from pathlib import Path
from llm_context_packer.core import collect_files
from llm_context_packer.ignore import get_default_ignore_spec
import pathspec

def test_collect_files_basic(tmp_path):
    (tmp_path / "file1.py").touch()
    (tmp_path / "file2.txt").touch()
    (tmp_path / "ignored.pyc").touch()
    
    # Create default ignore spec
    spec = get_default_ignore_spec()
    
    files = collect_files(tmp_path, spec)
    filenames = [f.name for f in files]
    
    assert "file1.py" in filenames
    assert "file2.txt" in filenames
    assert "ignored.pyc" not in filenames

def test_collect_files_nested(tmp_path):
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "nested.py").touch()
    
    files = collect_files(tmp_path, get_default_ignore_spec())
    # Should contain path relative to root? calculate relative names for assertion
    rel_paths = [str(f.relative_to(tmp_path)).replace("\\", "/") for f in files]
    
    assert "sub/nested.py" in rel_paths

def test_collect_files_ignore_directory(tmp_path):
    venv = tmp_path / "venv"
    venv.mkdir()
    (venv / "lib.py").touch()
    
    (tmp_path / "main.py").touch()
    
    files = collect_files(tmp_path, get_default_ignore_spec())
    filenames = [f.name for f in files]
    
    assert "main.py" in filenames
    assert "lib.py" not in filenames
