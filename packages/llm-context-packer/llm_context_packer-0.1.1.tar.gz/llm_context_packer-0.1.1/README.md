# LLM Context Packer

> "Stop manually opening 15 files and copy-pasting them one by one. LLM Context Packer packs your entire codebase into a single AI-ready prompt in <1 second."

**Turn your entire codebase into a single prompt-ready text file.**

## 🚀 Why?
When working with LLMs (ChatGPT, Claude, Gemini), context is everything. You often need to paste multiple files to get a good refactor or answer. Manually copying file content, adding filenames, and formatting is a pain.

**LLM Context Packer** does it for you:
1.  **Traverses** your project.
2.  **Respects** `.gitignore` (no `node_modules`, `.env`, or secrets).
3.  **Formats** everything into an LLM-friendly structure.
4.  **Copies** the result strictly to your clipboard.
5.  **Counts** the tokens so you know if you fit the context window.

## 📦 Installation

```
pip install llm-context-packer
```

Or manually:

```bash
# Clone the repository
git clone https://github.com/overcrash66/LLM_Context_Packer.git
cd LLM_Context_Packer

# Install locally
pip install .
```

## 🛠 Usage

You can use `llm-context-packer`.

### Basic Usage
Run in your project root. It automatically copies to clipboard.
```bash
llm-context-packer .
```

### Options

```bash
# Don't copy to clipboard, just print to stdout
llm-context-packer . --no-copy

# Write to a file instead of clipboard
llm-context-packer . --output context.txt

# Verbose mode (see what files are being packed)
llm-context-packer . --verbose
```

## 📝 Output Format
The tool generates a clean Markdown format that LLMs understand perfectly:

## 🛡 Security
- **Strictly follows `.gitignore`**: If you ignore it in git, it won't be packed.
- **Hidden files ignored**: Skips `.git` directory automatically.
