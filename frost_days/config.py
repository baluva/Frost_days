"""Constantes : chemins, URLs Météo-France, paramètres métier."""
from __future__ import annotations
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
METEO_DIR = DATA_DIR / "meteo"
COMMUNES_DIR = DATA_DIR / "communes"

for d in (METEO_DIR, COMMUNES_DIR):
    d.mkdir(parents=True, exist_ok=True)

METEO_BASE_URL = (
    "https://object.files.data.gouv.fr/meteofrance/data/synchro_ftp/BASE/QUOT"
)

# La plage 2014-2023 est intégralement contenue dans le fichier "previous-1950-2023".
METEO_FILE_TEMPLATE = "Q_{dept}_previous-1950-2024_RR-T-Vent.csv.gz"
METEO_LATEST_TEMPLATE = "Q_{dept}_latest-2025-2026_RR-T-Vent.csv.gz"

# Référentiel communes (data.gouv.fr, format JSON le plus stable).
COMMUNES_URL = (
    "https://www.data.gouv.fr/api/1/datasets/r/c63fd0b1-7987-46f6-b779-8b3ed889090c"
)
COMMUNES_FILE = "communes-france.csv"

# Seuil métier : on rejette une station si > 35 % de TN manquantes sur la plage.
MAX_MISSING_RATIO = 0.35

# Nombre de stations à conserver autour d'une commune (la plus proche valide gagne).
TOP_N_STATIONS = 5

DEFAULT_START = "2014-01-01"
DEFAULT_END = "2023-12-31"
