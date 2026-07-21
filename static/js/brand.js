// Branding loader — har page par chalta hai. /api/brand se naam/tagline le kar
// document.title aur sidebar ke .brand .name / .brand .tag set karta hai.
//
// Defaults yahin baked hain (config/brand.json jaise) taake agar fetch fail ho
// (offline server-side error), tab bhi sahi branding dikhe — koi FOUC nahi. HTML
// mein pehle se "Parcha ..." likha hota hai; yeh sirf confirm/replace karta hai.
//
// /api/brand auth ke bahar public hai, is liye plain fetch — key-gate trigger nahi hota.

(function () {
  const DEFAULTS = {
    name: "Parcha",
    full_name: "Parcha Paper Maker",
    tagline: "Exam paper generator",
  };

  function apply(brand) {
    const page = document.body.getAttribute("data-page") || "";
    document.title = page ? `${page} — ${brand.full_name}` : brand.full_name;

    // Sidebar .name par poora naam dikhta hai (jaise pehle "AII Smart Paper Maker").
    document.querySelectorAll(".brand .name").forEach((el) => {
      el.textContent = brand.full_name;
    });
    // .tag sirf tab set karo jab page ne apni koi khaas tag na di ho
    // (index ka "Phase 1 · MVP" data-i18n se aata hai — usay chhero mat).
    document.querySelectorAll(".brand .tag:not([data-i18n])").forEach((el) => {
      el.textContent = brand.tagline;
    });
  }

  // Pehle defaults laga do (instant, no flash), phir server se confirm/update.
  apply(DEFAULTS);

  fetch("/api/brand")
    .then((res) => (res.ok ? res.json() : Promise.reject(res.status)))
    .then((brand) => apply({ ...DEFAULTS, ...brand }))
    .catch(() => {
      /* fetch fail: defaults pehle se lage hain, kuch mat karo */
    });
})();
