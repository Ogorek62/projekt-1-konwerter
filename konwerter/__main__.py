import argparse
from pathlib import Path
from konwerter.gui import *

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--Input", help="input file path")
parser.add_argument("-o", "--Output", help="outpur file path")
args = parser.parse_args()

samples = Path.cwd() / "samples"
output = Path.cwd() / "output"



def main():
    #key = (Path(args.Input).suffix, Path(args.Output).suffix)
    #func = REGISTRY[key]
    #func(samples/args.Input, output)

    app = ConvertApp()
    app.start()


if __name__ == "__main__":
    main()

