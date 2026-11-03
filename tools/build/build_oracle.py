#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CONSTRUCTEUR DE L'ORACLE
========================
Assemble trois choses en un fichier HTML autonome, à ouvrir d'un double-clic,
hors ligne :

    engine.html              le moteur — aucune donnée de set
    data_set<N>_fige.js      les fiches figées (plans, BiS, augments, lexique)
    data/releves/<dernier>   les données du relevé, GÉNÉRÉES ici

    python3 tools/build/build_oracle.py        -> site/oracle.html (set auto)
    python3 tools/build/build_oracle.py 19     -> force un set

Pourquoi les blocs de relevé sont générés et non écrits à la main : ils vivaient
auparavant dans data_set18.js, en double avec data/releves/. Les deux copies
concordaient, mais rien ne le garantissait — et la première divergence serait
passée inaperçue. Désormais le relevé est la seule source, et l'Oracle en
descend, exactement comme le site.

AU SET 19 : écrire data_set19_fige.js (les fiches), déposer les relevés dans
data/releves/, lancer `build_oracle.py 19`. engine.html ne bouge pas.
"""

import sys, re, io, os

RACINE = os.path.dirname(os.path.abspath(__file__))          # tools/build/
DEPOT  = os.path.dirname(os.path.dirname(RACINE))            # racine du dépôt
SORTIE = os.path.join(DEPOT, "site")                         # servi par le site

sys.path.insert(0, os.path.join(os.path.dirname(RACINE), "lib"))
import mesures as M


def js_date(iso):
    a, m, j = iso.split("-")
    return f"{j}/{m}/{a}"


def ech(t):
    """Échappe pour une chaîne JS entre guillemets doubles."""
    return (str(t).replace("\\", "\\\\").replace('"', '\\"')
            .replace("\n", " ").replace("\r", ""))


def bloc_meta(r):
    n = f"{r.get('n_parties', 0):,}".replace(",", " ")
    # la note du relevé porte souvent un avertissement sur la qualité des
    # données (volume faible, fenêtre inhabituelle) : on la conserve.
    note = r.get("note", "")
    suffixe = f" — {ech(note)}" if note else ""
    return (f'const META_DATE  = "{js_date(r["date"])}";\n'
            f'const META_PATCH = "LIVE · patch {ech(r.get("patch","?"))} · '
            f'{ech(r.get("rang","?"))} · {ech(r.get("fenetre",""))}";\n'
            f'const META_N     = "{n} parties · {ech(r.get("source","MetaTFT"))}{suffixe}";\n'
            f'const NMIN_UNIT  = {M.NMIN};')


def bloc_units(r):
    lignes = [f' "{ech(k)}":[{v["avg"]},{v["wr"]},{v["n"]}],'
              for k, v in sorted(r["unites"].items(), key=lambda kv: kv[1]["avg"])]
    return "const UNITS = {\n" + "\n".join(lignes) + "\n};"


def bloc_metacomps(r):
    out = ["const METACOMPS = ["]
    for c in r.get("compos", []):
        ros = ",".join(f'"{ech(x)}"' for x in c.get("roster", []))
        t4 = "null" if c.get("t4") is None else c["t4"]
        out.append(
            f' {{n:"{ech(c["n"])}", lvl:"{ech(c.get("lvl",""))}", '
            f'carry:"{ech(c.get("carry",""))}",\n'
            f'  roster:[{ros}],\n'
            f'  avg:{c["avg"]}, pr:{c["pr"]}, wr:{c["wr"]}, t4:{t4},\n'
            f'  note:"{ech(c.get("note",""))}"}},')
    out.append("];")
    return "\n".join(out)


def set_courant():
    """Le set du relevé le plus récent, et non une valeur en dur.

    Le 03/11, `tactics.py` écrivait « set: 18 » en dur : au patch 19.1 il
    aurait écrit null, le 1er décembre, c'est-à-dire le jour exact où tout
    doit marcher. Même piège ici, en pire — le workflow de déploiement
    appelait `build_oracle.py 18`, donc au Set 19 le site aurait publié
    en silence un Oracle du Set 18, sans la moindre erreur pour le dire.
    """
    sets = [r.get("set") for r in M.charger() if r.get("set") is not None]
    return str(sets[-1]) if sets else None


def construire(num=None):
    if num is None:
        num = set_courant()
        if num is None:
            print("::warning::Aucun relevé ne porte de numéro de set. "
                  "Oracle non régénéré.")
            return None
        print(f"set détecté depuis le dernier relevé : {num}")

    moteur_p = os.path.join(RACINE, "engine.html")
    fige_p   = os.path.join(RACINE, f"data_set{num}_fige.js")
    if not os.path.exists(moteur_p):
        raise SystemExit(f"Introuvable : {moteur_p}")

    # Les fiches d'un set neuf n'existent pas tant que personne ne les a
    # écrites. C'est NORMAL au lancement d'un set, et ça ne doit surtout pas
    # faire échouer le déploiement de tout le site : l'Oracle est une page
    # parmi d'autres. On prévient, on passe.
    if not os.path.exists(fige_p):
        print(f"::warning::{os.path.basename(fige_p)} absent — "
              f"l'Oracle du Set {num} n'est pas régénéré. "
              "Écrire les fiches du set pour le rétablir.")
        return None

    moteur = io.open(moteur_p, encoding="utf-8").read()
    fige   = io.open(fige_p, encoding="utf-8").read()

    releves = [r for r in M.charger() if str(r.get("set")) == str(num)]
    if not releves:
        raise SystemExit(f"Aucun relevé pour le Set {num} dans {M.RELEVES}")
    r = releves[-1]
    print(f"relevé utilisé : {r['date']} ({r.get('patch')}, {r.get('rang')})")

    blocs = {}
    for m in re.finditer(r'/\*__DATA:([A-Z_]+)__\*/\n(.*?)(?=\n/\*__DATA:|\Z)', fige, re.S):
        blocs[m.group(1)] = m.group(2).rstrip()
    blocs["META"]      = bloc_meta(r)
    blocs["UNITS"]     = bloc_units(r)
    blocs["METACOMPS"] = bloc_metacomps(r)

    attendus = set(re.findall(r'/\*__DATA:([A-Z_]+)__\*/', moteur))
    manquants = attendus - set(blocs)
    if manquants:
        raise SystemExit("Blocs manquants : " + ", ".join(sorted(manquants)))
    en_trop = set(blocs) - attendus
    if en_trop:
        print(f"  (blocs ignorés, absents du moteur : {', '.join(sorted(en_trop))})")

    html = moteur
    for nom in attendus:
        html = html.replace(f'/*__DATA:{nom}__*/', blocs[nom])
    assert "__DATA:" not in html, "un marqueur n'a pas été substitué"

    os.makedirs(SORTIE, exist_ok=True)
    dest = os.path.join(SORTIE, "oracle.html")
    io.open(dest, "w", encoding="utf-8").write(html)
    print(f"OK  {dest}")
    print(f"    {len(html)} caractères · {len(r['unites'])} unités · "
          f"{len(r.get('compos', []))} compos")
    return dest


if __name__ == "__main__":
    # Sans argument : le set du relevé le plus récent. Un numéro en dur ici
    # serait une panne programmée au changement de set.
    construire(sys.argv[1] if len(sys.argv) > 1 else None)
