@echo off
REM ============================================================
REM  ORACLE TFT - la contestation seule, SANS CLE API
REM
REM  Pourquoi ce fichier existe separement de LANCER.bat :
REM  LANCER.bat commence par collecte.py, qui exige une cle API
REM  valide - et les cles de developpement expirent en 24 heures.
REM  Or la contestation se calcule sur les parties DEJA sur le
REM  disque. Aucune raison de redemander une cle pour relire des
REM  fichiers qu'on a deja.
REM
REM  Double-clic suffit.
REM ============================================================
cd /d "%~dp0"
chcp 65001 >nul

echo.
echo ==========================================
echo   ORACLE TFT - contestation
echo ==========================================
echo.

if not exist parties (
  echo [STOP] Dossier "parties" introuvable.
  echo.
  echo        Il n'y a rien a analyser. Lance LANCER.bat une fois
  echo        pour recolter les parties ^(la, il faudra une cle^).
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

REM --set auto : le set de la partie la plus recente. Survit au
REM passage au Set 19 sans qu'on touche a ce fichier.
%PY% contestation.py --set auto --sortie contestation_resume.json
if errorlevel 1 (
  echo.
  echo [STOP] Le calcul a echoue. Lis le message ci-dessus.
  echo        Si c'est un probleme d'import "mesures", c'est que le
  echo        dossier tools\lib n'est pas sur cette machine : copie
  echo        le dossier tools entier, ne recopie pas la fonction.
  pause
  exit /b 1
)

echo.
echo ==========================================
echo   TERMINE
echo ==========================================
echo.
echo Dis a Claude que c'est fait : il lit ce fichier sur ton disque.
echo   - contestation_resume.json
echo.
echo Il ne contient AUCUN identifiant : que des agregats par
echo champion et tes propres placements. Le dossier parties\, lui,
echo ne quitte jamais cette machine.
echo.
pause
