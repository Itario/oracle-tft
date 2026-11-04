#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CONSTRUCTEUR DU SITE — data/ -> data/meta/courant.json
=======================================================
Le site ne contient AUCUNE donnée en dur. Il lit `data/meta/courant.json`,
que ce script produit à partir des relevés.

C'est le point de couture qui rend la v2 possible : le jour où les données
viennent d'une base au lieu de fichiers, seul ce script change. Le site, lui,
continue de lire le même JSON au même endroit.

    python3 tools/build/build_site.py

Produit :
    data/meta/courant.json   tout ce dont le site a besoin, en un seul appel

À relancer après chaque nouveau relevé. La tâche planifiée du jeudi le fait.
"""

import json, os, sys
from datetime import date

# Le socle de mesure est partagé avec carnet.py : une seule implémentation.
sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import mesures as M

RACINE  = M.DEPOT
SORTIE  = os.path.join(RACINE, "data", "meta", "courant.json")
SCHEMA  = M.SCHEMA

charger_releves = M.charger
classement      = M.classement
spearman        = lambda a, b: M.spearman(a, b)[0]

# Champs internes au socle : utiles aux outils, inutiles au site.
# On les écarte pour ne pas gonfler la charge utile servie au navigateur.
_INTERNES = ("rangs_avant", "rangs_apres", "unites_avant", "unites_apres",
             "spearman_exact")

def diff(avant, apres):
    d = M.comparer(avant, apres)
    if d is None:
        return None
    d = {k: v for k, v in d.items() if k not in _INTERNES}
    d["montees"] = d["montees"][:5]
    d["chutes"]  = d["chutes"][:5]
    return d


def modes(compos):
    """Le même jeu de compos, classé selon trois enjeux différents."""
    def tri(cle, decroissant, filtre=None):
        src = [c for c in compos if (filtre is None or c.get(filtre) is not None)]
        return sorted(src, key=lambda c: c[cle], reverse=decroissant)[:5]
    return {
        "ladder": {
            "critere": "placement moyen", "cle": "avg", "unite": "",
            "pourquoi": "Le LP suit le placement moyen : à partir de la 4e on ne perd "
                        "plus, à partir de la 5e on ne gagne plus. À moyenne égale, la "
                        "variance est à peu près neutre.",
            "classement": tri("avg", False)},
        "cumule": {
            "critere": "taux de top 4", "cle": "t4", "unite": " %",
            "pourquoi": "Chaque bas de tableau coûte directement des points sur le "
                        "cumul. La régularité prime sur le coup d'éclat.",
            "classement": tri("t4", True, "t4")},
        "checkmate": {
            "critere": "taux de 1re place", "cle": "wr", "unite": " %",
            "pourquoi": "Seule la 1re place qualifie. Une 7e ne coûte rien de plus "
                        "qu'une 5e, donc le placement moyen ne veut plus rien dire.",
            "classement": tri("wr", True)},
    }


def main():
    rs = charger_releves()
    if not rs:
        sys.exit(f"Aucun relevé dans {RELEVES}")
    courant = rs[-1]
    print(f"relevé courant : {courant['date']} ({courant.get('patch')}, {courant.get('rang')})")

    # le diff le plus informatif : le dernier couple à MÊME tranche d'elo
    d = None
    for i in range(len(rs) - 1, 0, -1):
        cand = diff(rs[i - 1], rs[i])
        if cand and cand["meme_elo"]:
            d = cand
            break
    if d is None and len(rs) >= 2:
        d = diff(rs[-2], rs[-1])
        print("  (aucun couple à elo constant : diff à elo différent, signalé comme tel)")

    # stabilité de la tête sur toute la série
    tops = []
    for r in rs:
        g, _ = classement(r)
        tops.append([k for k in sorted(g, key=lambda x: g[x])[:8]])
    tete_commune = sorted(set(tops[0]).intersection(*[set(t) for t in tops[1:]])) if len(tops) > 1 else tops[0]

    g, u = classement(courant)
    ordre = sorted(g, key=lambda k: g[k])

    out = {
        "schema_version": SCHEMA,
        "genere_le": date.today().isoformat(),
        "releve": {
            "date": courant["date"], "patch": courant.get("patch"),
            "rang": courant.get("rang"), "source": courant.get("source"),
            "n_parties": courant.get("n_parties"), "fenetre": courant.get("fenetre"),
            "set": courant.get("set"), "note": courant.get("note"),
        },
        "diff": d,
        "tete_stable": {
            "unites": tete_commune,
            "n_releves": len(rs),
            "depuis": rs[0]["date"],
            "premiere_chaque_fois": tops[0][0] if all(t[0] == tops[0][0] for t in tops) else None,
        },
        "unites": [{"nom": k, "rang": g[k], "avg": u[k]["avg"],
                    "wr": u[k]["wr"], "n": u[k]["n"]} for k in ordre],
        "compos": courant.get("compos", []),
        "modes": modes(courant.get("compos", [])),
        "serie": [{"date": r["date"], "patch": r.get("patch"), "rang": r.get("rang"),
                   "n_parties": r.get("n_parties")} for r in rs],
    }

    os.makedirs(os.path.dirname(SORTIE), exist_ok=True)
    json.dump(out, open(SORTIE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    # Copie vers site/data/ pour le développement local. En production, le
    # workflow de déploiement fait la même chose — site/data/ n'est donc pas
    # versionné : la source reste data/.
    import shutil
    cible = os.path.join(RACINE, "site", "data")
    os.makedirs(os.path.join(cible, "meta"), exist_ok=True)
    shutil.copy(SORTIE, os.path.join(cible, "meta", "courant.json"))
    # ⚠ CETTE LISTE DOIT SUIVRE `SOURCES` DANS site/index.html.
    # Un fichier oublié ici ne provoque aucune erreur : le site reçoit un 404,
    # le bloc concerné ne s'affiche pas, et rien ne dit pourquoi. On annonce
    # donc les manquants à voix haute plutôt que de les laisser passer.
    attendus = ("profil.json", "calendrier.json", "miroir.json",
                "focus.json", "barre.json", "joueur.json",
                "objets.json", "recettes.json",
                "compos.json", "compos_lui.json")
    copies, manquants = [], []
    for f in attendus:
        src = os.path.join(RACINE, "data", f)
        if os.path.exists(src):
            shutil.copy(src, os.path.join(cible, f))
            copies.append(f)
        else:
            manquants.append(f)
    print(f"copié vers site/data/ : {len(copies)}/{len(attendus)} "
          f"({', '.join(copies)})")
    if manquants:
        print(f"  ⚠ absents de data/ : {', '.join(manquants)} — le site "
              f"affichera ces blocs vides, sans message d'erreur.")
    taille = os.path.getsize(SORTIE)
    print(f"écrit : {SORTIE} ({taille:,} octets)".replace(",", " "))
    if d:
        print(f"  diff {d['de']['patch']} -> {d['a']['patch']} : "
              f"Spearman {d['spearman']} · bruit {d['plancher_bruit']} · "
              f"{d['part_reelle_pct']} % réel")
    print(f"  tête stable sur {len(rs)} relevés : {len(tete_commune)} unités")


if __name__ == "__main__":
    main()
