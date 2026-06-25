# Frost Days

> Projet réalisé par **Alexis & Louey**.

Calcul du nombre de jours de gel pour une commune française sur une plage de dates,
à partir des données climatologiques quotidiennes Météo-France (data.gouv.fr).

Un **jour de gel** = un jour où la température minimale (`TN`) sous abri a été ≤ 0 °C.

**Problématique & questions d'analyse :** voir [`QUESTIONS.md`](QUESTIONS.md).
**Script de présentation orale :** voir [`PRESENTATION.md`](PRESENTATION.md).
**Validation contre le jeu de référence :** voir [`VALIDATION.md`](VALIDATION.md).
**Audit des 60 colonnes (qualité des données) :** notebook `notebooks/02_exploration.ipynb`, § 1 bis.

## Architecture

```
frost_days/
├── frost_days/          # package Python
│   ├── config.py        # chemins, URLs, constantes
│   ├── communes.py      # référentiel communes + correctifs lat/lon
│   ├── data_loader.py   # téléchargement Météo-France (cache local)
│   ├── stations.py      # Haversine + sélection N stations proches
│   └── frost.py         # cœur du calcul (filtres NaN 35 %, agrégations)
├── scripts/
│   └── download_data.py # télécharge le référentiel + 1 département
├── notebooks/
│   ├── 01_pipeline.ipynb     # pipeline de traitement (extrait du .py)
│   └── 02_exploration.ipynb  # exploration + justification + hypothèses
├── app.py               # interface Streamlit
└── cli.py               # entrée ligne de commande
```

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

## Données

Les fichiers ne sont pas versionnés (>100 M lignes, plusieurs Go).
Pour télécharger le référentiel des communes et un département :

```bash
python scripts/download_data.py --dept 75
python scripts/download_data.py --dept 21 35 69       # plusieurs
```

Source : <https://www.data.gouv.fr/datasets/donnees-climatologiques-de-base-quotidiennes>
Schéma des champs : `Q_descriptif_champs_RR-T-Vent.csv`.
Variables clés utilisées : `NUM_POSTE`, `NOM_USUEL`, `LAT`, `LON`, `AAAAMMJJ`, `TN`.

## Usage CLI

```bash
python cli.py --commune "Dijon" --dept 21 --debut 2014-01-01 --fin 2023-12-31
```

## Usage Streamlit

```bash
streamlit run app.py
```

Interface « bulletin climatique » (4 onglets) : *La commune* (décompte, saisonnalité),
*Température & gel* (tendance de la TN d'hiver), *Altitude & gel* (gradient altitudinal),
*Synthèse* (temps vs altitude dans la même unité).

## Période d'étude

Par défaut : **2014-01-01 → 2023-12-31** (10 ans).

## Règles de qualité

- Une station ayant > **35 %** de valeurs `TN` manquantes sur la plage demandée est exclue.
- Le **29 février** est exclu des statistiques jour-par-jour (rare, biaisant les fréquences).
- Les coordonnées manquantes du référentiel sont complétées par `missing_cities_lat_lon` (cf. `frost_days/communes.py`).
