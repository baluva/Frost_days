"""Construit les fichiers `_complete.csv` du dossier `validation/` (consigne V2).

Règle de sélection (= pipeline, mais pool de stations NATIONAL) :
  station retenue = la plus proche de la commune dont la couverture `TN`
  est ≥ 65 % (≤ 35 % manquantes) sur la plage d'observation 2013-2024.

Sorties dans validation/ :
  - stations_df_complete.csv               (station_id, station_name)
  - city_df_complete.csv                   (35 000 communes → station la plus proche)
  - <Commune>_<dept>_complete.csv  (×6)     (série quotidienne ~12 ans)
"""
from __future__ import annotations

import re
import sys
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from frost_days.config import COMMUNES_DIR, COMMUNES_FILE, METEO_DIR  # noqa: E402
from frost_days.data_loader import load_dept  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

START, END = "2013-01-01", "2024-12-31"
START_I, END_I = 20130101, 20241231
EXPECTED = (pd.Timestamp(END) - pd.Timestamp(START)).days + 1
THRESH = 0.65                       # couverture mini (= 35 % manquantes max)
EARTH = 6371.0088
REF_DIR = ROOT / "data" / "reference"
OUT_DIR = ROOT / "validation"
SER_COLS = ["station_id", "station_name", "latitude", "longitude", "alti",
            "date", "tmin", "frost_day", "year", "month", "day"]


def haversine_matrix(lat1, lon1, lat2, lon2):
    """Distances (km) entre chaque (lat1,lon1) [N] et chaque (lat2,lon2) [M] -> N×M."""
    la1 = np.radians(lat1)[:, None]
    lo1 = np.radians(lon1)[:, None]
    la2 = np.radians(lat2)[None, :]
    lo2 = np.radians(lon2)[None, :]
    a = np.sin((la2 - la1) / 2) ** 2 + np.cos(la1) * np.cos(la2) * np.sin((lo2 - lo1) / 2) ** 2
    return 2 * EARTH * np.arcsin(np.sqrt(a))


POOL_FULL_CACHE = ROOT / "data" / "cleaned" / "_station_pool_full.csv"


def compute_full_pool() -> pd.DataFrame:
    """TOUTES les stations ayant ≥ 1 relevé TN sur 2013-2024, avec leur couverture.

    Agrégation vectorisée + cache disque (calculé une seule fois).
    """
    if POOL_FULL_CACHE.exists():
        full = pd.read_csv(POOL_FULL_CACHE, dtype={"NUM_POSTE": str, "NOM_USUEL": str})
        print(f"  pool complet: cache ({len(full)} stations avec TN sur 2013-2024)")
        return full

    files = sorted(METEO_DIR.glob("Q_*_previous-*.csv.gz"))
    parts = []
    for i, f in enumerate(files, 1):
        gs = []
        for ch in pd.read_csv(f, sep=";", compression="gzip",
                              usecols=["NUM_POSTE", "NOM_USUEL", "LAT", "LON", "ALTI", "AAAAMMJJ", "TN"],
                              dtype={"NUM_POSTE": str, "NOM_USUEL": str}, chunksize=1_000_000):
            ch["AAAAMMJJ"] = pd.to_numeric(ch["AAAAMMJJ"], errors="coerce")
            ch = ch[(ch["AAAAMMJJ"] >= START_I) & (ch["AAAAMMJJ"] <= END_I)]
            if ch.empty:
                continue
            ch["tn_ok"] = pd.to_numeric(ch["TN"], errors="coerce").notna()
            gs.append(ch.groupby("NUM_POSTE").agg(
                NOM_USUEL=("NOM_USUEL", "first"), LAT=("LAT", "first"),
                LON=("LON", "first"), ALTI=("ALTI", "first"), n_tn=("tn_ok", "sum")))
        if gs:
            parts.append(pd.concat(gs).groupby(level=0).agg(
                {"NOM_USUEL": "first", "LAT": "first", "LON": "first",
                 "ALTI": "first", "n_tn": "sum"}))
        print(f"  pool: {i}/{len(files)} départements lus", end="\r", flush=True)
    print()
    st = pd.concat(parts).reset_index().rename(columns={"index": "NUM_POSTE"})
    for c in ("LAT", "LON"):
        st[c] = pd.to_numeric(st[c], errors="coerce")
    st["coverage"] = st["n_tn"] / EXPECTED
    st = st[(st["n_tn"] >= 1) & st["LAT"].notna()].sort_values("NUM_POSTE").reset_index(drop=True)
    POOL_FULL_CACHE.parent.mkdir(parents=True, exist_ok=True)
    st.to_csv(POOL_FULL_CACHE, index=False, encoding="utf-8")
    return st


def build_valid_pool(use_cache: bool = True) -> pd.DataFrame:
    """Stations retenues = couverture ≥ THRESH sur 2013-2024."""
    full = compute_full_pool()
    return full[full["coverage"] >= THRESH].sort_values("NUM_POSTE").reset_index(drop=True)


def load_communes_centre() -> pd.DataFrame:
    """Référentiel communes au schéma city_df (coordonnées = centre de la commune)."""
    raw = pd.read_csv(COMMUNES_DIR / COMMUNES_FILE, dtype=str)
    df = pd.DataFrame({
        "insee_code": raw["code_insee"], "name": raw["nom_standard"],
        "dep_code": raw["dep_code"], "dep_name": raw["dep_nom"],
        "lat": pd.to_numeric(raw.get("latitude_centre"), errors="coerce"),
        "lon": pd.to_numeric(raw.get("longitude_centre"), errors="coerce"),
    })
    # repli mairie si centre absent
    df["lat"] = df["lat"].fillna(pd.to_numeric(raw.get("latitude_mairie"), errors="coerce"))
    df["lon"] = df["lon"].fillna(pd.to_numeric(raw.get("longitude_mairie"), errors="coerce"))
    return df.dropna(subset=["lat", "lon"]).reset_index(drop=True)


def nearest_station(cities: pd.DataFrame, pool: pd.DataFrame) -> pd.DataFrame:
    """Ajoute closest_station_* à `cities` (station valide la plus proche, par paquets)."""
    s_lat, s_lon = pool["LAT"].to_numpy(), pool["LON"].to_numpy()
    s_id, s_nom = pool["NUM_POSTE"].to_numpy(), pool["NOM_USUEL"].to_numpy()
    idx = np.empty(len(cities), dtype=int)
    c_lat, c_lon = cities["lat"].to_numpy(), cities["lon"].to_numpy()
    STEP = 1000
    for i in range(0, len(cities), STEP):
        d = haversine_matrix(c_lat[i:i+STEP], c_lon[i:i+STEP], s_lat, s_lon)
        idx[i:i+STEP] = d.argmin(axis=1)
    out = cities.copy()
    out["closest_station_name"] = s_nom[idx]
    out["closest_station_num_poste"] = s_id[idx]
    out["station_dept"] = pd.Series(s_id[idx]).str[:2].to_numpy()
    return out


def commune_series(station_id: str) -> pd.DataFrame:
    df = load_dept(station_id[:2], start=START, end=END)
    df = df[df["NUM_POSTE"] == station_id].copy()
    df = df.rename(columns={"NUM_POSTE": "station_id", "NOM_USUEL": "station_name",
                            "LAT": "latitude", "LON": "longitude", "ALTI": "alti", "TN": "tmin"})
    df["frost_day"] = df["tmin"] <= 0
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["day"] = df["date"].dt.day
    df["date"] = df["date"].dt.strftime("%Y-%m-%d")
    return df[SER_COLS].sort_values("date").reset_index(drop=True)


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "", s)


def main() -> None:
    OUT_DIR.mkdir(exist_ok=True)
    n_depts = len(list(METEO_DIR.glob("Q_*_previous-*.csv.gz")))
    print(f"== Build validation/ ({n_depts} départements) ==")

    full = compute_full_pool()                       # catalogue : toutes les stations avec TN
    pool = full[full["coverage"] >= THRESH].sort_values("NUM_POSTE").reset_index(drop=True)
    print(f"catalogue (TN sur 2013-2024) : {len(full)} stations | "
          f"pool valide (couverture ≥ {THRESH:.0%}) : {len(pool)}")

    # 1) stations_df_complete = catalogue complet des stations à thermomètre sur la période
    sdf = full.sort_values("NUM_POSTE")[["NUM_POSTE", "NOM_USUEL"]].rename(
        columns={"NUM_POSTE": "station_id", "NOM_USUEL": "station_name"})
    sdf.to_csv(OUT_DIR / "stations_df_complete.csv", index=False, encoding="utf-8")
    print(f"→ stations_df_complete.csv ({len(sdf)} lignes)")

    # 2) city_df_complete = station VALIDE la plus proche (règle 35 %, cohérente avec les communes)
    cities = load_communes_centre()
    cdf = nearest_station(cities, pool)
    cols = ["insee_code", "name", "dep_code", "dep_name", "lat", "lon",
            "closest_station_name", "closest_station_num_poste", "station_dept"]
    cdf[cols].to_csv(OUT_DIR / "city_df_complete.csv", index=False, encoding="utf-8")
    print(f"→ city_df_complete.csv ({len(cdf)} lignes)")

    # 3) fichiers communes (déduits des fichiers de référence)
    print("\nFichiers communes :")
    for f in sorted(REF_DIR.glob("*_*_short.csv")):
        commune, dept, tag = f.stem.rsplit("_", 2)
        if tag != "short" or not dept.isdigit():
            continue
        row = cdf[(cdf["dep_code"] == dept) & (cdf["name"].map(norm) == norm(commune))]
        if row.empty:
            print(f"  {commune:24s} introuvable dans city_df"); continue
        sid = str(row.iloc[0]["closest_station_num_poste"])
        ref = str(pd.read_csv(f, usecols=["station_id"], dtype=str)["station_id"].iloc[0])
        ser = commune_series(sid)
        ser.to_csv(OUT_DIR / f"{commune}_{dept}_complete.csv", index=False, encoding="utf-8")
        ok = "OK" if sid.zfill(8) == ref.zfill(8) else f"≠ réf {ref}"
        print(f"  {commune:24s} -> {sid} ({len(ser)} lignes)  [{ok}]")

    print(f"\nTerminé. Fichiers dans {OUT_DIR}")


if __name__ == "__main__":
    main()
