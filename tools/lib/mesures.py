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

import json, os, glob, random, re, statistics as st
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

    # ── ⚠ LE PIÈGE DU VOLUME INÉGAL ──────────────────────────────────────
    #
    # Mesuré le 05/11 sur 18.5c -> 18.6 : le relevé d'arrivée avait 54 954
    # parties contre 500 777 au départ, soit 11 % du volume. SEIZE unités
    # sont passées sous le seuil `nmin`, dont les HUIT variantes de Lux —
    # c'est-à-dire tout le haut du classement de départ.
    #
    # Conséquences, toutes invisibles dans le Spearman seul :
    #   - on compare 57 unités là où le relevé mûr en portait 73 ;
    #   - « 0/8 de la tête conservée » est un artefact de volume, pas un
    #     bouleversement de la méta ;
    #   - le déplacement médian n'est pas comparable à celui d'une transition
    #     mesurée entre deux relevés mûrs, parce que les rangs se tassent.
    #
    # Le Spearman sur le sous-ensemble commun reste valide pour CE
    # sous-ensemble. Ce qui ne l'est pas, c'est de le comparer aux
    # transitions historiques, toutes mesurées entre relevés mûrs.
    na, nb = avant.get("n_parties") or 0, apres.get("n_parties") or 0
    ratio = (min(na, nb) / max(na, nb)) if max(na, nb) else None
    perdues = sorted(set(ga) - set(gb))
    gagnees = sorted(set(gb) - set(ga))
    volume_comparable = bool(ratio and ratio >= 0.5 and len(perdues) <= 3)

    return {
        "de": {"date": avant["date"], "patch": avant.get("patch"), "rang": avant.get("rang")},
        "a":  {"date": apres["date"], "patch": apres.get("patch"), "rang": apres.get("rang")},
        "jours": (date.fromisoformat(apres["date"]) - date.fromisoformat(avant["date"])).days,
        "meme_elo": avant.get("rang") == apres.get("rang"),
        "n_comparables": n,
        "volume": {
            "n_avant": na, "n_apres": nb,
            "ratio": round(ratio, 3) if ratio else None,
            "unites_perdues": perdues,
            "unites_gagnees": gagnees,
            "comparable": volume_comparable,
            "avertissement": None if volume_comparable else (
                f"VOLUMES TRÈS INÉGAUX ({na:,} contre {nb:,} parties) : "
                f"{len(perdues)} unité(s) sont passées sous le seuil de "
                f"{nmin} parties et sortent de la comparaison. Le Spearman "
                "reste valide POUR LE SOUS-ENSEMBLE COMMUN, mais ni la "
                "rotation de tête ni le déplacement médian ne se comparent "
                "aux transitions mesurées entre deux relevés mûrs. "
                "Refaire la mesure quand le patch d'arrivée aura mûri."
            ).replace(",", " "),
        },
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


# ── « LA MÊME UNITÉ » ────────────────────────────────────────────────────
# Définition PARTAGÉE. Elle existait en QUATRE exemplaires le 05/11 —
# build_focus, build_objets, build_compos et, imbriquée, unites_jouees().
# Les quatre étaient identiques ce jour-là, donc aucun bug actif : mais la
# prochaine correction en aurait fait diverger une, et deux fichiers qui
# répondent différemment à « est-ce la même unité ? » produisent deux pages
# qui se contredisent. C'est arrivé le 04/11 avec « ce qu'il joue ».
#
# tactics.tools éclate Lux en DIX entrées (Lux_Moonbeam, Lux_Sunbeam, …) et
# MetaTFT n'en voit qu'une. Sans regroupement, chaque variante compte pour
# une unité distincte et la contestation devient illisible.

def champion(ident):
    """Le champion seul : sans variante, sans numéro de set, sans préfixe."""
    toks = [re.sub(r"\d+", "", t) for t in str(ident).split("_")
            if t and t != "DA"]
    toks = [t for t in toks if t]
    return toks[0].lower() if toks else ""


# ── CE QU'IL JOUE ────────────────────────────────────────────────────────
# Définition PARTAGÉE, et elle l'est pour une raison précise.
#
# Le 04/11, deux blocs de la même page se contredisaient : le Focus affichait
# « tu la joues » pour murkwolf, le croisement des compos le comptait inconnu.
# Aucun des deux ne se trompait — ils employaient deux définitions :
#
#   build_focus.py   carries (n>=12) OU porteur d'une des 50 dernières parties
#   build_compos.py  carries (n>=12) seulement
#
# Deux fichiers portaient le même fait sous le même mot. La définition vit
# donc ici, et les deux nuances sont RENDUES au lieu d'être aplaties : avoir
# sorti une unité une fois en cinquante parties n'est pas la jouer, mais ce
# n'est pas non plus ne jamais l'avoir touchée.

def unites_jouees(miroir):
    """{champion: 'regulier'|'occasionnel'} d'après ses parties.

    `regulier`    : il la porte assez souvent pour qu'on mesure son placement
                    dessus (elle est dans miroir.carries, donc n >= NMIN).
    `occasionnel` : elle apparaît comme porteuse dans ses dernières parties,
                    sans atteindre ce seuil.
    Absente du dictionnaire : jamais vue comme porteuse.
    """
    out = {}
    for x in (miroir.get("parties") or []):
        for p in (x.get("pieces") or []):
            c = champion(p)
            if c:
                out.setdefault(c, "occasionnel")
    for c in (miroir.get("carries") or []):
        ch = champion(c.get("nom", ""))
        if ch:
            out[ch] = "regulier"
    return out
