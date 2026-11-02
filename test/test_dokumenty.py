"""Grupa B (TXT/DOCX) i grupa C (DOCX/ODT -> PDF przez LibreOffice)."""
from pathlib import Path

import pytest
from docx import Document

from konwerter.converters import find_office
from konwerter.errors import CorruptedInputFile

from conftest import SAMPLES


def libreoffice_zainstalowany() -> bool:
    try:
        find_office()
        return True
    except RuntimeError:
        return False


wymaga_libreoffice = pytest.mark.skipif(
    not libreoffice_zainstalowany(), reason="LibreOffice nie jest zainstalowany"
)


def to_jest_pdf(path: Path) -> bool:
    return path.read_bytes().startswith(b"%PDF")


# ---------------------------------------------------------------- Grupa B: poprawne dane
def test_txt_do_docx_zachowuje_akapity(convert):
    wynik = convert("txt_dokument.txt", ".docx")
    akapity = [p.text for p in Document(str(wynik)).paragraphs]
    # każda linia = osobny akapit, łącznie z pustą linią i wcięciem
    assert akapity == (SAMPLES / "txt_dokument.txt").read_text(encoding="utf-8").splitlines()


@pytest.mark.parametrize("plik", ["txt_dokument.txt", "txt_dluga_linia.txt"])
def test_txt_do_pdf(convert, plik):
    assert to_jest_pdf(convert(plik, ".pdf"))


def test_docx_do_txt(convert):
    wynik = convert("docx_dokument.docx", ".txt")
    assert wynik.read_text(encoding="utf-8") == (
        "Dokument testowy\nZażółć gęślą jaźń\n\nTrzeci akapit: ĄĆĘŁŃÓŚŹŻ"
    )


# ---------------------------------------------------------------- Grupa B: błędne dane
@pytest.mark.parametrize("cel", [".docx", ".pdf"])
def test_txt_w_cp1250_daje_czytelny_blad(convert, cel):
    with pytest.raises(CorruptedInputFile, match="UTF-8"):
        convert("txt_cp1250.txt", cel)


def test_uszkodzony_docx(convert):
    with pytest.raises(CorruptedInputFile):
        convert("docx_uszkodzony.docx", ".txt")


# ---------------------------------------------------------------- Grupa C: LibreOffice
@wymaga_libreoffice
@pytest.mark.parametrize("plik", ["docx_dokument.docx", "odt_dokument.odt"])
def test_dokument_biurowy_do_pdf(convert, plik):
    assert to_jest_pdf(convert(plik, ".pdf"))
