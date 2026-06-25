# Frost Days — script de présentation orale

**Binôme :** Alexis & Louey · **Durée cible :** 10–12 min + questions
**Support :** le dashboard Streamlit en direct (`streamlit run app.py`) + ce fil conducteur.

> Légende : 🅰 = Alexis parle · 🅛 = Louey parle · *(action)* = ce qu'on fait à l'écran.

---

## 0. Avant de commencer (checklist — 2 min avant le passage)

- [ ] App lancée : `streamlit run app.py`, onglet navigateur sur `localhost:8501`.
- [ ] Données présentes en local (`data/meteo/`) → **aucune dépendance internet** pendant la démo.
- [ ] Paramètres de départ : **Dijon · Côte-d'Or (21) · 2014-01-01 → 2023-12-31**.
- [ ] Un 2ᵉ scénario prêt en tête pour la synthèse : **Dijon · 1970 → 2024**.
- [ ] Zoom navigateur à ~110 % pour la lisibilité au vidéoprojecteur.

---

## 1. Accroche & problématique — 🅛 (≈ 1 min)

> 🅛 « En France, on dit que les hivers sont de moins en moins rudes. Mais *de moins en moins*,
> ça veut dire quoi, chiffré ? Nous, on a pris une mesure très simple et très concrète : **le
> jour de gel**. »

*(montrer l'écran d'accueil — masthead « FROST DAYS » + définition)*

> 🅛 « Notre problématique : **combien de jours de gel une commune française a-t-elle connus sur
> une période donnée ?** Avec une définition stricte : un jour de gel, c'est un jour où la
> température minimale sous abri — la variable `TN` — est descendue à **0 °C ou moins**. »

**Idée à faire passer :** une question simple, une définition non ambiguë. Tout le projet
tient sur cette ligne des **0 °C**.

## 2. Les données — 🅐 (≈ 1 min 30)

> 🅐 « Une seule source, officielle : **data.gouv.fr**, les données climatologiques quotidiennes
> de **Météo-France**. Deux fichiers : le référentiel des communes — pour la position GPS — et,
> par département, un fichier d'environ 40 colonnes de relevés quotidiens depuis 1950. »

> 🅐 « On n'en garde que **6** : l'identifiant et le nom de la station, sa latitude/longitude,
> son altitude, la date, et `TN`. Pourquoi `TN` et pas la moyenne `TM` ou le maximum `TX` ?
> Parce que le gel, c'est le **minimum** de la journée : une nuit courte mais glaciale gèle, même
> si la moyenne reste positive. »

*(facultatif : montrer le notebook `02_exploration.ipynb`, §1)*

## 3. Le pipeline & les choix techniques — 🅛 puis 🅐 (≈ 2 min)

> 🅛 « De la commune au résultat, il y a 5 étapes : on récupère le GPS de la commune, on charge
> le fichier du département — **par paquets de 500 000 lignes** pour ne jamais saturer la RAM —,
> on cherche la station la plus proche, puis on compte les `TN ≤ 0`. »

**Deux décisions qu'on assume (les montrer comme des choix, pas des détails) :**

> 🅐 « **Un :** la distance commune ↔ station, on la calcule en **Haversine**, la distance à vol
> d'oiseau sur la sphère. À la latitude de la France, 1° de longitude ≈ 70 km mais 1° de latitude
> ≈ 111 km : une distance naïve déformerait l'est-ouest. »

> 🅛 « **Deux :** la station la plus proche n'est **pas toujours** la bonne. Beaucoup de stations
> sont des pluviomètres **sans thermomètre** : 100 % de `TN` manquantes. Sur la Côte-d'Or, on a
> mesuré que **38 stations sur 58** sont dans ce cas. Donc on prend les 5 plus proches et on garde
> la première qui a **moins de 35 % de trous**. Pour Dijon, la station à 2 km est éliminée, on
> retombe sur *Dijon-Toison* à 4 km. Sans cette règle, on calculerait sur une station fantôme. »

## 4. Démo — la commune — 🅐 (≈ 1 min 30)

*(cliquer **Calculer** avec Dijon / 2014–2023)*

> 🅐 « Réponse directe à la problématique pour Dijon, sur 10 ans : **439 jours de gel**, soit
> **≈ 49 par an**. La station retenue, sa distance, et surtout la **couverture** des données
> sont affichées en haut — on est transparents sur la qualité. »

*(onglet **La commune** — barres par année, puis courbe jour-par-jour)*

> 🅐 « Le gel se concentre de **novembre à mars**, quasi rien de mai à octobre. Et certains jours
> sont des points noirs : le **24 janvier** a gelé **7 années sur 8**. Pour un jardinier, cette
> courbe, c'est un calendrier de risque. »

## 5. Démo — l'influence de la température — 🅛 (≈ 1 min 30)

*(onglet **Température & gel**)*

> 🅛 « Première influence : **le temps qui passe**. On trace la `TN` moyenne d'hiver, année après
> année. La ligne des **0 °C** sert de repère. On ajuste une tendance : ici **+0,7 °C par
> décennie** sur la fenêtre. Et quand on croise température et gel, la relation est nette :
> **un hiver plus doux = nettement moins de jours de gel**. »

> 🅛 « Honnêteté scientifique : sur **10 ans**, ce signal reste fragile, la variabilité naturelle
> domine. Pour parler vraiment de climat, il faut **30 ans** — c'est la norme de l'OMM, et le
> dashboard le rappelle. »

## 6. Démo — l'influence de l'altitude — 🅐 (≈ 1 min)

*(onglet **Altitude & gel**)*

> 🅐 « Deuxième influence : **l'espace**. Chaque point est une station du département ; en abscisse
> son altitude, en ordonnée ses jours de gel par an. La station de Dijon est en orange. La pente
> est positive : **plus on monte, plus ça gèle** — ici de l'ordre de quelques jours pour +100 m.
> Sur un département de plaine c'est modéré ; sur un département alpin, l'effet exploserait. »

## 7. La synthèse — temps **contre** espace — 🅛 (≈ 1 min 30) — *le moment fort*

*(onglet **Synthèse** ; puis changer la plage en **1970 → 2024** et re-Calculer)*

> 🅛 « Notre apport : ramener les **deux forces dans la même unité** — des jours de gel par an —
> pour les comparer. Sur Dijon, **1970 à 2024** : le réchauffement **retire ~1,7 jour de gel par
> décennie**, et l'altitude en **ajoute ~3 par 100 mètres**. »

> 🅛 « Ce qui donne une phrase parlante : **monter de 100 mètres ajoute autant de jours de gel que
> le réchauffement en a fait disparaître en environ deux décennies.** La géographie et le climat
> tirent sur le gel en sens contraire — et on peut désormais les mettre sur la même balance. »

## 8. Limites & rigueur — 🅐 (≈ 45 s)

> 🅐 « Ce qu'on assume : 10 ans ne suffisent pas pour le climat ; certaines années sont à
> couverture partielle, on les normalise ; et `TN ≤ 0` rate le **gel au ras du sol** (la gelée
> blanche), qui demanderait la variable `TNSOL`. Ce sont nos pistes d'amélioration. »

## 9. Conclusion & ouverture — 🅛 (≈ 30 s)

> 🅛 « En résumé : à partir d'une seule source ouverte, on répond précisément à *combien de jours
> de gel*, et on explique **quand**, **pourquoi ça bouge** et **où c'est pire**. Les prochaines
> étapes : la date du **dernier gel de printemps**, et comparer un département **maritime** à un
> département **continental**. Merci — on prend vos questions. »

---

## 10. Questions probables — réponses préparées

**« Pourquoi `TN ≤ 0` et pas `< 0` ? »**
> L'énoncé définit le gel à 0 °C inclus ; physiquement, l'eau gèle à 0 °C, donc `≤ 0` est cohérent.

**« Pourquoi 2014–2023 par défaut ? »**
> C'est la fenêtre de 10 ans de l'énoncé. Pour la lecture climatique, on bascule sur 30+ ans
> (1970–2024) — c'est exactement ce qu'on fait dans l'onglet Synthèse.

**« 2018 est absente du graphe, pourquoi ? »**
> La station Dijon-Toison n'a pas de relevés `TN` cette année-là. Plutôt que d'inventer une
> valeur, on l'exclut — et on l'affiche, on ne la cache pas.

**« La station change quand on change la période ? »**
> Oui : on resélectionne la station valide la plus proche **pour la période demandée**. Sur
> 1970–2024, une station à longue archive (Quétigny) passe le filtre là où Dijon-Toison, plus
> récente, ne couvre pas les années 70.

**« Comment vous gérez les fichiers de plusieurs centaines de Mo ? »**
> Lecture en *chunks* de 500 000 lignes avec filtrage de la plage de dates à la volée, et cache
> local du fichier décompressé : on télécharge une fois, on relit ensuite instantanément.

**« Comment savez-vous que vos chiffres sont justes ? »**
> On a validé le pipeline contre un jeu de référence (6 communes avec station attendue et gel
> jour par jour). Notre définition `TN ≤ 0` reproduit la référence **6/6**, et station + comptage
> sont **identiques** quand la station la plus proche est dans le département (Marseille 52, Paris 97,
> Digne 559 — exacts). Les 3 écarts viennent de communes **frontalières** dont la station la plus
> proche est dans le département voisin : on charge un département à la fois, c'est une limite de
> périmètre qu'on assume et qu'on sait corriger (recherche sur un référentiel national de stations).

**« La corrélation altitude–gel, c'est de la causalité ? »**
> Non, c'est une corrélation à l'échelle des stations du département. L'altitude est un facteur
> physique connu (gradient thermique), mais d'autres jouent : continentalité, proximité de la mer,
> effet d'abri. D'où notre piste de comparer 35 (maritime) et 21 (continental).

---

## 11. Répartition indicative du temps de parole

| Section | Voix | Durée |
|---|---|---|
| 1. Accroche & problématique | 🅛 | 1:00 |
| 2. Données | 🅐 | 1:30 |
| 3. Pipeline & choix techniques | 🅛 + 🅐 | 2:00 |
| 4. Démo — la commune | 🅐 | 1:30 |
| 5. Démo — température | 🅛 | 1:30 |
| 6. Démo — altitude | 🅐 | 1:00 |
| 7. Synthèse (moment fort) | 🅛 | 1:30 |
| 8. Limites | 🅐 | 0:45 |
| 9. Conclusion | 🅛 | 0:30 |
| **Total** | | **≈ 11:45** |
