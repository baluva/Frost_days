"""Cœur du calcul des jours de gel pour une commune et une plage de dates."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .config import DEFAULT_END, DEFAULT_START, MAX_MISSING_RATIO, TOP_N_STATIONS
from .data_loader import list_stations, load_dept
from .stations import nearest_stations


@dataclass
class FrostResult:
    commune: str
    dept: str
    start: pd.Timestamp
    end: pd.Timestamp
    station_id: str
    station_name: str
    station_distance_km: float
    station_altitude: float
    missing_ratio: float
    frost_days_total: int
    frost_days_per_year_mean: float
    per_year: pd.DataFrame          # cols: year, frost_days, total_days
    per_day_of_year: pd.DataFrame   # cols: month, day, n_frost, n_obs, freq
    # Évolution thermique : TN moyenne par année (annuelle + hiver DJF).
    tn_per_year: pd.DataFrame       # cols: year, tn_mean_annual, tn_mean_winter
    # Toutes les stations valides du département : altitude vs gel.
    dept_stations: pd.DataFrame     # cols: NUM_POSTE, NOM_USUEL, ALTI, frost_days, frost_days_per_year


def _select_best_station(
    df: pd.DataFrame,
    stations: pd.DataFrame,
    lat: float,
    lon: float,
    start: pd.Timestamp,
    end: pd.Timestamp,
    top_n: int,
    max_missing: float,
) -> tuple[pd.DataFrame, pd.Series]:
    """Choisit la station valide la plus proche (≤ `max_missing` de NaN sur TN)."""
    candidates = nearest_stations(stations, lat, lon, top_n=top_n)
    expected_days = (end - start).days + 1
    for _, row in candidates.iterrows():
        sdf = df[df["NUM_POSTE"] == row["NUM_POSTE"]].copy()
        sdf = sdf[(sdf["date"] >= start) & (sdf["date"] <= end)]
        # Taux de manquantes : à la fois jours absents et TN NaN.
        n_obs = sdf["TN"].notna().sum()
        missing_ratio = 1 - n_obs / expected_days
        if missing_ratio <= max_missing:
            row = row.copy()
            row["missing_ratio"] = missing_ratio
            return sdf, row
    # Aucune n'est valide : on prend la moins pire et on flag.
    best = None
    best_missing = 1.0
    best_sdf = pd.DataFrame()
    for _, row in candidates.iterrows():
        sdf = df[df["NUM_POSTE"] == row["NUM_POSTE"]].copy()
        sdf = sdf[(sdf["date"] >= start) & (sdf["date"] <= end)]
        miss = 1 - sdf["TN"].notna().sum() / expected_days
        if miss < best_missing:
            best, best_missing, best_sdf = row, miss, sdf
    if best is None:
        raise RuntimeError("Aucune station candidate trouvée.")
    best = best.copy()
    best["missing_ratio"] = best_missing
    return best_sdf, best


def compute_frost_days(
    commune: str,
    dept: str,
    lat: float,
    lon: float,
    start: str = DEFAULT_START,
    end: str = DEFAULT_END,
    top_n: int = TOP_N_STATIONS,
    max_missing: float = MAX_MISSING_RATIO,
) -> FrostResult:
    """Pipeline complet pour une commune : charge le département, sélectionne la station,
    calcule les statistiques de jours de gel."""
    start_ts = pd.Timestamp(start)
    end_ts = pd.Timestamp(end)
    df = load_dept(dept, start=start, end=end)
    if df.empty:
        raise RuntimeError(f"Aucune donnée pour le département {dept} sur la plage.")
    stations = list_stations(df)
    sdf, station = _select_best_station(
        df, stations, lat, lon, start_ts, end_ts, top_n, max_missing
    )

    # Un jour de gel = TN <= 0 °C. TN est en 1/10 °C dans le CSV brut Météo-France ?
    # Vérification : le descriptif dit "en °C et 1/10" → unité = °C avec 1 décimale.
    # Donc TN est déjà en °C (ex: -2.3 = -2.3 °C). Pas de division par 10.
    sdf = sdf.dropna(subset=["TN"]).copy()
    sdf["is_frost"] = sdf["TN"] <= 0
    sdf["year"] = sdf["date"].dt.year
    sdf["month"] = sdf["date"].dt.month
    sdf["day"] = sdf["date"].dt.day

    # Total + moyenne / an.
    total = int(sdf["is_frost"].sum())
    per_year = (
        sdf.groupby("year")
        .agg(frost_days=("is_frost", "sum"), total_days=("is_frost", "size"))
        .reset_index()
    )
    mean_per_year = float(per_year["frost_days"].mean()) if not per_year.empty else 0.0

    # Fréquence par jour de l'année (hors 29 février).
    not_leap = ~((sdf["month"] == 2) & (sdf["day"] == 29))
    doy = sdf[not_leap].groupby(["month", "day"]).agg(
        n_frost=("is_frost", "sum"), n_obs=("is_frost", "size")
    ).reset_index()
    doy["freq"] = doy["n_frost"] / doy["n_obs"]

    # Évolution thermique : moyenne annuelle TN + moyenne DJF (déc-jan-fév).
    is_winter = sdf["month"].isin([12, 1, 2])
    tn_annual = sdf.groupby("year")["TN"].mean().rename("tn_mean_annual")
    tn_winter = sdf[is_winter].groupby("year")["TN"].mean().rename("tn_mean_winter")
    tn_per_year = pd.concat([tn_annual, tn_winter], axis=1).reset_index()

    # Toutes les stations valides du département → altitude vs jours de gel.
    dept_stations = _compute_dept_stations(df, start_ts, end_ts, max_missing)

    return FrostResult(
        commune=commune,
        dept=str(dept).zfill(2),
        start=start_ts,
        end=end_ts,
        station_id=str(station["NUM_POSTE"]),
        station_name=str(station["NOM_USUEL"]),
        station_distance_km=float(station["dist_km"]),
        station_altitude=float(station.get("ALTI", float("nan")) or float("nan")),
        missing_ratio=float(station["missing_ratio"]),
        frost_days_total=total,
        frost_days_per_year_mean=mean_per_year,
        per_year=per_year,
        per_day_of_year=doy,
        tn_per_year=tn_per_year,
        dept_stations=dept_stations,
    )


def _compute_dept_stations(
    df: pd.DataFrame,
    start: pd.Timestamp,
    end: pd.Timestamp,
    max_missing: float,
) -> pd.DataFrame:
    """Pour toutes les stations du département dont la couverture TN est ≥ 65 %,
    renvoie altitude + jours de gel total + jours de gel / an. Sert au graphe altitude × gel."""
    expected = (end - start).days + 1
    df = df[(df["date"] >= start) & (df["date"] <= end)].copy()
    grp = df.groupby("NUM_POSTE")
    rows: list[dict] = []
    for nump, sub in grp:
        n_obs = sub["TN"].notna().sum()
        missing = 1 - n_obs / expected
        if missing > max_missing:
            continue
        alti = sub["ALTI"].dropna().median()
        if pd.isna(alti):
            continue
        n_frost = int((sub["TN"] <= 0).sum())
        # Approx années couvertes par cette station sur la plage.
        n_years = max(n_obs / 365.25, 1e-6)
        rows.append({
            "NUM_POSTE": str(nump),
            "NOM_USUEL": str(sub["NOM_USUEL"].iloc[0]),
            "ALTI": float(alti),
            "frost_days": n_frost,
            "frost_days_per_year": n_frost / n_years,
            "missing_ratio": missing,
        })
    return pd.DataFrame(rows).sort_values("ALTI").reset_index(drop=True)
