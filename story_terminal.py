import os
import re
import subprocess
from datetime import datetime

# ---------- helpers ----------
def slugify(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")

def run(cmd: list[str]):
    # print(">>", " ".join(cmd))  # debug
    subprocess.run(cmd, check=True)

# ---------- ensure folders/files ----------
os.makedirs("stories", exist_ok=True)
os.makedirs("book", exist_ok=True)

manuscript_path = os.path.join("book", "manuscript.md")
if not os.path.exists(manuscript_path):
    with open(manuscript_path, "w", encoding="utf-8") as f:
        f.write(
            "# Normale Gekte\n"
            "*How insanity becomes divinity and divinity goes insane*\n\n"
            "## Inhoud\n"
        )

# ---------- gather input ----------
title = input("Titel van je verhaal: ").strip()
if not title:
    raise SystemExit("Geen titel opgegeven.")

print("\nPlak je volledige Markdown. Typ alleen 'EOF' op een nieuwe regel om af te sluiten.")
lines = []
while True:
    line = input()
    if line.strip() == "EOF":
        break
    lines.append(line)
body = "\n".join(lines).strip() + "\n"

# ---------- compose file ----------
today = datetime.now().strftime("%Y-%m-%d")
filename = f"stories/{today}_{slugify(title)}.md"

# als gebruiker geen frontmatter gaf, voeg minimale header toe
if not body.lstrip().startswith("---"):
    header = (
        f"---\n"
        f"title: {title}\n"
        f"date: {today}\n"
        f"tags: [verhaal]\n"
        f"summary: \n"
        f"---\n\n"
    )
    content = header + body
else:
    content = body

with open(filename, "w", encoding="utf-8") as f:
    f.write(content)

print(f"✅ Verhaal opgeslagen: {filename}")

# ---------- update manuscript ----------
link_line = f"- [{title}](../{filename})"
with open(manuscript_path, "r", encoding="utf-8") as f:
    manus = f.read()
if link_line not in manus:
    if not manus.endswith("\n"):
        manus += "\n"
    manus += link_line + "\n"
    with open(manuscript_path, "w", encoding="utf-8") as f:
        f.write(manus)
    print("📘 manuscript.md bijgewerkt.")

# ---------- git commit & push ----------
try:
    run(["git", "add", filename, manuscript_path])
    run(["git", "commit", "-m", f"Add story: {title}"])
    run(["git", "push"])
    print("🚀 Gepusht naar GitHub.")
except subprocess.CalledProcessError as e:
    print("⚠️ Git-actie mislukte. Meldingen:")
    print(e)
    print("Tip: log in met 'git credential-helper' of configureer je account:\n"
          "  git config user.name \"SimBeSim\"\n"
          "  git config user.email \"<jouw-email-op-github>\"")
          
# story_terminal.py

def get_story():
    return """# Vonkje’s Vuurdoop

Er was eens een klein vonkje, geboren in de donkere diepte van een oude kachel.  
Het wist nog niets van de wereld — alleen dat het warm was, en dat er boven hem  
iets schitterde.

“Wie ben ik?” fluisterde Vonkje.  
“Jij bent warmte,” antwoordde de stem van het Hout.  
“Maar pas op… warmte kan groeien, of alles verslinden.”

Vonkje trilde. Hij wilde groeien. Hij wilde de wereld zien.  
Met één sprong greep hij de lucht die door het rooster binnenkwam,  
en plotseling laaide hij op.

De rook vertelde hem verhalen over verre bergen en diepe oceanen.  
De vlammen dansten om hem heen als oude vrienden.  
En toen kwam de Wind — speels, maar ook genadeloos.  
“Kom mee, klein vuur,” riep de Wind, “ik kan je groot maken.”

Vonkje aarzelde niet. Hij liet zich optillen, hoger en hoger,  
tot hij de sterren bijna kon aanraken.  
Maar onder hem werd het dorp onrustig. De mensen riepen.  
Water kwam in golven aanrollen.

Toen de druppels hem raakten, siste Vonkje van pijn.  
Toch glimlachte hij — want hij had de lucht gezien, de vrijheid gevoeld.  

En ergens, diep in de kachel, werd een nieuw vonkje geboren…

---
_Een kort verhaal over nieuwsgierigheid, groei en de prijs van vrijheid._
"""

if __name__ == "__main__":
    print(get_story())

