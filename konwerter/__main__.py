import csv
import json
import argparse
from konwerter.errors import * 
from pathlib import Path
from detect_delimiter import detect

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--Input", help="input file path")
parser.add_argument("-o", "--Output", help="outpur file path")
args = parser.parse_args()

samples = Path.cwd() / "samples"
output = Path.cwd() / "output"


def convert_csv_to_json(file_path_in, file_path_out):
    with open(file_path_in, mode='r', encoding='utf-8-sig') as csvfile:
        sample = csvfile.read(4096)
        csvfile.seek(0)
        delimeter = detect(sample, whitelist=[';',',','\t','|'])
        data = list(csv.DictReader(csvfile, delimiter=delimeter))

    with open(file_path_out, mode='w', encoding='utf-8') as jsonfile:
        json.dump(data, jsonfile, indent=4, ensure_ascii=False)
    print("[FUNCTION END] convert_csv_json")
    

def convert_json_to_csv(file_path_in, file_path_out):
    with open(file_path_in, mode='r', encoding='utf-8') as jsonfile:
        data = json.load(jsonfile)

    df = open(file_path_out, mode='w', encoding='utf-8')
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
            convert_json_to_csv(samples/args.Input, output/args.Output)
        except Exception as e:
            print("ERROR: ", e)
    elif args.Input.find(".csv") != -1:
        try:
            convert_csv_to_json(samples/args.Input, output/args.Output)
        except Exception as e:
            print("ERROR: ", e)
    else:
        print("daj argumenty")
    


if __name__ == "__main__":
    main()

