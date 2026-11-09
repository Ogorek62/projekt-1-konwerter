# Raport z testów

Raport opracowano na podstawie pliku [`raport_testow.txt`](raport_testow.txt), czyli surowego wyniku polecenia `pytest -v`.

## Środowisko

| | |
|---|---|
| System | Windows 11 (win32) |
| Python | 3.13.15 |
| pytest | 9.1.1 |
| LibreOffice | zainstalowany (`C:\Program Files\LibreOffice\program\soffice.exe`) |
| Dane testowe | `samples/` (opis oczekiwanych wyników: [`samples/OPIS.md`](samples/OPIS.md)) |

## Podsumowanie

| Wynik | Liczba |
|---|---|
| ✅ zaliczone (PASSED) | **46** |
| ❌ niezaliczone (FAILED) | 0 |
| ⏭️ pominięte (SKIPPED) | 0 |
| **Razem** | **46** (czas: 2,95 s) |

Wszystkie testy automatyczne zakończyły się powodzeniem. Żaden test nie został pominięty, więc konwersje przez LibreOffice również zostały faktycznie wykonane.

## Pokrycie minimalnej macierzy testów z instrukcji

| Przypadek z instrukcji | Oczekiwany rezultat | Testy | Wynik |
|---|---|---|---|
| Poprawny plik w każdej wspieranej grupie | powstaje otwieralny plik o właściwej treści | `test_csv_do_json`, `test_json_do_csv`, `test_txt_do_docx_zachowuje_akapity`, `test_txt_do_pdf_zachowuje_tresc`, `test_docx_do_txt`, `test_dokument_biurowy_do_pdf` | ✅ |
| Błędny lub uszkodzony plik | brak awarii, jednoznaczny komunikat | `test_csv_do_json_bledy`, `test_json_do_csv_bledy`, `test_txt_w_cp1250_daje_czytelny_blad`, `test_uszkodzony_docx` | ✅ |
| Nieobsługiwana para | opcja niewidoczna lub zablokowana | `test_available_targets` (np. `.xyz` → brak opcji), `test_validate_nieobslugiwana_para` | ✅ (logika); w GUI do pokazania na demonstracji |
| Brak LibreOffice | kontrolowany błąd z instrukcją | `test_brak_libreoffice_daje_kontrolowany_blad` | ✅ |
| Plik docelowy już istnieje | pytanie o nadpisanie | `test_validate_plik_docelowy_istnieje`, `test_execute_nie_nadpisuje_bez_zgody` | ✅ (logika); okno pytania w GUI do pokazania na demonstracji |
| Polskie znaki i puste wartości | znaki i struktura danych poprawne | `test_csv_do_json[csv_przecinek / csv_puste_wartosci]`, `test_json_do_csv[json_lista_obiektow / json_typy]`, `test_csv_json_csv_bez_utraty_danych`, `test_docx_do_txt` | ✅ |

## Wyniki według plików testowych

### `test/test_dane.py`: grupa A, CSV ↔ JSON (20 testów, wszystkie ✅)

| Test | Dane wejściowe | Co sprawdzono |
|---|---|---|
| `test_csv_do_json` (6×) | `csv_przecinek`, `csv_srednik`, `csv_tabulator`, `csv_bom`, `csv_puste_wartosci`, `csv_cudzyslowy` | dokładna zawartość JSON: automatyczne wykrycie separatora (`,` `;` tabulator), polskie znaki, kolejność kolumn, `"007"` zostaje tekstem, BOM nie trafia do nazwy kolumny, puste pola jako `""`, pola w cudzysłowach z przecinkiem i nową linią |
| `test_csv_do_json_bledy` (3×) | `csv_tylko_naglowek`, `csv_pusty`, `csv_cp1250` | brak danych → `EmptyInputFile`; kodowanie Windows-1250 → `CorruptedInputFile` |
| `test_json_do_csv` (5×) | `json_lista_obiektow`, `json_rozne_klucze`, `json_jeden_obiekt`, `json_typy`, `json_bom` | dokładna zawartość CSV: nagłówek jako suma kluczy w kolejności wystąpienia, brakujące wartości puste, pojedynczy obiekt, liczby i `null`, plik z BOM |
| `test_json_do_csv_bledy` (5×) | `json_pusta_lista`, `json_zagniezdzony`, `json_lista_w_wartosci`, `json_lista_wartosci`, `json_uszkodzony` | odpowiednio: `EmptyInputFile`, `JsonIsNested` (2×), `InvalidJsonStructure`, `CorruptedInputFile` |
| `test_csv_json_csv_bez_utraty_danych` | `csv_puste_wartosci` | CSV → JSON → CSV daje dane identyczne z wejściem (wynik da się ponownie odczytać) |

### `test/test_dokumenty.py`: grupy B i C (10 testów, wszystkie ✅)

| Test | Dane wejściowe | Co sprawdzono |
|---|---|---|
| `test_txt_do_docx_zachowuje_akapity` | `txt_dokument.txt` | każda linia jest osobnym akapitem DOCX, łącznie z pustą linią, wcięciem i polskimi znakami |
| `test_txt_do_pdf_zachowuje_tresc` | `txt_dokument.txt` | tekst odczytany z PDF (pypdf) jest identyczny z niepustymi liniami pliku TXT, łącznie z polskimi znakami i wcięciem |
| `test_txt_do_pdf_zawija_dluga_linie` | `txt_dluga_linia.txt` | długa linia jest zawinięta na kilka wierszy, a po złączeniu tekst jest identyczny z wejściem (nic nie zostało ucięte) |
| `test_docx_do_txt` | `docx_dokument.docx` | dokładna treść TXT z polskimi znakami i pustym akapitem |
| `test_txt_w_cp1250_daje_czytelny_blad` (2×) | `txt_cp1250.txt` → DOCX / PDF | błąd `CorruptedInputFile` z informacją o wymaganym UTF-8 |
| `test_uszkodzony_docx` (2×) | `docx_uszkodzony.docx` → TXT / PDF | błąd `CorruptedInputFile` zamiast awarii; przy PDF błąd pojawia się przed wywołaniem LibreOffice, więc ten test nie wymaga jego instalacji |
| `test_dokument_biurowy_do_pdf` (2×) | `docx_dokument.docx`, `odt_dokument.odt` | LibreOffice tworzy PDF, który da się otworzyć i który zawiera tekst dokumentu (sprawdzane fragmenty bez polskich liter, patrz uwaga niżej) |

### `test/test_rejestr.py`: rejestr, walidacja, nadpisywanie (16 testów, wszystkie ✅)

| Test | Co sprawdzono |
|---|---|
| `test_available_targets` (8×) | lista formatów docelowych dla `.csv`, `.json`, `.txt`, `.docx`, `.odt`; wielkie litery w rozszerzeniu; brak opcji dla nieobsługiwanego rozszerzenia i pliku bez rozszerzenia |
| `test_validate_poprawne_zadanie` | poprawne żądanie przechodzi walidację |
| `test_validate_brak_pliku` | brak pliku wejściowego → `FileNotFoundError` |
| `test_validate_brak_katalogu` | brak katalogu zapisu → `NotADirectoryError` |
| `test_validate_nieobslugiwana_para` | para CSV → PDF → `ValueError` |
| `test_validate_pusty_format_docelowy` | pusty wybór formatu → `ValueError` |
| `test_validate_plik_docelowy_istnieje` | istniejący plik → `TargetExists`; po potwierdzeniu (`overwrite=True`) walidacja przechodzi |
| `test_execute_nie_nadpisuje_bez_zgody` | bez zgody plik nie jest zmieniany; po zgodzie zostaje nadpisany |
| `test_brak_libreoffice_daje_kontrolowany_blad` | symulacja systemu bez LibreOffice (podmiana wyszukiwania programu) → kontrolowany `RuntimeError` z komunikatem „Nie znaleziono LibreOffice” |

> **Uwaga o sprawdzaniu PDF.** Treść plików PDF jest odczytywana biblioteką `pypdf`. W PDF tworzonych przez fpdf2 (TXT → PDF) sprawdzany jest cały tekst, łącznie z polskimi znakami. LibreOffice osadza czcionkę bez tabeli `ToUnicode`, przez co `pypdf` błędnie odczytuje litery z polskimi znakami, dlatego dla DOCX/ODT → PDF sprawdzane są tylko fragmenty bez nich.

## Wnioski

- Wszystkie 7 obsługiwanych kierunków konwersji działa dla danych typowych i brzegowych.
- Błędne dane (złe kodowanie, uszkodzony plik, nieobsługiwana struktura JSON, puste pliki) dają kontrolowane wyjątki z czytelnym komunikatem zamiast awarii programu.
- Walidacja i polityka nadpisywania działają niezależnie od GUI, dlatego można je było przetestować automatycznie.

## Jak odtworzyć

```powershell
pytest -v | Out-File -Encoding utf8 raport_testow.txt
```
