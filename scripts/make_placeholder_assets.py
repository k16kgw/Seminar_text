"""プレースホルダー画像・データ生成スクリプト.

第4章（ヘビ模様の反応拡散 II）の notebook は、外部画像がなくても動く。
このスクリプトは、`assets/data/` に差し替え用のサンプル模様画像を作っておきたい
場合に使う。実行は任意であり、教材本体の動作には必須ではない。

使い方::

    python scripts/make_placeholder_assets.py

生成物:
- assets/data/sample_snake_pattern.png : 反応拡散風の擬似ヘビ模様（グレースケール）
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "assets" / "data"


def make_sample_pattern(size: int = 200, seed: int = 0) -> np.ndarray:
    """斑点状の擬似模様を生成する（0-1 のグレースケール）。"""
    rng = np.random.default_rng(seed)
    y, x = np.mgrid[0:size, 0:size]
    field = np.zeros((size, size), dtype=float)
    # ランダムな位置にガウシアン斑点を重ねる。
    for _ in range(40):
        cy, cx = rng.integers(0, size, size=2)
        r2 = (x - cx) ** 2 + (y - cy) ** 2
        field += np.exp(-r2 / (2.0 * (size * 0.04) ** 2))
    field = field / field.max()
    return field


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    pattern = make_sample_pattern()

    # matplotlib は import が重いので、ここでだけ読み込む。
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    out_path = DATA_DIR / "sample_snake_pattern.png"
    plt.imsave(out_path, pattern, cmap="gray")
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()
