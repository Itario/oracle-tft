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
SORTIE = os.path.join(RACINE, "data", "releves-tt")
SCHEMA = 1

PAGE = "https://tactics.tools/units"
CDN  = "https://d3.tft.tools/stats2/general/1100/{code}/{rang}"

RANGS = {0: "Master+", 1: "Diamant+", 2: "Émeraude+", 3: "Platine+", 4: "GM+"}

# Le 02/11, la collecte Riot est restée bloquée deux semaines sur un 403
# causé par l'absence de User-Agent : urllib s'annonce « Python-urllib/3.x »
# et les bordures CDN rejettent cet agent. On ne refait pas l'erreur.
EN_TETES = {
    "User-Agent": "OracleTFT/1.0 (relevé de méta, usage personnel)",
    "Accept": "application/json, text/html",
}


def lire(url, json_attendu=True):
    req = urllib.request.Request(url, headers=EN_TETES)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            brut = r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        corps = ""
        try:
            corps = e.read(400).decode("utf-8", "replace").strip()
        except Exception:
            pass
        sys.exit(f"HTTP {e.code} sur {url}\n  corps : {corps}")
    except Exception as e:
        sys.exit(f"Impossible de joindre {url}\n  {type(e).__name__}: {e}\n"
                 "  (Depuis une session Claude, c'est normal : le proxy du "
                 "conteneur bloque ce domaine. Ce script est fait pour le "
                 "runner GitHub Actions.)")
    return json.loads(brut) if json_attendu else brut


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
    d = lire(CDN.format(code=code, rang=rang))
    unites = d.get("units") or {}
    if not unites:
        sys.exit(f"Aucune unité renvoyée pour le patch {libelle} (code {code}), "
                 f"tranche {rang}. Relevé non écrit.")

    # On garde les identifiants de Riot comme clés (DA_18_Alune). C'est ce
    # qui permettra de joindre ce relevé aux parties du Miroir sans
    # correspondance de noms approximative.
    table = {k: {"avg": v["place"], "wr": v.get("won"), "t4": v.get("top4"),
                 "n": v["count"]}
             for k, v in unites.items() if v.get("count")}

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
        "set": 18 if libelle.startswith("18") else None,
        "maj_source": d.get("lastUpdated"),
        "note": ("Série PARALLÈLE à data/releves/ (MetaTFT) : mêmes chiffres à "
                 "0.982 de corrélation, mais découpage des unités différent "
                 "(Lux éclatée en variantes) et libellés de patch différents. "
                 "NE JAMAIS comparer un relevé de cette série à un relevé "
                 "MetaTFT sans agréger les variantes."),
        "unites": table,
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
    # Un relevé est une photo FIGÉE : un seul par patch et par tranche, jamais
    # réécrit. Sans ce garde-fou, une exécution quotidienne écraserait la photo
    # du jour du patch par une photo diluée sur toute sa durée de vie.
    deja = [f for f in os.listdir(SORTIE)
            if f.endswith(f"_{libelle}_r{a.rang}.json")]
    if deja and not a.forcer:
        print(f"  relevé déjà présent : {deja[0]} — rien à faire.")
        print("::notice::Aucun nouveau patch, relevé inchangé.")
        return 0

    r = construire(code, libelle, a.rang)
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
