# validation/ — fichiers `_complete.csv` (consigne V2)

> Projet **Frost Days** — Alexis & Louey.
> Fichiers générés par `python scripts/build_validation.py` à partir des données
> Météo-France (98 départements) — pour vérification par l'enseignant via git.

## Contenu

| Fichier | Description | Lignes |
|---|---|---|
| `stations_df_complete.csv` | catalogue national des stations à thermomètre actives sur 2013-2024 | 2 965 |
| `city_df_complete.csv` | les ~35 000 communes → station la plus proche valide | 34 863 |
| `<Commune>_<dept>_complete.csv` (×6) | série quotidienne ~12 ans (2013-2024) de la station retenue | ~4 000 |

## Méthode

- **Période d'observation** : 2013-01-01 → 2024-12-31 (12 ans).
- **Station retenue pour une commune** : la **plus proche** (distance Haversine, coordonnées
  *centre* de la commune) dont la couverture `TN` est **≥ 65 %** (≤ 35 % de manquantes) sur la
  période — la règle métier du projet. La recherche est **nationale** (la station peut être
  dans un département voisin : ex. Asnières-sur-Saône (01) → station 71016001 du dépt 71).
- **`frost_day`** = `tmin ≤ 0 °C` (NaN → `False`).
- **`stations_df`** = toutes les stations ayant au moins un relevé `TN` sur la période (catalogue).

## Concordance avec le jeu de référence du prof (`data/reference/*_short.csv`)

- **6 fichiers communes** : station retenue **identique**, `frost_day` concordant à **100 %**
  sur toutes les dates communes.
- **stations_df** : couvre **94 %** des stations listées par le prof (le reste = différences de
  version des données data.gouv).
- **city_df** : **81 %** des communes ont la même station la plus proche que le prof. L'écart
  vient du **catalogue de stations** du prof, qui inclut des stations très peu couvertes (jusqu'à
  3 %) ou arrêtées avant 2024, sans règle reproductible — notre règle des 35 % est plus stricte et
  cohérente avec le reste du projet (et garde les 6 communes de validation exactes).

## Régénérer

```bash
python scripts/clean_data.py        # (optionnel) data/cleaned/
python scripts/build_validation.py  # -> validation/*_complete.csv
```
