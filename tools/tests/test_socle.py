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

# ⚠ CES TESTS LISENT DES FICHIERS QUI ONT DES ÉTATS. Jusqu'au 10/11 ils
# supposaient tous le régime de croisière — une projection chiffrée, un
# croisement rempli — et sortaient en erreur (ou en KeyError) dès qu'un
# fichier disait « pas encore ». Or ils tournent dans le workflow de relevé,
# sans tolérance, AVANT la poussée : une semaine après le changement de set,
# ce sont les tests eux-mêmes qui auraient empêché tout relevé d'entrer dans
# le dépôt. Trouvé par la répétition générale, une fois qu'elle a cessé
# d'écarter ce fichier de la chaîne qu'elle rejoue.
#
# Chaque leçon se vérifie donc là où elle s'applique, et l'état contraire se
# vérifie aussi : un fichier qui refuse doit être réellement vide.

def en_regime(o):
    return bool(o) and o.get("etat", "ok") == "ok"

j = donnees("joueur.json")
p = (j or {}).get("projection")
if p:
    e = p["erreur_decomposee"]
    # 04/11, leçon n°34 : le premier jet ne propageait que l'erreur du barème
    # (0.41) et annonçait ±5 parties. L'incertitude vient du PLACEMENT.
    verifier("l'erreur du placement domine celle du barème",
             e["placement"] > 2 * e["bareme"],
             f"placement {e['placement']} · barème {e['bareme']}")
    verifier("la projection porte un avertissement",
             bool(p.get("avertissement")))
    if p.get("parties_estimees") is not None:
        fo = p.get("parties_fourchette")
        verifier("un nombre de parties n'est jamais donné sans fourchette large",
                 fo is None or fo[1] - fo[0] > 30,
                 f"fourchette {fo}")
        verifier("un nombre de parties est annoncé OPTIMISTE",
                 "OPTIMISTE" in (p.get("avertissement") or ""))
    else:
        verifier("sans écart à la barre, aucune fourchette n'est inventée",
                 p.get("parties_fourchette") is None)
else:
    print("  (joueur.json sans projection — tests sautés)")

c = donnees("compos_lui.json")
if en_regime(c):
    # 04/11 : rankGroup 1 des compos == rang 0 des unités. Croiser sans le
    # vérifier aurait comparé Master+ à Diamant+.
    verifier("le croisement des compos a vérifié la population",
             (c.get("population") or {}).get("meme_population") is True,
             "build_compos doit REFUSER de croiser si les tranches divergent.")
elif c:
    verifier("un croisement de compos refusé est vide", not c.get("compos"),
             f"état « {c.get('etat')} » mais {len(c.get('compos') or [])} compos")

o = donnees("objets.json")
if en_regime(o):
    verifier("les objets disent si le patch est frais",
             "patch_frais" in (o.get("fraicheur") or {}))
elif o:
    verifier("un croisement d'objets refusé est vide", not o.get("carries"))

f = donnees("fuites.json")
if en_regime(f):
    # On ne compte pas une perte qu'on n'a pas constatée.
    verifier("la décroissance n'est pas comptée sans observation",
             f["decroissance"]["observee"] is False
             or "observ" in f["decroissance"].get("note", ""))
elif f:
    verifier("des fuites non calculées ne portent aucun chiffre",
             "abandons" not in f and bool(f.get("message")))


# ══ LE CHANGEMENT DE SET ═════════════════════════════════════════════════
print("\nLE CHANGEMENT DE SET")

# 10/11 : la répétition générale du 1er décembre a trouvé quatre réponses
# différentes à « quel set est en ligne ? ». Il n'y en a plus qu'une.
import tempfile

with tempfile.TemporaryDirectory() as tmp:
    def poser(nom, set_, patch, code, prefixe, n=50000):
        json.dump({"schema_version": 1, "date": nom, "patch": patch, "set": set_, "patch_code": code,
                   "rang": "Master+", "n_parties": n,
                   "unites": {f"{prefixe}_{set_}_U{chr(65 + i)}{chr(97 + i)}x":
                              {"avg": 4 + i / 50, "wr": 12, "t4": 50, "n": 3000}
                              for i in range(20)}},
                  open(os.path.join(tmp, f"{nom}.json"), "w", encoding="utf-8"))
    poser("2026-11-20", 18, "18.7", 16230, "DA")
    verifier("un set qu'on n'a pas vu commencer n'a pas de date de début",
             M.debut_du_set(tmp) is None,
             "sans relevé d'un set antérieur, le premier relevé n'est que le "
             "jour où la série a démarré.")
    poser("2026-12-01", 19, "19.1", 16240, "ZQ")
    verifier("le set courant est celui du dernier relevé automatique",
             M.set_courant(tmp) == 19)
    verifier("un set qu'on a vu commencer a une date de début",
             M.debut_du_set(tmp) == "2026-12-01")
    cs = M.codes_du_set(tmp)
    verifier("le premier code de patch du set sépare ses parties des anciennes",
             cs["premier_code"] == 16240 and cs["borne_fiable"] is True, str(cs))

    # Le préfixe n'est pas une constante : « DA » était retiré en dur.
    M._prefixes_cache.clear()
    ids = list(json.load(open(os.path.join(tmp, "2026-12-01.json")))["unites"])
    distincts = {M.champion(i, tmp) for i in ids}
    verifier("champion() survit à un changement de préfixe",
             len(distincts) == len(ids),
             f"{len(ids)} identifiants -> {len(distincts)} champions : "
             f"{sorted(distincts)[:4]}")
    verifier("nom_affichable() ne laisse ni préfixe ni numéro de set",
             all(not re.search(r"ZQ|\d", M.nom_affichable(i, tmp)) for i in ids),
             M.nom_affichable(ids[0], tmp))
    M._prefixes_cache.clear()

    # Mêmes identifiants des deux côtés, exprès : avec des identifiants
    # différents, comparer() renvoie None faute d'unité commune, et le test
    # passerait même sans le refus (vérifié par mutation le 10/11). Le cas qui
    # compte est celui où les noms SE RECOUVRENT d'un set à l'autre.
    r18 = json.load(open(os.path.join(tmp, "2026-11-20.json")))
    r19 = {**r18, "set": 19, "patch": "19.1", "date": "2026-12-01"}
    verifier("comparer() accepte deux relevés du même set",
             M.comparer(r18, {**r18, "date": "2026-11-21"}) is not None)
    verifier("comparer() refuse deux sets", M.comparer(r18, r19) is None,
             "une rotation de méta n'a de sens qu'à l'intérieur d'un set.")

# Aucun script ne retire un préfixe ou un numéro de set en dur.
durs = []
for chemin in (glob.glob(os.path.join(RACINE, "tools", "**", "*.py"), recursive=True)
               + [os.path.join(RACINE, "site", "index.html")]):
    if chemin.endswith(("test_socle.py", "repetition.py")):
        continue
    for n, ligne in enumerate(open(chemin, encoding="utf-8"), 1):
        if ligne.lstrip().startswith(("#", "//", "*", "/*")):
            continue
        if re.search(r'replace\(\s*["\']DA_|replace\(\s*["\']da_|replace\(\s*["\']18["\']'
                     r'|_\?18_\?', ligne):
            durs.append(f"{os.path.relpath(chemin, RACINE)}:{n}")
verifier("aucun préfixe ni numéro de set retiré en dur", not durs,
         f"{durs} — passer par M.champion() / M.nom_affichable().")

# Le réseau n'a qu'une porte, sans quoi la répétition ne peut pas rejouer.
portes = []
for chemin in glob.glob(os.path.join(RACINE, "tools", "releve", "*.py")):
    if "urlopen" in open(chemin, encoding="utf-8").read():
        portes.append(os.path.basename(chemin))
verifier("les relevés ne touchent au réseau que par tools/lib/reseau.py",
         not portes, f"urlopen trouvé dans {portes}")

# Tout fichier publié dit de quel set il parle.
muets = []
for nom in ("barre.json", "joueur.json", "compos.json", "recettes.json",
            "focus.json", "objets.json", "compos_lui.json", "fuites.json",
            "miroir.json", "contestation.json"):
    d = donnees(nom)
    if d is not None and not isinstance(d.get("set"), int):
        muets.append(nom)
verifier("tout fichier publié dit de quel set il parle", not muets,
         f"sans champ `set` entier : {muets}")

# Les croisements : deux côtés du même set, ou un refus réellement vide.
for nom, (ca, cb), cle in (("focus.json", ("parties", "meta"), "lignes"),
                           ("objets.json", ("parties", "meta"), "carries"),
                           ("compos_lui.json", ("parties", "meta"), "compos"),
                           ("fuites.json", ("parties", "bareme"), "abandons")):
    d = donnees(nom)
    if d is None:
        continue
    s_ = d.get("sets") or {}
    verifier(f"{nom} ne croise pas deux sets",
             bool(s_) and (s_.get(ca) == s_.get(cb) or not d.get(cle)),
             f"{ca} : {s_.get(ca)} · {cb} : {s_.get(cb)} · "
             f"contenu présent : {bool(d.get(cle))}")


# ══ CE QUE LE SITE NE FAIT PAS ═══════════════════════════════════════════
print("\nCE QUE LE SITE NE FAIT PAS")

# 10/11 : l'onglet « En partie » demandait « les unités que tu as en main »
# et classait les lignes accessibles. La politique de Riot pour les outils
# TFT interdit les recommandations fondées sur l'état d'une partie en cours ;
# le site est public. Les fiches sont statiques : aucune saisie.
verifier("le site ne prend aucune saisie sur la partie en cours",
         not re.search(r"<input|<textarea|<select", site),
         "un champ de saisie est revenu dans site/index.html. Si c'est pour "
         "décrire une partie en cours, il n'a pas sa place ici.")

# Les cotes de boutique : une ligne qui ne somme pas à 100 est une faute de
# recopie. (Les lignes 8 et 9 ont porté une table périmée du 04 au 10/11 —
# elles sommaient à 100, ce test ne l'aurait pas vu ; il attrape le reste.)
fo_ = donnees(os.path.join("reference", "fondamentaux.json"))
if fo_:
    faux = {k: sum(v) for k, v in fo_["cotes_boutique"]["par_niveau"].items()
            if sum(v) != 100}
    verifier("chaque ligne de cotes de boutique somme à 100", not faux, str(faux))
    verifier("les cotes citent au moins deux sources",
             sum(1 for x in fo_.get("sources", [])
                 if "cotes_boutique" in x.get("porte", [])) >= 2,
             "une table recopiée d'une seule source a déjà été fausse une fois.")

print(f"\n{'─' * 60}")
print(f"{PASSES} passés · {len(ECHECS)} échec(s)")
if ECHECS:
    print("\nÉCHECS :")
    for e in ECHECS:
        print(f"  · {e}")
    print("\nUn test qui casse ici n'est pas une régression technique :")
    print("c'est une erreur du projet qui revient.")
sys.exit(1 if ECHECS else 0)
