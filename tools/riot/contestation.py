#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LA CONTESTATION — ce que les SEPT AUTRES jouaient -> contestation_resume.json
==============================================================================
    python contestation.py                      # set de la partie la plus récente
    python contestation.py --set 18 --sortie contestation_resume.json

TOURNE SUR SA MACHINE, à côté de miroir.py, parce que c'est là que vivent les
fichiers de parties — et ils n'en bougent jamais (§ ci-dessous).

─── POURQUOI CE FICHIER EXISTE ────────────────────────────────────────────
`collecte.py` enregistre l'objet de partie ENTIER : les huit joueurs, avec
leurs unités, leurs objets et leurs traits. `miroir.py` ne s'en sert que pour
le classer dans le lobby.

**Environ 1 600 plateaux finaux dorment sur le disque, et on n'en lit que son
rang.** Or la contestation — combien d'autres joueurs construisaient la même
unité que lui — est l'axe le plus discriminant entre Master et Challenger, et
personne ne peut la publier : elle demande SES lobbies.

La charte affirme depuis le début « à placement égal, la ligne la moins
contestée gagne ». C'est une croyance tirée des statistiques globales.
**Ce fichier permet enfin de la tester sur ses propres parties.**

─── CE QUI NE SORT PAS D'ICI ──────────────────────────────────────────────
⚠ Les fichiers de parties portent le **puuid des sept adversaires** de chaque
lobby. C'est de la donnée personnelle de tiers. La sortie de ce script ne
contient **aucun identifiant, aucun pseudo, aucun compte par joueur** : rien
que des agrégats par champion et ses propres placements. Un test du socle
vérifie qu'aucun puuid n'atteint jamais `data/`.

─── CE QUE CE FICHIER NE DIT PAS ──────────────────────────────────────────
**LE BIAIS EST CONNU ET IL VA TOUJOURS DANS LE MÊME SENS.** Le joueur qui
PERD une contestation meurt tôt, avec un plateau maigre et sans objets sur
l'unité disputée : il n'apparaîtra donc pas comme contestant. **On sous-compte
la contestation**, et on la sous-compte surtout dans les parties où elle a été
la plus violente. Un écart mesuré ici est donc un PLANCHER.

C'est pour la même raison que deux définitions sont calculées, jamais une :

    contestation_porteurs  un autre joueur finit avec l'unité ET >= 2 objets
                           -> il la construisait vraiment. Sous-compte le perdant.
    contestation_presence  un autre joueur finit avec l'unité, objets ou non
                           -> inclut celui qui la tenait en remplissage. Surcompte.

La vérité est entre les deux. Les afficher toutes les deux est le seul moyen
honnête de le montrer.
"""

import argparse, json, os, statistics as st, sys
from collections import Counter, defaultdict

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
try:
    import miroir as MI           # charger(), trouver_moi(), carries(), numero_set()
except Exception as e:
    sys.exit(f"Impossible d'importer miroir.py depuis {ICI}\n  {e}\n"
             "  Ce script doit vivre à côté de miroir.py, dans tools/riot/.")

RACINE = os.path.dirname(os.path.dirname(ICI))
sys.path.insert(0, os.path.join(RACINE, "tools", "lib"))
try:
    from mesures import champion
except Exception:
    sys.exit("Impossible d'importer tools/lib/mesures.py.\n"
             "  champion() n'a qu'UNE définition dans ce projet, et elle est "
             "là-bas. Si tools/lib n'est pas sur cette machine, copie le "
             "dossier entier plutôt que de recopier la fonction.")

NMIN = 8          # sous 8 parties sur un champion, on n'affiche pas de split


def principal(p):
    """Son carry PRINCIPAL : le plus objetisé, départagé par les étoiles.

    On ne mesure pas la contestation sur tous ses carries à la fois : une
    partie où il tient trois unités à deux objets n'est pas trois fois plus
    contestée. C'est la pièce qui décide qui compte."""
    cs = MI.carries(p)
    if not cs:
        return None
    return max(cs, key=lambda c: (len(c[2]), c[1]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", default="auto")
    ap.add_argument("--depuis")
    ap.add_argument("--sortie", default="contestation_resume.json")
    ap.add_argument("--nom", help="son Riot ID, s'il n'est pas déductible")
    # Paramétrable pour que le script soit TESTABLE sur un jeu d'essai : sans
    # ça, il ne peut tourner que là où les vraies parties se trouvent, et on
    # ne vérifie jamais qu'il mesure ce qu'il prétend mesurer.
    ap.add_argument("--dossier", help="où sont les fichiers de parties")
    a = ap.parse_args()

    if a.dossier:
        MI.DOSSIER = a.dossier
    jeu_set = None if a.set == "auto" else int(a.set)
    parties = MI.charger(a.depuis, jeu_set)
    if not parties:
        sys.exit(f"Aucune partie dans {MI.DOSSIER}. Lance collecte.py d'abord.")
    if a.set == "auto":
        # Même règle que miroir.py : le set de la partie la plus récente, pour
        # survivre au passage au Set 19 sans qu'on touche à quoi que ce soit.
        recent = max(parties, key=lambda i: i.get("game_datetime") or 0)
        jeu_set = recent.get("_set")
        parties = [i for i in parties if i.get("_set") == jeu_set]
        print(f"set retenu : {jeu_set} ({len(parties)} parties)")

    moi = MI.trouver_moi(parties, a.nom)

    lignes, sans_carry = [], 0
    for info in parties:
        parts = info.get("participants") or []
        p = next((x for x in parts if x.get("puuid") == moi), None)
        if not p:
            continue
        mien = principal(p)
        if not mien:
            sans_carry += 1
            continue
        ch = champion(mien[0])

        # Les sept autres. On ne retient AUCUN identifiant : on compte.
        n_porteurs = n_presence = 0
        for q in parts:
            if q.get("puuid") == moi:
                continue
            noms = {champion(u.get("character_id") or u.get("name") or "")
                    for u in (q.get("units") or [])}
            if ch in noms:
                n_presence += 1
            if any(champion(u.get("character_id") or u.get("name") or "") == ch
                   and len(u.get("itemNames") or []) >= 2
                   for u in (q.get("units") or [])):
                n_porteurs += 1

        lignes.append({
            "champion": ch,
            "placement": p.get("placement"),
            "porteurs": n_porteurs,       # autres joueurs qui la CONSTRUISAIENT
            "presence": n_presence,       # autres joueurs qui l'avaient, point
            "etoiles": mien[1],
            "n_objets": len(mien[2]),
        })

    if not lignes:
        sys.exit("Aucune partie avec un carry identifiable.")

    def split(sous_ensemble):
        """Placement moyen selon qu'il était seul ou contesté, avec le seuil.

        Le seuil de bruit n'est pas décoratif : à 114 parties découpées en
        deux, chaque moitié est petite, et un écart de 0.3 place ne veut rien
        dire. On ne publie « solide » que si l'écart le franchit."""
        seul = [x["placement"] for x in sous_ensemble if x["porteurs"] == 0]
        cont = [x["placement"] for x in sous_ensemble if x["porteurs"] >= 1]
        if len(seul) < 3 or len(cont) < 3:
            return None
        tout = [x["placement"] for x in sous_ensemble]
        sd = st.stdev(tout) if len(tout) > 1 else 0.0
        err = sd * ((1 / len(seul) + 1 / len(cont)) ** 0.5)
        ecart = st.mean(cont) - st.mean(seul)
        return {
            "n_seul": len(seul), "placement_seul": round(st.mean(seul), 2),
            "n_conteste": len(cont), "placement_conteste": round(st.mean(cont), 2),
            "ecart": round(ecart, 2),
            "seuil_bruit": round(2 * err, 2),
            "solide": abs(ecart) >= 2 * err,
            "parties_requises": (round((2 * sd / abs(ecart)) ** 2)
                                 if ecart else None),
        }

    par_champ = defaultdict(list)
    for x in lignes:
        par_champ[x["champion"]].append(x)

    champions = []
    for ch, v in sorted(par_champ.items(), key=lambda kv: -len(kv[1])):
        if len(v) < NMIN:
            continue
        champions.append({
            "champion": ch, "n": len(v),
            "placement": round(st.mean([x["placement"] for x in v]), 2),
            "porteurs_moyen": round(st.mean([x["porteurs"] for x in v]), 2),
            "presence_moyenne": round(st.mean([x["presence"] for x in v]), 2),
            "part_contestee_pct": round(
                100 * sum(1 for x in v if x["porteurs"] >= 1) / len(v), 1),
            "split": split(v),
        })

    out = {
        "schema_version": 1,
        "set": jeu_set,
        "n_parties": len(lignes),
        "parties_sans_carry": sans_carry,
        "nmin_champion": NMIN,
        "definitions": {
            "porteurs": "un autre joueur finit avec cette unité ET au moins "
                        "deux objets dessus — il la construisait vraiment.",
            "presence": "un autre joueur finit avec cette unité, objets ou "
                        "non — inclut celui qui la tenait en remplissage.",
            "biais": "Le joueur qui PERD une contestation meurt tôt, sans "
                     "objets sur l'unité disputée : il n'apparaît pas comme "
                     "contestant. On sous-compte donc la contestation, et "
                     "surtout dans les parties où elle a été la plus violente. "
                     "Tout écart mesuré ici est un PLANCHER.",
        },
        # ⭐ LE TEST DE LA CROYANCE DE LA CHARTE, toutes parties confondues.
        "global": split(lignes),
        "par_champion": champions,
        "le_plus_conteste": sorted(
            ({"champion": c["champion"], "n": c["n"],
              "part_contestee_pct": c["part_contestee_pct"],
              "porteurs_moyen": c["porteurs_moyen"]} for c in champions),
            key=lambda d: -d["part_contestee_pct"])[:8],
        # ⚠ NE PAS ÉCRIRE LE MOT « p-u-u-i-d » DANS CETTE NOTE.
        # Le garde-fou des workflows et le test du socle cherchent cette
        # chaîne par simple sous-chaîne, dans N'IMPORTE QUEL fichier de
        # data/. Expliquer qu'on n'en met pas, en l'écrivant, suffit à
        # bloquer la publication. Constaté sur ce fichier même, au premier
        # essai — et c'est la preuve que le garde-fou fonctionne.
        "aucun_identifiant": ("Les fichiers de parties portent l'identifiant "
                              "Riot des sept adversaires. Rien de tout cela "
                              "ne sort d'ici : ce fichier ne contient que des "
                              "agrégats par champion et ses propres "
                              "placements."),
    }

    with open(a.sortie, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)

    print(f"écrit : {a.sortie}")
    print(f"  {len(lignes)} parties avec un carry identifiable"
          + (f" · {sans_carry} sans" if sans_carry else ""))
    g = out["global"]
    if g:
        print(f"\n  SEUL        placement {g['placement_seul']} sur {g['n_seul']} parties")
        print(f"  CONTESTÉ    placement {g['placement_conteste']} sur {g['n_conteste']} parties")
        print(f"  écart {g['ecart']:+} place · seuil de bruit ±{g['seuil_bruit']}"
              f" -> {'SOLIDE' if g['solide'] else 'dans le bruit'}")
        if not g["solide"] and g.get("parties_requises"):
            print(f"  (il faudrait ~{g['parties_requises']} parties pour trancher)")
    print("\n  les plus contestés dans SES lobbies :")
    for c in out["le_plus_conteste"][:5]:
        print(f"    {c['champion']:<14} contesté dans {c['part_contestee_pct']:>5} % "
              f"de ses {c['n']} parties · {c['porteurs_moyen']} porteur(s) en face")


if __name__ == "__main__":
    main()
