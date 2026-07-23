"""Excel se SLO (Student Learning Outcomes) bulk import — Marhala 0.

Har row ek SLO. slo_code se pehchan hoti hai:
  - naya slo_code  -> ADD
  - pehle se maujood -> UPDATE (slo_text / bloom_level / strand refresh;
    created_at ko haath nahi lagate)
bloom_level cell khali ho to slo_text ke verb se auto-suggest hota hai; teacher
ne value di ho to wahi rehne di jaati hai. Ek row fail hone se baaki nahi rukti.
sequence (optional, INTEGER): asal kitab ki tarteeb — khali ho to NULL; number na
ho (e.g. "abc") to us row ko error (chupke null nahi). Baaqi extra columns ignore.
"""

from __future__ import annotations

import io
import uuid
from typing import Optional

import pandas as pd

from app.core.bloom_standards import suggest_bloom_from_text
from app.repositories import slo_repository

REQUIRED_COLUMNS = {"class", "subject", "slo_code", "slo_text"}
OPTIONAL_COLUMNS = {"bloom_level", "strand", "sequence"}


def _cell(row: pd.Series, col: str) -> Optional[str]:
    """Row se col ka string value — khali/NaN to None."""
    if col not in row.index:
        return None
    val = row[col]
    if pd.isna(val):
        return None
    s = str(val).strip()
    return s if s else None


def import_slos_from_excel(file_bytes: bytes) -> dict:
    """Excel/CSV bytes parse karke slo table mein add/update karo.

    Returns:
        {added, updated, errors, results: [{row, slo_code, status, reason?}]}
        status: "added" | "updated" | "error"
    Raises:
        ValueError: agar koi required column missing ho ya file parse na ho sake.
    """
    try:
        df = pd.read_excel(io.BytesIO(file_bytes), dtype=str)
    except Exception as exc:
        raise ValueError(f"Excel parse nahi hua: {exc}") from exc

    # Column names normalize karo (lowercase + strip) — meta-import jaisa.
    df.columns = [str(c).strip().lower() for c in df.columns]

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        cols = ", ".join(sorted(missing))
        raise ValueError(f"Excel mein ye zaroori column(s) nahi mile: {cols}")

    added = 0
    updated = 0
    errors = 0
    results = []

    for idx, row in df.iterrows():
        row_num = int(idx) + 2  # 1-based, +1 for header

        slo_code = _cell(row, "slo_code")
        class_name = _cell(row, "class")
        subject = _cell(row, "subject")
        slo_text = _cell(row, "slo_text")

        missing_fields = [
            label
            for label, val in (
                ("slo_code", slo_code),
                ("class", class_name),
                ("subject", subject),
                ("slo_text", slo_text),
            )
            if not val
        ]
        if missing_fields:
            errors += 1
            results.append({
                "row": row_num,
                "slo_code": slo_code or "(khali)",
                "status": "error",
                "reason": f"zaroori field(s) khali: {', '.join(missing_fields)}",
            })
            continue

        # bloom_level: teacher di ho to wahi; khali to slo_text se auto-suggest.
        bloom_level = _cell(row, "bloom_level")
        if not bloom_level:
            bloom_level = suggest_bloom_from_text(slo_text)

        strand = _cell(row, "strand")

        # sequence: khali -> None; number -> int; kuch aur (e.g. "abc") -> row error
        # (chupke null nahi, taake teacher ko galti pata chale). Float bhi jo poora
        # number ho (Excel "3.0") qubool.
        sequence: Optional[int] = None
        seq_raw = _cell(row, "sequence")
        if seq_raw is not None:
            try:
                seq_float = float(seq_raw)
                if seq_float != int(seq_float):
                    raise ValueError
                sequence = int(seq_float)
            except (ValueError, TypeError):
                errors += 1
                results.append({
                    "row": row_num,
                    "slo_code": slo_code,
                    "status": "error",
                    "reason": f"sequence poora number hona chahiye, mila: '{seq_raw}'",
                })
                continue

        try:
            existing = slo_repository.find_by_code(slo_code)
            if existing is None:
                slo_repository.insert({
                    "id": str(uuid.uuid4()),
                    "class": class_name,
                    "subject": subject,
                    "slo_code": slo_code,
                    "slo_text": slo_text,
                    "bloom_level": bloom_level,
                    "strand": strand,
                    "sequence": sequence,
                })
                added += 1
                results.append({"row": row_num, "slo_code": slo_code, "status": "added"})
            else:
                # UPDATE mode: draft dobara import ho sakti hai. slo_text/bloom_level/
                # strand/sequence refresh; created_at nahi badalta (update mein hai hi nahi).
                slo_repository.update_by_code(slo_code, {
                    "slo_text": slo_text,
                    "bloom_level": bloom_level,
                    "strand": strand,
                    "sequence": sequence,
                })
                updated += 1
                results.append({"row": row_num, "slo_code": slo_code, "status": "updated"})
        except Exception as exc:  # noqa: BLE001 — ek row fail se poora import na ruke
            errors += 1
            results.append({
                "row": row_num,
                "slo_code": slo_code,
                "status": "error",
                "reason": str(exc),
            })

    return {"added": added, "updated": updated, "errors": errors, "results": results}
