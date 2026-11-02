#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
COLLECTE — historique de parties TFT depuis l'API officielle Riot
=================================================================
À LANCER SUR TA MACHINE. Claude ne peut pas joindre l'API Riot depuis
son environnement (le proxy la refuse), et de toute façon ta clé n'a
rien à y faire.

PRÉPARATION
-----------
1. Mets ta clé dans un fichier nommé  cle.txt  à côté de ce script.
   Une seule ligne, la clé, rien d'autre.
   (Ne la mets JAMAIS dans le script lui-même : tu finirais par le
   partager avec la clé dedans.)
2. Python 3 suffit. Aucune installation : tout est dans la librairie
   standard.

LANCEMENT
---------
    python3 collecte.py

    python3 collecte.py --nb 200       # remonter plus loin
    python3 collecte.py --joueur Autre#TAG

RÉSULTAT
--------
    parties/<match_id>.json    une partie brute par fichier
    collecte.log               le déroulé, pour déboguer

Le script est RELANÇABLE : il saute les parties déjà téléchargées.
Si ta clé expire en cours de route, relance avec une clé fraîche,
il reprendra où il s'est arrêté.

NOTE SUR LES CLÉS
-----------------
Une clé de développement expire toutes les 24 h : parfait pour une
première récolte. Une clé personnelle n'expire pas : nécessaire pour
la collecte automatique ensuite.
"""

import json, os, sys, time, argparse, datetime
import urllib.request, urllib.error, urllib.parse

RACINE   = os.path.dirname(os.path.abspath(__file__))
DOSSIER  = os.path.join(RACINE, "parties")
JOURNAL  = os.path.join(RACINE, "collecte.log")
ROUTAGE  = "europe"          # EUW, EUNE, TR, RU -> europe
                             # NA, BR, LAN, LAS  -> americas
                             # KR, JP            -> asia

# Clé de dev : 20 requêtes / 1 s et 100 / 2 min.
# On vise large : 1 requête toutes les 1.3 s = ~92 / 2 min.
PAUSE = 1.3


def log(msg):
    ligne = f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S}  {msg}"
    print(ligne, flush=True)
    with open(JOURNAL, "a", encoding="utf-8") as f:
        f.write(ligne + "\n")


def lire_cle():
    chemin = os.path.join(RACINE, "cle.txt")
    if not os.path.exists(chemin):
        sys.exit("Fichier cle.txt introuvable. Crée-le à côté du script, "
                 "avec ta clé API sur une seule ligne.")
    # utf-8-sig : Notepad ajoute parfois un marqueur invisible en tête
    cle = open(chemin, encoding="utf-8-sig").read().strip()
    cle = "".join(cle.split())          # retire espaces, retours ligne, tabulations
    if not cle.startswith("RGAPI-"):
        sys.exit("Le contenu de cle.txt ne ressemble pas à une clé Riot "
                 "(elle commence par RGAPI-).")
    if len(cle) != 42:
        sys.exit(f"La clé fait {len(cle)} caractères au lieu de 42. "
                 "La copie est probablement incomplète : retourne sur "
                 "developer.riotgames.com et recopie-la en entier.")
    return cle


def en_tetes(cle):
    """
    Les trois en-têtes sont obligatoires, et le User-Agent n'est PAS décoratif.

    Sans lui, urllib s'annonce « Python-urllib/3.x » — et la bordure de Riot
    rejette cet agent avec un 403 dont le corps est identique à celui d'une clé
    expirée. C'est exactement ce qui a immobilisé la collecte du 19/10 au 02/11 :
    on a changé la clé quatre fois alors que la clé n'avait jamais été en cause.

    Ne retire jamais le User-Agent.
    """
    return {
        "X-Riot-Token": cle,
        "Accept": "application/json",
        "User-Agent": "OracleTFT/1.0 (collecte post-partie, usage personnel)",
    }


def appel(url, cle, essais=5):
    """Un appel GET, avec gestion du quota et des pannes passagères."""
    for n in range(essais):
        req = urllib.request.Request(url, headers=en_tetes(cle))
        try:
            with urllib.request.urlopen(req, timeout=25) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 429:                       # quota dépassé
                attente = int(e.headers.get("Retry-After", 10))
                log(f"  quota atteint, pause de {attente}s")
                time.sleep(attente + 1)
                continue
            if e.code in (401, 403):
                # Le corps de la réponse est la SEULE chose qui distingue les
                # causes entre elles : on ne devine plus, on l'affiche.
                try:
                    corps = e.read(600).decode("utf-8", "replace").strip()
                except Exception:
                    corps = "(corps illisible)"
                trace = e.headers.get("X-Riot-Edge-Trace-Id", "—")
                sys.exit(
                    "\nAppel refusé (HTTP %d).\n"
                    "  url    : %s\n"
                    "  corps  : %s\n"
                    "  trace  : %s\n\n"
                    "Avant de soupçonner la clé, lance DIAGNOSTIC.bat : il fait "
                    "trois appels choisis pour distinguer les causes.\n"
                    "  - les trois refusés       -> la clé est en cause\n"
                    "  - seuls certains refusés  -> un droit manque sur le compte\n"
                    "  - les trois acceptés      -> le bug est dans ce script, "
                    "pas chez Riot (c'était le cas du 19/10 : User-Agent absent)"
                    % (e.code, url, corps, trace))
            if e.code == 404:
                return None
            if 500 <= e.code < 600:                 # panne côté Riot
                log(f"  erreur serveur {e.code}, nouvelle tentative")
                time.sleep(3 * (n + 1))
                continue
            raise
        except Exception as ex:
            log(f"  réseau : {ex} — nouvelle tentative")
            time.sleep(3 * (n + 1))
    raise SystemExit(f"Échec après {essais} tentatives : {url}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--joueur", default="Itario#EUW",
                    help="Riot ID complet, par exemple Itario#EUW")
    ap.add_argument("--nb", type=int, default=200,
                    help="nombre de parties à remonter (défaut 200)")
    a = ap.parse_args()

    if "#" not in a.joueur:
        sys.exit("Le Riot ID doit contenir un #, par exemple Itario#EUW")
    nom, tag = a.joueur.split("#", 1)

    cle = lire_cle()
    os.makedirs(DOSSIER, exist_ok=True)
    log(f"=== Collecte pour {a.joueur} — jusqu'à {a.nb} parties ===")

    # 1. identifiant du joueur
    compte = appel(f"https://{ROUTAGE}.api.riotgames.com/riot/account/v1/"
                   f"accounts/by-riot-id/{urllib.parse.quote(nom)}/"
                   f"{urllib.parse.quote(tag)}", cle)
    if not compte:
        sys.exit(f"Joueur {a.joueur} introuvable. Vérifie l'orthographe et le tag.")
    puuid = compte["puuid"]
    log(f"joueur trouvé : {compte.get('gameName')}#{compte.get('tagLine')}")

    # 2. liste des parties, par pages de 100
    ids, debut = [], 0
    while len(ids) < a.nb:
        lot = min(100, a.nb - len(ids))
        time.sleep(PAUSE)
        page = appel(f"https://{ROUTAGE}.api.riotgames.com/tft/match/v1/"
                     f"matches/by-puuid/{puuid}/ids?start={debut}&count={lot}", cle)
        if not page:
            break
        ids.extend(page)
        debut += len(page)
        log(f"  {len(ids)} identifiants récupérés")
        if len(page) < lot:
            break

    manquantes = [m for m in ids
                  if not os.path.exists(os.path.join(DOSSIER, m + ".json"))]
    log(f"{len(ids)} parties au total · {len(manquantes)} à télécharger "
        f"· {len(ids)-len(manquantes)} déjà sur le disque")

    # 3. téléchargement
    for i, mid in enumerate(manquantes, 1):
        time.sleep(PAUSE)
        m = appel(f"https://{ROUTAGE}.api.riotgames.com/tft/match/v1/"
                  f"matches/{mid}", cle)
        if m is None:
            log(f"  [{i}/{len(manquantes)}] {mid} introuvable, ignorée")
            continue
        with open(os.path.join(DOSSIER, mid + ".json"), "w", encoding="utf-8") as f:
            json.dump(m, f, ensure_ascii=False)
        if i % 10 == 0 or i == len(manquantes):
            reste = (len(manquantes) - i) * PAUSE
            log(f"  [{i}/{len(manquantes)}] — encore ~{reste/60:.1f} min")

    n = len([f for f in os.listdir(DOSSIER) if f.endswith(".json")])
    log(f"=== Terminé : {n} parties dans {DOSSIER} ===")
    log("Envoie le dossier parties/ (ou son zip) à Claude pour l'analyse.")


if __name__ == "__main__":
    main()
