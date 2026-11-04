#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LE MIROIR — analyse de tes propres parties
===========================================
L'idée centrale : **le lobby est le groupe de contrôle.**

Chaque partie contient les huit joueurs. Pas besoin de statistiques venues
d'ailleurs : pour chaque partie, on peut te classer parmi tes sept adversaires
sur le niveau atteint, l'or restant, les dégâts infligés, la survie. Et
comparer ce classement-là à ton placement réel.

C'est ce que ça révèle qui compte :

    tu es 2e du lobby en niveau mais 5e au classement
        -> tu obtiens les ressources, tu ne les convertis pas.
           Le travail est sur le board : positionnement, objets, composition.

    tu es 6e en niveau mais 3e au classement
        -> tu joues au-dessus de tes ressources.
           Le travail est sur l'économie et le tempo.

Aucune donnée externe, aucun site tiers, aucune hypothèse sur la méta.
Ton elo exact, tes adversaires réels, tes parties.

UTILISATION
-----------
    python3 miroir.py                    toutes les parties
    python3 miroir.py --joueur Itario    si ton nom diffère
    python3 miroir.py --depuis 2026-10-01
    python3 miroir.py --csv sortie.csv   pour creuser ailleurs

Écrit aussi miroir_resume.json, à envoyer à Claude pour l'interprétation.
"""

import json, os, sys, glob, argparse, statistics as st
from collections import Counter, defaultdict
from datetime import datetime, timezone

RACINE  = os.path.dirname(os.path.abspath(__file__))
DOSSIER = os.path.join(RACINE, "parties")


# ------------------------------------------------------------------ lecture

def numero_set(info):
    """
    Le numéro de set, par ordre de fiabilité décroissante des champs.

    Indispensable : une récolte de 200 parties remonte loin. Celle du 02/11
    couvrait 80 parties du Set 16 et 120 du Set 18 — moyenner les deux produit
    un chiffre qui ne décrit aucun des deux. On filtre, toujours.
    """
    n = info.get("tft_set_number")
    if isinstance(n, int):
        return n
    nom = str(info.get("tft_set_core_name") or "")
    chiffres = "".join(c for c in nom if c.isdigit())
    return int(chiffres) if chiffres else None


def charger(depuis=None, jeu_set=None):
    parties = []
    for f in sorted(glob.glob(os.path.join(DOSSIER, "*.json"))):
        try:
            d = json.load(open(f, encoding="utf-8"))
        except Exception:
            continue
        info = d.get("info") or {}
        if not info.get("participants"):
            continue
        s = numero_set(info)
        info["_set"] = s
        if jeu_set is not None and s != jeu_set:
            continue
        ts = info.get("game_datetime")
        if ts:
            dt = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
            if depuis and dt.date().isoformat() < depuis:
                continue
            info["_date"] = dt.date().isoformat()
        parties.append(info)
    return parties


def trouver_moi(parties, nom=None):
    """Le joueur présent dans TOUTES les parties, c'est forcément lui."""
    if nom:
        for info in parties:
            for p in info["participants"]:
                if (p.get("riotIdGameName") or "").lower() == nom.lower():
                    return p["puuid"]
    compte = Counter()
    for info in parties:
        for p in info["participants"]:
            if p.get("puuid"):
                compte[p["puuid"]] += 1
    if not compte:
        sys.exit("Aucun joueur identifiable dans ces parties.")
    puuid, n = compte.most_common(1)[0]
    if n < len(parties):
        print(f"  (le joueur le plus fréquent apparaît dans {n}/{len(parties)} parties)")
    return puuid


# ------------------------------------------------------------------ mesures

def rang_dans_lobby(participants, moi, cle, plus_haut_est_mieux=True):
    """Son rang de 1 à 8 parmi les huit joueurs, sur une dimension donnée."""
    vals = [(p.get(cle), p.get("puuid")) for p in participants if p.get(cle) is not None]
    if len(vals) < 4 or moi not in [v[1] for v in vals]:
        return None
    vals.sort(key=lambda x: x[0], reverse=plus_haut_est_mieux)
    for i, (_, pu) in enumerate(vals, 1):
        if pu == moi:
            return i
    return None


def carries(p):
    """Les unités portant 2 objets ou plus : ce sont les choix qui engagent."""
    out = []
    for u in p.get("units", []):
        noms = u.get("itemNames") or []
        if len(noms) >= 2:
            out.append((u.get("character_id") or u.get("name") or "?",
                        u.get("tier", 0), tuple(noms)))
    return out


def traits_actifs(p):
    return [t.get("name") for t in p.get("traits", [])
            if (t.get("tier_current") or 0) >= 1]


def augments_de(p):
    for k in p:
        if "augment" in k.lower():
            v = p[k]
            if isinstance(v, list):
                return [str(x) for x in v]
    return []


def joli(nom):
    """TFT14_Ivern -> Ivern ; Set18_Blossom -> Blossom"""
    s = str(nom)
    for sep in ("_",):
        if sep in s:
            s = s.split(sep)[-1]
    return s


# -------------------------------------------------------- parties lâchées

def est_abandon(x):
    """
    Une partie lâchée en cours de route n'est pas une partie mal jouée : elle
    ne doit pas entrer dans une mesure de niveau.

    Signature, découverte le 02/11 sur les 120 parties du Set 18 : qui lâche
    arrête de dépenser son or et arrête de monter de niveau, tout en continuant
    d'encaisser les revenus. L'or restant médian était de 0 à 4 à tous les
    placements SAUF la 8e place, où il montait à 33,5 — avec deux parties à
    152 et 115 or, impossibles en jouant.

    C'est la CONJONCTION qui trahit : garder de l'or en gagnant est banal
    (une 2e place à 37 or, niveau 9, tour 41, était une vraie partie), et mal
    finir sans or est une vraie défaite. Les deux ensemble, non.
    """
    o = x.get("or_restant") or 0
    p = x.get("placement") or 0
    return o >= 20 and p >= 5


def est_limite(x):
    """Zone grise : signalée, jamais retirée d'office."""
    o = x.get("or_restant") or 0
    p = x.get("placement") or 0
    return not est_abandon(x) and o >= 10 and p >= 6


# ------------------------------------------------------------------ analyse

def analyser(parties, moi):
    lignes = []
    for info in parties:
        parts = info["participants"]
        p = next((x for x in parts if x.get("puuid") == moi), None)
        if not p:
            continue
        lignes.append({
            "date": info.get("_date"),
            "version": (info.get("game_version") or "?").split("<")[0][:20],
            "placement": p.get("placement"),
            "niveau": p.get("level"),
            "or_restant": p.get("gold_left"),
            "degats": p.get("total_damage_to_players"),
            "dernier_tour": p.get("last_round"),
            "elimines": p.get("players_eliminated"),
            "rang_niveau":  rang_dans_lobby(parts, moi, "level"),
            "rang_degats":  rang_dans_lobby(parts, moi, "total_damage_to_players"),
            "rang_or":      rang_dans_lobby(parts, moi, "gold_left"),
            "traits":   traits_actifs(p),
            "carries":  carries(p),
            "augments": augments_de(p),
        })
    return lignes


def rapport(L):
    n = len(L)
    if not n:
        sys.exit("Aucune partie exploitable.")
    pl = [x["placement"] for x in L if x["placement"]]
    moy = st.mean(pl)
    dist = Counter(pl)

    print(f"\n{'='*62}")
    print(f"  LE MIROIR — {n} parties")
    dates = sorted(x["date"] for x in L if x["date"])
    if dates:
        print(f"  du {dates[0]} au {dates[-1]}")
    print(f"{'='*62}")

    # --- distribution : la mesure qu'on n'avait jamais eue ---
    print(f"\nPLACEMENT MOYEN : {moy:.2f}      top 4 : "
          f"{100*sum(dist[i] for i in (1,2,3,4))/n:.1f} %      "
          f"1res : {100*dist[1]/n:.1f} %")
    print("\nTa distribution de placements :")
    for i in range(1, 9):
        c = dist.get(i, 0)
        pct = 100 * c / n
        barre = "#" * min(28, round(pct / 1.5))
        ecart = pct - 12.5
        print(f"  {i}e  {pct:5.1f} %  ({c:3d})  {barre:<28s} {ecart:+5.1f} pt vs 12,5 %")
    sd = st.pstdev(pl)
    print(f"\n  écart-type {sd:.2f}  "
          f"({'profil de pointe' if sd > 2.1 else 'profil régulier' if sd < 1.9 else 'profil mixte'})")

    # --- le coeur : ressources contre résultat ---
    print(f"\n{'-'*62}\nRESSOURCES CONTRE RÉSULTAT — ton rang dans le lobby\n{'-'*62}")
    for cle, label, sens in (("rang_niveau", "niveau atteint", "plus haut = mieux"),
                             ("rang_degats", "dégâts infligés", "plus haut = mieux")):
        v = [x[cle] for x in L if x[cle]]
        if not v:
            print(f"  {label:18s} : donnée absente")
            continue
        rmoy = st.mean(v)
        ecart = moy - rmoy
        print(f"\n  {label:18s} rang moyen {rmoy:.2f}  ·  placement moyen {moy:.2f}"
              f"  ·  écart {ecart:+.2f}")
        if ecart > 0.35:
            print(f"     -> tu es MIEUX classé en {label.split()[0]} qu'au scoreboard.")
            print(f"        Tu obtiens les ressources sans les convertir : le travail")
            print(f"        est sur le board (positionnement, objets, composition).")
        elif ecart < -0.35:
            print(f"     -> tu places MIEUX que tes ressources ne le laissent prévoir.")
            print(f"        Tu joues au-dessus de tes moyens : le travail est sur")
            print(f"        l'économie et le tempo, pas sur le combat.")
        else:
            print(f"     -> ressources et résultat alignés. Rien d'anormal ici.")

    # --- économie ---
    org = [x["or_restant"] for x in L if x["or_restant"] is not None]
    if org:
        gaspille = [x for x in L if (x["or_restant"] or 0) >= 20 and (x["placement"] or 9) >= 5]
        print(f"\n  or restant en fin de partie : médiane {st.median(org):.0f}")
        if gaspille:
            print(f"     {len(gaspille)} partie(s) perdues avec 20 or ou plus en poche"
                  f" ({100*len(gaspille)/n:.0f} %)")
            print(f"     — de l'or non dépensé dans une partie perdue est de l'or gâché.")

    # --- traits ---
    par_trait = defaultdict(list)
    for x in L:
        for t in set(x["traits"]):
            par_trait[t].append(x["placement"])
    solides = {t: v for t, v in par_trait.items() if len(v) >= max(5, n // 15)}
    if solides:
        print(f"\n{'-'*62}\nTES TRAITS — placement moyen quand tu les joues\n{'-'*62}")
        clas = sorted(solides.items(), key=lambda kv: st.mean(kv[1]))
        for t, v in clas[:6]:
            print(f"  {joli(t):22s} {st.mean(v):.2f}   ({len(v)} parties)")
        if len(clas) > 6:
            print("  ...")
            for t, v in clas[-3:]:
                print(f"  {joli(t):22s} {st.mean(v):.2f}   ({len(v)} parties)")

    # --- carries ---
    par_carry = defaultdict(list)
    for x in L:
        for nom, tier, _ in x["carries"]:
            par_carry[joli(nom)].append(x["placement"])
    solides_c = {c: v for c, v in par_carry.items() if len(v) >= max(4, n // 20)}
    if solides_c:
        print(f"\n{'-'*62}\nTES CARRIES (2 objets ou plus)\n{'-'*62}")
        for c, v in sorted(solides_c.items(), key=lambda kv: st.mean(kv[1]))[:8]:
            print(f"  {c:22s} {st.mean(v):.2f}   ({len(v)} parties)")

    # --- étoiles des carries ---
    etoiles = Counter()
    for x in L:
        for _, tier, _ in x["carries"]:
            etoiles[tier] += 1
    if etoiles:
        tot = sum(etoiles.values())
        print(f"\n  niveau d'étoiles de tes carries : "
              + " · ".join(f"{k}★ {100*v/tot:.0f} %" for k, v in sorted(etoiles.items())))

    # --- augments ---
    aug = [a for x in L for a in x["augments"]]
    print(f"\n{'-'*62}\nAUGMENTS\n{'-'*62}")
    if aug:
        par_aug = defaultdict(list)
        for x in L:
            for a in x["augments"]:
                par_aug[a].append(x["placement"])
        assez = {a: v for a, v in par_aug.items() if len(v) >= 4}
        print(f"  {len(aug)} choix sur {len(par_aug)} augments distincts.")
        print(f"  {len(assez)} seulement atteignent 4 parties.")
        print(f"\n  ATTENTION : avec {len(par_aug)} augments pour {len(aug)} choix, aucune")
        print(f"  conclusion augment par augment n'est fiable. Ce classement est")
        print(f"  indicatif, pas un verdict.")
        if assez:
            for a, v in sorted(assez.items(), key=lambda kv: st.mean(kv[1]))[:6]:
                print(f"    {joli(a):30s} {st.mean(v):.2f}  ({len(v)})")
    else:
        print("  Aucun augment dans les données. L'analyse ci-dessus n'en dépend pas.")

    return {
        "n_parties": n, "placement_moyen": round(moy, 3),
        "ecart_type": round(sd, 3),
        "distribution": {str(i): dist.get(i, 0) for i in range(1, 9)},
        "top4_pct": round(100 * sum(dist[i] for i in (1, 2, 3, 4)) / n, 1),
        "premieres_pct": round(100 * dist[1] / n, 1),
        "rang_niveau_moyen": round(st.mean([x["rang_niveau"] for x in L if x["rang_niveau"]]), 3)
                              if any(x["rang_niveau"] for x in L) else None,
        "rang_degats_moyen": round(st.mean([x["rang_degats"] for x in L if x["rang_degats"]]), 3)
                              if any(x["rang_degats"] for x in L) else None,
        "or_restant_median": st.median(org) if org else None,
        "augments_presents": bool(aug),
        "traits": {joli(t): [round(st.mean(v), 2), len(v)] for t, v in solides.items()},
        "carries": {c: [round(st.mean(v), 2), len(v)] for c, v in solides_c.items()},
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--joueur", default=None, help="nom en jeu, si la détection se trompe")
    ap.add_argument("--depuis", default=None, help="AAAA-MM-JJ")
    ap.add_argument("--csv", default=None, help="exporter le détail partie par partie")
    ap.add_argument("--set", default=None, dest="jeu_set",
                    help="n'analyser qu'un set : un numéro (--set 18) ou "
                         "« auto » pour celui de la partie la plus récente. "
                         "À UTILISER TOUJOURS : une récolte couvre souvent "
                         "deux sets, et les moyenner ne décrit ni l'un ni l'autre. "
                         "« auto » survit au changement de set sans rien réécrire.")
    ap.add_argument("--sortie", default="miroir_resume.json",
                    help="nom du fichier de résumé")
    ap.add_argument("--garder-tout", action="store_true", dest="garder_tout",
                    help="ne retirer aucune partie lâchée (pour vérifier le seuil)")
    a = ap.parse_args()

    if not os.path.isdir(DOSSIER):
        sys.exit(f"Dossier {DOSSIER} introuvable. Lance d'abord collecte.py.")

    # Répartition par set, affichée avant toute mesure : c'est le garde-fou
    # contre la moyenne à cheval sur deux sets.
    tous = charger(a.depuis)
    repartition = Counter(p.get("_set") for p in tous)
    print("parties par set : " + ", ".join(
        f"set {k} : {v}" for k, v in sorted(repartition.items(),
                                            key=lambda kv: (kv[0] is None, kv[0]))))
    # « auto » : le set de la partie la plus récente. C'est ce qu'on veut
    # neuf fois sur dix, et surtout ça survit au passage d'un set au suivant
    # sans qu'on ait à éditer le script ou le .bat qui l'appelle.
    if str(a.jeu_set).lower() == "auto":
        recentes = sorted((p for p in tous if p.get("_set") is not None),
                          key=lambda p: p.get("game_datetime") or 0)
        if not recentes:
            sys.exit("Impossible de déterminer le set : aucune partie n'en porte un.")
        a.jeu_set = recentes[-1]["_set"]
        print(f"  --set auto -> set {a.jeu_set} (celui de la partie la plus récente)")
    elif a.jeu_set is not None:
        a.jeu_set = int(a.jeu_set)

    if a.jeu_set is None and len(repartition) > 1:
        print("  ! plusieurs sets présents et aucun filtre : les moyennes qui")
        print("    suivent sont à cheval. Relance avec --set auto.")

    parties = charger(a.depuis, a.jeu_set)
    if not parties:
        sys.exit("Aucune partie trouvée. Lance collecte.py, ou élargis --depuis/--set.")
    if a.jeu_set is not None:
        print(f"analyse restreinte au set {a.jeu_set} : {len(parties)} parties\n")

    moi = trouver_moi(parties, a.joueur)
    L = analyser(parties, moi)

    laches  = [x for x in L if est_abandon(x)]
    limites = [x for x in L if est_limite(x)]
    if laches or limites:
        print(f"--- parties lâchées : {len(laches)} retirées, "
              f"{len(limites)} en zone grise (gardées) ---")
        for x in sorted(laches + limites, key=lambda y: -(y.get("or_restant") or 0)):
            marque = "RETIRÉE" if est_abandon(x) else "gardée "
            print(f"  {marque}  {x['date']}  {x['placement']}e  "
                  f"niv {x['niveau']}  {x.get('or_restant')} or")
        print()
    if a.garder_tout:
        laches = []
        print("--- --garder-tout : aucune partie retirée ---\n")
    else:
        L = [x for x in L if not est_abandon(x)]
        if not L:
            sys.exit("Toutes les parties ont été classées comme lâchées : "
                     "le seuil est sûrement mauvais, relance avec --garder-tout.")

    resume = rapport(L)
    resume["set"] = a.jeu_set
    resume["parties_lachees_retirees"] = [
        {"date": x["date"], "placement": x["placement"],
         "niveau": x["niveau"], "or_restant": x.get("or_restant")} for x in laches]
    resume["parties_zone_grise"] = [
        {"date": x["date"], "placement": x["placement"],
         "niveau": x["niveau"], "or_restant": x.get("or_restant")} for x in limites]
    resume["repartition_sets"] = {str(k): v for k, v in repartition.items()}

    with open(os.path.join(RACINE, a.sortie), "w", encoding="utf-8") as f:
        json.dump(resume, f, ensure_ascii=False, indent=1)
    print(f"\n{'='*62}")
    print(f"  Résumé écrit dans {a.sortie} — envoie-le à Claude.")

    if a.csv:
        import csv
        with open(a.csv, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            # ⚠ `objets` a été ajoutée le 04/11, et elle corrige une perte.
            #
            # carries() LISAIT `itemNames` depuis le premier jour et les
            # gardait en troisième position de chaque tuple — puis cette
            # ligne n'écrivait que c[0], le nom de l'unité. La donnée était
            # collectée chez Riot et jetée à la frontière du fichier.
            #
            # Format : « unité:étoiles>objet1,objet2,objet3 », séparés par |.
            # Identifiants BRUTS, pas joli() : c'est ce qui permet de joindre
            # ses builds à data/recettes.json et au BiS du relevé sans
            # correspondance de noms approximative.
            w.writerow(["date","version","placement","niveau","or_restant","degats",
                        "dernier_tour","rang_niveau","rang_degats","traits","carries",
                        "objets"])
            for x in L:
                w.writerow([x["date"], x["version"], x["placement"], x["niveau"],
                            x["or_restant"], x["degats"], x["dernier_tour"],
                            x["rang_niveau"], x["rang_degats"],
                            "|".join(joli(t) for t in x["traits"]),
                            "|".join(joli(c[0]) for c in x["carries"]),
                            "|".join(f"{c[0]}:{c[1]}>{','.join(c[2])}"
                                     for c in x["carries"])])
        print(f"  Détail partie par partie : {a.csv}")


if __name__ == "__main__":
    main()
