#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RÉSEAU — la seule porte vers l'extérieur, et son mode « rejeu »
================================================================
Jusqu'au 10/11, chacun des cinq relevés (tactics, barre, joueur, compos,
recettes) portait sa propre copie de `lire()`. Cinq copies d'une fonction de
quinze lignes : la même duplication que champion(), avec la même conséquence
à terme.

Mais la vraie raison de ce module est ailleurs. **Tant que chaque script
ouvrait lui-même sa connexion, la chaîne ne pouvait tourner qu'en vrai, sur le
monde tel qu'il est aujourd'hui.** Impossible de lui présenter le monde du
1er décembre — un set neuf, un classement vide, un rang remis à zéro — pour
voir ce qui casse AVANT que ça casse.

D'où le mode rejeu. Si la variable d'environnement ORACLE_REJEU désigne un
dossier, `lire()` ne touche plus au réseau : il sert les réponses rangées dans
ce dossier, d'après son `index.json` :

    { "https://tactics.tools/units": "unites.html",
      "https://tactics.tools/leaderboards/euw": {"http": 404} }

Une URL absente de l'index fait échouer le script, exprès : en rejeu, toute
lecture non prévue est une découverte, pas un détail.

C'est ce qui permet à tools/tests/repetition.py de faire tourner les VRAIS
scripts, sans en modifier une ligne, sur un monde fabriqué.
"""

import json, os, sys
import urllib.error, urllib.request

# Le 02/11, la collecte Riot est restée bloquée deux semaines sur un 403 causé
# par l'absence de User-Agent : urllib s'annonce « Python-urllib/3.x » et les
# bordures CDN rejettent cet agent. Ne jamais retirer cet en-tête.
AGENT = "OracleTFT/1.0 ({quoi}, usage personnel)"


def _rejouer(dossier, url, json_attendu):
    try:
        index = json.load(open(os.path.join(dossier, "index.json"), encoding="utf-8"))
    except Exception as e:
        sys.exit(f"REJEU : index.json illisible dans {dossier}\n  {e}")
    if url not in index:
        sys.exit(f"REJEU : lecture non prévue de {url}\n"
                 "  En rejeu, toute URL doit figurer dans index.json.")
    rep = index[url]
    if isinstance(rep, dict):
        if rep.get("http"):
            sys.exit(f"HTTP {rep['http']} sur {url}")
        if rep.get("panne"):
            sys.exit(f"Impossible de joindre {url}\n  rejeu : {rep['panne']}")
        sys.exit(f"REJEU : entrée d'index incomprise pour {url}")
    brut = open(os.path.join(dossier, rep), encoding="utf-8").read()
    return json.loads(brut) if json_attendu else brut


def lire(url, json_attendu=False, delai=30, quoi="relevé"):
    """Le contenu d'une URL publique, en texte ou en JSON.

    Sort du script avec un message lisible si la lecture échoue : un relevé
    qui ne peut pas lire sa source n'a rien à écrire, et le workflow décide
    étape par étape si cet échec est tolérable."""
    rejeu = os.environ.get("ORACLE_REJEU")
    if rejeu:
        return _rejouer(rejeu, url, json_attendu)

    req = urllib.request.Request(url, headers={
        "User-Agent": AGENT.format(quoi=quoi),
        "Accept": "application/json, text/html",
    })
    try:
        with urllib.request.urlopen(req, timeout=delai) as r:
            brut = r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        corps = ""
        try:
            corps = e.read(400).decode("utf-8", "replace").strip()
        except Exception:
            pass
        sys.exit(f"HTTP {e.code} sur {url}" + (f"\n  corps : {corps}" if corps else ""))
    except Exception as e:
        sys.exit(f"Impossible de joindre {url}\n  {type(e).__name__}: {e}\n"
                 "  (Depuis une session Claude, c'est normal : le proxy du "
                 "conteneur bloque ce domaine. Ce script est fait pour le "
                 "runner GitHub Actions.)")
    return json.loads(brut) if json_attendu else brut
