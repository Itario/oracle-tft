#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LES RECETTES — quels composants font quel objet -> data/recettes.json
======================================================================
Un objet fini ne se choisit pas : il se FABRIQUE, à partir de composants
ramassés sur les tours de monstres et aux carrousels. La décision réelle du
joueur n'est donc jamais « quel objet est le meilleur » — c'est :

    quel composant prendre au carrousel, sachant ce que je tiens déjà ?
    est-ce que je slamme maintenant pour le tempo, ou je garde pour le BiS ?

Un classement d'objets finis par taux de victoire ne répond à aucune de ces
deux questions. Il faut la table de recettes pour les poser.

Source : les données de Riot elles-mêmes, via CommunityDragon, qui expose le
champ `composition` de chaque objet. Pas un site tiers, pas ma mémoire.

    python3 tools/releve/recettes.py

⚠ Comme les autres relevés : ne tourne pas depuis une session Claude, le proxy
du conteneur refuse le domaine. Fait pour le runner GitHub.

─── POURQUOI IL SE CALE SUR LE RELEVÉ PLUTÔT QUE SUR UN PRÉFIXE ────────────
Le fichier de Riot contient 4 230 objets — tous les sets depuis le premier.
Filtrer sur le préfixe du set courant (« DA_ » au Set 18) marcherait
aujourd'hui et casserait le 1er décembre, exactement comme `"set": 18` en dur
l'aurait fait dans tactics.py.

Alors on ne filtre pas sur un préfixe : on part des objets que le DERNIER
RELEVÉ a effectivement vus en partie, et on cherche leur recette. La table se
cale donc toute seule sur le set en cours, sans qu'on touche à ce fichier.
"""

import glob, json, os, sys
import urllib.error, urllib.request
from datetime import date

RACINE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SORTIE = os.path.join(RACINE, "data", "recettes.json")
RELEVES = os.path.join(RACINE, "data", "releves-tt")
SCHEMA = 1
CDRAGON = "https://raw.communitydragon.org/latest/cdragon/tft/en_us.json"

EN_TETES = {
    "User-Agent": "OracleTFT/1.0 (table de recettes, usage personnel)",
    "Accept": "application/json",
}

# Les composants parlent français sur le site. La correspondance se fait sur
# le SUFFIXE de l'identifiant Riot, pas sur le nom anglais, qui peut changer.
FR = {
    "BFSword": "épée", "RecurveBow": "arc", "NeedlesslyLargeRod": "baguette",
    "TearOfTheGoddess": "larme", "ChainVest": "plastron",
    "NegatronCloak": "cape", "GiantsBelt": "ceinture",
    "SparringGloves": "gants", "Spatula": "spatule", "FryingPan": "poêle",
}


def lire(url):
    req = urllib.request.Request(url, headers=EN_TETES)
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return json.loads(r.read().decode("utf-8", "replace"))
    except urllib.error.HTTPError as e:
        sys.exit(f"HTTP {e.code} sur {url}")
    except Exception as e:
        sys.exit(f"Impossible de joindre {url}\n  {type(e).__name__}: {e}\n"
                 "  (Normal depuis une session Claude : le proxy du conteneur "
                 "bloque ce domaine. Ce script est fait pour le runner GitHub.)")


def dernier_releve():
    fs = sorted(glob.glob(os.path.join(RELEVES, "*.json")))
    if not fs:
        sys.exit(f"Aucun relevé dans {RELEVES} — lance tactics.py d'abord.")
    return json.load(open(fs[-1], encoding="utf-8")), os.path.basename(fs[-1])


def main():
    forcer = "--forcer" in sys.argv
    rel, nom = dernier_releve()

    # Le fichier de CommunityDragon pèse plusieurs mégaoctets et les recettes
    # ne bougent qu'au patch. Huit téléchargements par jour pour un résultat
    # identique seraient du gaspillage pris sur une source gratuite.
    if not forcer and os.path.exists(SORTIE):
        try:
            ancien = json.load(open(SORTIE, encoding="utf-8"))
            if (ancien.get("cale_sur") or {}).get("patch") == rel.get("patch"):
                print(f"recettes déjà calées sur le patch {rel.get('patch')} "
                      f"— rien à faire (--forcer pour refaire).")
                return
        except Exception:
            pass          # fichier illisible : on le refait, c'est le but

    vus = rel.get("objets") or {}
    if not vus:
        sys.exit(f"{nom} ne porte pas de bloc `objets`. C'est un relevé "
                 "antérieur au 04/11 : relance tactics.py --forcer pour en "
                 "produire un qui en contienne.")

    d = lire(CDRAGON)
    par_id = {i["apiName"]: i for i in (d.get("items") or []) if i.get("apiName")}

    # On ne garde que les objets RÉELLEMENT VUS en partie dans le dernier
    # relevé — c'est ce qui cale la table sur le set en cours sans préfixe.
    composants, recettes, sans_recette, inconnus = {}, {}, [], []
    for oid in vus:
        it = par_id.get(oid)
        if not it:
            inconnus.append(oid)
            continue
        comp = it.get("composition")
        if isinstance(comp, list) and len(comp) == 2:
            recettes[oid] = {"nom": it.get("name"), "de": comp}
        elif "_Component_" in oid:
            suffixe = oid.split("_Component_")[-1]
            composants[oid] = {"nom": it.get("name"),
                               "fr": FR.get(suffixe, it.get("name"))}
        else:
            # Radiants, artefacts, objets d'emblème non craftables : ils
            # existent, ils ne se fabriquent pas à partir de deux composants.
            sans_recette.append(oid)

    # Les composants peuvent n'apparaître dans AUCUNE entrée du relevé (on ne
    # finit pas une partie avec un composant au banc). On les récupère alors
    # depuis les recettes elles-mêmes.
    for r in recettes.values():
        for c in r["de"]:
            if c not in composants:
                it = par_id.get(c) or {}
                suffixe = c.split("_Component_")[-1]
                composants[c] = {"nom": it.get("name", c),
                                 "fr": FR.get(suffixe, it.get("name", c))}

    # ── CE QUE CHAQUE COMPOSANT PERMET DE FABRIQUER ──────────────────────
    # C'est la table que le joueur lit AU CARROUSEL : « si je prends une
    # larme, qu'est-ce que ça m'ouvre ? ». L'inverse de la recette.
    ouvre = {c: [] for c in composants}
    for oid, r in recettes.items():
        for c in set(r["de"]):
            if c in ouvre:
                ouvre[c].append(oid)

    out = {
        "schema_version": SCHEMA,
        "genere_le": date.today().isoformat(),
        "source": "CommunityDragon (données Riot)",
        "cale_sur": {"releve": nom, "patch": rel.get("patch"),
                     "set": rel.get("set")},
        "composants": composants,
        "recettes": recettes,
        "ouvre": ouvre,
        "sans_recette": sorted(sans_recette),
        "inconnus": sorted(inconnus),
        "note": ("Table calée sur les objets vus dans le dernier relevé, pas "
                 "sur un préfixe de set : elle suivra le Set 19 sans qu'on "
                 "touche au script. `sans_recette` liste les objets qui "
                 "existent mais ne se fabriquent pas à partir de deux "
                 "composants (radiants, artefacts) ; `inconnus` ceux que "
                 "CommunityDragon ne connaît pas — s'il se remplit, c'est que "
                 "la source a changé de nommage."),
    }

    os.makedirs(os.path.dirname(SORTIE), exist_ok=True)
    json.dump(out, open(SORTIE, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    print(f"écrit : {SORTIE}")
    print(f"  calé sur {nom} (patch {rel.get('patch')})")
    print(f"  {len(composants)} composants · {len(recettes)} recettes · "
          f"{len(sans_recette)} sans recette · {len(inconnus)} inconnus")
    if composants:
        print("  composants : " + " · ".join(sorted(
            v["fr"] for v in composants.values())))
    if inconnus:
        print(f"  ⚠ inconnus de CommunityDragon : {', '.join(inconnus[:6])}"
              + (" …" if len(inconnus) > 6 else ""))


if __name__ == "__main__":
    main()
