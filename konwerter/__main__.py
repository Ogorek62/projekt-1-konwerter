import logging

from konwerter.gui import ConvertApp


def main():
    logging.basicConfig(
        filename="konwerter.log",
        level=logging.WARNING,  # biblioteki (np. fontTools z fpdf) tylko ostrzeżenia
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        encoding="utf-8",
    )
    logging.getLogger("konwerter").setLevel(logging.INFO)  # nasze logi: pełne
    app = ConvertApp()
    app.start()


if __name__ == "__main__":
    main()
