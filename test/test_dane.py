"""Grupa A - dane strukturalne: CSV -> JSON i JSON -> CSV."""
import csv
import json
from pathlib import Path

import pytest

from konwerter.converters import ConversionRequest, execute
from konwerter.errors import (
    CorruptedInputFile, EmptyInputFile, InvalidJsonStructure, JsonIsNested,
)

from conftest import SAMPLES


def wczytaj_json(path: Path):
    """Wczytuje wynikowy plik JSON do porównania z oczekiwanymi danymi."""
    return json.loads(path.read_text(encoding="utf-8"))


def wczytaj_csv(path: Path) -> list[list[str]]:
    """Wczytuje plik CSV jako listę wierszy (pierwszy wiersz to nagłówek)."""
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.reader(f))


# ---------------------------------------------------------------- CSV -> JSON: poprawne dane
@pytest.mark.parametrize("plik, oczekiwane", [
    # polskie znaki, kolejność kolumn, liczby zostają tekstem ("007")
    ("csv_przecinek.csv", [
        {"imię": "Łukasz", "nazwisko": "Żółkiewski", "miasto": "Łódź", "numer": "007"},
        {"imię": "Anna", "nazwisko": "Śliwińska", "miasto": "Gdańsk", "numer": "042"},
    ]),
    # średnik jako separator, przecinek wewnątrz wartości
    ("csv_srednik.csv", [
        {"produkt": "jabłko", "cena": "2,50", "ilość": "10"},
        {"produkt": "gruszka", "cena": "3,20", "ilość": "5"},
    ]),
    ("csv_tabulator.csv", [
        {"kod": "PL", "nazwa": "Polska"},
        {"kod": "DE", "nazwa": "Niemcy"},
    ]),
    # BOM nie może trafić do nazwy pierwszej kolumny
    ("csv_bom.csv", [{"imię": "Zofia", "wiek": "30"}]),
    # puste wartości zostają pustymi napisami
    ("csv_puste_wartosci.csv", [
        {"imię": "Jan", "telefon": "", "email": "jan@example.com"},
        {"imię": "Ewa", "telefon": "123456789", "email": ""},
    ]),
    # cudzysłowy: przecinek i nowa linia wewnątrz pola, podwojony cudzysłów
    ("csv_cudzyslowy.csv", [
        {"tytuł": "Raport, wersja 2", "opis": "Pierwsza linia\nDruga linia"},
        {"tytuł": "Cytat", "opis": 'Powiedział "dzień dobry"'},
    ]),
])
def test_csv_do_json(convert, plik, oczekiwane):
    dane = wczytaj_json(convert(plik, ".json"))
    assert dane == oczekiwane
    assert list(dane[0].keys()) == list(oczekiwane[0].keys())  # kolejność kolumn zachowana


# ---------------------------------------------------------------- CSV -> JSON: błędne dane
@pytest.mark.parametrize("plik, wyjatek", [
    ("csv_tylko_naglowek.csv", EmptyInputFile),
    ("csv_pusty.csv", EmptyInputFile),
    ("csv_cp1250.csv", CorruptedInputFile),
])
def test_csv_do_json_bledy(convert, plik, wyjatek):
    with pytest.raises(wyjatek):
        convert(plik, ".json")


# ---------------------------------------------------------------- JSON -> CSV: poprawne dane
@pytest.mark.parametrize("plik, oczekiwane", [
    ("json_lista_obiektow.json", [
        ["imię", "nazwisko", "miasto"],
        ["Łukasz", "Żółkiewski", "Łódź"],
        ["Anna", "Śliwińska", "Gdańsk"],
    ]),
    # nagłówek = suma kluczy w kolejności wystąpienia, brakujące wartości puste
    ("json_rozne_klucze.json", [
        ["imię", "wiek", "miasto"],
        ["Jan", "40", ""],
        ["Ewa", "", "Kraków"],
    ]),
    # pojedynczy obiekt traktowany jak lista z jednym elementem
    ("json_jeden_obiekt.json", [["imię", "wiek"], ["Zofia", "30"]]),
    # liczby jako tekst, null jako pusta wartość
    ("json_typy.json", [["tekst", "liczba", "ułamek", "pusto"], ["zażółć", "28", "3.5", ""]]),
    ("json_bom.json", [["klucz"], ["wartość"]]),
])
def test_json_do_csv(convert, plik, oczekiwane):
    assert wczytaj_csv(convert(plik, ".csv")) == oczekiwane


# ---------------------------------------------------------------- JSON -> CSV: błędne dane
@pytest.mark.parametrize("plik, wyjatek", [
    ("json_pusta_lista.json", EmptyInputFile),
    ("json_zagniezdzony.json", JsonIsNested),
    ("json_lista_w_wartosci.json", JsonIsNested),
    ("json_lista_wartosci.json", InvalidJsonStructure),
    ("json_uszkodzony.json", CorruptedInputFile),
])
def test_json_do_csv_bledy(convert, plik, wyjatek):
    with pytest.raises(wyjatek):
        convert(plik, ".csv")


# ---------------------------------------------------------------- CSV -> JSON -> CSV
def test_csv_json_csv_bez_utraty_danych(tmp_path, convert):
    """Wynik da się ponownie odczytać i po podwójnej konwersji dane są identyczne."""
    json_path = convert("csv_puste_wartosci.csv", ".json")
    powrot_dir = tmp_path / "powrot"
    powrot_dir.mkdir()
    csv_path = execute(ConversionRequest(json_path, ".csv", powrot_dir))

    assert wczytaj_csv(csv_path) == wczytaj_csv(SAMPLES / "csv_puste_wartosci.csv")
