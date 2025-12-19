from setuptools import setup, find_packages

setup(
    name="llm-context-packer",
    version="0.1.1",
    packages=find_packages(),
    install_requires=[
        "typer[all]>=0.9.0",
        "tiktoken>=0.5.0",
        "pathspec>=0.11.0",
        "pyperclip>=1.8.2",
    ],
    entry_points={
        "console_scripts": [
            "llm-context-packer=llm_context_packer.main:app",
        ],
    },
)
