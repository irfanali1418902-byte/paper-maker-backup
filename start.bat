@echo off
REM ============================================================================
REM  DEVELOPMENT launcher. School server ke liye start-school.bat use karein.
REM
REM  Farq: yahan uvicorn --reload ke saath chalta hai, jo dev mein chahiye (code
REM  save karte hi naya module) aur school par nuqsaan-deh hai -- server files
REM  watch karta rehta hai aur code chhune par RESTART kar deta hai, yani kisi
REM  teacher ka aadha bana paper ja sakta hai. start-school.bat mein wo flag
REM  jaan boojh kar nahi hai, aur wo chalne se pehle DB/auth/firewall check bhi
REM  karta hai.
REM ============================================================================
title AII Paper Maker (dev)
cd /d "%~dp0"

REM .env yahan parse NAHI hota - app khud karti hai (app/__init__.py ->
REM load_dotenv), jo tarteeb-mehfooz hai. Pehle yahan ek manual parse loop tha
REM kyunki app ke module-level vars .env se PEHLE parhe jaate the; wo bug
REM 2026-08-20 ko band hua (PROGRESS.md), aur do jagah do tareeqe rakhne ka ab
REM koi sabab nahi.
if not exist ".env" (
    echo [!] .env file nahi mili - keys unset raheingi.
)

REM --- Virtual environment check
if not exist ".venv\Scripts\activate.bat" (
    echo.
    echo [X] .venv nahi mila. Pehle ek baar yeh chalao:
    echo.
    echo     python -m venv .venv
    echo     .venv\Scripts\pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

call ".venv\Scripts\activate.bat"

REM --- Browser 2 second baad kholo (server ko start hone ka waqt do)
start "" cmd /c "timeout /t 2 /nobreak >nul && start http://localhost:8000"

echo.
echo ============================================================
echo   AII Paper Maker - Server chal raha hai
echo ============================================================
echo   Local:    http://localhost:8000
echo   Band karne ke liye: Ctrl+C dabao
echo ============================================================
echo.

REM --reload: code save karte hi server khud naya module load kare (stale-server se bacho)
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

echo.
echo [!] Server band ho gaya.
pause
