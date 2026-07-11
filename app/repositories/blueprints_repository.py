"""SQL access for the blueprints table. No business logic, no HTTP."""

import json
from typing import Optional

from app.core.database import get_connection


def insert(blueprint_id: str, name: str, subject: Optional[str],
           grade: Optional[str], sections: list) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO blueprints (id, name, subject, grade, sections) VALUES (?,?,?,?,?)",
        (blueprint_id, name, subject, grade, json.dumps(sections)),
    )
    conn.commit()
    conn.close()


def find_by_id(blueprint_id: str) -> Optional[dict]:
    conn = get_connection()
    row = conn.execute("SELECT * FROM blueprints WHERE id = ?", (blueprint_id,)).fetchone()
    conn.close()
    if not row:
        return None
    d = dict(row)
    d["sections"] = json.loads(d["sections"])
    return d


def list_all(subject: Optional[str] = None) -> list:
    conn = get_connection()
    if subject:
        rows = conn.execute(
            "SELECT * FROM blueprints WHERE subject = ? OR subject IS NULL ORDER BY created_at DESC",
            (subject,),
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM blueprints ORDER BY created_at DESC").fetchall()
    conn.close()
    result = []
    for row in rows:
        d = dict(row)
        d["sections"] = json.loads(d["sections"])
        result.append(d)
    return result


def delete(blueprint_id: str) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM blueprints WHERE id = ?", (blueprint_id,))
    affected = cur.rowcount
    conn.commit()
    conn.close()
    return affected > 0
