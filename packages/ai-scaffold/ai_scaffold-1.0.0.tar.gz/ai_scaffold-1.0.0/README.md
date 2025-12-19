# 🚀 ai-scaffold

> **Turn AI-generated Markdown or JSON into real project files — instantly.**

`ai-scaffold` is a lightweight **CLI tool and Python library** that converts **AI-generated content** (from ChatGPT, DeepSeek, Claude, Gemini, etc.) into a **real project directory structure** with actual files.

No more manual copy-paste.

No cleanup.

No broken file paths.

---

## ✨ Why ai-scaffold?

AI tools are great at generating code — but terrible at delivering it in a usable format.

This tool bridges that gap.

**You give AI output (Markdown/JSON).
It creates real files.**

---

## ✨ Features

- ✅ Convert AI Markdown or JSON into real files & folders
- ✅ **Multi-format Support**: Works with Bold titles (`**file**`), Headers (`### file`), or **Structured JSON**
- ✅ **Smart Cleanup**: Automatically removes emojis (`📁`, `📄`), numbering (`1.`), and comments
- ✅ **Auto-Deduplication**: Handles duplicate filenames by renaming them (e.g., `file_2.js`)
- ✅ Supports `.env`, `Dockerfile`, config files
- ✅ Safe overwrite handling
- ✅ Dry-run preview mode
- ✅ Works as **CLI** or **Python library**
- ✅ Zero dependencies

---

## 📦 Installation

```bash
pip install ai-scaffold

```

Verify installation:

```bash
ai-scaffold --version

```

---

## 🚀 Quick Start (CLI)

### 1. Default Format (Bold Titles)

Best for prompts like _"Use `**path/to/file**` for filenames"_.

```bash
ai-scaffold project.md

```

### 2. Header Format

Best for prompts like _"Use `### path/to/file` for filenames"_. Handles emojis and comments automatically.

```bash
ai-scaffold project.md --format 2

```

### 3. JSON Format (New!)

Best for high-precision scaffolding. Automatically detected for `.json` files.

```bash
ai-scaffold project.json --format 3

```

---

## 🧠 Supported Formats

`ai-scaffold` supports three common AI output styles.

### Format 1: Bold Titles (Default)

Matches files wrapped in bold asterisks `**...**`.

**Input Example:**

````markdown
Here is the **src/main.py** file:

```python
print("Hello")
```
````

### Format 2: Header Titles (`--format 2`)

Matches files in Markdown headers (`#`, `##`, `###`).

**Input Example:**

````markdown
### 📄 package.json (Backend)

```json
{}
```
````

### Format 3: JSON Structure (`--format 3`)

Matches structured JSON data.

**Input Example:**

```json
{
  "project_name": "my-app",
  "files": [
    {
      "path": "main.py",
      "content": "print('hello')"
    }
  ]
}
```

---

## 🤖 Recommended AI Prompt

To get perfect results, append one of these prompts to your AI request:

### Option A (For Default Format)

```text
Output code in Markdown.
IMPORTANT: Precede each code block with the filename in bold, like: **path/to/file.ext**

```

### Option B (For Header Format)

```text
Output code in Markdown.
IMPORTANT: Use headers for filenames, like: ### path/to/file.ext

```

### Option C (For JSON Format)

```text
Output the project structure in a single JSON object:
{ "project_name": "...", "files": [{ "path": "...", "content": "..." }] }

```

---

## 🧩 Python Library Usage

You can use `ai-scaffold` as a Python module.

```python
from ai_scaffold import parse_markdown, parse_json, generate

# For Markdown
with open("project.md") as f:
    files = parse_markdown(f.read(), fmt=1)

# For JSON
with open("project.json") as f:
    files, root = parse_json(f.read())

# Generate files
generate(files, root="my_project", overwrite=False, dry_run=False)

```

---

## ⚙️ CLI Options

| Option             | Description                                     |
| ------------------ | ----------------------------------------------- |
| `--format`         | `1` = Bold (default), `2` = Headers, `3` = JSON |
| `--dry-run`        | Preview files without writing                   |
| `--overwrite`      | Overwrite existing files                        |
| `--no-interactive` | Disable prompts                                 |
| `--version`        | Show version                                    |

---

## 🧪 Example Output

```bash
$ ai-scaffold project.json

Root folder detected: readme-builder
Use this folder? [Y/n] y
[INFO] Created: readme-builder/package.json
[INFO] Created: readme-builder/index.html
[INFO] Created: readme-builder/src/utils/generateMarkdown.js

Project successfully generated

```

---

## 🛡️ Safety & Stability

- Does **not** execute code
- Does **not** guess file paths
- Does **not** hallucinate structure
- Only uses what exists in the input

---

## 📦 Package Details

- **Name:** ai-scaffold
- **CLI:** ai-scaffold
- **Python import:** ai_scaffold
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

This tool exists because AI should **build projects**, not just talk about them.

If you find this useful — ⭐ star the repo, share it, or build on top of it.

Happy scaffolding 🚀
