"""Logika konwersji plików.

Każda funkcja konwertująca jest rejestrowana dekoratorem @converter w słowniku
REGISTRY pod kluczem (rozszerzenie_źródłowe, rozszerzenie_docelowe). GUI i testy
korzystają wyłącznie z ConversionRequest + execute(), nie wołają konwerterów wprost.
"""
from collections.abc import Callable
from dataclasses import dataclass
import csv
import json
from docx import Document
from fpdf import FPDF
import logging
import os
import shutil
import subprocess
import time
import zipfile
from pathlib import Path
from docx.opc.exceptions import PackageNotFoundError
from konwerter.errors import *

log = logging.getLogger(__name__)

# Typ funkcji konwertującej: (plik_źródłowy, katalog_docelowy) -> ścieżka utworzonego pliku
Converter = Callable[[Path, Path], Path]
# Rejestr wszystkich obsługiwanych konwersji, np. {(".csv", ".json"): csv_to_json, ...}
REGISTRY: dict[tuple[str, str], Converter] = {}


def find_office() -> str:
    """Zwraca ścieżkę do programu LibreOffice (soffice) albo zgłasza RuntimeError."""
    # najpierw szukamy w zmiennej PATH
    found = shutil.which("soffice") or shutil.which("libreoffice")
    if found:
        return found
    # potem w domyślnych katalogach instalacji na Windows
    for candidate in (
        r"C:\Program Files\LibreOffice\program\soffice.exe",
        r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
    ):
        if Path(candidate).exists():
            return candidate
    raise RuntimeError("Nie znaleziono LibreOffice (soffice.exe)")

def converter(source: str, target: str):
    """Dekorator rejestrujący pojedynczy kierunek konwersji."""
    def register(func: Converter) -> Converter:
        # rozszerzenia zapisujemy małymi literami, żeby .CSV i .csv działały tak samo
        REGISTRY[(source.lower(), target.lower())] = func
        return func
    return register

# Czcionka TTF z polskimi znakami - wbudowane czcionki FPDF ich nie obsługują
FONT_PATH = Path(__file__).resolve().parent.parent / "fonts" / "ARIAL.TTF"
NOT_UTF8 = "Plik nie jest zapisany w kodowaniu UTF-8. Zapisz go jako UTF-8 i spróbuj ponownie."


def is_json_nested(data: list[dict]) -> bool:
    """True, jeśli którakolwiek wartość w którymkolwiek obiekcie jest słownikiem lub listą."""
    return any(isinstance(v, (dict, list)) for d in data for v in d.values())

def read_text_lines(source_file: Path) -> list[str]:
    """Wczytuje plik TXT (UTF-8) jako listę linii - wspólne dla TXT -> DOCX i TXT -> PDF."""
    try:
        # utf-8-sig: usuwa ewentualny znacznik BOM z początku pliku
        return source_file.read_text(encoding="utf-8-sig").splitlines()
    except UnicodeDecodeError:
        raise CorruptedInputFile(NOT_UTF8)

@converter(".csv", ".json")
def csv_to_json(source_file: Path, output_dir: Path):
    """CSV -> JSON: każdy wiersz staje się obiektem {nagłówek: wartość}."""
    try:
        with open(source_file, mode='r', encoding='utf-8-sig', newline='') as csvfile:
            # na podstawie próbki pliku zgadujemy separator (; , tabulator lub |)
            sample = csvfile.read(4096)
            csvfile.seek(0)  # wracamy na początek, żeby DictReader czytał cały plik
            try:
                delimiter = csv.Sniffer().sniff(sample, delimiters=";,\t|").delimiter
            except csv.Error:
                # nie udało się rozpoznać (np. jedna kolumna) -> domyślnie średnik
                delimiter = ';'

            # DictReader używa pierwszego wiersza jako nagłówka (kluczy słownika)
            data = list(csv.DictReader(csvfile, delimiter=delimiter, strict=True))
    except UnicodeDecodeError as e:
        raise CorruptedInputFile(f"Nie mozna odczytac pliku przez złe kodowanie lub uszkodzone dane: {e}")
    except csv.Error as e:
        raise CorruptedInputFile(f"Uszkodzony plik csv: {e}")

    # pusty plik lub sam nagłówek -> brak danych do zapisania
    if not data:
        raise EmptyInputFile("Plik nie zawiera żadnych danych")

    target = output_dir / f"{source_file.stem}.json"

    # ensure_ascii=False zapisuje polskie znaki wprost, a nie jako \u0105 itp.
    with open(target, mode='w', encoding='utf-8') as jsonfile:
        json.dump(data, jsonfile, indent=4, ensure_ascii=False)
    return target

@converter(".json", ".csv")
def json_to_csv(source_file: Path, output_dir: Path):
    """JSON -> CSV: obsługuje pojedynczy obiekt lub płaską listę obiektów."""
    try:
        # utf-8-sig: akceptuje pliki zarówno z BOM, jak i bez
        with open(source_file, mode='r', encoding='utf-8-sig') as jsonfile:
            data = json.load(jsonfile)
    except UnicodeDecodeError:
        raise CorruptedInputFile(NOT_UTF8)
    except json.JSONDecodeError as e:
        raise CorruptedInputFile(f"Plik JSON jest uszkodzony (błąd składni): {e}")

    # pojedynczy obiekt traktujemy jak listę z jednym elementem
    if not isinstance(data, list):
        data = [data]
    # każdy element musi być obiektem (słownikiem), np. [1, 2, 3] jest odrzucane
    if not all(isinstance(d, dict) for d in data):
        raise InvalidJsonStructure(
            "Nieobsługiwana struktura JSON. Plik musi zawierać obiekt lub listę obiektów, "
            'np. [{"imie": "Anna", "wiek": 28}].'
        )
    # CSV jest płaską tabelą - zagnieżdżonych struktur nie da się w nim zapisać
    if is_json_nested(data):
        raise JsonIsNested("Plik .json zawiera zagnieżdżone obiekty lub listy - obsługiwany jest tylko płaski JSON.")
    if not data:
        raise EmptyInputFile("Plik nie zawiera żadnych danych")

    # nagłówek CSV = wszystkie klucze ze wszystkich obiektów, w kolejności pierwszego wystąpienia
    keys = []
    for d in data:
        for k in d:
            if k not in keys:
                keys.append(k)

    target = output_dir / f"{source_file.stem}.csv"
    # utf-8-sig (z BOM), żeby Excel poprawnie wyświetlał polskie znaki
    with open(target, mode='w', encoding='utf-8-sig', newline='') as csvfile:
        cw = csv.writer(csvfile)
        cw.writerow(keys)
        for d in data:
            # brakujący klucz lub null -> pusta komórka
            cw.writerow([d.get(k) for k in keys])
    return target

@converter(".txt", ".docx")
def txt_to_docx(source_file: Path, output_dir: Path):
    """TXT -> DOCX: każda linia tekstu staje się osobnym akapitem."""
    doc = Document()
    for line in read_text_lines(source_file):
        doc.add_paragraph(line)

    target = output_dir / f"{source_file.stem}.docx"

    doc.save(target)

    return target

@converter(".txt", ".pdf")
def txt_to_pdf(source_file: Path, output_dir: Path):
    """TXT -> PDF: tekst zapisywany czcionką Arial (z polskimi znakami) na stronach A4."""
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("Arial", style="", fname=FONT_PATH)
    pdf.set_font("Arial", size=15)
    for line in read_text_lines(source_file):
        # multi_cell zawija długie linie (cell ucinał tekst na marginesie)
        pdf.multi_cell(w=0, h=10, text=line, align='L', new_x="LMARGIN", new_y="NEXT")
    target = output_dir / f"{source_file.stem}.pdf"
    pdf.output(target)
    return target

@converter(".docx", ".txt")
def docx_to_txt(source_file: Path, output_dir: Path):
    """DOCX -> TXT: zapisuje sam tekst akapitów (bez formatowania), jeden akapit na linię."""
    try:
        doc = Document(str(source_file))
    except PackageNotFoundError as exc:
        # plik nie jest poprawnym archiwum DOCX
        raise CorruptedInputFile("Plik jest uszkodzony albo nie jest dokumentem DOCX.") from exc

    lines = [paragraph.text for paragraph in doc.paragraphs]

    target = output_dir / f"{source_file.stem}.txt"
    target.write_text("\n".join(lines), encoding="utf-8")
    return target

@converter(".docx", ".pdf")
@converter(".odt", ".pdf")
def office_to_pdf(source_file: Path, output_dir: Path) -> Path:
    """Konwersja DOCX/ODT -> PDF przez LibreOffice w trybie headless."""
    # DOCX i ODT to archiwa ZIP. LibreOffice rozpoznaje format po zawartości, więc bez tej
    # kontroli np. zwykły tekst z rozszerzeniem .docx zostałby "poprawnie" zamieniony na PDF.
    if not zipfile.is_zipfile(source_file):
        raise CorruptedInputFile(
            f"Plik jest uszkodzony albo nie jest dokumentem {source_file.suffix[1:].upper()}.")
    # uruchamiamy LibreOffice bez okna; PDF trafi do output_dir pod tą samą nazwą
    command = [
        find_office(), "--headless", "--convert-to", "pdf",
        "--outdir", str(output_dir), str(source_file)
        ]
    # timeout chroni przed zawieszeniem aplikacji, gdyby LibreOffice nie odpowiadał
    result = subprocess.run(command, capture_output=True, text=True, timeout=60)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "Konwersja nie powiodła się")
    # LibreOffice potrafi zakończyć się kodem 0 bez utworzenia pliku - sprawdzamy to
    target = output_dir / f"{source_file.stem}.pdf"
    if not target.exists():
        raise RuntimeError("Narzędzie nie utworzyło oczekiwanego pliku")
    return target


@dataclass(frozen=True)
class ConversionRequest:
    """Opis jednej konwersji: co, na jaki format i dokąd zapisać."""
    source: Path
    target_format: str
    output_dir: Path
    overwrite: bool = False  # True = użytkownik potwierdził nadpisanie istniejącego pliku

    @property
    def key(self) -> tuple[str, str]:
        """Klucz do REGISTRY, np. (".csv", ".json")."""
        return (self.source.suffix.lower(), self.target_format.lower())

    @property
    def target_path(self) -> Path:
        """Ścieżka pliku, który powstanie po konwersji."""
        return self.output_dir / f"{self.source.stem}{self.target_format.lower()}"

    def validate(self) -> None:
        """Sprawdza, czy żądanie da się wykonać; w razie problemu zgłasza odpowiedni wyjątek."""
        # czy wszystkie pola zostały uzupełnione
        if not str(self.source).strip() or self.source == Path("."):
            raise ValueError("Nie wybrano pliku wejściowego")
        if not self.target_format:
            raise ValueError("Nie wybrano formatu docelowego")
        if not str(self.output_dir).strip():
            raise ValueError("Nie wybrano katalogu zapisu")
        # czy plik i katalog istnieją oraz czy mamy prawo zapisu
        if not self.source.is_file():
            raise FileNotFoundError(f"Nie znaleziono pliku wejściowego: {self.source}")
        if not self.output_dir.is_dir():
            raise NotADirectoryError(f"Nie znaleziono katalogu docelowego: {self.output_dir}")
        if not os.access(self.output_dir, os.W_OK):
            raise PermissionError(f"Brak uprawnień do zapisu w katalogu: {self.output_dir}")
        # czy taka para formatów jest obsługiwana
        if self.key not in REGISTRY:
            raise ValueError(f"Nieobsługiwana konwersja: {self.key[0]} → {self.key[1]}")
        # czy nie nadpiszemy istniejącego pliku bez zgody użytkownika
        if self.target_path.exists() and not self.overwrite:
            raise TargetExists(self.target_path)


def available_targets(source: Path) -> list[str]:
    """Lista formatów docelowych dostępnych dla rozszerzenia danego pliku (posortowana)."""
    return sorted(target for (src, target) in REGISTRY if src == source.suffix.lower())


def execute(request: ConversionRequest) -> Path:
    """Waliduje żądanie, wykonuje konwersję i loguje jej czas oraz wynik.

    Polityka nadpisywania: jeśli plik docelowy istnieje, a request.overwrite == False,
    zgłaszany jest TargetExists - wywołujący (np. GUI) pyta użytkownika i ponawia
    żądanie z overwrite=True.
    """
    request.validate()
    log.info("Start: %s -> %s (katalog: %s)", request.source, request.target_format, request.output_dir)
    start = time.perf_counter()
    try:
        # wybieramy z rejestru funkcję dla danej pary formatów i ją wywołujemy
        result = REGISTRY[request.key](request.source, request.output_dir)
    except Exception:
        # logujemy błąd ze stosem wywołań, a wyjątek przekazujemy dalej (do GUI)
        log.exception("Błąd konwersji %s -> %s po %.2f s",
                      request.source, request.target_format, time.perf_counter() - start)
        raise
    log.info("OK: %s (%.2f s)", result, time.perf_counter() - start)
    return result
