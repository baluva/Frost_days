"""Sélection des stations météo les plus proches d'une commune via Haversine.

La distance grand-cercle est calculée avec la bibliothèque `haversine`
(https://pypi.org/project/haversine/), et non une formule réimplémentée à la main.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from haversine import Unit, haversine_vector


def haversine_km(lat1: float, lon1: float, lat2: np.ndarray, lon2: np.ndarray) -> np.ndarray:
    """Distance grand-cercle (km) entre 1 point et N points, via la lib `haversine`.

    Vectorisé : on répète l'origine `(lat1, lon1)` autant de fois qu'il y a de
    stations, puis `haversine_vector` calcule les N distances en un seul appel.
    """
    lat2 = np.atleast_1d(np.asarray(lat2, dtype=float))
    lon2 = np.atleast_1d(np.asarray(lon2, dtype=float))
    origin = [(lat1, lon1)] * len(lat2)          # (lat, lon) répété N fois
    targets = list(zip(lat2, lon2))              # [(lat, lon), ...] des stations
    return np.asarray(haversine_vector(origin, targets, Unit.KILOMETERS))


def nearest_stations(
    stations: pd.DataFrame, lat: float, lon: float, top_n: int = 5
) -> pd.DataFrame:
    """Renvoie les `top_n` stations les plus proches du point (lat, lon)."""
    dists = haversine_km(lat, lon, stations["LAT"].to_numpy(), stations["LON"].to_numpy())
    out = stations.copy()
    out["dist_km"] = dists
    return out.nsmallest(top_n, "dist_km").reset_index(drop=True)
