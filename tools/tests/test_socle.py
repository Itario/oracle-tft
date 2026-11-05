#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LES TESTS — chaque leçon du projet, rendue exécutable
======================================================
    python3 tools/tests/test_socle.py

POURQUOI CE FICHIER ARRIVE SI TARD, ET POURQUOI IL EST CE QU'IL EST.

Ce projet a trouvé une quinzaine de pannes silencieuses en deux semaines :
un relevé figé au plus mauvais moment, une chaîne de déploiement qui ne se
refermait pas, deux définitions d'« unité » qui se contredisaient sur la même
page, un calendrier en double, un plancher de bruit tiré avec les mauvais
volumes. **Aucune n'a été attrapée par un test. Toutes par quelqu'un qui
regardait.**

Ce fichier ne teste donc pas « le code marche ». Il teste **les leçons** :
chaque test correspond à une erreur qui a réellement été commise, et son nom
dit laquelle. Si un test casse, ce n'est pas une régression technique — c'est
une erreur du projet qui revient.

Pas de dépendance : ni pytest ni rien. Un script qui sort 1 s'il échoue, pour
que le workflow puisse l'exécuter sans rien installer.
"""

import glob, json, math, os, re, sys

RACINE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(RACINE, "tools", "lib"))
import mesures as M

ECHECS, PASSES = [], 0


def verifier(nom, condition, detail=""):
    global PASSES
    if condition:
        PASSES += 1
        print(f"  ok    {nom}")
    else:
        ECHECS.append(nom)
        print(f"  ÉCHEC {nom}" + (f"\n          {detail}" if detail else ""))


def donnees(nom):
    try:
        return json.load(open(os.path.join(RACINE, "data", nom), encoding="utf-8"))
    except Exception:
        return None


# ══ LE SOCLE DE MESURE ═══════════════════════════════════════════════════
print("\nLE SOCLE DE MESURE")

# 04/11 : le Focus disait « tu la joues » pour murkwolf pendant que les compos
# le comptaient inconnu. Deux définitions de « la même unité » sous un mot.
verifier("champion() regroupe les variantes de Lux",
         len({M.champion(x) for x in
              ["DA_18_Lux_Moonbeam", "DA_Lux18_Blackthorn", "DA_18_Lux_Coven"]}) == 1,
         "tactics.tools éclate Lux en dix entrées : sans regroupement, chaque "
         "variante compte pour une unité et la contestation devient illisible.")

verifier("champion() ne confond pas deux champions",
         M.champion("DA_18_Ezreal") != M.champion("DA_18_Ashe"))

verifier("champion() survit à un identifiant vide",
         M.champion("") == "" and M.champion(None) == "none")

verifier("champion() n'existe qu'à UN endroit",
         sum(1 for f in glob.glob(os.path.join(RACINE, "tools", "**", "*.py"),
                                  recursive=True)
             if re.search(r"^def champion\(", open(f, encoding="utf-8").read(),
                          re.M)) == 1,
         "Quatre copies existaient le 05/11. Identiques ce jour-là, donc sans "
         "bug — mais la prochaine correction en fait diverger une.")

# Spearman : deux classements identiques doivent donner 1, inversés -1.
rho_id, _ = M.spearman({"a": 1, "b": 2, "c": 3}, {"a": 1, "b": 2, "c": 3})
rho_inv, _ = M.spearman({"a": 1, "b": 2, "c": 3}, {"a": 3, "b": 2, "c": 1})
verifier("spearman : identique -> 1", abs(rho_id - 1.0) < 1e-9, f"obtenu {rho_id}")
verifier("spearman : inversé -> -1", abs(rho_inv + 1.0) < 1e-9, f"obtenu {rho_inv}")


# ══ LE PLANCHER DE BRUIT ═════════════════════════════════════════════════
print("\nLE PLANCHER DE BRUIT")

# 03/11 : le plancher était tiré en utilisant DEUX FOIS les volumes de A. Il
# donnait 0.991 pour une transition à 5 304 parties — moins de volume doit
# donner PLUS de bruit, donc un plancher PLUS BAS. L'erreur s'est vue dans le
# SENS, pas dans la valeur.
gros = {f"u{i}": {"avg": 4.0 + i * 0.01, "n": 200000} for i in range(40)}
petit = {f"u{i}": {"avg": 4.0 + i * 0.01, "n": 2000} for i in range(40)}
com = sorted(gros)
pl_gros = M.plancher_bruit(gros, gros, com)
pl_petit = M.plancher_bruit(gros, petit, com)
verifier("un faible volume donne un plancher PLUS BAS",
         pl_petit < pl_gros,
         f"gros volume {pl_gros:.4f} · petit volume {pl_petit:.4f} — si le "
         "petit est au-dessus, le plancher est tiré avec les mauvais volumes.")
verifier("le plancher dépend bien des DEUX côtés",
         abs(M.plancher_bruit(petit, gros, com) - pl_gros) > 1e-6,
         "Échanger A et B ne doit pas redonner le plancher de A contre A.")


# ══ LA COMPARAISON DE DEUX RELEVÉS ═══════════════════════════════════════
print("\nLA COMPARAISON DE DEUX RELEVÉS")

# 05/11, leçon n°39 : 18.5c (500 777 parties) contre 18.6 (54 954). Seize
# unités sous le seuil, dont les huit Lux. Le Spearman se calcule sur le
# sous-ensemble commun SANS JAMAIS dire que ce sous-ensemble a changé.
def faux_releve(date_, patch, unites, n):
    return {"schema_version": 1, "date": date_, "patch": patch,
            "rang": "Master+", "n_parties": n, "unites": unites}


mur = {f"u{i}": {"avg": 4.0 + i * 0.02, "n": 50000} for i in range(30)}
frais = {f"u{i}": {"avg": 4.0 + i * 0.02, "n": 5000} for i in range(20)}
frais.update({f"u{i}": {"avg": 4.0 + i * 0.02, "n": 500} for i in range(20, 30)})
r = M.comparer(faux_releve("2026-01-01", "A", mur, 500000),
               faux_releve("2026-01-02", "B", frais, 50000))
verifier("volumes inégaux : le drapeau tombe",
         r["volume"]["comparable"] is False)
verifier("volumes inégaux : les unités perdues sont NOMMÉES",
         len(r["volume"]["unites_perdues"]) == 10,
         f"trouvé {len(r['volume']['unites_perdues'])}")
verifier("volumes inégaux : l'avertissement est porté",
         bool(r["volume"]["avertissement"]))

r2 = M.comparer(faux_releve("2026-01-01", "A", mur, 500000),
                faux_releve("2026-01-02", "B", mur, 480000))
verifier("volumes comparables : pas de fausse alerte",
         r2["volume"]["comparable"] is True)


# ══ CE QUI EST PUBLIÉ ════════════════════════════════════════════════════
print("\nCE QUI EST PUBLIÉ")

# Le dépôt est PUBLIC. La page du joueur porte un puuid, les fichiers de
# parties portent celui des sept adversaires.
fichiers = glob.glob(os.path.join(RACINE, "data", "**", "*.json"), recursive=True)
avec_puuid = [os.path.relpath(f, RACINE) for f in fichiers
              if "puuid" in open(f, encoding="utf-8").read().lower()]
verifier("aucun puuid dans data/", not avec_puuid, f"trouvés dans {avec_puuid}")

cles = [os.path.relpath(f, RACINE) for f in fichiers
        if re.search(r"RGAPI-[0-9a-f-]{20,}", open(f, encoding="utf-8").read())]
verifier("aucune clé API dans data/", not cles, f"trouvées dans {cles}")

# 04/11 : build_site.py copiait une liste EXPLICITE. Un fichier oublié donnait
# un 404, un bloc vide, et aucun message.
site = open(os.path.join(RACINE, "site", "index.html"), encoding="utf-8").read()
lues = set(re.findall(r'"(data/[A-Za-z0-9_/\-]+\.json)"', site))
bs = open(os.path.join(RACINE, "tools", "build", "build_site.py"),
          encoding="utf-8").read()
copiees = set(re.findall(r'"([a-z_]+\.json)"', bs))
manquantes = {u for u in lues
              if os.path.basename(u) not in copiees
              and "reference/" not in u}
verifier("tout ce que le site LIT est copié par build_site",
         not manquantes,
         f"le site demande {sorted(manquantes)} que build_site ne copie pas — "
         "404 silencieux, bloc vide, aucun message.")


# ══ LES FICHIERS DE RÉFÉRENCE ════════════════════════════════════════════
print("\nLES FICHIERS DE RÉFÉRENCE")

# Ils périment au Set 19. Sans `set` ni `nature`, le site ne peut ni les
# marquer ni les cacher.
for f in glob.glob(os.path.join(RACINE, "data", "reference", "*.json")):
    o = json.load(open(f, encoding="utf-8"))
    nom = os.path.basename(f)
    verifier(f"{nom} déclare sa nature",
             o.get("nature") in ("reference", "raisonnement"),
             f"nature={o.get('nature')!r}")
    verifier(f"{nom} déclare son set (garde de péremption)",
             isinstance(o.get("set"), int))


# ══ LES MESURES PUBLIÉES, SI ELLES EXISTENT ══════════════════════════════
print("\nLES MESURES PUBLIÉES")

j = donnees("joueur.json")
if j and j.get("projection"):
    e = j["projection"]["erreur_decomposee"]
    # 04/11, leçon n°34 : le premier jet ne propageait que l'erreur du barème
    # (0.41) et annonçait ±5 parties. L'incertitude vient du PLACEMENT.
    verifier("l'erreur du placement domine celle du barème",
             e["placement"] > 2 * e["bareme"],
             f"placement {e['placement']} · barème {e['bareme']}")
    verifier("la fourchette de parties est large",
             (j["projection"]["parties_fourchette"] or [0, 0])[1]
             - (j["projection"]["parties_fourchette"] or [0, 0])[0] > 30)
    verifier("la projection porte son avertissement",
             "OPTIMISTE" in (j["projection"].get("avertissement") or ""))
else:
    print("  (joueur.json sans projection — tests sautés)")

c = donnees("compos_lui.json")
if c:
    # 04/11 : rankGroup 1 des compos == rang 0 des unités. Croiser sans le
    # vérifier aurait comparé Master+ à Diamant+.
    verifier("le croisement des compos a vérifié la population",
             (c.get("population") or {}).get("meme_population") is True,
             "build_compos doit REFUSER de croiser si les tranches divergent.")

o = donnees("objets.json")
if o:
    verifier("les objets disent si le patch est frais",
             "patch_frais" in (o.get("fraicheur") or {}))

f = donnees("fuites.json")
if f:
    # On ne compte pas une perte qu'on n'a pas constatée.
    verifier("la décroissance n'est pas comptée sans observation",
             f["decroissance"]["observee"] is False
             or "observ" in f["decroissance"].get("note", ""))

print(f"\n{'─' * 60}")
print(f"{PASSES} passés · {len(ECHECS)} échec(s)")
if ECHECS:
    print("\nÉCHECS :")
    for e in ECHECS:
        print(f"  · {e}")
    print("\nUn test qui casse ici n'est pas une régression technique :")
    print("c'est une erreur du projet qui revient.")
sys.exit(1 if ECHECS else 0)
