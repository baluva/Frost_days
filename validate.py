"""Validation du pipeline Frost Days contre un jeu de référence.

Compare nos résultats à la vérité-terrain fournie (dossier `validation/`) :
  1. la définition du gel  : `TN <= 0`  doit reproduire la colonne `frost_day` ;
  2. le pipeline complet   : même station retenue + même comptage de jours de gel,
     pour les départements dont le fichier Météo-France est présent en local.

Usage :
    python validate.py
    python validate.py --val-dir chemin/vers/les/csv_de_reference

Les CSV de référence attendus dans `validation/` :
    <Commune>_<dept>_short.csv   (colonnes : station_id, ..., tmin, frost_day, ...)
    city_df_short.csv / stations_df_short.csv  (référentiels, ignorés ici)
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from frost_days.communes import find_commune, load_communes  # noqa: E402
from frost_days.config import METEO_DIR, METEO_FILE_TEMPLATE  # noqa: E402
from frost_days.frost import compute_frost_days  # noqa: E402

# Sortie UTF-8 (la console Windows est en cp1252 par défaut).
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def norm_id(x) -> str:
    """Normalise un NUM_POSTE pour comparaison (la réf perd parfois le 0 de tête)."""
    return str(x).strip().zfill(8)


def dept_file_present(dept: str) -> bool:
    return (METEO_DIR / METEO_FILE_TEMPLATE.format(dept=dept)).exists()


def discover_reference_files(val_dir: Path) -> dict[str, tuple[str, Path]]:
    """{commune: (dept, path)} à partir des `<Commune>_<dept>_short.csv`."""
    out: dict[str, tuple[str, Path]] = {}
    for f in sorted(val_dir.glob("*_*_short.csv")):
        parts = f.stem.rsplit("_", 2)          # [Commune, dept, "short"]
        if len(parts) != 3:
            continue
        commune, dept, tag = parts
        if tag != "short":
            continue
        if not (dept.isdigit() or dept.upper() in {"2A", "2B"}):
            continue                            # exclut city_df_short / stations_df_short
        out[commune] = (dept.zfill(2) if dept.isdigit() else dept.upper(), f)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--val-dir", default=str(ROOT / "validation"),
                    help="Dossier des CSV de référence (défaut : ./validation)")
    args = ap.parse_args()

    val_dir = Path(args.val_dir)
    if not val_dir.exists():
        sys.exit(f"Dossier de référence introuvable : {val_dir}\n"
                 "Place-y les CSV de validation (ex : Paris_75_short.csv).")

    refs = discover_reference_files(val_dir)
    if not refs:
        sys.exit(f"Aucun fichier <Commune>_<dept>_short.csv dans {val_dir}.")

    # ── 1) Définition du gel : frost_day == (tmin <= 0) ? ─────────────────────
    print("=" * 78)
    print("1) DÉFINITION DU GEL   frost_day  ==  (tmin <= 0) ?")
    print("=" * 78)
    summary = {}
    logic_ok = 0
    for commune, (dept, f) in sorted(refs.items()):
        df = pd.read_csv(f)
        df["tmin"] = pd.to_numeric(df["tmin"], errors="coerce")
        recomputed = df["tmin"] <= 0                      # NaN <= 0 -> False (comme la réf)
        ref = df["frost_day"].astype(bool)
        ok = bool((recomputed == ref).all())
        logic_ok += ok
        summary[commune] = {
            "dept": dept, "n": len(df), "n_frost": int(ref.sum()),
            "stations": df["station_id"].astype(str).unique(),
            "d0": df["date"].min(), "d1": df["date"].max(),
        }
        print(f"{commune:22s} ({dept})  {'OK ' if ok else 'KO!'}  | {len(df):5d} j "
              f"| gel réf = {int(ref.sum()):4d} | station(s) {list(summary[commune]['stations'])} "
              f"| {df['date'].min()} → {df['date'].max()}")
    print(f"\n   → définition du gel : {logic_ok}/{len(refs)} exacte")

    # ── 2) Pipeline complet (départements présents en local) ─────────────────
    print("\n" + "=" * 78)
    print("2) PIPELINE COMPLET   (départements dont le .csv.gz est présent en local)")
    print("=" * 78)
    communes_ref = load_communes()
    e2e_total = e2e_match = 0
    for commune, (dept, _f) in sorted(refs.items()):
        info = summary[commune]
        if not dept_file_present(dept):
            print(f"{commune:22s} ({dept})  — fichier météo absent en local "
                  f"(→ python scripts/download_data.py --dept {dept})")
            continue
        try:
            lat, lon = find_commune(communes_ref, commune, dept)
            res = compute_frost_days(commune, dept, lat, lon, info["d0"], info["d1"])
        except Exception as e:
            print(f"{commune:22s} ({dept})  ERREUR : {e}")
            continue
        e2e_total += 1
        ref_ids = {norm_id(s) for s in info["stations"]}
        same_station = norm_id(res.station_id) in ref_ids
        same_count = res.frost_days_total == info["n_frost"]
        e2e_match += same_station and same_count
        verdict = "✅ IDENTIQUE" if (same_station and same_count) else "⚠️  DIFFÉRENT"
        print(f"{commune:22s} ({dept})  {verdict}")
        print(f"    station   réf {list(info['stations'])}  |  nous {res.station_id} "
              f"({res.station_name})  → {'même' if same_station else 'autre dépt/poste'}")
        print(f"    gel total réf {info['n_frost']:4d}  |  nous {res.frost_days_total:4d} "
              f"(Δ {res.frost_days_total - info['n_frost']:+d})  | couverture {1-res.missing_ratio:.0%}")

    # ── Bilan ────────────────────────────────────────────────────────────────
    print("\n" + "=" * 78)
    print(f"BILAN  ·  définition gel : {logic_ok}/{len(refs)}  "
          f"·  pipeline e2e : {e2e_match}/{e2e_total} identiques "
          f"(sur {e2e_total} départements testés en local)")
    print("=" * 78)


if __name__ == "__main__":
    main()
