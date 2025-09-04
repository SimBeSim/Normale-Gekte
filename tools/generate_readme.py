#!/usr/bin/env python3
import os, sys, pathlib, re, json, subprocess
from datetime import datetime
from typing import Dict, List

REPO_URL = "https://github.com/SimBeSim/Normale-Gekte"
ROOT = pathlib.Path(__file__).resolve().parents[1]
README = ROOT / "README.md"

CONFIG_PATH = ROOT / "tools" / "readme_config.json"

# Default config (can be overridden by readme_config.json)
CFG = {
    "ignore_dirs": [".git", ".github", "__pycache__", "venv", ".venv", "node_modules", "tools"],
    "ignore_files": ["README.md", "LICENSE", ".gitignore"],
    "hidden_prefix": ".",               # dotfiles/dirs hidden
    "categories": {                     # map top-level dir -> category name
        "Seks_en_Drugs": "Sensitive Index (titles only)",
        "Privé": "Private (local only)",
        "Publiek": "Public",
    },
    "category_order": ["Public", "Sensitive Index (titles only)", "Private (local only)", "Uncategorized"],
    "tree_max_depth": 6,
    "show_last_modified": True,         # uses git if available
}

START = "<!-- AUTO-GENERATED:START -->"
END   = "<!-- AUTO-GENERATED:END -->"

def load_config():
    if CONFIG_PATH.exists():
        try:
            user_cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            for k, v in user_cfg.items():
                CFG[k] = v
        except Exception as e:
            print(f"[warn] Failed to read config: {e}")

def git_last_modified(rel_path: str) -> str:
    try:
        out = subprocess.check_output(
            ["git", "log", "-1", "--format=%cd", "--date=short", "--", rel_path],
            cwd=ROOT, stderr=subprocess.DEVNULL, text=True
        ).strip()
        return out or ""
    except Exception:
        return ""

def link_for(path: pathlib.Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    return f"{REPO_URL}/blob/main/{rel}"

def is_ignored_dir(name: str) -> bool:
    if name in CFG["ignore_dirs"]: return True
    if CFG["hidden_prefix"] and name.startswith(CFG["hidden_prefix"]): return True
    return False

def is_ignored_file(name: str) -> bool:
    if name in CFG["ignore_files"]: return True
    if CFG["hidden_prefix"] and name.startswith(CFG["hidden_prefix"]): return True
    return False

def build_tree_for_dir(dir_path: pathlib.Path, depth=0, max_depth=6) -> List[str]:
    """
    Return a markdown tree (list of lines) for dir_path.
    """
    if depth > max_depth:
        return []

    # List dirs/files
    try:
        entries = sorted(dir_path.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
    except FileNotFoundError:
        return []

    lines = []
    for p in entries:
        name = p.name
        if p.is_dir():
            if is_ignored_dir(name): 
                continue
            indent = "  " * depth
            lines.append(f"{indent}- **{name}/**")
            lines.extend(build_tree_for_dir(p, depth+1, max_depth))
        else:
            if is_ignored_file(name):
                continue
            rel = p.relative_to(ROOT).as_posix()
            indent = "  " * depth
            if CFG["show_last_modified"]:
                lm = git_last_modified(rel)
                lm_str = f" — _{lm}_" if lm else ""
            else:
                lm_str = ""
            lines.append(f"{indent}- [{name}]({link_for(p)}){lm_str}")
    return lines

def top_level_dirs() -> List[pathlib.Path]:
    return [p for p in ROOT.iterdir() if p.is_dir() and not is_ignored_dir(p.name)]

def categorize() -> Dict[str, List[pathlib.Path]]:
    cats: Dict[str, List[pathlib.Path]] = {}
    for d in top_level_dirs():
        cat_name = CFG["categories"].get(d.name, "Uncategorized")
        cats.setdefault(cat_name, []).append(d)
    # sort within categories
    for k in cats:
        cats[k].sort(key=lambda p: p.name.lower())
    return cats

def render_category_block(title: str, dirs: List[pathlib.Path]) -> str:
    if not dirs:
        return ""
    out = [f"### {title}"]
    for d in dirs:
        out.append(f"- **{d.name}/**")
        out.extend(["  " + line for line in build_tree_for_dir(d, depth=1, max_depth=CFG["tree_max_depth"])])
    out.append("")
    return "\n".join(out)

def render_root_files() -> str:
    files = []
    for p in sorted(ROOT.iterdir(), key=lambda x: x.name.lower()):
        if p.is_file() and not is_ignored_file(p.name):
            rel = p.relative_to(ROOT).as_posix()
            if CFG["show_last_modified"]:
                lm = git_last_modified(rel)
                lm_str = f" — _{lm}_" if lm else ""
            else:
                lm_str = ""
            files.append(f"- [{p.name}]({link_for(p)}){lm_str}")
    if not files:
        return ""
    return "### Root\n" + "\n".join(files) + "\n"

def render_block() -> str:
    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    cats = categorize()

    # Order categories
    ordered_titles = [c for c in CFG["category_order"] if c in cats] + [c for c in cats if c not in CFG["category_order"]]

    parts = [f"_Last updated: **{ts}**_",
             "",
             "## Index (Tree & Categories)",
             render_root_files()]

    for title in ordered_titles:
        parts.append(render_category_block(title, cats[title]))

    content = "\n".join([p for p in parts if p is not None]).strip()
    return f"{START}\n{content}\n{END}"

def ensure_readme():
    if not README.exists():
        README.write_text(
f"""# Normale_Gekte – Centrale Index

Welkom! Dit repo is onze **centrale hub** met verwijzingen en structuur.
De boom hieronder wordt **automatisch** gegenereerd.

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
        return text.rstrip() + "\n\n" + block + "\n"

def main():
    load_config()
    ensure_readme()
    current = README.read_text(encoding="utf-8")
    new_block = render_block()
    updated = replace_block(current, new_block)
    if updated != current:
        README.write_text(updated, encoding="utf-8")
        print("README updated.")
    else:
        print("README up-to-date.")

if __name__ == "__main__":
    main()
