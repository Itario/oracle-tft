#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CONSTRUCTEUR DU MIROIR — parties de Clément -> data/miroir.json
================================================================
Le site ne lit jamais les parties elles-mêmes. Il lit cet agrégat.

POURQUOI un fichier séparé plutôt que les parties : chaque fichier de partie
contient le puuid des SEPT ADVERSAIRES du lobby. C'est de la donnée
personnelle de tiers, elle ne quitte pas la machine. `data/miroir.json` ne
porte que les mesures de Clément — aucun identifiant, aucun adversaire.

    python3 tools/build/build_miroir.py <set18_propre.csv> <miroir_set18.json>

Les deux entrées viennent d'UNE SEULE exécution de miroir.py :

    python miroir.py --set 18 --csv set18_propre.csv --sortie miroir_set18.json

Le CSV est déjà filtré par miroir.py (parties lâchées retirées) : on ne
réimplémente pas le filtre ici, on ne compte que ce qu'il a laissé passer.

RÈGLE DE LECTURE. Aucun écart n'est affiché comme un fait sans son seuil de
bruit. À 114 parties, un trait vu 20 fois a une erreur-type de 0,49 place :
un écart de 0,3 ne veut rien dire. Le champ `solide` porte ce jugement, et
le site doit le respecter — sinon on produit des conseils tirés du hasard.
"""

import csv, json, math, os, statistics as st, sys
from collections import defaultdict

RACINE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SORTIE = os.path.join(RACINE, "data", "miroir.json")
SCHEMA = 1
NMIN   = 12          # en dessous, on n'affiche rien : l'erreur-type explose


def z(obs, n, p):
    """Écart à ce que donnerait le hasard, en écarts-types."""
    sd = math.sqrt(n * p * (1 - p))
    return round((obs - n * p) / sd, 2) if sd else None


def groupes(lignes, cle, base, sdp):
    """Traits ou carries, comparés à SA propre moyenne — jamais à 4.50.

    Comparer un trait à 4.50 mesure surtout son niveau général ; le comparer
    à sa moyenne à lui mesure ce que CE trait lui apporte."""
    paquets = defaultdict(list)
    for r in lignes:
        for x in (r[cle] or "").split("|"):
            if x:
                paquets[x].append(r["placement"])
    out = []
    for nom, v in paquets.items():
        if len(v) < NMIN:
            continue
        moy = st.mean(v)
        ecart = moy - base
        err = sdp / math.sqrt(len(v))
        out.append({
            "nom": nom, "n": len(v),
            "placement": round(moy, 2),
            "ecart": round(ecart, 2),
            "solide": abs(ecart) >= 2 * err,
            "seuil": round(2 * err, 2),
        })
    return sorted(out, key=lambda d: d["ecart"])


def main(csv_path, resume_path):
    L = list(csv.DictReader(open(csv_path, encoding="utf-8")))
    for r in L:
        for k in ("placement", "niveau", "or_restant", "dernier_tour",
                  "rang_niveau", "rang_degats"):
            try:
                r[k] = float(r[k])
            except Exception:
                r[k] = None
    L = [r for r in L if r["placement"]]
    if not L:
        sys.exit("CSV vide ou illisible.")
    L.sort(key=lambda r: r["date"] or "")

    resume = json.load(open(resume_path, encoding="utf-8"))
    pl   = [r["placement"] for r in L]
    n    = len(pl)
    base = st.mean(pl)
    sdp  = st.stdev(pl) if n > 1 else 0
    dist = {str(k): sum(1 for p in pl if int(p) == k) for k in range(1, 9)}

    # Les champs que la migration Unreal a vidés : on les déclare morts ici
    # plutôt que de laisser le site afficher des zéros comme des mesures.
    degats_vides = all((r.get("degats") in (None, "", "0", "0.0", 0)) for r in L)

    out = {
        "schema_version": SCHEMA,
        "set": resume.get("set"),
        "n_parties": n,
        "fenetre": {"de": L[0]["date"], "a": L[-1]["date"]},
        "placement_moyen": round(base, 3),
        "top4_pct": round(sum(1 for p in pl if p <= 4) / n * 100, 1),
        "premieres_pct": round(sum(1 for p in pl if p == 1) / n * 100, 1),
        "distribution": dist,
        "ecarts": {
            "top2":  z(dist["1"] + dist["2"], n, .25),
            "top4":  z(sum(dist[str(k)] for k in (1, 2, 3, 4)), n, .50),
            "bas2":  z(dist["7"] + dist["8"], n, .25),
            "huit":  z(dist["8"], n, .125),
        },
        "seuil_solide": 2.0,
        "rang_niveau_moyen": round(st.mean([r["rang_niveau"] for r in L
                                            if r["rang_niveau"]]), 2),
        "or_restant_median": st.median([r["or_restant"] for r in L
                                        if r["or_restant"] is not None]),
        "lachees": [
            {"date": x["date"], "placement": x["placement"],
             "niveau": x["niveau"], "or_restant": x["or_restant"]}
            for x in resume.get("parties_lachees_retirees", [])
        ],
        "zone_grise": len(resume.get("parties_zone_grise", [])),
        "traits":  groupes(L, "traits",  base, sdp),
        "carries": groupes(L, "carries", base, sdp),
        "indisponible": {
            "augments": "Champ absent du DTO Riot depuis la migration Unreal "
                        "du Set 18. La revue des augments n'est pas constructible.",
            **({"degats": "total_damage_to_players vide sur toutes les parties "
                          "du Set 18. Le rang de dégâts est sans valeur."}
               if degats_vides else {}),
        },
        "nmin": NMIN,
    }

    os.makedirs(os.path.dirname(SORTIE), exist_ok=True)
    json.dump(out, open(SORTIE, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    sol_t = sum(1 for t in out["traits"] if t["solide"])
    sol_c = sum(1 for c in out["carries"] if c["solide"])
    print(f"écrit : {SORTIE}")
    print(f"  {n} parties · placement {out['placement_moyen']} · "
          f"{len(out['lachees'])} lâchées écartées")
    print(f"  {len(out['traits'])} traits retenus (n>={NMIN}), dont {sol_t} hors du bruit")
    print(f"  {len(out['carries'])} carries retenus, dont {sol_c} hors du bruit")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
