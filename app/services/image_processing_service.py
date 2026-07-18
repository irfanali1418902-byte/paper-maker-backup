"""Uploaded library images ko WebP mein convert karta hai — smart lossy/lossless.

HISSA 2 + Smart Lossy:
- Full:  max 1200px  -> static/library/{uuid}.webp
- Thumb: max 300px   -> static/library/thumbs/{uuid}.webp

Compression har image ke type se decide hota hai:
- Line drawing / trace / outline -> LOSSLESS (bacchon ke liye crisp, koi samjhauta nahi)
- Photo (rang zyada, gradients)   -> LOSSY quality 85 (zyada jagah bachao)
Ambiguous case hamesha lossless ki taraf jhukta hai (safety).

Purani JPG/PNG images ko yahan haath nahi lagaya jaata (HISSA 3 Bulk Convert).
"""

import io
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps

_FULL_MAX = 1200
_THUMB_MAX = 300
# Decompression-bomb guard: file bytes chhoti ho sakti hain par pixels bahut zyada
# (e.g. 30000x30000) — decode par gigabytes RAM. 50 MP high-res scans ke liye kaafi hai.
_MAX_PIXELS = 50_000_000

# Smart compression tuning
_LOSSY_QUALITY = 85
_QUANT_SHIFT = 3  # 8-bit channel -> 5-bit (32 levels): AA ke halke shades ek bucket mein
_COVERAGE_TARGET = 0.85  # itni coverage tak dominant buckets ginte hain
# 85% coverage kitne buckets me aata hai: flat art -> thode buckets, photo -> bohot.
# 40 do populations ke beech ke khaali gap me baitha hai (real uploads par mapa:
# line-art-side <=29 par rukta hai, photo-side 41 se shuru; 30-40 khaali). Isliye
# yeh magic number nahi — ±5 hilne par bhi split nahi tootta.
_MAX_BUCKETS_LOSSLESS = 40

# Saturation gate: detailed B/W line-art (grey shading, dense stippling) buckets me photos se
# OVERLAP karta hai (misaal: sharpener_bw 51, walnut_bw 55 vs cat_c 56) — buckets akele in dono
# ko alag nahi kar sakte. Lekin B/W drawing chahe kitni detailed ho, uski saturation ~0 hoti hai.
# Real library par mapa: _bw sat-frac <=0.122, _c >=0.104. 0.14 sab _bw ko pakadta hai (+margin);
# thodi muted-colour photos lossless jaa sakti hain -> sirf storage cost, quality nahi (safety bias).
_SAT_PIXEL_MIN = 40  # HSV S is se upar = "meaningful" rang (AA/JPEG noise neeche)
_SAT_LOSSLESS_MAX = 0.14  # itne se kam pixels saturated -> grayscale drawing -> lossless


def _has_transparency(img: Image.Image) -> bool:
    """True agar image mein sach-much transparent pixels hain (ya palette transparency)."""
    if "transparency" in img.info:
        return True
    if img.mode in ("RGBA", "LA"):
        alpha = img.getchannel("A")
        return alpha.getextrema()[0] < 255
    return False


def _has_graphic_signals(img: Image.Image) -> bool:
    """Mode-based hard signals — in par seedha lossless (coverage check ki zaroorat nahi).

    - Bilevel (mode "1")  -> definitely line art
    - Palette (mode "P")  -> <=256 colours graphic
    - Real transparency   -> sticker/graphic
    NOTE: grayscale "L" ko yahan lossless force NAHI karte — B/W photo bhi ho sakta hai;
    usko coverage decide karega.
    """
    if img.mode in ("1", "P"):
        return True
    return _has_transparency(img)


def _buckets_to_cover(img: Image.Image, target: float = _COVERAGE_TARGET) -> int:
    """Kitne dominant colour-buckets milkar `target` (85%) pixels cover karte hain.

    Colours ko quantize (>>3, 32 levels/channel) karke AA ka noise merge karte hain,
    phir buckets ko ghatte order me jodte hain jab tak `target` coverage na aa jaye.
    Flat line-art: chand flat rang (bg + ink) poori image cover karte hain -> bohot kam
    buckets. Photo: rang gradients me phaile -> 85% tak pahunchne me bohot buckets lagte hain.

    NOTE: yeh "kitne buckets" wala metric purane "top-8 coverage" se behtar hai kyunki
    rich flat art (10-15 flat rang) me bhi buckets kam rehte hain -> lossless bacha rehta hai;
    fixed top-N unhe galti se lossy kar deta tha.
    """
    rgb = img.convert("RGB")
    arr = np.asarray(rgb, dtype=np.uint16)  # H x W x 3
    q = arr >> _QUANT_SHIFT  # 0..31 per channel
    codes = (q[..., 0] << 10) | (q[..., 1] << 5) | q[..., 2]
    flat = codes.ravel()
    if flat.size == 0:
        return 1  # khaali/degenerate -> kam buckets -> safe lossless
    counts = np.bincount(flat)
    counts = np.sort(counts[counts > 0])[::-1]  # sirf maujood buckets, ghatte order
    cum = np.cumsum(counts) / flat.size
    return int(np.searchsorted(cum, target) + 1)


def _is_line_art(img: Image.Image) -> bool:
    """Kam buckets me 85% coverage -> flat line-art -> lossless; bohot buckets -> photo -> lossy."""
    return _buckets_to_cover(img) <= _MAX_BUCKETS_LOSSLESS


def _is_low_saturation(img: Image.Image) -> bool:
    """True agar image asal me grayscale hai (B/W drawing) — bahut kam saturated pixels.

    Detailed B/W line-art (shading/stippling) bucket-count me photos se milta-julta hai, par
    saturation se saaf alag hota hai. Yeh gate detailed drawings ko lossless bacha leta hai.
    """
    hsv = np.asarray(img.convert("HSV"))
    sat = hsv[..., 1]
    if sat.size == 0:
        return True  # khaali -> grayscale maan lo (safe lossless)
    return float((sat > _SAT_PIXEL_MIN).mean()) < _SAT_LOSSLESS_MAX


def _choose_compression(full: Image.Image, force_lossless: bool) -> str:
    """'lossless' ya 'lossy' — hard signals, phir saturation gate, phir bucket detection.

    1. force_lossless (mode 1/P/transparency)  -> lossless
    2. near-grayscale (B/W drawing, detailed bhi) -> lossless
    3. colour: flat graphic (kam buckets) -> lossless, warna photo -> lossy
    """
    if force_lossless:
        return "lossless"
    if _is_low_saturation(full):
        return "lossless"
    return "lossless" if _is_line_art(full) else "lossy"


def process_and_save(contents: bytes, image_id: str, library_dir: Path) -> dict:
    """Bytes se do WebP files (full + thumb) banata hai, smart lossy/lossless.

    `library_dir` = physical library folder (static/library ya test ka tmp).
    Full yahin likhti hai, thumb `library_dir/thumbs/` mein. Dono ek hi compression mode use karte hain.
    Returns: {"file_path": ..., "thumb_path": ..., "compression": "lossless"|"lossy"}
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

    # Graphic signals mode-normalization se PEHLE capture karo (P->RGBA palette signal kho deta hai)
    force_lossless = _has_graphic_signals(img)

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

    # Compression faisla resized full par (jo save bhi ho rahi hai)
    compression = _choose_compression(full, force_lossless)
    if compression == "lossless":
        save_kwargs = {"lossless": True, "method": 6}
    else:
        save_kwargs = {"quality": _LOSSY_QUALITY, "method": 6}

    full.save(full_dest, format="WEBP", **save_kwargs)

    # Thumb: alag copy, full jaisa hi compression mode
    thumb = img.copy()
    thumb.thumbnail((_THUMB_MAX, _THUMB_MAX), Image.LANCZOS)
    thumb.save(thumb_dest, format="WEBP", **save_kwargs)

    return {
        "file_path": f"library/{image_id}.webp",
        "thumb_path": f"library/thumbs/{image_id}.webp",
        "compression": compression,
    }
