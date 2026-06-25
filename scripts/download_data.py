"""Télécharge le référentiel communes + un ou plusieurs départements Météo-France."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Permet d'exécuter depuis la racine sans installer le package.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from frost_days.communes import download_communes  # noqa: E402
from frost_days.data_loader import download_dept  # noqa: E402


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--dept", nargs="+", required=True, help="Codes département (ex: 21 75 2A)")
    p.add_argument("--latest", action="store_true", help="Aussi télécharger 2024-2025")
    args = p.parse_args()

    print("[1/2] Référentiel communes…")
    path = download_communes()
    print(f"      OK -> {path}")

    print("[2/2] Données Météo-France par département…")
    for dept in args.dept:
        path = download_dept(dept)
        print(f"      OK -> {path}")
        if args.latest:
            path = download_dept(dept, latest=True)
            print(f"      OK -> {path}")


if __name__ == "__main__":
    main()
