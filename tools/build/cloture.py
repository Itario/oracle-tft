#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LA CLÔTURE D'UN SET — data/*.json -> data/archive/set<N>/
==========================================================
Le jour où un set commence, tout ce qui décrit le précédent est réécrit dans
les heures qui suivent : la position repart de zéro, la barre aussi, les
compos sont celles du nouveau patch. Rien de tout cela n'est versionné
ailleurs que dans l'historique git — c'est-à-dire nulle part où le site ou un
script irait le chercher.

Or la fin d'un set est exactement ce qu'on voudra relire : où il a fini, à
quel rythme, avec quel barème, ce que jouait la tête du classement. C'est le
point de départ de toute comparaison « Set 18 contre Set 19 ».

    python3 tools/build/cloture.py

Tourne dans le workflow de relevé, JUSTE APRÈS tactics.py et AVANT les autres
relevés. À ce moment précis, si le set vient de changer :

    data/releves-tt/   contient déjà le premier relevé du nouveau set ;
    data/joueur.json, data/barre.json, data/compos.json…
                       sont encore ceux du DERNIER relevé de l'ancien set.

C'est la seule fenêtre où les deux coexistent. On copie les seconds dans
data/archive/set<N>/, une fois, et on n'y touche plus.

Ne fait rien le reste du temps : hors changement de set, tous les fichiers
sont du set courant et il n'y a rien à archiver.
"""

import json, os, shutil, sys
from datetime import date

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import mesures as M

DATA = os.path.join(M.DEPOT, "data")
# Ce qui décrit un set et sera écrasé par le suivant. Pas calendrier.json ni
# profil.json (ils ne sont pas d'un set), pas les relevés d'unités (la série
# data/releves-tt/ les garde tous, un fichier par patch).
A_ARCHIVER = ("joueur.json", "barre.json", "compos.json", "recettes.json",
              "miroir.json", "focus.json", "objets.json", "compos_lui.json",
              "fuites.json", "contestation.json")


def main():
    courant = M.set_courant()
    if courant is None:
        print("clôture : aucun relevé, rien à faire.")
        return

    faits = {}
    for nom in A_ARCHIVER:
        src = os.path.join(DATA, nom)
        try:
            d = json.load(open(src, encoding="utf-8"))
        except Exception:
            continue
        s = d.get("set")
        if not isinstance(s, int) or s == courant:
            continue
        cible = os.path.join(DATA, "archive", f"set{s}", nom)
        if os.path.exists(cible):
            continue                 # archivé une fois, jamais réécrit
        os.makedirs(os.path.dirname(cible), exist_ok=True)
        shutil.copy(src, cible)
        faits.setdefault(s, []).append(nom)

    if not faits:
        print(f"clôture : tout est du Set {courant} (ou déjà archivé), rien à faire.")
        return

    for s, noms in sorted(faits.items()):
        dossier = os.path.join(DATA, "archive", f"set{s}")
        manifeste = os.path.join(dossier, "_cloture.json")
        try:
            m = json.load(open(manifeste, encoding="utf-8"))
        except Exception:
            m = {"set": s, "fichiers": {}}
        for nom in noms:
            m["fichiers"][nom] = date.today().isoformat()
        m["note"] = (f"État des fichiers au dernier relevé du Set {s}, copiés le jour "
                     f"où la série automatique est passée au Set {courant}. Ils ne "
                     "sont plus jamais réécrits. Une récolte de parties faite après "
                     "le changement de set n'y figure pas : miroir.json est celui "
                     "de la dernière récolte ANTÉRIEURE.")
        M.ecrire(manifeste, m)
        print(f"clôture du Set {s} : {len(noms)} fichier(s) archivé(s) dans "
              f"data/archive/set{s}/ — {', '.join(noms)}")


if __name__ == "__main__":
    main()
