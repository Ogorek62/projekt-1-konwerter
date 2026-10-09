# 🔄 Uniwersalny Konwerter Plików
 
Prosta aplikacja w Pythonie do konwersji plików między różnymi formatami (np. **CSV ⇄ JSON**).
 
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
python -m konwerter
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
    └── test_csv_json.py 
```
 
---
 
## ✅ TODO
 
- [x] Przetestować różne sytuacje konwersji
- [ ] Ulepszyc konwerter csv -> json
- [ ] Obsługa błędów - sobota
- [x] dodać automatyczne testowanie
- [x] sprawdzenie wyniku funkcji - sobota
- [ ] zrobić konwersje pdf i inne - niedziela

