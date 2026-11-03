# JOURNAL DE PRÉDICTIONS — Oracle Set 18

Règle unique : **une prédiction n'est valable que si elle est écrite avant de connaître le résultat.**
On n'édite jamais une entrée passée. On ajoute une colonne « vérifié » quand la donnée arrive.

---

## Entrée n°1 — 31/07/2026 (PBE, base zéro)

Source des chiffres : lolchess.gg/champions/set18/stats, 65 champions.
Moteur : `moteur18.py`, indices relatifs à la médiane du palier de coût.
Signal de correction disponible : **aucun** (pas de winrate exploitable en PBE).
Vérifiable à partir du : **26/08/2026** (live, placement moyen par compo sur tactics.tools / MetaTFT).

### Prédictions de nerf — surchargés pour leur palier

| Champion | Palier | Chiffre qui déclenche | Vérifié |
|---|---|---|---|
| Master Yi | 3 | auto 86 vs 50 de médiane, + 850 PV / 60 armure | ☐ |
| Gnar | 5 | auto 95, plus grosse auto-attaque du set | ☐ |
| Brambleback | 4 | auto 84 (110 AD), survie 62 | ☐ |
| Rengar | 3 | auto 74 vs 50 de médiane | ☐ |
| Ivern | 5 | cadence 99, le sort le plus rapide du palier | ☐ |
| Kennen | 5 | cumul cadence 79 + survie 65 sur un lanceur | ☐ |

### Prédictions de buff — sous-dimensionnés pour leur palier

| Champion | Palier | Chiffre qui déclenche | Vérifié |
|---|---|---|---|
| Draven | 5 | cadence 23, la plus lente du set (0/120 mana) | ☐ |
| Ahri | 4 | total le plus bas du palier 4 (cadence 38) | ☐ |
| Kayle | 2 | 10 AD, aucune barre de mana | ☐ |
| Varus | 1 | total le plus bas du palier 1 (cadence 32) | ☐ |
| Azir | 3 | total le plus bas du palier 3 | ☐ |

### Ce qu'on cherche à apprendre

Sur les six premiers patchs exploitables, on mesure pour chaque axe la corrélation entre
le delta d'indice et le delta de placement moyen de la compo concernée.

- Si **AUTO** prédit bien → les nerfs suivent les dégâts bruts, on augmente son poids.
- Si **CADENCE** prédit mieux → c'est le temps avant le premier sort qui décide, et
  c'est une information que les tier lists ne publient pas. Avantage réel.
- Si **SURVIE** ne prédit rien → on la sort du score composite et on la garde en info.

Garde-fou anti-surapprentissage : **on ne touche aux poids qu'après six observations
minimum**, et jamais plus d'un poids à la fois. Avec un patch par semaine au live, ça
veut dire pas d'ajustement avant octobre. C'est volontaire : mieux vaut un moteur lent
et honnête qu'un moteur qui épouse le bruit.

### Réserves connues sur cette base

- Résistance magique supposée égale à l'armure (vérifiée sur 2 champions seulement).
- Portée d'attaque absente de la source.
- **Ratios de sort masqués** → l'axe puissance de sort n'existe pas encore. C'est la
  moitié manquante du moteur, à câbler dès que les valeurs sont publiées.
- Cadence de Caitlyn et Master Yi non lisible : leur sort est un passif à 3 de mana.

---

## Entrée n°2 — (à remplir au prochain patch)

---

## Entrée n°2 — 01/08/2026 — RELEVÉ POST-PATCH

**Méthode.** Re-récolte des 65 champions sur lolchess.gg/champions/set18/stats
(page servie en vietnamien ce jour ; noms d'unités recyclées remappés sur les slugs
par coût + gabarit, correspondance exacte sur les 6 valeurs). Diff automatique
contre la base zéro du 31/07 (moteur18.py).

**Résultat : ZÉRO écart.** PV, AD, vitesse d'attaque, armure, mana de départ et
mana max sont identiques sur les 65 champions.

**Lecture.** Le patch n'a pas touché aux stats de base. Ce qui a bougé est donc
dans les couches non exposées par cette source : ratios de sort, valeurs de traits,
augments, objets, wisps. Les notes de patch PBE ne sont pas publiées (les mises à
jour PBE quotidiennes n'en ont pas).

**Conséquence pour le moteur.** Les indices SURVIE / AUTO / CADENCE de la base zéro
restent valides au 01/08. Les 6 candidats nerf et 5 candidats buff de l'entrée n°1
sont MAINTENUS sans modification.

**Piège de source à retenir.** La page Mobalytics "Best PBE Comps Set 18" affiche
dans son corps « Updated on Jul 16, 2026 », soit AVANT la sortie PBE du 28/07.
Ses tiers S/A/B sont des prédictions pré-set, pas un relevé post-patch. À ne pas
compter comme une observation. Le delta relevé précédemment (Blossom S→A, Sprykin
sortie du top) n'est donc PAS confirmé par cette lecture-ci : la page y donne
Blossom S et Sprykin S. Divergence à trancher au live.

**Ce que ça dit du plan.** La corrélation "nerf/up -> déplacement des compos" n'est
pas mesurable aujourd'hui, faute de winrates en PBE. Premier point de mesure réel :
26/08. D'ici là on accumule des photos datées ; c'est déjà ce qu'il faut.

---

## Entrée n°3 — 03/08/2026 — PREMIÈRE MESURE DU MOTEUR
[CORRIGÉ le 03/08 : datée par erreur 01/08. Le post source de Tim (@TheTruexy,
Live Balance Lead TFT) est horodaté 03/08/2026 16:48 CEST, déploiement midi PT.]

Notes du PREMIER GROS PATCH PBE du Set 18, publiées par Tim (@TheTruexy),
Live Balance Lead TFT. Le journal n°1 date du 31/07 : la prédiction est ANTÉRIEURE.

### Bilan des 11 paris de l'entrée n°1
CONFIRMÉS (4) :
  - Master Yi  candidat NERF -> NERFÉ (on-hit AP 155/235/375 -> 145/220/350)
  - Rengar     candidat NERF -> NERFÉ (sort 295/445/710 -> 270/405/650)
  - Draven     candidat BUFF -> BUFFÉ (AD 40 -> 48, soit +20 %)
  - Azir       candidat BUFF -> BUFFÉ (sort 48/72/115 -> 50/75/120)
NON TOUCHÉS (7) : Gnar, Brambleback, Ivern, Kennen (nerf) ; Ahri, Kayle, Varus (buff)
CONTREDITS : 0. Aucun candidat nerf n'a été buffé, aucun candidat buff n'a été nerfé.

### Faux négatifs — là où le moteur était aveugle
Buffs d'unités que le moteur classait HAUT dans leur palier :
  Camille (n°1 palier 1), Warwick (n°3 palier 2), Kha'Zix (n°3 palier 3), Sivir (n°3 palier 4)
Nerfs d'unités que le moteur classait BAS :
  Gromp (n°12 palier 2), Lux (n°9 palier 5)

### DIAGNOSTIC — la leçon la plus importante depuis l'ouverture du journal
Sur ~35 champions touchés, Riot n'a modifié QUE 3 stats de base (Draven AD,
Maokai PV, Ashe mana max). Tout le reste porte sur des DÉGÂTS DE SORT, SOINS,
BOUCLIERS et RATIOS. Or le moteur ne mesure que les stats de base.
=> Il est structurellement aveugle à ce que Riot équilibre réellement.
=> L'axe SORT n'est pas un complément : c'est l'axe PRINCIPAL. Priorité n°1.

Où il a bien marché : le palier 3, où les deux plus hauts totaux (Master Yi 237,
Rengar 178) ont été nerfés et le plus bas (Azir 123) buffé. C'est le palier où les
carries sont des auto-attaquants — donc là où l'axe AUTO capture la vraie puissance.
Hypothèse à tester : le moteur est fiable sur les auto-attaquants, aveugle sur
les lanceurs de sorts. Ne PAS ajuster les poids (règle des 6 observations minimum).

### Stats de base recalculées (base zéro amendée au 01/08)
  Draven  AUTO 34 -> 40   total 101 -> 109
  Maokai  SURVIE 54 -> 60  total 147 -> 156
  Ashe    CADENCE 56 -> 51 total 163 -> 158  (nerf déguisé : mana max 80 -> 90)
Les autres indices du palier 5 bougent de 1 à 7 points par déplacement de médiane.

### Traits — lecture d'impact sur les compos (DÉRIVÉE, non mesurée)
  DESCEND FORT : Solar Inferno Reroll — double nerf (Solar scaling 3 étoiles
    2.5%->1.5% ET Eclipse proc 3s->4s). Elle était étiquetée "la ligne FACILE".
  DESCEND : Veigar Reroll (Blackthorn multiplicateur 3 étoiles 300->280 / 400->330)
  DESCEND : Inferno Cap (Eclipse)
  MONTE : Elderwood et Elderwood Cap (PV Stonebark +50, sort Protector +6 %)
  MONTE : Elderwood Cap encore (Draven AD +20 %)
  NEUTRE : Riftbeasts (Draven buff compense Elder Dragon nerf)
  MONTE LÉGER : Coven (essence 70->100) mais reste la ligne la plus faible.

### Pari n°2 — à vérifier au prochain patch
Si l'hypothèse "Riot équilibre par les sorts" tient, le prochain patch touchera
encore majoritairement des ratios. Et Gnar / Ivern / Kennen, non touchés malgré
des totaux très hauts, devraient l'être si leur puissance vient bien de leurs
stats de base — sinon c'est que leur force est ailleurs et le moteur les surcote.

---

## Entrée n°4 — 03/08/2026 — CE QUE DIT LE RESPONSABLE DE L'ÉQUILIBRAGE

Source : Tim (@TheTruexy), Live Balance Lead TFT / Senior Game Designer Riot.
Trois posts du 03/08. C'est la source d'INTENTION la plus proche de la décision
qu'on puisse avoir. À suivre en priorité à chaque patch.

### 1. CORRECTION DU BILAN — Kennen passe de "non touché" à CONFIRMÉ
Tim écrit qu'une omission parmi les nerfs est Kennen, qu'ils sont d'accord qu'il
est trop fort actuellement, et qu'ils enquêtent sur un bug d'application des
brûlures Inferno qui constituerait un nerf significatif pour lui.
=> Le moteur avait Kennen en candidat NERF (198, n°3 du palier 5). Le dev confirme
   explicitement la surpuissance ; le nerf est seulement différé.
=> BILAN RÉVISÉ : 5 confirmés sur 11, 0 contredit.
   (Master Yi, Rengar, Draven, Azir appliqués + Kennen confirmé verbalement.)

### 2. ANGLE MORT STRUCTUREL DU MOTEUR — la découverte la plus importante
Tim explique qu'au niveau de la méta les 4-coûts galéraient, et que le patch
booste des 4-coûts peu joués tout en nerfant pas mal de 5-coûts haut de gamme.
=> Ça explique TOUS les "faux négatifs" de l'entrée n°3 (Sivir, Lillia, Nidalee,
   Zyra buffés alors que bien classés) : ce n'était pas de la puissance
   individuelle, c'était un REÉQUILIBRAGE DE PALIER ENTIER.
=> Or le moteur normalise chaque champion par la MÉDIANE DE SON PALIER. Il est
   donc mathématiquement incapable de voir qu'un palier entier est faible :
   la médiane bouge avec le palier. C'est un angle mort de construction.
=> CORRECTIF À BÂTIR (chantier n°2, après l'axe SORT) : un indice INTER-PALIER,
   comparant la valeur brute à la courbe de coût attendue plutôt qu'à la médiane
   du palier. Sans lui, le moteur ne verra jamais un patch de rééquilibrage de palier.

### 3. INTENTIONS DÉCLARÉES — utilisables directement en partie
- Riftbeast et Solar : nerfés VOLONTAIREMENT, Tim voulant une méta où ces deux
  compos ne dominent pas la fin de partie. => CORRECTION de l'entrée n°3 : j'y
  donnais Riftbeasts "neutre" (buff Draven compensant le nerf Elder Dragon).
  C'est FAUX au regard de l'intention : c'est une compo VISÉE. Elle descend.
- Elise : la compo tank AS reste voulue viable, mais Tim la considère d'abord
  comme un tank ; ils soutiennent les objets tank classiques sur elle et baissent
  son potentiel de carry. Il la compare à l'Udyr du Set 15.
  => Ne plus la construire en carry. Objets tank.
- Wisps : grosse passe sur les valeurs aberrantes de combat et sur l'économie
  fournie. Tim précise qu'ils reviendront vite en arrière si ça va trop loin.
  => Instabilité annoncée sur les Wisps. Blossom (ligne Wisps) est exposée aux
     deux sens. Ne pas se figer dessus avant stabilisation.

### 4. LEÇON DE MÉTHODE
Le compte du Live Balance Lead vaut plus que n'importe quelle tier list : il donne
l'INTENTION avant que la stat ne la reflète. C'est exactement le créneau que le
moteur vise. Nouvelle règle : à chaque patch, lire @TheTruexy AVANT de conclure.

### Pari n°3 — à vérifier au prochain patch
Kennen sera nerfé, ou verra ses brûlures Inferno corrigées à la baisse.
Le prochain patch touchera encore majoritairement des ratios de sort.

---

## Entrée n°5 — 03/08/2026 ~18h30 — PHOTO PRÉ-PATCH FIGÉE

Première photo de winrates réels du projet. Source metatft.com/pbe-comps,
121 968 compos analysées sur la fenêtre « Last Day », patch 18.1 PBE, relevée
AVANT déploiement (annoncé vers midi PT / 21h CEST).

Détail complet et 6 prédictions falsifiables : photo_prepatch_03aout2026.md
Relecture prévue MERCREDI 5 août (règle des 48 h après patch).

Tête de classement pré-patch : Inferno Taric 3.29 · Riftbeast Elder Dragon Draven
3.37 · Executioner Ezreal Draven 3.66 · Flora Fatalis Alune 3.69 · Sprykin Gnar 3.75.

Deux faits notables :
- Les trois 5-coûts les plus présents dans les compos (Ivern, Elder Dragon, Kennen)
  sont exactement les trois plus hauts totaux du moteur au palier 5 (207, 201, 198).
  Première corrélation observable entre le moteur et une donnée de terrain.
- ANOMALIE : Tim annonce nerfer Solar pour qu'elle cesse de dominer, mais aucune
  compo Solar n'apparaît dans le classement relevé. À élucider avant d'en tirer
  quoi que ce soit.

C'est la première fois que la boucle d'apprentissage est fermée des deux côtés :
une prédiction datée ET une mesure à venir pour la trancher.

---

## PROTOCOLE PBE — arrêté le 03/08/2026, applicable jusqu'au 26/08

OBJECTIF FINAL (rappelé par l'utilisateur, prime sur tout le reste) :
prédire la MÉTA avant qu'elle n'existe — à chaque patch, et surtout à la fin du
PBE, pour sortir la méta du live le 25/08 avant que la moindre partie soit jouée.

### CORRIGÉ le 03/08 après retour utilisateur — l'exercice CENTRAL du projet
La boucle principale est : LIRE LE PATCH -> PRÉDIRE LA MÉTA -> COMPARER AUX STATS.
J'avais d'abord classé cet exercice comme "quasi tautologique". C'est une erreur.
Ce n'est tautologique que pour une unité isolée (Taric nerfé donc Taric baisse).
Pour une COMPO ça ne l'est pas : il faut agréger des nerfs et buffs hétérogènes
sur 8 unités + traits + augments + wisps, et en sortir un CLASSEMENT ordonné.
Rien dans les notes ne dit de combien de places Inferno Taric va tomber.

C'est aussi la répétition EXACTE du livrable du 25/08 : ce jour-là on aura les
notes finales du 18.1 et zéro partie jouée. La seule matière sera les notes.
Chaque patch PBE est donc une répétition générale avec correction gratuite à H+48.

### Les 3 types de prédiction — tous comptent, mais séparément
  A — MÉTA D'APRÈS NOTES (EXERCICE PRINCIPAL) : à partir des notes seules,
      produire un CLASSEMENT ORDONNÉ des compos attendu après patch, avec sens
      et amplitude du mouvement. Scoré par corrélation de rang avec les stats
      réelles à H+48. C'est la compétence du 25/08.
  B — INTENTION DU DEV : Tim annonce vouloir faire tomber telle compo ; y
      arrive-t-il ? Teste l'efficacité de Riot et la fiabilité de ses annonces
      comme source. Scoré à part.
  C — ANTICIPATION SANS NOTES : prédire les nerfs/buffs AVANT publication, à
      partir des seuls indices du moteur. C'est ce qu'a fait l'entrée n°1
      (5/11 confirmés, 0 contredit). Sert à valider le MOTEUR lui-même.

A est l'objectif. C valide l'outil qui alimente A. Ne pas mélanger les scores.

### Rituel à chaque patch (dans cet ordre, sans sauter d'étape)
  1. AVANT les notes : poser la prédiction C (candidats nerf/buff depuis les
     seuls indices du moteur). Datée. Valide le moteur.
  2. Photo des winrates AVANT déploiement (metatft.com/pbe-comps, noter volume).
  3. Lire @TheTruexy (Live Balance Lead) : intentions déclarées.
  4. Lire les notes : champions, traits, augments, wisps.
  4bis. EXERCICE PRINCIPAL — produire la prédiction A : classement ordonné des
     compos attendu après patch, avec pour chacune le sens du mouvement et une
     amplitude estimée (en places). Écrit AVANT tout accès aux stats post-patch.
  5. Récolte lolchess/set18/stats -> diff des stats de base.
  6. H+48 minimum : relire les winrates. Trancher les prédictions une par une.
  7. Écrire l'entrée de journal : ce qui est confirmé, contredit, non testé.

### Règles de rigueur (non négociables)
  - 48 h après patch avant de lire une stat. Jamais le lendemain matin.
  - Noter le volume d'échantillon à côté de chaque chiffre. Sous 200 parties,
    on n'ordonne pas.
  - Une prédiction non datée avant le fait ne compte pas. Jamais de rattrapage.
  - Aucun ajustement de poids avant 6 observations, et jamais plus d'un à la fois.
  - Séparer toujours ce qui est MESURÉ de ce qui est DÉRIVÉ.

### État des chantiers, par ordre de priorité
  1. AXE SORT — le trou principal. Riot équilibre presque exclusivement sur les
     ratios de sort ; sans cet axe le moteur est aveugle à ce qui décide la méta.
  2. INDICE INTER-PALIER — le moteur normalise par médiane de palier, il ne peut
     donc pas voir qu'un palier entier est faible (cas des 4-coûts, 03/08).
  3. FONCTION CHIFFRES -> FORCE DE COMPO — PRIORITÉ RÉELLE N°1 au regard de
     l'objectif. Le moteur prédit les NERFS, pas la MÉTA : c'est la sortie qui
     manque, et c'est celle qu'il faut le 25/08. À calibrer en
     croisant indices et winrates réels, maintenant qu'on a enfin les deux bouts.
  4. Index de recherche par intention : fait le 03/08. Peut s'enrichir.

### Contraintes assumées
  - 3 semaines et demie, soit 3 à 4 patchs majeurs : sous le seuil des 6
    observations. La calibration du 25/08 sera UTILISABLE, pas SOLIDE.
    L'annoncer comme telle, ne pas la survendre.
  - La méta live ne sera pas la méta PBE (population, reset de ladder, ajustements
    de dernière minute). La fonction devra partir des CHIFFRES FINAUX du 18.1,
    pas extrapoler les winrates PBE.

### Prochaine échéance
  MERCREDI 5 août : trancher les 6 prédictions de photo_prepatch_03aout2026.md.

---

## Entrée n°6 — 04/08/2026 21h31 — HOTFIX + PROBLÈME DE PROTOCOLE

Tim (@TheTruexy) publie un « petit correctif d'équilibrage pendant que le patch
du week-end se stabilise ». Soit 24 h APRÈS le déploiement du gros patch.

### PROBLÈME DE MÉTHODE — la règle des 48 h est caduque en PBE
On s'était fixé 48 h après patch avant de lire une stat. Impossible ici : les
patchs PBE tombent à ~24 h d'intervalle. Conséquence directe : la fenêtre de
données PURES pour le patch du 03/08 est de 24 h, et elle se referme maintenant.
NOUVELLE RÈGLE PBE : relever les stats DÈS QU'UN NOUVEAU PATCH EST ANNONCÉ, sans
attendre. Noter la durée de la fenêtre propre à côté de chaque mesure. La règle
des 48 h ne redeviendra applicable qu'au live (26/08), où la cadence est bimensuelle.

### Contenu du hotfix
CHAMPIONS
  Gnar (5c)  NERF MAJEUR : dégâts de Leap 150/225 AD -> 100/150 AD  (−33 %)
  Krug (3c)  NERF : dégâts de sort en % PV 10 % -> 8 %
  3-étoiles de 4-coûts (cas rare, impact marginal) : Amumu 2.2 -> 4 % soin PV max,
    Lillia soin 600 -> 800 AP, Nidalee AD ignore armure 40 -> 80 %
TRAITS
  Blossom NERF : or par charme acheté 5 -> 4
  Coven : cashout 500 essence à 4 emblèmes aléatoires retiré
WISPS
  Nature's Wrath réactivé, coût 6 or -> 1 or, délai 8 -> 10 s, délai d'amélioration
  6 -> 8 s. Le passage à 1 or est un changement d'accès majeur.
OBJETS
  Dawncore NERF (réduction de mana par cast 7 % -> 4 %)
  Titanic Hydra NERF (6 % -> 4 % de l'AD de base en dégâts bonus)
  Wit's End NERF (dégâts on-hit 40/40/60/80/100/115 -> 30/30/55/75/95/115)
  Cappa Juice RETIRÉ (bug)
AUGMENTS
  Consuming Flora donne 3 or ; Consuming Flora++ RETIRÉ ; Slightly Magical Roll
  nerfé (cashout 6 : spatule -> emblème aléatoire) ; exclusions ajoutées sur
  Emblem Ensemble, Reroll Subscription et Trait Ladder.

### Impact sur la prédiction A du 03/08 (à intégrer en v0.2)
Gnar figure dans 6 des 17 compos suivies et il est CARRY de Sprykin Gnar.
Un nerf de 33 % sur sa compétence principale invalide notre estimation pour
cette ligne (on la prédisait à 3.87). Blossom prend un nerf d'économie qui touche
ses deux lignes. Wit's End et Titanic Hydra frappent les compos on-hit et bruiser.
=> La prédiction A du 03/08 reste valide POUR LA FENÊTRE 03/08 21h -> 04/08 21h30
   UNIQUEMENT. Au-delà, elle est contaminée et ne doit plus être scorée.

### Observation utile pour le projet
Deuxième patch d'affilée où Riot ne touche presque QUE des ratios de sort, des
valeurs d'objets et de l'économie. Les stats de base ne bougent pas. Ça confirme
l'entrée n°3 : l'axe SORT est bien le seul axe qui compte, et le moteur actuel
ne peut pas voir venir ces patchs.

---

## Entrée n°7 — 04/08/2026 22h — PREMIÈRE MESURE : LA PRÉDICTION EST RATÉE

Photo post-patch relevée dans la fenêtre propre de 24 h. Détail complet :
photo_postpatch_04aout2026.md

RÉSULTAT : 4 directions justes sur 8. Niveau du hasard. Le prédicteur v0.1 ne vaut
rien en l'état — c'est un bon résultat pour le projet, parce qu'il est net et daté.

TROIS ENSEIGNEMENTS
1. TEST B NÉGATIF. Tim voulait faire tomber Riftbeast ; Riftbeast Draven est
   PREMIÈRE (3.24, 71 % top 4). Les annonces du Live Balance Lead disent ce que
   Riot VEUT, pas ce que Riot OBTIENT. Ne pas les traiter comme prédictives.
   Correction de l'entrée n°4, qui proposait de les classer en source de 1er rang.
2. POIDS DU CARRY SOUS-ÉVALUÉ (j'avais parié l'inverse le 03/08). Le buff de Draven
   a dominé trois nerfs simultanés dans sa compo. v0.2 : carry 3 -> 5, et baisser K
   (amplitude 4x trop forte sur Inferno Taric).
3. LE MOTEUR EST FAUX HORS PALIER 5. Camille, classée n°1 du palier 1 par le moteur
   et buffée au patch, est le 2e pire champion du jeu (6.11). Master Yi, n°1 du
   palier 3 selon le moteur, est en tier C (4.64). En revanche Ivern, Elder Dragon
   et Kennen — top 3 du moteur au palier 5 — sont tous dans le top 10 réel.

CE QUE ÇA CHANGE : on a maintenant des winrates par champion sur 88 880 parties.
C'est la matière qui manquait pour calibrer une vraie fonction chiffres -> force.
Prochaine étape : régresser les indices du moteur contre les placements réels,
palier par palier, pour savoir quels axes gardent un pouvoir explicatif.

---

## Entrée n°8 — 04/08/2026 — LE MOTEUR NE MARCHE PAS. VERDICT CHIFFRÉ.

Premier test possible depuis la création du moteur : corrélation de rang (Spearman)
entre ses indices et le placement moyen réel des 64 champions, sur 88 880 parties.
Rappel de lecture : placement bas = bon, donc une corrélation NÉGATIVE = le moteur
a raison. Zéro = aucun pouvoir explicatif.

| palier | n  | SURVIE | AUTO  | CADENCE | TOTAL |
|--------|----|--------|-------|---------|-------|
| 1      | 14 | +0.09  | +0.30 | +0.26   | +0.35 |
| 2      | 13 | −0.16  | +0.12 | —       | +0.23 |
| 3      | 13 | −0.13  | +0.01 | +0.12   | −0.04 |
| 4      | 14 | +0.10  | +0.15 | −0.04   | +0.03 |
| 5      | 10 | −0.18  | +0.20 | −0.32   | −0.07 |
| GLOBAL | 64 |        |       |         | −0.17 |

**Coût brut du champion vs placement : −0.84.**

### Ce que ça dit, sans détour
1. Les trois axes du moteur n'expliquent RIEN. Aucune corrélation ne dépasse 0.35
   en valeur absolue, et les signes sont incohérents d'un palier à l'autre.
   Aux paliers 1 et 2, la corrélation est même POSITIVE : le moteur s'y trompe
   systématiquement (plus il note haut, plus le champion joue mal).
2. La seule variable qui prédit vraiment le placement, c'est le COÛT (−0.84).
   Ce qui est trivial : un 5-coût joue mieux qu'un 1-coût.
3. Or le moteur normalise chaque champion PAR LA MÉDIANE DE SON PALIER. Il détruit
   donc volontairement la seule information qui fonctionne, et ne la remplace par
   rien. C'est une erreur de conception, pas un défaut de calibration.

### Pourquoi c'était prévisible avec le recul
On l'avait établi dès la récolte du 31/07 sans en tirer la conséquence : au sein
d'un même palier, PV, AD et résistances suivent un gabarit quasi identique. Les
stats de base ne différencient pas les champions d'un même coût — elles définissent
le coût. Ce qui différencie, ce sont les ratios de sort. Qu'on n'a pas, et qu'on ne
peut pas obtenir (migration Unreal, pipeline CommunityDragon cassé, cf. ce jour).

### DÉCISION À PRENDRE
Le moteur de puissance mathématique, dans sa forme actuelle, est une impasse.
Les chantiers « axe SORT » et « indice inter-palier » ne le sauveraient pas :
le premier est impossible faute de données, le second reviendrait à mesurer le coût.

Voie restante pour l'objectif (prédire la méta avant qu'elle existe) :
partir des NOTES DE PATCH et des WINRATES OBSERVÉS, pas d'un modèle physique.
C'est-à-dire la ligne A du protocole — le prédicteur v0.1, à calibrer.
Ça reste faisable et c'est ce qui sera disponible le 25/08.

À conserver du moteur : rien pour la prédiction. Les lignes de stats dans l'Oracle
gardent une valeur descriptive en partie (savoir qu'un champion a 0.55 de vitesse
d'attaque reste utile pour choisir des objets), mais les indices 0-100 doivent être
retirés ou clairement étiquetés comme non prédictifs.

### Date du live CONFIRMÉE : 26 août 2026
Divergence tranchée. Le 12 août était le plan initial ; la sortie a été repoussée
de deux semaines à cause de la migration Unreal. Riot écrit dans son aperçu du
27/07 que le set sort avec le patch 18.1 le 26 août, et le compte @TFT annonçait
le 24/07 « PBE July 28, Live August 26 ». Le README du miroir GitHub qui indique
le 12 août n'a pas été mis à jour après le report.

---

## Entrée n°9 — 04/08/2026 — LE PRÉDICTEUR NON PLUS. ET CE QUE ÇA RÉVÈLE.

Calibration de v0.1 sur les 8 compos observées avant/après le patch du 03/08,
par minimisation de l'erreur quadratique sur 3 paramètres (poids carry, poids 2e
unité, facteur K).

Erreur moyenne obtenue :
  v0.1 (carry=3, K=0.06) ............................ 0.243 place
  **Ne RIEN prédire (garder la valeur d'avant)** ..... **0.147 place**
  v0.2 calibré (carry=8, 2e=6, K=0.008) ............. 0.116 place

### Lecture
Le modèle calibré ne bat le fait de ne rien prédire que de 0.03 place — sur
8 points de données et 3 paramètres ajustés. C'est du surapprentissage, pas un
signal. Deux indices le confirment : K tombe à 0.008 (mouvements quasi nuls) et
le poids du carry sature à la borne haute. Signature classique d'un optimiseur
qui cherche à annuler un modèle sans information.

**Conclusion : le prédicteur de méta ne fonctionne pas non plus.**

### MAIS le meilleur modèle nous apprend quelque chose d'exploitable
Le modèle le plus performant qu'on ait est « les compos ne bougent presque pas ».
0.147 place d'erreur moyenne d'un patch à l'autre, sur un patch pourtant qualifié
de « premier gros patch du set » par le Live Balance Lead lui-même.

=> LA MÉTA EST INERTIELLE. Un patch normal ne la rebat pas ; il la déplace à la
   marge. C'est cohérent avec l'échec de Riot à faire tomber Riftbeast, et avec
   le fait que les mêmes 5-coûts (Ivern, Kennen, Taric) dominent depuis le début.

### RÉORIENTATION PROPOSÉE — à valider avec l'utilisateur
Les deux hypothèses de départ du projet sont mortes en 4 jours, ce qui est une
bonne nouvelle par rapport à les découvrir le 25/08 :
  - prédire depuis les stats de base : FAUX (entrée n°8, corrélation nulle)
  - prédire le mouvement des compos depuis les notes : FAUX (cette entrée)

Ce qui reste vrai et mesuré :
  1. Le coût explique 84 % du rang d'un champion.
  2. La méta bouge peu (0.147 place/patch).
  3. Les winrates réels sont disponibles, gratuits, et à jour à l'heure près.

=> La meilleure prédiction de la méta du 26/08 sera probablement LA MÉTA PBE DE
   FIN, ajustée à la marge des derniers changements. Pas un modèle physique.
=> L'avantage compétitif réel du projet n'est donc PAS prédictif, il est
   OPÉRATIONNEL : être le plus rapide à lire la donnée le jour J et à la traduire
   en décisions pendant la partie. C'est exactement ce que l'Oracle sait faire.

Ce n'est pas l'ambition initiale, mais c'est la version qui tient debout,
et elle sert directement l'objectif Challenger.

### Prochain test (fenêtre ouverte cette nuit)
Prédiction naïve pour le hotfix du 04/08 21h31, à vérifier demain :
  - Sprykin Gnar se dégrade nettement (Gnar carry, −33 % sur son Leap)
  - Les 5 autres compos contenant Gnar se dégradent légèrement
  - Blossom se dégrade (or par charme 5 -> 4)
  - TOUT LE RESTE NE BOUGE PAS de plus de 0.15 place
Si cette prédiction naïve bat un modèle élaboré, l'inertie est confirmée.

---

## Entrée n°10 — 05/08/2026 07h21 — LA RÈGLE. ET LE PARI KENNEN GAGNÉ.

Nouveau patch (3e en 3 jours). Contenu principal :
CHAMPIONS — nerfs : Kennen (AS 0.9->0.85 ET sort 550/825->525/785, double nerf),
  Taric (bouclier passif 200/400+12% PV -> 175/350+10%, soin -11%), Ivern
  (bouclier 165/325 -> 150/275 AP).
CHAMPIONS — buffs : Akali +11 %, Cinderling +26 %, Pebbles +7 %, Yorick, Scuttlecrab
  +20 %, Yunara, Cassiopeia, Razorbeak, Ezreal (logique de dash), Nidalee, Sivir.
TRAITS : Adaptor BUFF · Blossom NERF (PV bonus 12->10 %) · Coven BUFF (paliers
  abaissés) · **Riftbeast BUFF** (7 pièces armure/RM 3->5) · Solar NERF (seuil 3 AS
  25->18 %).
SYSTÈME : XP niveau 8 : 56 -> 60 · niveau 9 : 64 -> 68. **Le fast 9 coûte plus cher.**
AUGMENTS : Jungle Pathing retiré · Patience is a Virtue nerf · Nesting Dolls buff.
WISPS : très large passe, beaucoup de coûts tombent à 0 or.

### PARI n°3 GAGNÉ (posé le 03/08)
« Kennen sera nerfé. » C'est fait, et doublement. Chaîne complète : le moteur le
signale le 31/07 -> Tim admet la surpuissance le 03/08 -> nerf appliqué le 05/08.

### LA DÉCOUVERTE — Riot équilibre sur le PLACEMENT MOYEN OBSERVÉ
Rangs (sur 64) des champions nerfés ces deux derniers patchs :
  Kennen 2e · Ivern 3e · Gnar 4e · Taric 5e   (Krug, 51e, est l'exception)
Rangs des champions buffés :
  56e Pebbles · 58e Scuttlecrab · 59e Akali · 60e Cinderling · 61e Cassiopeia
  (plus quelques-uns au milieu : Ezreal 12e, Nidalee, Sivir, Yunara, Razorbeak)
Et l'AMPLITUDE suit le rang : Cinderling (60e) +26 %, Scuttlecrab (58e) +20 %,
Akali (59e) +11 %, Pebbles (56e) +7 %, Cassiopeia (61e) +6 %.

=> Le prédicteur de nerfs/buffs n'est pas un modèle physique. C'est le CLASSEMENT
   DES PLACEMENTS RÉELS, lu directement. Trivial rétrospectivement : c'est
   littéralement le métier d'un Live Balance Lead.
=> Ça enterre définitivement le moteur (entrée n°8) tout en donnant ce qu'on lui
   demandait. On avait la réponse sous les yeux depuis qu'on a accès à MetaTFT.

### PARI n°4 — le plus net qu'on ait posé (à vérifier au prochain patch)
**Lux sera nerfée.** Rang 1 (3.34), non touchée sur les deux derniers patchs,
seule du top 5 encore intacte.
Suivants les plus probables : Draven (6e, 3.68) et Maokai (7e, 3.70).
Et côté buffs : Caitlyn (64e, 6.12), Camille (63e, 6.11), Elise (62e, 5.57) —
les trois derniers, tous encore non touchés.
Si ce pari passe, la règle est établie et devient le coeur du projet.

### ANOMALIE — Riftbeast BUFFÉ
Tim déclarait le 03/08 vouloir que Riftbeast cesse de dominer les fins de partie.
Riftbeast Draven est n°1 des compos (3.24) et le trait reçoit un BUFF (7 pièces).
Hypothèse : le palier 7 est rarement atteint, le buff vise la version verticale
sans toucher la version forte. À vérifier. Confirme en tout cas l'entrée n°7 :
les déclarations d'intention ne sont pas prédictives.

### IMPACT DE JEU IMMÉDIAT
- Le fast 9 est nerfé structurellement (XP 8 et 9 plus chers). Les compos « cap »
  perdent de la valeur ; les lignes qui plafonnent en 8 en gagnent relativement.
- Solar prend son 3e nerf consécutif, Blossom son 3e aussi. Deux lignes à éviter.
- Les Wisps à 0 or changent l'économie de début de partie en profondeur.

---

## Entrée n°11 — 13/08/2026 — PARI n°4 GAGNÉ. LA RÈGLE TIENT, ET ELLE EST OPÉRATIONNELLE.

Reprise après une semaine de trou dans le suivi (07 -> 12/08). Lecture directe du
compte de Tim (@TheTruexy) + MetaTFT.

### CADENCE RÉELLE DES PATCHS PBE
03, 04, 05, **07, 10, 11, 12** août. Sept patchs en dix jours. Quatre patchs
n'avaient pas été suivis. La cadence PBE est quasi quotidienne, confirmé.

### VERDICT DU PARI n°4 (posé le 05/08) — GAGNÉ
Prédiction : « Lux sera nerfée » (rang 1, 3.34, seule du top 5 intacte).
RÉSULTAT — patch du 11/08, section Champions, 5 Cost :
  **▼ Lux — Coven Resist Reduction : 12 >>> 8**
Prédiction jumelle : « Elise (62e) sera buffée ».
RÉSULTAT — même patch, 2 Cost :
  **▲ Elise — On-Attack Healing : 55/85/160 >>> 55/90/170**
Autres buffs du 11/08 cohérents avec le bas de classement : Cassiopeia (61e,
encore buffée : 425/640/1020 >>> 440/660/1050), Scuttlecrab (58e, encore buffée),
Krug, Karma, Varus, Kha'zix, Warwick, Mama Beak.
Nerfs du 11/08 : Lux, Master Yi, Sentinel.

=> **La règle de l'entrée n°10 est confirmée sur un patch qu'on n'avait pas vu au
   moment de poser le pari.** Riot équilibre sur le placement moyen observé.
   Ce n'est plus une observation rétrospective, c'est une prédiction validée.

### LE PATCH DU 12/08 (22h22) — SANS INTÉRÊT POUR L'ÉQUILIBRE
Tim l'annonce lui-même : peu de changements d'équilibre. Contenu réel :
- TRAITS : **refonte de Blackthorn**. Stats de sacrifice de base BUFFÉES (Tank
  17%PV/17 res -> 20%PV/17 res ; Champion AD 22+10%AS -> 24+12%AS ; Champion
  magique 13% amp -> 14% amp). **6 pièces REFAIT** : PV 350 -> 500, gain de stats
  +50%, l'unité sacrifiée meurt désormais comme au palier 2/4, stats bonus retirées.
- Primal : Phoenix compte désormais les kills de non-champions.
- WISPS : Curio Cart ne donne plus d'Artefact aléatoire, coût max affiché 15 or.
- OBJETS (Artefacts) : Dawncore ▼ · Eternal Pact ▼ (AP 40->35) · Fishbones ▼
  (AS et AD 30% -> 25%) · Forbidden Idol ▲ (PV 250->400, conversion 35->40%) ·
  Talisman of Ascension ▲ (regen 8->12) · **Titanic Hydra ▼▼ (4% -> 2%, moitié)**.
- Une longue liste de corrections de bugs, dont plusieurs sur Lux (le script de
  gestion de ses formes est nettoyé ; Ride the Wave et Leblanc ne créent plus de
  copies de Lux comptant séparément pour les traits). Nerf indirect probable.
- Tim annonce vouloir baisser le taux d'apparition des Anvils (trop élevé avec
  Ornn et les Wisps).

### LA MÉTA A COMPLÈTEMENT TOURNÉ (MetaTFT, 219 944 compos, patch 18.1 Aug-10)
Riftbeast Draven, n°1 le 04/08 à 3.24, N'EST PLUS DANS LE TOP. Nouveau classement :
  1. Executioner **Yunara** (niv 6)      3.60   PR 0.41   Top4 67.0 %
  2. Blossom **Sett** (fast 8)           3.79   PR 0.16   Top4 62.9 %
  3. Invoker **Nidalee** (fast 8)        3.81   PR 0.09   Top4 64.9 %
  4. Flora Fatalis **Cassiopeia** (niv 7) 3.84  PR 0.10   Top4 63.9 %
  5. Fae **Tristana** (niv 7)            3.89   PR 0.29   Top4 60.9 %
  6. Adaptor **Master Yi** (niv 7)       3.91   PR 0.08   Top4 61.3 %

### LA DÉCOUVERTE OPÉRATIONNELLE — les buffés d'hier sont les carries d'aujourd'hui
Croisement des buffs du 05/08 avec le classement des compos du 13/08 :
  Yunara   buffée 05/08 (400/680 -> 450/730)      -> carry de la compo **n°1**
  Cassiopeia buffée 05/08 PUIS 11/08              -> carry de la compo **n°4**
  Nidalee  buffée 05/08 (resists, heal, AP form)  -> carry de la compo **n°3**
  Sivir    buffée 05/08 (165/250 -> 180/270)      -> pièce de la n°2 et de la n°5
Ces quatre-là étaient en bas de classement il y a huit jours.

=> **Chaîne complète et exploitable : bas de classement -> buff Riot -> carry de
   la méta au patch suivant.** C'est ça, l'avantage réel du projet. Pas un modèle
   de puissance : la lecture de la liste des buffs, jouée avant que la méta suive.

### ERREUR À CORRIGER DANS MES CONSEILS DU 05/08
J'avais écrit « éviter Solar et Blossom, trois nerfs consécutifs chacune ».
**Blossom Sett est la compo n°2 aujourd'hui (3.79).** Le nerf répété n'a pas tué
la ligne. Leçon : un nerf ne signifie pas une ligne morte, il signifie une ligne
que Riot juge trop forte — souvent encore forte après. Ne plus déduire
« nerf = éviter » ; seule la donnée de placement tranche.

### PRÉDICTION POUR LE PROCHAIN PATCH D'ÉQUILIBRE (à vérifier)
Le 12/08 étant vide d'équilibre, le prochain patch devrait toucher :
  NERFS attendus : **Yunara** (carry n°1), Sett, Nidalee — têtes du classement.
  BUFFS attendus : le bas du classement des unités, à relever avant de parier.
Note : il faut refaire une photo des placements par CHAMPION (pas par compo) pour
poser un pari propre. C'est le prochain travail.

---

## Entrée n°12 — 14/08/2026 — RAFRAÎCHISSEMENT. UNE COMPO NAÎT SOUS NOS YEUX.

Correction : l'entrée n°11 et le premier relevé ont été datés 13/08 par erreur, ils
sont du 14/08. Un seul relevé fait foi, celui-ci.

### FRAÎCHEUR DE LA SOURCE — vérifiée
MetaTFT ne propose que DEUX paquets de patch : **18.1 Aug-10** et 18.1 Aug-03.
Le paquet « Aug-10 » englobe donc les patchs du 10, 11 ET 12. On est bien sur le
plus frais disponible. Volume sur 24 h : 298 776 compos (contre 189 504 au relevé
précédent, soit +58 %). Rafraîchissement annoncé toutes les 5 minutes.

### LE CLASSEMENT DES UNITÉS N'A PAS BOUGÉ
Tête identique : Gnar 3.53 · Lux 3.60 · Kennen 3.67 · Ashe 3.67 · Taric 3.68.
Queue identique : Camille 5.83 · Caitlyn 5.73 · Elise 5.30 · Warwick 5.11.
Les écarts sont de l'ordre de 0.01-0.02 place sur 58 % de volume en plus.
=> **Confirme l'inertie mesurée à l'entrée n°9** (0.147 place par patch). La méta
   des unités est stable ; ce sont les COMPOS qui bougent.

### CE QUI A CHANGÉ — UNE NOUVELLE LIGNE APPARAÎT
**Blackthorn Warwick, 3.90, pick rate 0.21. Elle n'existait pas il y a 24 heures.**
C'est le produit direct de la refonte de Blackthorn livrée le 12/08 (6 pièces
refait : PV 350->500, gain de stats +50 %, l'unité sacrifiée meurt comme au 2/4).
Warwick est **63e sur 65 en unité isolée (5.11)** et porte une compo à 3.90 :
l'écart le plus violent du classement. La ligne ne marche que montée en 3 étoiles.

=> **Leçon nouvelle et importante** : la règle « bas de classement + buff = future
   méta » avait une variante qu'on n'avait pas vue — **une REFONTE de trait crée
   une ligne entière d'un coup**, sans passer par le buff d'un champion. Les notes
   de patch qui contiennent le mot « rework » sont à traiter en priorité absolue,
   au-dessus des ajustements chiffrés.

### CLASSEMENT DES COMPOS AU 14/08 (186 952 compos)
  1. Executioner Yunara          3.63   PR 0.44   win 21.5 %
  2. Adaptor Master Yi Kog'Maw   3.80   PR 0.10   win 16.2 %
  3. Blossom Sett                3.87   PR 0.18   win 18.3 %
  4. Invoker Nidalee             3.88   PR 0.13   win 13.3 %
  5. Blackthorn Warwick          3.90   PR 0.21   win 13.1 %   <- NOUVELLE
  6. Fae Tristana                3.93   PR 0.28   win 18.4 %
  7. Flora Fatalis Cassiopeia    3.98   PR 0.11   win 12.8 %
  8. Invoker Morgana             4.05   PR 0.08   win 14.0 %

Mouvement notable : **Adaptor Master Yi Kog'Maw passe 6e -> 2e** alors que Master
Yi a été NERFÉ le 11/08 (AD 70->67). Deuxième cas après Blossom où un nerf ne fait
pas tomber la ligne. La règle prédit les DÉCISIONS de Riot, pas leurs EFFETS.

### CE QUI RESTE EN ATTENTE
**Caitlyn (5.73) et Camille (5.83) sont dernières depuis le 05/08 et n'ont
toujours pas été buffées** — dix jours au fond du classement. C'est l'anomalie
ouverte du moment. Si la règle tient, leur buff est imminent et important.

### ÉTAT DE L'ORACLE
Rafraîchi sur ces chiffres. Radar d'équilibrage en page d'accueil, 8 compos
réelles, ligne « Méta 14/08 » sur chaque fiche champion avec alerte nerf/buff.

---

## Entrée n°13 — 19/08/2026 — NOTES FINALES DU PBE. LA RÈGLE PASSE SON TEST LE PLUS DUR.

### CORRECTION DE DATE — à lire avant le reste
Les entrées n°11 et n°12 ont été datées 13/08 puis 14/08. **Elles sont du 19/08.**
Les CHIFFRES qu'elles contiennent étaient bien relevés en direct et restent valides
comme photo « avant patch du 18/08 » ; seules les étiquettes de date étaient fausses.
Les fichiers reel_placements_13/14aout ont été supprimés et remplacés par
reel_placements_19aout2026.py. Leçon : vérifier la date système avant de dater une
entrée, ne jamais la déduire du fil de la conversation.

### DEUX PATCHS À RATTRAPER
**18/08 — gros patch.** Champions : Cinderling AD 40→45 · Ornn ▼ · Pebbles AD 30→35 ·
Xayah ▼ · **Warwick ▼** (temps d'incantation moins réduit par la vitesse d'attaque) ·
**Yunara ▼** (155/230/350 → 150/225/335 AD) · Kha'Zix ▲▲ (PV 850→950, sort
260/370/550 → 285/400/580) · Mama Beak AD 60→65 · Rengar ▼ · Vi ▼ ·
Brambleback AD 110→115 · **Nidalee AP ▼** (320/480 → 285/425).
Objets : Aegis of Dusk ▲ · Death's Defiance RETIRÉ (bug) · Manazane ▲ ·
Rapid Firecannon ▼ (AS 65→55 %) · Silvermere Dawn ▲ · Wit's End ▼ (PV 400→300) ·
Gargoyle ▲ · Hand of Justice ▲ · Steadfast Heart ▼.
Emblèmes : **Executioner ▼▼** (crit 10→8 %, seuil d'exécution 12→8 %) · Brawler ▼ ·
Juggernaut ▲ · Vanguard ▼.
Traits : Blossom ▼ · **Elderwood ▲** (Protector 7 pièces 400→450) · Inferno (durée de
brûlure 4s→3s) · Vanguard ▼ (bouclier 18/32/42 → 18/30/40).

**19/08 20h24 — notes FINALES du PBE.** Tim : « petits buffs et ajustements
d'augments, la méta a été stable, on ne surréagit pas au patch d'hier ». Il annonce
une **réévaluation en début de semaine prochaine** pour un éventuel changement de
dernière minute avant le patch de lancement.
Champions (tous des buffs) : Akali · Gromp · Azir · Cassiopeia (425/640/1020/1625 →
440/660/1050/1650) · Fiddlesticks · **Ezreal (vitesse d'attaque du sort 25→30 %)** ·
Lillia · Elder Dragon (AD 110→115) · Maokai (PV 1100→1150).
Traits : Blackthorn ▼ (sacrifice tank 20 %→17 % PV) · **Elderwood ▲** (Protector
445/670 → 500/750, mais 9 pièces 60→55 %) · Juggernaut ▲.
Augments : Band of Thieves II ▲ · Bonus Gifts ▼ · Buried Treasures II ▲ ·
Capital Gains II ▲ · Comeback Story ▼ · **Flame On! RETIRÉ** · Golden Dragon ▼ ·
Investment Strategy II ▲ · Living Forge ▼ · Money Hungry+ ▲ · Nesting Anvils+ ▼.

### LA RÈGLE — TEST LE PLUS DUR, PASSÉ
Le 14/08 le classement des compos était : 1. Executioner Yunara · 4. Invoker Nidalee ·
5. Blackthorn Warwick. Prédiction implicite de la règle : leurs carries sont en tête,
donc ils tombent au prochain patch.
Le 18/08, Riot a nerfé **Yunara**, **Nidalee (forme AP)** ET **Warwick**, plus
l'emblème **Executioner** qui portait la compo n°1. Les trois carries des compos de
tête, dans le même patch.
Résultat mesuré aujourd'hui : **Yunara s'effondre de 4.26 (23e) à 4.65 (49e), tier C.**
Master Yi 4.40 → 4.60. La compo Executioner Yunara a DISPARU du classement.
=> La règle ne prédit pas seulement les décisions, ici elle a prédit l'effet.

### ANOMALIE OUVERTE — ELLE DEVIENT LE SUJET
**Caitlyn 5.74 et Camille 5.89 sont dernières depuis le 05/08. Quatorze jours.
Jamais buffées, dans aucun des sept patchs.** C'est la seule contradiction franche
de la règle. Hypothèses : (a) Riot les tient pour des unités de niche dont le
placement moyen bas est normal (unités « à condition ») ; (b) elles sont réservées
pour un buff de lancement ; (c) leur kit a un problème que des chiffres ne règlent
pas. À trancher au patch de lancement du 26/08 : c'est le test décisif.

### MÉTA AU 19/08 (161 584 compos, après le patch du 18)
Unités, tête : Lux 3.46 · Gnar 3.48 · Alune 3.55 · Ashe 3.62 · Ivern 3.66 · Taric 3.66.
**Lux reprend la première place** malgré son nerf du 11/08 — deuxième fois qu'un nerf
ne la sort pas du sommet. Elle est la première cible du patch de lancement.
Compos : 1. Blossom Sett 3.84 (PR 0.48) · 2. Rival Kha'Zix 3.93 (PR 0.11) ·
3. Elderwood Aphelios 3.96 (PR 0.18) · 4. Invoker Nidalee 4.04 (PR 0.45) ·
5. Invoker Morgana Sentinel 4.07 (PR 0.14) · 6. Vanguard Aphelios 4.07 (PR 0.30).

### PRÉDICTION POUR LE PATCH DE LANCEMENT 18.1 (26/08) — pari n°5
NERFS attendus : **Lux** (1re, déjà nerfée deux fois, ne descend pas) · Gnar · Alune ·
et **Blossom** une cinquième fois (compo n°1 à 0.48 de pick rate).
BUFFS attendus : **Camille et Caitlyn** — si la règle tient, c'est maintenant ou jamais.
Tim a annoncé une réévaluation « en début de semaine prochaine » : la fenêtre est
lundi 24 ou mardi 25/08.

### CONSEIL DE JEU AU 19/08
- **Rival Kha'Zix, 3.93 à 0.11 de pick rate** : meilleur rapport force/contestation.
  Kha'Zix a reçu un double buff le 18/08. Demande du 3 étoiles (Kha'Zix, Rengar, Hecarim).
- Blossom Sett est n°1 mais à 0.48 de pick rate : un lobby sur deux la joue. Ne la force pas.
- Elderwood Aphelios en Fast 9 : Elderwood buffé deux patchs de suite.
- Rapid Firecannon et Wit's End nerfés, Death's Defiance retiré. Gargoyle et Hand of
  Justice buffés.

---

## Entrée n°14 — 28/08/2026 — LIVE. **PARI n°5 PERDU.** ET C'EST LE RÉSULTAT LE PLUS UTILE DU PROJET.

Set 18 en live depuis le 26/08. Premier relevé live : 264 048 parties, Platine+.

### LE PARI n°5, POSÉ LE 19/08 — PERDU, NETTEMENT
Prédiction : « Lux sera nerfée au patch de lancement (1re, déjà nerfée deux fois) ;
Camille et Caitlyn seront buffées (dernières depuis 14 jours) ».
Patch de lancement réel (notes du 24/08, dernier patch avant le live) :
  **Lux ▲ BUFFÉE** — Inferno Mana Restore 8→10, Primal Attack Speed 50 %→60 %.
  **Caitlyn ▼ NERFÉE** — dégâts de sort 200/300/500 → 190/285/470 AD.
  **Camille : pas touchée.** Huitième patch consécutif sans la moindre modification.
Les trois prédictions sont fausses. Deux le sont dans le SENS INVERSE.

### POURQUOI — le correctif à la règle
La règle disait : Riot équilibre sur le placement moyen observé. Elle a tenu quatre
fois d'affilée en PBE (Lux 11/08, Elise 11/08, Yunara/Nidalee/Warwick 18/08, avec
l'effet mesuré sur Yunara). Elle casse au lancement, et le cas Caitlyn dit pourquoi :
**on ne peut pas nerfer l'avant-dernière unité du classement en regardant sa moyenne.**
Donc Riot ne regarde pas que la moyenne. Il regarde la **distribution**.
Une unité dont la moyenne est catastrophique mais dont le PLAFOND est abusif
(3 étoiles, ligne de niche, combinaison précise) se fait nerfer quand même. Et une
unité de prestige comme Lux peut être buffée pour l'expérience de lancement, contre
sa position au classement.
=> **La moyenne est un indicateur, pas un oracle.** Ce qui manquait à toutes nos
   analyses depuis le 05/08 : la VARIANCE. Le placement moyen que MetaTFT expose
   gratuitement écrase précisément l'information sur laquelle Riot décide.
=> Le radar de l'Oracle a été réétiqueté en conséquence : « placements les plus
   forts / les plus faibles », plus « cibles de nerf / de buff ».

### CE QUE ÇA CONFIRME QUAND MÊME
Le pari perdu ne renverse pas tout. Reste vrai et mesuré :
- Le coût explique 84 % du rang (entrée n°8).
- La méta est inertielle patch à patch (0.147 place, entrée n°9).
- Une refonte de trait crée une ligne entière d'un coup (entrée n°12, Blackthorn).
- Riot nerfe MAJORITAIREMENT le haut du classement — 4 vérifications sur 5.
Ce qui tombe, c'est l'usage PRÉDICTIF fin du classement. Ce qui reste, c'est son
usage DESCRIPTIF : savoir ce qui est fort maintenant, tout de suite, avant les
tier lists. C'est exactement la réorientation opérationnelle actée en v9.

### LE LADDER N'EXISTE PAS ENCORE — correction du plan de bascule
Le plan prévoyait de démarrer les relevés en **Master+**. Impossible :
  Platine 278 072 · Émeraude 33 592 · **Diamant 2 320 · Master, GM, Challenger : 0**
Deux jours après le reset, personne n'est monté. **On démarre en Platine+**, et on
repasse en Master+ dès que le volume le permet — à vérifier chaque semaine.
Conséquence à garder en tête : la méta Platine+ n'est PAS la méta Challenger. Les
compos faciles y sont surreprésentées.

### MÉTA LIVE AU 28/08 (Platine+)
Unités, tête : **Lux 3.49** (buffée, 1re) · Alune 3.74 · Gnar 3.74 · Ivern 3.84 ·
Taric 3.89 · Ashe 3.91 · Elder Dragon 3.94 · Kennen 3.98 · Maokai 4.13.
Queue : **Camille 6.32** (!) · Akali 5.18 · Warwick 5.16 · Elise 5.13 · Caitlyn 5.04.
Camille à 6.32 est l'écart le plus large jamais relevé sur ce set. Ne pas la jouer.

Compos (321 744 parties) — **aucune compo de la méta PBE n'a survécu** :
  1. Defender Cassiopeia    4.14   PR **0.59**   win 13.0 %   niveau 7
  2. Spellweaver Ahri       4.14   PR 0.23       win 14.2 %   Fast 8
  3. Sprykin Veigar         4.23   PR 0.30       win 13.0 %   niveau 5 (reroll)

### CONSEIL D'OUVERTURE POUR LE CLIMB
**Spellweaver Ahri.** Même placement que Defender Cassiopeia (4.14) pour un pick
rate deux fois et demie plus faible (0.23 contre 0.59) et le meilleur winrate des
trois (14.2 %). À placement égal, la ligne la moins contestée gagne — et 0.59 de
pick rate signifie que la Cassiopeia est partagée dans presque chaque lobby.
Sprykin Veigar en repli quand la partie démarre mal : reroll niveau 5, pas besoin
de monter, juste de l'or et des copies.

### PROCHAIN PARI — n°6, formulé autrement
Vu l'échec du n°5, on ne parie plus sur QUI sera nerfé. On parie sur ce qu'on peut
vérifier : **Defender Cassiopeia sera nerfée ou perdra sa place au prochain patch**
(pick rate 0.59 = Riot ne laisse pas une compo à 60 % de présence). Et **Camille
sera enfin touchée** — neuf patchs sans modification à 6.32, ce n'est pas tenable.

---

## Entrée n°15 — 28/08/2026 — L'ANOMALIE CAMILLE/CAITLYN EST RÉSOLUE.

En allant chercher le plan d'exécution de la Spellweaver Ahri, la réponse est
apparue dans le board de début de partie.

### LE BOARD EARLY DE LA COMPO N°2 EST : **Camille · Caitlyn · Elise · Cassiopeia**
Camille et Caitlyn ne sont pas des unités faibles. Ce sont des unités
**d'early game** : on les pose au niveau 4-5, elles tiennent le board, puis on les
vend. On ne FINIT jamais une partie avec elles.
=> Leur placement moyen ne mesure pas leur force. Il mesure les parties où on est
   resté bloqué avec elles, c'est-à-dire les parties ratées. **6.32 pour Camille est
   un artefact de mesure, pas un verdict de puissance.**

### ET ÇA EXPLIQUE LE NERF DE CAITLYN AU LANCEMENT
Riot a nerfé les dégâts de sort de Caitlyn 200/300/500 → 190/285/470 AD. La valeur
la plus touchée en pratique est celle de 1 et 2 étoiles — c'est-à-dire **sa puissance
d'early game**, exactement là où elle est réellement forte et où le placement moyen
ne voit rien.
=> Riot n'a pas violé sa propre logique. **C'est notre instrument de mesure qui était
   aveugle.** Le placement moyen d'une unité mélange deux usages incompatibles :
   « pièce de transition » et « carry de fin de partie ».

### CORRECTIF DE MÉTHODE — à appliquer désormais
Le classement des unités ne doit JAMAIS être lu seul. Une unité basse est soit
faible, soit une pièce d'early game. Pour trancher, il faut regarder si elle apparaît
dans les boards de début de partie des compos de tête. C'est maintenant intégré à
l'Oracle : Camille, Caitlyn et Elise portent une note explicative sur leur fiche.
Corollaire pour le pari n°6 posé à l'entrée n°14 : « Camille sera enfin touchée » est
une prédiction MAL FONDÉE, je la retire. Il n'y a aucune raison que Riot la buffe.

### LE PLAN D'EXÉCUTION DE LA SPELLWEAVER AHRI (versé dans l'Oracle)
Early : niveau 4 Camille/Caitlyn/Elise/Cassiopeia (35.5 % de rounds gagnés — early
faible, on assume de perdre) → niveau 5 + Diana = **58.1 %**, le vrai basculement →
niveau 6 + Fiddlesticks → niveau 7 + Morgana.
Paliers (Fast 8) : 4 en 2-2 · 5 en 2-6 · 6 en 3-2 · 7 en 3-6 · **8 en 4-2** · 9 en 5-5.
Objets : **Jeweled Gauntlet sur Ahri**, présent dans 95 % des parties, Ahri le porte
68 % du temps. Viser **3 objets sur Ahri** : 90 % des boards en ont trois et l'écart
3 objets → 2 objets coûte une place entière (4.07 contre 5.08).
**Le seuil qui décide tout : Ahri 2 étoiles = 3.69, Ahri 1 étoile = 5.84.** Plus de
deux places. Pas d'Ahri 2 étoiles en 4-2 = on joue le top 6, pas la gagne.
Placement : Ahri au fond dans un coin, Alune et Cassiopeia à côté ; devant Elise,
Diana, Sentinel, Taric, Fiddlesticks ; Morgana en relais.

### DEUX COMPOS DE PLUS RELEVÉES
Adaptor Master Yi 4.24 (PR 0.34, marquée DIFFICILE, 4 unités en 3 étoiles) — seul
survivant de la méta PBE.
**Riftbeast Sentinel 4.25 (PR 0.11, marquée FACILE)** — la moins contestée de toutes
pour un placement à peine moins bon que la tête. Bonne porte d'entrée dans le set.

---

## Entrée n°16 — 19/10/2026 — REPRISE. REFONTE POUR LE SET 19.

Sept semaines sans entrée. Reprise du projet avec un objectif changé : **l'outil
doit être prêt pour le Set 19**, qui sort le 01/12/2026 (patch 19.1, thème musical).

### LE BILAN DU JOUEUR — la seule donnée qui survivra au set
Itario#EUW : **Diamant II**, 105 parties, placement moyen **3.95**,
top 4 **56.2 %**, victoires **17.1 %**.
Centile victoires : **top 4.6 %**. Centile top 4 : **top 25.7 %**.
=> Profil **tout-ou-rien** : il gagne bien mieux qu'il ne se place. Le projet était
   posé sur « objectif top 4, biais flexibilité » ; les parties disent l'inverse.
   Le gain marginal le moins cher est de transformer les 6e-7e en 4e-5e, pas de
   gagner davantage — il est déjà dans le centile 4.6 % sur cet axe.
Progression : Silver I le 28/08 -> Diamant II le 19/10. Courbe régulière sur la
fenêtre 09/10-17/10 (Émeraude 2 -> Diamant 2).

### DIAGNOSTIC DE L'ORACLE
1 123 lignes, 43 % de données et 57 % de moteur ENTREMÊLÉS dans un seul fichier.
Données réparties en trois grappes (lignes 155-599, 692-746, 941-954) séparées par
du moteur. Trois millésimes cohabitaient : 31/07 PBE (l'essentiel, mort depuis trois
mois), 28/08 live (UNITS/METACOMPS), et un bloc LIVE jamais rempli.
=> Chaque rafraîchissement exigeait de l'édition de code dans le HTML. C'est la
   raison mécanique pour laquelle l'outil n'a plus bougé depuis le 28/08.

### LA REFONTE — moteur et données séparés
  oracle/engine.html      34 643 o  — moteur seul, AUCUNE donnée de set
  oracle/data_set18.js    32 938 o  — treize blocs marqués
  oracle/build_oracle.py            — assemble et produit le fichier autonome
`python3 build_oracle.py 18` reproduit l'Oracle à l'octet près (vérifié : 65 298
octets avant refonte, 65 298 après, avant ajout de la nouvelle fonction).
Le constructeur REFUSE de produire un fichier s'il manque un bloc.
=> **Au Set 19 : écrire data_set19.js, relancer la commande. Le moteur ne bouge pas.**

### FONCTION NOUVELLE — le profil de ligne
Tirée directement du profil joueur. Référence neutre 12.5 % de victoires et 4.50 de
placement. Pour chaque compo : pointe = (wr−12.5)/12.5, régularité = (4.50−avg)/4.50,
rapport = pointe/régularité.
  rapport >= 2.5 -> ligne de pointe (des 1ers et des 7es)
  rapport <= 1.2 -> ligne de régularité (monte du LP sans à-coups)
Mesure sur 18.4b Master+ :
  Vanguard Alune        rapport 16.0   pointe extrême (wr 17.4 %, avg 4.39, pr 0.11)
  Spellweaver Veigar    rapport  5.1   pointe
  Executioner Kha'Zix   rapport  2.6   pointe
  Flora Fatalis Azir    rapport  2.2   équilibrée
  Riftbeast Pebbles     rapport  0.8   RÉGULARITÉ (seule du classement)
=> Le patch 18.4b ne propose qu'UNE ligne de régularité, et c'est la plus contestée
   du jeu (pick rate 0.62). Information directement actionnable.

### MASTER+ EST ENFIN EXPLOITABLE
Point en suspens depuis le lancement, tranché : Master 164 480, Grandmaster 23 408,
Challenger 10 760 = ~198 000 parties. Les relevés passent en **Master+**
(171 832 parties sur 24 h). C'était impossible le 28/08 (Master et au-dessus à zéro).
Constante à retenir : **il faut trois à quatre semaines après un reset de ladder.**

### CALENDRIER
  21/10 patch 18.5 · 04/11 patch 18.6 · 11/11 patch 18.6B (dernier du Set 18)
  ~mi-novembre PBE Set 19 (NON ANNONCÉ, à surveiller sur @TheTruexy)
  01/12 Set 19 live, patch 19.1 · 15/12 patch 19.2
Set 18 : PBE 28/07 -> live 26/08, quatre semaines rallongées par la migration Unreal.
Au rythme habituel de deux à trois semaines, le PBE du Set 19 tombe entre le 10 et le
17 novembre. Estimation, pas un fait.

### MÉTA AU 19/10 (Master+, 18.4b, 171 832 parties)
Unités, tête : Lux 3.56 · Alune 3.65 · Gnar 3.82 · Ivern 3.97 · Taric 4.00 ·
Kennen 4.02 · Elder Dragon 4.04.
**Lux est première depuis le 28/08 malgré trois nerfs.** Record du set.
Queue : Caitlyn 5.88 · Camille 5.21 · Elise 5.05 · Tristana 5.04 — toujours les
mêmes, ce qui confirme l'entrée n°15 : ce sont des unités d'early game, leur
moyenne est un artefact de mesure.

### CE QU'ON RÉCOLTE D'ICI LE 1er DÉCEMBRE
Les contenus du Set 18 n'ont aucune valeur de transport. Les constantes de méthode,
si. À mesurer sur 18.5, 18.6 et 18.6B :
  - vitesse de rotation de la méta EN LIVE (mesurée seulement en PBE : 0.147/patch)
  - délai entre un buff et l'apparition de la ligne dans le top (~1 semaine en PBE)
  - seuil de pick rate où la contestation annule l'avantage (intuition 0.6, pas de chiffre)
  - volume minimum pour un classement stable (NMIN_UNIT = 2000, fixé au jugé)
  - profil du joueur remesuré à chaque patch

### EXPÉRIENCE PROPOSÉE
Dix parties en ne prenant QUE des lignes de régularité, comparées aux dix
précédentes. Seul moyen de savoir si le profil tout-ou-rien est un choix ou une
habitude. Six semaines sans enjeu de classement : c'est la fenêtre pour le tester.

### MÉMOIRE DU PROJET
Le plan complet est désormais un DOCUMENT DU PROJET (`plan-set19.md`), pas un
fichier de travail. Raison : Claude ne garde aucun fichier entre deux conversations,
et sept semaines de pause ont coûté une reconstruction complète du contexte. Le
document, lui, persiste.

---

## Entrée n°17 — 19/10/2026 — RATTRAPAGE DES SEPT SEMAINES MANQUÉES.

### AVEU : le suivi patch par patch s'est ARRÊTÉ au lancement
Le journal saute du 28/08 au 19/10. Aucune note prise sur 18.2, 18.3, 18.4.
Cause identifiée, et elle est STRUCTURELLE, pas un oubli :

**@TheTruexy ne publie PAS les notes des patchs LIVE sur X.** Recherche
`from:TheTruexy patch notes` : les résultats sautent du 24/08 directement au 15/10.
En PBE il postait les notes complètes en images à chaque patch ; en live, elles
partent sur la page officielle de Riot et il ne tweete que des commentaires.
=> **La source qui a porté tout le suivi PBE cesse de fonctionner au passage en live.**
   Leçon pour le Set 19 : prévoir la bascule de source au jour du lancement.

### CADENCE RÉELLE DES PATCHS (la constante qu'on cherchait)
  18.1  26/08  (lancement)
  18.2  10/09  (+15 j)
  18.3  23/09  (+13 j)
  18.4  07/10  (+14 j)
  micropatch 08/10 — correction de bugs critiques et de rollbacks du 18.4
  18.4b (non listé dans les calendriers publics, visible dans les filtres MetaTFT)
  18.5  21/10 attendu · 18.6  04/11 · 18.6B  11/11 (dernier du set)
=> **En live : un patch toutes les DEUX SEMAINES. En PBE : quasi quotidien.**
   Rapport d'environ 1 à 14. Le rythme de relevé doit changer d'un facteur 10 au
   passage en live. On avait gardé le réflexe PBE, d'où l'abandon du suivi.
À noter : le 18.4 a introduit des bugs critiques et des annulations de changements
(Tim le reconnaît le 07/10). Un patch live peut être partiellement défait.

### MESURE 28/08 -> 19/10 : LA TÊTE NE BOUGE PAS, LE VENTRE EST LABOURÉ
Comparaison des deux relevés (biais à noter : 28/08 en Platine+, 19/10 en Master+).
  **Top 8 identique, 8 sur 8** : Lux · Alune · Gnar · Ivern · Taric · Kennen ·
  Elder Dragon · Ashe. Aucune entrée, aucune sortie en sept semaines et cinq patchs.
  Déplacement médian sur l'ensemble : 10 rangs. Moyen : 12.1. Maximum : 45.
  Plus fortes montées : Kha'Zix 56e->11e · Azir 58e->14e · Kayle 53e->20e ·
    Brambleback 33e->9e · Varus 60e->38e.
  Plus fortes chutes : Shen 19e->57e · Sivir 22e->58e · Lillia 14e->47e ·
    Cinderling 10e->41e · Sett 15e->42e.
=> **Les patchs déplacent le ventre du classement, pas la tête.** Lux est première
   depuis le 28/08 malgré trois nerfs successifs.
=> Nuance importante à la règle de l'entrée n°10 : Riot nerfe bien le haut du
   classement, mais **les nerfs ne font pas descendre le haut du classement**. Le
   plancher des unités de coût élevé tient. Cohérent avec la corrélation coût/rang
   de −0.84 mesurée à l'entrée n°8 : le coût fixe un niveau que l'équilibrage ne
   franchit pas.

### LECTURE DU PATCH 18.4b (Master+, 171 832 parties)
Unités tout-ou-rien (gagnent beaucoup, se placent moyennement) :
  **Draven place 4.23 / win 22.6 %** — presque le double de la référence 12.5 %
  **Ivern place 3.97 / win 22.4 %** — le seul à cumuler bon placement ET gros winrate
  Maokai 4.25 / 19.7 % · Alistar 4.48 / 14.0 % · Cassiopeia 4.55 / 14.1 %
Unités de régularité (se placent mieux qu'elles ne gagnent) :
  Nidalee 4.45 / 7.7 % · Kog'Maw 4.41 / 8.4 % · Krug 4.41 / 10.8 % ·
  Aphelios 4.31 / 10.5 % · Pebbles 4.37 / 11.2 %
Contestation : Ancient Sentinel dans **41.6 %** des lobbies, Amumu 31.8 %,
Fiddlesticks 27.6 %, Diana 25.7 %.

### CONVERGENCE AVEC LE PROFIL DU JOUEUR
Sa meilleure unité personnelle sur ses 20 dernières parties est **Ivern, 3.57 de
moyenne sur 7 parties** — et Ivern est précisément la seule unité du set à cumuler
bon placement et taux de victoire très élevé (22.4 %). Son instinct le place déjà
sur l'unité qui correspond à son profil tout-ou-rien. Ce n'est pas un hasard à
corriger, c'est une force à exploiter.

### CE QUI N'A PAS ÉTÉ FAIT, ET POURQUOI
Les notes verbatim de 18.2, 18.3 et 18.4 n'ont PAS été reconstituées. Décision
assumée : le Set 18 meurt dans six semaines, ces notes n'ont aucune valeur de
transport et ne changent rien à une partie jouée ce soir. Ce qui avait de la valeur
— la cadence, la source qui lâche, le mouvement mesuré du classement — est pris.

---

## Entrée n°18 — 23/10/2026 — LA CONSTANTE DE ROTATION EST MESURÉE.

Premier relevé à **même tranche d'elo** que le précédent. C'est ce qui manquait
depuis le début du projet pour répondre à « de combien un patch déplace la méta ».

### RELEVÉ 18.5b (Master+, 56 816 parties, 3 derniers jours)
Note : MetaTFT propose 18.5b (690 638 parties au total), 18.5 (5 517 187) et
18.4b (18 122 123). Un correctif 18.5b est donc passé derrière le 18.5 du 21/10.
Unités, tête : Lux 3.58 · Gnar 3.70 · Alune 3.83 · Taric 3.90 · Elder Dragon 3.91 ·
Ivern 3.96 · Ashe 3.98 · Kennen 4.05 · Maokai 4.18.
**Lux reste première. Troisième relevé consécutif.**

### LA MESURE — un patch coûte 0.154 de corrélation de rang
  18.4b -> 18.5b, 4 jours, Master+ -> Master+ : **Spearman 0.846**
  déplacement médian 6 rangs · maximum 32 · **tête 8/8 conservée**
Montées : Sivir 58e->38e · Master Yi 44e->28e · Alistar 35e->20e.
Chutes : Gromp 17e->49e · Rammus 28e->51e · Teemo 22e->43e.

### DEUX CORRECTIONS MÉTHODOLOGIQUES FAITES AU PASSAGE

**1. Ne jamais extrapoler « par jour ».** Le Carnet calculait d'abord une perte de
corrélation par jour, puis l'extrapolait à la semaine (26.9 %). **C'est faux** : la
méta ne dérive pas continûment, elle SAUTE à chaque patch et reste stable entre
deux. L'unité pertinente est le PATCH, pas le jour. Corrigé dans l'outil.
Corollaire : la dérive ENTRE deux patchs reste NON MESURÉE. Il faudrait deux
relevés séparés de plusieurs jours sans patch entre eux.

**2. Vérifier le plancher de bruit avant de conclure.** Le relevé 18.5b a trois fois
moins de volume que le 18.4b (457 002 contre 1 378 194 sur les unités comparées).
Un classement bruité permute tout seul. Simulation de 400 tirages aux volumes réels,
à vraies valeurs IDENTIQUES :
  Spearman attendu si RIEN n'avait changé : **0.982**
  Spearman observé : **0.846**
=> **88 % de l'écart observé est du vrai mouvement.** La rotation est réelle.
Nouvelle commande `carnet.py bruit` : à lancer avant toute conclusion sur un
mouvement, surtout au Set 19 où les premiers relevés PBE auront peu de volume.

### CE QUE ÇA TRANCHE POUR LE RYTHME DE TRAVAIL
Un relevé d'avant-patch se trompe de ~6 rangs en médiane sur chaque unité. Les
patchs tombant toutes les deux semaines : **rafraîchir à chaque patch est nécessaire
et suffisant.** Un relevé par semaine serait du zèle, un par mois trop peu.
C'est la règle de cadence qu'on cherchait, et elle est maintenant chiffrée.

### LE TOP 4 PAR COMPO EST ENFIN RELEVÉ — le mode cumulé est débloqué
Douze compos avec placement, pick rate, winrate ET top 4. Le classement change
complètement selon le mode :
  LADDER (placement)   1. Riftbeast Krug 4.19
  CUMULÉ (top 4)       1. Riftbeast Krug 56.0 %
  CHECKMATE (victoire) 1. **Elderwood Draven 20.5 %** (placement 4.34, top4 51.2 %)
**Elderwood Draven a le meilleur taux de victoire du patch et un placement
médiocre.** C'est la définition d'une ligne de tournoi checkmate.
Inferno Elder Dragon est plus extrême encore : 20.2 % de victoires pour le PIRE
top 4 du classement (48.6 %).

### ANOMALIE DE CONTESTATION
**Riftbeast Krug a un pick rate de 1.01** — plus d'un joueur par lobby en moyenne.
MetaTFT l'affiche en rouge. Meilleur placement ET meilleur top 4 du patch, classée
FACILE : tout le monde la joue. À ne jamais forcer sans scouting.
Rapidfire Kayle offre le contraire : classée FACILE, pick rate 0.07, placement 4.43.

### VÉRIFICATION DE LA LEÇON n°12 — et correction d'une formulation
« En live, les patchs déplacent le ventre du classement, pas la tête. »
**Deuxième observation, pas troisième** (j'avais écrit « troisième fois » : faux,
il n'y a que deux transitions mesurées, 28/08->19/10 et 19/10->23/10).

Mais le fait réel est PLUS FORT que ce que disait la formulation. Ce ne sont pas
seulement huit places conservées : ce sont **les mêmes huit unités, nommément, dans
les trois relevés** —
  **Lux · Alune · Gnar · Ivern · Taric · Ashe · Elder Dragon · Kennen**
— malgré un changement de tranche d'elo (Platine+ puis Master+), 56 jours et au
moins cinq patchs. Seul leur ordre interne bouge. Et **Lux est première aux trois
relevés** (3.49 · 3.56 · 3.58), avec trois nerfs encaissés entre-temps.

La tête du classement est donc structurelle (le coût des unités), pas conjoncturelle
(l'équilibrage). Pendant ce temps le déplacement médian ailleurs est de 6 rangs par
patch. **Corollaire pratique : ne jamais relever le top 8 en espérant un changement.
Relever le ventre, c'est là que tout se joue.**

---

## 02/11/2026 — PREMIÈRE COLLECTE RÉELLE (200 parties)

*Le Miroir avait été construit en août et n'avait jamais vu une seule partie vraie.
Il en a vu 200 ce soir. Voici ce que ça a coûté et ce que ça a appris.*

### LE BLOCAGE N'ÉTAIT PAS CELUI QU'ON CROYAIT

Du 19/10 au 02/11, la collecte a échoué sur un **HTTP 403**. Nous l'avons attribué
quatre fois à la clé API — expirée, regénérée, mal copiée. **La clé n'a jamais été en
cause.**

`collecte.py` n'envoyait qu'un seul en-tête, `X-Riot-Token`. Sans `User-Agent`, urllib
s'annonce « Python-urllib/3.10 », et la bordure de Riot rejette cet agent avec un 403
**dont le corps est identique à celui d'une clé invalide**. Deux causes, un seul
symptôme, aucun test pour les séparer.

Ce qui a tranché : trois appels construits exprès pour se distinguer — un endpoint sans
permission (status-v4), un endpoint TFT (tft-league-v1), et l'appel exact de la collecte
(account-v1). **A=200, B=200, C=200.** Clé bonne, droits bons, bug chez nous.

**Leçon n°19 — un message d'erreur n'est pas un diagnostic.** Quand deux causes
produisent le même symptôme, construire un test qui les sépare. Ne pas réessayer la plus
probable. `collecte.py` affiche désormais le corps de la réponse et l'identifiant de
trace ; `DIAGNOSTIC.bat` fait les trois appels en quinze secondes.

### PRÉDICTION POSÉE AVANT DE REGARDER — puis corrigée

Avant de filtrer, la distribution brute montrait un creux net en 4e place (11) contre un
surplus en 5e (17) : exactement la frontière où le LP bascule. Hypothèse tentante :
« voilà où partent ses points ».

**Testée : 20 000 tirages. Le hasard produit un écart au moins aussi grand dans 15.9 %
des cas.** Non significatif. Aucun conseil donné.

### CE QUI RÉSISTE, APRÈS NETTOYAGE (114 parties, Set 18)

Placement **3.737** · top 4 **59.6 %** · 1res **18.4 %**.

- **top 2 : +2.70 écarts-types** (41 au lieu de 30) — solide
- **7e + 8e : −3.57 écarts-types** (12 au lieu de 28.5) — solide
- **top 4 : dans le bruit** — non significatif

**L'étiquette « tout-ou-rien » est fausse et abandonnée.** Elle supposait un excès de
8es places ; il en reste **2 sur 114**. Le profil réel est un sommet lourd sur un
plancher verrouillé.

### TROIS ERREURS DE MESURE ÉVITÉES, UNE COMMISE

**Évitée n°1 — la population.** Les 200 parties couvraient **deux sets** : 80 du Set 16
(décembre 2025) et 120 du Set 18. Le premier chiffre sorti, 4.08, ne décrivait aucun des
deux. Filtre par set ajouté, affiché avant toute mesure.

**Évitée n°2 — les parties lâchées.** Clément quitte parfois une partie (enfants).
*Aucune mesure ne les aurait écartées* : c'est sa phrase qui a ouvert la piste. La donnée
a ensuite confirmé seule — or restant médian de 0 à 4 à tous les placements **sauf la 8e,
à 33.5**, avec deux parties à **152 et 115 or**, impossibles en jouant. Six retirées
(`or >= 20 ET placement >= 5` : c'est la conjonction qui trahit).

**Leçon n°20 — demander au joueur ce que la donnée ne peut pas savoir.**

**COMMISE, puis rétractée — l'artefact qui ressemblait à un signal.** J'avais relevé que
les 12 parties finies à 20 or ou plus coûtaient 1.19 place, rangé en « suggestif ». C'était
la signature des parties lâchées. Traité comme un signal, cela donnait le conseil « mieux
dépenser ton or » — tiré d'un comportement hors jeu.

**Leçon n°21 — avant de transformer une corrélation en conseil, demander quel mécanisme
la produirait. Si la réponse est « le joueur n'était pas là », ce n'est pas un conseil.**

### CONTRAINTE STRUCTURELLE DÉCOUVERTE — l'API s'est appauvrie

Le Set 18 tourne sur **Unreal Engine** : `TFT16_KogMaw` devient `DA_18_Alistar`,
`game_version` affiche `TFT Unreal Version ?.?.?.?`.

- **`augments` : absent du DTO sur 200/200 parties**, Set 16 comme Set 18.
- **`total_damage_to_players` : 0 pour les huit joueurs** sur tout le Set 18, correct au
  Set 16. Le rang de dégâts est sans valeur.
- `units[].itemNames` : **présent et détaillé.** Les objets craftés sont analysables.

Ce n'est pas la clé : la réponse est enregistrée complète, et les trois appels passent.
Les augments existent comme mécanique (Riot parle d'élargir l'espace de conception « pour
les futurs traits et augments ») — c'est la remontée qui manque. **La liste publique des
réparations post-Unreal ne mentionne pas l'API.** Ni reconnaissance, ni calendrier.

**Conséquence sur l'ambition.** La revue d'augments, décrite comme le cœur de l'Oracle,
n'est pas constructible sur `tft/match/v1` en l'état. Et **tout ce qui est « refusé »
— unité non achetée, augment écarté — est hors de portée par nature** : l'API ne livre
que des boards finaux. Cette limite-là ne se lèvera pas.

À retester dès les premières parties du Set 19.

### PRÉDICTION FALSIFIABLE POSÉE CE SOIR

**Les champs `augments` et `total_damage_to_players` seront toujours vides au lancement
du Set 19 (01/12).** Raison : la régression date du 31/07, elle a survécu à six patchs,
et Riot ne l'a jamais inscrite à sa liste de réparations — ce qui n'est pas inscrit n'est
pas planifié. *À vérifier sur les premières parties du 01/12. Si je me trompe, c'est que
la migration Unreal se termine avec le set, et il faudra retenir que Riot livre des
correctifs de données sans les annoncer.*

---

## 02/11/2026, seconde partie de soirée — mise en ligne et réorganisation

### LE DÉPÔT ET LE SITE SONT EN LIGNE

`github.com/Itario/oracle-tft` → `itario.github.io/oracle-tft`. Chaque poussée régénère
le site depuis les relevés et le déploie. Le site publié ne peut plus diverger des
données : c'est le serveur qui recalcule.

**Une proposition rejetée, à raison.** J'ai proposé de passer le dépôt en privé pour
protéger `profil.json`. Clément a objecté qu'on l'avait laissé public pour la demande
Riot. En vérifiant, la raison est plus forte que la sienne : **GitHub Pages ne publie
pas depuis un dépôt privé hors Enterprise.** Le réglage n'aurait rien protégé — il aurait
supprimé le site.

**Leçon n°22 — un conseil de configuration se teste comme une mesure.** J'ai proposé un
réglage sans vérifier ce qu'il cassait.

**Et `enablement: true` ne marche pas** : le GITHUB_TOKEN d'un workflow ne peut pas créer
le site Pages, même avec `pages: write`. Une action manuelle reste nécessaire une fois
sur un dépôt neuf. La raison est écrite dans `deploy.yml`, là où on reviendra la chercher
— pas dans un README qu'on ne relit pas.

### LE SITE DÉCRIVAIT LE PROJET, PAS L'USAGE

Clément : « l'oracle est encore brouillon… en terme d'utilité ».

Diagnostic : le site était organisé selon la structure du projet — méta, préparer,
outils, profil. Trois onglets sur quatre se lisaient une fois. L'onglet « L'Oracle »
était de la documentation déguisée en page. Et la seule chose vraiment opérationnelle,
le moteur de pivot, était enterrée en bas du deuxième onglet.

Réorganisé selon les **moments d'usage** : `Avant` · `En partie` · `Après` · `Suivi`.

**Leçon n°23 — quand quelque chose est « brouillon en termes d'utilité », chercher ce
que la personne fait, pas ce que l'outil contient.**

### CORRECTION DE MESURE — le top 4 franchit le seuil

Le pipeline `build_miroir.py` a attrapé une de mes conclusions de la veille au soir.
Sur les 120 parties **brutes**, le top 4 était à +1.46 écarts-types : dans le bruit. Une
fois les six parties lâchées écartées — toutes dans la moitié basse — il passe à
**+2.06**. Il franchit le seuil, de justesse.

J'avais annoncé « dans le bruit » sans refaire le calcul après le nettoyage. **Un
nettoyage de données invalide toutes les mesures qui le précèdent, y compris celles
qu'on vient d'énoncer.**

Dans l'autre sens, les traits se sont resserrés : sur 24 vus au moins 12 fois, **deux
seulement** sortent du bruit après nettoyage (Alune −0.85 pour un seuil de 0.81,
Rapidfire −0.79 pour 0.69), et **aucun carry sur 12**. Lunar, solide sur les parties
brutes, est retombé dedans.

### LE RYTHME — la mesure qui manquait

46 jours joués sur 65. **19 jours sans jouer.** 1.75 partie par jour calendaire.

À Master, la décroissance retire 50 LP par jour une fois les 14 parties en banque
épuisées. **Un joueur qui place à 3.74 peut perdre son rang sans jamais mal jouer.**

C'est une mesure de régularité, pas de niveau : elle se lit **sans seuil de bruit**, ce
qui la rend exploitable tout de suite. Avec les parties lâchées, ce sont les deux seuls
gisements de LP identifiés qui ne demandent aucun progrès technique.

**Hypothèse posée, falsifiable :** ce qui sépare Clément de Challenger est un problème de
**volume joué proprement**, pas de niveau de jeu. *Test : la recollecte du 25/11. Si le
profil Master tient le placement de 3.74 sur ~100 parties, l'hypothèse se renforce. S'il
se dégrade nettement, c'est le niveau qui bloque et je me serai trompé.*

### CE QUI TIENT SUR UNE SEULE PARTIE

La review par partie posait un problème de méthode : à n = 1, aucune statistique n'existe.

La seule mesure honnête à cette échelle est **interne au lobby** — le rang de niveau
final parmi les huit, contre le placement réel. Elle ne compare à aucune population, donc
elle ne demande ni échantillon ni seuil de bruit. Positif : il a placé au-dessus de ses
ressources. Négatif : il les avait et ne les a pas converties.

Tout le reste de la liste des parties est présenté comme un **journal**, et le site
l'écrit explicitement plutôt que de laisser croire à une inférence.

### DEUX BUGS DE SORTIE ATTRAPÉS À L'ŒIL

Les verdicts d'écart affichaient « au-dessus du hasard » pour un écart **négatif** :
j'avais confondu le sens de l'écart et son caractère favorable. Les deux coïncidaient
dans trois cas sur quatre, ce qui rendait l'erreur presque invisible.

Et Cinzel, la police de titrage, n'a pas de bas de casse : « 1e » y rendait « 1E ».
Au passage, la première place s'abrège **1re** en français, pas 1e — le gabarit mettait
« e » pour les huit rangs.

**Leçon n°24 — relire la sortie rendue, pas seulement le code qui la produit.**

---

## 03/11/2026 — la constante de rotation tombe, et la question des augments se ferme

*Soirée ouverte par une question de Clément : « en source tu mets MetaTFT ? Il n'y a pas
mieux pour prendre de la data ? »*

### LA RÉPONSE N'EST NI OUI NI NON

Comparaison de MetaTFT et tactics.tools **sur le même patch (18.5), la même tranche
(Master+), 57 unités appariées** :

- **Spearman 0.982**, déplacement médian **1 rang** ;
- plancher de bruit pour ce couple : **0.955** ;
- l'observé dépasse le plancher → **l'écart entre les deux sources est indistinguable de
  l'échantillonnage.**

Un patch, lui, fait tomber la corrélation à 0.82–0.89 avec 4 à 6 rangs de déplacement.
**La différence de source est six fois plus petite que l'effet d'un patch.** Les deux
mesurent la même chose.

**Leçon n°25 — « est-ce qu'il n'y a pas mieux ? » mérite une mesure, pas une opinion.**

tactics.tools reste meilleur *pour le projet*, mais pour des raisons qui n'ont rien à
voir avec la qualité des chiffres : données lisibles sans navigateur, 9× le volume en
Master+, une tranche GM+, les identifiants de Riot, et tous les patchs archivés.

### LA CONSTANTE DE ROTATION ÉTAIT UN ACCIDENT D'ÉCHANTILLON

« Un patch coûte 0.154 de corrélation de rang » figurait dans la charte en gras depuis
dix jours. C'était **un seul couple de relevés**. Nous attendions le patch du 4 novembre
pour en obtenir un deuxième.

Six transitions dormaient dans l'archive publique de tactics.tools. Mesurées :

| de → à | Spearman | plancher | dépl. médian |
|---|---|---|---|
| 18.1 → 18.2 | **0.647** | 0.961 | **8 rangs** |
| 18.2 → 18.3 | **0.819** | 0.984 | 6 rangs |
| 18.3 → 18.4 | 0.874 | 0.914 | *inexploitable* |
| 18.4 → 18.4b | 0.886 | 0.933 | *inexploitable* |
| 18.4b → 18.5 | **0.885** | 0.996 | 4 rangs |
| 18.5 → 18.5c | **0.943** | 0.995 | **2 rangs** |

**La fourchette va de 0.647 à 0.943.** L'ancienne valeur tombait au milieu — ni fausse,
ni représentative. Les deux lignes inexploitables impliquent le patch 18.4 (5 304 parties
en Master+) : le plancher monte trop près de l'observé. *C'est exactement à ça que sert
le plancher, et c'est la première fois qu'il sert à disqualifier plutôt qu'à confirmer.*

**Leçon n°26 — une constante mesurée sur un point n'est pas une constante. Écrire le
nombre de points de mesure À CÔTÉ de toute constante, systématiquement.**

**Leçon n°27 — chercher l'historique avant d'attendre le futur.** Nous planifiions une
mesure pour demain alors que six points étaient publiés depuis des semaines.

### TROIS RÉGULARITÉS REMPLACENT LA CONSTANTE

1. **Au lancement d'un set, la méta tourne deux fois plus vite** : 0.647 et 8 rangs
   contre 0.885 et 4 rangs à maturité. *Conséquence directe : la règle « un relevé par
   patch » ne tiendra pas au 1er décembre.*
2. **Un patch à lettre déplace deux fois moins qu'un patch à chiffre** : 0.943 et 2 rangs
   pour 18.5c, contre 0.82–0.89 et 4–6 rangs pour les patchs numérotés.
3. **La rotation ralentit au fil du set** — trois points seulement, et confondu avec la
   montée du volume. À revérifier au Set 19.

### UNE ERREUR DE SIMULATION, ATTRAPÉE PAR LE SENS ET NON PAR LE CHIFFRE

Mon premier calcul de plancher tirait les deux côtés avec les volumes du PREMIER patch.
Les résultats n'avaient l'air ni absurdes ni suspects — jusqu'à ce qu'une transition dont
le second relevé comptait 5 304 parties affiche un plancher de **0.991**.

Moins de volume doit donner PLUS de bruit, donc un plancher PLUS BAS. Le chiffre allait
dans le mauvais sens.

**Leçon n°28 — quand un chiffre va dans le mauvais sens, c'est le calcul qu'il faut
relire, pas le chiffre qu'il faut expliquer.**

### LA QUESTION DES AUGMENTS EST CLOSE

L'hypothèse de travail était : « les sites de stats publient des winrates d'augments là
où l'API n'en livre pas, donc il existe une autre voie ». **Elle est fausse.**

- **tactics.tools** a gardé la page, les filtres et les colonnes — *At 2-1, At 3-2,
  At 4-2* comprises — et le tableau est **vide**. `augsData` renvoie
  `{singles: [], pairs: [], trios: []}` à toutes les tranches.
- **MetaTFT** a basculé sur une **tier list tenue à la main** par son équipe esport, avec
  des lettres S/A/B et aucun taux, mise à jour tous les quelques jours.

Deux sites majeurs, deux replis différents, même cause. **La donnée n'existe plus pour
personne depuis la migration Unreal.** La seule information disponible est de l'opinion
d'expert — utilisable, mais à étiqueter comme telle, jamais comme une mesure.

*Ne plus chercher de source. La question est close jusqu'au Set 19.*

### PRÉDICTION POSÉE CE SOIR

**Le patch 18.6 du 04/11 donnera un Spearman entre 0.82 et 0.90, avec un déplacement
médian de 4 à 6 rangs.** Raison : c'est un patch numéroté en régime mature, et les trois
transitions comparables mesurées donnent 0.819, 0.885 et 0.885.

*Si le résultat sort de cette fourchette, c'est que la fin de set se comporte autrement
que le milieu — ce qui serait une information neuve, et utile en décembre.*
