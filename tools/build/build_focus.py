#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LE FOCUS — croise ses parties et la méta -> data/focus.json
============================================================
La moitié « méta » et la moitié « ses parties » du projet ne se parlaient
pas. Elles le peuvent depuis que le relevé vient de tactics.tools, qui
utilise les identifiants de Riot — exactement ceux que renvoie l'API dans
ses propres parties.

    python3 tools/build/build_focus.py

Lit  : data/miroir.json  (ses parties)  +  data/releves-tt/<dernier>.json
Écrit: data/focus.json

─── TROIS PIÈGES, TOUS RENCONTRÉS LE 03/11 ────────────────────────────────

**1. Les variantes.** tactics.tools éclate Lux en DIX entrées
(Lux_Moonbeam, Lux_Elderwood, Lux_Base…). Prises séparément, chacune a un
pick rate de 1 à 3 % et un excellent placement : elles ressortaient toutes
comme « fortes et peu contestées ». Recollées, Lux est à 13.2 % de pick.
**Toujours regrouper par champion avant de parler de contestation.**

**2. La ligne de base.** Comparer son placement avec une unité au placement
du ladder avec la même unité donne un écart négatif sur TOUTES les unités,
de −0.21 à −1.22. Ce n'est pas de la compétence : le ladder fait 4.50 par
construction et lui 3.74, donc −0.76 d'office, partout. **On retire son
avantage général avant de lire quoi que ce soit.**

**3. Le conditionnement.** Même corrigé, l'écart reste imparfait : SON
chiffre porte sur les parties où l'unité tenait des objets (un carry),
celui du ladder sur les parties où elle était simplement présente, y
compris en bouche-trou. Les deux ne décrivent pas la même situation.
**L'écart est une piste, jamais une conclusion** — et le champ `solide`
dit s'il franchit seulement le bruit.
"""

import glob, json, math, os, re, statistics as st, sys, unicodedata

RACINE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(RACINE, "tools", "lib"))
import mesures as M
SORTIE = os.path.join(RACINE, "data", "focus.json")
SCHEMA = 1
SD = 2.2                 # écart-type du placement, pour les seuils de bruit
NEUTRE = 4.50            # placement moyen du ladder, par construction
VOL_MIN = 3000           # sous ce volume, une unité du relevé n'est pas lisible


# champion() vit dans tools/lib/mesures.py — UNE seule définition de
# « est-ce la même unité ? ». Quatre copies existaient le 05/11.
champion = M.champion


def norm(s):
    s = unicodedata.normalize("NFD", str(s))
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z]", "", s.lower().replace("da_", "").replace("18", ""))


def parties_requises(ecart):
    """Combien de parties il faudrait pour que cet écart sorte du bruit.

    C'est le chiffre le plus utile de tout le fichier : il transforme
    « on ne sait pas » en « voilà ce qu'il faudrait pour savoir »."""
    if not ecart:
        return None
    return int(math.ceil((2 * SD / abs(ecart)) ** 2))


def main():
    p_mi = os.path.join(RACINE, "data", "miroir.json")
    rel = sorted(glob.glob(os.path.join(RACINE, "data", "releves-tt", "*.json")))
    if not os.path.exists(p_mi):
        sys.exit("data/miroir.json absent — lance build_miroir.py d'abord.")
    if not rel:
        sys.exit("Aucun relevé dans data/releves-tt/ — lance tools/releve/tactics.py.")

    mi = json.load(open(p_mi, encoding="utf-8"))
    rv = json.load(open(rel[-1], encoding="utf-8"))
    TOT = rv["n_parties"]

    # --- la méta, regroupée par champion (piège n°1)
    agg = {}
    for ident, v in rv["unites"].items():
        a = agg.setdefault(champion(ident), {"n": 0, "somme": 0.0, "variantes": 0})
        a["n"] += v["n"]
        a["somme"] += v["avg"] * v["n"]
        a["variantes"] += 1
    for a in agg.values():
        a["avg"] = round(a["somme"] / a["n"], 2)
        a["pick"] = round(a["n"] / TOT * 100, 1)
        del a["somme"]

    lisibles = {k: a for k, a in agg.items() if a["n"] >= VOL_MIN}
    q1 = sorted(a["avg"] for a in lisibles.values())[len(lisibles) // 4]
    pick_med = st.median(a["pick"] for a in lisibles.values())

    # --- ce qu'il joue
    siens = {norm(c["nom"]) for c in mi.get("carries", [])}
    siens |= {norm(p) for x in mi.get("parties", []) for p in x.get("pieces", [])}

    base = round(mi["placement_moyen"] - NEUTRE, 3)     # piège n°2

    lignes = []
    for c in mi.get("carries", []):
        cle = norm(c["nom"])
        cible = next((a for k, a in agg.items() if norm(k) == cle), None)
        if not cible:
            continue
        brut = c["placement"] - cible["avg"]
        corr = round(brut - base, 2)
        seuil = round(2 * SD / math.sqrt(c["n"]), 2)
        lignes.append({
            "nom": c["nom"], "n": c["n"],
            "son_placement": c["placement"],
            "placement_ladder": cible["avg"],
            "ecart_brut": round(brut, 2),
            "ecart_corrige": corr,
            "seuil": seuil,
            "solide": abs(corr) >= seuil,
            "parties_requises": parties_requises(corr),
            "pick": cible["pick"],
        })
    lignes.sort(key=lambda x: x["ecart_corrige"])

    out = {
        "schema_version": SCHEMA,
        "genere_le": __import__("datetime").date.today().isoformat(),
        "releve": {"patch": rv["patch"], "rang": rv["rang"],
                   "source": rv["source"], "n_parties": TOT},
        "lui": {"parties": mi["n_parties"], "placement_moyen": mi["placement_moyen"],
                "avantage_general": base},
        "seuils": {"quartile_fort": q1, "pick_median": pick_med,
                   "volume_min": VOL_MIN},
        "lignes": lignes,
        "fortes_peu_contestees": sorted(
            [{"nom": k, **a, "il_la_joue": norm(k) in siens}
             for k, a in lisibles.items()
             if a["avg"] <= q1 and a["pick"] <= pick_med],
            key=lambda x: x["avg"]),
        "tres_contestees": sorted(
            [{"nom": k, **a, "il_la_joue": norm(k) in siens}
             for k, a in lisibles.items()],
            key=lambda x: -x["pick"])[:8],
        "reserves": {
            "conditionnement": "Son placement porte sur les parties où l'unité tenait "
                "des objets ; celui du ladder sur les parties où elle était présente, "
                "y compris en bouche-trou. Les deux ne décrivent pas la même situation : "
                "l'écart est une piste, jamais une conclusion.",
            "ligne_de_base": f"Le ladder place à {NEUTRE} par construction et lui à "
                f"{mi['placement_moyen']}, soit {base:+.2f} d'office sur toutes les "
                "unités. C'est retiré de l'écart corrigé.",
            "contestation": "Le pick rate mesure la présence en lobby. Pour un carry "
                "c'est de la contestation ; pour une unité universelle c'est de la "
                "banalité. Les deux ne se distinguent pas dans cette donnée.",
            "variantes": "Les variantes d'un même champion sont regroupées : "
                "séparées, les dix Lux passaient pour dix unités rares et fortes.",
        },
    }

    json.dump(out, open(SORTIE, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    sol = [l for l in lignes if l["solide"]]
    print(f"écrit : {SORTIE}")
    print(f"  relevé {rv['patch']} · {rv['rang']} · {TOT:,} parties".replace(",", " "))
    print(f"  {len(agg)} champions ({len(rv['unites'])} entrées regroupées)")
    print(f"  {len(lignes)} de ses lignes croisées · {len(sol)} hors du bruit")
    print(f"  {len(out['fortes_peu_contestees'])} unités fortes et peu contestées, "
          f"dont {sum(1 for x in out['fortes_peu_contestees'] if not x['il_la_joue'])} "
          "qu'il ne joue pas")
    if lignes:
        pire = lignes[-1]
        print(f"  à surveiller : {pire['nom']} {pire['ecart_corrige']:+.2f} "
              f"(seuil {pire['seuil']}, il faudrait {pire['parties_requises']} parties, "
              f"il en a {pire['n']})")


if __name__ == "__main__":
    main()
