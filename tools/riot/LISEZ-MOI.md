# Le Miroir — mode d'emploi

Trois scripts, à lancer dans cet ordre, **sur ta machine** (l'API de Riot est
inaccessible depuis l'environnement de Claude : le proxy renvoie 403).

## Préparation, une seule fois

Mets les trois scripts dans un dossier. À côté, un fichier **`cle.txt`** avec ta
clé API sur une seule ligne, rien d'autre.

Sous Windows, crée-le depuis le terminal pour éviter le piège du `.txt.txt` :

```
notepad cle.txt
```

Une clé de développement expire en **24 h** — largement assez pour la première
récolte. Les fichiers obtenus sont ensuite à toi pour toujours, sans clé.

## 1. Récolter

```
python collecte.py
```

Environ quatre minutes pour 200 parties. **Relançable** : il saute ce qui est déjà
téléchargé, donc si ta clé expire en cours, tu en regénères une et tu relances.

Si ça répond `403` : le portail Riot ne garde **qu'une seule clé valide à la fois**.
Recopie celle qui est affichée *maintenant* sur le tableau de bord.

## 2. Inspecter

```
python inspecter.py
```

Affiche ce que contiennent vraiment les données — notamment si les augments sont
exposés, ce que la documentation officielle de Riot ne dit pas.

**Envoie sa sortie à Claude.** Elle tient en quelques lignes.

## 3. Analyser

```
python miroir.py
python miroir.py --csv sortie.csv      pour creuser dans un tableur
python miroir.py --depuis 2026-10-01   fenêtre restreinte
```

Écrit `miroir_resume.json` — **c'est ce fichier qu'il faut envoyer à Claude** pour
l'interprétation. Il est petit, contrairement au dossier `parties/`.

---

## Ce que le Miroir mesure, et pourquoi c'est différent

**Le lobby est le groupe de contrôle.** Chaque partie contient les huit joueurs :
pas besoin de statistiques venues d'ailleurs. Pour chaque partie, tu es classé
parmi tes sept adversaires sur le niveau, les dégâts, l'or — et ce rang est comparé
à ton placement réel.

- **2e du lobby en niveau, 5e au classement** → tu obtiens les ressources sans les
  convertir. Le travail est sur le board : positionnement, objets, composition.
- **6e en niveau, 3e au classement** → tu joues au-dessus de tes ressources. Le
  travail est sur l'économie et le tempo.

Ton elo exact, tes adversaires réels, tes parties. Aucune hypothèse sur la méta.

Il produit aussi ta **distribution de placements** (1re à 8e) — la mesure qui
manquait depuis le début du projet, et sans laquelle on ne peut pas savoir si ton
profil est de pointe ou de régularité.

## Une limite à connaître

Environ 300 choix d'augments répartis sur plus de 200 augments : **aucune conclusion
augment par augment ne sera fiable**, même sur 200 parties. Le script le dit
lui-même quand il affiche ce classement. Ce qui est solide, c'est l'agrégat.

## Vie privée

Tout reste sur ta machine. `cle.txt` ne part nulle part — ne le partage pas, et ne
colle pas ta clé dans une conversation : seul `miroir_resume.json` a besoin d'être
envoyé.
