#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LE CARNET — historique des relevés de méta
===========================================
L'Oracle ne garde qu'une photo : celle du jour. C'est exactement pourquoi
on a perdu le fil entre le 28/08 et le 19/10, et pourquoi on ne sait
toujours pas de combien un patch live déplace la méta.

Le Carnet garde la SÉRIE. Il répond à trois questions que l'Oracle ne
peut pas poser :

  1. De combien un patch déplace-t-il le classement ?
     -> fixe la fréquence de rafraîchissement nécessaire au Set 19
  2. Un buff met combien de temps à produire une ligne de méta ?
     -> donne la fenêtre d'avance exploitable
  3. Ce relevé est-il encore valable ?
     -> évite de jouer sur une photo périmée

UTILISATION
-----------
    python3 carnet.py lister
    python3 carnet.py comparer 2026-08-28 2026-10-19
    python3 carnet.py rotation          # tous les couples consécutifs
    python3 carnet.py fraicheur         # le dernier relevé est-il à jour ?
    python3 carnet.py bruit             # ce mouvement est-il réel ou du hasard ?

FORMAT D'UN RELEVÉ  (releves/AAAA-MM-JJ_patch_rang.json)
--------------------------------------------------------
    {
      "date": "2026-10-19", "patch": "18.4b", "rang": "Master+",
      "source": "...", "n_parties": 171832, "fenetre": "24h", "set": 18,
      "note": "...",
      "unites": { "Lux": {"avg":3.56,"wr":25.1,"n":19751}, ... },
      "compos": [ {"n":"...","avg":4.11,"pr":0.34,"wr":15.3,"t4":null}, ... ]
    }

Ajouter un relevé = déposer un fichier de cette forme dans releves/.
Aucune base de données, aucune dépendance : des fichiers lisibles à l'œil.
"""

import json, os, sys, glob, datetime, statistics as st

# Le socle de mesure est partagé avec build_site.py : une seule implémentation,
# donc une seule correction à faire si un calcul est faux.
sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import mesures as M

DEPOT   = M.DEPOT
RELEVES = M.RELEVES

# Volume minimal pour qu'une unité entre dans les comparaisons.
# Sous ce seuil le classement est du bruit. Valeur à CALIBRER — voir
# la commande "rotation", qui mesure la sensibilité à ce seuil.
NMIN = M.NMIN


# ---------------------------------------------------------------- chargement

# Laquelle des deux séries on lit. Elles ne se mélangent JAMAIS dans une même
# comparaison — sources différentes, nommage des patchs différent, et
# tactics.tools éclate Lux en dix entrées là où MetaTFT n'en voit qu'une.
SERIES = {
    "metatft":  os.path.join(DEPOT, "data", "releves"),      # manuelle
    "tactics":  os.path.join(DEPOT, "data", "releves-tt"),    # AUTOMATIQUE
}
SERIE = "metatft"          # défaut historique ; `--serie tactics` pour l'autre


def charger():
    """Délégué au socle commun — vérifie schema_version.

    ⚠ Jusqu'au 05/11 ce carnet ne savait lire QUE data/releves/ (MetaTFT,
    déposée à la main, douze jours de retard au 04/11). La série automatique
    n'avait donc aucun outil de comparaison : au patch suivant, on n'aurait
    pas pu mesurer la rotation sur la seule série qui se tient à jour toute
    seule — et c'est elle qui portera la prédiction du 18.6.
    """
    return M.charger(SERIES[SERIE])


def par_date(releves, date):
    for r in releves:
        if r["date"] == date:
            return r
    dispo = ", ".join(r["date"] for r in releves)
    sys.exit(f"Relevé {date} introuvable. Disponibles : {dispo}")


# ---------------------------------------------------------------- mesures

def rangs(releve, nmin=None):
    """Délégué au socle commun."""
    return M.classement(releve, nmin if nmin is not None else M.NMIN)


def spearman(a, b):
    """Délégué au socle commun."""
    return M.spearman(a, b)


def comparer(r1, r2, nmin=NMIN, silencieux=False):
    g1, u1 = rangs(r1, nmin)
    g2, u2 = rangs(r2, nmin)
    com = sorted(set(g1) & set(g2))
    if not com:
        sys.exit("Aucune unité commune aux deux relevés.")

    dep = {k: g2[k] - g1[k] for k in com}
    absd = [abs(v) for v in dep.values()]
    rho, n = spearman(g1, g2)

    jours = (datetime.date.fromisoformat(r2["date"])
             - datetime.date.fromisoformat(r1["date"])).days

    # stabilité de la tête et de la queue
    def topn(g, n_):
        return set(sorted(g, key=lambda k: g[k])[:n_])
    t8_1, t8_2 = topn(g1, 8), topn(g2, 8)
    q8_1 = set(sorted(g1, key=lambda k: -g1[k])[:8])
    q8_2 = set(sorted(g2, key=lambda k: -g2[k])[:8])

    # variation du placement moyen des unités communes
    dav = [u2[k]["avg"] - u1[k]["avg"] for k in com]

    res = {
        "de": r1["date"], "a": r2["date"],
        "patch_de": r1.get("patch"), "patch_a": r2.get("patch"),
        "rang_de": r1.get("rang"), "rang_a": r2.get("rang"),
        "jours": jours, "n_communes": n,
        "spearman": rho,
        "dep_median": st.median(absd), "dep_moyen": st.mean(absd), "dep_max": max(absd),
        "top8_conserve": len(t8_1 & t8_2), "queue8_conservee": len(q8_1 & q8_2),
        "entres_top8": sorted(t8_2 - t8_1), "sortis_top8": sorted(t8_1 - t8_2),
        "montees": sorted(dep.items(), key=lambda kv: kv[1])[:8],
        "chutes": sorted(dep.items(), key=lambda kv: -kv[1])[:8],
        "delta_avg_median": st.median(dav),
        "comparable": r1.get("rang") == r2.get("rang"),
    }

    if silencieux:
        return res

    print(f"\n=== {r1['date']} ({r1.get('patch')}, {r1.get('rang')})"
          f"  ->  {r2['date']} ({r2.get('patch')}, {r2.get('rang')}) ===")
    print(f"{jours} jours · {n} unités comparables (volume >= {nmin})")
    if not res["comparable"]:
        print("  ⚠ TRANCHES D'ELO DIFFÉRENTES : une partie du mouvement vient du")
        print("    changement de population, pas des patchs. À interpréter avec prudence.")
    print(f"\nCorrélation de rang (Spearman) : {rho:.3f}"
          f"   ({'méta quasi figée' if rho>.95 else 'rotation modérée' if rho>.85 else 'forte rotation'})")
    print(f"Déplacement  médian {res['dep_median']:.0f} rangs ·"
          f" moyen {res['dep_moyen']:.1f} · max {res['dep_max']}")
    print(f"Placement moyen : variation médiane {res['delta_avg_median']:+.3f} place")
    print(f"\nTête  : {res['top8_conserve']}/8 conservées"
          + (f" · entrées {res['entres_top8']}" if res['entres_top8'] else " · aucun changement"))
    print(f"Queue : {res['queue8_conservee']}/8 conservées")
    print("\nPlus fortes montées :")
    for k, v in res["montees"]:
        print(f"  {k:18s} {g1[k]:2d}e -> {g2[k]:2d}e  ({v:+3d})"
              f"  place {u1[k]['avg']:.2f} -> {u2[k]['avg']:.2f}")
    print("Plus fortes chutes :")
    for k, v in res["chutes"]:
        print(f"  {k:18s} {g1[k]:2d}e -> {g2[k]:2d}e  ({v:+3d})"
              f"  place {u1[k]['avg']:.2f} -> {u2[k]['avg']:.2f}")
    return res


# ---------------------------------------------------------------- commandes

def cmd_lister():
    rs = charger()
    if not rs:
        sys.exit(f"Aucun relevé dans {RELEVES}/")
    print(f"{len(rs)} relevé(s) :\n")
    for r in rs:
        nu = len(r.get("unites", {}))
        nc = len(r.get("compos", []))
        print(f"  {r['date']}  {str(r.get('patch')):8s} {str(r.get('rang')):10s}"
              f"  {nu:3d} unités · {nc:2d} compos · {r.get('n_parties',0):>8,} parties"
              .replace(",", " "))
        if r.get("note"):
            print(f"              {r['note']}")


def cmd_comparer(d1, d2):
    rs = charger()
    comparer(par_date(rs, d1), par_date(rs, d2))


def cmd_rotation():
    """Tous les couples consécutifs : c'est la série qui donne la constante."""
    rs = charger()
    if len(rs) < 2:
        sys.exit("Il faut au moins deux relevés. Un seul pour l'instant :"
                 " la série commencera au prochain patch.")
    print("=== Rotation de la méta, relevé après relevé ===\n")
    lignes = []
    for a, b in zip(rs, rs[1:]):
        r = comparer(a, b, silencieux=True)
        lignes.append(r)
        flag = "" if r["comparable"] else "  ⚠ elo différent"
        print(f"  {r['de']} -> {r['a']}  ({r['jours']:3d} j, {r['patch_de']}->{r['patch_a']})"
              f"   Spearman {r['spearman']:.3f} · médian {r['dep_median']:.0f} rangs"
              f" · tête {r['top8_conserve']}/8{flag}")
    comp = [l for l in lignes if l["comparable"]]
    if comp:
        # On compte PAR PATCH, pas par jour : la méta ne dérive pas
        # continûment, elle saute à chaque patch et reste stable entre deux.
        # Diviser par le nombre de jours serait une extrapolation fausse.
        pertes = [1 - l["spearman"] for l in comp]
        deps   = [l["dep_median"] for l in comp]
        n = len(comp)
        print(f"\nSur {n} couple(s) à elo constant :")

        # ⚠ UNE MESURE SUR UN POINT N'EST PAS UNE CONSTANTE.
        # Cet outil a affiché « perte PAR PATCH : 0.154 » pendant dix jours
        # sur UN seul couple, et la charte l'a recopié en gras comme un fait
        # acquis. Mesuré sur six transitions le 03/11, l'intervalle réel va
        # de 0.057 à 0.353. Le chiffre n'était ni faux ni représentatif : il
        # était unique. On refuse désormais de le présenter autrement.
        if n == 1:
            print(f"  perte observée sur CE couple : {pertes[0]:.3f} "
                  f"({deps[0]:.0f} rangs de déplacement médian)")
            print("  ⚠ UN SEUL POINT DE MESURE — ce n'est pas une constante.")
            print("    Un patch peut coûter de 0.06 à 0.35 de corrélation selon")
            print("    qu'il est un correctif ou un vrai patch, et selon l'âge du")
            print("    set. Ne pas extrapoler ce chiffre.")
        else:
            print(f"  perte de corrélation par patch : {st.mean(pertes):.3f} "
                  f"en moyenne, de {min(pertes):.3f} à {max(pertes):.3f}")
            print(f"  déplacement médian : {st.mean(deps):.0f} rangs par unité")
            if n < 4:
                print(f"  ⚠ {n} points seulement : l'intervalle est indicatif.")
        # ⚠ Corrigé le 05/11 : « deux relevés sans patch » NE SUFFIT PAS.
        # Essayé sur 18.5c, 03/11 contre 04/11 : Spearman 0.999 pour un
        # plancher à 0.994, donc un observé AU-DESSUS du hasard. La raison
        # est que les relevés sont CUMULÉS depuis le début du patch — les
        # 500 777 parties du 04/11 contiennent les 449 902 du 03/11, et le n
        # de chaque unité ne fait que croître. Deux échantillons qui se
        # recouvrent à 90 % corrèlent à 0.999 par construction.
        print("  (la dérive INTRA-patch reste non mesurée, et deux relevés")
        print("   sans patch n'y suffisent PAS : ils sont cumulés depuis le")
        print("   début du patch, donc ils se recouvrent presque entièrement.")
        print("   Il faudrait des fenêtres DISJOINTES — une piste existe,")
        print("   le champ `dateStats` de la page des compos.)")
    else:
        print("\nAucun couple à elo constant : la constante de rotation n'est pas")
        print("encore mesurable. Il faut deux relevés consécutifs dans la MÊME tranche.")
        pro = prochain_patch()
        if pro:
            print(f"Le prochain (patch {pro['nom']}, {pro['date']}) rendra la mesure possible.")
        else:
            print("Aucun patch à venir dans data/calendrier.json.")


def patchs_connus():
    """Tous les patchs du calendrier, triés. UNE SEULE source.

    ⚠ Le 05/11, ce fichier portait DEUX calendriers : celui-ci, lu dans
    data/calendrier.json, et une liste en dur dans cmd_fraicheur() qui
    annonçait encore « 18.6B le 11/11 » alors que le calendrier disait 18.7
    depuis la veille. La docstring de prochain_patch() disait pourtant
    « jamais écrit en dur » : la leçon avait été appliquée à une fonction et
    pas à sa voisine, dans le même fichier.
    """
    try:
        cal = json.load(open(os.path.join(DEPOT, "data", "calendrier.json"),
                             encoding="utf-8"))
    except Exception:
        return []
    return sorted((p for p in cal.get("patchs", []) if p.get("date")),
                  key=lambda p: p["date"])


def prochain_patch():
    """Le prochain patch, lu dans le calendrier — jamais écrit en dur.

    Cette ligne annonçait « patch 18.6, 04/11 » en dur : juste jusqu'au
    4 novembre, faux ensuite, et silencieusement faux. Un message d'aide
    qui ment est pire qu'un message absent."""
    import datetime
    auj = datetime.date.today().isoformat()
    a_venir = [p for p in patchs_connus() if p["date"] > auj]
    return a_venir[0] if a_venir else None


def cmd_fraicheur():
    rs = charger()
    if not rs:
        sys.exit("Aucun relevé.")
    d = rs[-1]
    age = (datetime.date.today() - datetime.date.fromisoformat(d["date"])).days
    print(f"Dernier relevé : {d['date']} ({d.get('patch')}, {d.get('rang')}) — {age} jours")
    # Le MÊME calendrier que prochain_patch(). Cette liste était écrite en dur
    # juste ici et annonçait encore « 18.6B » pour le 11/11, un jour après que
    # le calendrier ait été corrigé en 18.7.
    auj = datetime.date.today().isoformat()

    # ⚠ LE CALENDRIER ANNONCE, IL NE CONSTATE PAS.
    #
    # Le 05/11, il affirmait « 18.6 le 04/11 » — et le patch en ligne était
    # toujours 18.5c. Une date prévue qui passe devient un faux fait
    # silencieux, et ce bloc déclarait le relevé « PÉRIMÉ » à cause d'un
    # patch qui n'est jamais sorti.
    #
    # On croise donc l'annonce avec l'observation : un patch est OBSERVÉ si
    # un relevé de la série porte son libellé. Sinon il reste annoncé, et on
    # le dit autrement.
    vus = {str(r.get("patch", "")).lower() for r in rs}
    def observe(p):
        return str(p.get("nom") or p.get("patch") or "").lower() in vus

    depuis = [p for p in patchs_connus() if d["date"] < p["date"] <= auj]
    obs = [p for p in depuis if observe(p)]
    annonces = [p for p in depuis if not observe(p)]

    if obs:
        print(f"\n  ⚠ {len(obs)} patch(s) OBSERVÉ(s) depuis ce relevé : "
              + ", ".join(f"{p.get('nom') or p.get('patch')} ({p['date']})"
                          for p in obs))
        print("    Le relevé est PÉRIMÉ. En refaire un avant de s'y fier.")
    if annonces:
        print(f"\n  {len(annonces)} patch(s) ANNONCÉ(s) mais pas encore vu(s) "
              "en relevé : "
              + ", ".join(f"{p.get('nom') or p.get('patch')} (prévu {p['date']})"
                          for p in annonces))
        print(f"    Le dernier patch réellement observé est {d.get('patch')}. "
              "Soit la sortie a glissé, soit le calendrier se trompe —")
        print("    dans les deux cas c'est le calendrier qu'il faut corriger, "
              "pas le relevé.")
    if not depuis:
        if age > 14:
            print(f"\n  ⚠ {age} jours sans patch connu, mais c'est long. "
                  "À rafraîchir.")
        else:
            print("\n  Aucun patch depuis ce relevé : il est à jour.")
    # Même source encore : prochain_patch() lit le calendrier.
    pro = prochain_patch()
    if pro:
        j = (datetime.date.fromisoformat(pro["date"]) - datetime.date.today()).days
        print(f"  Prochain patch : {pro.get('nom') or pro.get('patch')} "
              f"le {pro['date']} (dans {j} jours)"
              + (f" — {pro['note']}" if pro.get("note") else ""))


def cmd_bruit():
    """Quelle part d'un mouvement observé vient du simple hasard d'échantillonnage ?

    Un relevé à faible volume produit un classement bruité : des unités
    séparées de 0.01 place peuvent permuter sans que rien n'ait changé.
    Cette commande simule DEUX tirages des MÊMES vraies valeurs, aux volumes
    réels de chaque relevé, et donne la corrélation qu'on obtiendrait si la
    méta n'avait pas bougé du tout. C'est le PLANCHER : tout écart au-delà
    est du vrai mouvement."""
    import random
    rs = charger()
    if len(rs) < 2:
        sys.exit("Il faut deux relevés.")
    a, b = rs[-2], rs[-1]
    ga, ua = rangs(a); gb, ub = rangs(b)
    com = sorted(set(ga) & set(gb))
    SD = 2.3                      # écart-type du placement en TFT, ~constant
    obs, n = spearman(ga, gb)

    plancher = M.plancher_bruit(ua, ub, com)

    print(f"=== Bruit d'échantillonnage : {a['date']} vs {b['date']} ===\n")
    print(f"  volumes   : {sum(ua[k]['n'] for k in com):,} / {sum(ub[k]['n'] for k in com):,}"
          .replace(",", " "))
    print(f"  Spearman observé                    : {obs:.3f}")
    print(f"  Spearman si RIEN n'avait changé     : {plancher:.3f}  (bruit seul)")
    reel = plancher - obs
    print(f"\n  part attribuable au bruit  : {1-plancher:.3f}")
    print(f"  part de VRAI mouvement     : {reel:.3f}")
    if reel < 0.02:
        print("\n  => Le mouvement observé s'explique par le hasard. Ne pas conclure.")
    else:
        print(f"\n  => Le mouvement est réel : {100*reel/max(1-obs,1e-9):.0f} % de l'écart observé")
        print("     n'est pas du bruit.")


if __name__ == "__main__":
    cmds = {"lister":cmd_lister, "rotation":cmd_rotation,
            "fraicheur":cmd_fraicheur, "bruit":cmd_bruit}
    a = sys.argv[1:]

    # `--serie tactics` AVANT tout le reste : les commandes lisent SERIE au
    # moment où elles appellent charger(), donc le choix doit être arrêté
    # avant la première lecture.
    if "--serie" in a:
        i = a.index("--serie")
        if i + 1 >= len(a) or a[i + 1] not in SERIES:
            sys.exit(f"--serie attend : {' ou '.join(SERIES)}")
        SERIE = a[i + 1]
        del a[i:i + 2]
    print(f"[série : {SERIE} — {os.path.relpath(SERIES[SERIE], DEPOT)}]")

    if not a or a[0] not in list(cmds) + ["comparer"]:
        print(__doc__)
        sys.exit(0)
    if a[0] == "comparer":
        if len(a) != 3:
            sys.exit("Usage : python3 carnet.py [--serie tactics] "
                     "comparer AAAA-MM-JJ AAAA-MM-JJ")
        cmd_comparer(a[1], a[2])
    else:
        cmds[a[0]]()
