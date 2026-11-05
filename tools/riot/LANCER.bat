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

echo --- 1/4 collecte ------------------------------------------
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
echo --- 2/4 inspection ----------------------------------------
%PY% inspecter.py

echo.
echo --- 3/4 miroir --------------------------------------------
REM --set auto : le set de la partie la plus recente. Une recolte de 200
REM parties remonte loin et couvre souvent DEUX sets ; les moyenner ne
REM decrit ni l'un ni l'autre. "auto" survit au passage au Set 19 sans
REM qu'on ait a modifier ce fichier.
REM Le CSV et le resume alimentent build_miroir.py, qui produit le
REM data/miroir.json que lit le site.
%PY% miroir.py --set auto --csv parties_propres.csv --sortie miroir_resume.json

echo.
echo --- 4/4 contestation --------------------------------------
REM Ce que jouaient les SEPT AUTRES. collecte.py enregistre l'objet de
REM partie entier, donc les huit plateaux ; jusqu'ici on n'en lisait que
REM le rang. La contestation est l'axe le plus discriminant entre Master
REM et Challenger, et personne ne peut la publier : elle demande TES
REM lobbies.
REM NON BLOQUANT : si cette etape echoue, la collecte reste bonne et
REM miroir_resume.json est deja ecrit. On ne perd jamais une recolte
REM pour un calcul qui vient apres.
%PY% contestation.py --set auto --sortie contestation_resume.json
if errorlevel 1 (
  echo.
  echo [INFO] La contestation n'a pas pu etre calculee. Ce n'est pas grave :
  echo        le reste de la recolte est bon. Signale-le a Claude.
)

echo.
echo ==========================================
echo   TERMINE
echo ==========================================
echo.
echo Dis simplement a Claude que c'est fait : il lit ces trois
echo fichiers directement sur ton disque.
echo   - miroir_resume.json
echo   - parties_propres.csv
echo   - contestation_resume.json
echo.
echo N'envoie JAMAIS cle.txt, et jamais le dossier parties\ :
echo il contient l'identifiant de tes sept adversaires a chaque lobby.
echo.
pause
