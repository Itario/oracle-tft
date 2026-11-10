#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LES FUITES — ce qui coûte des LP sans aucun défaut de jeu -> data/fuites.json
=============================================================================
Lit  : data/miroir.json (ses parties) + data/joueur.json (le barème et la barre)
Écrit: data/fuites.json  -> onglet « Suivi »

POURQUOI CE FICHIER EXISTE. Tous les autres cherchent une faiblesse technique.
Au 05/11, ils ont tous répondu non :

    rang de niveau final dans le lobby  3.91 / 8   (2.8 écarts-types sous 4.50)
    conversion rang_niveau - placement  +0.40      (il place mieux que son niveau)
    or restant médian                   2          (il dépense, il ne thésaurise pas)
    traits hors du bruit                2 sur 24
    carries hors du bruit               0 sur 12

**Il n'y a pas de fuite technique dans les agrégats.** Chercher plus loin dans
cette direction, c'est produire du conseil tiré du hasard. Reste ce que la
donnée montre sans ambiguïté : des LP perdus pour des raisons qui n'ont rien
à voir avec la qualité du jeu.

─── LA SEULE RÈGLE DE DÉCISION QUE CE PROJET AIT PRODUITE ──────────────────
**Ne pas lancer une partie coûte 0 LP. En lancer une et l'abandonner en coûte
une cinquantaine.** Ce n'est pas un conseil de discipline, c'est une
asymétrie arithmétique : à Master, une 8e place vaut environ -52 LP là où une
partie non jouée vaut exactement zéro.

─── CE QUE CE FICHIER NE DIT PAS ──────────────────────────────────────────
1. **Le coût des abandons est PROSPECTIF, pas rétroactif.** Les six parties
   lâchées datent de septembre et octobre, quand il était entre Silver et
   Diamant : l'échelle de LP n'y était pas la même, et appliquer le barème
   Master à ces parties-là serait faux. Ce fichier chiffre donc ce que le
   MÊME comportement coûterait MAINTENANT, à son rang actuel. C'est une
   projection de taux, pas une addition de pertes passées.

2. **Les jours sans jouer ne « coûtent » rien en soi.** Le chiffre donné est
   un taux de change — combien de LP une journée de jeu rapporte en moyenne —
   pour qu'il décide lui-même. Un travail et des enfants ne se négocient pas
   contre des LP, et ce fichier ne prétend pas le contraire.

3. **La décroissance n'est PAS comptée tant qu'elle n'est pas observée.**
   `rankHistory` la montrerait. Au 05/11 elle n'a jamais frappé : son LP
   n'a bougé que sur des parties jouées. Proclamer une perte qu'on n'a pas
   constatée serait exactement l'erreur que ce projet s'interdit.
"""

import json, math, os, sys
from datetime import date

RACINE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(RACINE, "tools", "lib"))
import mesures as M
SORTIE = os.path.join(RACINE, "data", "fuites.json")
SCHEMA = 1


def charger(nom):
    try:
        return json.load(open(os.path.join(RACINE, "data", nom), encoding="utf-8"))
    except Exception:
        return None


def main():
    mi = charger("miroir.json")
    jo = charger("joueur.json")
    if not mi:
        sys.exit("data/miroir.json absent — lance build_miroir.py.")
    # ── CE FICHIER CROISE SES PARTIES (miroir) ET SON BARÈME (joueur) ────
    # Les deux doivent être du même set : six abandons du Set 18 chiffrés au
    # barème d'un joueur reclassé au Set 19 ne sont le coût de rien. Et
    # quand le croisement n'est pas possible, on ÉCRIT pourquoi : sortir en
    # erreur laissait le fichier de la veille en place, étape tolérée oblige.
    sets = {"parties": mi.get("set"), "bareme": (jo or {}).get("set")}
    def etat(nom, message):
        M.ecrire(SORTIE, {"schema_version": SCHEMA,
                          "genere_le": date.today().isoformat(),
                          "set": mi.get("set"), "sets": sets,
                          "etat": nom, "message": message})
        print(f"écrit : {SORTIE}\n  {nom} : {message}")
    if not jo:
        return etat("pas_de_position", "Aucune position relevée : le coût "
                    "d'un abandon ne se chiffre pas sans barème.")
    if sets["parties"] != sets["bareme"]:
        return etat("sets_differents",
                    f"Tes parties récoltées sont du Set {sets['parties']} et "
                    f"ta position relevée du Set {sets['bareme']} : le coût "
                    "des abandons ne se calcule pas entre deux sets. Il "
                    "reviendra à ta première récolte du set en cours "
                    "(LANCER.bat).")
    if not (jo.get("bareme_lp") or {}).get("droite"):
        return etat("pas_de_bareme",
                    "Pas encore assez de parties classées ce set pour ajuster "
                    "ton barème de LP (il en faut six). Le chiffrage des "
                    "abandons reviendra de lui-même.")

    dr = jo["bareme_lp"]["droite"]
    a, b = dr["ordonnee"], dr["pente_lp_par_place"]
    lp_de = lambda place: a + b * place          # la droite ajustée sur SES parties
    attendu = (jo.get("projection") or {}).get("lp_par_partie_attendu")
    manquants = (jo.get("ecart_a_la_barre") or {}).get("lp_manquants")

    # ── 1. LES PARTIES LÂCHÉES ───────────────────────────────────────────
    lach = mi.get("lachees") or []
    n_tot = mi.get("n_parties") or 0
    detail = []
    for x in lach:
        pl = int(x["placement"])
        perte = lp_de(pl)
        detail.append({
            "date": x["date"], "placement": pl,
            "niveau": x.get("niveau"), "or_restant": x.get("or_restant"),
            "lp_a_ce_placement": round(perte, 1),
            # Le vrai coût n'est pas la perte : c'est l'ÉCART à une partie
            # ordinaire. Abandonner, ce n'est pas perdre 52 LP, c'est renoncer
            # aux 13 qu'on aurait pris en moyenne EN PLUS de perdre les 52.
            "manque_a_gagner": round(attendu - perte, 1) if attendu is not None else None,
        })

    cout_unitaire = (round(attendu - lp_de(8), 1) if attendu is not None else None)
    total_si_maintenant = (round(sum(d["manque_a_gagner"] for d in detail), 1)
                           if attendu is not None else None)

    abandons = {
        "n": len(lach),
        "n_parties_total": n_tot + len(lach),
        "part_des_parties_pct": (round(100 * len(lach) / (n_tot + len(lach)), 1)
                                 if n_tot else None),
        "zone_grise_signalee": mi.get("zone_grise"),
        "detail": detail,
        "cout_d_un_abandon_maintenant": cout_unitaire,
        "cout_total_au_rang_actuel": total_si_maintenant,
        "part_de_l_ecart_a_la_barre_pct": (
            round(100 * total_si_maintenant / manquants, 1)
            if (total_si_maintenant and manquants) else None),
        "asymetrie": (
            f"Ne pas lancer une partie coûte 0 LP. En lancer une et "
            f"l'abandonner en coûte {abs(round(lp_de(8))):.0f} — et fait en plus "
            f"renoncer aux {attendu:.0f} qu'une partie ordinaire rapporte. "
            f"L'écart est de {abs(cout_unitaire):.0f} LP par partie abandonnée."
            if (attendu is not None and cout_unitaire is not None) else None),
        # Cette réserve portait, écrits en dur, « six abandons de septembre-
        # octobre, entre Silver et Diamant » : vrai le 05/11, faux dès la
        # récolte suivante. Un constructeur ne cite que ce qu'il a compté.
        "reserve": ((f"Ces {len(lach)} abandons vont du "
                     f"{min(x['date'] for x in lach)} au "
                     f"{max(x['date'] for x in lach)}. Ils n'ont pas tous été "
                     "joués au rang actuel, où l'échelle de LP n'est pas la "
                     "même : ce chiffre n'additionne PAS des pertes passées, "
                     "il projette ce que le même comportement coûte à son "
                     "rang ACTUEL.") if lach else
                    "Aucune partie lâchée dans la fenêtre récoltée."),
    }

    # ── 2. LE RYTHME, COMME TAUX DE CHANGE ───────────────────────────────
    ry = mi.get("rythme") or {}
    par_jour_actif = ry.get("parties_par_jour_actif")
    rythme = {
        **ry,
        "lp_par_jour_actif": (round(par_jour_actif * attendu, 1)
                              if (par_jour_actif and attendu is not None) else None),
        "jours_actifs_requis": (math.ceil(manquants / (par_jour_actif * attendu))
                                if (manquants and manquants > 0 and par_jour_actif
                                    and attendu and attendu > 0) else None),
        "lecture": ("Un taux de change, pas un reproche : voilà ce qu'une "
                    "journée de jeu rapporte en moyenne, pour qu'il décide "
                    "lui-même. Un travail et des enfants ne se négocient pas "
                    "contre des LP."),
    }

    # ── 3. LA DÉCROISSANCE : CONSTATÉE OU RIEN ───────────────────────────
    # On ne la déduit pas d'un nombre de jours : on la lit dans la position.
    decroissance = {
        "observee": False,
        "note": ("Aucune perte de LP sans partie n'a été observée à ce jour : "
                 "son LP n'a bougé que sur des parties jouées. La décroissance "
                 "à Master existe (-50 LP/jour une fois les parties en banque "
                 "épuisées) mais elle ne l'a jamais touché. On ne compte pas "
                 "une perte qu'on n'a pas constatée."),
    }

    out = {
        "schema_version": SCHEMA,
        "genere_le": date.today().isoformat(),
        "set": mi.get("set"), "sets": sets, "etat": "ok",
        "n_parties": n_tot,
        "lp_manquants": manquants,
        "lp_par_partie_attendu": attendu,
        "bareme": {"pente": b, "ordonnee": a,
                   "lp_8e_place": round(lp_de(8), 1),
                   "note": "La 8e place est EXTRAPOLÉE par la droite : aucune "
                           "8e propre dans la fenêtre de 50 parties (les seules "
                           "présentes finissaient à 0 LP, donc écrêtées)."},
        "abandons": abandons,
        "rythme": rythme,
        "decroissance": decroissance,
        # Même correction : les chiffres cités ici étaient écrits en dur.
        "pourquoi": (
            "Les autres fichiers cherchent une faiblesse technique dans les "
            f"agrégats : rang de niveau {mi.get('rang_niveau_moyen')}/8, or "
            f"restant médian {mi.get('or_restant_median')}, "
            f"{sum(1 for t in (mi.get('traits') or []) if t.get('solide'))} "
            f"trait(s) sur {len(mi.get('traits') or [])} hors du bruit, "
            f"{sum(1 for c in (mi.get('carries') or []) if c.get('solide'))} "
            f"carry sur {len(mi.get('carries') or [])}. Celui-ci chiffre ce "
            "qui ne relève pas de la qualité du jeu : des LP perdus par "
            "abandon, et ce que rapporte une journée jouée."),
    }

    os.makedirs(os.path.dirname(SORTIE), exist_ok=True)
    json.dump(out, open(SORTIE, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    print(f"écrit : {SORTIE}")
    print(f"  barème : 8e place = {out['bareme']['lp_8e_place']} LP · "
          f"partie ordinaire = {attendu if attendu is None else format(attendu, '+')} LP")
    print(f"  {abandons['n']} parties lâchées "
          f"({abandons['part_des_parties_pct']} % de ses parties)")
    print(f"  coût d'un abandon au rang actuel : "
          f"{abandons['cout_d_un_abandon_maintenant']} LP")
    print(f"  les {abandons['n']} au rang actuel : "
          f"{abandons['cout_total_au_rang_actuel']} LP, soit "
          f"{abandons['part_de_l_ecart_a_la_barre_pct']} % de l'écart à la barre")
    if rythme.get("jours_actifs_requis"):
        print(f"  rythme : {rythme['lp_par_jour_actif']:+} LP par jour joué -> "
              f"{rythme['jours_actifs_requis']} jours de jeu pour la barre")


if __name__ == "__main__":
    main()
