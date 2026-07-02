"""notebook の存在と妥当性を確認する簡単なテスト.

`pytest` で実行する．各 notebook が

1. 存在し，
2. nbformat として読み込め，
3. 対応章へのリンクを冒頭 Markdown セルに含み，
4. 末尾に課題セルを持つ

ことを確認する．実行（セルを走らせる）確認は時間がかかるため，
`scripts/check_notebooks.py --execute` に委ねる．
"""

from __future__ import annotations

from pathlib import Path

import nbformat
import pytest

ROOT = Path(__file__).resolve().parents[1]

NOTEBOOKS = [
    "10_pde_diffusion_basics.ipynb",
    "11_stegosaurus_heat_1d_fin.ipynb",
    "12_stegosaurus_single_plate_2d.ipynb",
    "21_reaction_diffusion_gray_scott.ipynb",
    "22_snake_pattern_features.ipynb",
    "31_train_boarding_ca.ipynb",
    "32_stochastic_simulation_repeats.ipynb",
    "41_love_dynamics_two_person.ipynb",
    "42_love_dynamics_network.ipynb",
]

CHAPTERS = [
    "00_research_design.md",
    "10_pde_foundations.md",
    "20_pattern_foundations.md",
    "30_agent_foundations.md",
    "40_network_foundations.md",
    "11_stegosaurus_heat_basic.md",
    "12_stegosaurus_heat_shape.md",
    "13_stegosaurus_research_roadmap.md",
    "21_reaction_diffusion_basic.md",
    "22_reaction_diffusion_snake.md",
    "23_snake_research_roadmap.md",
    "31_agent_boarding_basic.md",
    "32_agent_boarding_behavior.md",
    "33_boarding_research_roadmap.md",
    "41_love_dynamics_basic.md",
    "42_love_dynamics_network.md",
    "43_love_research_roadmap.md",
    "50_synthesis.md",
    "index.md",
]

INSTRUCTOR_NOTES = [
    "README.md",
    "13_stegosaurus_goal.md",
    "23_snake_goal.md",
    "33_boarding_goal.md",
    "43_love_network_goal.md",
]

NOTEBOOK_FIGURES = [
    "10_pde_stable_diffusion.png",
    "10_pde_stability_comparison.png",
    "11_fin_temperature.png",
    "11_fin_performance.png",
    "12_single_plate_temperature.png",
    "12_plate_h_sensitivity.png",
    "21_gray_scott_pattern.png",
    "21_gray_scott_parameter_comparison.png",
    "22_synthetic_patterns.png",
    "22_pattern_spectra.png",
    "31_boarding_states.png",
    "31_boarding_count_sweep.png",
    "32_bottleneck_trace.png",
    "32_repeat_distribution.png",
    "41_two_person_timeseries.png",
    "41_two_person_phase_portrait.png",
    "42_network_graph.png",
    "42_network_timeseries.png",
    "42_network_stability.png",
]


@pytest.mark.parametrize("name", NOTEBOOKS)
def test_notebook_exists_and_valid(name: str) -> None:
    path = ROOT / "notebooks" / name
    assert path.exists(), f"Missing notebook: {path}"
    nb = nbformat.read(path, as_version=4)
    assert nb.cells, f"Notebook has no cells: {name}"


@pytest.mark.parametrize("name", NOTEBOOKS)
def test_notebook_links_back_to_chapter(name: str) -> None:
    path = ROOT / "notebooks" / name
    nb = nbformat.read(path, as_version=4)
    md_sources = "\n".join(c.source for c in nb.cells if c.cell_type == "markdown")
    assert "../chapters/" in md_sources, f"No chapter link in {name}"


@pytest.mark.parametrize("name", NOTEBOOKS)
def test_notebook_has_exercise_cell(name: str) -> None:
    path = ROOT / "notebooks" / name
    nb = nbformat.read(path, as_version=4)
    sources = "\n".join(c.source for c in nb.cells)
    assert "課題" in sources, f"No exercise/課題 cell in {name}"


@pytest.mark.parametrize("name", CHAPTERS)
def test_chapter_exists(name: str) -> None:
    path = ROOT / "chapters" / name
    assert path.exists(), f"Missing chapter: {path}"


@pytest.mark.parametrize("name", CHAPTERS)
def test_chapter_links_to_notebook(name: str) -> None:
    if name in {
        "index.md",
        "00_research_design.md",
        "20_pattern_foundations.md",
        "30_agent_foundations.md",
        "40_network_foundations.md",
        "13_stegosaurus_research_roadmap.md",
        "23_snake_research_roadmap.md",
        "33_boarding_research_roadmap.md",
        "43_love_research_roadmap.md",
        "50_synthesis.md",
    }:
        pytest.skip("index・準備資料・卒研ロードマップ・振り返りは notebook を持たない")
    path = ROOT / "chapters" / name
    text = path.read_text(encoding="utf-8")
    assert "../notebooks/" in text, f"No notebook link in chapter {name}"


@pytest.mark.parametrize("name", INSTRUCTOR_NOTES)
def test_instructor_note_exists_but_is_hidden_from_toc(name: str) -> None:
    path = ROOT / "instructor_notes" / name
    assert path.exists(), f"Missing instructor note: {path}"

    myst = (ROOT / "myst.yml").read_text(encoding="utf-8")
    active_toc = "\n".join(
        line for line in myst.splitlines() if not line.lstrip().startswith("#")
    )
    assert f"instructor_notes/{name}" not in active_toc, (
        f"Instructor note must stay hidden from active MyST toc: {name}"
    )


@pytest.mark.parametrize("name", NOTEBOOK_FIGURES)
def test_exported_notebook_figure_exists(name: str) -> None:
    path = ROOT / "assets" / "figures" / "notebook" / name
    assert path.exists() and path.stat().st_size > 0, f"Missing notebook figure: {path}"
