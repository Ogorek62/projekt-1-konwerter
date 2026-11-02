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
from pathlib import Path
from docx.opc.exceptions import PackageNotFoundError
from konwerter.errors import *

log = logging.getLogger(__name__)

Converter = Callable[[Path, Path], Path]
REGISTRY: dict[tuple[str, str], Converter] = {}


def find_office() -> str:
    found = shutil.which("soffice") or shutil.which("libreoffice")
    if found:
        return found
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
        REGISTRY[(source.lower(), target.lower())] = func
        return func
    return register

FONT_PATH = Path(__file__).resolve().parent.parent / "fonts" / "ARIAL.TTF"
NOT_UTF8 = "Plik nie jest zapisany w kodowaniu UTF-8. Zapisz go jako UTF-8 i spróbuj ponownie."


def is_json_nested(data: list[dict]) -> bool:
    return any(isinstance(v, (dict, list)) for d in data for v in d.values())

def read_text_lines(source_file: Path) -> list[str]:
    """Wczytuje plik TXT (UTF-8) jako listę linii - wspólne dla TXT -> DOCX i TXT -> PDF."""
    try:
        return source_file.read_text(encoding="utf-8-sig").splitlines()
    except UnicodeDecodeError:
        raise CorruptedInputFile(NOT_UTF8)

@converter(".csv", ".json")
def csv_to_json(source_file: Path, output_dir: Path):
    try:
        with open(source_file, mode='r', encoding='utf-8-sig', newline='') as csvfile:
            sample = csvfile.read(4096)
            csvfile.seek(0)
            try:
                delimiter = csv.Sniffer().sniff(sample, delimiters=";,\t|").delimiter
            except csv.Error:
                delimiter = ';'

            data = list(csv.DictReader(csvfile, delimiter=delimiter, strict=True))
    except UnicodeDecodeError as e:
        raise CorruptedInputFile(f"Nie mozna odczytac pliku przez złe kodowanie lub uszkodzone dane: {e}")
    except csv.Error as e:
        raise CorruptedInputFile(f"Uszkodzony plik csv: {e}")

    if not data:
        raise EmptyInputFile("Plik nie zawiera żadnych danych")
    
    target = output_dir / f"{source_file.stem}.json"

    with open(target, mode='w', encoding='utf-8') as jsonfile:
        json.dump(data, jsonfile, indent=4, ensure_ascii=False)
    return target
    
@converter(".json", ".csv")
def json_to_csv(source_file: Path, output_dir: Path):
    try:
        # utf-8-sig: akceptuje pliki zarówno z BOM, jak i bez
        with open(source_file, mode='r', encoding='utf-8-sig') as jsonfile:
            data = json.load(jsonfile)
    except UnicodeDecodeError:
        raise CorruptedInputFile(NOT_UTF8)
    except json.JSONDecodeError as e:
        raise CorruptedInputFile(f"Plik JSON jest uszkodzony (błąd składni): {e}")

    if not isinstance(data, list):
        data = [data]
    if not all(isinstance(d, dict) for d in data):
        raise InvalidJsonStructure(
            "Nieobsługiwana struktura JSON. Plik musi zawierać obiekt lub listę obiektów, "
            'np. [{"imie": "Anna", "wiek": 28}].'
        )
    if is_json_nested(data):
        raise JsonIsNested("Plik .json zawiera zagnieżdżone obiekty lub listy - obsługiwany jest tylko płaski JSON.")
    if not data:
        raise EmptyInputFile("Plik nie zawiera żadnych danych")

    keys = []
    for d in data:
        for k in d:
            if k not in keys:
                keys.append(k)

    target = output_dir / f"{source_file.stem}.csv"
    with open(target, mode='w', encoding='utf-8-sig', newline='') as csvfile:
        cw = csv.writer(csvfile)
        cw.writerow(keys)
        for d in data:
            cw.writerow([d.get(k) for k in keys])
    return target

@converter(".txt", ".docx")
def txt_to_docx(source_file: Path, output_dir: Path):
    doc = Document()
    for line in read_text_lines(source_file):
        doc.add_paragraph(line)

    target = output_dir / f"{source_file.stem}.docx"

    doc.save(target)

    return target

@converter(".txt", ".pdf")
def txt_to_pdf(source_file: Path, output_dir: Path):
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
    try:
        doc = Document(str(source_file))
    except PackageNotFoundError as exc:
        raise CorruptedInputFile("Plik jest uszkodzony albo nie jest dokumentem DOCX.") from exc

    lines = [paragraph.text for paragraph in doc.paragraphs]

    target = output_dir / f"{source_file.stem}.txt"
    target.write_text("\n".join(lines), encoding="utf-8")
    return target

@converter(".docx", ".pdf")
@converter(".odt", ".pdf")
def office_to_pdf(source_file: Path, output_dir: Path) -> Path:
    """Konwersja DOCX/ODT -> PDF przez LibreOffice w trybie headless."""
    command = [
        find_office(), "--headless", "--convert-to", "pdf",
        "--outdir", str(output_dir), str(source_file)
        ]
    result = subprocess.run(command, capture_output=True, text=True, timeout=60)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "Konwersja nie powiodła się")
    target = output_dir / f"{source_file.stem}.pdf"
    if not target.exists():
        raise RuntimeError("Narzędzie nie utworzyło oczekiwanego pliku")
    return target


@dataclass(frozen=True)
class ConversionRequest:
    source: Path
    target_format: str
    output_dir: Path
    overwrite: bool = False  # True = użytkownik potwierdził nadpisanie istniejącego pliku

    @property
    def key(self) -> tuple[str, str]:
        return (self.source.suffix.lower(), self.target_format.lower())

    @property
    def target_path(self) -> Path:
        """Ścieżka pliku, który powstanie po konwersji."""
        return self.output_dir / f"{self.source.stem}{self.target_format.lower()}"

    def validate(self) -> None:
        if not str(self.source).strip() or self.source == Path("."):
            raise ValueError("Nie wybrano pliku wejściowego")
        if not self.target_format:
            raise ValueError("Nie wybrano formatu docelowego")
        if not str(self.output_dir).strip():
            raise ValueError("Nie wybrano katalogu zapisu")
        if not self.source.is_file():
            raise FileNotFoundError(f"Nie znaleziono pliku wejściowego: {self.source}")
        if not self.output_dir.is_dir():
            raise NotADirectoryError(f"Nie znaleziono katalogu docelowego: {self.output_dir}")
        if not os.access(self.output_dir, os.W_OK):
            raise PermissionError(f"Brak uprawnień do zapisu w katalogu: {self.output_dir}")
        if self.key not in REGISTRY:
            raise ValueError(f"Nieobsługiwana konwersja: {self.key[0]} → {self.key[1]}")
        if self.target_path.exists() and not self.overwrite:
            raise TargetExists(self.target_path)


def available_targets(source: Path) -> list[str]:
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
        result = REGISTRY[request.key](request.source, request.output_dir)
    except Exception:
        log.exception("Błąd konwersji %s -> %s po %.2f s",
                      request.source, request.target_format, time.perf_counter() - start)
        raise
    log.info("OK: %s (%.2f s)", result, time.perf_counter() - start)
    return result