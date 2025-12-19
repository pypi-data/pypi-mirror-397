import re
import json
from pathlib import Path

# Format 1 & 2 Regex
FMT1_TITLE_RE = re.compile(r".*?\*\*(.+?)\*\*.*")
FMT2_TITLE_RE = re.compile(r"^#{1,6}\s+(.+?)$")
CODE_BLOCK_RE = re.compile(r"^```")

KNOWN_FILES = {
    "dockerfile", "makefile", "jenkinsfile", "procfile", 
    "license", "readme", "changelog", ".gitignore", ".env", ".dockerignore"
}

def normalize_title(title: str) -> str:
    title = title.replace("`", "").replace("*", "")
    return title.rstrip(":").strip()

def is_likely_file(path_str: str) -> bool:
    if not path_str: return False
    path = path_str.lower()
    name = path.split("/")[-1]
    if name in KNOWN_FILES or path in KNOWN_FILES: return True
    if "." in name and not name.endswith("."): return True
    if "/" in path_str or "\\" in path_str: return True
    return False

def get_clean_token(text: str) -> str:
    if not text: return None
    text = text.replace("`", "").replace("*", "").strip()
    tokens = text.split()
    valid_tokens = [t for t in tokens if any(c.isalnum() for c in t)]
    return valid_tokens[0] if len(valid_tokens) == 1 else None

def parse_json(json_text: str):
    try:
        data = json.loads(json_text)
        files = []
        # Support format: { "files": [ { "path": "...", "content": "..." } ] }
        for f in data.get("files", []):
            path = f.get("path")
            content = f.get("content", "")
            if path:
                files.append((path, content))
        return files, data.get("project_name")
    except json.JSONDecodeError:
        return [], None

def parse_markdown(md_text: str, fmt: int = 1):
    files = []
    seen_paths = set()
    current = None
    in_code = False
    buf = []

    title_re = FMT1_TITLE_RE if fmt == 1 else FMT2_TITLE_RE

    for line in md_text.splitlines():
        if not in_code:
            match = title_re.match(line.strip())
            if match:
                raw_title = match.group(1)
                candidate = None
                if fmt == 2:
                    raw_title = re.sub(r"^\d+\.\s+", "", raw_title)
                    paren_match = re.search(r"\(([^)]+)\)", raw_title)
                    inside_text = paren_match.group(1) if paren_match else ""
                    outside_text = re.sub(r"\([^)]+\)", "", raw_title)
                    cand_inside = get_clean_token(inside_text)
                    cand_outside = get_clean_token(outside_text)
                    candidate = cand_inside if (cand_inside and is_likely_file(cand_inside)) else cand_outside
                else:
                    raw_title = re.sub(r"^\d+\.\s+", "", raw_title)
                    if "(" in raw_title: raw_title = raw_title.split("(")[0]
                    candidate = raw_title

                if candidate:
                    cleaned = normalize_title(candidate)
                    current = cleaned if is_likely_file(cleaned) else None
                buf = []
                continue

        if CODE_BLOCK_RE.match(line.strip()):
            in_code = not in_code
            if not in_code and current:
                # Duplicate handling
                final_path = current
                if final_path in seen_paths:
                    counter = 2
                    while f"{final_path}_{counter}" in seen_paths: counter += 1
                    final_path = f"{final_path}_{counter}"
                
                files.append((final_path, "\n".join(buf)))
                seen_paths.add(final_path)
                current = None
                buf = []
            continue

        if in_code: buf.append(line)

    return files