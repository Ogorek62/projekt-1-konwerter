import csv
import json
import argparse
from docx import Document
from fpdf import FPDF
import subprocess
from collections.abc import Callable
from konwerter.errors import * 
from pathlib import Path
from docx.opc.exceptions import PackageNotFoundError

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--Input", help="input file path")
parser.add_argument("-o", "--Output", help="outpur file path")
args = parser.parse_args()

samples = Path.cwd() / "samples"
output = Path.cwd() / "output"

Converter = Callable[[Path, Path], Path]
REGISTRY: dict[tuple[str, str], Converter] = {}

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
    print("[FUNCTION END] convert_csv_to_json")
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
    print("[FUNCTION END] convert_json_to_csv")
    return target

@converter(".txt", ".docx")
def txt_to_docx(source_file: Path, output_dir: Path):
    doc = Document() 

    with open(source_file, "r", encoding="utf-8", errors="replace") as file:
        for line in file:
            doc.add_paragraph(line.rstrip()) 

    target = output_dir / f"{source_file.stem}.docx"

    doc.save(target) 

    print(f"DOCX created successfully: {target}")
    return target 

@converter(".txt", ".pdf")
def txt_to_pdf(source_file: Path, output_dir: Path):
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("Arial", style="", fname="fonts/ARIAL.TTF")
    pdf.set_font("Arial", size=15)
    with open(source_file, 'r', encoding="utf-8") as f:
        for x in f:
            pdf.cell(w=200, h=10, text=x.strip(), align='C', new_x="LMARGIN", new_y="NEXT")
    target = output_dir / f"{source_file.stem}.pdf"
    pdf.output(target) 

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
def docx_to_pdf(source_file: Path, output_dir: Path) -> Path:
    command = [
        "libreoffice", "--headless", "--convert-to", "pdf",
        "--outdir", str(output_dir), str(source_file)
        ]
    result = subprocess.run(command, capture_output=True, text=True, timeout=60)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "Konwersja nie powiodła się")
    target = output_dir / f"{source_file.stem}.pdf"
    if not target.exists():
        raise RuntimeError("Narzędzie nie utworzyło oczekiwanego pliku")
    return target

def main():
    key = (Path(args.Input).suffix, Path(args.Output).suffix)
    func = REGISTRY[key]
    func(samples/args.Input, output)

if __name__ == "__main__":
    main()

