from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from hw_2.latex_table import render_image_block, render_table_document

ASSETS_DIR = Path(__file__).parent / "assets"
ARTIFACTS_DIR = Path(__file__).parent / "artifacts"


def main() -> None:
    data = [
        ["", "$0$", r"$\frac{\pi}{6}$", r"$\frac{\pi}{4}$", r"$\frac{\pi}{3}$", r"$\frac{\pi}{2}$"],
        ["sin", "0.0000", "0.5000", "0.7071", "0.8660", "1.0000"],
        ["cos", "1.0000", "0.8660", "0.7071", "0.5000", "0.0000"],
        ["tan", "0.0000", "0.5774", "1.0000", "1.7321", "---"],
        ["cot", "---", "1.7321", "1.0000", "0.5774", "0.0000"],
    ]

    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    image_name = copy_sample_image(ARTIFACTS_DIR)

    figure = render_image_block(
        image_name,
        caption="Sample PNG image",
        label="fig:sample",
        width=r"0.4\textwidth",
    )
    document = render_table_document(
        data,
        caption="Trigonometry table",
        label="tab:trig",
        extra_blocks=figure,
    )

    tex_path = ARTIFACTS_DIR / "table_artifact.tex"
    tex_path.write_text(document, encoding="utf-8")
    print(f"LaTeX table saved to {tex_path}")

    pdf_path = compile_pdf(tex_path)
    if pdf_path:
        print(f"PDF saved to {pdf_path}")
    else:
        print("PDF compilation skipped: install pdflatex or tectonic if you need local PDF.")


def copy_sample_image(target_dir: Path) -> str:
    source = ASSETS_DIR / "sample.png"
    if not source.exists():
        raise FileNotFoundError(f"Sample image not found at {source}")
    destination = target_dir / source.name
    shutil.copy(source, destination)
    return source.name


def compile_pdf(tex_path: Path) -> Path | None:
    tex_path = tex_path.resolve()
    out_dir = tex_path.parent
    pdf_path = out_dir / (tex_path.stem + ".pdf")

    def run_command(cmd: list[str]) -> bool:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print("LaTeX compiler output:\n", result.stdout, result.stderr)
            return False
        return True

    pdflatex = shutil.which("pdflatex")
    if pdflatex:
        command = [pdflatex, "-interaction=nonstopmode", f"-output-directory={out_dir}", str(tex_path)]
        if run_command(command) and pdf_path.exists():
            return pdf_path

    tectonic = shutil.which("tectonic")
    if tectonic:
        command = [tectonic, "-o", str(out_dir), str(tex_path)]
        if run_command(command) and pdf_path.exists():
            return pdf_path

    return None


if __name__ == "__main__":
    main()
