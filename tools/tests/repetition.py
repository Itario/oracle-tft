#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LA RÉPÉTITION GÉNÉRALE — le changement de set, joué avant qu'il arrive
=======================================================================
    python3 tools/tests/repetition.py            # tous les mondes
    python3 tools/tests/repetition.py jour_j     # un seul
    python3 tools/tests/repetition.py --garder   # garde les dossiers pour y regarder

POURQUOI. Le 1er décembre, tout change le même jour : les identifiants des
unités, le numéro du set, le classement (vide), son rang (remis à zéro), les
volumes (minuscules). Chaque script a été écrit et vérifié dans le monde du
Set 18 en régime de croisière. Aucun n'a jamais vu un jour de sortie.

Attendre le 1er décembre pour le découvrir, c'est refaire l'erreur que ce
projet a déjà payée plusieurs fois : une chaîne qui marche dans le monde où
on l'a écrite n'est pas une chaîne qui marche.

COMMENT. Ce script copie le dépôt dans un dossier jetable, y fabrique les
réponses que les sources donneraient ce jour-là, et fait tourner les VRAIS
scripts — sans en modifier une ligne — dans l'ordre exact des deux workflows,
lus dans les fichiers YAML eux-mêmes. Seul le réseau est remplacé, par le
mode rejeu de tools/lib/reseau.py.

QUATRE MONDES :

    controle     aujourd'hui, rejoué. Doit passer : sinon c'est le rejeu qui
                 est infidèle, et les autres mondes ne prouvent rien.
    jour_j       1er décembre au soir. Set neuf, volumes minuscules,
                 classement vide, joueur non classé, page des compos vide.
    semaine_1    une semaine après. Classement sans Challenger, joueur
                 reclassé en Diamant, ses parties récoltées datent ENCORE du
                 Set 18 — le monde où les croisements entre sets mentent.
                 Et les identifiants ont changé de PRÉFIXE (« MX_ » au lieu
                 de « DA_ ») : personne ne sait comment le Set 19 nommera ses
                 unités, donc rien ne doit en dépendre.
    recolte      même monde, après sa première récolte du Set 19 : neuf
                 parties, sous tous les seuils.

CE QUI EST VÉRIFIÉ, dans chaque monde :

    A  la chaîne ne s'arrête pas     une étape non tolérée qui échoue tue le
                                     job : plus de poussée, plus de site
    B  le relevé du jour est écrit   avec le bon numéro de set
    C  le site parle du set courant  meta/courant.json n'est pas resté au set
                                     précédent
    D  rien ne croise deux sets      ses parties d'un set contre la méta d'un
                                     autre : Ezreal existe dans les deux, et
                                     ce n'est pas la même unité. Un fichier
                                     qui REFUSE de croiser, et le dit, passe
                                     — à condition d'être réellement vide
    E  tout fichier publié dit de    sans quoi le site ne peut ni l'étiqueter
       quel set il parle             ni le cacher
    F  les relevés du jour sont du   barre, position, compos, recettes : un
       set courant                   relevé resté au set précédent se présente
                                     comme courant, et c'est le pire mensonge
    G  les unités restent distinctes si le préfixe change, champion() ne doit
                                     pas réduire tout le set au même nom
    J  le set qui finit est gardé    sa position, sa barre et ses compos sont
                                     copiées dans data/archive/ avant d'être
                                     réécrites par celles du nouveau set
    K  le jeu est du bon set         data/jeu.json (coûts, traits, noms) est du
                                     set courant ou absent — jamais celui du
                                     set d'avant sous le numéro du nouveau.
                                     Et quand le PBE porte le set suivant, le
                                     site l'annonce (monde `controle`)
    I  rien de personnel ne sort     la page du joueur fabriquée porte un
                                     identifiant ; il ne doit se retrouver
                                     dans aucun fichier produit
    H  la page s'affiche             les quatre onglets ouverts dans un vrai
                                     navigateur (tools/tests/rendu.py) : pas
                                     d'erreur, pas de « undefined », et le
                                     bandeau annonce le bon set. Sauté si
                                     Playwright n'est pas installé.
"""

import glob, json, os, re, shutil, subprocess, sys, tempfile

RACINE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

URL_UNITES   = "https://tactics.tools/units"
URL_CDN      = "https://d3.tft.tools/stats2/general/1100/{code}/0"
URL_COMPOS   = "https://tactics.tools/team-compositions"
URL_CDRAGON  = "https://raw.communitydragon.org/latest/cdragon/tft/en_us.json"
URL_CDR_FR   = "https://raw.communitydragon.org/latest/cdragon/tft/fr_fr.json"
URL_PBE      = "https://raw.communitydragon.org/pbe/cdragon/tft/en_us.json"
URL_PBE_FR   = "https://raw.communitydragon.org/pbe/cdragon/tft/fr_fr.json"
URL_BARRE    = "https://tactics.tools/leaderboards/euw"
URL_JOUEUR   = "https://tactics.tools/player/euw/Itario/EUW"


# ══ FABRIQUE DES RÉPONSES ════════════════════════════════════════════════

def page(titre, next_data):
    return (f"<html><head><title>{titre}</title></head><body>"
            f'<script id="__NEXT_DATA__" type="application/json">'
            f"{json.dumps(next_data)}</script></body></html>")


def charger(racine, rel):
    return json.load(open(os.path.join(racine, rel), encoding="utf-8"))


def dernier_releve(racine):
    fs = sorted(glob.glob(os.path.join(racine, "data", "releves-tt", "*.json")))
    return json.load(open(fs[-1], encoding="utf-8"))


PREFIXE = None      # posé par fabriquer() : le préfixe du monde en cours


def vers_set(ident, ancien, nouveau):
    """DA_18_Ezreal -> DA_19_Ezreal ; DA_Lux18_Base -> DA_Lux19_Base.
    Les objets sans numéro (DA_VoidStaff) ne changent que de préfixe, si le
    monde en impose un autre."""
    if isinstance(ident, list):               # certaines listes de la source
        return [vers_set(x, ancien, nouveau) for x in ident]   # sont imbriquées
    if not isinstance(ident, str):
        return ident
    out = re.sub(rf"(?<![0-9]){ancien}(?![0-9])", str(nouveau), ident)
    if PREFIXE and out.startswith("DA_"):
        out = PREFIXE + out[2:]
    return out


def brut_cdn(rel, echelle=1.0, ancien=None, nouveau=None):
    """Reconstitue la réponse du CDN à partir d'un relevé déjà écrit."""
    r = (lambda x: vers_set(x, ancien, nouveau)) if nouveau else (lambda x: x)
    n = lambda v: max(1, int(v * echelle))
    unites = {}
    for k, u in rel["unites"].items():
        e3 = u.get("etoile3") or {}
        unites[r(k)] = {"count": n(u["n"]), "place": u["avg"], "top4": u.get("t4"),
                        "won": u.get("wr"), "topItems": [r(o) for o in u.get("objets", [])],
                        "starCount": n(e3["n"]) if e3.get("n") else 0,
                        "starPlace": e3.get("avg"), "starTop4": e3.get("t4"),
                        "starWon": e3.get("wr")}
    items = [{"itemId": r(k), "count": n(o["n"]), "place": o.get("avg"),
              "top4": o.get("t4"), "won": o.get("wr"),
              "topUsers": [[r(u), d] for u, d in o.get("porteurs", [])]}
             for k, o in rel.get("objets", {}).items()]
    traits = {r(k): {"count": n(t["n"]), "place": t.get("avg"),
                     "top4": t.get("t4"), "won": t.get("wr")}
              for k, t in rel.get("traits", {}).items()}
    return {"totalEntries": n(rel["n_parties"]), "lastUpdated": 1795000000,
            "units": unites, "traits": traits, "items": items, "exalteds": []}


def brut_compos(racine, code, total, echelle=1.0, ancien=None, nouveau=None, vide=False):
    co = charger(racine, "data/compos.json")
    r = (lambda x: vers_set(x, ancien, nouveau)) if nouveau else (lambda x: x)
    n = lambda v: max(1, int((v or 0) * echelle))
    groupes = []
    for c in ([] if vide else co["compos"]):
        nn = n(c["n"])
        groupes.append({"full": {
            "code": c.get("code"), "count": nn, "place": c["place"],
            "top4": int(nn * (c.get("top4_pct") or 50) / 100),
            "win": int(nn * (c.get("premieres_pct") or 12) / 100),
            "lpDelta": c.get("lp_par_partie"),
            "units": [r(u) for u in c.get("unites", [])],
            "traits": [[r(t["trait"]), t["palier"], n(t["n"]), t["place"]] for t in c.get("traits", [])],
            "carryUnits": [[r(p["unite"]), p.get("objets_moy", p.get("etoiles_moy"))] for p in c.get("porteurs", [])],
            "winCons": [[[r(u) for u in w["unites"]], [r(u) for u in w["unites"]], n(w["n"]), w["place"]]
                        for w in c.get("conditions_de_victoire", [])],
            "levels": [[l["niveau"], n(l["n"]), nn] for l in c.get("niveaux", [])],
            "placementDistribution": c.get("distribution"),
            "comps": [{"units": [r(u) for u in (v.get("unites") or [])], "count": n(v["n"]),
                       "place": v["place"], "extraTraits": [r(t) for t in v.get("traits_sup", [])]}
                      for v in c.get("variantes", [])],
            "unitItems": [{"unitId": r(o["unite"]), "itemId": r(o["objet"]),
                           "count": n(o["n"]), "place": o["place"]}
                          for o in c.get("objets_par_unite", [])],
            "augmentSingles": [], "aug1s": [], "aug2s": [], "aug3s": [],
        }, "children": []})
    return {"props": {"pageProps": {
        "aperture": {"patch": {"_0": code}, "rankGroup": 1, "gameType": 0, "queue": 1100},
        "initialData": {"groups": groupes, "count": total, "place": 4.4937}}}}


def brut_cdragon(racine, ancien=None, nouveau=None):
    rec = charger(racine, "data/recettes.json")
    r = (lambda x: vers_set(x, ancien, nouveau)) if nouveau else (lambda x: x)
    items = [{"apiName": r(c), "name": v.get("nom"), "composition": []}
             for c, v in rec["composants"].items()]
    items += [{"apiName": r(k), "name": v.get("nom"), "composition": [r(x) for x in v["de"]]}
              for k, v in rec["recettes"].items()]
    items += [{"apiName": r(k), "name": k, "composition": []} for k in rec.get("sans_recette", [])]
    return {"items": items, "sets": {}}


def bloc_de_set(rel, ancien=None, nouveau=None, fr=False):
    """Le bloc `sets[N]` de CommunityDragon, fabriqué à partir du relevé :
    une unité par champion du relevé, un coût de 1 à 5, deux traits. Plus
    deux entrées hors boutique, parce que le vrai fichier en est plein."""
    r = (lambda x: vers_set(x, ancien, nouveau)) if nouveau else (lambda x: x)
    noms_traits = sorted({t["trait"] for t in (rel.get("traits") or {}).values() if t.get("trait")})
    traits = [{"apiName": r(t), "name": ("Trait " if not fr else "Trait fr ") + str(i),
               "effects": [{"minUnits": 2}, {"minUnits": 4}, {"minUnits": 6}]}
              for i, t in enumerate(noms_traits)]
    champions = []
    for i, ident in enumerate(sorted(rel.get("unites") or {})):
        champions.append({
            "apiName": r(ident), "cost": 1 + i % 5,
            "name": ("Nom " if not fr else "Nom fr ") + str(i),
            "traits": [traits[i % len(traits)]["name"],
                       traits[(i * 7 + 3) % len(traits)]["name"]] if traits else []})
    champions += [{"apiName": "Mannequin", "name": "Target Dummy", "cost": 1, "traits": []},
                  {"apiName": "Invocation", "name": "Summon", "cost": 11, "traits": []}]
    return {"name": "Set fabriqué", "champions": champions, "traits": traits}


def fichiers_du_jeu(racine, rel, monde, ancien, setn):
    """Les quatre fichiers de CommunityDragon pour un monde.

    controle   `latest` porte le set en ligne, et le PBE porte DÉJÀ le
               suivant : c'est le monde des deux semaines avant un lancement.
    jour_j     le relevé est passé au set suivant, mais `latest` est en
               retard de quelques heures : il ne porte encore que l'ancien.
    ensuite    `latest` porte le nouveau set, le PBE aussi, rien au-delà."""
    def fichier(sets, fr=False, renommer=None):
        base = brut_cdragon(racine, *(renommer or (None, None)))
        if fr:
            for it in base["items"]:
                it["name"] = f"{it['name']} (fr)"
        base["sets"] = sets(fr)
        return json.dumps(base)
    if monde == "controle":
        ici = lambda fr: {str(setn): bloc_de_set(rel, fr=fr)}
        pbe = lambda fr: {str(setn): bloc_de_set(rel, fr=fr),
                          str(setn + 1): bloc_de_set(rel, setn, setn + 1, fr=fr)}
        return {URL_CDRAGON: fichier(ici), URL_CDR_FR: fichier(ici, True),
                URL_PBE: fichier(pbe), URL_PBE_FR: fichier(pbe, True)}
    if monde == "jour_j":
        vieux = lambda fr: {str(ancien): bloc_de_set(rel, fr=fr)}
        neuf = lambda fr: {str(setn): bloc_de_set(rel, ancien, setn, fr=fr)}
        return {URL_CDRAGON: fichier(vieux, renommer=(ancien, setn)),
                URL_CDR_FR: fichier(vieux, True, (ancien, setn)),
                URL_PBE: fichier(neuf, renommer=(ancien, setn)),
                URL_PBE_FR: fichier(neuf, True, (ancien, setn))}
    neuf = lambda fr: {str(setn): bloc_de_set(rel, ancien, setn, fr=fr)}
    return {URL_CDRAGON: fichier(neuf, renommer=(ancien, setn)),
            URL_CDR_FR: {"panne": "français indisponible ce jour-là"},
            URL_PBE: fichier(neuf, renommer=(ancien, setn)),
            URL_PBE_FR: fichier(neuf, True, (ancien, setn))}


def brut_barre(mode):
    """mode : 'plein' (300 Challengers), 'sans_challenger', 'vide'."""
    if mode == "vide":
        return {"props": {"pageProps": {"data": {"date": "2026-12-01", "entries": []}}}}
    E = []
    for i in range(1000):
        if mode == "plein":
            palier = "CHALLENGER I" if i < 300 else ("GRANDMASTER I" if i < 900 else "MASTER I")
            lp = 1600 - i
        else:                       # début de saison : tout le monde est encore Master
            palier, lp = "MASTER I", max(0, 420 - i // 2)
        g = 300 - i // 5 if mode == "plein" else 30 + i % 25
        E.append({"rank": [palier, lp], "games": g, "top4": int(g * .55), "won": int(g * .15)})
    return {"props": {"pageProps": {"data": {"date": "2026-12-06", "entries": E}}}}


def parties_joueur(n, code, palier, lp0, t0):
    """n parties classées : placement, LP, rang avant/après."""
    bareme = {1: 55, 2: 42, 3: 24, 4: 11, 5: -10, 6: -21, 7: -35, 8: -52}
    suite = [3, 1, 6, 4, 2, 7, 5, 2, 4, 1, 8, 3, 5, 2, 6, 4, 3, 1, 7, 2, 5, 4]
    out, lp = [], lp0
    for i in range(n):
        pl = suite[i % len(suite)]
        d = bareme[pl]
        apres = max(0, min(99, lp + d))
        out.append({"dateTime": (t0 + i * 5400) * 1000, "patch": code, "queueId": 1100,
                    "duration": 2100, "lpDiff": d,
                    "info": {"placement": pl, "level": 8, "lastRound": 31},
                    "rankBefore": [palier, lp], "rankAfter": [palier, apres]})
        lp = apres
    return list(reversed(out))      # la page donne les plus récentes d'abord


def brut_joueur(etat, code19=None, code18=16220, setn=19):
    """etat : 'master18' (aujourd'hui), 'non_classe' (jour J), 'diamant19'.
    Les noms d'état datent du Set 18 ; les numéros, eux, sont relatifs."""
    info = {"name": "Itario", "tag": "EUW", "region": "euw1",
            "puuid": "IDENTIFIANT-QUI-NE-DOIT-JAMAIS-SORTIR"}
    vieux = parties_joueur(44, code18, "MASTER I", 30, 1793000000)
    if etat == "master18":
        info.update({"rankedLeague": ["MASTER I", 30], "localRank": [3947, 0.0055],
                     "globalRank": [44000, 0.0088]})
        return {"props": {"pageProps": {"initialData": {
            "playerInfo": info, "matches": vieux,
            "rankHistory": [[1793000000 + i * 5400, "MASTER I", 30, 123 - i] for i in range(10)],
            "seasonStats": {"games": 123, "avgPlace": 3.95, "top4": 70, "win": 21,
                            "topCarry": f"DA_{setn - 1}_Ezreal"}}}}}
    if etat == "non_classe":
        info.update({"rankedLeague": None, "localRank": None, "globalRank": None})
        return {"props": {"pageProps": {"initialData": {
            "playerInfo": info, "matches": vieux, "rankHistory": [],
            "seasonStats": {"games": 0, "avgPlace": 0, "top4": 0, "win": 0, "topCarry": None}}}}}
    neufs = parties_joueur(22, code19, "DIAMOND II", 40, 1796000000)
    info.update({"rankedLeague": ["DIAMOND II", 55], "localRank": [5200, 0.012],
                 "globalRank": [61000, 0.02]})
    return {"props": {"pageProps": {"initialData": {
        "playerInfo": info, "matches": neufs + vieux[:28],
        "rankHistory": [[1796000000 + i * 5400, "DIAMOND II", 55, 22 - i] for i in range(22)],
        "seasonStats": {"games": 22, "avgPlace": 3.9, "top4": 13, "win": 4,
                        "topCarry": f"DA_{setn}_Ezreal"}}}}}


def miroir_set19(racine, setn=19):
    """Sa première récolte du set suivant : neuf parties, sous tous les seuils."""
    m = charger(racine, "data/miroir.json")
    pl = [3, 1, 6, 4, 2, 7, 5, 2, 4]
    m.update({
        "set": setn, "n_parties": len(pl), "placement_moyen": round(sum(pl) / len(pl), 3),
        "placement_ecart_type": 2.0, "top4_pct": 66.7, "premieres_pct": 11.1,
        "distribution": {str(k): pl.count(k) for k in range(1, 9)},
        "fenetre": {"de": "2026-12-01", "a": "2026-12-09"},
        "traits": [], "carries": [], "lachees": [], "zone_grise": 0,
        "parties": [{"date": "2026-12-0%d" % (1 + i % 9), "placement": p, "niveau": 8,
                     "rang_niveau": 4, "conversion": 4 - p, "or_restant": 2,
                     "dernier_tour": 30, "pieces": [f"DA_{setn}_Ezreal"]} for i, p in enumerate(pl)],
        "sessions": [], "rythme": None,
    })
    return m


def fabriquer(racine, monde):
    """{url: contenu} pour un monde, et le set que ce monde considère courant."""
    rel = dernier_releve(racine)
    global PREFIXE
    PREFIXE = None
    if monde == "controle":
        code, lib, setn = rel["patch_code"], rel["patch"], rel["set"]
        cdn = brut_cdn(rel)
        return setn, {
            URL_UNITES: page(f"TFT Units Stats - Best Units for Set {setn} Patch {lib}",
                             {"props": {"pageProps": {"aperture": {"patch": {"_0": code}}}}}),
            URL_CDN.format(code=code): json.dumps(cdn),
            URL_COMPOS: page("TFT Meta Stats", brut_compos(racine, code, int(cdn["totalEntries"] * .985))),
            **fichiers_du_jeu(racine, rel, monde, setn, setn),
            URL_BARRE: page("Leaderboards", brut_barre("plein")),
            URL_JOUEUR: page("Itario", brut_joueur("master18", code18=code, setn=setn + 1)),
        }

    # Le monde suivant est RELATIF au relevé du jour : set + 1, premier patch,
    # un code de patch plus grand. Écrit « 19 » en dur, il aurait cessé de
    # représenter un changement de set le jour où le Set 19 serait en ligne.
    ancien = rel["set"]
    setn = ancien + 1
    code, lib = (rel.get("patch_code") or 16220) + 30, f"{setn}.1"
    code_avant = rel.get("patch_code") or 16220
    PREFIXE = None if monde == "jour_j" else "MX"
    if monde == "jour_j":
        cdn = brut_cdn(rel, echelle=0.02, ancien=ancien, nouveau=setn)
        compos = brut_compos(racine, code, 0, vide=True)
        barre, joueur = brut_barre("vide"), brut_joueur("non_classe", code18=code_avant, setn=setn)
    else:                           # semaine_1 et recolte
        cdn = brut_cdn(rel, echelle=0.45, ancien=ancien, nouveau=setn)
        compos = brut_compos(racine, code, int(cdn["totalEntries"] * .98),
                             echelle=0.45, ancien=ancien, nouveau=setn)
        barre, joueur = (brut_barre("sans_challenger"),
                         brut_joueur("diamant19", code, code18=code_avant, setn=setn))
    return setn, {
        URL_UNITES: page(f"TFT Units Stats - Best Units for Set {setn} Patch {lib}",
                         {"props": {"pageProps": {"aperture": {"patch": {"_0": code}}}}}),
        URL_CDN.format(code=code): json.dumps(cdn),
        URL_COMPOS: page("TFT Meta Stats", compos),
        **fichiers_du_jeu(racine, rel, monde, ancien, setn),
        URL_BARRE: page("Leaderboards", barre),
        URL_JOUEUR: page("Itario", joueur),
    }


# ══ LA CHAÎNE, LUE DANS LES WORKFLOWS ════════════════════════════════════

def etapes(racine):
    """[(commande, tolérée)] dans l'ordre réel : le relevé, puis le déploiement.

    Lue dans les YAML et non recopiée ici : une liste recopiée dériverait, et
    la répétition validerait alors une chaîne qui n'est plus celle qui tourne."""
    out = []
    for f in ("releve.yml", "deploy.yml"):
        txt = open(os.path.join(racine, ".github", "workflows", f), encoding="utf-8").read()
        for bloc in re.split(r"\n      - (?=name:|uses:)", txt):
            tol_bloc = bool(re.search(r"continue-on-error:\s*true", bloc))
            for ligne in bloc.split("\n"):
                m = re.search(r"(python3 tools/[\w/]+\.py[^|\\]*)", ligne)
                if not m or ligne.strip().startswith("#"):
                    continue
                cmd = m.group(1).strip()
                # ⚠ test_socle.py FAIT PARTIE DE LA CHAÎNE : il tourne dans les
                # deux workflows, sans tolérance, et un test qui casse le jour
                # du changement de set tue le relevé aussi sûrement qu'un
                # script qui plante. La première version de cette répétition
                # l'écartait (« pas de test dans le test ») : elle validait
                # donc une chaîne plus courte que celle qui tourne. Seule la
                # répétition elle-même est écartée, pour ne pas boucler.
                if "repetition.py" in cmd:
                    continue
                # les expressions GitHub n'ont pas de sens hors du runner
                cmd = re.sub(r'"?\$\{\{[^}]*\}\}"?', "", cmd).replace("--rang  ", "").strip()
                cmd = re.sub(r"\s+--rang\s*$", "", cmd)
                out.append((cmd, tol_bloc or "||" in ligne, f))
    return out


def jouer(monde, garder=False):
    tmp = tempfile.mkdtemp(prefix=f"oracle_{monde}_")
    copie = os.path.join(tmp, "depot")
    shutil.copytree(RACINE, copie, ignore=shutil.ignore_patterns(
        ".git", "parties", "__pycache__", "node_modules"))
    setn, reponses = fabriquer(copie, monde)

    rejeu = os.path.join(tmp, "rejeu")
    os.makedirs(rejeu)
    index = {}
    for i, (url, contenu) in enumerate(reponses.items()):
        if isinstance(contenu, dict):          # {"http": 404} ou {"panne": "…"}
            index[url] = contenu
            continue
        nom = f"r{i}.txt"
        open(os.path.join(rejeu, nom), "w", encoding="utf-8").write(contenu)
        index[url] = nom
    json.dump(index, open(os.path.join(rejeu, "index.json"), "w"))

    if monde == "recolte":
        json.dump(miroir_set19(copie, setn), open(os.path.join(copie, "data", "miroir.json"), "w",
                                            encoding="utf-8"), ensure_ascii=False)

    env = dict(os.environ, ORACLE_REJEU=rejeu)
    journal = []
    for cmd, toleree, source in etapes(copie):
        p = subprocess.run(["python3", "-I"] + cmd.split()[1:], cwd=copie, env=env,
                           capture_output=True, text=True)
        derniere = ((p.stderr or p.stdout).strip().split("\n") or [""])[-1][:150]
        journal.append({"cmd": cmd, "code": p.returncode, "toleree": toleree,
                        "source": source, "dit": derniere,
                        "sortie": (p.stdout + p.stderr)[-1500:]})
    return {"monde": monde, "set": setn, "copie": copie, "tmp": tmp, "journal": journal}


# ══ LES VÉRIFICATIONS ════════════════════════════════════════════════════

# Les fichiers qui croisent SES parties avec la méta : ils ne valent que si
# les deux côtés parlent du même set.
# Par fichier : les deux côtés du croisement, et ce qui en constitue le
# contenu croisé — ce qui doit être VIDE quand les sets diffèrent.
CROISES = {
    "focus.json":        (("parties", "meta"), lambda o: o.get("lignes") or o.get("fortes_peu_contestees")),
    "objets.json":       (("parties", "meta"), lambda o: o.get("carries")),
    "compos_lui.json":   (("parties", "meta"), lambda o: o.get("compos")),
    "contestation.json": (("parties", "meta"), lambda o: [c for c in (o.get("par_champion") or [])
                                                            if c.get("presence_attendue") is not None]),
    "fuites.json":       (("parties", "bareme"), lambda o: o.get("abandons")),
}
RELEVES_DU_JOUR = ("barre.json", "joueur.json", "compos.json", "recettes.json")


CAPTURES = None      # --captures DOSSIER : une image par onglet et par monde


def verifier(res):
    copie, W, monde = res["copie"], res["set"], res.get("monde", "monde")
    constats = []
    def c(lettre, nom, ok, detail=""):
        constats.append({"lettre": lettre, "nom": nom, "ok": bool(ok), "detail": detail})

    # A — la chaîne ne s'arrête pas
    morts = [j for j in res["journal"] if j["code"] != 0 and not j["toleree"]]
    c("A", "la chaîne ne s'arrête pas", not morts,
      " ; ".join(f"{j['cmd'].split('/')[-1]} sort en {j['code']} : {j['dit']}" for j in morts))

    # B — le relevé du jour est écrit, avec le bon set
    rels = [json.load(open(f, encoding="utf-8")) for f in
            sorted(glob.glob(os.path.join(copie, "data", "releves-tt", "*.json")))]
    c("B", f"un relevé du set {W} est écrit", any(r.get("set") == W for r in rels),
      f"sets présents : {sorted({r.get('set') for r in rels})}")

    # C — le site parle du set courant
    try:
        meta = charger(copie, "site/data/meta/courant.json")
        c("C", f"le site parle du set {W}", (meta.get("releve") or {}).get("set") == W,
          f"meta/courant.json : set {(meta.get('releve') or {}).get('set')}, "
          f"patch {(meta.get('releve') or {}).get('patch')}, du {(meta.get('releve') or {}).get('date')}")
    except Exception as e:
        c("C", f"le site parle du set {W}", False, f"meta/courant.json illisible : {e}")

    # D — rien ne croise deux sets
    for f, ((ca, cb), contenu) in CROISES.items():
        p = os.path.join(copie, "site", "data", f)
        if not os.path.exists(p):
            continue
        o = json.load(open(p, encoding="utf-8"))
        s = o.get("sets") or {}
        if not s:
            c("D", f"{f} ne croise pas deux sets", False,
              "le fichier ne dit pas de quels sets viennent ses deux côtés")
        elif s.get(ca) == s.get(cb):
            c("D", f"{f} ne croise pas deux sets", True)
        else:
            # Sets différents : acceptable seulement si le fichier le dit ET
            # ne contient réellement aucun croisement.
            reste = contenu(o)
            c("D", f"{f} ne croise pas deux sets",
              o.get("etat") not in (None, "ok") and not reste,
              f"{ca} : set {s.get(ca)} · {cb} : set {s.get(cb)} · état « {o.get('etat')} »"
              + (" · MAIS du contenu croisé est présent" if reste else ""))

    # E — tout fichier publié dit de quel set il parle
    muets = []
    for p in sorted(glob.glob(os.path.join(copie, "site", "data", "*.json"))):
        nom = os.path.basename(p)
        if nom in ("calendrier.json", "profil.json"):
            continue                              # ni l'un ni l'autre n'est lié à un set
        if not isinstance(json.load(open(p, encoding="utf-8")).get("set"), int):
            muets.append(nom)
    c("E", "tout fichier publié dit de quel set il parle", not muets,
      "sans champ `set` : " + ", ".join(muets))

    # F — les relevés du jour sont du set courant
    retard = []
    for nom in RELEVES_DU_JOUR:
        p = os.path.join(copie, "site", "data", nom)
        if not os.path.exists(p):
            retard.append(f"{nom} absent")
            continue
        s = json.load(open(p, encoding="utf-8")).get("set")
        if s != W:
            retard.append(f"{nom} (set {s})")
    c("F", f"les relevés du jour sont du set {W}", not retard, " · ".join(retard))

    # G — les unités restent distinctes (le préfixe n'est pas une constante)
    try:
        p = subprocess.run(
            ["python3", "-I", "-c",
             "import sys, json; sys.path.insert(0, 'tools/lib'); import mesures as M; "
             "r = M.releve_courant(); ids = list(r['unites']); "
             "print(json.dumps([len(ids), len({M.champion(i) for i in ids}), "
             "sorted({M.nom_affichable(i) for i in ids})[:3]]))"],
            cwd=copie, capture_output=True, text=True)
        n_ids, n_champ, ex = json.loads(p.stdout.strip().split("\n")[-1])
        c("G", "les unités restent distinctes", n_champ >= 0.6 * n_ids,
          f"{n_ids} identifiants -> {n_champ} champions distincts (ex. {ex})")
    except Exception as e:
        c("G", "les unités restent distinctes", False, f"mesure impossible : {e}")

    # J — le set précédent est archivé avant d'être écrasé
    if res.get("monde") != "controle":
        arch = os.path.join(copie, "data", "archive", f"set{W - 1}")
        attendus = ("joueur.json", "barre.json", "compos.json")
        etat = {}
        for nom in attendus:
            try:
                etat[nom] = json.load(open(os.path.join(arch, nom), encoding="utf-8")).get("set")
            except Exception:
                etat[nom] = "absent"
        c("J", f"le set {W - 1} est archivé avant d'être écrasé",
          all(v == W - 1 for v in etat.values()),
          " · ".join(f"{k} : {v}" for k, v in etat.items()))

    # K — les données du jeu : du bon set, et le set à venir quand il existe
    try:
        meta = json.load(open(os.path.join(copie, "site", "data", "meta", "courant.json"),
                              encoding="utf-8"))
        jp = os.path.join(copie, "data", "jeu.json")
        jeu = json.load(open(jp, encoding="utf-8")) if os.path.exists(jp) else None
        if monde == "jour_j":
            # `latest` est en retard : jeu.json ne doit PAS avoir été réécrit
            # pour le nouveau set, et le site ne doit pas s'en servir.
            c("K", "un jeu en retard d'un set n'est pas utilisé",
              (jeu is None or jeu.get("set") != W) and not meta["jeu"]["du_set"],
              f"jeu.json : set {(jeu or {}).get('set')} · utilisé par le site : {meta['jeu']['du_set']}")
        else:
            c("K", f"les données du jeu sont du set {W}",
              bool(jeu) and jeu.get("set") == W and meta["jeu"]["du_set"]
              and len(jeu.get("unites") or {}) >= 20 and "Mannequin" not in jeu["unites"],
              f"set {(jeu or {}).get('set')} · {len((jeu or {}).get('unites') or {})} unités")
        if monde == "controle":
            a = meta.get("a_venir") or {}
            c("K", f"le set {W + 1}, vu au PBE, est annoncé par le site",
              a.get("set") == W + 1 and a.get("n_unites", 0) >= 20 and len(a.get("par_cout") or []) == 5,
              f"a_venir : set {a.get('set')}, {a.get('n_unites')} unités")
        else:
            c("K", "aucun set à venir n'est inventé", not meta.get("a_venir"),
              f"a_venir : {meta.get('a_venir') and meta['a_venir'].get('set')}")
    except Exception as e:
        c("K", "les données du jeu se vérifient", False, f"{type(e).__name__} : {e}")

    # I — l'identifiant de la page du joueur ne sort nulle part
    fuites_id = []
    for base in ("data", "site"):
        for dossier, _, fichiers in os.walk(os.path.join(copie, base)):
            for f in fichiers:
                if not f.endswith((".json", ".html", ".js")):
                    continue
                txt = open(os.path.join(dossier, f), encoding="utf-8", errors="replace").read()
                if "IDENTIFIANT-QUI-NE-DOIT-JAMAIS-SORTIR" in txt or \
                        ("pu" + "uid") in txt.lower():
                    fuites_id.append(os.path.relpath(os.path.join(dossier, f), copie))
    c("I", "aucun identifiant personnel dans ce qui est produit", not fuites_id,
      ", ".join(fuites_id))

    # H — la page s'affiche, dans un vrai navigateur
    try:
        sys.path.insert(0, os.path.join(RACINE, "tools", "tests"))
        import rendu
        cap = (os.path.join(CAPTURES, monde) if CAPTURES else None)
        r = rendu.controler(os.path.join(copie, "site"), cap)
        if r is not None:
            soucis = r["erreurs"] + r["suspects"]
            c("H", "la page s'affiche sans erreur", not soucis, " | ".join(soucis[:4]))
            c("H", f"le bandeau annonce le set {W}", f"Set {W}" in (r["bandeau"] or ""),
              f"bandeau : {r['bandeau']}")
    except Exception as e:
        c("H", "la page s'affiche sans erreur", False, f"contrôle impossible : {e}")
    return constats


def main():
    global CAPTURES
    argv = sys.argv[1:]
    if "--captures" in argv:
        i = argv.index("--captures")
        CAPTURES = os.path.abspath(argv[i + 1])
        del argv[i:i + 2]
    args = [a for a in argv if not a.startswith("--")]
    garder = "--garder" in argv
    mondes = args or ["controle", "jour_j", "semaine_1", "recolte"]
    echecs = 0
    for monde in mondes:
        res = jouer(monde, garder)
        res["monde"] = monde
        print(f"\n{'═' * 70}\nMONDE : {monde}   (set courant de ce monde : {res['set']})\n{'═' * 70}")
        for j in res["journal"]:
            etat = "ok   " if j["code"] == 0 else ("toléré" if j["toleree"] else "MORT ")
            print(f"  {etat} {j['cmd'][:58]:<58} {'' if j['code'] == 0 else '← ' + j['dit'][:70]}")
        print()
        for k in verifier(res):
            if not k["ok"]:
                echecs += 1
            print(f"  [{'ok' if k['ok'] else 'ÉCHEC'}] {k['lettre']} · {k['nom']}"
                  + (f"\n          {k['detail']}" if (k["detail"] and not k["ok"]) else ""))
        if garder:
            print(f"\n  dossier gardé : {res['copie']}")
        else:
            shutil.rmtree(res["tmp"], ignore_errors=True)
    print(f"\n{'─' * 70}\n{echecs} échec(s) sur {len(mondes)} monde(s)")
    sys.exit(1 if echecs else 0)


if __name__ == "__main__":
    main()
