#!/usr/bin/env python3
import os, sys, pathlib, re
from datetime import datetime

REPO_URL = "https://github.com/SimBeSim/Normale-Gekte"
ROOT = pathlib.Path(__file__).resolve().parents[1]  # repo root
README = ROOT / "README.md"

# Folders/files to ignore in the listing
IGNORE_DIRS = {".git", ".github", "__pycache__", "venv", ".venv", "node_modules", "tools"}
IGNORE_FILES = {"README.md", "LICENSE", ".gitignore"}

START = "<!-- AUTO-GENERATED:START -->"
END   = "<!-- AUTO-GENERATED:END -->"

def make_link(path: pathlib.Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    return f"- [{rel}]({REPO_URL}/blob/main/{rel})"

def build_file_index() -> str:
    lines = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        p = pathlib.Path(dirpath)
        # prune ignored dirs
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS and not d.startswith(".")]
        # files
        files = [f for f in filenames if f not in IGNORE_FILES and not f.startswith(".")]
        files.sort()
        # skip root heading, we’ll group by directory
        rel_dir = p.relative_to(ROOT)
        if rel_dir == pathlib.Path("."):
            section_title = "Root"
        else:
            section_title = rel_dir.as_posix()
        # collect links
        links = []
        for f in files:
            fp = p / f
            links.append(make_link(fp))
        if links:
            lines.append(f"### {section_title}")
            lines.extend(links)
            lines.append("")  # blank line
    if not lines:
        return "_(No files yet)_"
    return "\n".join(lines).rstrip()

def render_block() -> str:
    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    index_md = build_file_index()
    return (
f"""{START}
_Last updated: **{ts}**_

## Index
{index_md}
{END}"""
    )

def ensure_readme():
    if not README.exists():
        # minimal scaffold with markers
        README.write_text(
f"""# Normale_Gekte – Centrale Index

Welkom! Dit repo is onze **centrale hub** met verwijzingen en structuur.

{START}
(automatically generated)
{END}
""",
            encoding="utf-8",
        )

def replace_block(text: str, block: str) -> str:
    if START in text and END in text:
        pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.S)
        return pattern.sub(block, text)
    else:
        # append at end if markers not found
        return text.rstrip() + "\n\n" + block + "\n"

def main():
    ensure_readme()
    current = README.read_text(encoding="utf-8")
    new_block = render_block()
    updated = replace_block(current, new_block)
    if updated != current:
        README.write_text(updated, encoding="utf-8")
        print("README updated.")
        sys.exit(0)
    else:
        print("README up-to-date.")
        sys.exit(0)

if __name__ == "__main__":
    main()
