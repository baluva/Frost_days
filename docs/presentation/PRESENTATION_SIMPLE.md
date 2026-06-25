# Frost Days — présentation orale (version simple)

**Binôme :** Alexis & Louey · **Durée :** ~7-8 min + questions
**Support :** le dashboard en direct (`streamlit run app.py`).

> 🅰 = Alexis · 🅛 = Louey · *(action)* = ce qu'on fait à l'écran.

---

## Avant de commencer (checklist rapide)

- [ ] L'appli est lancée (`streamlit run app.py`), sur `localhost:8501`.
- [ ] Réglages de départ : **Dijon · Côte-d'Or (21) · 2014 → 2023**.
- [ ] Données déjà en local → pas besoin d'internet pendant la démo.
- [ ] Zoom du navigateur à ~110 % pour que ce soit lisible au projecteur.

---

## 1. De quoi on parle — 🅛 (~1 min)

> 🅛 « On entend souvent que *les hivers sont de moins en moins froids*. Mais
> "de moins en moins", ça veut dire quoi exactement ? Nous on a voulu le mesurer
> avec quelque chose de très concret : **le jour de gel**. »

*(montrer l'écran d'accueil "FROST DAYS")*

> 🅛 « Notre question est toute simple : **combien de jours de gel une commune
> a connus sur une période donnée ?** Pour nous, un jour de gel, c'est un jour
> où il a fait **0 °C ou moins** pendant la nuit. Tout le projet tient sur cette
> ligne des zéro degré. »

> 🅛 « Et une fois qu'on sait compter le gel, on propose **deux questions** pour
> aller plus loin : est-ce qu'il gèle **de moins en moins avec le temps** (le
> réchauffement) ? Et est-ce qu'il gèle **plus quand on monte en altitude** ?
> C'est ce qu'on va regarder. »

## 2. D'où viennent les données — 🅐 (~1 min)

> 🅐 « On utilise **une seule source, officielle** : les données de Météo-France,
> disponibles sur data.gouv.fr. Ce sont les relevés des stations météo, jour par
> jour, depuis 1950. »

> 🅐 « Dans ces fichiers il y a une quarantaine d'infos par jour. Nous on n'en
> garde qu'**une** qui nous intéresse : la **température la plus basse de la nuit**.
> Parce que c'est ça qui fait geler — une seule nuit très froide suffit, même si
> la journée a été douce. »

## 3. Comment on calcule — 🅛 puis 🅐 (~1 min 30)

> 🅛 « Le principe en gros : tu nous donnes une commune, on récupère sa position,
> on regarde la **station météo la plus proche**, et on compte les nuits où il a
> fait zéro ou moins. »

**Deux petites difficultés qu'on a dû régler :**

> 🅐 « **Un :** beaucoup de stations ne mesurent pas la température — ce sont juste
> des pluviomètres. Si on prend bêtement la plus proche, on peut tomber sur une
> station qui n'a aucune donnée de température. Du coup on regarde les **5 plus
> proches** et on garde la première qui a assez de mesures. »

> 🅐 « Pour Dijon par exemple, la station la plus proche (2 km) est inutilisable :
> on prend celle juste à côté, à 4 km. »

> 🅛 « **Deux :** les fichiers sont énormes, plusieurs centaines de Mo. Donc on les
> lit **petit bout par petit bout** pour ne pas faire planter l'ordi. »

## 4. Le résultat pour Dijon — 🅐 (~1 min 30)

*(cliquer **Calculer** avec Dijon / 2014–2023)*

> 🅐 « Voilà la réponse directe : pour Dijon, sur 10 ans, **439 jours de gel**,
> donc à peu près **49 par an**. En haut, on affiche toujours quelle station on a
> utilisée et si les données sont complètes — on joue franc-jeu sur la qualité. »

*(onglet **La commune** — barres par année, puis la courbe jour par jour)*

> 🅐 « On voit tout de suite que le gel se concentre de **novembre à mars**, et
> qu'il n'y a quasiment rien l'été. Et certains jours reviennent tout le temps :
> le **24 janvier** a gelé **7 années sur 8**. Pour un jardinier, c'est un vrai
> calendrier des risques. »

## 5. Est-ce que ça se réchauffe ? — 🅛 (~1 min 30)

*(onglet **Température & gel**)*

> 🅛 « Première chose qui fait bouger le gel : **le temps qui passe**. On regarde la
> température moyenne des hivers, année après année. Ici la tendance monte un peu :
> les hivers se réchauffent doucement. Et logiquement, **plus l'hiver est doux,
> moins il y a de jours de gel** — la relation est nette. »

> 🅛 « Mais on reste honnêtes : sur seulement 10 ans, c'est encore fragile, il y a
> beaucoup de variations naturelles d'une année à l'autre. Pour vraiment parler de
> climat, il faut plutôt **30 ans**. »

## 6. Est-ce que l'altitude joue ? — 🅐 (~1 min)

*(onglet **Altitude & gel**)*

> 🅐 « Deuxième chose : **l'altitude**. Chaque point est une station du département.
> Plus on monte, plus il gèle — ça paraît évident, mais là on le **voit chiffré**.
> Dijon est le point orange. Sur un département de plaine c'est modéré ; en montagne,
> l'effet serait énorme. »

## 7. Le moment fort : le temps contre l'altitude — 🅛 (~1 min 30)

*(onglet **Synthèse** ; passer la période en **1970 → 2024** et re-Calculer)*

> 🅛 « Et là, notre idée à nous : mettre les **deux effets dans la même unité** pour
> pouvoir les comparer. Sur Dijon, de 1970 à 2024 : le réchauffement **enlève environ
> 1,7 jour de gel par décennie**, et monter de 100 mètres en **ajoute environ 3**. »


## 8. Ce qu'on assume — 🅐 (~30 s)

> 🅐 « On ne cache rien : 10 ans c'est court pour parler de climat ; certaines années
> ont des données incomplètes, on en tient compte ; et on ne mesure pas le petit gel
> du matin au ras du sol. Ce sont nos pistes pour aller plus loin. »

## 9. Conclusion — 🅛 (~30 s)

> 🅛 « Pour résumer : avec une seule source ouverte, on répond précisément à *combien
> de jours de gel*, et en plus on explique **quand** ça gèle, **pourquoi ça change**
> et **où c'est pire**. La suite, ce serait de regarder le **dernier gel du printemps**
> et de comparer une ville **au bord de la mer** avec une ville **dans les terres**.
> Merci ! On répond à vos questions. »

---

## Questions probables — réponses simples

**« Pourquoi 0 °C inclus et pas en dessous ? »**
> Parce que l'eau gèle à 0 °C, donc on compte 0 comme un jour de gel.

**« Pourquoi 2014–2023 par défaut ? »**
> C'est la période de 10 ans demandée. Pour une vraie lecture du climat, on passe à
> 30 ans et plus — c'est ce qu'on fait dans l'onglet Synthèse.

**« Pourquoi il manque une année sur le graphe ? »**
> La station n'avait pas de relevés cette année-là. Plutôt que d'inventer un chiffre,
> on préfère l'enlever — et on le montre, on ne le cache pas.

**« La station change quand on change la période ? »**
> Oui, on reprend la station valable la plus proche pour la période demandée. Sur une
> très longue période, certaines stations récentes ne couvrent pas le début.

**« Comment vous gérez des fichiers aussi gros ? »**
> On les lit par petits morceaux, et on garde une copie en local : on télécharge une
> fois, ensuite c'est instantané.

**« Comment vous savez que vos chiffres sont justes ? »**
> On les a comparés à un jeu de référence (6 communes). Notre définition du gel colle
> parfaitement (6/6), et on retrouve exactement les bons chiffres quand la station est
> dans le même département. Les rares écarts viennent de communes en bordure dont la
> station la plus proche est dans le département d'à côté — c'est une limite qu'on
> connaît et qu'on sait corriger.

**« Altitude et gel, c'est une cause ou juste un lien ? »**
> C'est un lien clair, et physiquement logique (il fait plus froid en hauteur), mais
> d'autres facteurs jouent aussi, comme la proximité de la mer. D'où notre idée de
> comparer une ville côtière et une ville continentale.

---

## Qui parle quand (repère)

| Section | Voix | Durée |
|---|---|---|
| 1. De quoi on parle | 🅛 | ~1:00 |
| 2. Les données | 🅐 | ~1:00 |
| 3. Comment on calcule | 🅛 + 🅐 | ~1:30 |
| 4. Résultat Dijon | 🅐 | ~1:30 |
| 5. La température | 🅛 | ~1:30 |
| 6. L'altitude | 🅐 | ~1:00 |
| 7. Temps vs altitude | 🅛 | ~1:30 |
| 8. Limites | 🅐 | ~0:30 |
| 9. Conclusion | 🅛 | ~0:30 |
| **Total** | | **≈ 10 min** |
