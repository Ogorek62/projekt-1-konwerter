<div align="center">

# 🔄 Uniwersalny Konwerter Plików

**Aplikacja desktopowa (Python 3 + Tkinter/ttk) do konwersji plików między wybranymi formatami.**

Projekt 1 – Programowanie V

</div>

---

## 📚 Spis treści

- [🎯 Cel projektu](#-cel-projektu)
- [✨ Obsługiwane konwersje](#-obsługiwane-konwersje)
- [🧰 Wymagania](#-wymagania)
- [🚀 Instalacja](#-instalacja)
- [▶️ Uruchomienie](#️-uruchomienie)
- [💻 Obsługa programu](#-obsługa-programu)
- [📋 Specyfikacja formatów](#-specyfikacja-formatów)
- [⚠️ Obsługa błędów i logi](#️-obsługa-błędów-i-logi)
- [🧪 Testy](#-testy)
- [📁 Struktura projektu](#-struktura-projektu)
- [🚧 Znane ograniczenia](#-znane-ograniczenia)
- [📖 Biblioteki i źródła](#-biblioteki-i-źródła)
- [🤖 Użycie AI](#-użycie-ai)
- [👤 Autor](#-autor)

---

## 🎯 Cel projektu

Aplikacja pozwala wybrać plik wejściowy, pokazuje **tylko te formaty docelowe, które są dla niego dostępne**, wykonuje konwersję i zapisuje wynik we wskazanym katalogu.

Program nie obiecuje „dowolnej konwersji”. Obsługuje zamkniętą listę par formatów, widoczną w oknie programu w panelu **„Możliwe konwersje”**.

---

## ✨ Obsługiwane konwersje

Macierz wspieranych par (7 kierunków z 3 grup):

| Grupa | Konwersja | Narzędzie | Znane ograniczenia |
|-------|-----------|-----------|--------------------|
| **A – dane strukturalne** | **CSV → JSON** | `csv`, `json` (biblioteka standardowa) | wszystkie wartości trafiają do JSON jako tekst; wejście tylko w UTF-8 |
| | **JSON → CSV** | `csv`, `json` | tylko płaski JSON (bez zagnieżdżeń i list w wartościach); `true/false` zapisywane jako `True/False` |
| **B – tekst i dokumenty** | **TXT → DOCX** | `python-docx` | jedna linia = jeden akapit, brak formatowania; wejście tylko w UTF-8 |
| | **TXT → PDF** | `fpdf2` + czcionka `fonts/ARIAL.TTF` | stała czcionka Arial 15 pt, długie linie są zawijane; wejście tylko w UTF-8 |
| | **DOCX → TXT** | `python-docx` | przenoszony jest tylko tekst akapitów; tabele, nagłówki/stopki i obrazy są pomijane |
| **C – formaty biurowe** | **DOCX → PDF** | LibreOffice (tryb `--headless`) | wymaga zainstalowanego LibreOffice; limit czasu 60 s |
| | **ODT → PDF** | LibreOffice (tryb `--headless`) | jak wyżej |

Nie jest wymagane zachowanie złożonego formatowania, wykresów, przypisów ani identycznego układu stron.

---

## 🧰 Wymagania

| Zależność | Wersja | Do czego |
|-----------|--------|----------|
| **Python** | 3.10 lub nowszy (testowane na 3.13) | uruchomienie programu |
| **Tkinter** | dołączony do Pythona z python.org | interfejs graficzny |
| **python-docx**, **fpdf2**, **pytest**, **pypdf** | wg `requirements.txt` | konwersje DOCX/PDF, testy (pypdf: odczyt treści PDF w testach) |
| **LibreOffice** | dowolna aktualna | **tylko** konwersje DOCX → PDF i ODT → PDF |

### LibreOffice (zależność systemowa)

Pobierz i zainstaluj ze strony **https://www.libreoffice.org/download/**.

Program szuka LibreOffice w tej kolejności:
1. polecenie `soffice` lub `libreoffice` w zmiennej `PATH` (Linux/macOS: zwykle dostępne po instalacji),
2. `C:\Program Files\LibreOffice\program\soffice.exe`,
3. `C:\Program Files (x86)\LibreOffice\program\soffice.exe`.

Jeśli LibreOffice zainstalowano w innym miejscu, dodaj katalog `program` z instalacji do zmiennej `PATH`.
Bez LibreOffice pozostałe 5 konwersji działa normalnie, a przy próbie konwersji do PDF przez LibreOffice program pokaże błąd *„Nie znaleziono LibreOffice (soffice.exe)”*.

---

## 🚀 Instalacja

Wszystkie polecenia wykonuj w **katalogu głównym projektu**.

### 1. Utworzenie środowiska wirtualnego

```bash
python -m venv .venv
```

### 2. Aktywacja środowiska

```bash
# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Windows (cmd)
.venv\Scripts\activate.bat

# Linux / macOS
source .venv/bin/activate
```

### 3. Instalacja bibliotek

```bash
pip install -r requirements.txt
```

---

## ▶️ Uruchomienie

```bash
python -m konwerter
```

Otworzy się okno programu.

### Konwersja bez GUI

Logikę konwersji można wywołać bezpośrednio z Pythona, bez interfejsu:

```bash
python -c "from pathlib import Path; from konwerter.converters import ConversionRequest, execute; print(execute(ConversionRequest(Path('samples/csv_przecinek.csv'), '.json', Path('.'))))"
```

`ConversionRequest(plik_wejściowy, format_docelowy, katalog_zapisu)` opisuje konwersję, a `execute()` ją sprawdza i wykonuje.

---

## 💻 Obsługa programu

1. **Format wejściowy** (opcjonalnie): zawęża okno wyboru pliku do danego rozszerzenia.
2. **Plik → „Wybierz...”**: wybór pliku do konwersji. Katalog zapisu ustawia się domyślnie na katalog pliku.
3. **Katalog zapisu → „Wybierz...”**: zmiana katalogu, w którym zostanie zapisany wynik.
4. **Konwertuj na**: lista zawiera **tylko formaty dostępne dla wybranego pliku**.
5. **„Konwertuj”**: przycisk jest aktywny dopiero wtedy, gdy wybrano plik, katalog i format.

Kliknięcie pozycji w panelu **„Możliwe konwersje”** ustawia format wejściowy i docelowy.

- Plik wynikowy ma nazwę pliku wejściowego z nowym rozszerzeniem, np. `dane.csv` → `dane.json`.
- **Jeśli plik o tej nazwie już istnieje**, program pyta, czy go nadpisać. Odpowiedź „Nie” anuluje konwersję.
- Konwersja działa w osobnym wątku, więc okno nie zawiesza się przy dłuższych operacjach (np. LibreOffice). Status widać pod przyciskiem.

---

## 📋 Specyfikacja formatów

### 🔤 Kodowanie

| Plik | Kodowanie |
|------|-----------|
| CSV, JSON, TXT (wejście) | UTF-8, z BOM lub bez |
| JSON, TXT (wyjście) | UTF-8, polskie znaki zapisane wprost (`ensure_ascii=False`) |
| CSV (wyjście) | UTF-8 z BOM, dzięki czemu Excel poprawnie wyświetla polskie znaki |
| Inne kodowania (np. Windows-1250) | ❌ nieobsługiwane: program pokaże błąd z prośbą o zapisanie pliku w UTF-8 |

### ➗ Separatory (CSV → JSON)

Separator jest **wykrywany automatycznie** (na podstawie pierwszych 4 KB pliku) spośród: przecinka `,`, średnika `;`, tabulatora i pionowej kreski `|`.
Jeśli wykrycie się nie powiedzie, używany jest średnik `;`.
Plik wynikowy CSV (JSON → CSV) zawsze ma separator `,`.

### 🏷️ Obsługa nagłówków

- **CSV → JSON**: pierwszy wiersz to nagłówek, a jego wartości stają się kluczami obiektów JSON. **Kolejność kolumn jest zachowana.** Wartości są zawsze tekstem (`007` zostaje `"007"`), a puste pola zostają pustym tekstem `""`.
- **JSON → CSV**: nagłówek to **suma kluczy ze wszystkich obiektów**, w kolejności ich pierwszego wystąpienia. Brakujące wartości i `null` dają puste pole.

### 🧱 Akceptowana struktura JSON

✅ **Obsługiwane**: lista płaskich obiektów albo pojedynczy płaski obiekt:

```json
[
    { "imię": "Anna", "wiek": 28 },
    { "imię": "Jan",  "miasto": "Opole" }
]
```

❌ **Nieobsługiwane**:

| Przykład | Komunikat |
|----------|-----------|
| `[{"adres": {"miasto": "Opole"}}]`, `[{"hobby": ["rower"]}]` | *Zagnieżdżony JSON* |
| `[1, 2, 3]`, `[[1, 2]]` | *Nieobsługiwana struktura JSON* |
| `[]` | *Plik nie zawiera żadnych danych* |
| błąd składni | *Plik JSON jest uszkodzony* (z numerem linii) |

---

## ⚠️ Obsługa błędów i logi

Program nie kończy działania przy błędnych danych, tylko pokazuje okno z przyczyną błędu:

| Sytuacja | Zachowanie |
|----------|------------|
| brak pliku / katalogu | komunikat i blokada przycisku „Konwertuj”, dopóki nie wybrano pliku, katalogu i formatu |
| nieobsługiwana para formatów | opcja niewidoczna na liście „Konwertuj na” |
| brak uprawnień do zapisu | komunikat *„Brak uprawnień do zapisu w katalogu”* |
| plik docelowy istnieje | pytanie o nadpisanie |
| uszkodzony plik / złe kodowanie / pusty plik | komunikat z przyczyną (patrz wyżej) |
| brak LibreOffice | komunikat *„Nie znaleziono LibreOffice”*; instrukcja w sekcji [Wymagania](#libreoffice-zależność-systemowa) |
| LibreOffice nie odpowiada | przerwanie po 60 s i komunikat *„Przekroczono czas”* |

Wszystkie konwersje (start, czas trwania, wynik) i błędy są zapisywane do pliku **`konwerter.log`** w katalogu, z którego uruchomiono program.

---

## 🧪 Testy

Testy automatyczne (pytest) znajdują się w folderze `test/`, a dane testowe w `samples/`. Opis oczekiwanego wyniku dla każdego pliku jest w [`samples/OPIS.md`](samples/OPIS.md).

```bash
pytest          # uruchomienie wszystkich testów
pytest -v       # z listą testów i wynikiem każdego z nich
```

| Plik | Co testuje |
|------|------------|
| `test/test_rejestr.py` | `available_targets()`, `ConversionRequest.validate()`, nadpisywanie plików, brak LibreOffice |
| `test/test_dane.py` | CSV → JSON i JSON → CSV: poprawne i błędne dane, polskie znaki, puste wartości |
| `test/test_dokumenty.py` | TXT → DOCX/PDF, DOCX → TXT, DOCX/ODT → PDF |

Testy wymagające LibreOffice są automatycznie **pomijane** (`SKIPPED`), jeśli LibreOffice nie jest zainstalowany.

Zapis wyniku do pliku (PowerShell):

```powershell
pytest -v | Out-File -Encoding utf8 raport_testow.txt
```

Omówienie wyników: [`RAPORT_TESTOW.md`](RAPORT_TESTOW.md).

---

## 📁 Struktura projektu

```
projekt-1-konwerter/
├── README.md
├── RAPORT_TESTOW.md     # raport z testów
├── raport_testow.txt    # surowy wynik pytest -v
├── requirements.txt
├── pytest.ini           # konfiguracja testów
├── fonts/
│   └── ARIAL.TTF        # czcionka z polskimi znakami dla TXT → PDF
├── konwerter/
│   ├── __main__.py      # punkt wejścia (python -m konwerter), konfiguracja logów
│   ├── gui.py           # interfejs Tkinter/ttk
│   ├── converters.py    # rejestr konwerterów, walidacja, execute(), konwertery
│   └── errors.py        # własne wyjątki
├── samples/             # dane testowe + OPIS.md
└── test/                # testy automatyczne (pytest)
```

**Architektura:** GUI (`gui.py`) nie zna szczegółów konwersji. Pobiera listę formatów z `available_targets()` i uruchamia konwersję przez `execute()`.
Każdy konwerter rejestruje się dekoratorem `@converter(".źródło", ".cel")`. Nowa para formatów to jedna nowa funkcja w `converters.py`, bez zmian w GUI.

---

## 🚧 Znane ograniczenia

- Obsługiwane jest tylko kodowanie **UTF-8** plików tekstowych (CSV, JSON, TXT).
- CSV → JSON nie rozpoznaje typów danych: liczby i wartości logiczne zostają tekstem.
- Przy powtarzających się nazwach kolumn w CSV zostaje wartość z ostatniej z nich.
- JSON → CSV obsługuje tylko płaską strukturę.
- Konwersje dokumentów przenoszą treść, nie formatowanie (pogrubienia, tabele, obrazy, przypisy).
- Konwersje przez LibreOffice mogą się nie udać, jeśli LibreOffice jest w tym samym czasie otwarty przez użytkownika. Należy go wtedy zamknąć i spróbować ponownie.
- Nazwa pliku wynikowego jest zawsze `<nazwa_wejściowa>.<nowe_rozszerzenie>` i nie można jej zmienić.

---

## 📖 Biblioteki i źródła

| Biblioteka / narzędzie | Zastosowanie | Dokumentacja |
|------------------------|--------------|--------------|
| `tkinter` / `ttk` | interfejs graficzny, okna wyboru plików | https://docs.python.org/3/library/tkinter.html |
| `csv`, `json`, `pathlib`, `subprocess`, `logging` | biblioteka standardowa Pythona | https://docs.python.org/3/library/ |
| `python-docx` | odczyt i tworzenie plików DOCX | https://python-docx.readthedocs.io/ |
| `fpdf2` | tworzenie plików PDF z tekstu | https://py-pdf.github.io/fpdf2/ |
| `pypdf` | odczyt tekstu z plików PDF w testach | https://pypdf.readthedocs.io/ |
| LibreOffice | konwersja DOCX/ODT → PDF w trybie headless | https://help.libreoffice.org/latest/en-US/text/shared/guide/start_parameters.html |
| `pytest` | testy automatyczne | https://docs.pytest.org/ |

Wzorzec rejestru konwerterów (`REGISTRY`, `@converter`, `ConversionRequest`, `available_targets`, `execute`) pochodzi z „Kodu inspiracyjnego” w instrukcji projektowej.

---

## 🤖 Użycie AI

W projekcie korzystano z asystenta AI **Claude (Anthropic)**. AI użyto do pomocy w:

- pisaniu **README**,
- tworzeniu **interfejsu użytkownika (UI)**,
- pisaniu **testów**,
- **poprawkach błędów** w kodzie,
- **zrozumieniu kodu napisanego przez AI**.

---

## 👤 Autor

**Mateusz Gorecki**
