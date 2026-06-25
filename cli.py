"""Frost Days -- interface ligne de commande."""
from __future__ import annotations

import argparse
import io
import sys

from frost_days.communes import find_commune, load_communes
from frost_days.config import DEFAULT_END, DEFAULT_START
from frost_days.frost import compute_frost_days

# Force UTF-8 sur la sortie Windows (cp1252 par défaut ne gère pas ≈, →, etc.).
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def main() -> None:
    p = argparse.ArgumentParser(description="Calcule les jours de gel pour une commune.")
    p.add_argument("--commune", required=True)
    p.add_argument("--dept", required=True)
    p.add_argument("--debut", default=DEFAULT_START)
    p.add_argument("--fin", default=DEFAULT_END)
    args = p.parse_args()

    communes = load_communes()
    lat, lon = find_commune(communes, args.commune, args.dept)
    res = compute_frost_days(args.commune, args.dept, lat, lon, args.debut, args.fin)

    print(f"\nCommune : {res.commune} ({res.dept})  ->  ({lat:.4f}, {lon:.4f})")
    print(f"Station retenue : {res.station_name} [{res.station_id}]"
          f"  distance ~ {res.station_distance_km:.1f} km"
          f"  | NaN sur TN : {res.missing_ratio:.1%}")
    print(f"Periode : {res.start.date()} -> {res.end.date()}")
    print(f"\n- Jours de gel total       : {res.frost_days_total}")
    print(f"- Moyenne par annee        : {res.frost_days_per_year_mean:.1f}")

    print("\nPar annee :")
    print(res.per_year.to_string(index=False))

    print("\nTop 10 jours-de-l'annee les plus gelifs :")
    top = res.per_day_of_year.sort_values("freq", ascending=False).head(10)
    top = top.assign(jour=top.apply(lambda r: f"{int(r['day']):02d}/{int(r['month']):02d}", axis=1))
    print(top[["jour", "n_frost", "n_obs", "freq"]].to_string(index=False))


if __name__ == "__main__":
    main()
