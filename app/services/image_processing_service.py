"""Uploaded library images ko WebP (full + thumbnail) mein convert karta hai.

HISSA 2: har naye upload par do lossless WebP copies banti hain —
- Full:  max 1200px  -> static/library/{uuid}.webp
- Thumb: max 300px   -> static/library/thumbs/{uuid}.webp

Trace/outline images ke liye dono LOSSLESS hain taake quality na gire.
Purani JPG/PNG images ko yahan haath nahi lagaya jaata (HISSA 3 Bulk Convert).
"""

import io
from pathlib import Path

from PIL import Image, ImageOps

_FULL_MAX = 1200
_THUMB_MAX = 300
# Decompression-bomb guard: file bytes chhoti ho sakti hain par pixels bahut zyada
# (e.g. 30000x30000) — decode par gigabytes RAM. 50 MP high-res scans ke liye kaafi hai.
_MAX_PIXELS = 50_000_000


def process_and_save(contents: bytes, image_id: str, library_dir: Path) -> dict:
    """Bytes se do lossless WebP files banata hai aur unke URL-relative paths wapas karta hai.

    `library_dir` = physical library folder (static/library ya test ka tmp).
    Full yahin likhti hai, thumb `library_dir/thumbs/` mein.
    Returns: {"file_path": "library/<id>.webp", "thumb_path": "library/thumbs/<id>.webp"}
    Corrupt / na-khulne wali image par ValueError raise hoti hai.
    """
    try:
        img = Image.open(io.BytesIO(contents))
    except Exception as exc:  # noqa: BLE001 - Pillow bahut se exception types phenkta hai
        raise ValueError("Image process nahi hui — file kharab ya support nahi.") from exc

    # Pixel guard bhaari decode se PEHLE (size header se milti hai — sasta reject)
    width, height = img.size
    if width * height > _MAX_PIXELS:
        raise ValueError(
            "Image ke dimensions bahut bade hain (50 MP se zyada). / Image resolution too large."
        )

    try:
        img.load()
    except Exception as exc:  # noqa: BLE001 - Pillow bahut se exception types phenkta hai
        raise ValueError("Image process nahi hui — file kharab ya support nahi.") from exc

    # Phone photos ka EXIF rotation theek karo
    img = ImageOps.exif_transpose(img)

    # Palette (P) images ko RGBA mein le aao taake WebP save saaf ho aur alpha bache
    if img.mode == "P":
        img = img.convert("RGBA")

    library_dir = Path(library_dir)
    thumbs_dir = library_dir / "thumbs"
    library_dir.mkdir(parents=True, exist_ok=True)
    thumbs_dir.mkdir(parents=True, exist_ok=True)

    full_dest = library_dir / f"{image_id}.webp"
    thumb_dest = thumbs_dir / f"{image_id}.webp"

    # Full: sirf tab chhota karo jab bada ho (upscale kabhi nahi). thumbnail() aspect ratio rakhta hai.
    full = img.copy()
    full.thumbnail((_FULL_MAX, _FULL_MAX), Image.LANCZOS)
    full.save(full_dest, format="WEBP", lossless=True, method=6)

    # Thumb: alag copy, lossless (outline crisp rahe)
    thumb = img.copy()
    thumb.thumbnail((_THUMB_MAX, _THUMB_MAX), Image.LANCZOS)
    thumb.save(thumb_dest, format="WEBP", lossless=True, method=6)

    return {"file_path": f"library/{image_id}.webp", "thumb_path": f"library/thumbs/{image_id}.webp"}
