#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MESURES — le socle commun des outils
=====================================
Lecture des relevés, classement, corrélation de rang, plancher de bruit.

Avant ce module, `carnet.py` et `build_site.py` portaient chacun leur copie
de ces calculs. Ils concordaient, mais rien ne le garantissait : toute
correction aurait dû être faite deux fois, et la première divergence serait
passée inaperçue. Un seul endroit, désormais.

Règle : ce module ne lit que `data/releves/`. Il n'écrit rien, n'affiche rien,
et ne connaît ni le site ni l'Oracle.
"""

import json, os, glob, random, statistics as st
from datetime import date

SCHEMA = 1            # version de format attendue pour un relevé
NMIN = 2000           # volume minimal pour qu'une unité soit classée
SD_PLACEMENT = 2.3    # écart-type du placement en TFT, ~constant
GRAINE = 1            # graine fixe : deux exécutions donnent le même chiffre

DEPOT   = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RELEVES = os.path.join(DEPOT, "data", "releves")


# ------------------------------------------------------------------ lecture

def charger(dossier=None, strict=True):
    """Tous les relevés, du plus ancien au plus récent.
       strict=True écarte ce qui n'est pas au bon format, en le disant."""
    dossier = dossier or RELEVES
    out = []
    for f in sorted(glob.glob(os.path.join(dossier, "*.json"))):
        try:
            d = json.load(open(f, encoding="utf-8"))
        except Exception as e:
            print(f"  ! {os.path.basename(f)} illisible : {e}")
            continue
        v = d.get("schema_version")
        if strict and v != SCHEMA:
            print(f"  ! {os.path.basename(f)} : schema_version {v} ignoré "
                  f"(attendu {SCHEMA})")
            continue
        d["_fichier"] = os.path.basename(f)
        out.append(d)
    return sorted(out, key=lambda d: d["date"])


def par_date(releves, d):
    for r in releves:
        if r["date"] == d:
            return r
    return None


# ------------------------------------------------------------------ mesures

def classement(releve, nmin=NMIN):
    """(rang par unité, unités retenues). Une unité sous `nmin` n'est pas classée :
       son placement moyen est trop bruité pour être ordonné."""
    u = {k: v for k, v in releve["unites"].items() if v["n"] >= nmin}
    ordre = sorted(u, key=lambda k: u[k]["avg"])
    return {k: i + 1 for i, k in enumerate(ordre)}, u


def spearman(a, b):
    """Corrélation de rang sur les clés communes. 1 = classement identique.
       Renvoie (rho, n) ; rho vaut None sous trois unités communes."""
    com = sorted(set(a) & set(b))
    n = len(com)
    if n < 3:
        return None, n
    d2 = sum((a[k] - b[k]) ** 2 for k in com)
    return 1 - (6 * d2) / (n * (n ** 2 - 1)), n


def plancher_bruit(ua, ub, com, tirages=400, graine=GRAINE):
    """Corrélation qu'on obtiendrait si RIEN n'avait changé, aux volumes réels
       de chaque relevé. Tout écart au-delà est du vrai mouvement.

       Sans ce plancher, un relevé à faible volume paraît toujours « bouger » :
       des unités séparées de 0.01 place permutent par simple hasard."""
    rnd = random.Random(graine)
    sims = []
    for _ in range(tirages):
        va = sorted((ua[k]["avg"] + rnd.gauss(0, SD_PLACEMENT / ua[k]["n"] ** .5), k)
                    for k in com)
        vb = sorted((ua[k]["avg"] + rnd.gauss(0, SD_PLACEMENT / ub[k]["n"] ** .5), k)
                    for k in com)
        ra = {k: i + 1 for i, (_, k) in enumerate(va)}
        rb = {k: i + 1 for i, (_, k) in enumerate(vb)}
        s, _ = spearman(ra, rb)
        if s is not None:
            sims.append(s)
    return st.mean(sims) if sims else None


def comparer(avant, apres, nmin=NMIN, avec_bruit=True):
    """Tout ce qu'on sait dire de l'écart entre deux relevés."""
    ga, ua = classement(avant, nmin)
    gb, ub = classement(apres, nmin)
    com = sorted(set(ga) & set(gb))
    if not com:
        return None
    obs, n = spearman(ga, gb)
    plancher = plancher_bruit(ua, ub, com) if avec_bruit else None
    reel = (plancher - obs) if (plancher is not None and obs is not None) else None
    dep = sorted(((gb[k] - ga[k], k) for k in com))
    absd = [abs(d) for d, _ in dep]

    def ligne(d, k):
        return {"nom": k, "rang_avant": ga[k], "rang_apres": gb[k], "delta": d,
                "avg_avant": ua[k]["avg"], "avg_apres": ub[k]["avg"]}

    def topn(g, n_):
        return set(sorted(g, key=lambda k: g[k])[:n_])

    return {
        "de": {"date": avant["date"], "patch": avant.get("patch"), "rang": avant.get("rang")},
        "a":  {"date": apres["date"], "patch": apres.get("patch"), "rang": apres.get("rang")},
        "jours": (date.fromisoformat(apres["date"]) - date.fromisoformat(avant["date"])).days,
        "meme_elo": avant.get("rang") == apres.get("rang"),
        "n_comparables": n,
        "spearman": round(obs, 3) if obs is not None else None,
        "spearman_exact": obs,
        "plancher_bruit": round(plancher, 3) if plancher is not None else None,
        "mouvement_reel": round(reel, 3) if reel is not None else None,
        "part_reelle_pct": round(100 * reel / max(1 - obs, 1e-9)) if reel is not None else None,
        "deplacement_median": int(st.median(absd)),
        "deplacement_moyen": round(st.mean(absd), 1),
        "deplacement_max": max(absd),
        "top8_conserve": len(topn(ga, 8) & topn(gb, 8)),
        "entres_top8": sorted(topn(gb, 8) - topn(ga, 8)),
        "sortis_top8": sorted(topn(ga, 8) - topn(gb, 8)),
        "montees": [ligne(d, k) for d, k in dep[:8]],
        "chutes":  [ligne(d, k) for d, k in dep[-8:]][::-1],
        "delta_avg_median": round(st.median([ub[k]["avg"] - ua[k]["avg"] for k in com]), 3),
        "rangs_avant": ga, "rangs_apres": gb, "unites_avant": ua, "unites_apres": ub,
    }


def tete_stable(releves, n=8, nmin=NMIN):
    """Les unités présentes dans le top n de TOUS les relevés."""
    tops = []
    for r in releves:
        g, _ = classement(r, nmin)
        tops.append([k for k in sorted(g, key=lambda x: g[x])[:n]])
    if not tops:
        return {"unites": [], "n_releves": 0}
    commun = set(tops[0]).intersection(*[set(t) for t in tops[1:]]) if len(tops) > 1 else set(tops[0])
    return {
        "unites": sorted(commun, key=lambda k: tops[-1].index(k) if k in tops[-1] else 99),
        "n_releves": len(releves),
        "depuis": releves[0]["date"],
        "premiere_chaque_fois": tops[0][0] if all(t and t[0] == tops[0][0] for t in tops) else None,
    }
