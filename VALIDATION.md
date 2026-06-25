# Validation du pipeline — jeu de référence `validation_3`

> Projet **Frost Days** — Alexis & Louey.
> Jeu de référence fourni : 6 communes + référentiels `city_df` / `stations_df`,
> avec, pour chaque commune, la station retenue et le `frost_day` **attendu** jour par jour.

## Méthode

On confronte notre pipeline à la vérité-terrain sur **deux niveaux** :

1. **Définition du gel** — notre règle `TN ≤ 0 °C` reproduit-elle la colonne `frost_day`
   de référence, jour pour jour ? (les `NaN` comptent comme « pas de gel », comme dans la référence)
2. **Pipeline complet** — pour chaque commune, est-ce qu'on sélectionne **la même station**
   et trouve-t-on **le même total** de jours de gel ?
   (départements 01, 04, 13, 38, 63, 75 téléchargés pour le test)

Script : `python validate.py` (voir le dossier de travail).

## Résultat 1 — définition du gel : **6 / 6 exacte**

Pour les 6 communes, `TN ≤ 0` reproduit **exactement** la colonne `frost_day` de référence.
La définition métier est donc validée sans écart.

## Résultat 2 — pipeline complet

| Commune | Dépt | Station de référence | Notre station | Gel réf. | Notre gel | Verdict |
|---|---|---|---|---|---|---|
| **Digne-les-Bains** | 04 | `4070009` | `04070009` DIGNE LES BAINS | 559 | **559** | ✅ identique |
| **Marseille** | 13 | `13055029` | `13055029` MARSEILLE | 52 | **52** | ✅ identique |
| **Paris** | 75 | `75106001` | `75106001` LUXEMBOURG | 97 | **97** | ✅ identique |
| Asnières-sur-Saône | 01 | `71016001` *(dépt 71)* | `01367002` | 193 | 224 | ⚠️ station hors dépt |
| Espinchal | 63 | `15114002` *(dépt 15)* | `63006002` | 629 | 688 | ⚠️ station hors dépt |
| Montfalcon | 38 | `26298001` *(dépt 26)* | `38130001` | 239 | 273 | ⚠️ station hors dépt |

*(L'identifiant `4070009` de la référence et notre `04070009` sont **la même station** : la référence
a perdu le zéro de tête en lisant le code comme un entier.)*

## Lecture

- **Chaque fois que la station la plus proche est dans le département de la commune, on tombe
  exactement juste** : même station, même comptage (Δ = 0). C'est le cas de Digne, Marseille et Paris.
- **Les 3 écarts ont tous la même cause :** la station la plus proche de la référence est dans un
  **département voisin** (Asnières → 71, Espinchal → 15, Montfalcon → 26). Ces 3 communes sont sur
  une **limite départementale**, et leur station la plus proche est de l'autre côté de la frontière.

Notre pipeline charge **un seul département à la fois** (choix assumé pour la performance : ne jamais
charger toute la France en mémoire). Il ne peut donc pas « voir » une station au-delà de la frontière.
**Ce n'est pas une erreur de calcul** — la logique de gel et la sélection *intra-département* sont exactes —
mais une **limite de périmètre** que la validation a permis de mettre au jour.

## Piste d'amélioration (suite logique)

Pour matcher la référence à 6/6 : faire la recherche de station la plus proche sur un **référentiel
national** de stations (comme `stations_df`), puis ne charger que le département de la station retenue.
Cela couvrirait les communes frontalières sans renoncer au chargement département par département.
