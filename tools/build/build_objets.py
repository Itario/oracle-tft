#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LES OBJETS — en composants, parce que c'est comme ça qu'on les fabrique
========================================================================
Lit  : data/miroir.json (ses carries) + le dernier data/releves-tt/ (le BiS
       mesuré de chaque unité) + data/recettes.json (la table de Riot)
Écrit: data/objets.json  -> onglet « Avant »

─── POURQUOI PAS UN CLASSEMENT D'OBJETS FINIS ──────────────────────────────
La première version de ce fichier allait trier les 126 objets par taux de
victoire. Clément a corrigé, et il avait raison : **un objet fini ne se
choisit pas, il se fabrique.** On ramasse des composants sur les tours de
monstres et aux carrousels, et les vraies décisions sont :

    au carrousel : quel composant prendre, sachant ce que je tiens déjà ?
    en partie    : je slamme maintenant pour le tempo, ou je garde le BiS ?

Un classement d'objets finis ne répond à aucune des deux. Ce fichier raisonne
donc en COMPOSANTS, et produit trois choses :

**1. Le BiS de chaque carry qu'il joue vraiment.** Pas des 74 unités du jeu :
   des douze qu'il sort assez souvent pour que ça le concerne.

**2. La liste de courses en composants.** Le BiS décomposé : « pour monter
   Ezreal correctement il faut telle et telle pièce ». C'est ce qui se lit au
   carrousel, pas un nom d'objet fini.

**3. Les composants POLYVALENTS.** Celui qui alimente le BiS de plusieurs de
   ses carries est un pari sûr au carrousel, parce qu'il reste utile quel que
   soit le pivot. Celui qui ne sert qu'à une seule unité engage la partie.
   *C'est le seul vrai conseil de priorisation que la donnée permette.*

─── CE QUE CE FICHIER NE DIT PAS ──────────────────────────────────────────
**IL NE DÉCIDE PAS DES SLAMS.** Slammer dépend des points de vie, du tempo,
de la force du plateau et de ce que font les sept autres — rien de tout cela
n'est dans la donnée. Ce qu'il donne, c'est la seule moitié objective de la
question : **un slam est GRATUIT si l'objet figure déjà au BiS d'un de ses
carries, et c'est un vrai arbitrage sinon.** Le reste est son jugement.

**LE BiS EST UN CLASSEMENT DE FRÉQUENCE, PAS D'EFFET.** `topItems` liste les
objets les plus PORTÉS sur l'unité, pas ceux qui la font le mieux placer. Les
deux coïncident souvent — les bons joueurs construisent bien — mais c'est une
hypothèse, pas une mesure. `porteurs`, lui, porte un effet mesuré : on
l'affiche à côté quand il existe.

**ET LE BIAIS DE SURVIE S'APPLIQUE ICI AUSSI.** Un objet « porté sur un
board final » l'a été dans une partie qui s'est assez bien passée pour qu'il
soit construit.
"""

import glob, json, os, re, sys
from collections import Counter, defaultdict
from datetime import date

RACINE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SORTIE = os.path.join(RACINE, "data", "objets.json")
SCHEMA = 1
VOL_MIN = 3000     # sous ce volume, le BiS d'une unité n'est pas lisible


def champion(ident):
    """Le champion, sans sa variante ni son numéro de set.

    Repris de build_focus.py : tactics.tools éclate Lux en dix entrées, et
    sans ce regroupement chaque variante compte pour une unité distincte."""
    toks = [re.sub(r"\d+", "", t) for t in str(ident).split("_") if t and t != "DA"]
    toks = [t for t in toks if t]
    return toks[0].lower() if toks else ""


def charger(chemin):
    try:
        return json.load(open(chemin, encoding="utf-8"))
    except Exception:
        return None


def main():
    mi = charger(os.path.join(RACINE, "data", "miroir.json"))
    rec = charger(os.path.join(RACINE, "data", "recettes.json"))
    fs = sorted(glob.glob(os.path.join(RACINE, "data", "releves-tt", "*.json")))
    if not mi:
        sys.exit("data/miroir.json absent — lance build_miroir.py.")
    if not fs:
        sys.exit("Aucun relevé dans data/releves-tt/ — lance tactics.py.")
    rel = json.load(open(fs[-1], encoding="utf-8"))

    # ── ⚠ UN PATCH FRAIS DONNE UN BiS FRAGILE ────────────────────────────
    # Le BiS est un classement de FRÉQUENCE sur les cinq objets les plus
    # portés. À 11 % du volume d'un patch mûr — 54 954 parties pour 18.6 le
    # jour de sa sortie, contre 500 777 pour 18.5c — l'ordre de ces cinq
    # peut se brouiller sans que rien ne le signale, exactement comme le
    # Spearman ne signalait pas le changement de sous-ensemble (leçon n°39).
    #
    # On ne devine pas un seuil absolu : on compare au relevé PRÉCÉDENT de la
    # même série, qui est mûr. En dessous de la moitié, on le dit.
    precedent = None
    if len(fs) >= 2:
        try:
            precedent = json.load(open(fs[-2], encoding="utf-8"))
        except Exception:
            precedent = None
    n_cour = rel.get("n_parties") or 0
    n_prec = (precedent or {}).get("n_parties") or 0
    frais = bool(n_prec and n_cour < 0.5 * n_prec)

    if not rel.get("objets"):
        sys.exit(f"{os.path.basename(fs[-1])} ne porte pas de bloc `objets`. "
                 "C'est un relevé antérieur au 04/11 : relance tactics.py "
                 "--forcer.")
    if not rec:
        sys.exit("data/recettes.json absent — lance tools/releve/recettes.py.")

    recettes = rec.get("recettes") or {}
    composants = rec.get("composants") or {}
    nom_fr = {c: v.get("fr") or v.get("nom") or c for c, v in composants.items()}
    objets_meta = rel.get("objets") or {}

    # ── Regrouper les variantes d'une même unité ─────────────────────────
    # Lux éclatée en dix entrées donnerait dix BiS différents pour un seul
    # champion. On garde, par champion, la variante la PLUS JOUÉE : c'est
    # celle dont le BiS décrit ce que le ladder construit réellement.
    par_champ = {}
    for uid, u in (rel.get("unites") or {}).items():
        if not u.get("objets") or (u.get("n") or 0) < VOL_MIN:
            continue
        c = champion(uid)
        if not c:
            continue
        if c not in par_champ or u["n"] > par_champ[c]["n"]:
            par_champ[c] = {**u, "_id": uid}

    # ── Ses carries, et leur BiS ─────────────────────────────────────────
    siens, absents = [], []
    for car in (mi.get("carries") or []):
        c = champion(car["nom"])
        u = par_champ.get(c)
        if not u:
            absents.append(car["nom"])
            continue

        bis = []
        for oid in u["objets"]:
            r = recettes.get(oid)
            om = objets_meta.get(oid) or {}
            # L'effet mesuré de CET objet sur CETTE unité, quand la source
            # le donne. C'est la seule valeur du bloc qui soit un effet et
            # non une fréquence.
            effet = None
            for porteur, delta in (om.get("porteurs") or []):
                if champion(porteur) == c:
                    effet = delta
                    break
            bis.append({
                "objet": oid,
                "nom": (r or {}).get("nom") or oid.replace("DA_", ""),
                "composants": [nom_fr.get(x, x) for x in (r or {}).get("de", [])],
                "craftable": bool(r),
                "place_objet": om.get("avg"),
                "n_objet": om.get("n"),
                "effet_sur_cette_unite": effet,
            })

        # La liste de courses : tous les composants du BiS, avec combien de
        # fois chacun y apparaît. Deux épées dans le BiS, c'est deux épées
        # à ramasser, pas une.
        besoins = Counter()
        for b in bis:
            for x in b["composants"]:
                besoins[x] += 1

        siens.append({
            "carry": car["nom"],
            "unite_meta": u["_id"],
            "n_parties_lui": car["n"],
            "sa_place": car["placement"],
            "son_ecart": car["ecart"],
            "solide": car["solide"],
            "place_ladder": u.get("avg"),
            "n_ladder": u.get("n"),
            "etoile3": u.get("etoile3"),
            "bis": bis,
            "composants_requis": [{"composant": k, "fois": v}
                                  for k, v in besoins.most_common()],
        })

    # ── LE CHIFFRE QUI SERT AU CARROUSEL ─────────────────────────────────
    # Pour chaque composant : combien de SES carries en ont besoin, et
    # lesquels. Un composant qui en alimente huit se prend sans réfléchir ;
    # un qui n'en alimente qu'un engage la partie.
    polyvalence = defaultdict(set)
    for s in siens:
        for b in s["bis"]:
            for x in b["composants"]:
                polyvalence[x].add(s["carry"])

    carrousel = sorted(
        ({"composant": k, "n_carries": len(v), "carries": sorted(v)}
         for k, v in polyvalence.items()),
        key=lambda d: -d["n_carries"])

    # ── LES SLAMS GRATUITS ───────────────────────────────────────────────
    # Un objet qui figure au BiS d'au moins un de ses carries ne coûte rien
    # à construire tôt : il servira. C'est la seule moitié de la décision de
    # slam que la donnée puisse trancher.
    gratuits = defaultdict(set)
    for s in siens:
        for b in s["bis"]:
            if b["craftable"]:
                gratuits[b["objet"]].add(s["carry"])
    slams = sorted(
        ({"objet": k, "nom": (recettes.get(k) or {}).get("nom") or k,
          "composants": [nom_fr.get(x, x) for x in (recettes.get(k) or {}).get("de", [])],
          "n_carries": len(v), "carries": sorted(v),
          "place_objet": (objets_meta.get(k) or {}).get("avg")}
         for k, v in gratuits.items()),
        key=lambda d: (-d["n_carries"], d["place_objet"] or 9))

    out = {
        "schema_version": SCHEMA,
        "genere_le": date.today().isoformat(),
        "patch": rel.get("patch"),
        "rang": rel.get("rang"),
        "n_parties_ladder": rel.get("n_parties"),
        "source": "tactics.tools (BiS et effets) + CommunityDragon (recettes)",
        "carries": siens,
        "carrousel": carrousel,
        "slams_gratuits": slams,
        "carries_sans_correspondance": absents,
        "fraicheur": {
            "n_parties": n_cour,
            "n_parties_patch_precedent": n_prec or None,
            "patch_precedent": (precedent or {}).get("patch"),
            "patch_frais": frais,
            # ⚠ Les séparateurs de milliers se formatent AVANT, pas en
            # nettoyant la phrase : un .replace(",", " ") sur la chaîne
            # entière mange aussi les virgules grammaticales — il avait
            # produit « à ce volume  l'ordre ».
            "avertissement": (
                f"Le patch {rel.get('patch')} vient de sortir : "
                f"{n_cour:,}".replace(",", " ")
                + f" parties contre {n_prec:,}".replace(",", " ")
                + f" pour {(precedent or {}).get('patch')}. "
                "Le BiS est un classement de FRÉQUENCE — à ce volume, l'ordre "
                "des cinq objets peut encore bouger. Les composants "
                "polyvalents, eux, tiennent mieux : ils agrègent cinq objets "
                "sur douze carries, donc beaucoup plus de parties que chaque "
                "objet pris isolément."
            ) if frais else None,
        },
        "reserves": {
            "bis_est_une_frequence": (
                "`topItems` liste les objets les plus PORTÉS sur l'unité, pas "
                "ceux qui la font le mieux placer. Les deux coïncident "
                "souvent, mais c'est une hypothèse. `effet_sur_cette_unite` "
                "porte un effet mesuré quand la source le donne — un delta "
                "NÉGATIF veut dire meilleur placement."),
            "pas_de_decision_de_slam": (
                "Slammer dépend des PV, du tempo, de la force du plateau et "
                "des sept autres joueurs : rien de cela n'est dans la donnée. "
                "Ce fichier dit seulement qu'un slam est GRATUIT si l'objet "
                "est déjà au BiS d'un de tes carries, et un vrai arbitrage "
                "sinon."),
            "biais_de_survie": (
                "Un objet « porté sur un board final » l'a été dans une "
                "partie qui s'est assez bien passée pour qu'on le construise."),
        },
    }

    os.makedirs(os.path.dirname(SORTIE), exist_ok=True)
    json.dump(out, open(SORTIE, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    print(f"écrit : {SORTIE}")
    print(f"  {len(siens)} de ses carries appariés au relevé {rel.get('patch')}"
          + (f" · {len(absents)} sans correspondance : {', '.join(absents)}"
             if absents else ""))
    print("  au carrousel, ses composants les plus polyvalents :")
    for c in carrousel[:5]:
        print(f"    {c['composant']:<10} sert à {c['n_carries']} de ses carries")
    print("  slams les plus sûrs (au BiS du plus grand nombre de ses carries) :")
    for s in slams[:5]:
        print(f"    {s['nom']:<22} {' + '.join(s['composants']):<22} "
              f"{s['n_carries']} carries")


if __name__ == "__main__":
    main()
