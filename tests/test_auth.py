"""`/api` ki key wali auth — dono modes.

KYUN YE FILE MOJOOD HAI. 2026-09-08 tak is behaviour par **ek bhi test nahi
tha** (UI-107 mein dhoonda gaya: `grep -rn "API_KEY" tests/` sirf `ai_service`
ki provider keys deta tha). Usi din Irfan ne faisla kiya ke school par
`PAPER_MAKER_API_KEY` set hogi — yani ye rule school ke LAN par asal security
boundary ban gaya: bina is ke WiFi par koi bhi device `/api` par likh-parh
sakta hai.

Us waqt tak wo boundary sirf haath se `curl` chala kar dekhi gayi thi. Ek
boundary jise koi gate nahi dekhta, wo agle refactor mein khamoshi se khul
sakti hai — aur khulne par kuch bhi fail nahi hoga.

⚠ `auth.API_KEY` MODULE IMPORT PAR EK DAFA PARHI JATI HAI, is liye yahan
`monkeypatch.setattr` module ke global par lagta hai, environment par nahi.
`require_api_key()` us global ko HAR CALL par parhti hai (`app/api/auth.py`:88),
is liye ye kaam karta hai aur module reload ki zaroorat nahi.

⚠ STATIC SURFACE HAMESHA KHULA REHTA HAI, aur wo aakhri test us ka guard hai:
teacher ka browser HTML/JS bina key ke load karta hai, phir key ek dafa daalta
hai. Agar kabhi auth `/static` par bhi lag gayi to teacher app khol hi nahi
payega — aur wo galti "sab kuch mehfooz kar do" ki neeyat se bilkul mumkin hai.
"""

import pytest
from fastapi.testclient import TestClient

from app.api import auth

KEY = "test-key-jo-sirf-yahan-hai"


@pytest.fixture
def client(test_db):
    # test_db par munhasir, taake DB_PATH temp file par ho is se pehle ke
    # app.main import ho -- wahi tareeqa jo tests/test_api_routes.py use karta hai.
    from app.main import app

    return TestClient(app)


class TestAuthOff:
    """Key set na ho to `/api` khula rehta hai — local dev ka mode."""

    def test_api_khula_hai_jab_key_nahi(self, client, monkeypatch):
        monkeypatch.setattr(auth, "API_KEY", "")
        assert client.get("/api/papers").status_code == 200


class TestAuthOn:
    """Key set ho to har `/api` call par sahi header zaroori."""

    def test_bina_header_401(self, client, monkeypatch):
        monkeypatch.setattr(auth, "API_KEY", KEY)
        res = client.get("/api/papers")
        assert res.status_code == 401

    def test_ghalat_key_401(self, client, monkeypatch):
        monkeypatch.setattr(auth, "API_KEY", KEY)
        res = client.get("/api/papers", headers={"x-api-key": "ghalat"})
        assert res.status_code == 401

    def test_sahi_key_200(self, client, monkeypatch):
        monkeypatch.setattr(auth, "API_KEY", KEY)
        res = client.get("/api/papers", headers={"x-api-key": KEY})
        assert res.status_code == 200

    def test_header_ka_naam_case_insensitive_hai(self, client, monkeypatch):
        """HTTP headers case-insensitive hain; teacher ka browser jo bhi bheje."""
        monkeypatch.setattr(auth, "API_KEY", KEY)
        res = client.get("/api/papers", headers={"X-API-Key": KEY})
        assert res.status_code == 200

    def test_error_message_batata_hai_kya_karna_hai(self, client, monkeypatch):
        """401 ka matn teacher/admin ko raasta de -- khali "Unauthorized" nahi."""
        monkeypatch.setattr(auth, "API_KEY", KEY)
        detail = client.get("/api/papers").json()["detail"]
        assert "x-api-key" in detail


class TestStaticSurface:
    """⚠ Sab se ahem test: key ON hone par bhi app ka safha khulna chahiye."""

    @pytest.mark.parametrize("path", ["/static/index.html", "/static/bank.html"])
    def test_static_page_key_ke_baghair_bhi_khulta_hai(self, client, monkeypatch, path):
        monkeypatch.setattr(auth, "API_KEY", KEY)
        assert client.get(path).status_code == 200
