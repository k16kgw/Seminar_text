"""Executed notebook outputsから学生用章へ掲載する代表図を書き出す．

Notebookを先に実行し，各セルの ``image/png`` 出力を
``assets/figures/notebook/`` へ保存する．図の選定はセルIDで固定し，
Notebookの再実行後も同じファイル名で章から参照できるようにする．
"""

from __future__ import annotations

import base64
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "assets" / "figures" / "notebook"

EXPORTS: dict[str, list[tuple[str, str]]] = {
    "10_pde_diffusion_basics.ipynb": [
        ("stable-code", "10_pde_stable_diffusion.png"),
        ("unstable-code", "10_pde_stability_comparison.png"),
    ],
    "20_pattern_foundations.ipynb": [
        ("comparison", "20_reaction_diffusion_separation.png"),
    ],
    "30_agent_foundations.ipynb": [
        ("update-comparison", "30_update_comparison.png"),
        ("random-trials", "30_random_conflicts.png"),
    ],
    "40_network_foundations.ipynb": [
        ("network-representation", "40_graph_matrix.png"),
        ("one-step", "40_one_step_update.png"),
    ],
    "11_stegosaurus_heat_1d_fin.ipynb": [
        ("fin-temperature", "11_fin_temperature.png"),
        ("fin-performance", "11_fin_performance.png"),
    ],
    "12_stegosaurus_single_plate_2d.ipynb": [
        ("visualization", "12_single_plate_temperature.png"),
        ("parameter", "12_plate_h_sensitivity.png"),
    ],
    "21_reaction_diffusion_gray_scott.ipynb": [
        ("gray-scott-pattern", "21_gray_scott_pattern.png"),
        ("gray-scott-comparison", "21_gray_scott_parameter_comparison.png"),
    ],
    "22_snake_pattern_features.ipynb": [
        ("patterns", "22_synthetic_patterns.png"),
        ("spectrum", "22_pattern_spectra.png"),
    ],
    "31_train_boarding_ca.ipynb": [
        ("boarding-states", "31_boarding_states.png"),
        ("boarding-count-sweep", "31_boarding_count_sweep.png"),
    ],
    "32_stochastic_simulation_repeats.ipynb": [
        ("trace", "32_bottleneck_trace.png"),
        ("distribution", "32_repeat_distribution.png"),
    ],
    "41_love_dynamics_two_person.ipynb": [
        ("solve", "41_two_person_timeseries.png"),
        ("phase", "41_two_person_phase_portrait.png"),
    ],
    "42_love_dynamics_network.ipynb": [
        ("graph", "42_network_graph.png"),
        ("simulation", "42_network_timeseries.png"),
        ("coupling", "42_network_stability.png"),
    ],
}


def first_png_output(cell: dict) -> str:
    """セルの最初のPNG出力をbase64文字列として返す．"""
    for output in cell.get("outputs", []):
        png = output.get("data", {}).get("image/png")
        if png:
            return "".join(png) if isinstance(png, list) else png
    raise ValueError(f"No image/png output in cell id={cell.get('id')}")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    exported = 0
    for notebook_name, specs in EXPORTS.items():
        path = ROOT / "notebooks" / notebook_name
        notebook = json.loads(path.read_text(encoding="utf-8"))
        cells = {cell.get("id"): cell for cell in notebook["cells"]}
        for cell_id, output_name in specs:
            if cell_id not in cells:
                raise KeyError(f"Missing cell id={cell_id} in {notebook_name}")
            png_data = first_png_output(cells[cell_id])
            output_path = OUTPUT_DIR / output_name
            output_path.write_bytes(base64.b64decode(png_data))
            print(f"Saved: {output_path.relative_to(ROOT)}")
            exported += 1
    print(f"OK: exported {exported} notebook figures")


if __name__ == "__main__":
    main()
