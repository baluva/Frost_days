"""Téléchargement / chargement des fichiers quotidiens Météo-France par département."""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import requests

from .config import (
    METEO_BASE_URL,
    METEO_DIR,
    METEO_FILE_TEMPLATE,
    METEO_LATEST_TEMPLATE,
)

# Colonnes utiles pour le calcul des jours de gel.
# ALTI ajoutée pour l'analyse "impact de l'altitude sur le gel".
USECOLS = ["NUM_POSTE", "NOM_USUEL", "LAT", "LON", "ALTI", "AAAAMMJJ", "TN"]


def _normalize_dept(dept: str | int) -> str:
    """'1' -> '01', '75' -> '75', '2A' -> '2A'."""
    s = str(dept).strip().upper()
    if s in {"2A", "2B"}:
        return s
    return s.zfill(2)


def file_url(dept: str, latest: bool = False) -> str:
    tmpl = METEO_LATEST_TEMPLATE if latest else METEO_FILE_TEMPLATE
    return f"{METEO_BASE_URL}/{tmpl.format(dept=dept)}"


def download_dept(dept: str | int, latest: bool = False) -> Path:
    """Télécharge le fichier d'un département s'il n'est pas en cache."""
    dept = _normalize_dept(dept)
    tmpl = METEO_LATEST_TEMPLATE if latest else METEO_FILE_TEMPLATE
    fname = tmpl.format(dept=dept)
    path = METEO_DIR / fname
    if path.exists() and path.stat().st_size > 0:
        return path
    url = file_url(dept, latest=latest)
    print(f"[meteo] téléchargement {url}")
    with requests.get(url, stream=True, timeout=600) as r:
        r.raise_for_status()
        tmp = path.with_suffix(path.suffix + ".part")
        with open(tmp, "wb") as f:
            for chunk in r.iter_content(chunk_size=1 << 20):
                f.write(chunk)
        tmp.replace(path)
    return path


def load_dept(
    dept: str | int,
    start: str | None = None,
    end: str | None = None,
    usecols: list[str] = USECOLS,
) -> pd.DataFrame:
    """Charge le CSV d'un département, ne garde que les lignes dans [start, end].

    Le CSV est gros : on charge en chunks et on filtre tout de suite la plage de dates.
    """
    path = download_dept(dept)
    start_i = int(pd.Timestamp(start).strftime("%Y%m%d")) if start else None
    end_i = int(pd.Timestamp(end).strftime("%Y%m%d")) if end else None

    chunks: list[pd.DataFrame] = []
    reader = pd.read_csv(
        path,
        sep=";",
        compression="gzip",
        usecols=usecols,
        dtype={"NUM_POSTE": str, "NOM_USUEL": str},
        chunksize=500_000,
        low_memory=False,
    )
    for chunk in reader:
        chunk["AAAAMMJJ"] = pd.to_numeric(chunk["AAAAMMJJ"], errors="coerce")
        if start_i is not None:
            chunk = chunk[chunk["AAAAMMJJ"] >= start_i]
        if end_i is not None:
            chunk = chunk[chunk["AAAAMMJJ"] <= end_i]
        if not chunk.empty:
            chunks.append(chunk)
    if not chunks:
        return pd.DataFrame(columns=usecols)
    df = pd.concat(chunks, ignore_index=True)
    df["date"] = pd.to_datetime(df["AAAAMMJJ"].astype(int).astype(str), format="%Y%m%d")
    df["TN"] = pd.to_numeric(df["TN"], errors="coerce")
    df["LAT"] = pd.to_numeric(df["LAT"], errors="coerce")
    df["LON"] = pd.to_numeric(df["LON"], errors="coerce")
    df["ALTI"] = pd.to_numeric(df["ALTI"], errors="coerce")
    return df


def list_stations(df: pd.DataFrame) -> pd.DataFrame:
    """Une ligne par station avec ses coordonnées et altitude."""
    return (
        df.dropna(subset=["LAT", "LON"])
        .groupby("NUM_POSTE", as_index=False)
        .agg(
            NOM_USUEL=("NOM_USUEL", "first"),
            LAT=("LAT", "first"),
            LON=("LON", "first"),
            ALTI=("ALTI", "first"),
        )
    )
