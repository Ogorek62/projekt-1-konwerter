import subprocess
import sys
from pathlib import Path

import pytest

project_root = Path.cwd()
samples_dir = project_root / "samples"
output_dir = project_root / "output"

SUPPORTED = [
    (".csv", ".json"),
    (".json", ".csv"),
    (".txt", ".docx"),
    (".txt", ".pdf"),
    (".docx", ".txt"),
    (".docx", ".pdf"),
]


def build_cases():
    cases = []
    for src_file in sorted(samples_dir.iterdir()):
        if not src_file.is_file():
            continue
        for src_ext, dst_ext in SUPPORTED:
            if src_file.suffix.lower() == src_ext:
                cases.append(
                    pytest.param(src_file, dst_ext, id=f"{src_file.name}->{dst_ext}")
                )
    return cases


@pytest.mark.parametrize("src_file, dst_ext", build_cases())
def test_conversion(src_file, dst_ext):
    output_dir.mkdir(exist_ok=True)
    expected = output_dir / f"{src_file.stem}{dst_ext}"
    expected.unlink(missing_ok=True) 

    result = subprocess.run(
        [sys.executable, "-m", "konwerter",
         "-i", src_file.name,
         "-o", f"{src_file.stem}{dst_ext}"],
        cwd=project_root, capture_output=True, text=True,
    )

    assert result.returncode == 0, (
        f"NIE UDAŁO SIĘ: {src_file.name} -> {dst_ext}\n{result.stderr}"
    )
    assert expected.exists(), (
        f"NIE UDAŁO SIĘ: {src_file.name} -> {dst_ext} (program nie utworzył pliku w output/)"
    )