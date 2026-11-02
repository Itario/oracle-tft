# Mettre le dépôt sur GitHub

Trois étapes, dix minutes.

## 1. Créer le dépôt

Sur github.com → **New repository** → nom `oracle-tft` → **Private** (tu pourras le
passer public plus tard) → **Create**. Ne coche rien d'autre : pas de README, pas de
`.gitignore`, ils sont déjà dans l'archive.

## 2. Pousser le code

Décompresse l'archive, ouvre un terminal dans le dossier `oracle-tft`, puis :

```bash
git init
git add .
git commit -m "Oracle TFT v1 : site, Carnet, Miroir, trois relevés"
git branch -M main
git remote add origin https://github.com/TON-PSEUDO/oracle-tft.git
git push -u origin main
```

Remplace `TON-PSEUDO` par ton nom d'utilisateur GitHub.

## 3. Activer le site

Dans le dépôt → **Settings** → **Pages** → section *Build and deployment* →
**Source : GitHub Actions**. C'est tout.

Le fichier `.github/workflows/deploy.yml` fait le reste : à chaque `git push` sur
`main`, il copie les données dans le site, **vérifie qu'aucune clé API ne s'y
trouve**, et publie. L'adresse apparaît dans l'onglet *Actions* après le premier
déploiement.

## Ton propre nom de domaine

Une fois le site en ligne : **Settings → Pages → Custom domain**. Il faudra ajouter
un enregistrement CNAME chez ton registrar vers `TON-PSEUDO.github.io`. GitHub
fournit le certificat HTTPS automatiquement.

## Ce que je peux faire ensuite

Une fois le dépôt créé, donne-moi son adresse : je pourrai y pousser les mises à
jour moi-même à chaque relevé, au lieu de te renvoyer des fichiers.

## Rappel de sécurité

`cle.txt` est dans `.gitignore` et le déploiement refuse de publier si une chaîne
`RGAPI-` apparaît quelque part. **Ne retire jamais ce garde-fou.**
