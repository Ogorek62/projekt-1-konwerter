from collections.abc import Callable
from dataclasses import dataclass
import csv
import json
from docx import Document
from fpdf import FPDF
import shutil
import subprocess
from pathlib import Path
from docx.opc.exceptions import PackageNotFoundError
from konwerter.errors import * 

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

def is_json_nested(data) -> bool:

    for d in data:
        if isinstance(d, list):
            return True
        if isinstance(d, dict):
            for v in d.values():
                if isinstance(v,(dict,list)):
                    return True

    return False

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
        with open(source_file, mode='r', encoding='utf-8') as jsonfile:
            data = json.load(jsonfile)
            if not isinstance(data, list):
                    data = [data]

            if is_json_nested(data):
                raise JsonIsNested("Plik .json zawiera zagnieżdżenie lub listy")
    except json.JSONDecodeError as e:
        raise CorruptedInputFile(f"Nie mozna odczytac pliku przez złe kodowanie lub uszkodzone dane: {e}")

    if not data:
        raise EmptyInputFile("Plik nie zawiera żadnych danych")

    target = output_dir / f"{source_file.stem}.csv"

    try:
        df = open(target, mode='w', encoding='utf-8-sig', newline='')
        cw = csv.writer(df)
    except Exception as e:
        raise Exception
    else:
        keys = []
        for d in data:
            for k in d:
                if k not in keys:
                    keys.append(k)

        cw.writerow(keys)
        for d in data:
            cw.writerow([d.get(k) for k in keys])
        
    
    finally:
        df.close()
    return target

@converter(".txt", ".docx")
def txt_to_docx(source_file: Path, output_dir: Path):
    doc = Document() 

    with open(source_file, "r", encoding="utf-8", errors="replace") as file:
        for line in file:
            doc.add_paragraph(line.rstrip()) 

    target = output_dir / f"{source_file.stem}.docx"

    doc.save(target)

    return target

@converter(".txt", ".pdf")
def txt_to_pdf(source_file: Path, output_dir: Path):
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("Arial", style="", fname="fonts/ARIAL.TTF")
    pdf.set_font("Arial", size=15)
    with open(source_file, 'r', encoding="utf-8") as f:
        for x in f:
            pdf.cell(w=0, h=10, text=x.strip(), align='L', new_x="LMARGIN", new_y="NEXT")
    target = output_dir / f"{source_file.stem}.pdf"
    pdf.output(target)
    return target

@converter(".docx", ".txt")
def docx_to_txt(source_file: Path, output_dir: Path):
    try:
        doc = Document(str(source_file))
    except PackageNotFoundError as exc:
        raise ValueError("Plik jest uszkodzony albo nie jest dokumentem DOCX.") from exc

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

    def validate(self) -> None:
        if not self.source.is_file():
            raise FileNotFoundError("Nie znaleziono pliku wejściowego")
        if not self.output_dir.is_dir():
            raise NotADirectoryError("Nie znaleziono katalogu docelowego")
        key = (self.source.suffix.lower(), self.target_format.lower())
        if key not in REGISTRY:
            raise ValueError(f"Nieobsługiwana konwersja: {key}")


def available_targets(source: Path) -> list[str]:
    return sorted(target for (src, target) in REGISTRY if src == source.suffix.lower())


def execute(request: ConversionRequest) -> Path:
    request.validate()
    key = (request.source.suffix.lower(), request.target_format.lower())
    # TODO: polityka nadpisywania i rejestrowanie czasu operacji
    return REGISTRY[key](request.source, request.output_dir)