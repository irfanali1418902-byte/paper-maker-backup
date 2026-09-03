"""`js/brand.js` ke DOM hooks ka guard — D57.

brand.js `document.querySelectorAll(".brand .name")` aur
`".brand .tag:not([data-i18n])"` par chalta hai, yani **presentational classes**
par — wohi cheez jo `CLAUDE.md` §11 mana karta hai ("never `querySelector` a
presentational class — that is what welds styling to logic").

**Ye kyun khatarnaak hai, aur khatra farzi nahi:** UI-ARCH ka drain `.brand` ko
`99-legacy/` se nikal raha hai. Jis din wo class markup se jati hai, **kuch fail
nahi hoga** — na koi error, na koi test — bas naam khamoshi se update hona band
ho jayega. `plan.html` par ye pehle hi ho chuka hai: wo brand.js load karti hai
aur us ke dono selectors **sifar** element match karte hain, kyunke us ka markup
poori tarah `.sidenav__brand-name` par hai.

Ye tests wohi khamoshi torte hain.

⚠ D57 KA BAYAN GHALAT HAI AUR US KA TAJWEEZ-KARDA FIX NUQSAN-DEH — naapa gaya
2026-09-02, tafseel `DEFERRED.md` D57 mein. Mukhtasar: `/api/brand` school ka
naam deta hi nahi (`full_name` = "Parcha Paper Maker", product ka naam), aur
wohi string har page ke markup mein pehle se likhi hai — is liye aaj daswon
pages ek jaisa dikhate hain aur koi nazar aane wala farq nahi hai. Yahan jo
guard kiya ja raha hai wo aaj ka farq nahi, **kal ki khamoshi** hai.
"""

from __future__ import annotations

from html.parser import HTMLParser

from scripts.css_baseline import PROJECT_ROOT, page_paths

#: `print.html` brand.js load NAHI karti, aur ye jaan-boojh kar hai — dekhein
#: `test_print_is_the_only_page_without_brand_js` ka docstring.
PAGES_WITHOUT_BRAND_JS = {"print.html"}

#: `plan.html` brand.js load karti hai magar us ke hooks sifar match karte hain.
#: Ye D57 ka zinda nisf hai. Isay yahan naam se rakha gaya hai, chhupaya nahi:
#: agar plan theek ho jaye to ye test fail karega aur bataega ke row band karo.
PAGES_WITH_BRAND_JS_BUT_NO_HOOK = {"plan.html"}


class _BrandHookFinder(HTMLParser):
    """`.brand` ke andar `.name` / `.tag` descendants ginta hai.

    Regex se nahi kiya gaya: `class` attribute mein tarteeb aur ginti dono badalti
    hain (`class="brand sidenav__brand"`), aur nesting regex se theek nahi parhi
    jati. `html.parser` stdlib mein hai, koi nayi dependency nahi.
    """

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._depth = 0
        self._brand_depth: int | None = None
        self.names = 0
        self.tags = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in ("br", "img", "input", "link", "meta", "hr"):
            return  # void elements — inka koi closing tag nahi aata
        attr = dict(attrs)
        classes = (attr.get("class") or "").split()
        self._depth += 1
        if self._brand_depth is None and "brand" in classes:
            self._brand_depth = self._depth
        elif self._brand_depth is not None:
            if "name" in classes:
                self.names += 1
            # brand.js `.tag` ko sirf tab chhoota hai jab us par data-i18n na ho
            if "tag" in classes and "data-i18n" not in attr:
                self.tags += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in ("br", "img", "input", "link", "meta", "hr"):
            return
        if self._brand_depth is not None and self._depth == self._brand_depth:
            self._brand_depth = None
        self._depth = max(0, self._depth - 1)


def _hooks(path) -> tuple[int, int]:
    finder = _BrandHookFinder()
    finder.feed(path.read_text(encoding="utf-8"))
    return finder.names, finder.tags


def _loads_brand_js(path) -> bool:
    return "js/brand.js" in path.read_text(encoding="utf-8")


def test_print_is_the_only_page_without_brand_js():
    """Ginti hard-coded hai, derive nahi ki gayi — yehi ratchet ka pura maqsad hai.

    `print.html` ise load nahi karti aur **karni bhi nahi chahiye**: us ke `<body>`
    par `data-page` nahi hai, aur brand.js `document.title` ko
    `data-page ? "<page> — <full_name>" : "<full_name>"` par set karta hai. Yani
    use load karne se title `Exam Paper — Print` se ghat kar sirf
    `Parcha Paper Maker` reh jayega — **maloomat kam ho jayegi.** D57 ne yehi
    tajweez ki thi; naapne par wo nuqsan-deh nikli.
    """
    missing = {p.name for p in page_paths() if not _loads_brand_js(p)}
    assert missing == PAGES_WITHOUT_BRAND_JS, (
        f"brand.js load na karne wale pages badal gaye: {sorted(missing)}. "
        "Agar ye jaan-boojh kar hai to is set ko wajah ke saath update karein."
    )


def test_every_page_that_loads_brand_js_still_has_a_hook_for_it():
    """Jis din drain `.brand` ko lay jayega, ye test bolega — script khamosh rahegi.

    Ye woh khamoshi hai jo D57 record karti hai: hook gaayab ho to koi error nahi
    aata, naam bas update hona chhor deta hai.
    """
    broken = set()
    for path in page_paths():
        if not _loads_brand_js(path) or path.name in PAGES_WITH_BRAND_JS_BUT_NO_HOOK:
            continue
        names, _ = _hooks(path)
        if names == 0:
            broken.add(path.name)

    assert not broken, (
        f"in pages par brand.js chalti hai magar '.brand .name' ab kuch match nahi karta: "
        f"{sorted(broken)} — naam khamoshi se update hona band ho gaya hai (D57)"
    )


def test_plan_is_the_only_page_where_the_hook_is_already_gone():
    """D57 ka zinda nisf, naam ke saath — chhupaya nahi gaya.

    `plan.html` (R7 Marhala 4) pehla page hai jis ka markup poori tarah
    `.sidenav__brand-*` par hai aur jis mein `.brand` ka koi `.name` bachcha nahi.
    Wo brand.js load karti hai, aur script wahan **sifar** element chhooti hai —
    yani wo silent failure jis se baqi pages ko bachana hai, wahan ho chuki hai.

    Ye test **ulta** likha gaya hai: agar plan theek kar di jaye to ye FAIL karega
    aur agle session ko batayega ke D57 band karo. Ek known gap ko khamoshi se
    exempt karna wahi bimari hoti jo D57 khud hai.
    """
    for name in PAGES_WITH_BRAND_JS_BUT_NO_HOOK:
        path = PROJECT_ROOT / "static" / name
        assert _loads_brand_js(path), f"{name} ab brand.js load nahi karti — ye set update karein"
        names, tags = _hooks(path)
        assert (names, tags) == (0, 0), (
            f"{name} ko ab brand.js ka hook mil gaya hai ({names} name, {tags} tag) — "
            "yani D57 ka ye nisf hal ho gaya. Row band karein aur is set se hataayen."
        )
