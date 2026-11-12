#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CONSTRUCTEUR DU SITE — data/ -> data/meta/courant.json
=======================================================
Le site ne contient AUCUNE donnée en dur. Il lit `data/meta/courant.json`,
que ce script produit à partir des relevés.

    python3 tools/build/build_site.py

─── CE QUI A CHANGÉ LE 10/11, ET POURQUOI ─────────────────────────────────
Jusque-là ce script lisait `data/releves/` : la série MetaTFT, saisie à la
main au navigateur. Son dernier relevé datait du 23 octobre (18.5b) pendant
que la série automatique en était à 18.6 mûr — le bandeau du site avait donc
deux patchs de retard, et personne ne le voyait parce que rien ne plantait.

La répétition générale du 1er décembre (tools/tests/repetition.py) a montré
la suite : au soir du changement de set, le relevé automatique passe au
Set 19, et le site reste sur « Set 18 · 18.5b · 23/10 » jusqu'à ce que
quelqu'un ouvre un navigateur pour saisir un relevé. Le jour exact où le site
doit servir.

Désormais TOUT vient de la série automatique :

    data/releves-tt/   le relevé d'unités, de traits et d'objets
    data/compos.json   les compos, avec leur LP par partie
    data/recettes.json les composants de chaque objet

La série manuelle reste dans le dépôt comme archive du Set 18. Elle ne porte
plus rien.

─── LES FICHES DE LIGNE ───────────────────────────────────────────────────
Chaque compo relevée devient une FICHE : ce qu'on prépare AVANT de lancer une
partie. Porteurs, niveau auquel on la joue, objets à viser et composants à
ramasser, ce qui la fait gagner. Les fiches sont statiques et identiques pour
tout le monde : elles ne prennent aucune entrée sur la partie en cours. C'est
la limite que fixe la politique de Riot pour les outils TFT (pas de
recommandation fondée sur l'état d'une partie), et c'est aussi la bonne
façon de travailler — on choisit ses lignes avant, pas pendant.
"""

import json, os, shutil, sys
from collections import Counter
from datetime import date

# Le socle de mesure est partagé avec carnet.py : une seule implémentation.
sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import mesures as M

RACINE  = M.DEPOT
SORTIE  = os.path.join(RACINE, "data", "meta", "courant.json")
SCHEMA  = 2            # 2 : série automatique, fiches de ligne, manifeste
TROIS_ETOILES = 0.5    # part des plateaux où un porteur est en trois étoiles
                       # au-delà de laquelle la ligne est une « compo trois
                       # étoiles » : c'est alors ce qu'on y fait le plus souvent
PORTEUR = 1.0          # nombre moyen d'objets à partir duquel une unité
                       # PORTE la ligne (en dessous, c'est une unité d'appoint)

# Champs internes au socle : utiles aux outils, inutiles au site.
_INTERNES = ("rangs_avant", "rangs_apres", "unites_avant", "unites_apres",
             "spearman_exact")


def charger(nom):
    try:
        return json.load(open(os.path.join(RACINE, "data", nom), encoding="utf-8"))
    except Exception:
        return None


# ══ LES NOMS ET LES COÛTS ════════════════════════════════════════════════
# data/jeu.json (tools/releve/jeu.py) porte les noms français, les coûts et
# les traits, lus dans les données de Riot. Il ne sert que s'il est du set du
# relevé ; sinon — premier jour d'un set, source en retard — on retombe sur
# le nom déduit de l'identifiant, et le site s'affiche quand même.
JEU = {"unites": {}, "traits": {}, "objets": {}, "par_champion": {}}


def brancher_jeu(setn):
    j = charger("jeu.json")
    if not j or j.get("set") != setn:
        return j
    JEU["unites"] = j.get("unites") or {}
    JEU["traits"] = j.get("traits") or {}
    JEU["objets"] = j.get("objets") or {}
    # Le relevé éclate certaines unités en variantes (Lux en dix entrées) que
    # les données du jeu ne connaissent que sous un nom : repli par champion.
    JEU["par_champion"] = {M.champion(k): v for k, v in JEU["unites"].items()}
    return j


def nommer(ident):
    """Le nom à afficher : celui des données du jeu, sinon celui qu'on déduit
    de l'identifiant. UNE définition, servie au site dans `noms`."""
    if ident in JEU["unites"]:
        return JEU["unites"][ident]["nom"]
    if ident in JEU["traits"]:
        return JEU["traits"][ident]["nom"]
    if ident in JEU["objets"]:
        return JEU["objets"][ident]
    deduit = M.nom_affichable(ident)
    u = JEU["par_champion"].get(M.champion(ident))
    if u:                                 # variante : nom du jeu + (variante)
        return u["nom"] + (" " + deduit[deduit.index("("):] if "(" in deduit else "")
    return deduit


def cout(ident):
    u = JEU["unites"].get(ident) or JEU["par_champion"].get(M.champion(ident))
    return u.get("cout") if u else None


def a_venir(j):
    """Le set qui arrive, tel que le PBE le montre : unités par coût, traits
    et paliers. Des faits de composition, aucune force."""
    a = (j or {}).get("a_venir")
    if not a:
        return None
    U, T = a.get("unites") or {}, a.get("traits") or {}
    nom_trait = lambda t: (T.get(t) or {}).get("nom") or t
    par_cout = {}
    for u in U.values():
        par_cout.setdefault(u["cout"], []).append(
            {"nom": u["nom"], "traits": [nom_trait(t) for t in u.get("traits") or []]})
    porteurs = {}
    for u in U.values():
        for t in u.get("traits") or []:
            porteurs.setdefault(t, []).append((u["cout"], u["nom"]))
    return {
        "set": a.get("set"), "nom": a.get("nom"),
        "vu_la_premiere_fois": a.get("vu_la_premiere_fois"),
        "releve_le": a.get("releve_le"), "note": a.get("note"),
        "n_unites": len(U), "n_traits": len(T),
        "par_cout": [{"cout": c, "unites": sorted(par_cout[c], key=lambda x: x["nom"])}
                     for c in sorted(par_cout)],
        "traits": sorted(
            ({"nom": v.get("nom") or k, "paliers": v.get("paliers") or [],
              "unites": [n for _, n in sorted(porteurs.get(k, []))]}
             for k, v in T.items() if porteurs.get(k)),
            key=lambda x: (-len(x["unites"]), x["nom"])),
    }


def diff(avant, apres):
    d = M.comparer(avant, apres)
    if d is None:
        return None
    d = {k: v for k, v in d.items() if k not in _INTERNES}
    for cle in ("montees", "chutes"):
        d[cle] = [{**x, "id": x["nom"], "nom": nommer(x["nom"])}
                  for x in d[cle][:5]]
    for cle in ("entres_top8", "sortis_top8"):
        d[cle] = [nommer(x) for x in d[cle]]
    d["volume"]["unites_perdues"] = [nommer(x)
                                     for x in d["volume"]["unites_perdues"]]
    d["volume"]["unites_gagnees"] = [nommer(x)
                                     for x in d["volume"]["unites_gagnees"]]
    return d


# ══ LA ROUTINE DE PATCH : CE QUE LE PATCH CHANGE POUR SES LIGNES ═════════
#
# Le bloc « rotation » dit ce qui bouge sur tout le ladder : 74 unités, dont
# la plupart qu'il ne joue jamais. La question qu'il se pose le jour d'un
# patch est plus étroite — c'est la « routine de patch » du livre 2 : « mes
# lignes ont-elles bougé, et dois-je changer quelque chose ? ».
#
# Pour chacune de ses lignes régulières : son placement sur le ladder avant et
# après, et si l'écart sort du bruit. Le seuil est calculé, pas choisi :
# l'écart-type d'un placement sur huit places vaut ~2.29, donc deux moyennes
# sur na et nb parties diffèrent par hasard de 2 × 2.29 × √(1/na + 1/nb) au
# plus, 19 fois sur 20. À 30 000 parties de chaque côté, ~0.04 place ; à
# 3 000, ~0.12. Un patch frais ne tranche donc presque rien, et le bloc le dit.
#
# ⚠ MAIS À 400 000 PARTIES, TOUT SORT DU BRUIT. Premier essai, 18.5c -> 18.6 :
# Aphelios « tombe » de 0.04 place, avec un seuil à 0.027. Vrai, et sans
# aucune importance. Un écart réel n'est pas un écart qui compte : le verdict
# demande AUSSI que l'écart pèse au moins 1.5 LP par partie à son barème
# (−15.4 LP par place, soit ~0.1 place). Les deux seuils sont affichés.

ECART_TYPE_PLACEMENT = 2.29
LP_QUI_COMPTE = 1.5          # LP par partie en deçà desquels on ne change rien
PENTE_PAR_DEFAUT = -15.4     # LP par place, si joueur.json n'est pas du set


def _par_champion(releve):
    """Les variantes d'un même champion (Lux en dix entrées) réunies, pondérées
    par leur volume. Le BiS est celui de la variante la plus jouée."""
    out = {}
    for ident, v in (releve.get("unites") or {}).items():
        c = M.champion(ident)
        if not c or not v.get("n"):
            continue
        e = out.setdefault(c, {"n": 0, "somme": 0.0, "ident": ident, "n_max": 0})
        e["n"] += v["n"]
        e["somme"] += v["n"] * v["avg"]
        if v["n"] > e["n_max"]:
            e.update(n_max=v["n"], ident=ident, objets=(v.get("objets") or [])[:3])
    for e in out.values():
        e["avg"] = e["somme"] / e["n"]
    classes = sorted((c for c, e in out.items() if e["n"] >= M.NMIN),
                     key=lambda c: out[c]["avg"])
    for i, c in enumerate(classes):
        out[c]["rang"] = i + 1
    return out, len(classes)


def ses_lignes_au_patch(avant, apres, miroir, setn, d):
    if not (avant and apres and miroir):
        return None
    if not (avant.get("set") == apres.get("set") == miroir.get("set") == setn):
        return None
    jouees = M.unites_jouees(miroir)
    regulieres = [c for c, s in jouees.items() if s == "regulier"]
    if not regulieres:
        return None
    A, na = _par_champion(avant)
    B, nb = _par_champion(apres)
    jo = charger("joueur.json") or {}
    pente = (((jo.get("bareme_lp") or {}).get("droite") or {}).get("pente_lp_par_place")
             if jo.get("set") == setn else None) or PENTE_PAR_DEFAUT
    lignes = []
    for c in regulieres:
        a, b = A.get(c), B.get(c)
        base = (b or a or {}).get("ident")
        nom = nommer(base).split(" (")[0] if base else c
        if not (a and b):
            lignes.append({"champion": c, "nom": nom, "verdict": "absente",
                           "detail": "absente d'un des deux relevés"})
            continue
        delta = b["avg"] - a["avg"]
        seuil = 2 * ECART_TYPE_PLACEMENT * (1 / a["n"] + 1 / b["n"]) ** 0.5
        lp = -delta * abs(pente)      # placement qui baisse = LP gagnés
        reel = abs(delta) > seuil
        compte = abs(lp) >= LP_QUI_COMPTE
        bis_a = [nommer(x) for x in a.get("objets") or []]
        bis_b = [nommer(x) for x in b.get("objets") or []]
        lignes.append({
            "champion": c, "nom": nom,
            "avg_avant": round(a["avg"], 2), "avg_apres": round(b["avg"], 2),
            "n_avant": a["n"], "n_apres": b["n"],
            # Un placement qui BAISSE est un progrès : 4.10 vaut mieux que 4.30.
            "delta": round(delta, 3), "seuil": round(seuil, 3),
            "lp_par_partie": round(lp, 1),
            "verdict": ("stable" if not (reel and compte)
                        else "monte" if delta < 0 else "tombe"),
            "detail": (None if (reel and compte) else
                       "dans le bruit" if not reel else
                       f"réel, mais moins de {LP_QUI_COMPTE} LP par partie"),
            "rang_avant": a.get("rang"), "rang_apres": b.get("rang"),
            "bis_avant": bis_a, "bis_apres": bis_b,
            # Le relevé donne les objets dans l'ordre de fréquence, sans les
            # fréquences : un 3ᵉ et un 4ᵉ à égalité permutent par hasard. On ne
            # signale donc qu'un vrai déplacement — un objet des DEUX premiers
            # qui n'était pas dans les trois premiers de l'autre relevé.
            "bis_entre": [x for x in bis_b[:2] if x not in bis_a] if (bis_a and bis_b) else [],
            "bis_sort": [x for x in bis_a[:2] if x not in bis_b] if (bis_a and bis_b) else [],
        })
    ordre = {"tombe": 0, "monte": 1, "stable": 2, "absente": 3}
    for x in lignes:
        x["bis_change"] = bool(x.get("bis_entre") or x.get("bis_sort"))
    lignes.sort(key=lambda x: (ordre[x["verdict"]], -abs(x.get("delta") or 0)))
    n_bouge = sum(1 for x in lignes if x["verdict"] in ("monte", "tombe"))
    comparable = (d or {}).get("volume", {}).get("comparable", True)
    return {
        "de": avant.get("patch"), "a": apres.get("patch"),
        "set": setn,
        "n_classes": {"avant": na, "apres": nb},
        "volumes": {"avant": avant.get("n_parties"), "apres": apres.get("n_parties")},
        "comparable": comparable,
        "lignes": lignes,
        "n_bouge": n_bouge,
        "pente_lp_par_place": pente,
        "lp_qui_compte": LP_QUI_COMPTE,
        "lecture": (
            f"Aucune de tes {len(lignes)} lignes n'a bougé assez pour compter "
            f"(au moins {LP_QUI_COMPTE} LP par partie, au-delà du hasard) : rien "
            "à changer à ton répertoire pour ce patch."
            if n_bouge == 0 else
            f"{n_bouge} de tes {len(lignes)} lignes ont bougé assez pour compter. "
            "Une ligne qui tombe n'est pas à abandonner : c'est à revoir dans "
            "la fiche, et à ne plus forcer."),
        "reserve": None if comparable else (
            "Le patch vient de sortir : les volumes des deux relevés sont trop "
            "inégaux pour que ces verdicts tiennent. Ils se stabilisent à "
            "mesure que le relevé mûrit, dans les jours qui suivent."),
    }


# ══ LES FICHES ═══════════════════════════════════════════════════════════

def fiche(c, total, recettes, composants_fr):
    """Une compo relevée -> une fiche de ligne. Rien n'est inventé : chaque
    champ est une lecture directe de compos.json ou de recettes.json."""
    n = c.get("n") or 0
    nom = nommer

    # Le plateau : la source donne une entrée par (unité, étoiles). On garde,
    # par unité, sa présence totale et la répartition de ses étoiles.
    par_unite = {}
    for u in (c.get("unites") or []):
        if not (isinstance(u, list) and len(u) >= 3):
            continue
        e = par_unite.setdefault(u[0], {"n": 0, "etoiles": Counter()})
        e["n"] += u[2] or 0
        e["etoiles"][u[1]] += u[2] or 0

    def part_3(ident):
        e = par_unite.get(ident)
        return round(e["etoiles"][3] / e["n"], 2) if (e and e["n"]) else None

    # Un porteur est une unité qui porte des objets : `objets_moy` est le
    # nombre moyen d'objets sur elle (voir compos.py pour la façon dont ce
    # champ a été mal lu jusqu'au 10/11). Les étoiles, elles, se lisent dans
    # `unites`, et nulle part ailleurs.
    def objets_moy(p):
        return p.get("objets_moy", p.get("etoiles_moy")) or 0
    porteurs = [{"id": p["unite"], "nom": nom(p["unite"]),
                 "objets_moy": objets_moy(p), "cout": cout(p["unite"]),
                 "part_trois_etoiles": part_3(p["unite"]),
                 "trois_etoiles": (part_3(p["unite"]) or 0) >= TROIS_ETOILES}
                for p in (c.get("porteurs") or [])
                if objets_moy(p) >= PORTEUR]
    plateau = sorted(
        ({"id": k, "nom": nom(k), "cout": cout(k),
          "part": round(min(1.0, v["n"] / n), 2) if n else None,
          "etoiles": v["etoiles"].most_common(1)[0][0]}
         for k, v in par_unite.items()),
        key=lambda x: -(x["part"] or 0))

    # Les objets, par porteur, avec leur recette : c'est elle qui transforme
    # « tel objet » en « tels composants à ramasser ».
    ids_porteurs = [p["id"] for p in porteurs]
    objets, besoins = {}, Counter()
    for o in (c.get("objets_par_unite") or []):
        if o.get("unite") not in ids_porteurs:
            continue
        r = recettes.get(o.get("objet")) or {}
        de = [composants_fr.get(x, nom(x)) for x in r.get("de", [])]
        liste = objets.setdefault(o["unite"], [])
        if len(liste) >= 3:
            continue                      # trois objets par unité, pas plus
        liste.append({"id": o["objet"],
                      "nom": JEU["objets"].get(o["objet"]) or r.get("nom") or nom(o["objet"]),
                      "composants": de, "n": o.get("n"), "place": o.get("place")})
        for x in de:
            besoins[x] += 1

    def cond(w):
        us = []
        for u in (w.get("unites") or []):
            ident, _, et = str(u).rpartition("-")
            us.append({"nom": nom(ident or u), "etoiles": int(et) if et.isdigit() else None})
        return {"unites": us, "n": w.get("n"), "place": w.get("place")}

    niv_tot = sum(x.get("n") or 0 for x in (c.get("niveaux") or []))
    niveaux = sorted(({"niveau": x["niveau"],
                       "part": round((x.get("n") or 0) / niv_tot, 2) if niv_tot else None}
                      for x in (c.get("niveaux") or [])),
                     key=lambda x: -(x["part"] or 0))

    dist = c.get("distribution") or []
    sd = sum(dist)
    trois = [p for p in porteurs if p["trois_etoiles"]]
    traits = [{"nom": nom(t["trait"]), "palier": t.get("palier"),
               "part": round(min(1.0, (t.get("n") or 0) / n), 2) if n else None}
              for t in (c.get("traits") or [])]

    titre = " · ".join(x for x in (
        traits[0]["nom"] if traits else None,
        porteurs[0]["nom"] if porteurs else None) if x)

    return {
        "code": c.get("code"),
        "nom": titre or "Compo sans nom",
        "n": n,
        # `total` compte des PLATEAUX (une partie = huit plateaux) : le pick
        # d'un 4-coûts populaire y vaut ~10 %, ce qui n'a de sens qu'ainsi.
        # 8 × la part des plateaux = le nombre moyen de joueurs par lobby.
        "par_lobby": round(8 * n / total, 2) if total else None,
        "place": c.get("place"), "top4": c.get("top4_pct"),
        "premieres": c.get("premieres_pct"), "lp": c.get("lp_par_partie"),
        "bas_pct": round(100 * sum(dist[6:8]) / sd, 1) if (sd and len(dist) >= 8) else None,
        "type": "trois_etoiles" if trois else "niveau",
        "type_libelle": (
            "compo trois étoiles sur " + ", ".join(
                p["nom"] + (f" ({p['cout']}-coût)" if p.get("cout") else "") for p in trois)
            if trois else
            f"montée de niveau (jouée au niveau {niveaux[0]['niveau']})"
            if niveaux else "montée de niveau"),
        "niveaux": niveaux[:3],
        "porteurs": porteurs,
        "plateau": plateau,
        "objets": objets,
        "composants": [{"composant": k, "fois": v} for k, v in besoins.most_common()],
        "victoire": [cond(w) for w in (c.get("conditions_de_victoire") or [])
                     if (w.get("n") or 0) >= 300][:3],
        "traits": traits[:6],
        "variantes": [{"unites": [nom(u) for u in (v.get("unites") or [])],
                       "n": v.get("n"), "place": v.get("place")}
                      for v in (c.get("variantes") or [])[:3]],
    }


def modes(fiches):
    """Le même jeu de fiches, classé selon trois enjeux différents."""
    def tri(cle, decroissant):
        src = [f for f in fiches if f.get(cle) is not None]
        return [f["code"] for f in sorted(src, key=lambda f: f[cle],
                                          reverse=decroissant)]
    return {
        "ladder": {
            "critere": "LP gagné par partie", "cle": "lp", "unite": " LP",
            "pourquoi": "L'objectif est un classement, et le classement se "
                        "compte en LP : c'est la mesure directe, là où le "
                        "placement moyen n'en est qu'une approximation.",
            "classement": tri("lp", True)},
        "cumule": {
            "critere": "taux de top 4", "cle": "top4", "unite": " %",
            "pourquoi": "Chaque bas de tableau coûte directement des points "
                        "sur le cumul. La régularité prime sur le coup d'éclat.",
            "classement": tri("top4", True)},
        "checkmate": {
            "critere": "taux de 1re place", "cle": "premieres", "unite": " %",
            "pourquoi": "Seule la 1re place qualifie. Une 7e ne coûte rien de "
                        "plus qu'une 5e, donc le placement moyen ne veut plus "
                        "rien dire.",
            "classement": tri("premieres", True)},
    }


# ══ LE MANIFESTE ═════════════════════════════════════════════════════════

ATTENDUS = ("profil.json", "calendrier.json", "miroir.json", "jeu.json",
            "focus.json", "barre.json", "joueur.json",
            "objets.json", "recettes.json",
            "compos.json", "compos_lui.json",
            "fuites.json", "contestation.json")


def manifeste(set_courant):
    """Pour chaque fichier publié : de quel set il parle, et dans quel état.

    Le site s'en sert pour décider, bloc par bloc, s'il affiche, s'il étiquette
    « archive du Set N », ou s'il explique pourquoi le bloc est vide. Sans ça
    il n'avait que deux états — présent ou absent — et ne distinguait pas
    « rien à signaler » de « pas de données » de « données d'un autre set »."""
    out = {}
    for f in ATTENDUS:
        d = charger(f)
        if d is None:
            out[f] = {"present": False}
            continue
        s = d.get("set")
        out[f] = {"present": True, "set": s,
                  "du_set_courant": (s == set_courant) if s is not None else None,
                  "etat": d.get("etat"),
                  "date": d.get("genere_le") or d.get("date")}
    return out


def main():
    rs = M.serie()
    if not rs:
        sys.exit(f"Aucun relevé dans {M.RELEVES_TT} — lance tools/releve/tactics.py.")
    courant = rs[-1]
    setn = courant.get("set")
    du_set = [r for r in rs if r.get("set") == setn]
    jeu = brancher_jeu(setn)
    print(f"relevé courant : {courant['date']} (Set {setn}, {courant.get('patch')}, "
          f"{courant.get('rang')}, {courant.get('n_parties'):,} parties)".replace(",", " "))

    # ── La rotation : le patch précédent DU MÊME SET, à même tranche ─────
    d, d_raison, paire = None, None, (None, None)
    if len(du_set) < 2:
        d_raison = (f"Premier patch relevé du Set {setn} : il n'y a pas encore "
                    "de patch précédent auquel le comparer.")
    else:
        for i in range(len(du_set) - 1, 0, -1):
            cand = diff(du_set[i - 1], du_set[i])
            if cand and cand["meme_elo"]:
                d = cand
                paire = (du_set[i - 1], du_set[i])
                break
        if d is None:
            d_raison = ("Aucune paire de relevés comparables dans ce set "
                        "(tranches de rang différentes ou aucune unité commune).")

    g, u = M.classement(courant)
    ordre = sorted(g, key=lambda k: g[k])
    tete = M.tete_stable(du_set) if len(du_set) >= 2 else None
    if tete:
        tete = {**tete, "unites": [{"id": k, "nom": nommer(k)}
                                   for k in tete["unites"]],
                "premiere_chaque_fois": (nommer(tete["premiere_chaque_fois"])
                                         if tete.get("premiere_chaque_fois") else None)}

    # ── Les compos : seulement si elles sont du même set que le relevé ───
    co = charger("compos.json") or {}
    rec = charger("recettes.json") or {}
    rec_ok = rec.get("set") == setn
    recettes = (rec.get("recettes") or {}) if rec_ok else {}
    comp_fr = ({k: v.get("fr") or v.get("nom") or k
                for k, v in (rec.get("composants") or {}).items()} if rec_ok else {})
    fiches, compos_etat = [], None
    if not co:
        compos_etat = "Les compos n'ont pas encore été relevées."
    elif co.get("set") != setn:
        compos_etat = (f"Les compos relevées sont celles du Set {co.get('set')} ; "
                       f"le relevé courant est du Set {setn}. Elles ne sont pas "
                       "affichées.")
    elif not co.get("compos"):
        compos_etat = co.get("etat_note") or "Aucune compo dans le relevé."
    else:
        fiches = [fiche(c, co.get("n_parties"), recettes, comp_fr)
                  for c in co["compos"]]

    # ── Le volume : un patch qui vient de sortir ne se lit pas comme un mûr
    precedent = du_set[-2] if len(du_set) >= 2 else None
    n_cour = courant.get("n_parties") or 0
    n_prec = (precedent or {}).get("n_parties") or 0
    frais = bool((n_prec and n_cour < 0.5 * n_prec) or len(ordre) < 20)

    # Tous les noms dont le site a besoin, calculés ICI et nulle part ailleurs.
    ids = set(courant.get("unites") or {}) | set(courant.get("objets") or {})
    ids |= {t.get("trait") for t in (courant.get("traits") or {}).values() if t.get("trait")}
    for c in (co.get("compos") or []):
        ids |= {x[0] for x in (c.get("unites") or []) if isinstance(x, list)}
        ids |= {p["unite"] for p in (c.get("porteurs") or [])}
        ids |= {t["trait"] for t in (c.get("traits") or [])}
    noms = {i: nommer(i) for i in sorted(i for i in ids if i)}
    # Les fichiers tirés de SES parties (miroir, focus, contestation) nomment
    # les unités autrement que le relevé : « Draven18 », « murkwolf ». La clé
    # commune est champion() ; le site s'en sert en second recours.
    par_cle = {}
    for i in sorted(ids | set(JEU["unites"]) | set(JEU["traits"])):
        if i:
            par_cle.setdefault(M.champion(i), nommer(i).split(" (")[0])

    fige = os.path.join(RACINE, "tools", "build", f"data_set{setn}_fige.js")
    out = {
        "schema_version": SCHEMA,
        "genere_le": date.today().isoformat(),
        "set": setn,
        "releve": {
            "date": courant["date"], "patch": courant.get("patch"),
            "rang": courant.get("rang"), "source": courant.get("source"),
            "n_parties": n_cour, "fenetre": courant.get("fenetre"),
            "set": setn,
            "premier_releve": courant.get("premier_releve"),
            "n_mises_a_jour": courant.get("n_mises_a_jour"),
        },
        "volume": {
            "frais": frais,
            "n_unites_classees": len(ordre),
            "n_unites_relevees": len(courant.get("unites") or {}),
            "seuil_par_unite": M.NMIN,
            "patch_precedent": (precedent or {}).get("patch"),
            "n_parties_patch_precedent": n_prec or None,
            "note": (
                f"{n_cour:,} parties : ".replace(",", " ")
                + (f"{len(ordre)} unités sur {len(courant.get('unites') or {})} "
                   f"dépassent le seuil de {M.NMIN} parties. " if len(ordre) < 20 else "")
                + "Le patch vient de sortir, les classements bougent encore. "
                  "Le relevé se met à jour tout seul à mesure qu'il mûrit."
            ) if frais else None,
        },
        "diff": d, "diff_raison": d_raison,
        "ses_lignes": ses_lignes_au_patch(paire[0], paire[1],
                                          charger("miroir.json"), setn, d),
        "tete_stable": tete,
        "unites": [{"id": k, "nom": nommer(k), "cout": cout(k), "rang": g[k],
                    "avg": u[k]["avg"], "wr": u[k]["wr"], "t4": u[k].get("t4"),
                    "n": u[k]["n"]} for k in ordre],
        "compos": fiches,
        "compos_etat": compos_etat,
        "compos_source": ({"date": co.get("date"), "n_parties": co.get("n_parties"),
                           "limite": co.get("limite"),
                           "population": (co.get("population") or {}).get("meme_population")}
                          if fiches else None),
        "modes": modes(fiches),
        "noms": noms,
        "noms_par_cle": par_cle,
        "jeu": {"du_set": bool(JEU["unites"]), "n_unites": len(JEU["unites"]),
                "francais": bool((jeu or {}).get("francais")) if JEU["unites"] else None},
        "a_venir": a_venir(jeu),
        "serie": [{"date": r["date"], "patch": r.get("patch"), "rang": r.get("rang"),
                   "set": r.get("set"), "n_parties": r.get("n_parties"),
                   "premier_releve": r.get("premier_releve"),
                   "n_mises_a_jour": r.get("n_mises_a_jour")} for r in rs],
        "fichiers": manifeste(setn),
        "oracle": {"set": setn, "disponible": os.path.exists(fige),
                   "note": None if os.path.exists(fige) else
                           f"Les fiches figées du Set {setn} ne sont pas écrites : "
                           "l'ancien moteur n'est pas publié pour ce set."},
    }

    M.ecrire(SORTIE, out)

    # Copie vers site/data/ pour le développement local. En production, le
    # workflow de déploiement fait la même chose — site/data/ n'est donc pas
    # versionné : la source reste data/.
    cible = os.path.join(RACINE, "site", "data")
    os.makedirs(os.path.join(cible, "meta"), exist_ok=True)
    shutil.copy(SORTIE, os.path.join(cible, "meta", "courant.json"))
    # ⚠ `ATTENDUS` DOIT SUIVRE `SOURCES` DANS site/index.html.
    # Un fichier oublié ici ne provoque aucune erreur : le site reçoit un 404,
    # le bloc concerné ne s'affiche pas, et rien ne dit pourquoi. On annonce
    # donc les manquants à voix haute plutôt que de les laisser passer.
    copies, manquants = [], []
    for f in ATTENDUS:
        src = os.path.join(RACINE, "data", f)
        if os.path.exists(src):
            shutil.copy(src, os.path.join(cible, f))
            copies.append(f)
        else:
            manquants.append(f)
            # Un fichier absent de data/ ne doit pas survivre dans site/data/
            # d'une construction précédente.
            vieux = os.path.join(cible, f)
            if os.path.exists(vieux):
                os.remove(vieux)
    # Les fichiers de référence vivent dans data/reference/ : ils sont écrits
    # à la main, pas produits par un script, et ce dossier les distingue.
    src_ref = os.path.join(RACINE, "data", "reference")
    if os.path.isdir(src_ref):
        dst_ref = os.path.join(cible, "reference")
        os.makedirs(dst_ref, exist_ok=True)
        for f in os.listdir(src_ref):
            if f.endswith(".json"):
                shutil.copy(os.path.join(src_ref, f), os.path.join(dst_ref, f))
                copies.append("reference/" + f)

    print(f"copié vers site/data/ : {len(copies)} fichiers")
    if manquants:
        print(f"  ⚠ absents de data/ : {', '.join(manquants)}")
    autres = [f"{f} (Set {m['set']})" for f, m in out["fichiers"].items()
              if m.get("du_set_courant") is False]
    if autres:
        print(f"  ⚠ ne parlent pas du Set {setn} : {', '.join(autres)} — "
              "le site les étiquette ou les masque.")
    taille = os.path.getsize(SORTIE)
    print(f"écrit : {SORTIE} ({taille:,} octets)".replace(",", " "))
    print(f"  {len(ordre)} unités classées · {len(fiches)} fiches de ligne"
          + (f" · {compos_etat}" if compos_etat else ""))
    if d:
        print(f"  rotation {d['de']['patch']} -> {d['a']['patch']} : "
              f"Spearman {d['spearman']} · bruit {d['plancher_bruit']} · "
              f"{d['part_reelle_pct']} % réel"
              + ("" if d["volume"]["comparable"] else " · ⚠ volumes inégaux"))
    elif d_raison:
        print(f"  pas de rotation : {d_raison}")


if __name__ == "__main__":
    main()
