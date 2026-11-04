#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LES COMPOS — ce que le ladder joue vraiment -> data/compos.json
================================================================
Relève les compositions sur tactics.tools/team-compositions, qui en publie
bien plus que le classement d'unités : par compo, les unités exactes, les
paliers de traits atteints, les porteurs, le niveau auquel on la joue, et
surtout `lpDelta` — **le LP gagné par partie**.

    python3 tools/releve/compos.py

⚠ Comme les autres relevés : ne tourne pas depuis une session Claude, le
proxy du conteneur bloque le domaine. Fait pour le runner GitHub.

─── POURQUOI `lpDelta` EST LE CHIFFRE QUI COMPTE ──────────────────────────
Un placement moyen décrit une performance. Le LP décrit un CLASSEMENT. Depuis
qu'on sait que 704 LP séparent Clément de la barre (data/joueur.json), une
compo ne se juge plus à son placement mais à ce qu'elle rapporte par partie.
Les deux sont liés — notre propre barème donne LP ≈ 70.8 − 15.4 × place —
mais `lpDelta` est mesuré, là où notre barème est ajusté.

─── LA VÉRIFICATION QUI ÉVITE LE PIÈGE DE POPULATION ──────────────────────
La page des compos expose `aperture.rankGroup: 1`. La page des unités, elle,
numérote ses tranches autrement : son rang 0 vaut Master+, son rang 1 vaut
Diamant+. **Les deux « 1 » ne désignent pas la même chose.**

Mesuré le 04/11 :

    unités rang 0 (Master+)    500 777 parties
    unités rang 1 (Diamant+)  2 614 557
    compos rankGroup 1           495 058   <- à 1 % de Master+

Donc `rankGroup: 1` des compos = Master+, la même population que le relevé
d'unités. Ce script le REVÉRIFIE à chaque exécution au lieu de le supposer :
si l'écart dépasse le seuil, il écrit l'avertissement dans le fichier plutôt
que de laisser croiser deux populations différentes en silence.

─── CE QUE CE FICHIER NE DIT PAS ──────────────────────────────────────────
**Le serveur n'envoie que les cinq premiers groupes.** C'est le haut du
classement, pas la méta entière : une compo absente d'ici n'est pas mauvaise,
elle n'est pas dans les cinq premières.

**Les augments n'y sont pas non plus.** Les champs existent — `augmentSingles`,
`aug1s`, `aug2s`, `aug3s` — et ils sont VIDES à 495 000 parties. C'est la
confirmation la plus nette qu'on ait obtenue : tactics.tools a gardé les
emplacements, Riot n'envoie plus rien. Le script compte ces champs et écrit
le résultat, pour que le jour où ils se remplissent, on le sache sans rien
relancer.
"""

import glob, json, os, re, sys
import urllib.error, urllib.request
from datetime import date

RACINE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SORTIE = os.path.join(RACINE, "data", "compos.json")
RELEVES = os.path.join(RACINE, "data", "releves-tt")
SCHEMA = 1
PAGE = "https://tactics.tools/team-compositions"
ECART_MAX = 0.15        # au-delà, les deux relevés ne décrivent plus la même population

EN_TETES = {
    "User-Agent": "OracleTFT/1.0 (relevé de compos, usage personnel)",
    "Accept": "text/html",
}


def lire(url):
    req = urllib.request.Request(url, headers=EN_TETES)
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            return r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        sys.exit(f"HTTP {e.code} sur {url}")
    except Exception as e:
        sys.exit(f"Impossible de joindre {url}\n  {type(e).__name__}: {e}\n"
                 "  (Normal depuis une session Claude : le proxy du conteneur "
                 "bloque ce domaine. Ce script est fait pour le runner GitHub.)")


def dernier_releve():
    fs = sorted(glob.glob(os.path.join(RELEVES, "*.json")))
    if not fs:
        return None, None
    return json.load(open(fs[-1], encoding="utf-8")), os.path.basename(fs[-1])


def paires(v, n=6):
    """Les listes de la source sont des tableaux positionnels. On les nomme
    ici plutôt que de laisser chaque lecteur deviner ce que vaut `x[2]`."""
    return v[:n] if isinstance(v, list) else []


def main():
    html = lire(PAGE)
    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S)
    if not m:
        sys.exit("__NEXT_DATA__ introuvable : la page des compos a changé "
                 "de structure.")
    pp = json.loads(m.group(1)).get("props", {}).get("pageProps", {})
    d = pp.get("initialData") or {}
    groupes = d.get("groups") or []
    if not groupes:
        sys.exit("Aucun groupe de compos renvoyé. Relevé non écrit.")

    # ⚠ Le patch se lit dans l'aperture, PAS dans le <title> : celui-ci
    # annonçait « Set 15 » le 04/11 alors que le patch était 18.5c. Un titre
    # est du texte de page, pas une donnée.
    code_patch = ((pp.get("aperture") or {}).get("patch") or {}).get("_0")
    rank_group = (pp.get("aperture") or {}).get("rankGroup")

    # ── La vérification de population, refaite à chaque exécution ────────
    rel, nom_rel = dernier_releve()
    pop = {"compos_count": d.get("count"), "rank_group": rank_group}
    if rel and rel.get("n_parties"):
        a, b = d.get("count") or 0, rel["n_parties"]
        ecart = abs(a - b) / b if b else 1
        pop.update({
            "releve_unites": nom_rel,
            "unites_count": b,
            "unites_rang": rel.get("rang"),
            "ecart_relatif": round(ecart, 4),
            "meme_population": ecart <= ECART_MAX,
            "note": ("Les deux relevés décrivent la même tranche : on peut "
                     "croiser compos et unités."
                     if ecart <= ECART_MAX else
                     "⚠ LES VOLUMES DIVERGENT. La page des compos numérote "
                     "ses tranches autrement que celle des unités. NE PAS "
                     "croiser les deux tant que ce n'est pas élucidé."),
        })
        if code_patch and rel.get("patch_code") and code_patch != rel["patch_code"]:
            pop["note"] = (f"⚠ PATCHS DIFFÉRENTS : compos {code_patch}, "
                           f"unités {rel['patch_code']}. Ne pas croiser.")
            pop["meme_population"] = False

    # ── Les augments, comptés plutôt que proclamés absents ───────────────
    champs_aug = ("augmentSingles", "aug1s", "aug2s", "aug3s")
    n_aug = sum(len((g.get("full") or {}).get(c) or [])
                for g in groupes for c in champs_aug)
    augments = {
        "champs": list(champs_aug),
        "entrees_trouvees": n_aug,
        "note": ("Les quatre champs d'augments existent dans le schéma de la "
                 "source et sont VIDES. Ce n'est pas une absence supposée : "
                 "elle est comptée à chaque relevé. Si ce nombre devient "
                 "positif, la donnée d'augments est revenue."
                 if n_aug == 0 else
                 "⚠ DES AUGMENTS SONT APPARUS. La question rouverte : "
                 "reprendre §4.4 de la charte."),
    }

    sortie = []
    for g in groupes:
        f = g.get("full") or {}
        if not f.get("count"):
            continue
        n = f["count"]
        sortie.append({
            "code": f.get("code"),
            "n": n,
            "place": round(f["place"], 3) if f.get("place") else None,
            "top4_pct": round(100 * f["top4"] / n, 1) if f.get("top4") else None,
            "premieres_pct": round(100 * f["win"] / n, 1) if f.get("win") else None,
            # Le chiffre qui compte : ce que la compo RAPPORTE, pas où elle place.
            "lp_par_partie": round(f["lpDelta"], 2) if f.get("lpDelta") is not None else None,
            "unites": [u for u in (f.get("units") or [])][:12],
            # [trait, palier, parties, placement]
            "traits": [{"trait": t[0], "palier": t[1], "n": t[2],
                        "place": round(t[3], 3)}
                       for t in paires(f.get("traits"), 8) if len(t) >= 4],
            # [unite, étoiles moyennes]
            "porteurs": [{"unite": c[0], "etoiles_moy": round(c[1], 2)}
                         for c in paires(f.get("carryUnits"), 5) if len(c) >= 2],
            # [[unités], [unités], parties, placement] — ce qui fait gagner
            "conditions_de_victoire": [
                {"unites": w[0], "n": w[2], "place": round(w[3], 3)}
                for w in paires(f.get("winCons"), 4) if len(w) >= 4],
            # [niveau, parties, ?]
            "niveaux": [{"niveau": l[0], "n": l[1]}
                        for l in paires(f.get("levels"), 5) if len(l) >= 2],
            "distribution": f.get("placementDistribution"),
            # Les variantes exactes de la compo, avec leur propre placement.
            "variantes": [
                {"unites": c.get("units"), "n": c.get("count"),
                 "place": round(c["place"], 3) if c.get("place") else None,
                 "traits_sup": c.get("extraTraits") or []}
                for c in paires(f.get("comps"), 4) if c.get("count")],
            # couple unité×objet AVEC placement — un effet, pas une fréquence
            # ⚠ `unitItems` est une LISTE, pas un dictionnaire. Sondé depuis
            # le navigateur avec Object.keys(), il renvoyait "0", "1", "2" —
            # les indices d'un tableau, que j'ai lus comme des clés. Une
            # sonde qui marche sur les deux formes ne distingue pas les deux
            # formes : vérifier le TYPE, pas seulement les clés.
            "objets_par_unite": [
                {"unite": v.get("unitId"), "objet": v.get("itemId"),
                 "n": v.get("count"),
                 "place": round(v["place"], 3) if v.get("place") else None}
                for v in (f.get("unitItems") or [])[:14]
                if isinstance(v, dict) and v.get("count")],
        })

    sortie.sort(key=lambda c: -(c["lp_par_partie"] or -99))

    out = {
        "schema_version": SCHEMA,
        "date": date.today().isoformat(),
        "patch_code": code_patch,
        "patch": (rel or {}).get("patch") if (pop.get("meme_population")) else None,
        "source": "tactics.tools/team-compositions",
        "n_parties": d.get("count"),
        "place_lobby": round(d["place"], 4) if d.get("place") else None,
        "population": pop,
        "augments": augments,
        "compos": sortie,
        "limite": ("Le serveur n'envoie que les cinq premiers groupes. C'est "
                   "le haut du classement, pas la méta entière : une compo "
                   "absente d'ici n'est pas mauvaise, elle n'est simplement "
                   "pas dans les cinq premières."),
    }

    os.makedirs(os.path.dirname(SORTIE), exist_ok=True)
    json.dump(out, open(SORTIE, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    print(f"écrit : {SORTIE}")
    print(f"  {len(sortie)} compos · patch {code_patch} · "
          f"{d.get('count'):,} parties".replace(",", " "))
    if pop.get("meme_population") is False:
        print(f"  ⚠ {pop.get('note')}")
    elif pop.get("meme_population"):
        print(f"  population vérifiée : écart de "
              f"{100*pop['ecart_relatif']:.1f} % avec {pop['unites_rang']}")
    print(f"  augments : {n_aug} entrées trouvées "
          f"({'toujours vide' if n_aug == 0 else '⚠ LA DONNÉE EST REVENUE'})")
    for c in sortie[:3]:
        print(f"    {c['lp_par_partie']:+.2f} LP/partie · place {c['place']} · "
              f"{c['n']:,} parties · ".replace(",", " ")
              + ", ".join(p["unite"].replace("DA_", "").replace("18", "")
                          for p in c["porteurs"][:2]))


if __name__ == "__main__":
    main()
