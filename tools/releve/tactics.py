#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RELEVÉ AUTOMATIQUE — tactics.tools -> data/releves-tt/
=======================================================
Produit un relevé de méta sans navigateur. C'était le verrou de la v3 :
MetaTFT ne rend ses chiffres qu'en JavaScript, donc tout relevé exigeait
Chrome, donc une intervention humaine. tactics.tools sert les mêmes
chiffres en JSON.

    python3 tools/releve/tactics.py            # Master+, patch courant
    python3 tools/releve/tactics.py --rang 4   # GM+
    python3 tools/releve/tactics.py --forcer   # réécrit un relevé existant

⚠ CE SCRIPT NE TOURNE PAS DEPUIS UNE SESSION CLAUDE. Le proxy du conteneur
refuse `d3.tft.tools` au CONNECT (403). Il est fait pour le runner GitHub
Actions, dont le réseau est libre. Depuis une session, passer par Chrome.

─── Pourquoi une série SÉPARÉE de data/releves/ ───────────────────────────
Le 03/11, les deux sources ont été comparées sur le même patch et la même
tranche : Spearman 0.982, déplacement médian 1 rang, pour un plancher de
bruit à 0.955. Elles mesurent la même chose.

MAIS elles ne la DÉCOUPENT pas pareil :
  - tactics.tools éclate Lux en neuf entrées (Lux_Sunbeam, Lux_Elderwood…)
    là où MetaTFT n'en compte qu'une : 74 entrées contre 60 ;
  - les patchs ne portent pas les mêmes noms (« 18.5 » contre « 18.5b »).

Mélanger les deux séries dans un même dossier produirait des comparaisons
silencieusement fausses. D'où `data/releves-tt/`, physiquement à part.
"""

import argparse, json, os, re, sys, urllib.error, urllib.request
from datetime import date

RACINE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# La seule porte vers l'extérieur vit dans tools/lib/reseau.py : une définition,
# et un mode rejeu qui permet de répéter le 1er décembre sans réseau.
sys.path.insert(0, os.path.join(RACINE, "tools", "lib"))
from reseau import lire as _lire


def lire(url, **kw):
    return _lire(url, quoi="relevé de méta", **kw)

SORTIE = os.path.join(RACINE, "data", "releves-tt")
# ⚠ RESTE À 1, ET C'EST DÉLIBÉRÉ.
#
# Le 04/11, `objets`, `traits` et `unites[].objets` ont été ajoutés au relevé.
# La tentation était de passer à 2. Mais `tools/lib/mesures.py` ÉCARTE en mode
# strict tout relevé dont la version ne vaut pas son propre SCHEMA — et il
# l'annonce sur une ligne au milieu d'une sortie de script. Monter ici aurait
# fait disparaître tous les nouveaux relevés de la série de rotation, en
# silence, au moment précis où on en ajoute.
#
# Les champs ajoutés sont PUREMENT ADDITIFS : aucun lecteur existant ne les
# lit, aucun champ n'a changé de sens. Un lecteur qui en a besoin CONSTATE
# leur présence (`if r.get("objets")`) au lieu de la supposer. Ne monter cette
# version que pour un changement qui CASSE la lecture — et alors monter aussi
# celle de mesures.py dans le même commit.
SCHEMA = 1

PAGE = "https://tactics.tools/units"
CDN  = "https://d3.tft.tools/stats2/general/1100/{code}/{rang}"

RANGS = {0: "Master+", 1: "Diamant+", 2: "Émeraude+", 3: "Platine+", 4: "GM+"}





def patch_courant():
    """Le code ET le libellé du patch, lus sur la page elle-même.

    Jamais codés en dur : les codes changent à chaque patch, et surtout à
    chaque set. Le code vit dans __NEXT_DATA__, le libellé dans le <title>.
    """
    html = lire(PAGE, json_attendu=False)

    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S)
    if not m:
        sys.exit("__NEXT_DATA__ introuvable : la page a changé de structure. "
                 "Rouvrir tactics.tools et relire où vit le code du patch.")
    code = (json.loads(m.group(1)).get("props", {}).get("pageProps", {})
            .get("aperture", {}).get("patch", {}).get("_0"))
    if not isinstance(code, int):
        sys.exit("Code de patch absent de __NEXT_DATA__ "
                 "(props.pageProps.aperture.patch._0).")

    t = re.search(r"<title>(.*?)</title>", html, re.S)
    titre = (t.group(1) if t else "")
    lib = re.search(r"Patch\s+([0-9][0-9.a-zA-Z]*)", titre)
    if not lib:
        sys.exit(f"Libellé de patch introuvable dans le titre : {titre!r}")
    return code, lib.group(1).strip()


def construire(code, libelle, rang):
    d = lire(CDN.format(code=code, rang=rang), json_attendu=True)
    unites = d.get("units") or {}
    if not unites:
        sys.exit(f"Aucune unité renvoyée pour le patch {libelle} (code {code}), "
                 f"tranche {rang}. Relevé non écrit.")

    # On garde les identifiants de Riot comme clés (DA_18_Alune). C'est ce
    # qui permettra de joindre ce relevé aux parties du Miroir sans
    # correspondance de noms approximative.
    #
    # `topItems` : les cinq objets les plus portés par CETTE unité, dans
    # l'ordre de la source. C'est le BiS mesuré, et il était téléchargé depuis
    # le premier jour sans jamais être conservé.
    # `star*` : les mêmes statistiques en 3 étoiles, qui n'ont rien à voir avec
    # celles en 2 — une unité peut être médiocre en 2 et décisive en 3.
    table = {k: {"avg": v["place"], "wr": v.get("won"), "t4": v.get("top4"),
                 "n": v["count"],
                 "objets": v.get("topItems") or [],
                 "etoile3": ({"n": v["starCount"], "avg": v.get("starPlace"),
                              "t4": v.get("starTop4"), "wr": v.get("starWon")}
                             if v.get("starCount") else None)}
             for k, v in unites.items() if v.get("count")}

    # ── LES OBJETS ────────────────────────────────────────────────────────
    # 126 entrées, dans la MÊME réponse que les unités. Jetées jusqu'ici.
    #
    # `porteurs` (topUsers à la source) est la pièce rare : pour chaque objet,
    # les unités qui le portent AVEC l'effet mesuré sur le placement. Un delta
    # négatif veut dire « meilleur placement » — c'est la convention de la
    # source, et on la conserve telle quelle pour ne pas inventer un signe.
    objets = {}
    for o in (d.get("items") or []):
        oid = o.get("itemId")
        if not oid or not o.get("count"):
            continue
        objets[oid] = {
            "avg": o.get("place"), "wr": o.get("won"), "t4": o.get("top4"),
            "n": o["count"],
            "porteurs": [[u, round(delta, 4)]
                         for u, delta in (o.get("topUsers") or [])],
        }

    # ── LES TRAITS ────────────────────────────────────────────────────────
    # Les clés portent le palier : « DA_18_Blackthorn__2 » = Blackthorn à 2.
    # On sépare nom et palier ici plutôt que dans chaque lecteur — un palier
    # n'est pas un suffixe de texte, c'est une donnée.
    traits = {}
    for k, v in (d.get("traits") or {}).items():
        if not v.get("count"):
            continue
        nom, _, palier = k.partition("__")
        traits[k] = {"trait": nom, "palier": int(palier) if palier.isdigit() else None,
                     "avg": v.get("place"), "wr": v.get("won"),
                     "t4": v.get("top4"), "n": v["count"]}

    return {
        "schema_version": SCHEMA,
        "date": date.today().isoformat(),
        "patch": libelle,
        "patch_code": code,
        "rang": RANGS.get(rang, str(rang)),
        "rang_code": rang,
        "source": "tactics.tools",
        "n_parties": d.get("totalEntries"),
        "fenetre": "cumul depuis le début du patch",
        # Le numéro de set se lit dans le libellé (« 19.1 » -> 19). En dur,
        # ce champ passerait à null le 1er décembre — le jour exact où il
        # faudra que tout marche.
        "set": int(libelle.split(".")[0]) if libelle.split(".")[0].isdigit() else None,
        "maj_source": d.get("lastUpdated"),
        "note": ("Série PARALLÈLE à data/releves/ (MetaTFT) : mêmes chiffres à "
                 "0.982 de corrélation, mais découpage des unités différent "
                 "(Lux éclatée en variantes) et libellés de patch différents. "
                 "NE JAMAIS comparer un relevé de cette série à un relevé "
                 "MetaTFT sans agréger les variantes."),
        "unites": table,
        "objets": objets,
        "traits": traits,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rang", type=int, default=0,
                    help="0=Master+ (défaut) · 1=Diamant+ · 4=GM+")
    ap.add_argument("--forcer", action="store_true",
                    help="réécrire un relevé déjà présent pour ce patch")
    a = ap.parse_args()

    code, libelle = patch_courant()
    print(f"patch courant : {libelle} (code {code}) · tranche {RANGS.get(a.rang, a.rang)}")

    os.makedirs(SORTIE, exist_ok=True)

    # ─── UN RELEVÉ PAR PATCH, QUI MÛRIT ───────────────────────────────────
    #
    # Ce bloc figeait le PREMIER relevé de chaque patch et ne le réécrivait
    # jamais. L'intention était bonne — « ne pas diluer la photo du jour du
    # patch sur toute sa durée de vie » — et elle servait mal les deux seuls
    # usages réels :
    #
    #   « qu'est-ce qui est fort maintenant » (le site) veut le cliché LE PLUS
    #   FOURNI ; « de combien la méta a tourné » veut deux clichés COMPARABLES,
    #   donc tous deux mûrs.
    #
    # Figer à J+0 ne sert ni l'un ni l'autre. Un patch sort, le workflow le
    # voit dans les heures qui suivent, et on gèle pour toujours le cliché le
    # moins fourni qui existera jamais de ce patch — puis on s'en sert pour
    # mesurer une rotation. Les six transitions de la charte viennent
    # d'archives de FIN de patch : on comparerait un jeune à des mûrs.
    #
    # Et les relevés sont CUMULÉS depuis le début du patch, constaté le 05/11 :
    # les 500 777 parties du 04/11 contiennent les 449 902 du 03/11, le n de
    # chaque unité ne fait que croître. Réécrire n'écrase donc pas une mesure
    # par une autre : ça complète la même mesure.
    #
    # Nouvelle règle : on réécrit tant que le nouveau cliché est PLUS FOURNI,
    # en gardant le nom de fichier du premier (l'ordre chronologique de la
    # série reste stable) et en conservant la date de première vue.
    #
    # ⚠ Ce qu'on perd : la reproductibilité d'une mesure faite hier sur un
    # relevé qui a changé depuis. C'est assumé — l'historique git garde chaque
    # version, et `premier_releve` dit depuis quand le patch est suivi.
    deja = sorted(f for f in os.listdir(SORTIE)
                  if f.endswith(f"_{libelle}_r{a.rang}.json"))
    ancien = None
    if deja:
        try:
            ancien = json.load(open(os.path.join(SORTIE, deja[0]),
                                    encoding="utf-8"))
        except Exception:
            ancien = None

    r = construire(code, libelle, a.rang)

    if ancien and not a.forcer:
        avant = ancien.get("n_parties") or 0
        if r["n_parties"] <= avant:
            print(f"  relevé déjà présent et aussi fourni : {deja[0]} "
                  f"({avant:,} parties) — rien à faire.".replace(",", " "))
            print("::notice::Relevé inchangé.")
            return 0
        # On complète : même fichier, même date de première vue.
        r["premier_releve"] = ancien.get("premier_releve") or ancien.get("date")
        r["n_parties_premier"] = ancien.get("n_parties_premier") or avant
        r["n_mises_a_jour"] = (ancien.get("n_mises_a_jour") or 0) + 1
        nom = deja[0]
        print(f"  le patch mûrit : {avant:,} -> {r['n_parties']:,} parties"
              .replace(",", " "))
    else:
        r["premier_releve"] = r["date"]
        r["n_parties_premier"] = r["n_parties"]
        r["n_mises_a_jour"] = 0
        nom = f"{r['date']}_{libelle}_r{a.rang}.json"

    chemin = os.path.join(SORTIE, nom)
    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(r, f, ensure_ascii=False, indent=1)

    print(f"  écrit : data/releves-tt/{nom}")
    print(f"  {len(r['unites'])} unités · {r['n_parties']:,} parties"
          .replace(",", " "))
    meilleures = sorted(r["unites"].items(), key=lambda kv: kv[1]["avg"])[:3]
    for k, v in meilleures:
        print(f"    {v['avg']:.2f}  {k}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
