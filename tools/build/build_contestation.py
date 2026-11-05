#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LA CONTESTATION, CONTRE CE QU'ELLE DEVRAIT ÊTRE -> data/contestation.json
==========================================================================
    python3 tools/build/build_contestation.py <contestation_resume.json>

Le résumé produit sur sa machine dit combien d'adversaires jouaient la même
unité que lui. Seul, ce chiffre ne veut rien dire : une unité jouée par un
tiers du ladder SERA contestée, et ce n'est pas une erreur de sa part.

Ce fichier ajoute le repère qui manque. Si une unité est présente sur p % des
plateaux du ladder, on attend **7 × p** de ses sept adversaires dessus. Le
rapport entre l'observé et cet attendu est la seule lecture honnête :

    rapport < 1   il la trouve MOINS disputée que la moyenne du ladder
    rapport > 1   il tombe dessus plus souvent que le hasard ne l'explique

─── CE QUE CE FICHIER NE DIT PAS ──────────────────────────────────────────
**Le repère ne vaut que pour la PRÉSENCE.** Le relevé donne la part des
plateaux portant l'unité ; il ne dit pas quelle fraction la portait AVEC des
objets. Il n'y a donc pas d'attendu pour les « porteurs », et le rapport
n'est calculé que sur la présence. Les porteurs restent affichés bruts.

**Le biais de sous-comptage du résumé se propage ici.** Le joueur qui perd
une contestation meurt tôt et n'apparaît pas : tout rapport calculé ici est
un plancher.

**Un rapport supérieur à 1 n'est pas une faute.** Il peut vouloir dire qu'il
joue aux heures où cette unité est populaire, ou qu'il la force quand il la
voit libre tôt. Le fichier mesure, il n'interprète pas.
"""

import json, os, sys
from datetime import date

RACINE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(RACINE, "tools", "lib"))
import mesures as M

SORTIE = os.path.join(RACINE, "data", "contestation.json")
SCHEMA = 1
ADVERSAIRES = 7


def dernier_releve():
    import glob
    fs = sorted(glob.glob(os.path.join(RACINE, "data", "releves-tt", "*.json")))
    return json.load(open(fs[-1], encoding="utf-8")) if fs else None


def main(chemin_resume):
    try:
        r = json.load(open(chemin_resume, encoding="utf-8"))
    except Exception as e:
        sys.exit(f"Résumé illisible : {chemin_resume}\n  {e}")

    rel = dernier_releve()
    # Part des plateaux du ladder portant chaque champion, variantes
    # regroupées — tactics.tools éclate Lux en dix entrées.
    pick = {}
    if rel and rel.get("n_parties"):
        tot = rel["n_parties"]
        for uid, u in (rel.get("unites") or {}).items():
            c = M.champion(uid)
            if c:
                pick[c] = pick.get(c, 0) + (u.get("n") or 0)
        pick = {c: n / tot for c, n in pick.items()}

    champions = []
    for c in (r.get("par_champion") or []):
        ch = c["champion"]
        p = pick.get(ch)
        attendu = round(ADVERSAIRES * p, 2) if p is not None else None
        obs = c.get("presence_moyenne")
        champions.append({
            **c,
            "pick_ladder_pct": round(100 * p, 1) if p is not None else None,
            "presence_attendue": attendu,
            "rapport": (round(obs / attendu, 2)
                        if (attendu and obs is not None and attendu > 0) else None),
        })

    # Ceux où il tombe sur l'unité PLUS souvent que le ladder ne l'explique.
    sur = sorted((c for c in champions if c.get("rapport") is not None),
                 key=lambda c: -c["rapport"])

    out = {
        "schema_version": SCHEMA,
        "genere_le": date.today().isoformat(),
        "set": r.get("set"),
        "n_parties": r.get("n_parties"),
        "patch_releve": (rel or {}).get("patch"),
        "adversaires": ADVERSAIRES,
        "definitions": r.get("definitions"),
        # ⭐ Le test de la croyance que la charte porte depuis le début :
        # « à placement égal, la ligne la moins contestée gagne ».
        "global": r.get("global"),
        "par_champion": champions,
        "plus_disputes_que_prevu": sur[:6],
        "moins_disputes_que_prevu": sur[-6:][::-1],
        "reserves": {
            "repere_presence_seulement": (
                "Le relevé donne la part des plateaux portant l'unité, pas la "
                "fraction qui la portait AVEC des objets. Le rapport n'est "
                "donc calculé que sur la présence ; les porteurs restent bruts."),
            "plancher": (
                "Le joueur qui PERD une contestation meurt tôt, sans objets "
                "sur l'unité disputée, et n'apparaît pas comme contestant. "
                "Tout chiffre ici est un plancher."),
            "pas_une_faute": (
                "Un rapport supérieur à 1 n'est pas une erreur de jeu : il "
                "peut venir des heures auxquelles il joue, ou du fait qu'il "
                "force une unité quand il la voit libre tôt. On mesure, on "
                "n'interprète pas."),
        },
    }

    os.makedirs(os.path.dirname(SORTIE), exist_ok=True)
    json.dump(out, open(SORTIE, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    print(f"écrit : {SORTIE}")
    print(f"  {out['n_parties']} parties · set {out['set']} · "
          f"repère du patch {out['patch_releve']}")
    g = out["global"] or {}
    if g:
        print(f"  seul {g['placement_seul']} ({g['n_seul']}) · "
              f"contesté {g['placement_conteste']} ({g['n_conteste']}) · "
              f"écart {g['ecart']:+} ± {g['seuil_bruit']} -> "
              f"{'SOLIDE' if g['solide'] else 'dans le bruit'}")
    for c in out["plus_disputes_que_prevu"][:4]:
        print(f"    {c['champion']:<13} vu {c['presence_moyenne']} fois en face, "
              f"attendu {c['presence_attendue']} -> rapport {c['rapport']}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1])
