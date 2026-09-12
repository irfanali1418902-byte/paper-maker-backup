@echo off
REM ============================================================================
REM  AII Smart Paper Maker - SCHOOL SERVER launcher (Windows)
REM
REM  Yeh production launcher hai. Dev ke liye start.bat use karein (--reload ke
REM  saath). Farq sirf ek nahi hai, teen hain:
REM
REM    1. --reload NAHI. Wo development ka flag hai: uvicorn saari files watch
REM       karta rehta hai aur code chhune par server RESTART kar deta hai. School
REM       server par iska matlab hai ke koi teacher paper banate hue apna kaam
REM       kho sakta hai, aur 20 teachers ke saath wo watcher muft mein CPU khaata
REM       hai. 2026-08-20 se pehle dono launchers is flag ke saath chal rahe the.
REM
REM    2. .env yahan parse NAHI hota. App khud karti hai (app/__init__.py ->
REM       load_dotenv), aur wahi tarteeb-mehfooz jagah hai. Pehle start.bat ise
REM       khud parse karta tha kyunki app ke module-level vars .env se PEHLE
REM       parhe jaate the -- wo bug 2026-08-20 ko band hua.
REM
REM    3. Chalne se pehle teen cheezein check hoti hain jo khamoshi se ghalat ja
REM       sakti hain: DB file, firewall, aur auth key.
REM ============================================================================
title AII Paper Maker - School Server
cd /d "%~dp0"

echo(
echo ============================================================
echo   AII Smart Paper Maker - School Server
echo ============================================================

REM --- venv ---------------------------------------------------------------
if not exist ".venv\Scripts\activate.bat" (
  echo(
  echo   [X] .venv nahi mila. Pehle ek dafa yeh chalao:
  echo(
  echo       python -m venv .venv
  echo       .venv\Scripts\pip install -r requirements.txt
  echo(
  pause
  exit /b 1
)
call ".venv\Scripts\activate.bat"

REM --- .env ---------------------------------------------------------------
REM Sirf batane ke liye. App khud load karti hai; yahan parse karne ki koshish
REM mat karo, warna do jagah do tareeqe ho jayenge.
if not exist ".env" (
  echo(
  echo   [!] .env nahi mila.
  echo       - AI question generation band rahegi ^(GEMINI_API_KEY / ANTHROPIC_API_KEY^)
  echo       - PAPER_MAKER_API_KEY ke baghair LAN par /api BILKUL KHULA hai
  echo       - DB_PATH ke baghair data repo folder mein banega, C:\PaperMakerData mein nahi
  echo       .env.example copy kar ke .env banayen. SETUP-LOCAL.md step 5.
  echo(
)

REM --- DB check -----------------------------------------------------------
REM SAB SE AHEM CHECK. Ghalat ya typo'd DB_PATH par app error NAHI deti - wo
REM chup-chaap nayi khali DB bana leti hai, folder samet. School ko lagta hai
REM saara data urh gaya, jabke asli file apni jagah salamat hoti hai. Isi liye
REM yahan file ka HONA check hota hai, sirf var ka set hona nahi.
for /f "usebackq delims=" %%P in (`.venv\Scripts\python.exe -c "from app.core.database import DB_PATH; print(DB_PATH)"`) do set "RESOLVED_DB=%%P"

echo(
echo   Database: %RESOLVED_DB%
if not exist "%RESOLVED_DB%" (
  echo(
  echo   [!] YEH FILE ABHI MOJOOD NAHI HAI.
  echo       Server chala to ek NAYI KHALI database banegi.
  echo(
  echo       Agar yeh school ka pehla setup hai - theek hai, aage barhein.
  echo       Agar school ka data pehle se hai - RUK JAYEN. DB_PATH ghalat hai.
  echo       Sahi path .env mein theek karein, warna purana data nazar nahi aayega.
  echo(
  choice /c YN /n /m "   Phir bhi chalayein? (Y/N): "
  if errorlevel 2 (
    echo   Band kiya ja raha hai.
    pause
    exit /b 1
  )
)

REM --- auth check ---------------------------------------------------------
REM Teen mein se ek jawab. Mode DB se tay hota hai, kisi flag se nahi (SEC-02):
REM koi active user mojood ho to login laazmi, warna shared key, warna khula.
REM Isi liye yahan `auth_mode()` se poochha jata hai, sirf key dekh kar farz
REM nahi kiya jata -- warna users bana lene ke baad bhi ye "key" chhapta rehta.
for /f "usebackq delims=" %%A in (`.venv\Scripts\python.exe -c "from app.api.auth import auth_mode; print(auth_mode())"`) do set "AUTH_MODE=%%A"

if "%AUTH_MODE%"=="users" (
  echo   Auth:     LOGIN ^(har teacher apne account se - /login.html^)
) else if "%AUTH_MODE%"=="key" (
  echo   Auth:     shared key ^(teachers ko ek hi Access key chahiye^)
  echo             Behtar: python scripts\create_admin.py chala kar asli accounts banayen
) else (
  echo   Auth:     [!] KHULA - LAN par koi bhi /api use kar sakta hai
  echo             Theek karne ke liye: python scripts\create_admin.py
)

REM --- firewall check -----------------------------------------------------
REM Bina iske server chal to jayega magar sirf isi PC par khulega; teachers ka
REM "connection timed out" ka sab se aam sabab yehi hai.
netsh advfirewall firewall show rule name="Paper Maker 8000" >nul 2>&1
if errorlevel 1 (
  echo   Firewall: [!] port 8000 ka rule nahi mila
  echo(
  echo       Teachers connect nahi kar payenge. ADMIN PowerShell mein ek dafa:
  echo       netsh advfirewall firewall add rule name="Paper Maker 8000" dir=in action=allow protocol=TCP localport=8000
) else (
  echo   Firewall: rule mojood hai
)

REM --- LAN addresses ------------------------------------------------------
echo(
echo ------------------------------------------------------------
echo   Is PC par:       http://localhost:8000
echo   Teachers ^(LAN^):  http://^<niche wala 192.168.x.x^>:8000
echo ------------------------------------------------------------
ipconfig | findstr /C:"IPv4"
echo ------------------------------------------------------------
echo   Band karne ke liye: Ctrl+C
echo ============================================================
echo(

REM --host 0.0.0.0 laazmi hai - isi se LAN ke doosre devices connect karte hain.
REM --reload yahan JAAN BOOJH KAR nahi hai; upar wajah likhi hai.
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

echo(
echo [!] Server band ho gaya. Koi key dabayein.
pause >nul
