"""App package. Ek hi kaam yahan hota hai: `.env` sab se pehle load karna.

YEH JAGAH ITTEFAQI NAHI HAI. Python koi bhi `app.*` module import kare — `app.main`,
`app.api.auth`, `app.core.database` — yeh file us se PEHLE chalti hai. Isliye har
module-level `os.environ.get(...)` ko `.env` mil jata hai, chahe import kis tarteeb
mein hon.

KYA TOOT RAHA THA. `app/api/auth.py`:25 `PAPER_MAKER_API_KEY` ko module import par
parhta hai, aur wo file `database` import nahi karti. 2026-08-20 tak yeh sirf isliye
kaam kar raha tha ke `app/main.py`:14 ka pandrah-module block (jo `app.core.database`
kheench laata hai, aur wahan `load_dotenv()` chalta hai) line 30 ke `auth` import se
pehle likha hua tha. **Us auth import ko do line ooper le jane par key khamoshi se
khali reh jaati aur LAN par `/api` bilkul unprotected ho jata** — koi error nahi, koi
log nahi, bas auth band. Ek school ke WiFi par yeh chup-chaap khula darwaza hai.

Isi bug ki pehli shakl `DB_PATH` par pakri gayi thi (PROGRESS.md 2026-08-20): wahan
`.env` ka path zaya ho raha tha aur app repo folder mein nayi khali DB bana leti thi.
`app/core/database.py` apna `load_dotenv()` ehtiyatan rakhe hue hai — do dafa chalna
be-zarar hai (dotenv mojooda vars override nahi karta), aur wo file akeli import ho to
bhi mehfooz rehti hai.

TARJEEH KA SILSILA, naapa hua: asli environment variable > `.env` > code ka default.
`load_dotenv()` pehle se set vars ko nahi chhoota, isliye `set DB_PATH=...` ya NSSM ka
`AppEnvironmentExtra` ab bhi sab se oopar hai.
"""

from dotenv import load_dotenv

load_dotenv()
