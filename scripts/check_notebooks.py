"""Notebook 確認スクリプト.

目的:
- 9 個の notebook が存在し、nbformat として読み込めることを確認する（既定動作）。
- ``--execute`` を付けると、各 notebook を上から順に実行できるかも確認する。

使い方::

    python scripts/check_notebooks.py            # 存在 + 読み込み確認のみ
    python scripts/check_notebooks.py --execute   # 実行確認も行う

CI では時間短縮のため既定動作（読み込みのみ）を呼ぶ。ローカルでは
``--execute`` で全 notebook が落ちずに最後まで走ることを確認できる。
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import nbformat

# リポジトリルート（このファイルの 1 つ上）を基準にする。
ROOT = Path(__file__).resolve().parents[1]

NOTEBOOKS = [
    "notebooks/00_pde_diffusion_basics.ipynb",
    "notebooks/01_stegosaurus_heat_1d_fin.ipynb",
    "notebooks/02_stegosaurus_shape_comparison.ipynb",
    "notebooks/03_reaction_diffusion_gray_scott.ipynb",
    "notebooks/04_snake_pattern_features.ipynb",
    "notebooks/05_train_boarding_ca.ipynb",
    "notebooks/06_train_boarding_behavior_rules.ipynb",
    "notebooks/07_love_dynamics_two_person.ipynb",
    "notebooks/08_love_dynamics_network.ipynb",
]


def check_exists_and_valid() -> None:
    """全 notebook が存在し、nbformat として妥当か確認する。"""
    for name in NOTEBOOKS:
        path = ROOT / name
        if not path.exists():
            raise FileNotFoundError(f"Missing notebook: {path}")
        nbformat.read(path, as_version=4)
    print(f"OK: {len(NOTEBOOKS)} 個の notebook が存在し、nbformat として妥当です。")


def check_executable(timeout: int = 300) -> None:
    """各 notebook を上から順に実行し、エラーで止まらないか確認する。"""
    from nbclient import NotebookClient

    for name in NOTEBOOKS:
        path = ROOT / name
        nb = nbformat.read(path, as_version=4)
        client = NotebookClient(
            nb,
            timeout=timeout,
            kernel_name="python3",
            resources={"metadata": {"path": str(path.parent)}},
        )
        client.execute()
        print(f"OK (executed): {name}")
    print(f"OK: {len(NOTEBOOKS)} 個の notebook を最後まで実行できました。")


def main() -> int:
    parser = argparse.ArgumentParser(description="Notebook 確認スクリプト")
    parser.add_argument(
        "--execute",
        action="store_true",
        help="notebook を実際に実行して確認する（時間がかかる）",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="セル 1 つあたりの実行タイムアウト秒（--execute 時のみ）",
    )
    args = parser.parse_args()

    check_exists_and_valid()
    if args.execute:
        check_executable(timeout=args.timeout)
    return 0


if __name__ == "__main__":
    sys.exit(main())
