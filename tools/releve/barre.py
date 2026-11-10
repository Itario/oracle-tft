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
# La seule porte vers l'extérieur vit dans tools/lib/reseau.py : une définition,
# et un mode rejeu qui permet de répéter le 1er décembre sans réseau.
sys.path.insert(0, os.path.join(RACINE, "tools", "lib"))
from reseau import lire as _lire
import mesures as M


def lire(url, **kw):
    return _lire(url, quoi="relevé de classement", **kw)

SORTIE = os.path.join(RACINE, "data", "barre.json")
SCHEMA = 1
PAGE = "https://tactics.tools/leaderboards/{region}"





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
    if "data" not in pp:
        # La page n'a plus la forme attendue : ça, c'est une vraie panne, et
        # on ne touche pas au fichier de la veille.
        sys.exit("props.pageProps.data absent : la page du classement a "
                 "changé de structure.")
    brut = (pp.get("data") or {}).get("entries") or []

    E = []
    for e in brut:
        rang = e.get("rank") or []
        g = e.get("games") or 0
        if g <= 0 or len(rang) < 2:
            continue
        E.append({"palier": str(rang[0]).split(" ")[0], "lp": rang[1], "g": g,
                  "t4": e.get("top4") or 0, "w": e.get("won") or 0})

    # ── UN CLASSEMENT VIDE N'EST PAS UNE PANNE ───────────────────────────
    #
    # Jusqu'au 10/11, ce script sortait en erreur sur un classement vide, puis
    # plantait (TypeError) sur un classement sans Challenger. Les deux cas ne
    # se produisent jamais en cours de set — et se produisent TOUS LES DEUX,
    # à coup sûr, dans la semaine qui suit un changement de set : le
    # classement repart de zéro, et Challenger n'ouvre que quelques jours
    # plus tard. Comme cette étape n'est pas tolérée dans le workflow, le
    # relevé entier mourait : rien n'était poussé, pas même le premier relevé
    # du nouveau set. Trouvé par tools/tests/repetition.py, pas en production.
    #
    # Un classement vide est une INFORMATION sur le monde. Elle s'écrit dans
    # le fichier (`etat`), et le site l'affiche au lieu d'une barre périmée.
    ch = [e for e in E if e["palier"] == "CHALLENGER"]
    etat = ("ferme" if not E else
            "sans_challenger" if not ch else "ouvert")

    # ── DE QUEL SET PARLE CE CLASSEMENT ? ────────────────────────────────
    # La page ne le dit pas. On sait quel set est en ligne par le relevé
    # (tactics.py tourne juste avant). Mais le jour d'un changement de set,
    # la page du classement peut encore servir le classement FINAL du set
    # précédent pendant que le relevé d'unités est déjà passé au suivant —
    # et la barre du Set 18 serait alors affichée comme celle du Set 19.
    #
    # Garde physique : personne ne joue plus de 40 parties par jour. Si la
    # médiane des Challengers dépasse ce que la durée du set autorise, ce
    # classement n'est pas celui du set courant. Elle ne s'applique que si on
    # a VU le set commencer (M.debut_du_set) — sinon on ne sait pas depuis
    # quand il dure, et on ne coupe rien.
    set_courant = M.set_courant()
    debut = M.debut_du_set()
    set_du_classement = set_courant
    if etat == "ouvert" and debut:
        jours = (date.today() - date.fromisoformat(debut)).days + 1
        med = st.median(e["g"] for e in ch)
        if med > 40 * jours:
            etat = "classement_du_set_precedent"
            set_du_classement = set_courant - 1 if isinstance(set_courant, int) else None

    gm = [e for e in E if e["palier"] == "GRANDMASTER"]
    # Les derniers Challengers sont la vraie barre : la médiane de tout le
    # palier décrit des joueurs déjà installés, pas le ticket d'entrée.
    bas = sorted(ch, key=lambda e: e["lp"])[:25]

    # ── LE SEUIL : trois estimateurs, parce que le premier était mauvais ──
    #
    # min(LP des joueurs étiquetés Challenger) est une statistique d'ordre
    # sur UN SEUL joueur. Mesurée trois fois en 24 h, elle a donné 447, 740
    # puis 677 LP — pendant que la MÉDIANE des 25 derniers restait à 728,
    # 750, 743 et leur taux de top 4 à 54.7, 54.7, 54.1. Ce n'est donc pas
    # le ladder qui bougeait, c'est l'estimateur qui était fragile : les
    # étiquettes de palier sont réattribuées périodiquement, et un joueur
    # en cours de rétrogradation reste marqué CHALLENGER avec peu de LP.
    #
    # `seuil_par_rang` ne regarde aucune étiquette : Challenger est le top N
    # par LP, donc le seuil est le LP du N-ième joueur de la liste triée.
    # C'est la définition structurelle, immunisée contre le retard des
    # étiquettes. C'est celle que le site affiche.
    par_lp = sorted(E, key=lambda e: -e["lp"])
    n_ch = len(ch)
    seuil_rang = par_lp[n_ch - 1]["lp"] if 0 < n_ch <= len(par_lp) else None
    lps_ch = sorted(e["lp"] for e in ch)
    seuil_p10 = lps_ch[max(0, int(len(lps_ch) * 0.10) - 1)] if lps_ch else None

    out = {
        "schema_version": SCHEMA,
        "genere_le": date.today().isoformat(),
        "region": a.region.upper(),
        "source": "tactics.tools",
        # Le set dont ce classement parle, et l'état du classement. Le site
        # compare `set` au set courant et lit `etat` avant d'afficher quoi
        # que ce soit : une barre sans ces deux champs est une barre qu'on
        # ne sait ni dater ni cacher.
        "set": set_du_classement,
        "etat": etat,
        "etat_note": {
            "ouvert": None,
            "ferme": "Le classement est vide : la saison classée n'a pas "
                     "encore produit de classement. Il n'y a pas de barre à "
                     "mesurer, et ce n'est pas une panne.",
            "sans_challenger": "Personne n'est encore Challenger : le palier "
                     "n'ouvre que quelques jours après le début de la saison. "
                     "Il n'y a pas encore de barre — seulement le haut du "
                     "classement, donné plus bas à titre indicatif.",
            "classement_du_set_precedent": "Ce classement porte plus de "
                     "parties que le set courant n'en permet depuis son "
                     "début : c'est encore le classement FINAL du set "
                     "précédent. Il n'est pas la barre du set en cours.",
        }[etat],
        "date_classement": (pp.get("data") or {}).get("date"),
        "entrees_lues": len(E),
        "paliers": {p: sum(1 for e in E if e["palier"] == p)
                    for p in sorted({e["palier"] for e in E})},
        # Celui que le site affiche : la définition structurelle.
        "seuil_challenger_lp": seuil_rang,
        # Les deux autres, pour qu'on puisse voir l'écart plutôt que le subir.
        "seuil_estimateurs": {
            "par_rang": seuil_rang,
            "percentile_10": seuil_p10,
            "min_etiquette": min((e["lp"] for e in ch), default=None),
            "note": "min_etiquette est VOLATILE : statistique d'ordre sur un "
                    "seul joueur, et les étiquettes de palier sont réattribuées "
                    "avec du retard. Mesurée 447, 740 puis 677 LP en 24 h alors "
                    "que la médiane des 25 derniers ne bougeait pas. Ne pas "
                    "l'afficher.",
        },
        "challenger": stats(ch),
        "challenger_derniers_25": stats(bas),
        "grandmaster": stats(gm),
        # Sans Challenger, le seul repère honnête est le haut du classement
        # tel qu'il est : le LP du 1er, celui du 250e. Ce n'est PAS un seuil.
        "haut_du_classement": ({
            "lp_premier": par_lp[0]["lp"],
            "lp_250e": par_lp[249]["lp"] if len(par_lp) >= 250 else None,
            "parties_mediane_top_250": int(st.median(
                e["g"] for e in par_lp[:250])),
            "note": "Indicatif : aucun palier Challenger n'existe encore, "
                    "donc aucun seuil. Le 250e n'est pas « la barre »."}
            if (etat == "sans_challenger" and par_lp) else None),
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
    es = out["seuil_estimateurs"]
    print(f"  {a.region.upper()} · {out['entrees_lues']} joueurs lus · "
          f"set {set_du_classement} · état : {etat}")
    if etat != "ouvert":
        print(f"  {out['etat_note']}")
    if b:
        print(f"  seuil Challenger : {es['par_rang']} LP (par rang) · "
              f"{es['percentile_10']} (p10) · {es['min_etiquette']} (min, volatile)")
        print(f"  les 25 derniers Challengers : {b['parties_mediane']} parties, "
              f"{b['top4_pct_median']} % de top 4, {b['premieres_pct_median']} % de 1res")


if __name__ == "__main__":
    main()
