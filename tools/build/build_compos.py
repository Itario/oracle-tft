#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LES COMPOS, CROISÉES AVEC CE QU'IL JOUE -> data/compos_lui.json
================================================================
Lit  : data/compos.json (le relevé) + data/miroir.json (ses parties)
Écrit: data/compos_lui.json  -> onglet « Avant »

Le relevé classe les compos du ladder par LP rapporté. Ce fichier répond à la
question suivante, qui est la sienne : **lesquelles sont à MA portée ?**

Une compo dont il joue déjà les porteurs ne demande aucun apprentissage : il
sait la piloter, il lui manque au plus de savoir qu'elle est forte. Une compo
sur des unités qu'il ne sort jamais est un pari — peut-être bon, mais à
chiffrer comme un pari.

─── CE QUE CE FICHIER NE DIT PAS ──────────────────────────────────────────
**« À ta portée » n'est pas « meilleure pour toi ».** Le recouvrement mesure
une FAMILIARITÉ, pas une aptitude : il dit qu'il a déjà sorti ces unités,
pas qu'il les joue bien. Son placement sur ces unités est affiché à côté pour
qu'on puisse en juger — et ce placement, lui, ne sort pas du bruit à 114
parties (data/focus.json dit la même chose de ses douze lignes).

**Le lpDelta du relevé est mesuré sur le ladder, pas sur lui.** Il décrit ce
que la compo rapporte à un joueur Master+ moyen. Le sien dépendrait de son
exécution, qu'on ne sait pas isoler.
"""

import json, os, re, sys
from datetime import date

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import mesures as M

RACINE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SORTIE = os.path.join(RACINE, "data", "compos_lui.json")
SCHEMA = 1


# champion() vit dans tools/lib/mesures.py — UNE seule définition de
# « est-ce la même unité ? ». Quatre copies existaient le 05/11.
champion = M.champion


def charger(nom):
    try:
        return json.load(open(os.path.join(RACINE, "data", nom), encoding="utf-8"))
    except Exception:
        return None


def main():
    co = charger("compos.json")
    mi = charger("miroir.json")
    if not co:
        sys.exit("data/compos.json absent — lance tools/releve/compos.py.")
    if not mi:
        sys.exit("data/miroir.json absent — lance build_miroir.py.")

    # ⚠ Le relevé de compos porte son propre verdict de population. S'il dit
    # que les tranches divergent, on ne croise pas : on le dit et on s'arrête.
    # compos.json porte son propre set (retrouvé par le code de patch) : c'est
    # lui le côté « méta » de ce croisement, pas le dernier relevé d'unités.
    sets = M.garde_de_set(mi, co, SCHEMA, SORTIE, "le croisement des compos")
    if sets is None:
        return

    pop = co.get("population") or {}
    if pop.get("meme_population") is False:
        # Refus motivé, ÉCRIT : sortir en erreur laissait en place le fichier
        # de la veille, c'est-à-dire un croisement que plus rien ne garantit.
        M.ecrire(SORTIE, {
            "schema_version": SCHEMA, "genere_le": date.today().isoformat(),
            "set": sets["meta"], "sets": sets, "etat": "populations_differentes",
            "message": pop.get("note"), "compos": []})
        print(f"écrit : {SORTIE}\n  croisement refusé : {pop.get('note')}")
        return

    # ⚠ DÉFINITION PARTAGÉE avec build_focus.py, via le socle.
    #
    # Ce fichier ne comptait d'abord que miroir.carries (n >= 12). Le Focus,
    # lui, compte aussi les porteurs des 50 dernières parties. Résultat : le
    # Focus affichait « tu la joues » pour murkwolf pendant que ce bloc le
    # déclarait inconnu, sur la MÊME page. Aucun des deux ne se trompait ;
    # ils employaient deux définitions sous un seul mot.
    #
    # On prend la définition commune, et on RESTITUE la nuance : sortir une
    # unité une fois en cinquante parties n'est pas la jouer, mais ce n'est
    # pas non plus ne jamais l'avoir touchée.
    jouees = M.unites_jouees(mi)
    siens = {}
    for c in (mi.get("carries") or []):
        ch = champion(c["nom"])
        if ch:
            siens[ch] = c

    sortie = []
    for comp in (co.get("compos") or []):
        # ⚠ `unites` est une liste de LISTES ([identifiant, étoiles, parties,
        # placement]) depuis le 04/11. Passée telle quelle à champion(), une
        # liste devient sa propre représentation en texte — et « combien
        # d'unités connaît-il » comptait n'importe quoi, sans erreur.
        unites = sorted({u[0] if isinstance(u, list) else u
                         for u in (comp.get("unites") or [])})
        porteurs = [p["unite"] for p in (comp.get("porteurs") or [])]

        # Deux recouvrements, et ils ne disent pas la même chose.
        # Le plateau entier mesure la familiarité générale ; les PORTEURS
        # mesurent s'il sait piloter le cœur de la compo. C'est le second
        # qui compte : on peut connaître sept unités sur huit et ne jamais
        # avoir joué celle qui porte les objets.
        conn_plateau = [u for u in unites if champion(u) in jouees]
        # Les porteurs, en TROIS états plutôt que deux.
        reguliers = [u for u in porteurs if jouees.get(champion(u)) == "regulier"]
        occasionnels = [u for u in porteurs
                        if jouees.get(champion(u)) == "occasionnel"]
        jamais = [u for u in porteurs if champion(u) not in jouees]
        conn_porteurs = reguliers

        # Son placement moyen sur les porteurs qu'il connaît, pondéré par le
        # nombre de fois qu'il les a sortis.
        poids = [(siens[champion(u)]["placement"], siens[champion(u)]["n"])
                 for u in conn_porteurs]
        sa_place = (round(sum(p * n for p, n in poids) / sum(n for _, n in poids), 2)
                    if poids else None)

        sortie.append({
            "unites_distinctes": unites,
            **{k: comp[k] for k in ("code", "n", "place", "top4_pct",
                                    "premieres_pct", "lp_par_partie",
                                    "unites", "traits", "porteurs",
                                    "conditions_de_victoire", "niveaux",
                                    "variantes", "objets_par_unite")
               if k in comp},
            "porteurs_reguliers": reguliers,
            "porteurs_occasionnels": occasionnels,
            "porteurs_jamais_joues": jamais,
            # La jauge compte un occasionnel pour une demie : il a touché
            # l'unité, il ne la pilote pas.
            "part_porteurs_connus": (
                round((len(reguliers) + 0.5 * len(occasionnels)) / len(porteurs), 2)
                if porteurs else None),
            "unites_connues": len(conn_plateau),
            "unites_total": len(unites),
            "son_placement_sur_les_porteurs": sa_place,
            "parties_sur_les_porteurs": sum(n for _, n in poids),
        })

    # Les compos qu'il sait déjà piloter d'abord, et à familiarité égale,
    # celles qui rapportent le plus.
    sortie.sort(key=lambda c: (-(c["part_porteurs_connus"] or 0),
                               -(c["lp_par_partie"] or -99)))

    out = {
        "schema_version": SCHEMA,
        "genere_le": date.today().isoformat(),
        "set": sets["meta"], "sets": sets,
        "etat": "ok" if sortie else "vide",
        "message": None if sortie else co.get("etat_note"),
        "patch": co.get("patch") or co.get("patch_code"),
        "n_parties_ladder": co.get("n_parties"),
        "population": pop,
        # Le compteur d'augments voyage avec ce fichier plutôt que d'obliger
        # le site à charger compos.json en entier pour un seul entier.
        "augments": co.get("augments"),
        "compos": sortie,
        "limite": co.get("limite"),
        "reserves": {
            "familiarite_pas_aptitude": (
                "Le recouvrement dit qu'il a déjà sorti ces unités, pas qu'il "
                "les joue bien. Son placement dessus est affiché à côté — et "
                "aucune de ses douze lignes ne sort du bruit à 114 parties."),
            "lp_mesure_sur_le_ladder": (
                "`lp_par_partie` décrit ce que la compo rapporte à un joueur "
                "Master+ moyen, pas à lui. Le sien dépendrait de son "
                "exécution, qu'on ne sait pas isoler."),
        },
    }

    os.makedirs(os.path.dirname(SORTIE), exist_ok=True)
    json.dump(out, open(SORTIE, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    print(f"écrit : {SORTIE}")
    print(f"  {len(sortie)} compos croisées · patch {out['patch']}")
    for c in sortie:
        p = c["part_porteurs_connus"]
        print(f"    {int(100*(p or 0)):>3} % des porteurs connus · "
              f"{c['lp_par_partie']:+.2f} LP/partie · "
              + ", ".join(M.nom_affichable(u)
                          for u in c["porteurs_reguliers"][:3] or ["aucun"])
            + (f" (+{len(c['porteurs_occasionnels'])} occasionnels)"
               if c["porteurs_occasionnels"] else ""))


if __name__ == "__main__":
    main()
