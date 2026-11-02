/* ====================================================================
   BLOCS FIGÉS — Set 18
   Fiches du relevé PBE du 31/07/2026 : plans, anciennes compos, BiS,
   augments, lexique de recherche. Elles décrivent des mécaniques, pas
   la méta du jour, et l'Oracle les affiche avec un bandeau.

   Ce fichier NE CONTIENT PLUS les données de relevé (META, UNITS,
   METACOMPS) : elles sont générées depuis data/releves/ par
   build_oracle.py. Une seule source de vérité.
   ==================================================================== */

/*__DATA:PLANS__*/
const PLANS = {
  R1:   {t:"R1 · Reroll 1-coût", p:"Achète chaque copie de ton carry à vue (9 copies = 3★). Slow roll niveau 6 à partir de 3-2, roll au-dessus de 50 or seulement.", e:"Erreur classique : monter niveau 7 avant le 3★ — tes odds de 1-coût s'effondrent."},
  R23:  {t:"R23 · Reroll 2-3 coûts", p:"Slow roll niveau 7 (Sprykin) ou 6-7 selon la cible. Garde 50+ or, roll l'excédent chaque round.", e:"Erreur classique : roll agressif à 30 or — tu perds les intérêts ET le 3★."},
  F8:   {t:"F8 · Fast 8", p:"Éco stricte jusqu'à 4-1/4-2, monte niveau 8, rolldown à ~50 or pour stabiliser des 4-coûts 2★. Le plan par défaut du top 4.", e:"Erreur classique : roll au niveau 7 « pour survivre » — si tu dois le faire, roll franchement, pas 20 or."},
  F9:   {t:"F9 · Fast 9", p:"Réservé au win-streak avec 40+ PV. Niveau 9 avant 5-1, cap avec les 5-coûts (Lux, Elder Dragon). Fast 9 raté = 7e-8e.", e:"Erreur classique : forcer le 9 à 30 PV — tu meurs pendant la montée."},
  VERT: {t:"VERT · Vertical", p:"Vise le palier HAUT d'un seul trait (Elderwood, Inferno, Riftbeast — tous S). L'emblème décide de la compo, pas toi.", e:"Erreur classique : splitter sur deux verticaux — tu n'actives le palier haut d'aucun."},
  PIVOT:{t:"PIVOT · Reconstruction", p:"Accepte le reset : revends ce qui ne sert plus, lis ton nouveau board, rejoins la ligne S la plus proche.", e:"Erreur classique : s'accrocher à l'ancienne compo après un Recombobulator."},
  FLEX: {t:"FLEX · Garde tes options", p:"Rien à forcer : éco, garde un board fort, décide au rolldown 4-1 selon items + hits + contestation.", e:"Erreur classique : se commit à 2-5 « parce qu'il faut bien choisir ». Non : 4-1."},
};

/*__DATA:COMPS__*/
const COMPS = [
 {n:"Eldritch", tier:"S", lvl:"Fast 8", code:"F8", traits:["Eldritch"], roster:["Malphite*","Soraka","Zyra*","Azir","Fiddlesticks","Rammus","Kobuko","Rek'Sai","Veigar"], open:"Rek'Sai / Veigar", note:"2 relevés concordants — la valeur sûre du patch."},
 {n:"Elderwood", tier:"S", lvl:"Fast 8", code:"F8", traits:["Elderwood"], roster:["Alune*","Gnar*","Aphelios*","Lillia","Alistar","LeBlanc","Ornn","Xayah"], open:"Ornn / Alistar / LeBlanc", note:"2 relevés concordants."},
 {n:"Inferno Cap", tier:"S", lvl:"Fast 9", code:"F9", traits:["Inferno","Lunar","Solar"], roster:["Kennen*","Lux*","Alune*","Amumu","Maokai","Taric","Soraka","Diana","Fiddlesticks"], open:"ligne Inferno early", note:"Difficile : exige streak + PV."},
 {n:"Riftbeasts", tier:"S", lvl:"Fast 8", code:"F8", traits:["Riftbeast"], roster:["Draven*","Elder Dragon*","Ancient Sentinel","Brambleback","Gnar","Krug","Murkwolf","Pebbles"], open:"3 Riftbeasts distincts avant 2-5", note:"Elder Dragon = 2 slots. MAJ 03/08 : ⬇⬇ COMPO VISÉE. Le Live Balance Lead annonce nerfer Riftbeast pour qu'elle ne domine plus la fin de partie. Draven BUFF (AD 40→48) ne compense pas."},
 {n:"Elderwood Cap", tier:"S", lvl:"Fast 9", code:"F9", traits:["Elderwood"], roster:["Ezreal*","Kennen*","Draven*","Maokai","Gnar","Ivern","Taric","Amumu","Alistar"], open:"Ornn / Alistar", note:"Version cappée, difficile."},
 {n:"Solar Inferno Reroll", tier:"S", lvl:"Slow roll niv 6", code:"R1", traits:["Solar","Inferno"], roster:["Kayle*","Varus*","Sejuani","Shen","Alune","Amumu","Aphelios","Diana","Leona"], open:"Kayle / Varus / Leona", note:"La ligne FACILE du patch. ⬇⬇ MAJ 03/08 : COMPO VISÉE. Double nerf (Solar 3 étoiles + Eclipse proc) et le Live Balance Lead la cite comme l'une des 2 lignes à faire redescendre."},
 {n:"Sprykin", tier:"S", lvl:"Slow roll niv 7", code:"R23", traits:["Sprykin"], roster:["Kog'Maw*","Tristana*","Rammus","Gnar","Lillia","Nidalee","Sivir","Teemo","Kobuko"], open:"Kobuko / Teemo", note:"⬆ Monté de A vers S au 2e relevé."},
 {n:"Blossom", tier:"S", lvl:"Fast 8", code:"F8", traits:["Blossom"], roster:["Ashe*","Zyra*","Sett","Gnar (TG)","Ahri","Sivir","Master Yi","Vi","Yorick"], open:"Wisps + ligne Blossom", note:"⬆ Monté de A vers S au 2e relevé."},
 {n:"Veigar Reroll", tier:"A", lvl:"Slow roll", code:"R1", traits:["Eldritch"], roster:["Veigar*","Rek'Sai","puis colle à Eldritch"], open:"Veigar early", note:"1 seul relevé. ⬇ MAJ 03/08 : Blackthorn nerf le multiplicateur 3 étoiles (2c 300→280 %, 3c 400→330 %) — coeur de cette ligne."},
 {n:"Spellweaver", tier:"A", lvl:"Fast 8-9", code:"F8", traits:["Spellweaver"], roster:["flex AP","cap niveau 8-9"], open:"Rod ×2 + Spellweavers", note:"Ligne flex."},
 {n:"Coven", tier:"B", lvl:"—", code:"FLEX", traits:["Coven"], roster:["Camille","Caitlyn","Elise"], open:"—", note:"La ligne la plus faible des deux relevés. Ne pas forcer."},
];

/*__DATA:TRAITS__*/
const TRAITS = {
 "Eldritch":   {note:"Vertical S. Ouverture Rek'Sai/Veigar, Malphite tank la fin."},
 "Elderwood":  {note:"Le trait le plus riche du relevé : 2 compos S (fast 8 standard, fast 9 cap). ⬆ MAJ 03/08 : BUFF (PV Stonebark 100→150, dégâts Protector 420/630→445/670)."},
 "Inferno":    {note:"Porté par Kennen. Version reroll facile (Solar) ou cap fast 9 difficile."},
 "Solar":      {note:"Moitié du duo Eclipse (Solar+Lunar → exécute l'ennemi le plus bas en PV). Diana fait la charnière. ⬇ MAJ 03/08 : NERF (scaling bonus 3 étoiles 2.5%→1.5%) — frappe les rerolls."},
 "Lunar":      {note:"L'autre moitié d'Eclipse. Alune en est la carry AP principale."},
 "Riftbeast":  {note:"Vertical S autour d'Elder Dragon (2 slots) et Draven."},
 "Sprykin":    {note:"Slow roll niveau 7, Kog'Maw/Tristana. Monté de A vers S entre deux relevés."},
 "Blossom":    {note:"Le trait qui casse les règles des Wisps : achats quasi toujours corrects. Monté A→S."},
 "Spellweaver":{note:"Classe AP flex — pas un vertical. Se joue en cap 8-9 si Rod ×2."},
 "Coven":      {note:"⚠ Ligne la plus faible des deux relevés. Ne pas forcer. ⬆ MAJ 03/08 : BUFF (essence par défaite en 7 : 70→100). Reste la ligne la plus faible."},
 "Eclipse":    {note:"Trait CACHÉ : s'active en combinant Solar + Lunar. Exécute périodiquement l'ennemi le plus bas en PV. ⬇ MAJ 03/08 : NERF (cadence de proc 3s→4s, soit −25% de fréquence)."},
};

/*__DATA:BIS__*/
const BIS = {
 "Kennen":{items:"Rabadon's · Hand of Justice · Guardbreaker", comp:"Rod ×2, Gant", tier:"S"},
 "Alune":{items:"Inferno Cap → Void · Shojin · Morello — Elderwood → Nashor's · Jeweled · Void", comp:"Rod, Tear, Gant, Bow selon version", tier:"S"},
 "Aphelios":{items:"Infinity Edge · Guinsoo's · Giant Slayer", comp:"B.F., Bow ×2, Gant", tier:"S"},
 "Ezreal":{items:"Infinity Edge · Deathblade · Striker's Flail", comp:"B.F. ×2, Gant, Bow", tier:"A"},
 "Draven":{items:"Guinsoo's · Guardbreaker · Infinity Edge", comp:"Bow ×2, B.F., Gant", tier:"S"},
 "Ashe":{items:"Giant Slayer · Guinsoo's · Kraken's Fury", comp:"Bow ×2, B.F. ×2", tier:"A"},
 "Zyra":{items:"Shojin · Void Staff · Morello", comp:"Tear, Rod ×2, Ceinture", tier:"S"},
 "Kog'Maw":{items:"Jeweled Gauntlet · Morello · Nashor's", comp:"Rod ×2, Gant, Bow", tier:"A"},
 "Tristana":{items:"Infinity Edge · Deathblade · Shojin", comp:"B.F. ×2, Gant, Tear", tier:"A"},
 "Lux":{items:"Nashor's ×2 · Jeweled Gauntlet", comp:"Rod ×2, Bow ×2, Gant", tier:"A"},
 "Soraka":{items:"Jeweled Gauntlet · Nashor's ×2", comp:"Rod, Gant, Bow ×2", tier:"A"},
 "Elder Dragon":{items:"Titan's · Sterak's · Bloodthirster", comp:"B.F. ×2, Ceinture, Bow", tier:"S"},
 "Gnar":{items:"BT · Sterak's · Titan's (carry) ou Thief's Gloves", comp:"B.F. ×2, Ceinture, Négatron — ou Gant ×2", tier:"S"},
 "Malphite":{items:"Gargoyle ×2 · Warmog's", comp:"Cotte ×2, Négatron ×2, Ceinture ×2", tier:"S"},
 "Rammus":{items:"Gargoyle ×2 · Warmog's", comp:"Cotte ×2, Négatron ×2, Ceinture ×2", tier:"A"},
 "Amumu":{items:"Warmog's · Bramble · Dragon's Claw", comp:"Ceinture ×2, Cotte ×2, Négatron ×2", tier:"A"},
 "Sett":{items:"Warmog's · Gargoyle · Evenshroud", comp:"Ceinture ×2, Cotte, Négatron ×2", tier:"A"},
 "Lillia":{items:"Evenshroud · Sunfire · Warmog's", comp:"Négatron, Ceinture ×3, Cotte", tier:"A"},
 "Ancient Sentinel":{items:"Warmog's · Evenshroud · Bramble", comp:"Ceinture ×2, Négatron, Cotte ×2", tier:"B"},
 "Kayle":{items:"vitesse d'attaque + crit (Guinsoo, Rageblade core)", comp:"Bow ×2, Gant", tier:"A"},
 "Varus":{items:"AD crit (IE core)", comp:"B.F., Gant, Bow", tier:"A"},
 "Veigar":{items:"AP burst (Rabadon, Jeweled)", comp:"Rod ×2, Gant", tier:"A"},
 "Diana":{items:"charnière Solar↔Lunar — items tank légers", comp:"—", tier:"A"},
};

/*__DATA:STATS__*/
const STATS = {
 "Akali":{c:1,pv:650,ad:40,as_:0.75,ar:35,mana:"0/30",sur:50,auto:54,cad:100},
 "Camille":{c:1,pv:700,ad:40,as_:0.75,ar:40,mana:"0/25",sur:56,auto:54,cad:100},
 "Cinderling":{c:1,pv:500,ad:40,as_:0.7,ar:25,mana:"0/50",sur:36,auto:50,cad:57},
 "Karma":{c:1,pv:500,ad:25,as_:0.7,ar:25,mana:"0/40",sur:36,auto:31,cad:72},
 "Kobuko":{c:1,pv:700,ad:55,as_:0.65,ar:40,mana:"30/90",sur:56,auto:64,cad:44},
 "Leona":{c:1,pv:700,ad:50,as_:0.65,ar:40,mana:"40/100",sur:56,auto:58,cad:44},
 "Ornn":{c:1,pv:700,ad:40,as_:0.6,ar:40,mana:"40/100",sur:56,auto:43,cad:41},
 "Pebbles":{c:1,pv:500,ad:30,as_:0.8,ar:25,mana:"25/65",sur:36,auto:43,cad:82},
 "Rakan":{c:1,pv:700,ad:45,as_:0.6,ar:35,mana:"20/90",sur:54,auto:48,cad:35},
 "Rek'Sai":{c:1,pv:700,ad:50,as_:0.55,ar:40,mana:"40/100",sur:56,auto:49,cad:38},
 "Varus":{c:1,pv:500,ad:40,as_:0.7,ar:25,mana:"30/120",sur:36,auto:50,cad:32},
 "Veigar":{c:1,pv:500,ad:25,as_:0.7,ar:25,mana:"0/30",sur:36,auto:31,cad:96},
 "Xayah":{c:1,pv:450,ad:45,as_:0.7,ar:25,mana:"0/50",sur:32,auto:56,cad:57},
 "Yorick":{c:1,pv:650,ad:50,as_:0.6,ar:35,mana:"50/110",sur:50,auto:54,cad:41},
 "Alistar":{c:2,pv:950,ad:50,as_:0.6,ar:45,mana:"30/90",sur:70,auto:50,cad:33},
 "Caitlyn":{c:2,pv:550,ad:50,as_:0.7,ar:30,mana:"0/3",sur:36,auto:58,cad:100},
 "Elise":{c:2,pv:900,ad:30,as_:0.65,ar:45,mana:"20/70",sur:67,auto:32,cad:43},
 "Gromp":{c:2,pv:550,ad:30,as_:0.7,ar:30,mana:"0/45",sur:36,auto:35,cad:51},
 "Kayle":{c:2,pv:550,ad:10,as_:0.75,ar:30,mana:"—",sur:36,auto:12,cad:null},
 "LeBlanc":{c:2,pv:550,ad:30,as_:0.7,ar:30,mana:"0/40",sur:36,auto:35,cad:57},
 "Murk Wolf":{c:2,pv:700,ad:50,as_:0.75,ar:40,mana:"0/40",sur:50,auto:62,cad:61},
 "Scuttle Crab":{c:2,pv:950,ad:50,as_:0.65,ar:45,mana:"40/100",sur:70,auto:54,cad:35},
 "Sejuani":{c:2,pv:900,ad:50,as_:0.6,ar:45,mana:"40/100",sur:67,auto:50,cad:33},
 "Shen":{c:2,pv:900,ad:50,as_:0.65,ar:45,mana:"30/90",sur:67,auto:54,cad:35},
 "Teemo":{c:2,pv:550,ad:35,as_:0.75,ar:30,mana:"0/50",sur:36,auto:44,cad:49},
 "Warwick":{c:2,pv:750,ad:40,as_:0.75,ar:45,mana:"0/40",sur:55,auto:50,cad:61},
 "Yunara":{c:2,pv:550,ad:42,as_:0.75,ar:30,mana:"0/35",sur:36,auto:52,cad:70},
 "Azir":{c:3,pv:650,ad:30,as_:0.75,ar:35,mana:"0/35",sur:33,auto:35,cad:55},
 "Cassiopeia":{c:3,pv:650,ad:30,as_:0.75,ar:35,mana:"0/30",sur:33,auto:35,cad:65},
 "Diana":{c:3,pv:850,ad:30,as_:0.8,ar:50,mana:"0/40",sur:48,auto:37,cad:52},
 "Fiddlesticks":{c:3,pv:1000,ad:50,as_:0.65,ar:55,mana:"30/90",sur:58,auto:50,cad:28},
 "Hecarim":{c:3,pv:1100,ad:50,as_:0.65,ar:50,mana:"30/110",sur:62,auto:50,cad:21},
 "Kha'Zix":{c:3,pv:850,ad:30,as_:0.8,ar:55,mana:"0/25",sur:49,auto:37,cad:83},
 "Kog'Maw":{c:3,pv:650,ad:40,as_:0.8,ar:35,mana:"15/55",sur:33,auto:49,cad:52},
 "Krug":{c:3,pv:1100,ad:55,as_:0.6,ar:40,mana:"80/135",sur:58,auto:51,cad:28},
 "Master Yi":{c:3,pv:850,ad:70,as_:0.8,ar:60,mana:"0/3",sur:51,auto:86,cad:100},
 "Rammus":{c:3,pv:1100,ad:50,as_:0.6,ar:50,mana:"30/80",sur:62,auto:46,cad:31},
 "Raptor":{c:3,pv:650,ad:60,as_:0.75,ar:35,mana:"30/70",sur:33,auto:69,cad:48},
 "Rengar":{c:3,pv:900,ad:60,as_:0.8,ar:55,mana:"10/50",sur:52,auto:74,cad:52},
 "Tristana":{c:3,pv:650,ad:55,as_:0.75,ar:35,mana:"0/60",sur:33,auto:63,cad:32},
 "Vi":{c:3,pv:1100,ad:45,as_:0.75,ar:50,mana:"0/60",sur:62,auto:52,cad:32},
 "Ahri":{c:4,pv:850,ad:40,as_:0.8,ar:40,mana:"20/100",sur:40,auto:44,cad:38},
 "Amumu":{c:4,pv:1300,ad:70,as_:0.7,ar:60,mana:"30/140",sur:71,auto:68,cad:24},
 "Ancient Sentinel":{c:4,pv:1300,ad:75,as_:0.6,ar:60,mana:"60/150",sur:71,auto:62,cad:25},
 "Aphelios":{c:4,pv:850,ad:60,as_:0.8,ar:40,mana:"20/70",sur:40,auto:66,cad:61},
 "Brambleback":{c:4,pv:1100,ad:110,as_:0.55,ar:65,mana:"0/40",sur:62,auto:84,cad:52},
 "Ezreal":{c:4,pv:850,ad:45,as_:0.75,ar:40,mana:"0/30",sur:40,auto:47,cad:95},
 "Lillia":{c:4,pv:1300,ad:40,as_:0.65,ar:60,mana:"50/150",sur:71,auto:36,cad:25},
 "Malphite":{c:4,pv:1300,ad:70,as_:0.55,ar:70,mana:"30/80",sur:75,auto:53,cad:42},
 "Morgana":{c:4,pv:1100,ad:45,as_:0.75,ar:60,mana:"0/60",sur:60,auto:47,cad:48},
 "Nidalee":{c:4,pv:850,ad:35,as_:0.8,ar:30,mana:"0/40",sur:37,auto:39,cad:76},
 "Sett":{c:4,pv:1200,ad:80,as_:0.65,ar:60,mana:"60/135",sur:65,auto:72,cad:33},
 "Sivir":{c:4,pv:850,ad:50,as_:0.8,ar:40,mana:"0/40",sur:40,auto:55,cad:76},
 "Soraka":{c:4,pv:850,ad:30,as_:0.75,ar:40,mana:"0/30",sur:40,auto:31,cad:95},
 "Zyra":{c:4,pv:850,ad:40,as_:0.75,ar:40,mana:"0/45",sur:40,auto:42,cad:64},
 "Alune":{c:5,pv:900,ad:40,as_:0.8,ar:45,mana:"0/35",sur:44,auto:34,cad:87},
 "Ashe":{c:5,pv:900,ad:75,as_:0.8,ar:45,mana:"30/90",sur:44,auto:63,cad:51},
 "Draven":{c:5,pv:900,ad:48,as_:0.8,ar:45,mana:"0/120",sur:44,auto:40,cad:25},
 "Elder Dragon":{c:5,pv:1800,ad:100,as_:0.5,ar:70,mana:"20/60",sur:100,auto:53,cad:48},
 "Gnar":{c:5,pv:900,ad:100,as_:0.9,ar:55,mana:"0/70",sur:47,auto:95,cad:49},
 "Ivern":{c:5,pv:1000,ad:60,as_:0.85,ar:55,mana:"50/80",sur:53,auto:54,cad:100},
 "Kennen":{c:5,pv:1200,ad:50,as_:0.9,ar:60,mana:"0/40",sur:65,auto:47,cad:86},
 "Lux":{c:5,pv:900,ad:40,as_:0.8,ar:45,mana:"20/70",sur:44,auto:34,cad:61},
 "Maokai":{c:5,pv:1100,ad:80,as_:0.65,ar:60,mana:"40/100",sur:60,auto:55,cad:41},
 "Taric":{c:5,pv:1300,ad:55,as_:0.75,ar:65,mana:"0/65",sur:73,auto:43,cad:44},
};

/*__DATA:VERDICT__*/
const VERDICT = {
 "Master Yi":"Auto-attaque à 86 contre 50 de médiane sur son palier : surchargé pour un 3-coûts. Candidat reroll — et candidat nerf au prochain patch.",
 "Gnar":"La plus grosse auto-attaque du set : 100 d'AD à 0.9 de vitesse. C'est un vrai carry, pas un porteur de trait.",
 "Brambleback":"110 d'AD, le plus haut du palier — mais 0.55 de vitesse, le plus lent. Sans vitesse d'attaque dessus, il ne tape pas.",
 "Draven":"0/120 de mana, la cadence la plus lente du set. Sans Shojin ou Blue Buff, il ne lance jamais son sort.",
 "Xayah":"450 PV, le chiffre le plus bas du jeu entier, avec une auto-attaque au-dessus de la médiane. Le positionnement ne pardonne rien.",
 "Kennen":"Lance vite ET encaisse : survie 65, très au-dessus des autres lanceurs 5-coûts. C'est pour ça qu'il cap. ⚠ 03/08 : le Live Balance Lead le dit TROP FORT mais non nerfé — un correctif sur les brûlures Inferno est à l'étude. Fort maintenant, risqué à moyen terme.",
 "Elder Dragon":"1800 PV et 70 d'armure : survie plafonnée. Mais 0.5 de vitesse d'attaque, le plus lent du jeu — il tient, il ne carry pas seul.",
 "Ivern":"Cadence 99 : le sort le plus rapide de tous les 5-coûts. Il lance avant que l'adversaire n'ait démarré.",
 "Ahri":"20/100 de mana à 0.8 de vitesse : le lanceur 4-coûts le plus lent à démarrer. Objet de mana quasi obligatoire.",
 "Kayle":"10 d'AD et aucune barre de mana : ses stats brutes ne veulent rien dire. Tout passe par le trait et les objets.",
 "Caitlyn":"Sort à 3 de mana — c'est un passif, pas un sort. Ne lis pas sa cadence comme une force.",
 "Ezreal":"0/30 de mana : il lance presque immédiatement. Cadence 95, la meilleure de son palier.",
 "Soraka":"0/30 de mana donc cadence 95, mais 30 d'AD : elle ne tape pas. Tout est dans le sort, rien dans l'auto.",
 "Aphelios":"60 d'AD à 0.8 de vitesse : le meilleur profil de carry AD du palier 4 après Brambleback, et lui n'a pas besoin de vitesse d'attaque pour exister.",
 "Malphite":"Survie 75, la plus haute du palier 4. Mais 0.55 de vitesse : c'est un mur, pas une menace.",
 "Amumu":"1300 PV et 70 d'AD : un tank qui tape. 30/140 de mana par contre, il lance tard.",
 "Sett":"80 d'AD sur un tank, mais 60/135 de mana : le sort arrive tard dans le combat.",
 "Ancient Sentinel":"60/150 de mana, cadence 25 : parmi les plus lents du jeu à lancer.",
 "Lillia":"50/150 de mana, cadence 25. Elle encaisse longtemps avant de faire quoi que ce soit.",
 "Krug":"80/135 de mana, cadence 28 : le plus lent des 3-coûts à lancer.",
 "Rek'Sai":"0.55 de vitesse d'attaque, le plus lent des 1-coûts.",
 "Veigar":"0/30 de mana : il lance très vite pour un 1-coût. C'est ce qui fait marcher son reroll.",
 "Tristana":"0/60 de mana à 0.75 de vitesse : cadence 32, lente pour un carry. Elle a besoin d'aide au mana.",
 "Alune":"0/35 de mana, cadence 80 : elle enchaîne les sorts vite.",
 "Ashe":"75 d'AD à 0.8 de vitesse, le meilleur socle d'auto-attaque des 5-coûts après Gnar.",
 "Taric":"1300 PV et 65 d'armure : le tank pur du palier 5.",
 "Sivir":"0/40 de mana à 0.8 de vitesse : cadence 76, elle relance vite.",
 "Rengar":"74 en auto-attaque contre 50 de médiane : très au-dessus de son palier.",
 "Kha'Zix":"Cadence 83 sur un 3-coûts, mais seulement 37 en auto : tout passe par le sort.",
 "Morgana":"1100 PV et 60 d'armure sur un lanceur : elle survit à un plongeon.",
};

/*__DATA:AUG__*/
const AUG = [
 ["Branching Out / +","S","🔒 COMMIT FORT","VERT","Gagne un emblème aléatoire (+ Reforger)","Le palier haut du trait de l'emblème","L'augment le plus directif du jeu. Suis-le sans discuter."],
 ["Flame On","S","🔒 COMMIT FORT","R1","Le champion Inferno le plus performant est On Fire. Gagne Varus + Akali","Varus 3★ prioritaire, Shen en tank, Kennen en cap","Inferno est S-tier au 31/07. Excellent augment actuellement."],
 ["Forge a Friend","S","🔒 COMMIT FORT","R1","Le prochain 1-coût acheté est 3★. Gagne 5 or","Choisis LE bon 1-coût : Kayle, Varus, Veigar, Leona","3★ gratuit = énorme tempo. Prends un carry, pas un tank."],
 ["Weight The Worth","A","🔒 COMMIT FORT","R1","Quand tu 3★ un champion, gagne une copie chaque round. + Lesser Duplicator","Ton premier 3★ le plus tôt possible","Snowball massif si tu 3★ tôt. Inutile en fast 8."],
 ["Missed Connections","S","🔒 COMMIT FORT","R1","Gagne une copie de chaque 1-coût","Identifie tes 2 meilleurs 1-coûts et roll dessus","Te met à mi-chemin de plusieurs 3★. Très fort."],
 ["Recombobulator","A","🔒 COMMIT FORT","PIVOT","Tes champions se transforment en unités 1 tier au-dessus. + 2 Removers","Rien — tu subis le résultat, adapte-toi après","Reset ta compo. Accepte le pivot, ne force pas l'ancienne."],
 ["Dummify","A","🔒 COMMIT FORT","PIVOT","Perds tout ton board → Training Dummy. Gagne un 2-coût 2★ non-tank","Le Dummy tank tout : construis un board full dégâts","Très fort si pris tôt. Dangereux en Stage 3+."],
 ["Verticality I","A","🔒 COMMIT FORT","VERT","Stats (AD/AP/Armure/RM) par allié partageant un trait","Le palier haut d'UN trait vertical","Pousse vers Elderwood/Inferno/Riftbeast (tous S)."],
 ["Residual Magic (I/+/++)","A","🔓 COMMIT MOU","VERT","PV d'équipe, augmenté à chaque achat de Wisp","Achète des Wisps régulièrement, vise Blossom","Blossom est monté S au 2e relevé — meilleur qu'hier."],
 ["Wisp Rebate / +","A","🔓 COMMIT MOU","VERT","Chaque achat de Wisp rapporte de l'or","Le palier Blossom qui paie aussi l'or (double dip)","Résout le piège des intérêts. Achète les Wisps librement."],
 ["Carve a Path","A","🔓 COMMIT MOU","F8","Gagne un B.F. Sword, puis 2 de plus après 65 000 dégâts physiques","Un carry AD qui tient la durée : Aphelios, Draven, Ashe","3 B.F. = tu es AD. Mais choisis le carry selon le tier."],
 ["Continuous Conjuration","A","🔓 COMMIT MOU","F8","Gagne un Rod, puis 2 de plus après 42 000 dégâts magiques","Un carry AP : Kennen, Alune, Zyra, Kog'Maw","3 Rods = tu es AP. Kennen/Alune prioritaires vu le tier."],
 ["Backup Bows","B","🔓 COMMIT MOU","F8","Gagne un Bow, puis 2 de plus après 1 000 attaques","Une ligne vitesse d'attaque : Kayle, Aphelios, Draven","Les attaques comptent vite avec un carry AS. Bon early."],
 ["Flowing Tears","B","🔓 COMMIT MOU","F8","Gagne un Tear, puis 2 de plus après 6 500 mana dépensé","Un carry à gros sort (Alune, Zyra)","Invoker donne déjà du mana → surplus possible."],
 ["Extra Buckles","B","🔓 COMMIT MOU","F8","Gagne un Giant's Belt, puis 2 de plus après 75 000 dégâts subis","Une frontline qui encaisse : Malphite, Rammus, Sett","Bon en Eldritch (Malphite S). Ne carry pas seul."],
 ["Late Game Specialist","A","💰 ÉCO-FLEX","F9","Niveau 9 → gagne 30 or","Atteindre le niveau 9 avant 5-1","Confirme le fast 9. Garde tes PV pour y arriver."],
 ["Future Focused","B","💰 ÉCO-FLEX","F9","Ton Tactician perd des PV, puis gagne des 4-coûts et de l'or","Ne pas mourir avant le payout","Pari sur les PV. Risqué si tu vises le top 4 en sécurité."],
 ["One, Two, Five!","B","🌀 FLEX","F9","1 composant, 2 or, 1 champion 5-coût aléatoire","Regarde le 5-coût : s'il est S-tier, c'est un signal","Elder Dragon ou Lux = signal fort. Sinon, ignore."],
 ["Slice of Life","A","💰 ÉCO-FLEX","F9","2× par stage, un champion dont le coût monte","Rien de précis — accumule et lis ce qui sort","Excellent pour rester flex. Très bon pour le top 4."],
 ["Champ Delivery (/+/++)","B","💰 ÉCO-FLEX","F8","Gagne des champions d'un coût donné, puis d'autres après X rounds","Les unités offertes orientent ta ligne","Regarde les traits des unités reçues avant de décider."],
 ["Caretaker's Ally","A","🔓 COMMIT MOU","R23","Un 2-coût aléatoire, puis le même à chaque montée de niveau","Ce 2-coût sera 3★ facilement → construis autour","Si c'est Alistar/LeBlanc (Elderwood S), très fort."],
 ["Cognitive Tax / +","S","💰 ÉCO-FLEX","FLEX","8 or et 1 XP (ou 12 or et 3 XP)","Rien","Or pur. Te laisse toutes les portes ouvertes. Idéal top 4."],
 ["Feeling Lucky","A","💰 ÉCO-FLEX","FLEX","12 or, puis pile ou face pour 4 de plus","Rien","Or pur, zéro contrainte."],
 ["Capital Gains I","B","💰 ÉCO-FLEX","F9","Stocke de l'or égal à une part de tes intérêts, versé plus tard","Ne pas casser ta banque","⚠ Conflit direct avec l'achat de Wisps. Choisis."],
 ["Kingslayer","B","💰 ÉCO-FLEX","FLEX","Or après victoire, plus si l'adversaire avait plus de PV","Rester fort tôt pour gagner les combats","Récompense le board fort. Bon avec un starter propre."],
 ["Quick Streaks","B","💰 ÉCO-FLEX","FLEX","Progression de streak doublée (gain ET perte)","Choisis ton camp tôt : win-streak OU loss-streak franc","Fort avec Coven — mais Coven est B. Prudence."],
 ["Called Shot","B","💰 ÉCO-FLEX","FLEX","Ton win-streak passe à 4. Gagne 4 or","Enchaîner pour garder le streak","Tempo immédiat. Il faut un board déjà correct."],
 ["Rolling For Days I","B","🔓 COMMIT MOU","R23","10 rerolls gratuits","Utilise-les au bon stage, pas immédiatement","Rerolls = tempo. Garde-les pour un palier précis."],
 ["Patience is a Virtue","B","🔓 COMMIT MOU","R1","Rerolls maintenant, + 1 gratuit par round sans achat","Discipline : ne pas acheter pour cumuler","Demande de la rigueur. Bon en slow roll."],
 ["Loaded Dice","C","💰 ÉCO-FLEX","FLEX","Tes dés font toujours 6, tes pièces toujours face","Rien","Synergise avec les Wisps Risky/Coin Flip. Petit bonus."],
 ["Component Buffet","S","🌀 FLEX","FLEX","Tes composants deviennent des anvils. + 1 composant","Rien — tu choisis tes composants","Flexibilité d'items maximale. Excellent pour le top 4."],
 ["Item Grab Bag","A","🌀 FLEX","FLEX","1 objet complet aléatoire","L'objet reçu oriente AD/AP","Regarde l'objet, il tranche ta direction d'items."],
 ["Small Grab Bag","B","🌀 FLEX","FLEX","2 composants aléatoires","Croise avec les patterns : Rod+Gant = AP, B.F.+Gant = AD","Signal d'items faible mais réel."],
 ["Iron Assets","B","🌀 FLEX","FLEX","1 component anvil et 3 or","Rien","Tu choisis le composant → aucune contrainte."],
 ["Stand United","B","🌀 FLEX","FLEX","AD et AP par trait non-unique actif","Multiplier les traits, PAS en empiler un seul","⚠ Piège anti-vertical : pousse à l'inverse d'Elderwood/Inferno."],
 ["Pandora's Items I","C","🌀 FLEX","FLEX","Les objets de ton banc sont randomisés chaque round. + 1 composant","Ne pas laisser d'objets importants au banc","Piège : équipe tes objets vite."],
 ["Corrosion","C","🌀 FLEX","FLEX","Les ennemis des 2 premières lignes perdent armure/RM","Rien","Combat pur. N'oriente aucune compo."],
 ["Partial Ascension","B","🌀 FLEX","FLEX","Après 12s de combat, +20% d'amplification","Un board qui tient 12s → frontline solide","Récompense les combats longs. Bon avec des tanks."],
 ["Glass Cannon I","B","🌀 FLEX","FLEX","Les alliés du fond commencent à 80% PV mais +16% amplif.","Protéger ta backline","Bon avec un carry unique bien positionné."],
 ["Effets de combat divers (Electrocharge, Healing Orbs, Group Hug, Makeshift Armor, Boxing Lessons, Twin Guardians, Find Your Center, Focused Fire, The Tower, Celestial Blessing)","C","🌀 FLEX","FLEX","Effets de combat / défensifs variés","Rien","Ne décident rien. Prends-les si les autres options te forcent la main."],
];

/*__DATA:TAGS__*/
const TAGS = {
 "Eldritch": [
  "ap",
  "fast8",
  "fiable",
  "fort",
  "quatrecost",
  "tank"
 ],
 "Elderwood": [
  "ad",
  "ap",
  "fast8",
  "fort",
  "hybride",
  "peeba",
  "quatrecost"
 ],
 "Inferno Cap": [
  "ap",
  "cap",
  "difficile",
  "fast9",
  "fort",
  "peeba"
 ],
 "Riftbeasts": [
  "ad",
  "fast8",
  "fort",
  "peeba"
 ],
 "Elderwood Cap": [
  "ad",
  "ap",
  "cap",
  "difficile",
  "fast9",
  "fort",
  "hybride",
  "peeba",
  "quatrecost"
 ],
 "Solar Inferno Reroll": [
  "ad",
  "ap",
  "facile",
  "fort",
  "hybride",
  "ouverture",
  "reroll"
 ],
 "Sprykin": [
  "ad",
  "ap",
  "fort",
  "hybride",
  "reroll"
 ],
 "Blossom": [
  "ad",
  "ap",
  "fast8",
  "fort",
  "hybride",
  "quatrecost",
  "wisps"
 ],
 "Veigar Reroll": [
  "ap",
  "ouverture",
  "reroll"
 ],
 "Spellweaver": [
  "ap",
  "fast8",
  "flex"
 ],
 "Coven": [
  "faible",
  "flex"
 ]
};

/*__DATA:LEX__*/
const LEX = {
 "ouverture": [
  "demarrer",
  "demarrage",
  "ouverture",
  "debut",
  "early",
  "opener",
  "commencer",
  "start",
  "lancer"
 ],
 "facile": [
  "facile",
  "simple",
  "safe",
  "tranquille",
  "easy",
  "accessible",
  "confort",
  "confortable"
 ],
 "difficile": [
  "difficile",
  "dur",
  "hard",
  "exigeant",
  "risque",
  "technique"
 ],
 "reroll": [
  "reroll",
  "rerol",
  "roll",
  "slowroll",
  "3etoiles",
  "troisetoiles"
 ],
 "fast8": [
  "fast8",
  "f8",
  "8",
  "huit"
 ],
 "fast9": [
  "fast9",
  "f9",
  "9",
  "neuf"
 ],
 "cap": [
  "cap",
  "capper",
  "cappee",
  "plafond"
 ],
 "ad": [
  "ad",
  "physique",
  "attaque",
  "autoattaque",
  "adcarry"
 ],
 "ap": [
  "ap",
  "magique",
  "magie",
  "sort",
  "sorts",
  "apcarry"
 ],
 "tank": [
  "tank",
  "tanks",
  "frontline",
  "devant",
  "resistant"
 ],
 "flex": [
  "flex",
  "flexible",
  "adaptable",
  "polyvalent",
  "souple"
 ],
 "peeba": [
  "peeba",
  "peba",
  "peebaa",
  "pebaa",
  "pibas",
  "piba",
  "legendaire",
  "legendaires",
  "legendary",
  "5cost",
  "cinqcost",
  "findepartie",
  "boarddefin",
  "plateaudefin"
 ],
 "quatrecost": [
  "4cost",
  "quatrecost",
  "quatre"
 ],
 "hybride": [
  "hybride",
  "mixte",
  "adap",
  "apad"
 ],
 "fort": [
  "fort",
  "forte",
  "meilleur",
  "meilleure",
  "top",
  "best",
  "puissant"
 ],
 "faible": [
  "faible",
  "mauvais",
  "eviter"
 ],
 "fiable": [
  "fiable",
  "stable",
  "constant",
  "consistant",
  "regulier",
  "sur",
  "sure"
 ],
 "wisps": [
  "wisp",
  "wisps"
 ]
};

/*__DATA:ROLE__*/
const ROLE = {
 "Malphite":"tank","Rammus":"tank","Kobuko":"tank","Amumu":"tank","Maokai":"tank",
 "Alistar":"tank","Ornn":"tank","Lillia":"tank","Sejuani":"tank","Shen":"tank",
 "Leona":"tank","Sett":"tank","Yorick":"tank","Pebbles":"tank","Brambleback":"tank",
 "Ancient Sentinel":"tank","Elder Dragon":"tank",
 "Rek'Sai":"bruiser","Gnar":"bruiser","Diana":"bruiser","Krug":"bruiser",
 "Murkwolf":"bruiser","Master Yi":"bruiser","Vi":"bruiser","Camille":"bruiser",
 "Soraka":"support","Fiddlesticks":"support","Taric":"support","Ivern":"support",
 "Nidalee":"support","Teemo":"support","Elise":"support",
 "Zyra":"carry","Azir":"carry","Veigar":"carry","Alune":"carry","Aphelios":"carry",
 "LeBlanc":"carry","Xayah":"carry","Kennen":"carry","Lux":"carry","Draven":"carry",
 "Ezreal":"carry","Kayle":"carry","Varus":"carry","Kog'Maw":"carry","Tristana":"carry",
 "Sivir":"carry","Ashe":"carry","Ahri":"carry","Caitlyn":"carry",
};
