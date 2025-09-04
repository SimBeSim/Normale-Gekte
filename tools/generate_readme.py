#!/usr/bin/env python3
import os, sys, pathlib, re, json, subprocess, shlex
from datetime import datetime
from typing import Dict, List, Tuple

REPO = "SimBeSim/Normale-Gekte"
REPO_URL = f"https://github.com/{REPO}"
ROOT = pathlib.Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
CONFIG_PATH = ROOT / "tools" / "readme_config.json"

CFG = {
    "ignore_dirs": [".git", ".github", "__pycache__", "venv", ".venv", "node_modules", "tools"],
    "ignore_files": ["README.md", "LICENSE", ".gitignore"],
    "hidden_prefix": ".",
    "categories": {
        "Publiek": "Public",
        "Seks_en_Drugs": "Sensitive Index (titles only)",
        "Privé": "Private (local only)"
    },
    "category_order": ["Public", "Sensitive Index (titles only)", "Private (local only)", "Uncategorized"],
    "tree_max_depth": 6,
    "show_last_modified": True,
    "collapse_categories": True,
    "badge_workflow": "update-readme.yml",   # naam van je workflow file
}

START = "<!-- AUTO-GENERATED:START -->"
END   = "<!-- AUTO-GENERATED:END -->"

def run(cmd: List[str]) -> str:
    try:
        out = subprocess.check_output(cmd, cwd=ROOT, stderr=subprocess.DEVNULL, text=True)
        return out.strip()
    except Exception:
        return ""

 def load_config():
    if CONFIG_PATH.exists():
        try:
            user_cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            for k, v in user_cfg.items():
                CFG[k] = v
        except Exception as e:
            print(f"[warn] Failed to read config: {e}")
 
 def prettify_filename(name: str) -> str:
    base = name.rsplit(".", 1)[0]
    base = base.replace("_", " ").replace("-", " ").strip()
    return " ".join(w.capitalize() for w in base.split() if w)

def md_first_h1(path: pathlib.Path) -> str:
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if line.startswith("# "):             # pakt de eerste H1
                    return line[2:].strip()
    except Exception:
        pass
    return ""

def display_name(path: pathlib.Path) -> str:
    # 1) probeer H1 uit markdown
    if path.suffix.lower() == ".md":
        h1 = md_first_h1(path)
        if h1:
            return h1
    # 2) anders: nette bestandsnaam
    return prettify_filename(path.name)

