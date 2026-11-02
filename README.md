<div align="center">

# 🔄 Uniwersalny Konwerter Plików

**Prosty konwerter plików w Pythonie — obecnie CSV ⇄ JSON**



---

## 📚 Spis treści

- [✨ Możliwości](#-możliwości)
- [🚀 Szybki start](#-szybki-start)
- [💻 Użycie](#-użycie)
- [📋 Specyfikacja formatów](#-specyfikacja-formatów)
- [🧪 Testy](#-testy)
- [📁 Struktura projektu](#-struktura-projektu)
- [✅ TODO](#-todo)

---

## ✨ Możliwości

Aktualnie dostępne konwersje:

| Konwersja | Status | Opis |
|-----------|:------:|------|
| **CSV → JSON** | ✅ Działa | Automatyczne wykrywanie separatora, nagłówki z pierwszego wiersza |
| **JSON → CSV** | ✅ Działa | Obsługa płaskich obiektów, wspólny nagłówek z kluczy |
| CSV / JSON → PDF | 🚧 Planowane | — |
| Inne formaty (XML, XLSX…) | 🚧 Planowane | — |

---

## 🚀 Szybki start

### 1. Utworzenie środowiska wirtualnego

```bash
python -m venv .venv
```

Aktywacja środowiska:

```bash
# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate
```

### 2. Instalacja bibliotek

```bash
pip install -r requirements.txt
```

### 3. Uruchomienie programu

```bash
python -m konwerter -i <plik_wejściowy> -o <plik_wyjściowy>
```

---

## 💻 Użycie

| Argument | Opis |
|----------|------|
| `-i`, `--Input` | nazwa pliku wejściowego (szukanego w folderze `samples/`) |
| `-o`, `--Output` | nazwa pliku wynikowego (zapisywanego w folderze `output/`) |

Kierunek konwersji jest wybierany **automatycznie** na podstawie rozszerzenia pliku wejściowego (`.csv` lub `.json`).

**Przykłady:**

```bash
# CSV → JSON
python -m konwerter -i dane.csv -o dane.json

# JSON → CSV
python -m konwerter -i dane.json -o dane.csv
```

> 💡 Programy uruchamiaj z katalogu głównego projektu — foldery `samples/` i `output/` są wyszukiwane względem bieżącego katalogu.

---

## 📋 Specyfikacja formatów

### 🔤 Kodowanie

| Plik | Kodowanie | Status |
|------|-----------|:------:|
| CSV (wejście) | UTF-8 oraz UTF-8 z BOM (`utf-8-sig`) | ✅ Obsługiwane |
| JSON (wejście) | UTF-8 | ✅ Obsługiwane |
| JSON (wyjście) | UTF-8, polskie znaki zachowane (`ensure_ascii=False`) | ✅ |
| CSV (wyjście) | UTF-8 z BOM — poprawne otwieranie w Excelu | ✅ |
| Dowolny plik | `cp1250` (Windows-1250) | ❌ Nieobsługiwane |

### ➗ Separatory (CSV → JSON)

Separator jest **wykrywany automatycznie** spośród:

| Separator | Znak |
|-----------|:----:|
| przecinek | `,` |
| średnik | `;` |
| tabulator | `\t` |
| pionowa kreska | `\|` |

Jeśli wykrycie się nie powiedzie, używany jest domyślny separator `;`.
W pliku wynikowym CSV (JSON → CSV) separatorem jest przecinek `,`.

### 🏷️ Obsługa nagłówków

- **CSV → JSON** — pierwszy wiersz pliku jest traktowany jako nagłówek; jego wartości stają się kluczami w obiektach JSON.
- **JSON → CSV** — nagłówek tworzony jest z **sumy wszystkich kluczy** występujących w obiektach, w kolejności ich pojawiania się. Brakujące wartości zostają puste.
- Wszystkie wartości z CSV trafiają do JSON jako **tekst** (konwerter nie zgaduje typów liczbowych ani logicznych).

### 🧱 Akceptowalna struktura JSON

✅ **Obsługiwane** — tablica płaskich obiektów albo pojedynczy płaski obiekt:

```json
[
    { "imie": "Anna", "wiek": 28 },
    { "imie": "Jan",  "miasto": "Opole" }
]
```

❌ **Nieobsługiwane** — zagnieżdżone obiekty i listy (zgłaszany jest błąd `JsonIsNested`):

```json
[
    { "imie": "Anna", "adres": { "miasto": "Opole" }, "hobby": ["rower", "książki"] }
]
```


---

## 🧪 Testy

```bash
pytest -s test/test_csv.py

# lub

pytest -s test/test_json.py
```

---

## 📁 Struktura projektu

```
projekt-1-konwerter/
├── .gitignore
├── README.md
├── requirements.txt
├── konwerter/
│   ├── __init__.py
│   ├── __main__.py      # punkt wejścia programu
│   └── errors.py        # własne wyjątki
├── output/              # pliki wynikowe
├── samples/             # przykładowe dane
│   ├── dane.csv
│   ├── dane.json
│   └── zly.json         # celowo błędny plik do testów
└── test/
    ├── test_csv.py
    └── test_json.py
```

---
