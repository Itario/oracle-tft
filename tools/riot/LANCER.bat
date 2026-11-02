@echo off
REM ============================================================
REM  ORACLE TFT - collecte + inspection + miroir, en une fois
REM  Double-clic suffit. Pas besoin d'ouvrir un terminal.
REM ============================================================
cd /d "%~dp0"
chcp 65001 >nul

echo.
echo ==========================================
echo   ORACLE TFT - recolte des parties
echo ==========================================
echo.

if not exist cle.txt (
  echo [STOP] Fichier cle.txt introuvable.
  echo.
  echo        1. Va sur developer.riotgames.com
  echo        2. Copie la DEVELOPMENT API KEY affichee maintenant
  echo        3. Ouvre le Bloc-notes, colle-la, enregistre sous:
  echo           %~dp0cle.txt
  echo           ^(type de fichier: "Tous les fichiers", PAS .txt en plus^)
  echo.
  pause
  exit /b 1
)

set PY=python
%PY% --version >nul 2>&1 || set PY=py
%PY% --version >nul 2>&1 || (
  echo [STOP] Python introuvable. Reinstalle-le en cochant
  echo        "Add python.exe to PATH".
  pause
  exit /b 1
)

echo --- 1/3 collecte ------------------------------------------
%PY% collecte.py
if errorlevel 1 (
  echo.
  echo [STOP] La collecte a echoue. Lis le message ci-dessus.
  echo        Si c'est une erreur 403: la cle a expire,
  echo        recopie celle affichee MAINTENANT sur le portail.
  pause
  exit /b 1
)

echo.
echo --- 2/3 inspection ----------------------------------------
%PY% inspecter.py

echo.
echo --- 3/3 miroir --------------------------------------------
%PY% miroir.py

echo.
echo ==========================================
echo   TERMINE
echo ==========================================
echo.
echo Envoie a Claude le fichier: miroir_resume.json
echo N'envoie JAMAIS cle.txt.
echo.
pause
