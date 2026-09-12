# Auth — kaun andar aa sakta hai, aur kaise

_SEC-02, 2026-09-12. Is se pehle ki halat aur us ki kami niche "Pehle kya tha"
mein hai — wo hissa tareekh hai, aur jaan-boojh kar rakha gaya hai._

## Teen modes, aur mode DATA se tay hota hai

| Mode | Kab | Kya chahiye |
|---|---|---|
| `users` | `users` table mein koi **active** user hai | Login (session cookie) |
| `key` | koi user nahi, magar `PAPER_MAKER_API_KEY` set hai | `x-api-key` header |
| `open` | na user, na key | Kuch nahi (sirf local dev) |

⚠ **Koi flag nahi hai jo auth "on" karta ho.** Pehla user banate hi mode badal
jata hai, aur aakhri active user band hote hi wapas. Ye jaan-boojh kar hai: ek
chalti hui school par auth upgrade ka matlab hargiz ye nahi hona chahiye ke
kisi subah teachers andar na aa sakein. Jab tak koi account nahi bana, app
haraf ba haraf wahi hai jo pehle thi.

Code: `app/api/auth.py` → `auth_mode()`.

## Shuru kaise karein (school par, ek dafa)

```
python scripts/create_admin.py
```

Naam aur password poochha jayega (password screen par nazar nahi aata, aur
command line par dena mumkin hi nahi rakha gaya — wo shell history mein reh
jata hai). Ye chalte hi:

* app `users` mode par chali jati hai,
* `PAPER_MAKER_API_KEY` `/api` ke liye kaam karna chhor deti hai,
* teachers ka rasta ban jata hai: `http://<server>:8000/login.html`

Baqi teachers ke accounts admin app ke andar se banata hai: **Users** (top bar
mein, sirf admin ko dikhta hai) → `users.html`.

Kuch ghalat ho jaye to wohi script bachati hai:

```
python scripts/create_admin.py --list
python scripts/create_admin.py --username irfan --reset-password
```

## Kya kya lagaya gaya hai

| Cheez | Kahan | Faisla |
|---|---|---|
| Password hashing | `user_service` | `hashlib.scrypt` — stdlib, koi nayi dependency nahi (school PC par `pip install` karne wala koi nahi hota) |
| Session | `sessions` table | Cookie mein khaam token, **DB mein sirf SHA-256** — DB ki copy se koi session churai nahi ja sakti |
| Cookie | `HttpOnly`, `SameSite=Lax` | JS use parh hi nahi sakta; CSRF ka aam raasta band. `Secure` sirf https par (LAN aaj http hai) |
| Idle hadd | 30 minute | Wahi adad jo browser-lock par pehle se tha |
| Sakht hadd | 12 ghante | Ek school ka din — idle ghadi har request par aage barhti hai, ye us silsile ko kaatti hai |
| Lockout | 5 nakaam → 15 minute | **Naam par, IP par nahi**: bees teachers ek hi router ke peeche hain |
| Roles | `admin` / `teacher` | Admin = user management; teacher = baqi poori app |
| Log | `auth_events` | Login, nakami, lockout, logout, account banna/badalna |
| `/docs` | `app/main.py` | Key set ho (ya fail-closed flag) to band |

## Jo jaan-boojh kar khula hai

* **Static `/`** — HTML/JS/CSS bina auth ke load hote hain. Warna login page
  khud kabhi load na ho: ek darwaza jis ki chaabi andar rakhi ho.
* **`/api/brand`** — cosmetic shell, har page load par chahiye.
* **`/api/auth/me`** — "login zaroori hai" khud ek jawab hai, error nahi.
* **`static/library/` aur `static/uploads/`** — question images. Ye **khula
  masla hai, faisla nahi**: filename UUID hai (andaze se nahi milta), magar ek
  dafa URL leak ho jaye to hamesha khula rehta hai. Ise band karne ka matlab
  har `<img>` ke liye blob-fetch hai — kaafi frontend kaam. `PROGRESS.md` ki
  SEC-02 row mein khuli hui cheezon mein darj hai.

## Pehle kya tha, aur wo kaafi kyun nahi tha

Ek shared key (`PAPER_MAKER_API_KEY`), localStorage mein, har teacher ke paas
wahi ek qeemat. Us se darwaza band hota tha — magar:

* system ko nahi pata tha ke banda **kaun** hai,
* koi role nahi tha (har kisi ke paas delete ka wahi ikhtiyar),
* "ye parcha kis ne mitaya" ka jawab **kahin darj hi nahi hota tha**,
* aur 2026-09-08 wala idle auto-lock **sirf browser mein** tha: key
  localStorage se mit jati thi, magar server ke nazdeek wo us ke baad bhi utni
  hi durust rehti thi — yani DevTools se qeemat copy kar lene wale ke liye lock
  ka koi wajood nahi tha.

Aakhri nuqta khud `static/apiClient.js` ne apne upar likh kar maan liya tha:
_"⚠ YE AUTHENTICATION NAHI HAI … asli users/roles/activity-log alag kaam hai."_
Ye file us kaam ka record hai.

## Abhi bhi khula (tarteeb se)

1. `static/library` + `static/uploads` bina auth ke serve hote hain (upar).
2. Destructive actions (parcha/sawal delete) ka apna activity log nahi — abhi
   sirf auth events log hote hain. `auth_events` ka shape us ke liye tayyar hai.
3. `/docs` ka faisla startup par hota hai, is liye `users` mode us mein shamil
   nahi ho sakta (`app/main.py` par tafseel).
4. HTTPS nahi hai. LAN par cookie plain http par jati hai. Jis din proxy/TLS
   lage, cookie khud ba khud `Secure` ho jayegi — code change nahi chahiye.
