# Tijdloze Fundamenten vs. Lock-in Tools

Dit document is ons **kompas voor technologie**.  
Het laat zien waar we veilig op kunnen bouwen, en waar we risico lopen vast te zitten in afhankelijkheden.

---

## ✅ Tijdloze Fundamenten
Deze verdwijnen niet zomaar: het zijn protocollen, open standaarden of breed gedragen tools.
- **Git** (versiebeheer, door Linus Torvalds)  
- **GitHub/GitLab** (diensten erboven, maar Git zelf is tijdloos)  
- **HTTP/HTTPS** (basis van het web)  
- **HTML, CSS, JavaScript** (open webstandaarden)  
- **Markdown** (lichtgewicht tekststandaard, menselijk leesbaar)  
- **JSON / XML / CSV** (data-uitwisseling, overal bruikbaar)  
- **SQL (SQLite, Postgres, MySQL)** (relationele databases)  
- **Programmeertalen:** Python, C, JavaScript, Bash  
- **E-mail protocollen:** SMTP, IMAP, POP3  

---

## ⚠️ Lock-in / Risicovolle Tools
Kunnen handig zijn, maar bouwen hierop als kern = gevaarlijk.
- **Netlify, Vercel, Heroku** → afhankelijk van hun businessmodel  
- **Proprietary API’s** (Twitter/X API, Facebook Graph API, etc.) → wijzigen of verdwijnen plots  
- **Zapier, IFTTT** → leuk voor snelle hacks, maar fragiel en duur  
- **Closed CMS** (Wix, Squarespace) → mooi tot je vastloopt, migratie is ramp  
- **Microsoft Power Automate / Sharepoint** → handig in bedrijven, maar zwaar lock-in  

---

## 🌍 Semi-veilige Middengroep
Goed bruikbaar, mits we een exit-strategie hebben.
- **Google Drive/Sheets/Docs** → stabiel, maar tóch Google-dependent  
- **AWS / Azure / GCP** → solide, maar vendor lock-in mogelijk  
- **Slack, Discord** → handig, maar geen garantie → archiveren in eigen logboeken  

---

## 🔑 Onze Regel
1. Kern = **tijdloze fundamenten**.  
2. Hulpmiddelen = alleen inzetten met een **plan B**.  
3. Alles wat we maken = zoveel mogelijk in **Markdown, JSON, SQLite, Git** → zodat het nooit verloren gaat.  
