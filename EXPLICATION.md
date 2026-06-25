# Frost Days — explication du projet

## 1. Ce que fait l'appli

À partir d'une **commune française**, d'un **département** et d'une **plage de dates**, on calcule :
- le **nombre total de jours de gel** sur la période,
- la **moyenne par année**,
- la **fréquence de gel pour chaque jour de l'année** (ex : le 24 janv → 7/8 = 88 %).

**Définition métier** : un jour de gel = un jour où la température minimale sous abri (`TN`) a été ≤ 0 °C.

## 2. Les données

Source unique : **data.gouv.fr** — dataset *"Données climatologiques de base — quotidiennes"* (producteur : Météo-France).

Deux fichiers utilisés :
- **Référentiel communes** (CSV ~21 Mo, version 17/06/2026) → pour récupérer lat/lon de la commune.
- **Fichier départemental** `Q_<dept>_previous-1950-2024_RR-T-Vent.csv.gz` (~10-30 Mo gzippé chacun) → données quotidiennes par station météo.

Colonnes gardées dans le CSV départemental (parmi ~40) : `NUM_POSTE`, `NOM_USUEL`, `LAT`, `LON`, `AAAAMMJJ`, **`TN`**. Le reste (pluie, vent…) ne sert pas pour le gel.

## 3. Pipeline (en 5 étapes)

```
commune + dept + dates
        │
        ▼
[1] référentiel communes      → lat/lon de la commune (+ correctifs manuels Paris/Marseille/…)
        │
        ▼
[2] download CSV.gz du dept   → mis en cache local, pas re-téléchargé ensuite
        │
        ▼
[3] load_dept (par chunks 500k lignes, filtré sur la plage)
        │
        ▼
[4] Haversine sur les stations → 5 plus proches → on prend la 1re qui a ≤ 35 % de NaN sur TN
        │
        ▼
[5] is_frost = TN ≤ 0  →  total / moyenne par an / fréquence par jour de l'année
```

## 4. Choix techniques justifiés

| Choix | Pourquoi |
|---|---|
| **Lecture en chunks** | Le fichier décompressé fait des centaines de Mo. On filtre la plage de dates au fur et à mesure pour ne jamais tout charger en RAM. |
| **Haversine** vs Euclidien | À 47° N, 1° de longitude ≈ 70 km vs 1° de latitude ≈ 111 km. Haversine corrige la sphéricité. |
| **Règle des 35 % de NaN** | Une station avec trop de trous donne des stats biaisées. Justifié sur le département 21 : **38 / 58 stations ont 100 % de NaN sur TN** (ce sont des pluviomètres sans thermomètre), la distribution est bimodale → le seuil isole proprement les stations exploitables. |
| **Stratégie top-N puis filtre** (pas la plus proche absolue) | Sur Dijon, la station la plus proche (*DIJON*, 2 km) est éliminée pour cause de NaN > 35 % → on retombe sur *DIJON TOISON* à 4 km, qui passe le filtre. Sans cette stratégie, on aurait calculé sur une station fantôme. |
| **Exclusion du 29 février** | Pour la stat jour-par-jour, le 29/02 a 1 observation contre 10 ailleurs → fréquence biaisée. |
| **Cache local des CSV** | Le téléchargement Météo-France est lent ; on télécharge une fois et on lit ensuite localement. |

## 5. Architecture du code

```
frost_days/                    ← package Python (cœur métier)
├── config.py                  constantes, URLs, seuils
├── communes.py                référentiel + dict missing_cities_lat_lon
├── data_loader.py             download + lecture chunks
├── stations.py                Haversine
└── frost.py                   pipeline complet, retourne un FrostResult

scripts/download_data.py       télécharge le référentiel + un département
cli.py                         interface ligne de commande
app.py                         interface Streamlit « bulletin climatique » (4 onglets Plotly)

notebooks/
├── 01_pipeline.ipynb          rejoue le pipeline étape par étape (pour comprendre le flux)
└── 02_exploration.ipynb       qualité des données + justifs des graphes + 7 hypothèses
```

## 6. Résultat de validation

Test end-to-end sur **Dijon, 2014-01-01 → 2023-12-31** :
- Station : **DIJON TOISON** à 4 km (10,8 % de NaN sur TN)
- **439 jours de gel** sur 10 ans → **48,8 jours/an** en moyenne
- Jour le plus gélif : **24 janvier** (7/8 années = 87,5 %)
- Gel concentré **novembre → mars**, pratiquement zéro de mai à octobre

## 7. Pour relancer

```bash
pip install -r requirements.txt
python scripts/download_data.py --dept 21          # un département
python cli.py --commune Dijon --dept 21            # CLI
streamlit run app.py                                # UI graphique
```

Les notebooks (`01_pipeline.ipynb`, `02_exploration.ipynb`) se lancent avec Jupyter pour comprendre le détail.
