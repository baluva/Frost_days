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

## 7. La synthèse — temps **contre** espace — 🅛 (≈ 1 min 30) — *le moment fort*

*(onglet **Synthèse** ; puis changer la plage en **1970 → 2024** et re-Calculer)*

> 🅛 « Sur Dijon, de **1970 à 2024** : le réchauffement **retire ~1,7 jour de gel par
> décennie**, et l'altitude en **ajoute ~3 par 100 mètres**. »



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


