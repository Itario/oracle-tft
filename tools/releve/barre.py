#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LA BARRE — ce qu'il faut vraiment pour être Challenger -> data/barre.json
==========================================================================
Trois semaines de projet sans avoir jamais mesuré la cible. Le classement
public d'une région donne, pour chaque joueur : son palier, ses LP, son
nombre de parties, ses top 4 et ses premières places. Tout ce qu'il faut
pour savoir ce que la barre demande réellement.

    python3 tools/releve/barre.py            # EUW
    python3 tools/releve/barre.py --region na

⚠ Comme tools/releve/tactics.py : ne tourne pas depuis une session Claude,
le proxy du conteneur bloque le domaine. Fait pour le runner GitHub.

─── CE QUE CE FICHIER NE DIT PAS ──────────────────────────────────────────
Le taux de top 4 d'un Challenger est mesuré dans des lobbies Challenger.
Celui de Clément l'est dans des lobbies Diamant/Master. **Les deux chiffres
ne décrivent pas la même difficulté**, et comparer les deux directement
flatte le joueur du bas. Le nombre de PARTIES, lui, se compare sans
réserve : c'est un compte, pas une performance.
"""

import argparse, json, os, re, statistics as st, sys
import urllib.error, urllib.request
from datetime import date

RACINE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SORTIE = os.path.join(RACINE, "data", "barre.json")
SCHEMA = 1
PAGE = "https://tactics.tools/leaderboards/{region}"

EN_TETES = {
    "User-Agent": "OracleTFT/1.0 (relevé de classement, usage personnel)",
    "Accept": "text/html",
}


def lire(url):
    req = urllib.request.Request(url, headers=EN_TETES)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        sys.exit(f"HTTP {e.code} sur {url}")
    except Exception as e:
        sys.exit(f"Impossible de joindre {url}\n  {type(e).__name__}: {e}\n"
                 "  (Normal depuis une session Claude : le proxy du conteneur "
                 "bloque ce domaine. Ce script est fait pour le runner GitHub.)")


def stats(groupe):
    """Médianes d'un groupe de joueurs. La médiane, pas la moyenne : un
    joueur à 2 000 parties tirerait la moyenne sans rien dire de la barre."""
    if not groupe:
        return None
    med = lambda f: st.median([f(e) for e in groupe])
    return {
        "n_joueurs": len(groupe),
        "lp_median": int(med(lambda e: e["lp"])),
        "lp_min": min(e["lp"] for e in groupe),
        "parties_mediane": int(med(lambda e: e["g"])),
        "parties_min": min(e["g"] for e in groupe),
        "top4_pct_median": round(med(lambda e: e["t4"] / e["g"] * 100), 1),
        "premieres_pct_median": round(med(lambda e: e["w"] / e["g"] * 100), 1),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--region", default="euw")
    a = ap.parse_args()

    html = lire(PAGE.format(region=a.region))
    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S)
    if not m:
        sys.exit("__NEXT_DATA__ introuvable : la page du classement a changé "
                 "de structure.")
    pp = json.loads(m.group(1)).get("props", {}).get("pageProps", {})
    brut = (pp.get("data") or {}).get("entries") or []
    if not brut:
        sys.exit("Classement vide : props.pageProps.data.entries est absent.")

    E = []
    for e in brut:
        rang = e.get("rank") or []
        g = e.get("games") or 0
        if g <= 0 or len(rang) < 2:
            continue
        E.append({"palier": str(rang[0]).split(" ")[0], "lp": rang[1], "g": g,
                  "t4": e.get("top4") or 0, "w": e.get("won") or 0})
    if not E:
        sys.exit("Aucune entrée exploitable dans le classement.")

    ch = [e for e in E if e["palier"] == "CHALLENGER"]
    gm = [e for e in E if e["palier"] == "GRANDMASTER"]
    # Les derniers Challengers sont la vraie barre : la médiane de tout le
    # palier décrit des joueurs déjà installés, pas le ticket d'entrée.
    bas = sorted(ch, key=lambda e: e["lp"])[:25]

    out = {
        "schema_version": SCHEMA,
        "genere_le": date.today().isoformat(),
        "region": a.region.upper(),
        "source": "tactics.tools",
        "date_classement": (pp.get("data") or {}).get("date"),
        "entrees_lues": len(E),
        "paliers": {p: sum(1 for e in E if e["palier"] == p)
                    for p in sorted({e["palier"] for e in E})},
        "seuil_challenger_lp": min((e["lp"] for e in ch), default=None),
        "challenger": stats(ch),
        "challenger_derniers_25": stats(bas),
        "grandmaster": stats(gm),
        "reserve": ("Le taux de top 4 d'un Challenger est mesuré dans des lobbies "
                    "Challenger. Celui d'un joueur Master l'est dans des lobbies "
                    "Master. Les deux ne décrivent pas la même difficulté, et les "
                    "comparer directement flatte celui du bas. Le nombre de parties, "
                    "lui, se compare sans réserve : c'est un compte."),
    }

    os.makedirs(os.path.dirname(SORTIE), exist_ok=True)
    json.dump(out, open(SORTIE, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    b = out["challenger_derniers_25"]
    print(f"écrit : {SORTIE}")
    print(f"  {a.region.upper()} · {out['entrees_lues']} joueurs lus · "
          f"seuil Challenger {out['seuil_challenger_lp']} LP")
    print(f"  les 25 derniers Challengers : {b['parties_mediane']} parties, "
          f"{b['top4_pct_median']} % de top 4, {b['premieres_pct_median']} % de 1res")


if __name__ == "__main__":
    main()
