"""Testy rejestru konwerterów: available_targets(), ConversionRequest.validate(),
polityki nadpisywania w execute() oraz wykrywania braku LibreOffice."""
from pathlib import Path

import pytest

from konwerter import converters
from konwerter.converters import ConversionRequest, available_targets, execute
from konwerter.errors import TargetExists

from conftest import SAMPLES


# ---------------------------------------------------------------- available_targets()
@pytest.mark.parametrize("plik, oczekiwane", [
    ("a.csv", [".json"]),
    ("a.json", [".csv"]),
    ("a.txt", [".docx", ".pdf"]),
    ("a.docx", [".pdf", ".txt"]),
    ("a.odt", [".pdf"]),
    ("A.CSV", [".json"]),   # wielkość liter rozszerzenia nie ma znaczenia
    ("a.xyz", []),          # nieobsługiwany format -> brak opcji w GUI
    ("bez_rozszerzenia", []),
])
def test_available_targets(plik, oczekiwane):
    assert available_targets(Path(plik)) == oczekiwane


# ---------------------------------------------------------------- validate()
def test_validate_poprawne_zadanie(tmp_path):
    ConversionRequest(SAMPLES / "csv_przecinek.csv", ".json", tmp_path).validate()


def test_validate_brak_pliku(tmp_path):
    with pytest.raises(FileNotFoundError):
        ConversionRequest(SAMPLES / "nie_istnieje.csv", ".json", tmp_path).validate()


def test_validate_brak_katalogu(tmp_path):
    with pytest.raises(NotADirectoryError):
        ConversionRequest(SAMPLES / "csv_przecinek.csv", ".json", tmp_path / "brak").validate()


def test_validate_nieobslugiwana_para(tmp_path):
    with pytest.raises(ValueError, match="Nieobsługiwana konwersja"):
        ConversionRequest(SAMPLES / "csv_przecinek.csv", ".pdf", tmp_path).validate()


def test_validate_pusty_format_docelowy(tmp_path):
    with pytest.raises(ValueError, match="formatu docelowego"):
        ConversionRequest(SAMPLES / "csv_przecinek.csv", "", tmp_path).validate()


def test_validate_plik_docelowy_istnieje(tmp_path):
    (tmp_path / "csv_przecinek.json").write_text("stara zawartość", encoding="utf-8")
    request = ConversionRequest(SAMPLES / "csv_przecinek.csv", ".json", tmp_path)
    with pytest.raises(TargetExists):
        request.validate()
    # po potwierdzeniu nadpisania walidacja przechodzi
    ConversionRequest(SAMPLES / "csv_przecinek.csv", ".json", tmp_path, overwrite=True).validate()


# ---------------------------------------------------------------- execute() - nadpisywanie
def test_execute_nie_nadpisuje_bez_zgody(tmp_path):
    request = ConversionRequest(SAMPLES / "csv_przecinek.csv", ".json", tmp_path)
    wynik = execute(request)
    wynik.write_text("zmieniony", encoding="utf-8")

    with pytest.raises(TargetExists):
        execute(request)
    assert wynik.read_text(encoding="utf-8") == "zmieniony"  # plik nietknięty

    execute(ConversionRequest(SAMPLES / "csv_przecinek.csv", ".json", tmp_path, overwrite=True))
    assert wynik.read_text(encoding="utf-8") != "zmieniony"  # nadpisany po zgodzie


# ---------------------------------------------------------------- brak LibreOffice
def test_brak_libreoffice_daje_kontrolowany_blad(monkeypatch, tmp_path):
    """Symulujemy system bez LibreOffice: brak w PATH i w typowych katalogach."""
    request = ConversionRequest(SAMPLES / "docx_dokument.docx", ".pdf", tmp_path)
    with monkeypatch.context() as m:
        m.setattr(converters.shutil, "which", lambda name: None)
        m.setattr(converters.Path, "exists", lambda self: False)
        with pytest.raises(RuntimeError, match="LibreOffice"):
            execute(request)
