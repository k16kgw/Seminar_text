"""編集用PowerPointからMyST本文用の概念図PNGを書き出す．

macOSのKeynoteでPowerPointをPDFへ変換し，pdftoppmで各ページをPNGへ
変換する．1枚目は表紙であり，2枚目以降を概念図名へ対応づける．
"""

from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
CONCEPT_DIR = ROOT / "assets" / "figures" / "concepts"
POWERPOINT = CONCEPT_DIR / "concept_diagrams_editable.pptx"

SLIDES = {
    2: "learning_path.png",
    3: "research_cycle.png",
    4: "pde_five_point_stencil.png",
    5: "reaction_diffusion_parts.png",
    6: "agent_update_modes.png",
    7: "network_matrix_graph.png",
    8: "fin_heat_balance.png",
    9: "plate_boundary_conditions.png",
    10: "pattern_measurements.png",
    11: "boarding_space_rules.png",
    12: "repeated_simulation.png",
    13: "two_person_coupling.png",
    14: "heat_research_pipeline.png",
    15: "pattern_research_pipeline.png",
    16: "boarding_research_pipeline.png",
    17: "relation_research_pipeline.png",
    18: "cross_theme_transfer.png",
}


def require_command(name: str) -> None:
    if shutil.which(name) is None:
        raise RuntimeError(f"必要なコマンドが見つからない: {name}")


def export_pdf(pdf_path: Path) -> None:
    keynote = Path("/Applications/Keynote.app")
    if not keynote.exists():
        raise RuntimeError("Keynoteがインストールされていない")
    input_path = str(POWERPOINT.resolve())
    output_path = str(pdf_path.resolve())
    subprocess.run(
        [
            "osascript",
            "-e",
            'tell application "Keynote"',
            "-e",
            f'set docRef to open POSIX file "{input_path}"',
            "-e",
            f'export docRef to POSIX file "{output_path}" as PDF',
            "-e",
            "close docRef saving no",
            "-e",
            "end tell",
        ],
        check=True,
    )


def main() -> None:
    require_command("osascript")
    require_command("pdftoppm")
    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "build_concept_diagrams_pptx.py")],
        check=True,
        cwd=ROOT,
    )

    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        pdf_path = tmpdir / "concept_diagrams.pdf"
        export_pdf(pdf_path)
        prefix = tmpdir / "slide"
        subprocess.run(
            ["pdftoppm", "-png", "-r", "180", str(pdf_path), str(prefix)],
            check=True,
        )
        pages = sorted(tmpdir.glob("slide-*.png"))
        if len(pages) != 18:
            raise RuntimeError(f"想定外のスライド数: {len(pages)}")
        for number, output_name in SLIDES.items():
            shutil.copy2(pages[number - 1], CONCEPT_DIR / output_name)
            print(f"Saved: assets/figures/concepts/{output_name}")

    print(f"OK: exported {len(SLIDES)} concept diagrams")


if __name__ == "__main__":
    main()
