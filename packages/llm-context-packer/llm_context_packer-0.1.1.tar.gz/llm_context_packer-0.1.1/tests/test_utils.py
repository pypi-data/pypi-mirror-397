import tiktoken
from pathlib import Path
from llm_context_packer.utils import count_tokens, format_file_to_markdown

def test_count_tokens():
    text = "Hello world"
    # exact count depends on tokenizer, but should be > 0
    assert count_tokens(text) > 0
    
    # "Hello world" is usually 2 tokens in cl100k_base
    assert count_tokens("Hello world") == 2

def test_format_file_to_markdown(tmp_path):
    f = tmp_path / "test.py"
    f.write_text("print('hello')", encoding="utf-8")
    
    formatted = format_file_to_markdown(f, tmp_path)
    expected = "# File: test.py\n```py\nprint('hello')\n```\n\n"
    assert formatted == expected

def test_format_file_to_markdown_no_ext(tmp_path):
    f = tmp_path / "LICENSE"
    f.write_text("MIT", encoding="utf-8")
    
    formatted = format_file_to_markdown(f, tmp_path)
    # Should default to txt
    assert "```txt" in formatted
