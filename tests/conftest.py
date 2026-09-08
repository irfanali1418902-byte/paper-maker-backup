"""Shared pytest fixtures.

The `test_db` fixture monkeypatches `app.core.database.DB_PATH` to a fresh
SQLite file under pytest's `tmp_path`, then runs `init_db()` so the schema
is ready. Repositories pick this up automatically because `get_connection()`
looks up `DB_PATH` from its module's namespace at call time.

Each test gets its own DB file — no cross-test contamination.
"""

import os

import pytest

# ⚠ AUTH KO TESTS KE LIYE BAND KARO -- AUR YE LINE APP KE IMPORT SE PEHLE HONI
# CHAHIYE. `app/api/auth.py` apni key MODULE IMPORT PAR ek dafa parhti hai
# (`os.environ.get("PAPER_MAKER_API_KEY")`), aur `app/core/database.py:33` ka
# `load_dotenv()` `.env` se qeematein bhar deta hai.
#
# Natija: jis machine par `.env` mein asli key hoti, wahan poori suite girti
# thi -- `assert 401 == 200`. Ye 2026-09-08 ko waqai hua jab school ke liye key
# set ki gayi (UI-107). Suite ko developer ki `.env` par munhasir nahi hona
# chahiye; wo ek hi repo ko do machinon par do alag natije deti hai.
#
# Khali string yahan set karna kaafi hai: `load_dotenv()` default par mojooda
# environment variables ko OVERRIDE NAHI karta (`database.py`:39 khud yehi
# likhta hai), aur `auth.py` `... or ""` karta hai, yani khali = auth OFF.
#
# Auth ka apna behaviour `tests/test_auth.py` mein alag se test hota hai, jahan
# key jaan-boojh kar set ki jati hai -- wo is se mutassir nahi hota.
os.environ["PAPER_MAKER_API_KEY"] = ""

from app.core import database  # noqa: E402  -- upar wali line ke baad hi


@pytest.fixture
def test_db(tmp_path, monkeypatch):
    test_db_path = tmp_path / "test.db"
    monkeypatch.setattr(database, "DB_PATH", test_db_path)
    database.init_db()
    return test_db_path
