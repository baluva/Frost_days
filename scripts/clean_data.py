"""Nettoie les fichiers bruts Météo-France → data/cleaned/.

Traitement appliqué à chaque `Q_<dept>_previous-1950-2024_RR-T-Vent.csv.gz` :
  1. on ne garde que les **7 colonnes utiles** sur 60 (cf. notebook 02, § 1 bis) ;
  2. on **supprime les lignes sans température** (`TN` manquante) — les relevés
     inexploitables pour le gel (pluviomètres sans thermomètre, jours non mesurés) ;
  3. on dérive `frost_day = (tmin <= 0)`, plus `date`, `year`, `month`, `day` ;
  4. on renomme au schéma de référence et on écrit `data/cleaned/<dept>_clean.csv`.

Usage :
    python scripts/clean_data.py              # tous les départements présents
    python scripts/clean_data.py --dept 21 75 # une sélection
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from frost_days.config import METEO_DIR  # noqa: E402

CLEANED_DIR = METEO_DIR.parent / "cleaned"
USECOLS = ["NUM_POSTE", "NOM_USUEL", "LAT", "LON", "ALTI", "AAAAMMJJ", "TN"]
RENAME = {
    "NUM_POSTE": "station_id", "NOM_USUEL": "station_name",
    "LAT": "latitude", "LON": "longitude", "ALTI": "alti", "TN": "tmin",
}
FINAL_COLS = ["station_id", "station_name", "latitude", "longitude", "alti",
              "date", "tmin", "frost_day", "year", "month", "day"]


def clean_one(path: Path) -> tuple[pd.DataFrame, int]:
    """Renvoie (DataFrame nettoyé, nombre de lignes brutes lues)."""
    raw_total = 0
    kept: list[pd.DataFrame] = []
    reader = pd.read_csv(
        path, sep=";", compression="gzip", usecols=USECOLS,
        dtype={"NUM_POSTE": str, "NOM_USUEL": str}, chunksize=500_000, low_memory=False,
    )
    for chunk in reader:
        raw_total += len(chunk)
        chunk["TN"] = pd.to_numeric(chunk["TN"], errors="coerce")
        chunk = chunk.dropna(subset=["TN"])           # ← on jette les relevés sans température
        if not chunk.empty:
            kept.append(chunk)

    if not kept:
        return pd.DataFrame(columns=FINAL_COLS), raw_total

    df = pd.concat(kept, ignore_index=True)
    for c in ("LAT", "LON", "ALTI"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["date"] = pd.to_datetime(df["AAAAMMJJ"].astype(int).astype(str), format="%Y%m%d")
    df["frost_day"] = df["TN"] <= 0
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["day"] = df["date"].dt.day
    df = df.rename(columns=RENAME)
    df["date"] = df["date"].dt.strftime("%Y-%m-%d")
    df = df[FINAL_COLS].sort_values(["station_id", "date"]).reset_index(drop=True)
    return df, raw_total


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dept", nargs="+", help="Codes département (défaut : tous ceux présents)")
    args = ap.parse_args()

    files = sorted(METEO_DIR.glob("Q_*_previous-*_RR-T-Vent.csv.gz"))
    if args.dept:
        wanted = {d.zfill(2) if d.isdigit() else d.upper() for d in args.dept}
        files = [f for f in files if re.search(r"Q_([0-9AB]+)_", f.name).group(1) in wanted]
    if not files:
        sys.exit("Aucun fichier brut trouvé dans data/meteo/.")

    CLEANED_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Nettoyage de {len(files)} département(s) → {CLEANED_DIR}\n")
    print(f"{'dept':<5} {'lignes brutes':>14} {'lignes propres':>15} "
          f"{'% gardé':>8} {'stations':>9} {'jours gel':>10}  période")
    print("-" * 82)

    summary = []
    for f in files:
        dept = re.search(r"Q_([0-9AB]+)_", f.name).group(1)
        df, raw_total = clean_one(f)
        out = CLEANED_DIR / f"{dept}_clean.csv"
        df.to_csv(out, index=False, encoding="utf-8")
        pct = 100 * len(df) / raw_total if raw_total else 0
        n_st = df["station_id"].nunique()
        n_frost = int(df["frost_day"].sum())
        d0, d1 = (df["date"].min(), df["date"].max()) if len(df) else ("—", "—")
        print(f"{dept:<5} {raw_total:>14,} {len(df):>15,} {pct:>7.1f}% "
              f"{n_st:>9} {n_frost:>10,}  {d0} → {d1}")
        summary.append({"dept": dept, "lignes_brutes": raw_total, "lignes_propres": len(df),
                        "pct_garde": round(pct, 1), "n_stations": n_st, "jours_gel": n_frost,
                        "debut": d0, "fin": d1, "fichier": out.name})

    pd.DataFrame(summary).to_csv(CLEANED_DIR / "_SUMMARY.csv", index=False, encoding="utf-8")
    print("-" * 82)
    print(f"OK · {len(files)} fichiers écrits + _SUMMARY.csv dans {CLEANED_DIR}")


if __name__ == "__main__":
    main()
