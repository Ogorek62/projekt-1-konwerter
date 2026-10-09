import csv
import json
import argparse
from konwerter.errors import * 
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--Input", help="input file path")
parser.add_argument("-o", "--Output", help="outpur file path")
args = parser.parse_args()

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
    
    if args.Input.find(".json") != -1:
        try:
            convert_json_csv(args.Input, args.Output)
        except Exception as e:
            print("ERROR: ", e)
    elif args.Input.find(".csv") != -1:
        try:
            convert_csv_json(args.Input, args.Output)
        except Exception as e:
            print("ERROR: ", e)
    else:
        print("daj argumenty")
    


if __name__ == "__main__":
    main()

