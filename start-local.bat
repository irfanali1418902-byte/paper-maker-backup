@echo off
REM ============================================================================
REM  SHIM - asli launcher ab start-school.bat hai.
REM
REM  Yeh file DELETE NAHI ki gayi, aur wajah yeh hai: SETUP-LOCAL.md step 9 school
REM  ko kehta aaya hai ke iski shortcut `shell:startup` folder mein rakho, taake
REM  PC on hote hi server chalu ho jaye. Naam badalne ya hatane se woh shortcut
REM  chup-chaap toot jaati - PC chalu hota, server nahi, aur subah pehla teacher
REM  hi is se takraata.
REM
REM  Purani file do cheezein karti thi jo school ke liye ghalat theen:
REM    * uvicorn --reload ke saath chalati thi (development ka flag; server code
REM      chhune par restart kar deta hai)
REM    * config env.local.bat se parhti thi, jabke start.bat .env se - do
REM      launchers, do config files, aur admin ko pata nahi kaunsi asli hai
REM
REM  Dono ab ek jagah tay hain: .env, aur start-school.bat.
REM ============================================================================
cd /d "%~dp0"
echo(
echo [i] start-local.bat ab sirf start-school.bat ko chalata hai.
echo     Apni shortcut seedha start-school.bat par bana lein to behtar hai.
echo(
call "%~dp0start-school.bat"
