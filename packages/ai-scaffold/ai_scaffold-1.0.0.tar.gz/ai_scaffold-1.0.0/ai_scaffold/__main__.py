import argparse
import json
from pathlib import Path
from .parser import parse_markdown, parse_json
from .generator import generate
from . import __version__

def ask(question, default="y"):
    prompt = " [Y/n] " if default.lower() == "y" else " [y/N] "
    ans = input(question + prompt).strip().lower()
    return default.lower() == "y" if not ans else ans in ("y", "yes")

def detect_root(md_text):
    import re
    match = re.search(r"```([\s\S]+?)```", md_text)
    if not match: return None
    for line in match.group(1).splitlines():
        if line.strip().endswith("/"): return line.strip().rstrip("/")
    return None

def main():
    parser = argparse.ArgumentParser(
        prog="ai-scaffold",
        description="Generate project files from AI-generated Markdown or JSON"
    )
    parser.add_argument("input", nargs="+", help="Markdown or JSON file(s)")
    parser.add_argument("--format", type=int, choices=[1, 2, 3], default=1, 
                        help="Format: 1=Bold, 2=Header, 3=JSON")
    parser.add_argument("--dry-run", action="store_true", help="Preview only")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite files")
    parser.add_argument("--no-interactive", action="store_true", help="Disable prompts")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    args = parser.parse_args()
    combined = ""
    for file_path in args.input:
        combined += Path(file_path).read_text(encoding="utf-8") + "\n"

    files = []
    root_path = "."
    
    # Auto-detect JSON if format is 3 or extension is .json
    is_json = args.format == 3 or any(Path(p).suffix == '.json' for p in args.input)

    if is_json:
        files, detected_root = parse_json(combined)
        if detected_root: root_path = detected_root
    else:
        files = parse_markdown(combined, fmt=args.format)
        detected_root = detect_root(combined)
        if detected_root: root_path = detected_root

    if not files:
        print(f"[ERROR] No files detected")
        return

    if not args.no_interactive and root_path != ".":
        print(f"Root folder detected: {root_path}")
        if not ask("Use this folder?", "y"):
            root_path = "."

    generate(files, root=root_path, overwrite=args.overwrite, dry_run=args.dry_run)

if __name__ == "__main__":
    main()