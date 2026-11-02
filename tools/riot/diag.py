#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DIAGNOSTIC DE CLÉ — pourquoi le 403 ?
=====================================
Un 403 de Riot a toujours le même corps de réponse, quelle que soit la cause.
Impossible de trancher sur un seul appel. Ce script en fait TROIS, choisis pour
qu'ils se distinguent :

  A. status-v4 (LoL)       ne demande aucune permission particulière
  B. tft-league-v1         endpoint TFT, sans puuid
  C. account-v1 by-riot-id le tout premier appel de collecte.py

Lecture du résultat :
  A, B, C tous KO  -> la clé elle-même est refusée (expirée, regénérée, ou
                      accord développeur non accepté sur le compte)
  A ou B OK, C KO  -> la clé est bonne mais n'a pas le droit ACCOUNT-V1
  A, B, C tous OK  -> la clé marche : le problème est ailleurs dans collecte.py

La clé n'est jamais affichée en entier.
"""

import json, os, sys, urllib.request, urllib.error

ICI = os.path.dirname(os.path.abspath(__file__))

TESTS = [
    ("A", "status-v4 (LoL, aucune permission requise)",
     "https://euw1.api.riotgames.com/lol/status/v4/platform-data"),
    ("B", "tft-league-v1 challenger (endpoint TFT)",
     "https://euw1.api.riotgames.com/tft/league/v1/challenger"),
    ("C", "account-v1 by-riot-id (1er appel de collecte.py)",
     "https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/Itario/EUW"),
]

EN_TETE = ("x-riot-edge-trace-id", "x-app-rate-limit",
           "x-app-rate-limit-count", "retry-after", "date")


def lire_cle():
    p = os.path.join(ICI, "cle.txt")
    if not os.path.exists(p):
        sys.exit("cle.txt introuvable a cote de ce script.")
    # utf-8-sig : Notepad ajoute parfois un marqueur invisible en tete
    brut = open(p, "rb").read()
    cle = brut.decode("utf-8-sig", errors="replace").strip()
    print("=== la cle, telle que le script la lit ===")
    print(f"  octets dans le fichier : {len(brut)}")
    print(f"  apres nettoyage        : {len(cle)} caracteres"
          f"{'' if len(cle) == 42 else '   <-- ANORMAL, attendu 42'}")
    print(f"  prefixe RGAPI-         : {cle.startswith('RGAPI-')}")
    print(f"  apercu                 : {cle[:11]}...{cle[-4:]}")
    # un espace, un retour ou un guillemet colle a la cle la rend invalide
    suspects = [c for c in cle if not (c.isalnum() or c == "-")]
    print(f"  caracteres suspects    : "
          f"{'aucun' if not suspects else repr(''.join(suspects)) + '   <-- A CORRIGER'}")
    print()
    return cle


def appel(cle, url):
    req = urllib.request.Request(url, headers={
        "X-Riot-Token": cle,
        "Accept": "application/json",
        "User-Agent": "OracleTFT/diag",
    })
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, r.read(400).decode("utf-8", "replace"), dict(r.headers)
    except urllib.error.HTTPError as e:
        return e.code, e.read(600).decode("utf-8", "replace"), dict(e.headers)
    except Exception as e:
        return None, f"{type(e).__name__}: {e}", {}


def main():
    cle = lire_cle()
    resultats = {}

    for code, libelle, url in TESTS:
        print(f"--- {code}. {libelle}")
        print(f"    {url}")
        statut, corps, entetes = appel(cle, url)
        resultats[code] = statut
        verdict = "OK" if statut == 200 else f"HTTP {statut}"
        print(f"    -> {verdict}")
        if statut != 200:
            print(f"    corps : {corps.strip()[:400]}")
            for h in EN_TETE:
                for k, v in entetes.items():
                    if k.lower() == h:
                        print(f"    {k}: {v}")
        print()

    a, b, c = resultats.get("A"), resultats.get("B"), resultats.get("C")
    print("=" * 58)
    print("VERDICT")
    print("=" * 58)
    if a == b == c == 200:
        print("  La cle fonctionne sur les trois appels.")
        print("  -> Le probleme n'est pas la cle. Relance LANCER.bat et")
        print("     envoie-moi la sortie complete.")
    elif c != 200 and (a == 200 or b == 200):
        print("  La cle est VALIDE mais n'a pas acces a ACCOUNT-V1.")
        print("  -> C'est une restriction du compte developpeur, pas une")
        print("     expiration. Je contourne : collecte.py peut prendre ton")
        print("     puuid autrement. Envoie-moi juste ce verdict.")
    elif all(x in (401, 403) for x in (a, b, c) if x is not None):
        print("  Les trois appels sont refuses -> c'est la CLE qui est rejetee.")
        print("  Causes, dans l'ordre :")
        print("   1. l'accord developpeur n'est pas accepte sur le compte")
        print("      (le portail affiche une cle mais elle ne marche pas) ;")
        print("   2. la cle a ete regeneree depuis la copie ;")
        print("   3. tu n'es pas connecte au bon compte Riot sur le portail.")
    elif any(x is None for x in (a, b, c)):
        print("  Au moins un appel n'a pas abouti au reseau.")
        print("  -> Pare-feu, VPN ou proxy. Teste dans un navigateur :")
        print("     https://euw1.api.riotgames.com/lol/status/v4/platform-data")
    else:
        print(f"  Combinaison inattendue : A={a} B={b} C={c}")
        print("  -> Envoie-moi cette sortie telle quelle.")
    print()
    json.dump(resultats, open(os.path.join(ICI, "diag_resultat.json"), "w"))


if __name__ == "__main__":
    main()
