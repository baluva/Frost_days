# Frost Days — problématique & questions d'analyse

> Projet réalisé par **Alexis & Louey** — données data.gouv.fr (producteur Météo-France).

## Problématique du projet (inchangée)

> **Combien de jours de gel une commune française a-t-elle connus sur une plage de dates donnée ?**
> (jour de gel = jour où la température minimale sous abri `TN` est descendue à **0 °C ou moins**.)

Cette question reste le cœur du projet. Les questions ci-dessous ne la remplacent pas :
elles **l'approfondissent** pour passer d'un simple compteur à une vraie lecture du gel
(quand, pourquoi, où il varie). Chaque question est posée de façon **mesurable** et indique
la métrique utilisée + l'onglet du dashboard qui y répond.

---

## A. Quand gèle-t-il ? (saisonnalité & risque)

| # | Question | Métrique | Où |
|---|----------|----------|----|
| A1 | À quelle période de l'année le gel se concentre-t-il pour cette commune ? | jours de gel cumulés par mois | onglet *La commune* |
| A2 | Quels jours du calendrier ont la plus forte probabilité de gel ? | fréquence de gel par jour de l'année (n_gel / n_obs) | onglet *La commune* |
| A3 | Jusqu'à quand peut-il geler au printemps (gel tardif) ? | date moyenne du dernier gel de printemps | *à creuser* |

**Pourquoi c'est mieux que « juste compter » :** A1–A2 transforment le total en information
**actionnable** (un jardinier sait quand le risque retombe). A3 est la suite logique et
n'est pas encore dans le dashboard → bonne piste d'amélioration.

## B. La température fait-elle reculer le gel ? (influence du temps)

| # | Question | Métrique | Où |
|---|----------|----------|----|
| B1 | La température minimale d'hiver (DJF) augmente-t-elle sur la période ? | pente de régression `TN_hiver ~ année`, en °C/décennie | onglet *Température & gel* |
| B2 | Le nombre de jours de gel diminue-t-il quand l'hiver se réchauffe ? | corrélation `TN_hiver × jours_de_gel` | onglet *Température & gel* |
| B3 | Combien de jours de gel perd-on par hiver **+1 °C** plus doux ? | pente de régression `jours_de_gel ~ TN_hiver` (sensibilité) | onglet *Température & gel* |

**Formulation rigoureuse :** on ne demande pas « est-ce que ça se réchauffe » (oui/non flou)
mais **« de combien, et avec quel effet chiffré sur le gel »**. C'est falsifiable et défendable.
**Limite à assumer à l'oral :** sur 10 ans (l'énoncé) la variabilité naturelle domine — il faut
viser ~30 ans (norme OMM) pour un vrai signal climatique. Le dashboard l'affiche.

## C. L'altitude commande-t-elle le gel ? (influence de l'espace)

| # | Question | Métrique | Où |
|---|----------|----------|----|
| C1 | Le nombre de jours de gel augmente-t-il avec l'altitude des stations du département ? | pente de régression `gel/an ~ altitude`, en jours / +100 m | onglet *Altitude & gel* |
| C2 | Quelle part de la variabilité du gel entre stations s'explique par l'altitude seule ? | corrélation (et R²) altitude × gel | onglet *Altitude & gel* |
| C3 | À altitude comparable, un département maritime gèle-t-il moins qu'un continental ? | comparer la pente entre, p. ex., 35 (Ille-et-Vilaine) et 21 (Côte-d'Or) | *à creuser* |

**Pourquoi c'est mieux :** C1–C2 quantifient le gradient (un département de plaine comme la
Côte-d'Or aura une corrélation modérée ; un département alpin, forte). C3 introduit un **second
facteur** (continentalité / proximité de la mer) et montre qu'on a réfléchi au-delà d'une variable.

## D. Synthèse — temps contre espace

| # | Question | Métrique | Où |
|---|----------|----------|----|
| D1 | Des deux forces (réchauffement vs altitude), laquelle pèse le plus sur le gel ? | les deux pentes exprimées dans la **même unité** : jours de gel / an | onglet *Synthèse* |
| D2 | Combien de mètres d'altitude « annulent » une décennie de réchauffement ? | ratio `effet_altitude(+100 m) / |tendance_temporelle(/décennie)|` | onglet *Synthèse* |

**L'idée forte de l'oral :** ramener les deux influences à la même unité permet de les
**comparer directement**. Exemple validé sur Dijon, 1970–2024 :
gel **−1,7 j/an par décennie** (le temps) contre **+3,0 j/an par +100 m** (l'espace)
→ *« monter de 100 m ajoute autant de jours de gel que le réchauffement en a retiré en ~2 décennies »*.

## E. Qualité des données (rigueur méthodologique — bonus)

| # | Question | Métrique | Où |
|---|----------|----------|----|
| E1 | Quelle proportion des stations d'un département est exploitable pour le gel ? | part des stations ≤ 35 % de `TN` manquantes | notebook 02 (§2) |
| E2 | La station la plus proche est-elle toujours utilisable ? | distance retenue après filtre 35 % vs station la plus proche brute | notebook 02 (§3) |
| E3 | `TN ≤ 0 °C` sous-estime-t-il le gel au ras du sol ? | comparaison conceptuelle avec `TNSOL` (gelée blanche) | *à creuser* |

---

## En une phrase

On garde la **même** question — *combien de jours de gel ?* — mais on y répond en trois temps :
**quand** (saisonnalité), **pourquoi ça change** (température), **où c'est pire** (altitude),
puis on **oppose les deux moteurs** dans la même unité. Les pistes notées *« à creuser »*
(A3 gel tardif, C3 continentalité, E3 gel au sol) sont les prolongements naturels du projet.
