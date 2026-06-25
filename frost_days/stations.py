"""Sélection des stations météo les plus proches d'une commune via Haversine."""
from __future__ import annotations

import numpy as np
import pandas as pd

EARTH_RADIUS_KM = 6371.0088


def haversine_km(lat1: float, lon1: float, lat2: np.ndarray, lon2: np.ndarray) -> np.ndarray:
    """Distance grand-cercle (km) entre 1 point et N points. Vectorisé."""
    lat1r = np.radians(lat1)
    lon1r = np.radians(lon1)
    lat2r = np.radians(lat2)
    lon2r = np.radians(lon2)
    dlat = lat2r - lat1r
    dlon = lon2r - lon1r
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1r) * np.cos(lat2r) * np.sin(dlon / 2) ** 2
    return 2 * EARTH_RADIUS_KM * np.arcsin(np.sqrt(a))


def nearest_stations(
    stations: pd.DataFrame, lat: float, lon: float, top_n: int = 5
) -> pd.DataFrame:
    """Renvoie les `top_n` stations les plus proches du point (lat, lon)."""
    dists = haversine_km(lat, lon, stations["LAT"].to_numpy(), stations["LON"].to_numpy())
    out = stations.copy()
    out["dist_km"] = dists
    return out.nsmallest(top_n, "dist_km").reset_index(drop=True)
