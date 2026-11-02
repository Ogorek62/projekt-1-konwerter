"""Grupa B (TXT/DOCX) i grupa C (DOCX/ODT -> PDF przez LibreOffice)."""
from pathlib import Path

import pytest
from docx import Document
from pypdf import PdfReader

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


def tekst_pdf(path: Path) -> str:
    """Wyciąga tekst ze wszystkich stron PDF.

    PdfReader rzuca wyjątek, jeśli plik nie jest poprawnym PDF - więc samo
    wczytanie sprawdza też, że wynik da się otworzyć.
    """
    reader = PdfReader(path)
    return "\n".join(page.extract_text() for page in reader.pages)


# ---------------------------------------------------------------- Grupa B: poprawne dane
def test_txt_do_docx_zachowuje_akapity(convert):
    wynik = convert("txt_dokument.txt", ".docx")
    akapity = [p.text for p in Document(str(wynik)).paragraphs]
    # każda linia = osobny akapit, łącznie z pustą linią i wcięciem
    assert akapity == (SAMPLES / "txt_dokument.txt").read_text(encoding="utf-8").splitlines()


def test_txt_do_pdf_zachowuje_tresc(convert):
    wynik = tekst_pdf(convert("txt_dokument.txt", ".pdf"))
    zrodlo = (SAMPLES / "txt_dokument.txt").read_text(encoding="utf-8")
    # każda niepusta linia trafia do PDF z polskimi znakami i wcięciem
    # (puste linie w PDF są tylko odstępem, więc pypdf ich nie zwraca)
    assert wynik.splitlines() == [linia for linia in zrodlo.splitlines() if linia.strip()]


def test_txt_do_pdf_zawija_dluga_linie(convert):
    wynik = tekst_pdf(convert("txt_dluga_linia.txt", ".pdf"))
    zrodlo = (SAMPLES / "txt_dluga_linia.txt").read_text(encoding="utf-8")
    assert len(wynik.splitlines()) > 1                  # linia została zawinięta...
    assert " ".join(wynik.split()) == " ".join(zrodlo.split())  # ...i nic nie zostało ucięte


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


@pytest.mark.parametrize("cel", [".txt", ".pdf"])
def test_uszkodzony_docx(convert, cel):
    # Dla .pdf błąd pojawia się przed wywołaniem LibreOffice, więc test nie wymaga jego instalacji.
    with pytest.raises(CorruptedInputFile):
        convert("docx_uszkodzony.docx", cel)


# ---------------------------------------------------------------- Grupa C: LibreOffice
@wymaga_libreoffice
@pytest.mark.parametrize("plik", ["docx_dokument.docx", "odt_dokument.odt"])
def test_dokument_biurowy_do_pdf(convert, plik):
    wynik = tekst_pdf(convert(plik, ".pdf"))
    # Sprawdzamy tylko fragmenty bez polskich liter: LibreOffice osadza czcionkę bez
    # tabeli ToUnicode, przez co pypdf błędnie odczytuje znaki diakrytyczne
    # (to ograniczenie odczytu w teście, nie konwersji).
    assert "Dokument testowy" in wynik
    assert "akapit" in wynik
