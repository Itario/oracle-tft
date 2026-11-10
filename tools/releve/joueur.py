#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LE JOUEUR — où Clément en est, en LP -> data/joueur.json
=========================================================
Jusqu'ici le site affichait « Master, 55 LP » : un chiffre relevé à la main
le 22 octobre. Le 4 novembre, le vrai chiffre était 39. Treize jours de
retard sur la seule mesure que l'objectif du projet concerne directement.

Ce script relève la position réelle sur la page publique du joueur, sans
navigateur et sans clé API, depuis le runner GitHub. Il tourne huit fois
par jour avec le reste du relevé.

    python3 tools/releve/joueur.py
    python3 tools/releve/joueur.py --region euw --nom Itario --tag EUW

⚠ Comme tactics.py et barre.py : ne tourne pas depuis une session Claude,
le proxy du conteneur bloque le domaine. Fait pour le runner GitHub.

─── CE QUE CE FICHIER APPORTE DE NEUF ─────────────────────────────────────
Chaque partie de la page porte `lpDiff` : le LP réellement gagné ou perdu.
C'est la monnaie du classement, mesurée et non déduite d'un placement.

Et au-dessus de Master, **il n'y a plus de palier**. De Master 0 LP jusqu'à
Challenger, c'est une seule échelle continue — pas de division à repasser,
pas de série de promotion. Donc un LP/partie mesuré en Master se projette
directement jusqu'à la barre. C'est ce qui transforme « passer Challenger »
en un nombre de parties.

─── CE QUE CE FICHIER NE DIT PAS ──────────────────────────────────────────
1. LES GAINS SE COMPRIMENT QUAND ON MONTE. Le LP accordé pour un placement
   donné dépend de l'écart entre le MMR et le LP affiché : un joueur dont le
   MMR dépasse son rang gagne gros, et ce surplus s'épuise en montant. La
   table mesurée ici l'est à son MMR d'octobre. La projection est donc
   OPTIMISTE par construction — une borne basse sur la difficulté, pas une
   prévision.
2. LE PLACEMENT DÉRIVE VERS 4.50. Son 3.737 est mesuré dans des lobbies
   Diamant/Master. Plus haut, les adversaires sont meilleurs et le placement
   moyen remonte mécaniquement. Deux effets qui vont dans le même sens :
   la projection est un plafond de vitesse, jamais un calendrier.
3. LES DÉFAITES ÉCRÊTÉES SONT EXCLUES. À 5 LP d'une fin de division, une
   7e place ne retire que 5 LP : la protection de rétrogradation tronque la
   perte. Garder ces parties aplatirait la table du bas. `censurees` compte
   celles qu'on a écartées.
"""

import argparse, json, math, os, re, statistics as st, sys
import urllib.error, urllib.request
from datetime import date, datetime, timezone

RACINE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# La seule porte vers l'extérieur vit dans tools/lib/reseau.py : une définition,
# et un mode rejeu qui permet de répéter le 1er décembre sans réseau.
sys.path.insert(0, os.path.join(RACINE, "tools", "lib"))
from reseau import lire as _lire
import mesures as M


def lire(url, **kw):
    return _lire(url, quoi="relevé de position", **kw)

SORTIE = os.path.join(RACINE, "data", "joueur.json")
BARRE  = os.path.join(RACINE, "data", "barre.json")
MIROIR = os.path.join(RACINE, "data", "miroir.json")
SCHEMA = 1
PAGE   = "https://tactics.tools/player/{region}/{nom}/{tag}"

# Au-dessus de Master, une seule échelle continue. En dessous, les divisions
# remettent le compteur à zéro : les LP n'y sont pas sur la même règle.
HAUT = ("MASTER", "GRANDMASTER", "CHALLENGER")
# Sous Master : sept paliers de quatre divisions, 100 LP par division.
PALIERS = ("IRON", "BRONZE", "SILVER", "GOLD", "PLATINUM", "EMERALD", "DIAMOND")
DIVISIONS = {"IV": 0, "III": 1, "II": 2, "I": 3}


def lp_jusqu_a_master(palier, lp):
    """Combien de LP séparent ce rang de Master 0 LP.

    Diamant II 55 LP : il reste 45 LP pour finir la division, puis les
    100 LP de Diamant I. Les LP en trop sont reportés à la promotion et TFT
    n'a pas de série de promotion : le compte est exact, à la protection de
    rétrogradation près (qui ne joue qu'à la baisse).

    None si le palier est déjà Master ou plus, ou s'il est illisible."""
    mots = str(palier or "").split(" ")
    if mots[0] in HAUT or mots[0] not in PALIERS:
        return None
    div = DIVISIONS.get(mots[1] if len(mots) > 1 else "", None)
    if div is None:
        return None
    divisions_restantes = (len(PALIERS) - 1 - PALIERS.index(mots[0])) * 4 + (3 - div)
    return divisions_restantes * 100 + (100 - (lp or 0))





def charger_json(chemin):
    try:
        return json.load(open(chemin, encoding="utf-8"))
    except Exception:
        return None


def ajustement(points):
    """Moindres carrés de lp sur le placement : lp = a + b·placement.

    Deux paramètres au lieu d'une table de huit cases. À une quarantaine de
    parties, une table laisse des cases à une seule observation (la 8e place
    n'apparaît qu'une fois) ; la droite, elle, utilise toutes les parties pour
    estimer chaque point. Le gain de LP est quasi linéaire en placement : ce
    n'est pas une commodité, c'est la forme réelle du barème.

    Renvoie aussi l'écart-type des résidus : c'est lui qui dit si la droite
    décrit quoi que ce chose, et il porte le seuil de bruit de la projection.
    """
    n = len(points)
    if n < 6:
        return None
    sx  = sum(p for p, _ in points)
    sy  = sum(l for _, l in points)
    sxx = sum(p * p for p, _ in points)
    sxy = sum(p * l for p, l in points)
    den = n * sxx - sx * sx
    if den == 0:
        return None
    b = (n * sxy - sx * sy) / den
    a = (sy - b * sx) / n
    res = [l - (a + b * p) for p, l in points]
    sd  = st.stdev(res) if n > 2 else 0.0
    # R² : la part de la variation des LP que le placement explique.
    moy = sy / n
    sct = sum((l - moy) ** 2 for _, l in points)
    scr = sum(r * r for r in res)
    return {
        "n": n,
        "pente_lp_par_place": round(b, 2),
        "ordonnee": round(a, 2),
        "place_neutre": round(-a / b, 2) if b else None,
        "sd_residus": round(sd, 2),
        "r2": round(1 - scr / sct, 3) if sct else None,
        "_a": a, "_b": b, "_sd": sd,
    }


def table(points):
    """Le LP moyen par placement, pour qu'on puisse VOIR le barème.

    La projection n'utilise pas cette table — elle utilise la droite. Celle-ci
    est là pour qu'un écart à la linéarité se remarque au lieu d'être lissé.
    """
    par = {}
    for p, l in points:
        par.setdefault(int(p), []).append(l)
    return {str(k): {"n": len(v), "lp_moyen": round(st.mean(v), 1)}
            for k, v in sorted(par.items())}


def extraire(data, premier_code=None):
    """Les parties exploitables pour le barème, et celles qu'on écarte.

    `premier_code` : le plus petit code de patch du set courant. Toute partie
    d'un code inférieur est d'un set PASSÉ et sort du barème — la page du
    joueur garde ses vieilles parties, et au lendemain d'un changement de set
    elles sont majoritaires. Un barème de Master du Set 18 ne dit rien des
    gains d'un joueur reclassé en Diamant au Set 19, où le MMR dépasse
    largement le rang affiché et où chaque place rapporte davantage.

    Une partie n'entre dans le barème que si :
      - elle est classée (queueId 1100) et porte un lpDiff non nul ;
      - la perte n'a pas été tronquée par la protection de rétrogradation,
        c'est-à-dire qu'elle ne s'arrête pas pile à 0 LP.
    """
    bons, censurees, hautes, anciennes = [], 0, [], 0
    for m in data.get("matches") or []:
        if m.get("queueId") != 1100:
            continue
        if premier_code and (m.get("patch") or 0) < premier_code:
            anciennes += 1
            continue
        pl = (m.get("info") or {}).get("placement")
        lp = m.get("lpDiff")
        if not pl or lp in (None, 0):
            continue
        avant  = (m.get("rankBefore") or [None, None])
        apres  = (m.get("rankAfter")  or [None, None])
        # Défaite qui finit exactement à 0 LP : la perte a été écrêtée.
        if lp < 0 and apres[1] == 0:
            censurees += 1
            continue
        bons.append((float(pl), float(lp)))
        if str(avant[0] or "").split(" ")[0] in HAUT:
            hautes.append((float(pl), float(lp)))
    return bons, hautes, censurees, anciennes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--region", default="euw")
    ap.add_argument("--nom",    default="Itario")
    ap.add_argument("--tag",    default="EUW")
    a = ap.parse_args()

    url = PAGE.format(region=a.region, nom=a.nom, tag=a.tag)
    html = lire(url)
    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S)
    if not m:
        sys.exit("__NEXT_DATA__ introuvable : la page du joueur a changé "
                 "de structure.")
    d = (json.loads(m.group(1)).get("props", {})
         .get("pageProps", {}).get("initialData") or {})
    pi = d.get("playerInfo") or {}
    rl = pi.get("rankedLeague") or [None, None]
    if not pi and not d.get("matches"):
        # Ni joueur ni parties : la page n'a plus la forme attendue. Ça, c'est
        # une panne, et on ne touche pas au fichier de la veille.
        sys.exit("playerInfo et matches absents : la page du joueur a changé "
                 "de structure.")

    # ── LE SET, D'ABORD ──────────────────────────────────────────────────
    # Ce fichier décrit une position dans UN classement, celui du set en
    # ligne. Tout ce qu'il croise (la barre, ses parties récoltées, les
    # parties de la page) doit être du même set, ou être écarté en le disant.
    set_courant = M.set_courant()
    codes = M.codes_du_set() or {}
    premier_code = codes.get("premier_code") if codes.get("borne_fiable") else None

    # ── NON CLASSÉ N'EST PAS UNE PANNE ───────────────────────────────────
    # Jusqu'au 10/11, ce script sortait en erreur quand la page ne portait
    # aucun palier. L'étape est tolérée dans le workflow, donc rien ne
    # cassait — et c'était pire : data/joueur.json de la veille restait en
    # place, et le site affichait « Master, 30 LP » au soir d'un changement
    # de set où tout le monde est remis à zéro. Un fichier périmé qui se
    # présente comme courant est la faute que ce projet a le plus commise.
    classe = bool(rl[0])

    # ── POSITION ──────────────────────────────────────────────────────────
    # Le puuid est présent sur la page ; il ne sort pas d'ici. Le dépôt est
    # public, et un puuid est un identifiant Riot stable.
    loc = pi.get("localRank") or [None, None]
    glo = pi.get("globalRank") or [None, None]
    hist = d.get("rankHistory") or []
    dernier_point = None
    if hist and isinstance(hist[0], list) and hist[0]:
        try:
            dernier_point = datetime.fromtimestamp(
                hist[0][0], timezone.utc).isoformat(timespec="minutes")
        except Exception:
            pass

    position = {
        "palier": rl[0],
        "lp": rl[1],
        "rang_region": loc[0],
        "percentile_region": round(loc[1] * 100, 3) if loc[1] else None,
        "rang_monde": glo[0],
        "percentile_monde": round(glo[1] * 100, 3) if glo[1] else None,
        "derniere_partie_connue": dernier_point,
    }

    ss = d.get("seasonStats") or {}
    saison = {
        "parties": ss.get("games"),
        "placement_moyen": ss.get("avgPlace"),
        "top4": ss.get("top4"),
        "premieres": ss.get("win"),
        "carry_principal": ss.get("topCarry"),
        "note": "Chiffres de tactics.tools, SANS retrait des parties lâchées. "
                "data/miroir.json porte la version nettoyée. Les deux doivent "
                "concorder sur le nombre de parties : si l'écart dépasse le "
                "nombre de parties lâchées, une des deux collectes a dérivé.",
    }

    # ── LE BARÈME ─────────────────────────────────────────────────────────
    tous, hautes, censurees, anciennes = extraire(d, premier_code)
    aj_tous   = ajustement(tous)
    aj_hautes = ajustement(hautes)
    # On préfère le barème mesuré en Master+ dès qu'il tient debout : c'est
    # celui de l'échelle qui mène à Challenger. Sinon, tous paliers, et on le
    # dit.
    aj = aj_hautes if (aj_hautes and aj_hautes["n"] >= 15) else aj_tous
    assiette = ("master_plus" if aj is aj_hautes else
                "tous_paliers" if aj else None)

    bareme = {
        "parties_retenues": len(tous),
        "parties_d_un_set_passe_ecartees": anciennes,
        "parties_master_plus": len(hautes),
        "censurees_exclues": censurees,
        "assiette_utilisee": assiette,
        "droite": {k: v for k, v in aj.items() if not k.startswith("_")} if aj else None,
        "droite_master_plus": ({k: v for k, v in aj_hautes.items()
                                if not k.startswith("_")} if aj_hautes else None),
        "table_observee": table(tous),
        "note_assiette": (
            "Barème ajusté sur Master+ uniquement."
            if assiette == "master_plus" else
            "Pas encore assez de parties en Master+ pour un barème propre : "
            "ajusté sur tous les paliers. Les gains y sont plus généreux "
            "qu'en haut de l'échelle, donc la projection est optimiste."),
    }

    # ── L'ÉCART À LA BARRE, EN PARTIES ────────────────────────────────────
    barre  = charger_json(BARRE) or {}
    miroir = charger_json(MIROIR) or {}
    # La barre ne vaut que si elle est du set courant ET ouverte. Un seuil du
    # set précédent, ou un classement sans Challenger, ne donne aucun écart.
    barre_valide = (barre.get("etat", "ouvert") == "ouvert"
                    and barre.get("set", set_courant) == set_courant)
    seuil  = barre.get("seuil_challenger_lp") if barre_valide else None
    palier_haut = str(rl[0] or "").split(" ")[0] in HAUT
    sous_master = lp_jusqu_a_master(rl[0], rl[1]) if classe else None
    if not classe or seuil is None:
        manquants = None
    elif palier_haut:
        manquants = seuil - rl[1]
    elif sous_master is not None:
        manquants = sous_master + seuil
    else:
        manquants = None

    # Ses parties récoltées (miroir) ne servent que si elles sont du même set.
    if miroir.get("set") != set_courant:
        miroir = {}

    projection = None
    # Le LP attendu par partie ne dépend PAS de la barre : il vient du barème
    # et du placement. Jusqu'au 10/11 il n'était calculé que si un écart à la
    # barre existait — donc pas du tout en début de set, quand Challenger
    # n'est pas encore ouvert, alors que c'est le chiffre dont build_fuites a
    # besoin. Seul le nombre de parties jusqu'à la barre dépend d'elle.
    a_un_ecart = manquants is not None and manquants > 0
    if aj:
        # Le placement sur lequel on projette : celui du Miroir (nettoyé) de
        # préférence, sinon celui de la saison (qui inclut les parties lâchées
        # et sous-estime donc son niveau).
        pm = miroir.get("placement_moyen")
        src = "miroir (parties lâchées retirées)"
        if pm is None:
            pm = ss.get("avgPlace") if (ss.get("games") or 0) >= 10 else None
            src = "tactics.tools (parties lâchées incluses)"
        if pm:
            attendu = aj["_a"] + aj["_b"] * pm

            # ── D'OÙ VIENT L'INCERTITUDE ─────────────────────────────────
            # Deux sources, et la première version de ce calcul n'en voyait
            # qu'une. Le barème s'ajuste à R² ≈ 0.99 : son erreur résiduelle
            # est de l'ordre de 0.6 LP/partie, ce qui donnait une fourchette
            # de ±5 parties — une précision absurde.
            #
            # La vraie incertitude est sur SON PLACEMENT MOYEN. À 114 parties
            # d'écart-type 2.2, l'erreur-type du placement vaut 0.21 place ;
            # multipliée par la pente (≈15 LP par place), elle pèse 3.2
            # LP/partie. Soit dix fois le terme du barème, et c'est elle qui
            # gouverne tout.
            #
            #   Var(LP) = sd_résidus²/n_barème  +  pente² · erreur-type(p̄)²
            #
            sd_pl = miroir.get("placement_ecart_type")
            n_pl  = miroir.get("n_parties") or ss.get("games")
            approx_sd = sd_pl is None
            if approx_sd:
                # Écart-type d'un placement uniforme sur 1..8. Il surestime un
                # peu le sien (sa distribution penche vers le top 4), donc la
                # fourchette penche vers la prudence. On le signale.
                sd_pl = 2.29
            err_pl = (sd_pl / math.sqrt(n_pl)) if n_pl else None
            var_bareme = (aj["_sd"] ** 2 / aj["n"]) if aj["n"] else 0.0
            var_place  = ((aj["_b"] * err_pl) ** 2) if err_pl else 0.0
            err = math.sqrt(var_bareme + var_place) if (var_bareme or var_place) else None

            projection = {
                "placement_projete": pm,
                "source_placement": src,
                "lp_par_partie_attendu": round(attendu, 2),
                "erreur_type": round(err, 2) if err else None,
                "erreur_decomposee": {
                    "bareme": round(math.sqrt(var_bareme), 2),
                    "placement": round(math.sqrt(var_place), 2),
                    "n_parties_placement": n_pl,
                    "ecart_type_placement": round(sd_pl, 2),
                    "ecart_type_approche": approx_sd,
                    "note": "Le terme dominant est le placement, pas le "
                            "barème. Il décroît en 1/racine(n) : c'est le "
                            "volume de parties qui resserre la fourchette.",
                },
                "solide": bool(err and abs(attendu) >= 2 * err),
                "lp_manquants": round(manquants, 1) if a_un_ecart else None,
                "parties_estimees": (round(manquants / attendu)
                                     if (a_un_ecart and attendu > 0) else None),
                # La fourchette, parce qu'un seul nombre serait un mensonge.
                "parties_fourchette": (
                    [round(manquants / (attendu + 2 * err)),
                     round(manquants / (attendu - 2 * err))]
                    if (a_un_ecart and err and attendu - 2 * err > 0) else None),
                "avertissement":
                    "OPTIMISTE PAR CONSTRUCTION. Deux effets non modélisés "
                    "poussent dans le même sens : les gains de LP se "
                    "compriment quand le MMR rejoint le rang, et le placement "
                    "moyen remonte vers 4.50 dans des lobbies plus durs. "
                    "À lire comme une vitesse maximale, pas comme un "
                    "calendrier.",
            }
        if projection and not a_un_ecart:
            projection["avertissement"] = (
                "Pas d'écart à la barre à convertir en parties ("
                + ("déjà au-dessus du seuil" if (manquants is not None and manquants <= 0)
                   else "aucun seuil de Challenger valide pour ce set")
                + ") : seul le LP attendu par partie est donné.")
        elif projection and projection["parties_estimees"] is None:
            projection["avertissement"] = (
                "LP par partie négatif ou nul au placement projeté : à ce "
                "rythme la barre ne se rapproche pas. Ce n'est pas un volume "
                "qui manque, c'est le placement.")

    # ── LA CONTRE-ÉPREUVE ─────────────────────────────────────────────────
    # Deux chiffres se contredisent, et les cacher l'un à l'autre serait la
    # pire des solutions :
    #
    #   - l'écart de LP divisé par le rythme projeté donne ~53 parties ;
    #   - les 25 derniers Challengers en ont 381 au compteur.
    #
    # La projection suppose que son LP/partie actuel tient. Or il est mesuré
    # PENDANT une montée rapide, le régime exact où le MMR devance le LP
    # affiché et où les gains sont les plus généreux. Quand les deux se
    # rejoignent, le gain tend vers zéro — on ne monte plus qu'à la vitesse à
    # laquelle on progresse vraiment.
    #
    # Deux témoins indépendants, qu'on publie à côté de la projection :
    #
    #   1. SON LP/PARTIE RÉELLEMENT OBSERVÉ EN MASTER. Sans modèle, sans
    #      barème : la somme des LP de ses parties en Master+, divisée par
    #      leur nombre. Si elle décroche de la projection, la compression est
    #      en train de se produire.
    #
    #   2. SON RANG. Challenger est le top N de la région : un rang se compare
    #      sans hypothèse, là où un LP/partie se projette avec une. C'est la
    #      mesure de position la plus honnête dont on dispose.
    obs = [l for _, l in hautes]
    contre = None
    if obs:
        moy_obs = st.mean(obs)
        sd_obs = st.stdev(obs) if len(obs) > 1 else 0.0
        err_obs = sd_obs / math.sqrt(len(obs)) if len(obs) else None
        att = (projection or {}).get("lp_par_partie_attendu")
        contre = {
            "lp_par_partie_observe": round(moy_obs, 2),
            "n_parties": len(obs),
            "seuil_bruit": round(2 * err_obs, 2) if err_obs else None,
            "exploitable": bool(err_obs and abs(moy_obs) >= 2 * err_obs),
            "ecart_a_la_projection": (round(moy_obs - att, 2)
                                      if att is not None else None),
            "note": "Mesure brute, sans barème : la somme des LP de ses "
                    "parties en Master+, divisée par leur nombre. Tant que "
                    "`exploitable` est faux, elle ne tranche rien — mais "
                    "c'est elle qui tranchera, et elle s'accumule toute "
                    "seule à chaque relevé.",
        }

    n_ch = (barre.get("paliers") or {}).get("CHALLENGER") if barre_valide else None
    rang = None
    if loc[0] and n_ch:
        rang = {
            "rang_region": loc[0],
            "challengers_region": n_ch,
            "joueurs_a_depasser": loc[0] - n_ch,
            "note": "Challenger est le top N de la région. Un rang se compare "
                    "SANS hypothèse — c'est sa force contre la projection en "
                    "LP, qui en demande une (que le rythme actuel tienne). "
                    "Quand les deux racontent des histoires différentes, "
                    "croire le rang.",
        }

    out = {
        "schema_version": SCHEMA,
        "genere_le": date.today().isoformat(),
        "source": "tactics.tools",
        # Le set dont cette position parle, et si elle existe. Le site lit
        # ces deux champs avant tout le reste.
        "set": set_courant,
        "etat": "classe" if classe else "non_classe",
        "etat_note": None if classe else (
            "Aucun palier classé sur la page : la saison vient de commencer "
            "et aucune partie classée n'est encore comptée, ou le profil "
            "n'a pas été rafraîchi. Il n'y a pas de position à afficher — "
            "et surtout pas celle du set précédent."),
        "page": url,
        "joueur": {"nom": pi.get("name"), "tag": pi.get("tag"),
                   "region": pi.get("region")},
        "position": position,
        "saison": saison,
        "bareme_lp": bareme,
        "ecart_a_la_barre": {
            "seuil_challenger_lp": seuil,
            "source_seuil": f"data/barre.json du {barre.get('genere_le')}"
                            if barre else None,
            "lp_manquants": round(manquants, 1) if manquants is not None else None,
            "dont_jusqu_a_master": sous_master,
            "raison_si_absent": (
                None if manquants is not None else
                "non classé" if not classe else
                barre.get("etat_note") if (barre and not barre_valide
                                           and barre.get("etat", "ouvert") != "ouvert") else
                "la barre relevée est celle d'un autre set" if (barre and not barre_valide) else
                "barre non relevée"),
            "note": None if (palier_haut or not classe) else
                    "Sous Master, l'écart additionne les divisions restantes "
                    "(100 LP chacune, sans série de promotion) et le seuil de "
                    "Challenger. Les gains y sont plus généreux qu'en Master : "
                    "cette partie du chemin va plus vite que la droite ne le "
                    "dit une fois en haut.",
        },
        "projection": projection,
        "contre_epreuve": contre,
        "rang": rang,
        "echelle": "Au-dessus de Master il n'y a plus de division ni de série "
                   "de promotion : de Master 0 LP à Challenger, c'est une "
                   "seule échelle continue. C'est ce qui rend un LP/partie "
                   "mesuré en Master directement projetable jusqu'à la barre.",
    }

    os.makedirs(os.path.dirname(SORTIE), exist_ok=True)
    json.dump(out, open(SORTIE, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    print(f"écrit : {SORTIE}")
    print(f"  set {set_courant} · {out['etat']}"
          + (f" · {anciennes} parties d'un set passé écartées" if anciennes else ""))
    if classe:
        print(f"  {position['palier']} · {position['lp']} LP · "
              f"{position['rang_region']}e {str(pi.get('region') or '').upper()} "
              f"(top {position['percentile_region']} %)")
    else:
        print(f"  {out['etat_note']}")
    if aj:
        print(f"  barème : {aj['pente_lp_par_place']} LP par place, "
              f"neutre à la {aj['place_neutre']}e · R² {aj['r2']} "
              f"({aj['n']} parties, assiette {assiette}, "
              f"{censurees} écrêtées exclues)")
    if projection and projection["lp_manquants"] is not None:
        p = projection
        fr = (f" (fourchette {p['parties_fourchette'][0]}–"
              f"{p['parties_fourchette'][1]})" if p["parties_fourchette"] else "")
        print(f"  à {p['placement_projete']} de placement : "
              f"{p['lp_par_partie_attendu']} LP/partie "
              f"-> {p['lp_manquants']} LP manquants = "
              f"{p['parties_estimees']} parties{fr}")
        print("  ⚠ borne basse sur la difficulté, pas un calendrier")
    if contre:
        c = contre
        print(f"  contre-épreuve : {c['lp_par_partie_observe']:+} LP/partie "
              f"observé sur {c['n_parties']} parties en Master "
              f"(bruit ±{c['seuil_bruit']}, "
              f"{'exploitable' if c['exploitable'] else 'PAS ENCORE exploitable'})")
    if rang:
        print(f"  rang : {rang['rang_region']}e, et Challenger s'arrête au "
              f"{rang['challengers_region']}e -> "
              f"{rang['joueurs_a_depasser']} joueurs à dépasser")


if __name__ == "__main__":
    main()
