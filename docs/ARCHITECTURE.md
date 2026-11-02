# Architecture — v1, v2, v3

*Écrit le 25/10/2026. Ce document existe pour une seule raison : que la v2 et la v3
s'ajoutent sans rien reconstruire. À relire avant toute décision de structure.*

---

## La règle qui tient tout

**Trois couches, jamais mélangées.**

```
data/     ce qui est vrai          JSON versionnés, lisibles à l'œil
tools/    ce qui calcule          Python, sans dépendance au site
site/     ce qui montre           HTML statique, AUCUNE donnée en dur
```

**Et une seule source de vérité : `data/releves/`.** Le site, l'Oracle et les
mesures en descendent tous. Rien d'autre ne porte les mêmes faits.

*Cette règle a été enfreinte puis corrigée le 25/10.* Les données de relevé
vivaient aussi dans `tools/build/data_set18.js`, maintenu à la main. Les deux
copies concordaient — mais rien ne le garantissait, et la première divergence
serait passée inaperçue. `data_set18_fige.js` ne contient plus que les fiches
figées du 31/07 ; les blocs de relèvement sont générés.

Le site ne connaît des données que **trois URL**. Il ne sait pas d'où elles viennent :

```js
const SOURCES = {
  meta:       "data/meta/courant.json",
  profil:     "data/profil.json",
  calendrier: "data/calendrier.json"
};
```

**C'est le point de couture.** En v2, ces trois chemins deviennent `/api/meta`,
`/api/profil`, `/api/calendrier`. Le reste du site ne change pas d'une ligne.

Corollaire à ne jamais enfreindre : **si une donnée de jeu se retrouve écrite dans
le HTML, la migration est déjà cassée.** C'est l'erreur qui a immobilisé l'Oracle
entre août et octobre — 43 % de données enchâssées dans le moteur, chaque mise à
jour demandant d'éditer du code.

---

## Le versionnement des données

Chaque fichier de `data/` porte un `schema_version`. Les outils refusent ce qu'ils
ne savent pas lire, au lieu de deviner :

```python
if d.get("schema_version") != SCHEMA:
    print(f"  ! {nom} : schema_version {d.get('schema_version')} ignoré")
    continue
```

**Règle de changement.** Ajouter un champ facultatif : on garde la version. Changer
le sens d'un champ, en retirer un, ou changer une unité : on incrémente, et on écrit
une fonction de conversion dans `tools/build/`. Jamais de changement silencieux.

---

## v1 — aujourd'hui

**Ce que c'est.** Un site statique, pour un joueur, sans compte. Les outils tournent
sur la machine de Clément. Les relevés sont des fichiers.

```
data/releves/*.json      un relevé par patch, figé, jamais réécrit
data/meta/courant.json   dérivé des relevés par build_site.py
data/profil.json         un tableau "joueurs" qui n'en contient qu'un
data/calendrier.json     patchs et jalons
```

**Pourquoi `profil.json` contient déjà un tableau alors qu'il n'y a qu'un joueur :**
pour que la v2 n'ait pas à changer la forme. Le site lit `joueurs[0]` ; en v2 il
lira `joueurs[moi]`.

**Limite assumée.** MetaTFT ne se lit qu'avec Chrome connecté. Le relevé reste un
geste manuel déclenché par Claude. La tâche du jeudi le rappelle et le fait quand
elle peut ; sinon elle le dit, plutôt que d'inventer des chiffres.

---

## v2 — comptes et groupe de joueurs (cible : Set 19)

**Ce qui change vraiment.** Dès qu'il y a plusieurs joueurs, trois choses deviennent
impossibles en statique :

1. **La clé API Riot ne peut plus vivre côté joueur.** Dans un téléchargement ou
   dans le navigateur, chacun la verrait. C'est le serveur qui interroge Riot pour
   tout le monde, avec une seule clé.
2. **Les parties de chacun doivent être stockées quelque part de partagé.**
3. **Il faut savoir qui est qui.**

**Ce qui ne change pas :** `site/` dans sa quasi-totalité, `tools/carnet/` et
`tools/riot/miroir.py` — la logique d'analyse ne dépend pas de l'origine des données.

**Forme pressentie.**

```
api/                      serveur (une fonction par route suffit au début)
  /api/meta               <- remplace data/meta/courant.json
  /api/profil             <- remplace data/profil.json, filtré par session
  /api/moi/parties        nouveau : les parties du joueur connecté
  /api/groupe             nouveau : le classement du groupe
db/                       une table joueurs, une table parties, une table releves
```

**Migration des relevés vers la base :** les JSON de `data/releves/` sont la source
de vérité historique. Ils seront importés tels quels, `schema_version` compris. Ne
jamais les supprimer après l'import — ils sont l'audit du projet.

**Ordre de travail recommandé :** d'abord `/api/meta` en lisant les mêmes fichiers
(le site ne voit aucune différence, c'est le test que la couture est propre), puis
la base, puis les comptes.

---

## v3 — automatisation complète

Le récap se génère et se publie sans intervention. Trois briques manquantes :

- **Relever sans navigateur.** Aujourd'hui MetaTFT exige Chrome. Il faudra soit une
  source lisible par un serveur, soit un relevé bâti sur l'API Riot elle-même — plus
  lent, mais autonome.
- **Produire le récap depuis `courant.json`.** La page animée existe déjà ; il faut
  la générer plutôt que l'écrire.
- **Publier.** Déjà en place : un `git push` déclenche le déploiement.

---

## Déploiement

`.github/workflows/deploy.yml` publie `site/` sur GitHub Pages à chaque poussée sur
`main`. Le site étant entièrement statique, il n'y a ni build ni dépendance.

**Point d'attention à la v2 :** GitHub Pages ne sert que du statique. Dès qu'il y a
une API, il faudra un hébergeur qui exécute du code. Le site lui-même pourra rester
où il est — seules les trois URL de `SOURCES` changeront de destination.

---

## Ce qu'il ne faut pas faire

- **Écrire une donnée de jeu dans le HTML.** C'est la panne de septembre.
- **Mélanger deux sources de statistiques** sans vérifier qu'elles mesurent la même
  population. metabot.gg publie des compos à 1.84 de placement moyen là où MetaTFT
  les situe vers 4.1 : il ne compte que les parties finies avec le board complet.
- **Réécrire un relevé déjà figé.** Un relevé est une photo datée. S'il est faux, on
  en ajoute un autre avec une note, on ne corrige pas l'historique.
- **Mettre la clé API dans le dépôt.** `cle.txt` est dans `.gitignore`. En v2 elle
  vivra dans les secrets de l'hébergeur.
- **Réimplémenter un calcul déjà dans `tools/lib/mesures.py`.** Spearman, le
  classement et le plancher de bruit y vivent une seule fois. Deux copies
  concordent jusqu'au jour où l'une est corrigée.
- **Conclure d'un mouvement sans vérifier le plancher de bruit.** `carnet.py bruit`
  existe pour ça, et il sera indispensable au Set 19, dont les premiers relevés PBE
  auront peu de volume.
