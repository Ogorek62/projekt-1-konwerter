import csv
import json
import logging
from konwerter.errors import * 
from pathlib import Path


samples = Path.cwd() / "samples"
output = Path.cwd() / "output"


def convert_csv_json(file_in:str, file_out:str):
    with open(samples/file_in, mode='r', encoding='utf-8') as csvfile:
        data = list(csv.DictReader(csvfile))

    with open(output/file_out, mode='w', encoding='utf-8') as jsonfile:
        json.dump(data, jsonfile, indent=4, ensure_ascii=False)
    print("[FUNCTION END] convert_csv_json")


def convert_json_csv(file_in:str, file_out:str):
    with open(samples/file_in, mode='r', encoding='utf-8') as jsonfile:
        data = json.load(jsonfile)

    df = open(output/file_out, mode='w', encoding='utf-8')
    cw = csv.writer(df)

    c = 0
    for data in data:
        if c == 0:
            header = data.keys()
            cw.writerow(header)
            c += 1
        cw.writerow(data.values())

    df.close()
    print("[FUNCTION END] convert_json_csv")


def main():
    try:
        convert_csv_json("dane.csv", "csvout.json")
    except Exception as e:
        print("ERROR: ", e)

    try:
        convert_json_csv("dane.json", "jsonout.csv")
    except Exception as e:
        print("ERROR: ", e)
    
    print("elo")

if __name__ == "__main__":
    main()

