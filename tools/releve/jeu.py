#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LE JEU — les unités, leurs coûts, leurs traits, et leurs noms -> data/jeu.json
===============================================================================
Les relevés disent ce que le ladder joue. Ils ne disent pas ce que le jeu
CONTIENT : combien coûte une unité, quels traits elle porte, à combien
d'unités un trait s'active, comment tout cela s'appelle en français.

Jusqu'au 10/11 le projet tenait ces faits dans `data_set18_fige.js`, un
fichier écrit à la main à partir des notes du PBE de juillet. Il faudrait le
réécrire à chaque set, à la main, dans la semaine où l'on a le moins de temps.

Riot publie tout cela dans ses propres fichiers de données, que
CommunityDragon expose. Ce script les lit — c'est un RELEVÉ, pas une
transcription.

    python3 tools/releve/jeu.py [--forcer]

─── DEUX CANAUX, ET C'EST TOUT L'INTÉRÊT ──────────────────────────────────
    latest   ce qui est en ligne         -> le bloc principal du fichier
    pbe      ce qui arrive               -> le bloc `a_venir`

Deux semaines avant un changement de set, le canal `pbe` porte déjà le set
suivant en entier. Ce script le voit apparaître tout seul : le jour où le
fichier du PBE contient un set de numéro supérieur au set en ligne, `a_venir`
se remplit — les unités par coût, les traits et leurs paliers. C'est ce qu'on
étudie avant un lancement, et on l'a le jour où Riot le publie, sans rien
saisir.

─── CE QUE CE FICHIER NE DIT PAS ──────────────────────────────────────────
Aucune force, aucun classement. Un coût et un trait sont des faits ; « cette
unité est forte » est une mesure, et elle n'existe pas avant que le ladder
joue. Tout ce qui s'écrit sur le PBE (taux de victoire, listes de niveaux)
est mesuré sur un jeu qui change tous les jours, par une population qui
n'est pas celle du classé : ce script n'y touche pas.

─── CADENCE ───────────────────────────────────────────────────────────────
Quatre fichiers de plusieurs mégaoctets. Relu une fois par jour, ou quand
le patch change : le PBE bouge tous les jours pendant ses deux semaines, le
reste du temps rien ne bouge.

⚠ Ne tourne pas depuis une session Claude (proxy). Fait pour le runner.
"""

import json, os, sys
from datetime import date

RACINE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(RACINE, "tools", "lib"))
from reseau import lire as _lire
import mesures as M

SORTIE = os.path.join(RACINE, "data", "jeu.json")
SCHEMA = 1
URL = "https://raw.communitydragon.org/{canal}/cdragon/tft/{langue}.json"


def lire(canal, langue):
    return _lire(URL.format(canal=canal, langue=langue), quoi="données du jeu",
                 json_attendu=True, delai=90)


def tenter(canal, langue):
    """Une lecture qui a le droit d'échouer : le français et le PBE sont des
    compléments. Sans eux le fichier s'écrit quand même, et le dit."""
    try:
        return lire(canal, langue)
    except SystemExit as e:
        print(f"  ({canal}/{langue} illisible : {str(e).splitlines()[0]})")
        return None


def bloc_set(fichier, numero):
    """Le set `numero` dans un fichier CommunityDragon, ou None.

    La forme attendue : {"sets": {"18": {"champions": [...], "traits": [...]}}}.
    Elle n'est documentée nulle part ; si elle change, on renvoie None et
    l'appelant écrit ce qu'il a vu plutôt que de deviner."""
    sets = (fichier or {}).get("sets")
    if not isinstance(sets, dict):
        return None
    b = sets.get(str(numero))
    if not isinstance(b, dict) or not isinstance(b.get("champions"), list):
        return None
    return b


def numeros(fichier):
    sets = (fichier or {}).get("sets")
    if not isinstance(sets, dict):
        return []
    return sorted(int(k) for k in sets if str(k).isdigit())


def decrire(b_en, b_fr):
    """Un bloc de set -> unités et traits, avec leurs noms français quand le
    fichier français les donne."""
    fr_unites = {c.get("apiName"): c.get("name") for c in ((b_fr or {}).get("champions") or [])}
    fr_traits = {t.get("apiName"): t.get("name") for t in ((b_fr or {}).get("traits") or [])}

    traits, par_nom = {}, {}
    for t in (b_en.get("traits") or []):
        ident = t.get("apiName")
        if not ident:
            continue
        paliers = sorted({e.get("minUnits") for e in (t.get("effects") or [])
                          if isinstance(e.get("minUnits"), int)})
        traits[ident] = {"nom": fr_traits.get(ident) or t.get("name") or ident,
                         "nom_en": t.get("name"), "paliers": paliers}
        if t.get("name"):
            par_nom[t["name"]] = ident       # les unités citent leurs traits par NOM

    unites, autres = {}, []
    for c in (b_en.get("champions") or []):
        ident, cout = c.get("apiName"), c.get("cost")
        if not ident:
            continue
        # Le fichier mélange les unités jouables et tout ce qui peut se
        # trouver sur un plateau (mannequins, invocations, monstres de
        # tour). Une unité de boutique coûte de 1 à 5 et porte des traits.
        if not (isinstance(cout, int) and 1 <= cout <= 5 and c.get("traits")):
            autres.append(ident)
            continue
        unites[ident] = {"nom": fr_unites.get(ident) or c.get("name") or ident,
                         "nom_en": c.get("name"), "cout": cout,
                         "traits": [par_nom.get(n, n) for n in c.get("traits")]}
    return unites, traits, autres


def main():
    forcer = "--forcer" in sys.argv
    rel = M.releve_courant()
    if not rel:
        sys.exit(f"Aucun relevé dans {M.RELEVES_TT} — lance tactics.py d'abord.")
    setn = rel.get("set")

    if not forcer and os.path.exists(SORTIE):
        try:
            a = json.load(open(SORTIE, encoding="utf-8"))
            if (a.get("set") == setn and a.get("patch") == rel.get("patch")
                    and a.get("genere_le") == date.today().isoformat()):
                print(f"jeu.json déjà relevé aujourd'hui pour {rel.get('patch')} "
                      "— rien à faire (--forcer pour refaire).")
                return
        except Exception:
            pass

    en = lire("latest", "en_us")
    b_en = bloc_set(en, setn)
    if b_en is None:
        # Le relevé d'unités est passé à un set que le canal `latest` de
        # CommunityDragon ne porte pas encore (il suit le patch avec quelques
        # heures de retard), ou la forme du fichier a changé. On n'écrit pas
        # le set d'avant sous le numéro du nouveau : on sort, et le fichier
        # précédent — qui porte son propre `set` — reste étiqueté pour ce
        # qu'il est.
        sys.exit(f"Le set {setn} est absent du canal latest "
                 f"(sets présents : {numeros(en)[-4:]}). Fichier non réécrit.")
    fr = tenter("latest", "fr_fr")
    unites, traits, autres = decrire(b_en, bloc_set(fr, setn))

    # Les noms français des objets VUS dans le relevé — même calage que
    # recettes.py : ce que le ladder porte, pas un préfixe de set.
    fr_objets = {i.get("apiName"): i.get("name") for i in ((fr or {}).get("items") or [])}
    en_objets = {i.get("apiName"): i.get("name") for i in (en.get("items") or [])}
    vus = set(rel.get("objets") or {})
    try:
        rec = json.load(open(os.path.join(RACINE, "data", "recettes.json"), encoding="utf-8"))
        vus |= set(rec.get("composants") or {})
    except Exception:
        pass
    objets = {o: (fr_objets.get(o) or en_objets.get(o))
              for o in sorted(vus) if (fr_objets.get(o) or en_objets.get(o))}

    # ── Ce qui arrive : le canal du PBE ──────────────────────────────────
    a_venir, a_venir_note = None, None
    pbe = tenter("pbe", "en_us")
    if pbe is None:
        a_venir_note = "Canal PBE illisible à ce relevé."
    else:
        suivants = [n for n in numeros(pbe) if isinstance(setn, int) and n > setn]
        if not suivants:
            a_venir_note = (f"Le PBE ne porte aucun set au-delà du Set {setn} : "
                            "le suivant n'y est pas encore.")
        else:
            n_suiv = suivants[0]
            b_pbe = bloc_set(pbe, n_suiv)
            if b_pbe is None:
                a_venir_note = f"Le Set {n_suiv} apparaît au PBE sous une forme illisible."
            else:
                pbe_fr = tenter("pbe", "fr_fr")
                u2, t2, _ = decrire(b_pbe, bloc_set(pbe_fr, n_suiv))
                ancien = {}
                try:
                    ancien = (json.load(open(SORTIE, encoding="utf-8")).get("a_venir") or {})
                except Exception:
                    pass
                a_venir = {
                    "set": n_suiv,
                    "nom": b_pbe.get("name"),
                    "canal": "pbe",
                    "vu_la_premiere_fois": (ancien.get("vu_la_premiere_fois")
                                            if ancien.get("set") == n_suiv
                                            else date.today().isoformat()),
                    "releve_le": date.today().isoformat(),
                    "unites": u2, "traits": t2,
                    "note": ("Relevé sur le PBE : le jeu y change tous les jours "
                             "jusqu'à la sortie. Les coûts et les traits sont "
                             "des faits du moment ; aucune force ne s'en déduit."),
                }

    out = {
        "schema_version": SCHEMA,
        "genere_le": date.today().isoformat(),
        "nature": "releve",
        "source": "CommunityDragon (données Riot)",
        "set": setn,
        "patch": rel.get("patch"),
        "francais": fr is not None,
        "unites": unites,
        "traits": traits,
        "objets": objets,
        "hors_boutique": sorted(autres),
        "a_venir": a_venir,
        "a_venir_note": a_venir_note,
        "note": ("Coûts, traits, paliers et noms, lus dans les données de Riot. "
                 "Aucune force, aucun classement : ce fichier dit ce que le jeu "
                 "contient, pas ce qui gagne."),
    }
    M.ecrire(SORTIE, out)

    par_cout = {}
    for u in unites.values():
        par_cout[u["cout"]] = par_cout.get(u["cout"], 0) + 1
    print(f"écrit : {SORTIE}")
    print(f"  Set {setn} · {len(unites)} unités ("
          + " · ".join(f"{n} à {c}" for c, n in sorted(par_cout.items()))
          + f") · {len(traits)} traits · {len(objets)} objets nommés"
          + ("" if fr is not None else " · ⚠ sans le français"))
    # Combien des unités du relevé retrouve-t-on ? C'est le seul contrôle
    # qui dise si les deux sources parlent bien du même jeu.
    ids = list(rel.get("unites") or {})
    connus = {M.champion(k) for k in unites}
    trouves = sum(1 for i in ids if i in unites or M.champion(i) in connus)
    print(f"  {trouves} des {len(ids)} unités du relevé y figurent")
    if a_venir:
        print(f"  ⚠ LE SET {a_venir['set']} EST AU PBE : {len(a_venir['unites'])} unités, "
              f"{len(a_venir['traits'])} traits (vu la première fois le "
              f"{a_venir['vu_la_premiere_fois']})")
    else:
        print(f"  à venir : {a_venir_note}")


if __name__ == "__main__":
    main()
