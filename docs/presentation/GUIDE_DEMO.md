# Frost Days — guide de démo : quoi montrer, quand

> Idée clé : **le site est le support.** Tu n'as quasiment pas besoin de diapos.
> Tu parles, et en même temps tu montres l'écran. Ce guide dit, pour chaque moment,
> **où cliquer** et **quoi pointer du doigt**.

---

## En 1 phrase
Tu as **un seul écran à montrer** : le dashboard. Il a **4 onglets** qui suivent
exactement le plan de l'oral. Tu ajoutes juste **1 petite image** au début pour
expliquer "comment on calcule" (ça, le site ne le montre pas).

---

## Le déroulé, écran par écran

### 🟦 Moment 1 — "De quoi on parle" → **l'écran d'accueil**
*(avant de cliquer sur Calculer)*

Montre la grande page d'accueil : le titre **FROST DAYS**, la définition du jour de
gel, et surtout les **3 cartes** en bas :
> `01 · LA COMMUNE` — `02 · LA TEMPÉRATURE` — `03 · L'ALTITUDE`

👉 **À dire :** « Voilà notre plan. On va répondre à : combien de jours de gel,
puis nos deux questions — la température et l'altitude. »
*(Ces 3 cartes annoncent ton plan toutes seules. C'est ta meilleure "diapo de plan", et elle est déjà dans le site.)*

---

### 🟦 Moment 2 — "D'où viennent les données" → **une petite image** (voir plus bas)
Là, le site n'a rien à montrer. Tu peux soit rester sur l'accueil, soit afficher
**une image simple** : *Météo-France → on garde 1 seule info : la température mini de la nuit (TN)*.

👉 **À dire :** « Une seule source officielle, et de ses 40 colonnes on n'en garde qu'une : la température mini. »

---

### 🟦 Moment 3 — "Comment on calcule" → **l'image du pipeline** : [assets/pipeline.png](../../assets/pipeline.png)
C'est LE moment où une image aide vraiment, parce que le calcul se passe "dans le
moteur", le site ne le montre pas. Tu affiches le schéma **[assets/pipeline.png](../../assets/pipeline.png)** (3 étapes illustrées) :

> 📍 **Commune** → 🌡️ **Station la plus proche utilisable** → ❄️ **On compte les nuits ≤ 0 °C** → **439 jours**

👉 **À dire :** les 2 difficultés (stations sans thermomètre → on prend la 1re utilisable ; fichiers énormes → on lit par morceaux).

---

### 🟦 Moment 4 — "Le résultat pour Dijon" → **clique sur Calculer**, puis onglet **La commune**
1. Dans le panneau de gauche : **Dijon · Côte-d'Or (21) · 2014 → 2023**, clique **Calculer**.
2. En haut apparaît le **bandeau station** : `STATION DIJON TOISON · 4 KM · COUVERTURE 89%`.
   👉 Pointe-le : « On dit toujours quelle station, à quelle distance, et si les données sont complètes. »
3. Les **4 grands chiffres** : **439 jours de gel**, **~49 par an**, la TN moyenne d'hiver, et le **jour le plus gélif**.
4. Onglet **La commune** :
   - le **graphe en barres** (jours de gel par année) → « ça varie d'une année à l'autre, la ligne orange est la moyenne. »
   - la **courbe jour par jour** → « le gel est concentré de novembre à mars. »
   - le tableau **"10 jours les plus gélifs"** → pointe le **24 janvier (7/8 années)**.

---

### 🟦 Moment 5 — "Est-ce que ça se réchauffe ?" → onglet **Température & gel**
- La **courbe de la température d'hiver** année par année + la **ligne de tendance** (en pointillés) et la **ligne des 0 °C**.
  👉 « La tendance monte un peu : les hivers se réchauffent doucement. »
- Plus bas, le **nuage de points** "plus l'hiver est doux, moins il gèle" + les 2 chiffres (corrélation, effet d'un hiver +1 °C).
- 👉 Montre l'**encadré d'avertissement** en bas (« moins de 25 ans → variabilité naturelle ») : « on reste honnêtes, 10 ans c'est court. »

---

### 🟦 Moment 6 — "Est-ce que l'altitude joue ?" → onglet **Altitude & gel**
- Le **nuage de points** : chaque point = une station du département, X = altitude, Y = jours de gel/an.
- Le **point orange** = la station de Dijon.
- La **ligne de pente** : « +X jours par 100 m. »
- 👉 Les 3 chiffres en dessous (corrélation, gain par +100 m).

---

### 🟦 Moment 7 — "Le moment fort : temps vs altitude" → onglet **Synthèse**
1. **Change les dates** dans le panneau de gauche → **1970 → 2024**, re-clique **Calculer**.
   *(important : la synthèse n'est vraiment parlante que sur une longue période.)*
2. Onglet **Synthèse** : le **graphe en 2 barres horizontales** (le temps en orange tire le gel vers le bas, l'altitude en bleu vers le haut).
3. 👉 LE truc à lire à voix haute : l'**encadré "LECTURE"** —
   *« Monter de 100 m ajoute autant de gel que le réchauffement en a fait disparaître en ~2 décennies. »*

---

### 🟦 Moment 8 & 9 — Limites + conclusion → tu peux **rester sur la Synthèse**
Pas besoin de changer d'écran. Tu parles des limites (10 ans c'est court, gel au sol
non mesuré) puis tu conclus.

---

## Donc, combien d'images à préparer ?

| # | Image | Indispensable ? | État |
|---|---|---|---|
| 1 | **Schéma du pipeline** — [assets/pipeline.png](../../assets/pipeline.png) | ✅ Oui | ✅ **Créé** |
| 2 | **Schéma "1 source → 1 variable TN"** | ⬜ Bonus | À faire si tu veux |
| 3 | **Captures d'écran des 4 onglets** | ✅ Oui (sécurité) | À faire (capture d'écran du site) |

👉 En clair : **le site fait 90 % du travail visuel**. Tu prépares juste 1 schéma
de pipeline + des captures de secours. Pas besoin d'un PowerPoint complet.

---

## Conseils pratiques pour le jour J
- **Lance le site AVANT de parler** (`streamlit run app.py`), avec Dijon/2014–2023 déjà calculé : pas de temps mort.
- **Zoom navigateur ~110 %** pour que les chiffres soient lisibles au fond de la salle.
- **Garde l'onglet voulu ouvert** avant chaque transition, pour ne pas chercher en direct.
- **Plan B** : si le wifi/site lâche, tu enchaînes avec tes captures d'écran sans stresser.
