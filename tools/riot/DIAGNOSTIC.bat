@echo off
cd /d "%~dp0"
chcp 65001 >nul
set PY=python
%PY% --version >nul 2>&1 || set PY=py
echo.
echo ==========================================
echo   ORACLE TFT - diagnostic de la cle
echo ==========================================
echo.
%PY% diag.py
echo.
pause
