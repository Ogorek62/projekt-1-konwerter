"""Wspólne elementy testów - pytest wczytuje ten plik automatycznie."""
from pathlib import Path

import pytest

from konwerter.converters import ConversionRequest, execute

SAMPLES = Path(__file__).resolve().parent.parent / "samples"


@pytest.fixture
def convert(tmp_path):
    """Konwertuje plik z samples/ do tymczasowego katalogu testu i zwraca ścieżkę wyniku.

    Użycie w teście: wynik = convert("csv_przecinek.csv", ".json")
    """
    def _convert(name: str, target: str) -> Path:
        return execute(ConversionRequest(SAMPLES / name, target, tmp_path))
    return _convert
