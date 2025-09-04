#!/usr/bin/env python3
import os, pathlib, re, json, subprocess
from datetime import datetime
from typing import List, Dict

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
    "badge_workflow": "update-readme.yml"
}

START = "<!-- AUTO-GENERATED:START -->"
END   = "<!-- AUTO-GENERATED:END -->"

# ---------------- helpers ----------------

def run(cmd: List[str]) -> str:
    try:
        return subprocess.check_output(cmd, cwd=ROOT, stderr=subprocess.DEVNULL, text=True).strip()
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
                if line.startswith("# "):
                    return line[2:].strip()
    except Exception:
        pass
    return ""

def display_name(path: pathlib.Path) -> str:
    if path.suffix.lower() == ".md":
        h1 = md_first_h1(path)
        if h1:
            return h1
    return prettify_filename(path.name)

def last_modified(rel_path: str) -> str:
    if not CFG["show_last_modified"]:
        return ""
    return run(["git", "log", "-1", "--format=%cd", "--date=short", "--", rel_path])

def file_link(path: pathlib.Path) -> str:
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

def list_entries_sorted(base: pathlib.Path) -> List[pathlib.Path]:
    try:
        entries = sorted(base.iterdir(), key=lambda p: p.name.lower())
    except FileNotFoundError:
        return []
    return [p for p in entries if not (p.is_dir() and is_ignored_dir(p.name)) and not (p.is_file() and is_ignored_file(p.name))]

# ---------------- tree rendering ----------------

def unicode_tree(dir_path: pathlib.Path, prefix: str = "\n", depth: int = 0, max_depth: int = 6) -> List[str]:
    if depth > max_depth: return []
    entries = list_entries_sorted(dir_path)
    lines = []
    for i, p in enumerate(entries):
        is_last = (i == len(entries)-1)
        branch = "└── " if is_last else "├── "
        pad = prefix + branch
        if p.is_dir():
            lines.append(f"{pad}**{p.name}/**")
            next_prefix = prefix + ("    " if is_last else "│   ")
            lines.extend(unicode_tree(p, next_prefix, depth+1, max_depth))
        else:
            rel = p.relative_to(ROOT).as_posix()
            label = display_name(p)
            lm = f"  — _{last_modified(rel)}_" if last_modified(rel) else ""
            lines.append(f"{pad}[{label}]({file_link(p)}){lm}")
    return lines

def render_root_files() -> str:
    files = [p for p in list_entries_sorted(ROOT) if p.is_file()]
    if not files: return ""
    lines = []
    for p in files:
        rel = p.relative_to(ROOT).as_posix()
        label = display_name(p)
        lm = f"  — _{last_modified(rel)}_" if last_modified(rel) else ""
        lines.append(f"- [{label}]({file_link(p)}){lm}")
    return "### Root\n" + "\n".join(lines) + "\n"

# ---------------- categories ----------------

def top_level_dirs() -> List[pathlib.Path]:
    return [p for p in list_entries_sorted(ROOT) if p.is_dir()]

def categorize() -> Dict[str, List[pathlib.Path]]:
    cats: Dict[str, List[pathlib.Path]] = {}
    for d in top_level_dirs():
        cat = CFG["categories"].get(d.name, "Uncategorized")
        cats.setdefault(cat, []).append(d)
    return cats

def details_block(summary: str, content_md: str) -> str:
    if not CFG["collapse_categories"]:
        return f"### {summary}\n\n{content_md}\n"
    return f"<details>\n<summary><strong>{summary}</strong></summary>\n\n{content_md}\n</details>\n"

def render_categories() -> str:
    cats = categorize()
    ordered = [c for c in CFG["category_order"] if c in cats] + [c for c in cats if c not in CFG["category_order"]]
    parts = []
    for title in ordered:
        dirs = cats[title]
        if not dirs: continue
        buf = []
        for d in dirs:
            buf.append(f"**{d.name}/**")
            buf.extend(unicode_tree(d, prefix="", depth=1, max_depth=CFG["tree_max_depth"]))
            buf.append("")
        parts.append(details_block(title, "\n".join(buf).strip()))
    return "\n\n".join(parts).strip()

# ---------------- main rendering ----------------

def badges_line() -> str:
    wf = CFG["badge_workflow"]
    return (
        f"[![Auto README]({REPO_URL}/actions/workflows/{wf}/badge.svg)]"
        f"({REPO_URL}/actions/workflows/{wf}) "
        f"![Repo size](https://img.shields.io/github/repo-size/{REPO}) "
        f"![Last commit](https://img.shields.io/github/last-commit/{REPO})"
    )

def render_highlights(n: int = 3) -> str:
    """Read last n '- ' items from Publiek/Voltooid.md and render as a collapsible block."""
    voltooid = ROOT / "Publiek" / "Voltooid.md"
    if not voltooid.exists():
        return ""
    lines = [l.rstrip() for l in voltooid.read_text(encoding="utf-8").splitlines()]
    # alleen lijstregels met taken
    task_lines = [l for l in lines if l.startswith("- ")]
    if not task_lines:
        return ""
    last = task_lines[-n:]
    inner = "\n".join(last)
    return (
        "<details>\n"
        "<summary><strong>Highlights (laatste voltooid)</strong></summary>\n\n"
        f"{inner}\n"
        "\n</details>\n"
    )


def render_block() -> str:
    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    pieces = [
        badges_line(),
        f"_Last updated: **{ts}**_",
        "",
        render_highlights(),  # << nieuwe regel
        "## Index (Tree, Recent-first)",
        render_root_files(),
        render_categories()
    ]

    return f"{START}\n" + "\n".join([p for p in pieces if p]).strip() + f"\n{END}"

def ensure_readme():
    if not README.exists():
        README.write_text(
f"""# Normale_Gekte – Centrale Hub

Welkom! Dit repo is onze **centrale index**.  
Onderstaande sectie wordt **automatisch** bijgewerkt.

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
