from konwerter.gui import *

def main():
    #key = (Path(args.Input).suffix, Path(args.Output).suffix)
    #func = REGISTRY[key]
    #func(samples/args.Input, output)

    app = ConvertApp()
    app.start()


if __name__ == "__main__":
    main()

