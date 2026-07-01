"""notebook の存在と妥当性を確認する簡単なテスト.

`pytest` で実行する。各 notebook が

1. 存在し、
2. nbformat として読み込め、
3. 対応章へのリンクを冒頭 Markdown セルに含み、
4. 末尾に「課題」セルを持つ

ことを確認する。実行（セルを走らせる）確認は時間がかかるため、
`scripts/check_notebooks.py --execute` に委ねる。
"""

from __future__ import annotations

from pathlib import Path

import nbformat
import pytest

ROOT = Path(__file__).resolve().parents[1]

NOTEBOOKS = [
    "00_pde_diffusion_basics.ipynb",
    "01_stegosaurus_heat_1d_fin.ipynb",
    "02_stegosaurus_shape_comparison.ipynb",
    "03_reaction_diffusion_gray_scott.ipynb",
    "04_snake_pattern_features.ipynb",
    "05_train_boarding_ca.ipynb",
    "06_train_boarding_behavior_rules.ipynb",
    "07_love_dynamics_two_person.ipynb",
    "08_love_dynamics_network.ipynb",
]

CHAPTERS = [
    "00_research_design.md",
    "00_pde_foundations.md",
    "01_stegosaurus_heat_basic.md",
    "02_stegosaurus_heat_shape.md",
    "03_reaction_diffusion_basic.md",
    "04_reaction_diffusion_snake.md",
    "05_agent_boarding_basic.md",
    "06_agent_boarding_behavior.md",
    "07_love_dynamics_basic.md",
    "08_love_dynamics_network.md",
    "09_synthesis.md",
    "index.md",
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
    if name in {"index.md", "00_research_design.md", "09_synthesis.md"}:
        pytest.skip("index・研究設計・振り返りは notebook を持たない")
    path = ROOT / "chapters" / name
    text = path.read_text(encoding="utf-8")
    assert "../notebooks/" in text, f"No notebook link in chapter {name}"
