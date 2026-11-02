# Oracle TFT

Outil d'analyse Teamfight Tactics. Trois briques qui se complètent, un site qui
les présente.

**Le site** → quatre onglets, selon les moments d'usage :
`Avant` (quoi jouer) · `En partie` (le moteur de pivot) · `Après` (la review de tes
parties) · `Suivi` (rotation, calendrier, outils).
En ligne : <https://itario.github.io/oracle-tft>
**L'Oracle** → référence consultable en partie, un fichier HTML autonome, hors ligne.
**Le Carnet** → garde la série des relevés, mesure la rotation d'un patch à l'autre.
**Le Miroir** → analyse tes propres parties, le lobby servant de groupe de contrôle.

## Démarrer

```bash
# après avoir ajouté un relevé dans data/releves/
python3 tools/build/build_site.py      # données du site + copie locale
python3 tools/build/build_oracle.py 18 # régénère site/oracle.html

# regarder le site
cd site && python3 -m http.server 8000   # puis http://localhost:8000
```

## Le Carnet

```bash
python3 tools/carnet/carnet.py lister      # les relevés
python3 tools/carnet/carnet.py fraicheur   # le dernier est-il périmé ?
python3 tools/carnet/carnet.py rotation    # de combien un patch déplace la méta
python3 tools/carnet/carnet.py bruit       # ce mouvement est-il réel ou du hasard ?
python3 tools/carnet/carnet.py comparer 2026-10-19 2026-10-23
```

## Le Miroir

Voir `tools/riot/LISEZ-MOI.md`. En résumé :

```bash
cd tools/riot
# mettre la clé API dans cle.txt (jamais dans le dépôt — voir .gitignore)
python3 collecte.py      # récolte les parties
python3 inspecter.py     # dit ce que les données contiennent vraiment
python3 miroir.py --set auto --csv parties_propres.csv --sortie miroir_resume.json
```

Sous Windows, `LANCER.bat` enchaîne les trois d'un double-clic, et `DIAGNOSTIC.bat`
tranche la question « est-ce la clé ? » en trois appels choisis pour se distinguer
entre eux.

`--set auto` n'est pas optionnel : une récolte de 200 parties remonte loin et couvre
souvent **deux sets**. Les moyenner produit un chiffre qui ne décrit aucun des deux.

Puis, pour que le site voie ces mesures :

```bash
python3 tools/build/build_miroir.py parties_propres.csv miroir_resume.json
# -> data/miroir.json
```

⚠ **Le dossier `parties/` ne quitte jamais la machine.** Chaque fichier contient le
puuid des **sept adversaires** du lobby — de la donnée personnelle de tiers.
`data/miroir.json` est un agrégat sans aucun identifiant, et c'est lui qu'on versionne.

## Structure

```
data/releves/      LA SOURCE DE VÉRITÉ — un relevé par patch, figé
data/profil.json   identité et lecture — AUCUN chiffre mesuré
data/miroir.json   les mesures de tes parties — produit par build_miroir.py
data/calendrier.json
data/meta/         généré par build_site.py

tools/lib/         le socle de mesure, partagé — une seule implémentation
tools/carnet/      historique et comparaisons
tools/riot/        collecte et analyse des parties
tools/build/       générateurs du site et de l'Oracle

site/              HTML statique, AUCUNE donnée en dur
docs/              ARCHITECTURE.md : v1, v2, v3
```

**Ce qui est généré, et donc non versionné :** `site/data/`, `site/oracle.html`,
`data/meta/courant.json`. Tout descend de `data/releves/`. Le workflow les
régénère à chaque déploiement, ce qui garantit que le site publié ne peut pas
diverger des relevés.

**La règle :** le site ne connaît des données que **quatre URL** (`meta`, `profil`,
`calendrier`, `miroir`). En v2 elles deviennent des routes d'API et rien d'autre ne
change. Si une donnée de jeu se retrouve écrite
dans le HTML, la migration est déjà cassée — lire `docs/ARCHITECTURE.md`.

## Ajouter un relevé

1. Relever sur MetaTFT (filtre Ranked + patch courant + Master+).
2. Écrire `data/releves/AAAA-MM-JJ_patch_rang.json` sur le modèle des existants,
   avec `schema_version: 1`.
3. `python3 tools/build/build_site.py`
4. Pousser sur `main` — le site se republie seul.

Sur un dépôt recréé de zéro, une action manuelle est nécessaire **une fois** :
Settings → Pages → Source : **GitHub Actions**. Le workflow ne peut pas l'activer
lui-même (le GITHUB_TOKEN n'a pas le droit de créer le site Pages) ; la raison est
écrite dans `.github/workflows/deploy.yml`.

Un relevé est une photo datée : **on ne le réécrit jamais.** S'il est faux, on en
ajoute un autre avec une note.

---

Projet personnel, sans lien avec Riot Games. Données : MetaTFT.
