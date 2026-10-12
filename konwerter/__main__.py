import csv
import json
import argparse
from docx import Document
from fpdf import FPDF
from konwerter.errors import * 
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--Input", help="input file path")
parser.add_argument("-o", "--Output", help="outpur file path")
args = parser.parse_args()

samples = Path.cwd() / "samples"
output = Path.cwd() / "output"

def is_json_nested(data) -> bool:

    for d in data:
        if isinstance(d, list):
            return True
        if isinstance(d, dict):
            for v in d.values():
                if isinstance(v,(dict,list)):
                    return True

    return False


def convert_csv_to_json(file_path_in, file_path_out):
    try:
        with open(file_path_in, mode='r', encoding='utf-8-sig', newline='') as csvfile:
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
    
    with open(file_path_out, mode='w', encoding='utf-8') as jsonfile:
        json.dump(data, jsonfile, indent=4, ensure_ascii=False)
    print("[FUNCTION END] convert_csv_to_json")
    

def convert_json_to_csv(file_path_in, file_path_out):
    try:
        with open(file_path_in, mode='r', encoding='utf-8') as jsonfile:
            data = json.load(jsonfile)
            if not isinstance(data, list):
                    data = [data]

            if is_json_nested(data):
                raise JsonIsNested("Plik .json zawiera zagnieżdżenie lub listy")
    except json.JSONDecodeError as e:
        raise CorruptedInputFile(f"Nie mozna odczytac pliku przez złe kodowanie lub uszkodzone dane: {e}")

    if not data:
        raise EmptyInputFile("Plik nie zawiera żadnych danych")

    try:
        df = open(file_path_out, mode='w', encoding='utf-8-sig', newline='')
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

def convert_txt_to_docx(file_path_in, file_path_out):
    doc = Document() 

    with open(file_path_in, "r", encoding="utf-8", errors="replace") as file:
        for line in file:
            doc.add_paragraph(line.rstrip()) 

    doc.save(file_path_out) 

    print(f"DOCX created successfully: {file_path_out}") 

def convert_txt_to_pdf(file_path_in, file_path_out):
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("Arial", style="", fname="fonts/ARIAL.TTF")
    pdf.set_font("Arial", size=15)
    with open(file_path_in, 'r', encoding="utf-8") as f:
        for x in f:
            pdf.cell(w=200, h=10, text=x.strip(), align='C', new_x="LMARGIN", new_y="NEXT")
    pdf.output(file_path_out) 

def main():
    
    if args.Input.find(".json") != -1:
        try:
            convert_json_to_csv(samples/args.Input, output/args.Output)
        except ConversionError as e:
            print("ERROR: ", e)
        except Exception as e:
            print("ERROR: ", e)
    elif args.Input.find(".csv") != -1:
        try:
            convert_csv_to_json(samples/args.Input, output/args.Output)
        except ConversionError as e:
            print("ERROR", e)
        except Exception as e:
            print("ERROR: ", e)
    elif (args.Input.find(".txt") != -1) and (args.Output.find(".docx") != -1):
        try:
            convert_txt_to_docx(samples/args.Input, output/args.Output)
        except Exception as e:
            print("ERROR: ", e)
    elif (args.Input.find(".txt") != -1) and (args.Output.find(".pdf") != -1):
        try:
            convert_txt_to_pdf(samples/args.Input, output/args.Output)
        except Exception as e:
            print("ERROR: ", e)
    else:
        print("daj argumenty")
    

if __name__ == "__main__":
    main()

