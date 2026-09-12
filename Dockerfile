# Container image. Slim Python, koi LibreOffice nahi.
#
# ⚠ Ye file do purani baaton par likhi gayi thi, dono ab ghalat hain (durust 2026-08-31):
#   1. "Northflank deploy image" — cloud plan BAND hai (docs/ROADMAP.md, O1). Is image ka
#      maqsad ab school PC / publisher distribution package hai, koi cloud host nahi.
#   2. "koi LibreOffice nahi (PDF export baad ke PR mein)" — wo PR kabhi nahi aayega:
#      DOCX/PDF export 2026-08-13 ko delete hua (e2bdcc4). Paper browser se chhapta hai.
#      LibreOffice ki zaroorat KABHI nahi paregi — ye ghair-mojoodgi ab permanent hai.
#
# App uvicorn ko fixed port 8080 par bind karta hai (PORT env kahin parha nahi jata).
FROM python:3.12-slim

WORKDIR /app

# Deps pehle copy karo taake requirements.txt na badle to ye layer cache ho (build fast).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

# FAIL-CLOSED IS IMAGE MEIN. Bina is line ke container CHUP-CHAAP bina auth ke
# start ho jata tha, aur yahi asal deploy raasta hai.
#
# `app/api/auth.py` ka fail-closed check sirf do soorton mein chalta hai: Railway
# ke inject kiye markers (RAILWAY_*), ya ye flag. Cloud plan 2026-08-31 ko band ho
# gaya — koi Railway nahi rahi — to container mein koi marker hota hi nahi, aur
# `PAPER_MAKER_API_KEY` bhool jane par app khushi se UNPROTECTED chal parti.
# Flag lagne ke baad wo soorat loud crash hai: key do, warna image chalegi nahi.
#
# Local dev (`uvicorn` seedha, bina container) is se bilkul mutasir nahi — wahan
# ye var set hi nahi hota, auth pehle ki tarah off rehti hai.
ENV PAPER_MAKER_REQUIRE_API_KEY=1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
