"""Référentiel des communes françaises + correctifs pour les coordonnées manquantes."""
from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

from .config import COMMUNES_DIR, COMMUNES_FILE, COMMUNES_URL

# Communes avec coordonnées absentes / erronées dans le référentiel,
# complétées manuellement (énoncé du challenge).
MISSING_CITIES_LAT_LON: dict[str, list[float]] = {
    "Marseille": [43.295, 5.372],
    "Paris": [48.866, 2.333],
    "Culey": [48.755, 5.266],
    "Les Hauts-Talican": [49.3436, 2.0193],
    "Lyon": [45.75, 4.85],
    "Bihorel": [49.4542, 1.1162],
    "Saint-Lucien": [48.6480, 1.6229],
    "L'Oie": [46.7982, -1.1302],
    "Sainte-Florence": [46.7965, -1.1520],
}


def download_communes(force: bool = False) -> Path:
    """Télécharge le référentiel communes si absent."""
    path = COMMUNES_DIR / COMMUNES_FILE
    if path.exists() and not force:
        return path
    print(f"[communes] téléchargement {COMMUNES_URL}")
    r = requests.get(COMMUNES_URL, timeout=120)
    r.raise_for_status()
    path.write_bytes(r.content)
    return path


def load_communes() -> pd.DataFrame:
    """Charge et normalise le référentiel communes.

    Colonnes garanties en sortie : `nom`, `nom_norm`, `dept`, `lat`, `lon`.
    """
    path = download_communes()
    # Le CSV data.gouv utilise ';' comme séparateur.
    # Le séparateur peut varier selon le snapshot data.gouv (',' ou ';').
    # On laisse pandas le détecter via le moteur python pour être robuste.
    df = pd.read_csv(path, sep=None, engine="python", dtype=str)
    # Détection souple des colonnes (les noms varient selon les exports).
    cols = {c.lower(): c for c in df.columns}

    def pick(*candidates: str) -> str | None:
        for c in candidates:
            if c in cols:
                return cols[c]
        return None

    name_col = pick("nom_standard", "nom_commune", "nom", "libelle", "nom_complet")
    dept_col = pick("dep_code", "code_departement", "departement", "dep")
    lat_col = pick("latitude_mairie", "latitude", "lat", "latitude_centre")
    lon_col = pick("longitude_mairie", "longitude", "lon", "lng", "longitude_centre")

    if not all([name_col, dept_col, lat_col, lon_col]):
        raise RuntimeError(
            f"Colonnes introuvables dans le référentiel: {list(df.columns)[:15]}…"
        )

    out = pd.DataFrame({
        "nom": df[name_col].str.strip(),
        "dept": df[dept_col].str.zfill(2),
        "lat": pd.to_numeric(df[lat_col], errors="coerce"),
        "lon": pd.to_numeric(df[lon_col], errors="coerce"),
    })
    out["nom_norm"] = out["nom"].str.lower().str.strip()

    # Patch des coordonnées manquantes.
    for name, (lat, lon) in MISSING_CITIES_LAT_LON.items():
        mask = out["nom_norm"] == name.lower()
        out.loc[mask & out["lat"].isna(), "lat"] = lat
        out.loc[mask & out["lon"].isna(), "lon"] = lon

    return out


def find_commune(df: pd.DataFrame, nom: str, dept: str) -> tuple[float, float]:
    """Retourne (lat, lon) pour (nom, dept). Lève KeyError si introuvable / sans coord."""
    dept = str(dept).zfill(2)
    nom_norm = nom.lower().strip()
    sub = df[(df["nom_norm"] == nom_norm) & (df["dept"] == dept)]
    if sub.empty:
        # Fallback : recherche par nom seul, on prend la plus 'similaire'.
        sub = df[df["nom_norm"] == nom_norm]
    if sub.empty:
        raise KeyError(f"Commune introuvable: {nom} ({dept})")
    row = sub.iloc[0]
    if pd.isna(row["lat"]) or pd.isna(row["lon"]):
        raise KeyError(f"Coordonnées manquantes pour {nom} ({dept})")
    return float(row["lat"]), float(row["lon"])
