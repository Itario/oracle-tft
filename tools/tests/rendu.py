#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LE RENDU — le site s'affiche-t-il, et dit-il quelque chose de faux ?
=====================================================================
Les tests du socle vérifient les fichiers ; la répétition vérifie la chaîne.
Aucun des deux n'ouvre la page. Or c'est la page que Clément lit, et un
fichier juste peut s'afficher « undefined LP » sans qu'aucun test ne bouge.

    python3 tools/tests/rendu.py [dossier_du_site] [--captures DOSSIER]

Ouvre les quatre onglets dans un vrai navigateur (Playwright, s'il est
installé) et relève :

    - les erreurs JavaScript et les exceptions non rattrapées ;
    - les mots qui trahissent une valeur manquante affichée telle quelle :
      « undefined », « NaN », « null », « [object Object] » ;
    - le bandeau, pour vérifier qu'il annonce le bon set.

Sort en erreur s'il trouve quoi que ce soit. Sans Playwright, il le dit et
sort en succès : ce contrôle est un filet de plus, pas une condition.
"""

import http.server, json, os, re, socketserver, sys, threading

ICI = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ONGLETS = ("avant", "fiches", "apres", "suivi")
SUSPECTS = re.compile(r"\bundefined\b|\bNaN\b|\bnull\b|\[object Object\]")


def servir(dossier):
    class H(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *a, **k):
            super().__init__(*a, directory=dossier, **k)
        def log_message(self, *a):
            pass
    srv = socketserver.TCPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def controler(dossier, captures=None, largeur=1100):
    try:
        from playwright.sync_api import sync_playwright
    except Exception:
        print("Playwright absent : rendu non contrôlé (ce n'est pas un échec).")
        return None
    srv = servir(dossier)
    base = f"http://127.0.0.1:{srv.server_address[1]}/index.html"
    constats = {"erreurs": [], "suspects": [], "bandeau": None, "textes": {}}
    with sync_playwright() as p:
        nav = p.chromium.launch()
        page = nav.new_page(viewport={"width": largeur, "height": 900})
        page.on("pageerror", lambda e: constats["erreurs"].append(str(e)))
        page.on("console", lambda m: constats["erreurs"].append(m.text)
                if m.type == "error" and "favicon" not in m.text
                and "Failed to load resource" not in m.text else None)
        for o in ONGLETS:
            page.goto(f"{base}#{o}")
            page.wait_for_function("document.querySelector('#hsub').textContent !== 'chargement…'")
            page.wait_for_timeout(150)
            texte = page.inner_text(f"#v-{o}")
            constats["textes"][o] = texte
            if len(texte.strip()) < 40:
                constats["erreurs"].append(f"onglet {o} : vide")
            for m in SUSPECTS.finditer(texte):
                a, b = max(0, m.start() - 50), min(len(texte), m.end() + 30)
                constats["suspects"].append(f"{o} : …{texte[a:b].strip()}…".replace("\n", " "))
            if captures:
                os.makedirs(captures, exist_ok=True)
                page.screenshot(path=os.path.join(captures, f"{o}.png"), full_page=True)
        constats["bandeau"] = page.inner_text("#hsub")
        nav.close()
    srv.shutdown()
    return constats


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dossier = args[0] if args else os.path.join(ICI, "site")
    captures = None
    if "--captures" in sys.argv:
        captures = sys.argv[sys.argv.index("--captures") + 1]
        args = [a for a in args if a != captures]
        dossier = args[0] if args else os.path.join(ICI, "site")
    c = controler(dossier, captures)
    if c is None:
        return
    print(f"bandeau : {c['bandeau']}")
    for o, t in c["textes"].items():
        print(f"  {o:<7} {len(t):>6} caractères")
    for e in c["erreurs"]:
        print(f"  ERREUR   {e}")
    for s in c["suspects"][:20]:
        print(f"  SUSPECT  {s}")
    if c["erreurs"] or c["suspects"]:
        sys.exit(f"{len(c['erreurs'])} erreur(s), {len(c['suspects'])} valeur(s) suspecte(s)")
    print("rendu propre")


if __name__ == "__main__":
    main()
