# 🚀 ai-md-scaffold

> **Turn AI-generated Markdown into real project files — instantly.**

`ai-md-scaffold` is a lightweight **CLI tool and Python library** that converts **AI-generated Markdown** (from ChatGPT, DeepSeek, Claude, Gemini, etc.) into a **real project directory structure** with actual files.

No more manual copy-paste.  
No cleanup.  
No broken file paths.

---

## ✨ Why ai-md-scaffold?

AI tools are great at generating code — but terrible at delivering it in a usable format.

This tool bridges that gap.

**You give Markdown.  
It creates real files.**

---

## ✨ Features

- ✅ Convert AI Markdown into real files & folders
- ✅ Works with **any AI model**
- ✅ Supports `.env`, `Dockerfile`, config files
- ✅ Safe overwrite handling
- ✅ Dry-run preview mode
- ✅ Works as **CLI** or **Python library**
- ✅ Zero dependencies
- ✅ Stable parsing

---

## 📦 Installation

```bash
pip install ai-md-scaffold
```

Verify installation:

```bash
ai-md-scaffold --version
```

---

## 🚀 Quick Start (CLI)

```bash
ai-md-scaffold project.md
```

### With overwrite

```bash
ai-md-scaffold project.md --overwrite
```

### Preview only (no files written)

```bash
ai-md-scaffold project.md --dry-run
```

---

## 🧠 Supported Markdown Format

Each file **must start with a bold title** representing the file path.

### Example:

````markdown
**src/main.py**

```python
print("Hello, world!")
```

**.env**

```
PORT=3000
DEBUG=true
```

**Dockerfile**

```dockerfile
FROM python:3.11-slim
```
````

> ✅ Files **without code blocks** are still generated  
> ✅ Trailing colons (`:`) are automatically cleaned  
> ❌ Explanations outside file blocks are ignored

---

## 🤖 Recommended AI Prompt (IMPORTANT)

To get perfect results, use this prompt with your AI:

```text
Generate project files using STRICT Markdown rules:

- Each file starts with **relative/path**
- Use fenced code blocks
- No explanations
- No emojis
- No bullet lists
- Markdown ONLY
```

### Example Prompt:

```text
Create a Node.js backend project.
Output Markdown only.
Use **path/file.ext** for each file.
```

---

## 🧩 Python Library Usage

You can also use `ai-md-scaffold` as a Python module:

```python
from ai_md_scaffold import parse_markdown, generate

# Read AI-generated markdown
with open("project.md") as f:
    markdown_text = f.read()

# Parse markdown
files = parse_markdown(markdown_text)

# Generate files
generate(files, root="my_project", overwrite=False, dry_run=False)
```

---

## ⚙️ CLI Options

| Option             | Description                   |
| ------------------ | ----------------------------- |
| `--dry-run`        | Preview files without writing |
| `--overwrite`      | Overwrite existing files      |
| `--no-interactive` | Disable prompts               |
| `--version`        | Show version                  |

---

## 🧪 Example Output

```bash
$ ai-md-scaffold project.md

[INFO] Created: src/main.py
[INFO] Created: .env
[INFO] Created: Dockerfile

Project successfully generated
```

---

## 🛡️ Safety & Stability

- Does **not** execute code
- Does **not** guess file paths
- Does **not** hallucinate structure
- Only uses what exists in Markdown

---

## 📦 Package Details

- **Name:** ai-md-scaffold
- **CLI:** ai-md-scaffold
- **Python import:** ai_md_scaffold
- **Python:** >= 3.8
- **License:** MIT

---

## 🧭 Use Cases

- Generate full-stack projects from DeepSeek, ChatGPT, Claude, Gemini, etc
- Convert AI answers into real repos
- Automate scaffolding
- Developer productivity tooling
- AI-assisted coding workflows

---

## 📜 License

MIT License — free for personal & commercial use.

---

## ❤️ Author Note

This tool exists because AI should **build projects**, not just talk about them.\
If you find this useful — ⭐ star the repo, share it, or build on top of it.\
Happy scaffolding 🚀

---
