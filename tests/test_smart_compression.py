"""Unit tests — smart lossy/lossless detection ke core functions.

Ye pure functions hain (PIL image andar, string/int bahar) — koi DB/client nahi.
numpy se controlled images bana kar exact bucket-count aur saturation-fraction test karte hain,
khaas taur par boundaries (N=40 buckets, 0.14 saturation).
"""

import numpy as np
from PIL import Image

from app.services.image_processing_service import (
    _MAX_BUCKETS_LOSSLESS,
    _SAT_LOSSLESS_MAX,
    _buckets_to_cover,
    _choose_compression,
    _is_line_art,
    _is_low_saturation,
)

# ---------------------------------------------------------------------------
# Image builders (chhoti, deterministic — resize nahi hota, exact counts bachte hain)
# ---------------------------------------------------------------------------

def _img(arr: np.ndarray) -> Image.Image:
    return Image.fromarray(arr.astype(np.uint8), "RGB")


def _solid(rgb, w=20, h=20) -> Image.Image:
    a = np.zeros((h, w, 3), np.uint8)
    a[:] = rgb
    return _img(a)


def _equal_colours(colours) -> Image.Image:
    """Har colour ko 1 pixel — sab equal area. Shape (1, N, 3)."""
    a = np.array(colours, np.uint8).reshape(1, len(colours), 3)
    return _img(a)


def _n_distinct_colours(n: int) -> Image.Image:
    """n alag quantized-distinct colours, equal area. buckets_to_85 = ceil(0.85*n)."""
    cols = [((i % 16) * 16, (i // 16) * 16, 0) for i in range(n)]
    return _equal_colours(cols)


def _near_gray_many() -> Image.Image:
    """64 light near-gray colours (base 176, +8 offsets) — bahut buckets par saturation kam.

    sharpener_bw / walnut_bw jaise: detailed B/W jise bucket-rule galti se lossy karta,
    par saturation gate lossless bacha leta hai. Har pixel S<=~31 (<40).
    """
    base = 176
    cols = [
        (base + 8 * a, base + 8 * b, base + 8 * c)
        for a in range(4)
        for b in range(4)
        for c in range(4)
    ]
    return _equal_colours(cols)  # 64 distinct -> buckets = ceil(0.85*64) = 55


def _mix_saturated(frac_sat: float, total: int = 200) -> Image.Image:
    """`frac_sat` hissa saturated (pure red S=255), baaki gray (S=0). frac(S>40) == frac_sat."""
    n_sat = round(frac_sat * total)
    cols = [(255, 0, 0)] * n_sat + [(128, 128, 128)] * (total - n_sat)
    return _equal_colours(cols)


# ===========================================================================
# _buckets_to_cover
# ===========================================================================

def test_buckets_flat_single_colour():
    """Ek hi flat colour -> 1 bucket (85% pehle hi bucket me)."""
    assert _buckets_to_cover(_solid((255, 255, 255))) == 1


def test_buckets_flat_two_colours():
    """60/40 do-colour -> 2 buckets (pehla 60% <85%, doosra milkar 100%)."""
    img = _equal_colours([(255, 255, 255)] * 60 + [(0, 0, 0)] * 40)
    assert _buckets_to_cover(img) == 2


def test_buckets_photo_like_many():
    """Random RGB noise (photo-jaisa) -> bahut buckets, N=40 se kaafi upar."""
    rng = np.random.default_rng(0)
    arr = rng.integers(0, 256, (50, 50, 3), dtype=np.uint8)
    assert _buckets_to_cover(_img(arr)) > _MAX_BUCKETS_LOSSLESS


def test_buckets_boundary_at_40():
    """47 equal colours -> ceil(0.85*47)=40 -> N=40 ke andar (lossless side)."""
    assert _buckets_to_cover(_n_distinct_colours(47)) == 40
    assert _is_line_art(_n_distinct_colours(47)) is True


def test_buckets_boundary_at_41():
    """48 equal colours -> ceil(0.85*48)=41 -> N=40 se bahar (lossy side)."""
    assert _buckets_to_cover(_n_distinct_colours(48)) == 41
    assert _is_line_art(_n_distinct_colours(48)) is False


def test_buckets_empty_returns_one():
    """Khaali/degenerate image -> 1 (safe lossless)."""
    assert _buckets_to_cover(Image.new("RGB", (0, 0))) == 1


# ===========================================================================
# _is_low_saturation
# ===========================================================================

def test_low_sat_pure_grayscale_true():
    """Pure grayscale B/W drawing (R=G=B) -> saturation 0 -> True (lossless)."""
    ramp = np.tile(np.arange(0, 256, dtype=np.uint8).reshape(1, 256, 1), (10, 1, 3))
    assert _is_low_saturation(_img(ramp)) is True


def test_low_sat_colour_photo_false():
    """Poori saturated colour (pure red) -> frac(S>40)=1.0 -> False."""
    assert _is_low_saturation(_solid((255, 0, 0))) is False


def test_low_sat_boundary_just_below():
    """13% saturated (<0.14) -> True."""
    assert _mix_saturated(0.13) is not None
    assert _is_low_saturation(_mix_saturated(0.13)) is True


def test_low_sat_boundary_just_above():
    """15% saturated (>0.14) -> False."""
    assert _is_low_saturation(_mix_saturated(0.15)) is False


def test_low_sat_threshold_constant_sane():
    """Sanity: threshold 0 aur 1 ke beech."""
    assert 0.0 < _SAT_LOSSLESS_MAX < 1.0


def test_low_sat_empty_returns_true():
    """Khaali image -> True (safe lossless)."""
    assert _is_low_saturation(Image.new("RGB", (0, 0))) is True


# ===========================================================================
# _choose_compression — teen-marhala order:
#   1) force_lossless  2) saturation gate  3) bucket rule
# ===========================================================================

def test_choose_force_lossless_wins():
    """force_lossless=True har content par lossless (stage 1), chahe colour photo ho."""
    rng = np.random.default_rng(1)
    photo = _img(rng.integers(0, 256, (50, 50, 3), dtype=np.uint8))
    assert _choose_compression(photo, force_lossless=True) == "lossless"


def test_choose_saturation_gate_beats_bucket_rule():
    """High-detail B/W: buckets>40 (bucket-rule akela lossy kehta) par low saturation ->
    saturation gate (stage 2) pehle lag kar lossless deta hai."""
    img = _near_gray_many()
    assert _is_line_art(img) is False          # bucket-rule akela -> lossy hota
    assert _is_low_saturation(img) is True      # par grayscale hai
    assert _choose_compression(img, force_lossless=False) == "lossless"


def test_choose_colour_photo_lossy():
    """Saturated colour photo (high sat + bahut buckets) -> stage 3 bucket rule -> lossy."""
    rng = np.random.default_rng(2)
    photo = _img(rng.integers(0, 256, (60, 60, 3), dtype=np.uint8))
    assert _is_low_saturation(photo) is False
    assert _choose_compression(photo, force_lossless=False) == "lossy"


def test_choose_flat_colour_graphic_lossless():
    """Flat colour graphic (saturated par chand buckets) -> bucket rule -> lossless."""
    img = _equal_colours([(255, 0, 0), (0, 200, 0), (0, 0, 255)])
    assert _is_low_saturation(img) is False     # saturation gate se nahi
    assert _is_line_art(img) is True            # buckets kam -> bucket rule se lossless
    assert _choose_compression(img, force_lossless=False) == "lossless"
