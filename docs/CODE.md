# Comment marche le code — `frost_days` (vite fait)

> Le cœur tient en **5 fichiers Python** dans `frost_days/`. Tout part d'**un seul appel** :
> `compute_frost_days(commune, dept, lat, lon, start, end)` → un objet `FrostResult`.
> La CLI, l'app Streamlit et les notebooks ne font qu'**appeler cette fonction et afficher le résultat**.

## Le flux en un coup d'œil (qui appelle qui)

```
app.py / cli.py / notebook
   │  find_commune(nom, dept) ─► (lat, lon)            [communes.py]
   ▼
compute_frost_days(commune, dept, lat, lon, start, end)   [frost.py]  ◄── point d'entrée unique
   ├─ load_dept(dept, start, end)                      [data_loader.py]  charge le CSV.gz filtré
   ├─ list_stations(df)                                [data_loader.py]  1 ligne / station
   ├─ _select_best_station(...)                        [frost.py]
   │      └─ nearest_stations(stations, lat, lon)      [stations.py]     Haversine → 5 plus proches
   ├─ is_frost = TN ≤ 0  → total, moyenne/an, fréquence/jour
   └─ _compute_dept_stations(...)                      [frost.py]        altitude × gel (toutes stations)
   ▼
FrostResult (dataclass)  ──►  graphes / metrics
```

## Module par module

### `config.py` — les constantes (rien de caché)
Tous les paramètres sont ici, pas de valeur magique perdue dans le code :
- `MAX_MISSING_RATIO = 0.35` (seuil station), `TOP_N_STATIONS = 5`, dates par défaut **2014 → 2023**.
- URLs Météo-France + nom de fichier `Q_{dept}_previous-1950-2024_RR-T-Vent.csv.gz`.
- Crée les dossiers `data/meteo` et `data/communes` dès l'import.

### `communes.py` — commune → (lat, lon)
- `load_communes()` : lit le référentiel communes. **Robuste aux changements de format data.gouv** : détecte le séparateur (`sep=None`, moteur python) *et* les noms de colonnes via `pick("latitude_mairie","latitude",…)` (ils varient selon le snapshot).
- `MISSING_CITIES_LAT_LON` : dict de rattrapage pour ~9 communes (Paris, Marseille, Lyon…) dont les coordonnées manquent dans le référentiel — complétées à la main.
- `find_commune(df, nom, dept)` → `(lat, lon)`. Cherche par (nom + dept), sinon fallback par nom seul, sinon `KeyError`.

### `data_loader.py` — télécharger + lire le CSV
- `download_dept(dept)` : télécharge le `.csv.gz` **une seule fois** (cache : si le fichier existe et n'est pas vide, on ne re-télécharge pas). Écrit dans un `.part` puis `replace()` → jamais de `.gz` à moitié écrit si la connexion coupe.
- `load_dept(dept, start, end)` : **le point clé perf**. Le CSV décompressé pèse des centaines de Mo → on lit en **chunks de 500 000 lignes** et on **filtre la plage de dates dans chaque chunk** avant de concaténer. On ne garde que **7 colonnes** (`USECOLS`) et on type proprement (`TN`, `LAT`, `LON`, `ALTI` en numérique, `date` en datetime).
- `list_stations(df)` : réduit le DataFrame à **une ligne par station** (coords + altitude) — c'est l'entrée du calcul de distance.

### `stations.py` — la station la plus proche
- `haversine_km(lat1, lon1, lat2[], lon2[])` : distance grand-cercle **vectorisée** (1 point vs N stations, en numpy). Corrige la sphéricité de la Terre, contrairement à une distance euclidienne sur lat/lon qui déformerait l'axe est-ouest.
- `nearest_stations(stations, lat, lon, top_n=5)` : distance vers toutes les stations → renvoie les `top_n` plus proches triées (`nsmallest`) avec une colonne `dist_km`.

### `frost.py` — le calcul (le cœur)
`compute_frost_days(...)` enchaîne :
1. `load_dept` → DataFrame du département sur la plage.
2. `_select_best_station(...)` : prend les 5 plus proches (`nearest_stations`) et **descend la liste jusqu'à la première station avec ≤ 35 % de manquantes**.
   *Subtilité* : `missing_ratio = 1 − n_obs / expected_days` → il compte **à la fois les jours absents et les `TN` à NaN**, pas seulement les NaN. Si **aucune** ne passe le seuil → on prend « la moins pire » et on la garde quand même (signalée par son `missing_ratio`).
3. Calcul du gel sur la station retenue :
   - `is_frost = TN ≤ 0` (`TN` est déjà en °C dans le CSV brut → **pas de division par 10**).
   - **total** = somme des `is_frost`.
   - **par an** : `groupby("year")` → `frost_days` + `total_days`, puis la moyenne.
   - **fréquence par jour de l'année** : `groupby(["month","day"])` → `n_frost / n_obs`, en **excluant le 29 février** (1 obs contre ~10 → fréquence faussée).
   - **bonus** : `tn_per_year` (TN moyenne annuelle + hiver DJF déc-jan-fév) et `_compute_dept_stations` (altitude × gel pour **toutes** les stations ≥ 65 % de couverture → graphe altitude/gel).
4. Renvoie un **`FrostResult`** (dataclass) qui transporte tout : station retenue, distance, altitude, total, séries `per_year` / `per_day_of_year`, etc.

## Les points subtils (à savoir pour défendre le code)

| Dans le code | Pourquoi c'est fait comme ça |
|---|---|
| `chunksize=500_000` + filtre date par chunk | ne **jamais** charger des centaines de Mo en RAM d'un coup |
| `missing_ratio = 1 − n_obs/expected_days` | un jour **absent** est aussi gênant qu'un `TN` NaN → les deux comptent |
| boucle « 5 plus proches **puis** filtre » (≠ plus proche absolue) | la station la plus proche peut être vide — ex. *DIJON* (2 km) éliminée → *DIJON TOISON* (4 km) |
| `not_leap` (exclusion du 29/02) | sinon le 29 fév a ~1 obs vs ~10 → sa fréquence de gel serait trompeuse |
| download via `.part` puis `replace()` | un téléchargement coupé ne laisse pas un fichier corrompu dans le cache |
| `sep=None` + `pick(...)` dans `communes.py` | le référentiel data.gouv change de séparateur / de noms de colonnes selon le snapshot |
| `FrostResult` = **une seule** dataclass | l'app, la CLI et les notebooks consomment **le même objet** — zéro recalcul, zéro divergence |

## Où ce cœur est utilisé
- **`cli.py`** — appelle `compute_frost_days` puis affiche le résultat en texte.
- **`app.py`** — Streamlit (« bulletin climatique »), graphes Plotly, lit le même `FrostResult`.
- **`notebooks/01_pipeline.ipynb`** — rejoue le pipeline étape par étape (pour comprendre le flux).
- **`notebooks/02_exploration.ipynb`** — justifie chaque choix (audit des 60 colonnes, seuil 35 %, type de graphe…) et pose les hypothèses H1→H6 + le retour de validation.

## Pour relancer
```bash
pip install -r requirements.txt
python scripts/download_data.py --dept 21      # télécharge un département (mis en cache)
python cli.py --commune Dijon --dept 21        # calcul en ligne de commande
streamlit run app.py                            # interface graphique
```
