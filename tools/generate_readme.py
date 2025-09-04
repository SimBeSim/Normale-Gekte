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
