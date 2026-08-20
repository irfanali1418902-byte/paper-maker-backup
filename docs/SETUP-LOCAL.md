# Local Deployment Guide — School System (AII Smart Paper Maker)

FastAPI app ek **school computer** (server) par chalti hai. 20 teachers usi WiFi/LAN par
apne browser se `http://<server-IP>:8000` khol kar use karte hain. Koi cloud/monthly cost
nahi. **Internet sirf AI question-generation (Gemini) ke waqt** chahiye — question bank,
papers, dashboard, Word/PDF export sab **offline** chalte hain.

**Server PC requirement:** 4 GB RAM kaafi hai (app halki hai — Python + SQLite). Ek PC
chuno jo school hours mein ON + LAN par rahe.

---

## 1. Prerequisites (server PC par ek dafa)

| Software | Kyun | Kahan se |
|---|---|---|
| **Python 3.12** | app runtime | https://www.python.org/downloads/ (3.12.x; "Add Python to PATH" tick karo) |
| **LibreOffice** *(optional)* | **PDF export** chalane ke liye | https://www.libreoffice.org/download — default path par install (`C:\Program Files\LibreOffice\`) |

> LibreOffice ke baghair: **Word (.docx) export chalega**, PDF export par app saaf error
> deti hai. LibreOffice install karte hi PDF export bhi chalne lagega (app khud
> `C:\Program Files\LibreOffice\program\soffice.exe` dhoond leti hai).

Verify (CMD/PowerShell): `python --version` → `Python 3.12.x`.

---

## 2. Code laao

```
git clone https://github.com/irfanali1418902-byte/paper-maker-mvp.git
cd paper-maker-mvp
```
(Ya repo ka ZIP copy karke server PC par rakh do.)

---

## 3. Virtual environment + dependencies

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```
Sab pip se aata hai (koi system tool nahi). Ek dafa internet chahiye.

---

## 4. Database — school ka real data

App SQLite ka **ek file** use karti hai. Data ko repo se bahar ek stable folder mein rakho
taake git operations/updates se mehfooz rahe:

1. Folder banao: `C:\PaperMakerData\`
2. **Real data (247 questions, 27 papers…):** verified backup file
   `paper_maker_prod_20260704.db` ko us folder mein **`paper_maker.db`** naam se copy karo.
   *(Ya fresh khaali DB chahiye to ye step chhod do — app pehli baar khud bana legi.)*
3. Neeche `DB_PATH` isi file ko point karega.

> ⚠️ Agar cloud (Railway/Northflank) copies bhi chal rahi hain to data alag-alag ho jayega
> (local aur cloud sync nahi hote). Tay karo **kaun sa primary** hai; ek hi jagah edit ho.

---

## 5. Configuration (env vars)

Repo root mein **`.env`** file banao — `.env.example` ki copy. Ye **gitignored** hai.

```
DB_PATH=C:\PaperMakerData\paper_maker.db
PAPER_MAKER_API_KEY=your-long-random-key
GEMINI_API_KEY=your-gemini-key
```

> **20 Agast se pehle yeh guide `env.local.bat` kehti thi, aur wo ab nahi chahiye.**
> Do launchers do alag config files parhte the (`start-local.bat` → `env.local.bat`,
> `start.bat` → `.env`) aur admin ke liye koi tareeqa nahi tha ke kaunsi asli hai. Ab
> **sirf `.env`** hai, aur app khud use load karti hai. Agar aap ke school PC par
> `env.local.bat` pehle se hai to uski qeematein `.env` mein copy kar dein.

> ⚠ **`DB_PATH` sab se ahem line hai.** Ghalat ya typo'd path par app **error nahi
> deti** — wo us jagah nayi khali database bana leti hai, folder samet, aur school ko
> lagta hai saare papers urh gaye jabke asli file apni jagah salamat hoti hai.
> `start-school.bat` chalne se pehle check karta hai ke file waqai mojood hai, aur na
> ho to poochta hai.

Vars ka matlab:

| Var | Value | Note |
|---|---|---|
| `DB_PATH` | `C:\PaperMakerData\paper_maker.db` | step 4 wali file |
| `PAPER_MAKER_API_KEY` | koi lambi random string | teachers ise ek dafa app ke "Access key" box mein daalenge (browser yaad rakhta hai). **Set na karo to LAN par auth OFF** (trusted network ho to theek) |
| `GEMINI_API_KEY` | apni Gemini key | AI question generation ke liye (internet ke saath). Na ho to baaki app chalti hai, AI generate band |

---

## 6. Windows Firewall — port 8000 kholo (20 teachers ke liye zaroori)

**Admin** PowerShell mein ek dafa:
```
netsh advfirewall firewall add rule name="Paper Maker 8000" dir=in action=allow protocol=TCP localport=8000
```

---

## 7. Server chalao

**Aasan:** repo mein **`start-school.bat`** par double-click.

Chalne se pehle wo chaar cheezein check karta hai jo khamoshi se ghalat ja sakti hain:

| check | agar ghalat ho |
|---|---|
| `.venv` mojood hai | banane ka command dikhata hai |
| **database file waqai mojood hai** | rukta hai aur poochta hai — nayi khali DB banne se pehle |
| `PAPER_MAKER_API_KEY` set hai | batata hai ke LAN par `/api` khula hai |
| firewall rule mojood hai | poora `netsh` command dikhata hai |

Phir LAN IP dikha kar server chalata hai.

> `start-local.bat` ab sirf isi ko chalata hai (purani shortcuts ke liye rakha gaya).
> **`start.bat` development ke liye hai** — us mein `--reload` hai, jo school server par
> nahi hona chahiye: wo files watch karta hai aur code chhune par server restart kar deta
> hai, yani teacher ka aadha bana paper ja sakta hai.

**Ya manually** (venv active hote hue):
```
uvicorn app.main:app --host 0.0.0.0 --port 8000
```
`--host 0.0.0.0` zaroori hai — isi se doosre devices LAN par connect kar paate hain.
`--reload` **mat** lagayen. Aur is command ko **repo folder ke andar se** chalayen —
`.env` current folder se ooper talash hota hai.

---

## 8. Access — teachers kaise kholenge

- **Server PC par khud:** http://localhost:8000
- **Kisi bhi teacher ke phone/laptop (same WiFi) par:** `http://<server-IP>:8000`

Server PC ka IP (CMD): `ipconfig` → `IPv4 Address` (jaise `192.168.1.25`) → teachers
kholenge **http://192.168.1.25:8000**.

- Router mein server PC ko **static/reserved IP** do (reboot par IP na badle).
- Agar `PAPER_MAKER_API_KEY` set hai: har teacher pehli baar "Access key" box mein wahi key
  daalega (browser localStorage mein save ho jati hai).

---

## 9. Server ko chalta rakhna (recommended)

- **Simple:** `start-school.bat` ki shortcut `shell:startup` folder mein — PC on hote hi chalu.
  (Purani `start-local.bat` wali shortcut bhi chalti rahegi, wo isi ko bulati hai.)
- **Service jaisa (auto-restart, background):** [NSSM](https://nssm.cc/download) se —
  ```
  nssm install PaperMaker "C:\path\paper-maker-mvp\.venv\Scripts\python.exe" "-m uvicorn app.main:app --host 0.0.0.0 --port 8000"
  nssm set PaperMaker AppDirectory "C:\path\paper-maker-mvp"
  nssm set PaperMaker AppEnvironmentExtra DB_PATH=C:\PaperMakerData\paper_maker.db PAPER_MAKER_API_KEY=... GEMINI_API_KEY=...
  nssm start PaperMaker
  ```

---

## 10. Backups (SQLite = ek file, aasan)

Rozana/haftawar `C:\PaperMakerData\paper_maker.db` ko kisi aur drive/USB par copy kar lo.
Safe copy ke liye (app chalte hue) SQLite `.backup` behtar hai:
```
python -c "import sqlite3; s=sqlite3.connect(r'C:\PaperMakerData\paper_maker.db'); d=sqlite3.connect(r'D:\backups\paper_maker_%DATE%.db'); s.backup(d); print('ok')"
```

---

## 11. Troubleshooting

| Masla | Hal |
|---|---|
| Teacher connect nahi hota | Firewall rule (step 6)? Same WiFi? Sahi IP? Server `--host 0.0.0.0` par chal raha? |
| `/api` par "API key ghalat ya missing" | Teacher ne sahi key daali? Server par `PAPER_MAKER_API_KEY` wahi hai? |
| AI generate fail | `GEMINI_API_KEY` set + internet? |
| PDF export error, Word chal raha | LibreOffice install karo (step 1) — default path par |
| Purana data nahi dikh raha | `DB_PATH` sahi file (step 4) point kar raha? |

---

## Internet dependency — saaf
- **One-time setup:** `pip install` ke liye internet.
- **Rozana:** sirf **Gemini AI** call ke waqt internet. Baaki sab (bank, papers, dashboard,
  Word/PDF export, 20 teachers LAN serving) **offline**.

---

## (Task 3 — future) Company/Publisher distribution
Multi-school package alag `docs/DISTRIBUTION.md` mein: Docker image (Python + LibreOffice
bundled), ek installer script, per-school config (DB_PATH, keys, port), aur update mechanism.
Repo ka `Dockerfile` (slim, cloud wala) is ke liye base hai — LibreOffice add hoga.
