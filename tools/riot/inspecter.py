#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
INSPECTEUR — que contient vraiment une partie TFT ?
====================================================
La documentation officielle de Riot est incomplète : elle ne mentionne pas
les augments, qui existent pourtant dans la réponse réelle depuis le Set 6.
Plutôt que de deviner, cet outil LIT ce qui est là.

À LANCER APRÈS collecte.py, dans le même dossier :

    python3 inspecter.py

Il affiche l'inventaire complet des champs, repère les augments quel que soit
leur nom, et dit ce qui est exploitable. **Envoie sa sortie à Claude** : elle
tient en quelques lignes, contrairement aux fichiers JSON.
"""

import json, os, sys, glob, collections

RACINE  = os.path.dirname(os.path.abspath(__file__))
DOSSIER = os.path.join(RACINE, "parties")


def arbre(obj, prefixe="", profondeur=0, max_prof=4, vus=None):
    """Inventaire récursif des champs, avec leur type et un exemple."""
    if vus is None:
        vus = []
    if profondeur > max_prof:
        return vus
    if isinstance(obj, dict):
        for k, v in obj.items():
            chemin = f"{prefixe}.{k}" if prefixe else k
            if isinstance(v, (dict, list)):
                n = len(v)
                t = "objet" if isinstance(v, dict) else f"liste[{n}]"
                vus.append((chemin, t, ""))
                if isinstance(v, list) and v:
                    arbre(v[0], chemin + "[]", profondeur + 1, max_prof, vus)
                elif isinstance(v, dict):
                    arbre(v, chemin, profondeur + 1, max_prof, vus)
            else:
                ex = repr(v)
                if len(ex) > 42:
                    ex = ex[:39] + "..."
                vus.append((chemin, type(v).__name__, ex))
    return vus


def chercher_augments(obj, chemin=""):
    """Trouve tout champ qui ressemble à des augments, quel que soit son nom."""
    trouves = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            c = f"{chemin}.{k}" if chemin else k
            if "augment" in k.lower():
                trouves.append((c, v))
            trouves += chercher_augments(v, c)
    elif isinstance(obj, list) and obj:
        trouves += chercher_augments(obj[0], chemin + "[]")
    return trouves


def main():
    if not os.path.isdir(DOSSIER):
        sys.exit(f"Dossier {DOSSIER} introuvable. Lance d'abord collecte.py.")
    fichiers = sorted(glob.glob(os.path.join(DOSSIER, "*.json")))
    if not fichiers:
        sys.exit(f"Aucune partie dans {DOSSIER}. Lance d'abord collecte.py.")

    print(f"=== {len(fichiers)} parties dans {DOSSIER} ===\n")
    m = json.load(open(fichiers[0], encoding="utf-8"))

    info = m.get("info", {})
    print(f"Set        : {info.get('tft_set_number')} ({info.get('tft_set_core_name')})")
    print(f"Version    : {info.get('game_version')}")
    print(f"Type       : {info.get('tft_game_type')} · queue {info.get('queue_id', info.get('queueId'))}")
    print(f"Joueurs    : {len(info.get('participants', []))}")
    print(f"Durée      : {info.get('game_length')}")

    # --- les augments existent-ils ? ---
    print("\n--- AUGMENTS ---")
    aug = chercher_augments(m)
    if aug:
        for c, v in aug[:5]:
            apercu = v if not isinstance(v, list) else f"{len(v)} éléments : {v[:4]}"
            print(f"  TROUVÉ  {c}")
            print(f"          {apercu}")
    else:
        print("  ABSENTS de cette partie. Deux causes possibles :")
        print("    - le champ a un autre nom que prévu (cherché : tout ce qui")
        print("      contient « augment »)")
        print("    - ils ne sont pas exposés pour ce mode de jeu")
        print("  Dans ce cas, l'analyse portera sur les unités, objets, traits,")
        print("  niveaux et économie — ce qui suffit largement pour commencer.")

    # --- structure d'un participant ---
    print("\n--- CHAMPS D'UN PARTICIPANT ---")
    p = info.get("participants", [{}])[0]
    for c, t, ex in arbre(p, max_prof=2):
        print(f"  {c:38s} {t:10s} {ex}")

    # --- cohérence sur l'ensemble du lot ---
    print("\n--- COHÉRENCE SUR LES", len(fichiers), "PARTIES ---")
    sets_, versions, modes, champs = collections.Counter(), collections.Counter(), \
                                     collections.Counter(), collections.Counter()
    avec_aug = 0
    for f in fichiers:
        try:
            d = json.load(open(f, encoding="utf-8"))
        except Exception:
            continue
        i = d.get("info", {})
        sets_[i.get("tft_set_number")] += 1
        versions[(i.get("game_version") or "?").split("<")[0][:24]] += 1
        modes[i.get("tft_game_type")] += 1
        for pa in i.get("participants", []):
            champs.update(pa.keys())
            if any("augment" in k.lower() for k in pa):
                avec_aug += 1
            break
    print(f"  sets      : {dict(sets_)}")
    print(f"  modes     : {dict(modes)}")
    print(f"  versions  : {len(versions)} distinctes — {', '.join(list(versions)[:4])}")
    print(f"  parties avec augments : {avec_aug}/{len(fichiers)}")
    print(f"\n  champs présents sur tous les participants :")
    print(f"    {', '.join(sorted(champs))}")

    print("\n>>> Envoie TOUT ce qui précède à Claude. C'est court, et ça lui")
    print(">>> permet d'écrire l'analyse contre la vraie structure.")


if __name__ == "__main__":
    main()
