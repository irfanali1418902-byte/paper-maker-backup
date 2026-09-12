"""Pehla admin banao — ya kisi ka password reset karo — seedha server par.

    python scripts/create_admin.py                  # poochta hua (interactive)
    python scripts/create_admin.py --username irfan --role admin
    python scripts/create_admin.py --username irfan --reset-password
    python scripts/create_admin.py --list

KYUN YE SCRIPT MOJOOD HAI. Ye us soorat ka jawab hai jis mein UI se kuch nahi
kiya ja sakta: koi admin bacha hi nahi (aakhri admin ka password kho gaya), ya
school ne pehle din hi API se nahi, server se account banana hai. Is ka
ikhtiyar file-system par baithne se aata hai — jo is DB file tak pahunch sakta
hai wo waise bhi sab kuch parh sakta hai, to yahan koi naya darwaza nahi khul
raha.

⚠ PASSWORD COMMAND LINE PAR MAT DO. Isi liye `--password` jaisa koi flag yahan
NAHI hai: command line shell ki history mein reh jati hai, aur Windows par
`Get-History` / PSReadLine us file ko disk par likh deta hai. Password hamesha
poochha jata hai aur `getpass` se liya jata hai (screen par nazar nahi aata).
"""

import argparse
import getpass
import sys
from pathlib import Path

# Script ko `python scripts/create_admin.py` se bhi chalna chahiye, jahan
# project root sys.path par nahi hota.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import DB_PATH, init_db  # noqa: E402
from app.repositories import users_repository  # noqa: E402
from app.services import session_service, user_service  # noqa: E402
from app.services.exceptions import UserValidationError  # noqa: E402

_NO_TTY_MSG = """  [X] Ye script ek ASLI terminal maangti hai, aur abhi koi nahi hai.

      Windows par `getpass` password seedha console se parhta hai -- pipe ya
      redirect se NAHI. Is ka matlab ye hai ke aise chalane par script chup-chaap
      LATAK jati hai (na koi paighaam, na koi error, bas ruki rehti hai), aur
      wahi sab se bura anjaam hai. Naapa gaya 2026-09-12: `printf 'pw\\npw\\n' |
      python scripts/create_admin.py` 120 second tak khamoshi se ruka raha.

      Chalane ka sahi tareeqa -- PowerShell ya CMD khol kar seedha:

          python scripts\\create_admin.py

      (Claude Code ke andar se: prompt mein `!` laga kar wahi command likho --
      wo tumhare apne terminal mein chalti hai.)

      Password command-line par dene ka koi flag JAAN-BOOJH KAR nahi hai: wo
      shell ki history mein reh jata, aur Windows par PSReadLine us file ko
      disk par likh deta hai."""


def _ask_password() -> str:
    """Do dafa poochho. Ek dafa poochne ka matlab hai ke pehli typo ka pata us
    waqt chale jab admin login ki koshish kare — aur tab tak use ye bhi nahi
    pata hoga ke ghalti kahan hui."""
    # ⚠ PEHLE YE. Bina terminal ke `getpass` latak jata hai (upar wajah), is
    # liye us soorat ko yahin, saaf paighaam ke saath, kaata jata hai.
    if not sys.stdin.isatty():
        print(_NO_TTY_MSG)
        raise SystemExit(2)
    while True:
        pw = getpass.getpass("Password: ")
        if len(pw) < user_service.MIN_PASSWORD_LEN:
            print(f"  [!] Kam az kam {user_service.MIN_PASSWORD_LEN} harf ka password rakho.")
            continue
        if pw != getpass.getpass("Password (dobara): "):
            print("  [!] Dono ek jaise nahi. Phir se.")
            continue
        return pw


def cmd_list() -> int:
    users = user_service.list_users()
    if not users:
        print("Koi user nahi — app abhi key/khule mode par hai.")
        return 0
    print(f"{'username':<20} {'role':<9} {'haalat':<8} aakhri login")
    print("-" * 62)
    for u in users:
        print(
            f"{u['username']:<20} {u['role']:<9} "
            f"{'active' if u['is_active'] else 'band':<8} {u['last_login_at'] or '-'}"
        )
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Pehla admin banao ya password reset karo.")
    ap.add_argument("--username", help="Login ka naam (lower-case mein mehfooz hota hai).")
    ap.add_argument("--display-name", default="", help="Poora naam, jo app mein dikhega.")
    ap.add_argument("--role", default="admin", choices=list(user_service.ROLES))
    ap.add_argument("--reset-password", action="store_true", help="Mojooda user ka password badlo.")
    ap.add_argument("--list", action="store_true", help="Saare users dikhao.")
    args = ap.parse_args()

    # Schema ka mojood hona yahin yaqeeni bana lo: ye script app ke pehle bhi
    # chal sakti hai (naye school PC par pehla qadam), jab tables bani hi na hon.
    init_db()
    print(f"Database: {DB_PATH}\n")

    if args.list:
        return cmd_list()

    username = args.username or input("Username: ").strip()
    existing = users_repository.get_by_username(username)

    if args.reset_password:
        if not existing:
            print(f"  [X] '{username}' naam ka koi user nahi. `--list` se dekho.")
            return 1
        password = _ask_password()
        # change_password() us bande ki saari sessions bhi khatam karta hai —
        # aur reset ki soorat mein wahi maqsood hai.
        session_service.change_password(existing["id"], password, ip="cli")
        print(f"\n  [OK] '{username}' ka password badal diya. Us ki saari sessions khatam.")
        return 0

    if existing:
        print(f"  [X] '{username}' pehle se mojood hai. Password badalna ho to --reset-password do.")
        return 1

    password = _ask_password()
    try:
        user = user_service.create_user(
            username=username,
            password=password,
            display_name=args.display_name,
            role=args.role,
        )
    except UserValidationError as e:
        print(f"  [X] {e}")
        return 1

    session_service.log_event(
        event="user_created", username=user["username"], user_id=user["id"], ip="cli", detail="cli"
    )
    print(f"\n  [OK] '{user['username']}' ban gaya ({user['role']}).")
    # Ye jumla sab se ahem hai jo ye script chhap sakti hai: pehla user banate
    # hi poori app ka auth mode badal jata hai. Jo admin ye chala raha hai use
    # ye maloom hona chahiye us se PEHLE ke teachers subah aayen.
    #
    # ⚠ IS FUNCTION KE `print()` MEIN SIRF ASCII. Yahan pehle "⚠" tha, aur
    # 2026-09-12 ko chala kar dekhne par wo Windows console (cp1252) par
    # `UnicodeEncodeError` de gaya -- account BAN CHUKA hota tha aur admin ko
    # us ke foran baad Python ka traceback milta, theek us jumle ki jagah jo
    # sab se zaroori tha. Comments mein Unicode theek hai (wo chhapte nahi);
    # `print` ke andar nahi.
    if len(user_service.list_users()) == 1:
        print("\n  [!] Ye is app ka PEHLA user hai - ab /api sirf login se khulta hai.")
        print("    Shared key (PAPER_MAKER_API_KEY) ab /api ke liye nahi chalegi.")
        print("    Teachers ko batao: http://<server>:8000/login.html")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
