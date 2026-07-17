"""HISSA A tests — Smart Image Library: DB migration, search, filter, PATCH naye fields.

test_db fixture fresh SQLite deta hai; _LIBRARY_DIR monkeypatched.
"""

import io

from fastapi.testclient import TestClient

import app.api.library as library_module
from app.core import database
from app.main import app

client = TestClient(app)

_PNG = (
    b"\x89PNG\r\n\x1a\n"
    b"\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x02\x00\x00\x00\x90wS\xde"
    b"\x00\x00\x00\x0cIDATx\x9cc\xf8\xff\xff?\x00\x05\xfe\x02\xfe\r\xefF\xb8"
    b"\x00\x00\x00\x00IEND\xaeB`\x82"
)


def _upload(tmp_path, monkeypatch, *, name="TestImg", mime="image/png"):
    lib = tmp_path / "library"
    lib.mkdir(exist_ok=True)
    monkeypatch.setattr(library_module, "_LIBRARY_DIR", lib)
    resp = client.post(
        "/api/library",
        data={"name": name},
        files={"file": ("img.png", io.BytesIO(_PNG), mime)},
    )
    assert resp.status_code == 200
    return resp.json()["id"]


# ---------------------------------------------------------------------------
# 1. DB Migration idempotent
# ---------------------------------------------------------------------------

def test_migration_idempotent(tmp_path, monkeypatch):
    """init_db() dusri baar chalane se koi error nahi aana chahiye."""
    monkeypatch.setattr(database, "DB_PATH", tmp_path / "test.db")
    database.init_db()
    database.init_db()  # dusri baar — idempotent


def test_new_columns_exist_after_migration(test_db):
    """image_library table mein 5 naye columns hone chahiye."""
    conn = database.get_connection()
    cols = {row[1] for row in conn.execute("PRAGMA table_info(image_library)").fetchall()}
    conn.close()
    assert "keywords" in cols
    assert "question_types" in cols
    assert "category" in cols
    assert "source_book" in cols
    assert "page_number" in cols


# ---------------------------------------------------------------------------
# 2. PATCH — naye fields save hote hain
# ---------------------------------------------------------------------------

def test_patch_saves_keywords(test_db, tmp_path, monkeypatch):
    img_id = _upload(tmp_path, monkeypatch, name="Apple Fruit")
    resp = client.patch(f"/api/library/{img_id}", json={"keywords": "apple, fruit, red"})
    assert resp.status_code == 200
    assert resp.json()["keywords"] == "apple, fruit, red"


def test_patch_saves_question_types(test_db, tmp_path, monkeypatch):
    img_id = _upload(tmp_path, monkeypatch, name="Counting Stars")
    resp = client.patch(f"/api/library/{img_id}", json={"question_types": "count, identify"})
    assert resp.status_code == 200
    assert resp.json()["question_types"] == "count, identify"


def test_patch_saves_category(test_db, tmp_path, monkeypatch):
    img_id = _upload(tmp_path, monkeypatch, name="Mango")
    resp = client.patch(f"/api/library/{img_id}", json={"category": "fruit"})
    assert resp.status_code == 200
    assert resp.json()["category"] == "fruit"


def test_patch_saves_source_book_and_page(test_db, tmp_path, monkeypatch):
    img_id = _upload(tmp_path, monkeypatch, name="Triangle Shape")
    resp = client.patch(
        f"/api/library/{img_id}",
        json={"source_book": "Maths Book 3", "page_number": 42},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["source_book"] == "Maths Book 3"
    assert data["page_number"] == 42


def test_patch_all_smart_fields_at_once(test_db, tmp_path, monkeypatch):
    img_id = _upload(tmp_path, monkeypatch, name="Blue Circle")
    resp = client.patch(
        f"/api/library/{img_id}",
        json={
            "keywords": "circle, blue, shape",
            "question_types": "colour, match",
            "category": "shape",
            "source_book": "Art Book 1",
            "page_number": 7,
        },
    )
    assert resp.status_code == 200
    d = resp.json()
    assert d["keywords"] == "circle, blue, shape"
    assert d["question_types"] == "colour, match"
    assert d["category"] == "shape"
    assert d["source_book"] == "Art Book 1"
    assert d["page_number"] == 7


# ---------------------------------------------------------------------------
# 3. Search — naam + keywords + category se
# ---------------------------------------------------------------------------

def test_search_by_name(test_db, tmp_path, monkeypatch):
    _upload(tmp_path, monkeypatch, name="Parrot Bird")
    resp = client.get("/api/library?q=parrot")
    assert resp.status_code == 200
    names = [i["name"] for i in resp.json()["images"]]
    assert "Parrot Bird" in names


def test_search_by_keyword(test_db, tmp_path, monkeypatch):
    img_id = _upload(tmp_path, monkeypatch, name="Green Fruit")
    client.patch(f"/api/library/{img_id}", json={"keywords": "mango, tropical, green"})
    resp = client.get("/api/library?q=tropical")
    assert resp.status_code == 200
    ids = [i["id"] for i in resp.json()["images"]]
    assert img_id in ids


def test_search_by_category_field(test_db, tmp_path, monkeypatch):
    img_id = _upload(tmp_path, monkeypatch, name="Sunflower")
    client.patch(f"/api/library/{img_id}", json={"category": "plant"})
    resp = client.get("/api/library?q=plant")
    assert resp.status_code == 200
    ids = [i["id"] for i in resp.json()["images"]]
    assert img_id in ids


def test_search_empty_returns_all(test_db, tmp_path, monkeypatch):
    _upload(tmp_path, monkeypatch, name="ImgA")
    _upload(tmp_path, monkeypatch, name="ImgB")
    resp = client.get("/api/library")
    assert resp.status_code == 200
    assert len(resp.json()["images"]) >= 2


def test_search_null_keywords_not_crash(test_db, tmp_path, monkeypatch):
    """Purani image (keywords=NULL) hone par search crash nahi karna chahiye."""
    _upload(tmp_path, monkeypatch, name="OldImage")
    resp = client.get("/api/library?q=something")
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# 4. Filter — category aur question_type
# ---------------------------------------------------------------------------

def test_filter_by_category(test_db, tmp_path, monkeypatch):
    id1 = _upload(tmp_path, monkeypatch, name="Cat Animal")
    id2 = _upload(tmp_path, monkeypatch, name="Rose Flower")
    client.patch(f"/api/library/{id1}", json={"category": "animal"})
    client.patch(f"/api/library/{id2}", json={"category": "flower"})

    resp = client.get("/api/library?category=animal")
    assert resp.status_code == 200
    ids = [i["id"] for i in resp.json()["images"]]
    assert id1 in ids
    assert id2 not in ids


def test_filter_by_question_type(test_db, tmp_path, monkeypatch):
    id1 = _upload(tmp_path, monkeypatch, name="Counting Apples")
    id2 = _upload(tmp_path, monkeypatch, name="Match Shapes")
    client.patch(f"/api/library/{id1}", json={"question_types": "count, identify"})
    client.patch(f"/api/library/{id2}", json={"question_types": "match, colour"})

    resp = client.get("/api/library?question_type=count")
    assert resp.status_code == 200
    ids = [i["id"] for i in resp.json()["images"]]
    assert id1 in ids
    assert id2 not in ids


def test_filter_question_type_null_images_excluded(test_db, tmp_path, monkeypatch):
    """question_types=NULL wali images filter mein nahi aani chahiye."""
    img_id = _upload(tmp_path, monkeypatch, name="NoTypeImage")
    resp = client.get("/api/library?question_type=count")
    assert resp.status_code == 200
    ids = [i["id"] for i in resp.json()["images"]]
    assert img_id not in ids


# ---------------------------------------------------------------------------
# 5. GET /api/library/categories + /api/library/question-types
# ---------------------------------------------------------------------------

def test_categories_endpoint(test_db, tmp_path, monkeypatch):
    id1 = _upload(tmp_path, monkeypatch, name="Dog")
    id2 = _upload(tmp_path, monkeypatch, name="Cat")
    client.patch(f"/api/library/{id1}", json={"category": "Animal"})
    client.patch(f"/api/library/{id2}", json={"category": "animal"})  # duplicate, different case

    resp = client.get("/api/library/categories")
    assert resp.status_code == 200
    cats = resp.json()["categories"]
    assert cats.count("animal") == 1  # deduplicated


def test_question_types_endpoint(test_db, tmp_path, monkeypatch):
    img_id = _upload(tmp_path, monkeypatch, name="Balls")
    client.patch(f"/api/library/{img_id}", json={"question_types": "count, colour"})

    resp = client.get("/api/library/question-types")
    assert resp.status_code == 200
    types = resp.json()["question_types"]
    assert "count" in types
    assert "colour" in types
