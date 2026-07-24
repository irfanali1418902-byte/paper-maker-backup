@echo off
title AII Paper Maker
cd /d "%~dp0"

REM --- .env load karo (# comments skip, blank lines skip)
if exist ".env" (
    for /f "usebackq eol=# tokens=1,* delims==" %%A in (".env") do (
        if not "%%A"=="" set "%%A=%%B"
    )
) else (
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
