#!/usr/bin/env python3
import sys, pathlib, datetime, subprocess

ROOT = pathlib.Path(__file__).resolve().parents[1]
FILE = ROOT / "Publiek" / "Voltooid.md"

def today():
    return datetime.date.today()

def month_header(d):
    return f"## {d.year:04d}-{d.month:02d}"

def get_default_link():
    # Probeer laatste commit URL te raden (fallback: leeg)
    try:
        sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
        return f"https://github.com/SimBeSim/Normale-Gekte/commit/{sha}"
    except Exception:
        return ""

def ensure_file():
    if not FILE.exists():
        FILE.parent.mkdir(parents=True, exist_ok=True)
        FILE.write_text("# Voltooid\n\nKorte changelog van wat we AFRONDEN. Elke regel = 1 afgerond item.\n\n"
                        "_Format:_ `YYYY-MM-DD — ✔ <korte omschrijving> — ⏱ <duur> — 🔗 <link>`\n\n", encoding="utf-8")

def append_entry(desc, duration, link):
    ensure_file()
    text = FILE.read_text(encoding="utf-8")
    today_d = today()
    header = month_header(today_d)

    if header not in text:
        # Voeg nieuwe maand bovenaan toe (onder de titel)
        parts = text.splitlines()
        # vind eerste lege regel na titelblok
        if len(parts) < 2 or not parts[0].startswith("# Voltooid"):
            parts.insert(0, "# Voltooid")
        # Zorg dat de maandkop bovenaan staat (na de intro)
        insert_at = len(parts)
        # probeer na de intro (2 lege regels) in te voegen
        for i, line in enumerate(parts):
            if line.strip().startswith("## "):
                insert_at = i
                break
        parts.insert(insert_at, "")
        parts.insert(insert_at, header)
        text = "\n".join(parts) + "\n"

    line = f"- {today_d} — ✔ {desc} — ⏱ {duration} — 🔗 {link}".rstrip()
    text = text.replace(header, header + "\n" + line, 1)
    FILE.write_text(text if text.endswith("\n") else text + "\n", encoding="utf-8")
    print("Voltooid: regel toegevoegd.")

def main():
    if len(sys.argv) < 3:
        print("Gebruik: add_voltooid.py \"omschrijving\" \"duur\" [link]")
        sys.exit(1)
    desc = sys.argv[1].strip()
    dur = sys.argv[2].strip()
    link = sys.argv[3].strip() if len(sys.argv) >= 4 else get_default_link()
    append_entry(desc, dur, link)

if __name__ == "__main__":
    main()
