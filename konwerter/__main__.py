"""Punkt wejścia aplikacji - uruchamiany poleceniem `python -m konwerter`."""
import logging

from konwerter.gui import ConvertApp


def main():
    # Konfiguracja logowania do pliku konwerter.log (w bieżącym katalogu roboczym).
    logging.basicConfig(
        filename="konwerter.log",
        level=logging.WARNING,  # biblioteki (np. fontTools z fpdf) tylko ostrzeżenia
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        encoding="utf-8",
    )
    logging.getLogger("konwerter").setLevel(logging.INFO)  # nasze logi: pełne
    # Tworzymy okno aplikacji i uruchamiamy pętlę zdarzeń tkintera.
    app = ConvertApp()
    app.start()


# Uruchomienie tylko przy bezpośrednim wywołaniu modułu (nie przy imporcie).
if __name__ == "__main__":
    main()
