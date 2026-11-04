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
SORTIE = os.path.join(RACINE, "data", "joueur.json")
BARRE  = os.path.join(RACINE, "data", "barre.json")
MIROIR = os.path.join(RACINE, "data", "miroir.json")
SCHEMA = 1
PAGE   = "https://tactics.tools/player/{region}/{nom}/{tag}"

# Au-dessus de Master, une seule échelle continue. En dessous, les divisions
# remettent le compteur à zéro : les LP n'y sont pas sur la même règle.
HAUT = ("MASTER", "GRANDMASTER", "CHALLENGER")

EN_TETES = {
    "User-Agent": "OracleTFT/1.0 (relevé de position, usage personnel)",
    "Accept": "text/html",
}


def lire(url):
    req = urllib.request.Request(url, headers=EN_TETES)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        sys.exit(f"HTTP {e.code} sur {url}")
    except Exception as e:
        sys.exit(f"Impossible de joindre {url}\n  {type(e).__name__}: {e}\n"
                 "  (Normal depuis une session Claude : le proxy du conteneur "
                 "bloque ce domaine. Ce script est fait pour le runner GitHub.)")


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


def extraire(data):
    """Les parties exploitables pour le barème, et celles qu'on écarte.

    Une partie n'entre dans le barème que si :
      - elle est classée (queueId 1100) et porte un lpDiff non nul ;
      - la perte n'a pas été tronquée par la protection de rétrogradation,
        c'est-à-dire qu'elle ne s'arrête pas pile à 0 LP.
    """
    bons, censurees, hautes = [], 0, []
    for m in data.get("matches") or []:
        if m.get("queueId") != 1100:
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
    return bons, hautes, censurees


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
    if not rl[0]:
        sys.exit("Aucun palier classé sur la page : profil vide ou non joué.")

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
    tous, hautes, censurees = extraire(d)
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
    seuil  = barre.get("seuil_challenger_lp")
    palier_haut = str(rl[0] or "").split(" ")[0] in HAUT
    manquants = (seuil - rl[1]) if (seuil is not None and palier_haut) else None

    projection = None
    if aj and manquants is not None and manquants > 0:
        # Le placement sur lequel on projette : celui du Miroir (nettoyé) de
        # préférence, sinon celui de la saison (qui inclut les parties lâchées
        # et sous-estime donc son niveau).
        pm = miroir.get("placement_moyen")
        src = "miroir (parties lâchées retirées)"
        if pm is None:
            pm = ss.get("avgPlace")
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
                "lp_manquants": round(manquants, 1),
                "parties_estimees": (round(manquants / attendu)
                                     if attendu > 0 else None),
                # La fourchette, parce qu'un seul nombre serait un mensonge.
                "parties_fourchette": (
                    [round(manquants / (attendu + 2 * err)),
                     round(manquants / (attendu - 2 * err))]
                    if (err and attendu - 2 * err > 0) else None),
                "avertissement":
                    "OPTIMISTE PAR CONSTRUCTION. Deux effets non modélisés "
                    "poussent dans le même sens : les gains de LP se "
                    "compriment quand le MMR rejoint le rang, et le placement "
                    "moyen remonte vers 4.50 dans des lobbies plus durs. "
                    "À lire comme une vitesse maximale, pas comme un "
                    "calendrier.",
            }
        if projection and projection["parties_estimees"] is None:
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

    n_ch = (barre.get("paliers") or {}).get("CHALLENGER")
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
            "note": None if palier_haut else
                    "Sous Master, les divisions remettent les LP à zéro : "
                    "l'écart à la barre ne s'exprime pas en LP depuis ici.",
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
    print(f"  {position['palier']} · {position['lp']} LP · "
          f"{position['rang_region']}e {str(pi.get('region') or '').upper()} "
          f"(top {position['percentile_region']} %)")
    if aj:
        print(f"  barème : {aj['pente_lp_par_place']} LP par place, "
              f"neutre à la {aj['place_neutre']}e · R² {aj['r2']} "
              f"({aj['n']} parties, assiette {assiette}, "
              f"{censurees} écrêtées exclues)")
    if projection:
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
