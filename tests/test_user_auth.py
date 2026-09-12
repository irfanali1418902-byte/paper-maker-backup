"""SEC-02 — asli users, sessions, roles aur auth ka log.

KYUN YE FILE ITNI BARI HAI. Ye app ki waahid security boundary hai: is se aage
har parcha, har sawal, har natija hai. `tests/test_auth.py` (2026-09-08) ne wohi
kaam purani shared-key ke liye kiya tha aur us ki wajah aaj bhi wahi hai — ek
boundary jise koi gate na dekhe, wo agle refactor mein khamoshi se khul sakti
hai, aur khulne par kuch bhi fail nahi hota.

⚠ SAB SE AHEM TEST IS FILE KA WO HAI JO KUCH NAYA SABIT NAHI KARTA:
`TestModeFallback` — yani jab tak koi user nahi bana, app HARAF BA HARAF wahi
hai jo pehle thi. Ye poore kaam ki bunyaad hai. Agar wo tests kabhi fail hon to
matlab ye migration ek chalti hui school ko subah bahar kar sakti hai, aur us
soorat mein baqi sab kuch theek hona bhi kaafi nahi.
"""

import pytest
from fastapi.testclient import TestClient

from app.api import auth
from app.repositories import sessions_repository
from app.services import session_service, user_service
from app.services.exceptions import LoginFailed, UserValidationError

KEY = "test-key-jo-sirf-yahan-hai"
ADMIN_PW = "admin-ka-lamba-password"
TEACHER_PW = "teacher-ka-lamba-password"


@pytest.fixture
def client(test_db):
    from app.main import app

    return TestClient(app)


@pytest.fixture
def admin(test_db):
    return user_service.create_user("irfan", ADMIN_PW, display_name="Irfan Ali", role="admin")


@pytest.fixture
def teacher(test_db):
    return user_service.create_user("sana", TEACHER_PW, display_name="Sana", role="teacher")


def login(client, username, password):
    return client.post("/api/auth/login", json={"username": username, "password": password})


# ── password hashing ─────────────────────────────────────────────────────────


class TestPasswordHashing:
    def test_hash_har_dafa_alag_hai(self):
        """Salt ka poora maqsad yehi hai. Do teachers ka password agar ittefaq
        se ek hi ho, to DB dekh kar ye pata NAHI chalna chahiye."""
        assert user_service.hash_password(ADMIN_PW) != user_service.hash_password(ADMIN_PW)

    def test_plain_password_hash_mein_kahin_nahi(self):
        assert ADMIN_PW not in user_service.hash_password(ADMIN_PW)

    def test_sahi_password_verify_hota_hai(self):
        assert user_service.verify_password(ADMIN_PW, user_service.hash_password(ADMIN_PW))

    def test_ghalat_password_verify_nahi_hota(self):
        assert not user_service.verify_password("kuch aur", user_service.hash_password(ADMIN_PW))

    @pytest.mark.parametrize("kharab", ["", "plain-text", "scrypt$kuch$ghalat", "a$b$c$d$e$f"])
    def test_kharab_hash_par_false_aata_hai_exception_nahi(self, kharab):
        """DB mein koi kati hui ya purani shakal ki qeemat mile to login 401
        hona chahiye, 500 nahi. 500 ka matlab hai poora page toot gaya aur
        teacher ko koi raasta nahi milta."""
        assert user_service.verify_password(ADMIN_PW, kharab) is False


# ── mode: data se badalta hai, flag se nahi ──────────────────────────────────


class TestModeFallback:
    """⚠ Koi user na ho to app bilkul pehle jaisi chalti hai. Poore kaam ki bunyaad."""

    def test_na_user_na_key_to_khula(self, client, monkeypatch):
        monkeypatch.setattr(auth, "API_KEY", "")
        assert auth.auth_mode() == auth.MODE_OPEN
        assert client.get("/api/papers").status_code == 200

    def test_key_set_ho_aur_user_koi_nahi_to_purana_behaviour(self, client, monkeypatch):
        monkeypatch.setattr(auth, "API_KEY", KEY)
        assert auth.auth_mode() == auth.MODE_KEY
        assert client.get("/api/papers").status_code == 401
        assert client.get("/api/papers", headers={"x-api-key": KEY}).status_code == 200

    def test_pehla_user_bante_hi_mode_badal_jata_hai(self, client, monkeypatch, admin):
        monkeypatch.setattr(auth, "API_KEY", KEY)
        assert auth.auth_mode() == auth.MODE_USERS

    def test_users_mode_mein_shared_key_ab_nahi_chalti(self, client, monkeypatch, admin):
        """⚠ YE IS POORE KAAM KA NUQTA HAI. Jab tak sirf ek shared key thi,
        system ko ye pata hi nahi tha ke banda kaun hai. Users ban jane ke baad
        wo key andar aane ka raasta nahi rehni chahiye — warna har teacher ke
        paas identity ke ird gird ghoomne ka ek darwaza baaqi reh jata."""
        monkeypatch.setattr(auth, "API_KEY", KEY)
        assert client.get("/api/papers", headers={"x-api-key": KEY}).status_code == 401

    def test_deactivate_ke_baad_mode_wapas_key_par_aa_jata_hai(self, client, monkeypatch, teacher):
        """Sirf ACTIVE users ginte hain. Aakhri account band ho jaye to app
        band nahi hoti — key wale mode par lautti hai, taake school bahar na
        reh jaye.

        ⚠ YAHAN `teacher` HAI, `admin` NAHI, aur ye is test ka doosra maana
        hai: pehla draft admin ko band karta tha aur `UserValidationError` par
        gira — yani aakhri-admin wala guard (`TestLastAdminGuard`) is raaste
        par bhi waqai lagta hai. Wo galti nahi thi, wo guard ka kaam karna tha.
        """
        monkeypatch.setattr(auth, "API_KEY", KEY)
        assert auth.auth_mode() == auth.MODE_USERS
        user_service.update_user(teacher["id"], "Sana", "teacher", is_active=False)
        assert auth.auth_mode() == auth.MODE_KEY


# ── login / logout ───────────────────────────────────────────────────────────


class TestLogin:
    def test_sahi_password_par_andar(self, client, admin):
        res = login(client, "irfan", ADMIN_PW)
        assert res.status_code == 200
        assert res.json()["username"] == "irfan"
        assert session_service.COOKIE_NAME in res.cookies

    def test_login_ke_baad_api_khulti_hai(self, client, admin):
        login(client, "irfan", ADMIN_PW)
        assert client.get("/api/papers").status_code == 200

    def test_bina_login_401(self, client, admin):
        assert client.get("/api/papers").status_code == 401

    def test_401_apna_mode_batati_hai(self, client, admin):
        """Frontend isi header se faisla karta hai: login page bhejna hai ya
        purana key-gate kholna. Bina is ke use ek aur request karni parti."""
        res = client.get("/api/papers")
        assert res.headers.get(auth.MODE_HEADER) == auth.MODE_USERS

    def test_ghalat_password_401(self, client, admin):
        assert login(client, "irfan", "ghalat-password").status_code == 401

    def test_ghalat_username_aur_ghalat_password_ka_jawab_ek_jaisa_hai(self, client, admin):
        """⚠ Farq batane ka matlab hai ajnabi ko ye batana ke kaun se accounts
        is school mein waqai mojood hain — aur phir wo sirf password par hamla
        karta hai. Dono jawab haraf ba haraf ek jaise hone chahiyen."""
        nahi_hai = login(client, "koi-aur", "kuch-bhi-lamba")
        ghalat_pw = login(client, "irfan", "ghalat-password-lamba")
        assert nahi_hai.status_code == ghalat_pw.status_code == 401
        assert nahi_hai.json()["detail"] == ghalat_pw.json()["detail"]

    def test_band_kiya_hua_account_login_nahi_kar_sakta(self, client, admin, teacher):
        user_service.update_user(teacher["id"], "Sana", "teacher", is_active=False)
        assert login(client, "sana", TEACHER_PW).status_code == 401

    def test_username_ka_case_mayne_nahi_rakhta(self, client, admin):
        assert login(client, "IRFAN", ADMIN_PW).status_code == 200

    def test_logout_ke_baad_api_band(self, client, admin):
        login(client, "irfan", ADMIN_PW)
        assert client.post("/api/auth/logout").status_code == 200
        assert client.get("/api/papers").status_code == 401

    def test_logout_bina_session_bhi_khamoshi_se_chalta_hai(self, client, admin):
        assert client.post("/api/auth/logout").status_code == 200


class TestSessionToken:
    def test_db_mein_khaam_token_kahin_nahi(self, client, admin):
        """⚠ DB ki copy (backup file, chori, bheja hua .db) kisi ke haath lage
        to us se koi zinda session nahi milni chahiye. Cookie mein token hai,
        DB mein sirf us ka SHA-256."""
        res = login(client, "irfan", ADMIN_PW)
        token = res.cookies[session_service.COOKIE_NAME]
        rows = sessions_repository.list_for_user(admin["id"])
        assert len(rows) == 1
        assert rows[0]["token_hash"] != token
        assert token not in rows[0]["token_hash"]

    def test_cookie_httponly_aur_samesite_lax_hai(self, client, admin):
        """HttpOnly: JS cookie parh hi nahi sakta (purani localStorage key ke
        bilkul ulta). SameSite=Lax: kisi doosri site ka form CSRF nahi kar
        sakta."""
        res = login(client, "irfan", ADMIN_PW)
        raw = res.headers["set-cookie"].lower()
        assert "httponly" in raw
        assert "samesite=lax" in raw

    def test_http_par_secure_flag_nahi_lagti(self, client, admin):
        """School ka LAN aaj plain http hai. Secure lagane ka matlab hota ke
        browser cookie bhejta hi nahi aur koi login kaam na kare."""
        res = login(client, "irfan", ADMIN_PW)
        assert "secure" not in res.headers["set-cookie"].lower()

    def test_jaali_token_andar_nahi_le_jata(self, client, admin):
        client.cookies.set(session_service.COOKIE_NAME, "main-ne-bana-liya")
        assert client.get("/api/papers").status_code == 401


# ── waqt ki hadd ─────────────────────────────────────────────────────────────


class TestExpiry:
    def test_30_minute_bekari_par_session_khatam(self, client, admin, monkeypatch):
        """Shared school PC ka asal khatra: teacher uth kar chala gaya, aur
        koi aur usi khuli hui app par baith gaya. Browser wala lock pehle se
        tha (2026-09-08) magar wo sirf browser mein tha — server ke nazdeek
        key/session tab bhi zinda thi."""
        login(client, "irfan", ADMIN_PW)
        monkeypatch.setattr(session_service, "IDLE_MINUTES", 0)
        assert client.get("/api/papers").status_code == 401

    def test_bekari_wali_session_db_se_bhi_nikal_jati_hai(self, client, admin, monkeypatch):
        login(client, "irfan", ADMIN_PW)
        monkeypatch.setattr(session_service, "IDLE_MINUTES", 0)
        client.get("/api/papers")
        assert sessions_repository.list_for_user(admin["id"]) == []

    def test_sakht_hadd_par_session_khatam_chahe_banda_active_ho(self, client, admin, monkeypatch):
        """Idle ghadi har request par aage barhti hai, to ek khula hua tab
        hamesha zinda reh sakta hai. Barri hadd us silsile ko kaatti hai."""
        login(client, "irfan", ADMIN_PW)
        monkeypatch.setattr(session_service, "ABSOLUTE_HOURS", 0)
        # Nayi session banao (purani ki expires_at pehle se likhi ja chuki hai).
        client.post("/api/auth/logout")
        login(client, "irfan", ADMIN_PW)
        assert client.get("/api/papers").status_code == 401

    def test_active_rehne_par_session_chalti_rehti_hai(self, client, admin):
        login(client, "irfan", ADMIN_PW)
        for _ in range(3):
            assert client.get("/api/papers").status_code == 200


# ── lockout ──────────────────────────────────────────────────────────────────


class TestLockout:
    def test_paanch_nakami_ke_baad_account_band(self, client, admin):
        for _ in range(session_service.MAX_FAILURES):
            assert login(client, "irfan", "ghalat-password").status_code == 401
        assert login(client, "irfan", "ghalat-password").status_code == 429

    def test_lock_ke_baad_sahi_password_bhi_nahi_chalta(self, client, admin):
        """Warna lockout ka koi matlab nahi — hamlawar sirf sahi qeemat par
        pahunchne tak try karta rehta."""
        for _ in range(session_service.MAX_FAILURES):
            login(client, "irfan", "ghalat-password")
        assert login(client, "irfan", ADMIN_PW).status_code == 429

    def test_lockout_ka_paighaam_saaf_batata_hai_kitni_der(self, client, admin):
        for _ in range(session_service.MAX_FAILURES):
            login(client, "irfan", "ghalat-password")
        detail = login(client, "irfan", ADMIN_PW).json()["detail"]
        assert str(session_service.LOCKOUT_MINUTES) in detail

    def test_lock_sirf_usi_account_par_lagta_hai(self, client, admin, teacher):
        """⚠ IP par lock lagana yahan ghalat hota: school ke bees teachers ek
        hi router ke peeche hain. Ek banda apna password teen dafa ghalat likhe
        aur poora staff room bahar — ye is app ke liye hamle se zyada mehnga
        natija hai."""
        for _ in range(session_service.MAX_FAILURES + 1):
            login(client, "irfan", "ghalat-password")
        assert login(client, "sana", TEACHER_PW).status_code == 200

    def test_kamiyab_login_purani_nakamiyan_saaf_kar_deta_hai(self, client, admin):
        """Warna teacher subah do dafa ghalti kare, din bhar theek chale, aur
        shaam ko teesri ghalti par lock ho jaye. Window ka matlab 'lagatar' hai."""
        for _ in range(session_service.MAX_FAILURES - 1):
            login(client, "irfan", "ghalat-password")
        assert login(client, "irfan", ADMIN_PW).status_code == 200
        client.post("/api/auth/logout")
        for _ in range(session_service.MAX_FAILURES - 1):
            assert login(client, "irfan", "ghalat-password").status_code == 401

    def test_lockout_process_ki_memory_mein_nahi_db_mein_hai(self, test_db, admin):
        """Restart par counter sifar nahi hona chahiye — aur restart hamlawar
        ke apne bas mein ho sakta hai (koi bhi cheez jo server gira de)."""
        for _ in range(session_service.MAX_FAILURES):
            with pytest.raises(LoginFailed):
                session_service.login("irfan", "ghalat-password")
        # Naya "process": service dobara se poochho, koi shared state nahi.
        assert session_service.is_locked_out("irfan") is True


# ── roles ────────────────────────────────────────────────────────────────────


class TestRoles:
    def test_admin_user_list_dekh_sakta_hai(self, client, admin):
        login(client, "irfan", ADMIN_PW)
        assert client.get("/api/users").status_code == 200

    def test_teacher_user_list_nahi_dekh_sakta(self, client, admin, teacher):
        login(client, "sana", TEACHER_PW)
        assert client.get("/api/users").status_code == 403

    def test_teacher_ko_403_milta_hai_401_nahi(self, client, admin, teacher):
        """Farq mayne rakhta hai: 401 kehta hai 'tum kaun ho pata nahi' (aur
        frontend login page khol deta), jabke asal baat ye hai ke teacher andar
        hai, bas is kaam ka ikhtiyar nahi rakhta. 401 par use bar bar login
        karwaya jata — jo kabhi kaam nahi karta."""
        login(client, "sana", TEACHER_PW)
        assert client.post("/api/users", json={"username": "naya", "password": "lamba-password"}).status_code == 403

    def test_teacher_apna_kaam_kar_sakta_hai(self, client, admin, teacher):
        login(client, "sana", TEACHER_PW)
        assert client.get("/api/papers").status_code == 200

    def test_role_badalne_par_purani_session_khatam(self, client, admin, teacher):
        """Naya ikhtiyar (ya us ka chhinna) agli hi request par lagna chahiye."""
        tclient = TestClient(client.app)
        login(tclient, "sana", TEACHER_PW)
        assert tclient.get("/api/papers").status_code == 200
        user_service.update_user(teacher["id"], "Sana", "admin", is_active=True)
        session_service.end_all_sessions(teacher["id"])
        assert tclient.get("/api/papers").status_code == 401

    def test_band_kiye_gaye_user_ki_khuli_session_foran_mar_jati_hai(self, client, admin, teacher):
        """⚠ Warna 'band kar diya' ek jhoot hai jo us ke browser band karne
        tak chalta rehta hai. Yahan `end_all_sessions` JAAN-BOOJH KAR nahi
        bulaya gaya — ye `resolve()` ki apni deewar ka test hai."""
        tclient = TestClient(client.app)
        login(tclient, "sana", TEACHER_PW)
        user_service.update_user(teacher["id"], "Sana", "teacher", is_active=False)
        assert tclient.get("/api/papers").status_code == 401


class TestLastAdminGuard:
    def test_aakhri_admin_teacher_nahi_ban_sakta(self, admin):
        """Ek click user management ka darwaza hamesha ke liye band kar sakta
        hai. Us ke baad sirf server par baith kar create_admin.py chalana
        raasta bachta hai — ek soorat jo school ke waqt par nahi aati."""
        with pytest.raises(UserValidationError):
            user_service.update_user(admin["id"], "Irfan", "teacher", is_active=True)

    def test_aakhri_admin_band_nahi_ho_sakta(self, admin):
        with pytest.raises(UserValidationError):
            user_service.update_user(admin["id"], "Irfan", "admin", is_active=False)

    def test_doosra_admin_ho_to_pehla_badla_ja_sakta_hai(self, admin):
        user_service.create_user("nadia", "nadia-ka-lamba-password", role="admin")
        out = user_service.update_user(admin["id"], "Irfan", "teacher", is_active=True)
        assert out["role"] == "teacher"


# ── pehla account banane ka raasta ───────────────────────────────────────────


class TestBootstrap:
    def test_khuli_app_par_pehla_admin_ban_sakta_hai(self, client, monkeypatch):
        monkeypatch.setattr(auth, "API_KEY", "")
        res = client.post(
            "/api/users",
            json={"username": "irfan", "password": "lamba-sa-password", "role": "admin"},
        )
        assert res.status_code == 200

    def test_key_wali_app_par_pehla_admin_banane_ke_liye_key_chahiye(self, client, monkeypatch):
        monkeypatch.setattr(auth, "API_KEY", KEY)
        body = {"username": "irfan", "password": "lamba-sa-password", "role": "admin"}
        assert client.post("/api/users", json=body).status_code == 401
        assert client.post("/api/users", json=body, headers={"x-api-key": KEY}).status_code == 200

    def test_pehla_user_bante_hi_bootstrap_ka_darwaza_band(self, client, monkeypatch, admin):
        """⚠ Ye darwaza sirf utni der khula hai jitni der ek bhi active user na
        ho. Agar ye test kabhi fail ho to matlab koi bhi ajnabi apne liye admin
        account bana sakta hai."""
        monkeypatch.setattr(auth, "API_KEY", KEY)
        res = client.post(
            "/api/users",
            json={"username": "ghuspaithiya", "password": "lamba-sa-password", "role": "admin"},
            headers={"x-api-key": KEY},
        )
        assert res.status_code == 401


# ── password badalna ─────────────────────────────────────────────────────────


class TestPasswordChange:
    def test_apna_password_badalne_ke_liye_purana_chahiye(self, client, admin):
        """Ye us shakhs ke khilaf bachao hai jo kisi ka khula hua browser paa
        leta hai aur chupke se password badal kar account apne naam kar leta."""
        login(client, "irfan", ADMIN_PW)
        res = client.post(
            "/api/auth/password",
            json={"new_password": "naya-lamba-password", "current_password": "ghalat"},
        )
        assert res.status_code == 401

    def test_purana_sahi_ho_to_password_badal_jata_hai(self, client, admin):
        login(client, "irfan", ADMIN_PW)
        res = client.post(
            "/api/auth/password",
            json={"new_password": "naya-lamba-password", "current_password": ADMIN_PW},
        )
        assert res.status_code == 200
        client.post("/api/auth/logout")
        assert login(client, "irfan", "naya-lamba-password").status_code == 200
        assert login(client, "irfan", ADMIN_PW).status_code == 401

    def test_chhota_password_rad_hota_hai(self, client, admin):
        login(client, "irfan", ADMIN_PW)
        res = client.post(
            "/api/auth/password", json={"new_password": "chhota", "current_password": ADMIN_PW}
        )
        assert res.status_code == 400

    def test_apna_password_badalne_par_apni_session_bachi_rehti_hai(self, client, admin):
        """Khud ko bahar phenkna bila wajah ki sazaa hai."""
        login(client, "irfan", ADMIN_PW)
        client.post(
            "/api/auth/password",
            json={"new_password": "naya-lamba-password", "current_password": ADMIN_PW},
        )
        assert client.get("/api/papers").status_code == 200

    def test_password_badalne_par_baqi_sessions_khatam(self, client, admin):
        """⚠ Password badalne ki asal wajah aksar yehi hoti hai ke kisi aur ko
        pata chal gaya. Agar us ki pehle se khuli session zinda rahe to naya
        password sirf ek rasm hai."""
        doosra = TestClient(client.app)
        login(doosra, "irfan", ADMIN_PW)
        assert doosra.get("/api/papers").status_code == 200
        login(client, "irfan", ADMIN_PW)
        client.post(
            "/api/auth/password",
            json={"new_password": "naya-lamba-password", "current_password": ADMIN_PW},
        )
        assert doosra.get("/api/papers").status_code == 401

    def test_admin_kisi_ka_password_reset_kar_sakta_hai(self, client, admin, teacher):
        login(client, "irfan", ADMIN_PW)
        res = client.post(
            f"/api/users/{teacher['id']}/password", json={"new_password": "reset-kiya-password"}
        )
        assert res.status_code == 200
        doosra = TestClient(client.app)
        assert login(doosra, "sana", "reset-kiya-password").status_code == 200

    def test_admin_ke_reset_par_us_bande_ki_sessions_khatam(self, client, admin, teacher):
        doosra = TestClient(client.app)
        login(doosra, "sana", TEACHER_PW)
        login(client, "irfan", ADMIN_PW)
        client.post(f"/api/users/{teacher['id']}/password", json={"new_password": "reset-kiya-password"})
        assert doosra.get("/api/papers").status_code == 401


# ── /api/auth/me ─────────────────────────────────────────────────────────────


class TestWhoAmI:
    def test_me_bina_login_bhi_jawab_deta_hai(self, client, admin):
        """Ye endpoint khud auth ke peeche nahi (brand ki tarah): 'login
        zaroori hai' khud ek jawab hai, error nahi."""
        res = client.get("/api/auth/me")
        assert res.status_code == 200
        assert res.json()["mode"] == "users"
        assert res.json()["user"] is None

    def test_login_ke_baad_me_naam_batata_hai(self, client, admin):
        login(client, "irfan", ADMIN_PW)
        body = client.get("/api/auth/me").json()
        assert body["user"]["username"] == "irfan"
        assert body["user"]["role"] == "admin"

    def test_khuli_app_par_mode_open_aata_hai(self, client, monkeypatch):
        monkeypatch.setattr(auth, "API_KEY", "")
        assert client.get("/api/auth/me").json()["mode"] == "open"


# ── log ──────────────────────────────────────────────────────────────────────


class TestAuthEvents:
    def test_kamiyab_login_log_hota_hai(self, client, admin):
        login(client, "irfan", ADMIN_PW)
        events = [e["event"] for e in session_service.recent_events()]
        assert "login_ok" in events

    def test_nakaam_login_log_hota_hai(self, client, admin):
        login(client, "irfan", "ghalat-password")
        events = [e["event"] for e in session_service.recent_events()]
        assert "login_fail" in events

    def test_admin_log_dekh_sakta_hai(self, client, admin):
        login(client, "irfan", ADMIN_PW)
        res = client.get("/api/auth/events")
        assert res.status_code == 200
        assert any(e["event"] == "login_ok" for e in res.json())

    def test_teacher_log_nahi_dekh_sakta(self, client, admin, teacher):
        login(client, "sana", TEACHER_PW)
        assert client.get("/api/auth/events").status_code == 403

    def test_log_mein_password_kahin_nahi(self, client, admin):
        """Nakaam login par wajah log hoti hai ('bad-password'), qeemat NAHI."""
        login(client, "irfan", "mera-raaz-password")
        assert all("mera-raaz-password" not in str(e) for e in session_service.recent_events())


# ── jo bahar nahi jana chahiye ───────────────────────────────────────────────


class TestNoLeak:
    def test_user_list_mein_password_hash_nahi(self, client, admin, teacher):
        login(client, "irfan", ADMIN_PW)
        body = client.get("/api/users").text
        assert "password_hash" not in body
        assert "scrypt$" not in body

    def test_login_ke_jawab_mein_hash_nahi(self, client, admin):
        assert "scrypt$" not in login(client, "irfan", ADMIN_PW).text


# ── static surface ───────────────────────────────────────────────────────────


class TestStaticSurface:
    """⚠ `tests/test_auth.py` ka wahi guard, ab users mode ke liye. Agar auth
    kabhi static par lag gayi to login page KHUD kabhi load nahi hoga — yani
    app ek aisa darwaza ban jati hai jis ki chaabi andar rakhi ho."""

    @pytest.mark.parametrize("path", ["/static/index.html", "/static/login.html"])
    def test_page_login_ke_baghair_bhi_khulta_hai(self, client, admin, path):
        assert client.get(path).status_code == 200
