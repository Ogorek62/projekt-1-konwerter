import pytest
import subprocess
from pathlib import Path


project_root = Path.cwd()

test_folder = Path("C:/Users/BoGdA/Desktop/pojekt-1-konwerter/samples")

files_to_test = list(test_folder.glob("*.json"))

@pytest.mark.parametrize("file_name", files_to_test)
def test_files(file_name):
    result = subprocess.run(["python", 
                             "-m", 
                             "konwerter", 
                             "-i", file_name , 
                             "-o", f"{file_name.stem}.csv"],
                             cwd=project_root, capture_output=True, text=True)

    print("\nSTDNAME:", file_name)
    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)

    assert result.returncode == 0, (f"skrypt {file_name} zakonczyl sie bledem")