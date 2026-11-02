# Dane testowe

Pliki są używane przez testy automatyczne w `test/` i można je też ręcznie wybrać w GUI.
Wszystkie pliki tekstowe są w UTF-8, chyba że opis mówi inaczej.

## Grupa A: CSV → JSON

| Plik | Co sprawdza | Oczekiwany wynik |
|---|---|---|
| `csv_przecinek.csv` | separator `,`, polskie znaki, liczby z zerem na początku | JSON z kluczami `imię, nazwisko, miasto, numer` w tej kolejności; `"007"` zostaje tekstem |
| `csv_srednik.csv` | separator `;`, przecinek w wartości (`2,50`) | `"cena": "2,50"`, przecinek nie dzieli kolumny |
| `csv_tabulator.csv` | separator tabulatora | 2 obiekty `kod`, `nazwa` |
| `csv_bom.csv` | UTF-8 z BOM | klucz `imię` bez znaku BOM |
| `csv_puste_wartosci.csv` | puste pola | puste pola jako `""` |
| `csv_cudzyslowy.csv` | pola w cudzysłowach z przecinkiem, nową linią i `""` | wartości odczytane w całości |
| `csv_tylko_naglowek.csv` | brak wierszy danych | błąd „Plik nie zawiera żadnych danych” |
| `csv_pusty.csv` | plik pusty (0 bajtów) | błąd „Plik nie zawiera żadnych danych” |
| `csv_cp1250.csv` | kodowanie Windows-1250 | błąd „uszkodzony plik / złe kodowanie” |

## Grupa A: JSON → CSV

| Plik | Co sprawdza | Oczekiwany wynik |
|---|---|---|
| `json_lista_obiektow.json` | lista płaskich obiektów, polskie znaki | CSV z nagłówkiem `imię,nazwisko,miasto` |
| `json_rozne_klucze.json` | obiekty z różnymi kluczami | nagłówek `imię,wiek,miasto`, brakujące wartości puste |
| `json_jeden_obiekt.json` | pojedynczy obiekt zamiast listy | CSV z jednym wierszem danych |
| `json_typy.json` | liczby i `null` | `28`, `3.5`; `null` jako puste pole |
| `json_bom.json` | UTF-8 z BOM | poprawny CSV |
| `json_pusta_lista.json` | `[]` | błąd „Plik nie zawiera żadnych danych” |
| `json_zagniezdzony.json` | obiekt w obiekcie | błąd „Zagnieżdżony JSON” |
| `json_lista_w_wartosci.json` | lista jako wartość | błąd „Zagnieżdżony JSON” |
| `json_lista_wartosci.json` | `[1, 2, 3]`, czyli nie obiekty | błąd „Nieobsługiwana struktura JSON” |
| `json_uszkodzony.json` | brak przecinka (błąd składni) | błąd „Plik JSON jest uszkodzony” z numerem linii |

## Grupa B: tekst i dokumenty

| Plik | Konwersja | Oczekiwany wynik |
|---|---|---|
| `txt_dokument.txt` | → DOCX, → PDF | każda linia to osobny akapit (z pustą linią i wcięciem), polskie znaki poprawne |
| `txt_dluga_linia.txt` | → PDF | długa linia zawinięta, nie ucięta |
| `txt_cp1250.txt` | → DOCX, → PDF | błąd z instrukcją „zapisz plik jako UTF-8” |
| `docx_dokument.docx` | → TXT | 4 linie: `Dokument testowy`, `Zażółć gęślą jaźń`, pusta, `Trzeci akapit: ĄĆĘŁŃÓŚŹŻ` |
| `docx_uszkodzony.docx` | → TXT | błąd „Plik jest uszkodzony albo nie jest dokumentem DOCX” |

## Grupa C: formaty biurowe (wymaga LibreOffice)

| Plik | Konwersja | Oczekiwany wynik |
|---|---|---|
| `docx_dokument.docx` | → PDF | otwieralny PDF z treścią dokumentu |
| `odt_dokument.odt` | → PDF | otwieralny PDF z treścią dokumentu |
