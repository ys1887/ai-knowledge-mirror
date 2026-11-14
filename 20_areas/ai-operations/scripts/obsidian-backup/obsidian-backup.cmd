@echo off
setlocal
rem Obsidian backup: mirror C:\Users\nekol\Obsidian to two independent destinations:
rem   stage 1: E:\Documents\Backup\Obsidian (local copy; does not need the vault)
rem   stage 2: Z:\Obsidian (Cryptomator vault; skipped when Z: is absent)
set "SRC=C:\Users\nekol\Obsidian"
set "DST1=E:\Documents\Backup\Obsidian"
set "DST2=Z:\Obsidian"
set "LOG=%~dp0obsidian-backup.log"
set "FAIL="

echo ==== %DATE% %TIME% backup start ==== >> "%LOG%"

rem --- stage 1: local copy to E: (always runs) ---
echo ---- stage 1: local copy to %DST1% ---- >> "%LOG%"
robocopy "%SRC%" "%DST1%" /MIR /COPY:DAT /DCOPY:DAT /R:3 /W:5 /NP /LOG+:"%LOG%"
set "RC1=%ERRORLEVEL%"
echo robocopy stage 1 exit code: %RC1% >> "%LOG%"
if %RC1% GEQ 8 set "FAIL=1"

rem --- stage 2: vault copy (only when Z: is present) ---
rem Wait for the vault drive (auto-unlock may take a moment after sign-in). Up to about 5 minutes.
set "FOUND="
for /L %%i in (1,1,30) do (
  if exist "Z:\" set "FOUND=1"
  if defined FOUND goto :stage2
  timeout /t 10 /nobreak >nul
)
echo Z drive not found. Stage 2 skipped. >> "%LOG%"
goto :finish

:stage2
echo ---- stage 2: vault copy to %DST2% ---- >> "%LOG%"
robocopy "%SRC%" "%DST2%" /MIR /COPY:DAT /DCOPY:DAT /R:3 /W:5 /NP /LOG+:"%LOG%"
set "RC2=%ERRORLEVEL%"
echo robocopy stage 2 exit code: %RC2% >> "%LOG%"
if %RC2% GEQ 8 set "FAIL=1"

:finish
if defined FAIL (exit /b 1) else (exit /b 0)
