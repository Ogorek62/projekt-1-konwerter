import os
import queue
import shutil
import subprocess
import tempfile
import threading
import tkinter as tk
from pathlib import Path
from tkinter import ttk, filedialog, messagebox

from konwerter.converters import REGISTRY
from konwerter.errors import CorruptedInputFile, EmptyInputFile, JsonIsNested

ANY_FORMAT = "Wszystkie"


class ConvertApp:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("konwerter")
        self.window.geometry("720x380")
        self.window.columnconfigure(1, weight=1)

        self.sources = sorted({src for src, _ in REGISTRY})
        self.all_pairs: list[tuple[str, str]] = sorted(REGISTRY)  # wszystkie konwersje (lista po prawej)
        self.pairs: list[tuple[str, str]] = []  # konwersje pasujące do aktualnego formatu wejściowego
        self.result_queue: queue.Queue = queue.Queue()
        self.busy = False  # True w trakcie konwersji

        # --- Lewa strona: formularz ---
        left = tk.Frame(self.window)
        left.grid(row=0, column=0, sticky="n", padx=10, pady=10)

        # Wiersz 0: format wejściowy
        tk.Label(left, text="Format wejściowy:").grid(row=0, column=0, padx=5, pady=10, sticky="e")
        self.input_format = ttk.Combobox(
            left, values=[ANY_FORMAT] + self.sources, state="readonly", width=20
        )
        self.input_format.current(0)
        self.input_format.grid(row=0, column=1, columnspan=2, padx=5, pady=10, sticky="ew")
        self.input_format.bind("<<ComboboxSelected>>", self.on_input_format_change)

        # Wiersz 1: plik (tylko do odczytu - ścieżkę ustawia się przyciskiem "Wybierz...")
        tk.Label(left, text="Plik:").grid(row=1, column=0, padx=5, pady=10, sticky="e")
        self.file_var = tk.StringVar()
        self.field_file = tk.Entry(
            left, width=30, textvariable=self.file_var, state="readonly"
        )
        self.field_file.grid(row=1, column=1, padx=5, pady=10)
        tk.Button(left, text="Wybierz...", command=self.choose_file).grid(
            row=1, column=2, padx=5, pady=10
        )

        # Wiersz 2: format docelowy
        tk.Label(left, text="Konwertuj na:").grid(row=2, column=0, padx=5, pady=10, sticky="e")
        self.format_list = ttk.Combobox(left, state="readonly", width=20)
        self.format_list.grid(row=2, column=1, columnspan=2, padx=5, pady=10, sticky="ew")
        self.format_list.bind("<<ComboboxSelected>>", lambda e: self.update_status())

        # Wiersz 3: konwersja
        self.button_convert = tk.Button(
            left, text="Konwertuj i zapisz jako...", command=self.convert_and_save
        )
        self.button_convert.grid(row=3, column=0, columnspan=3, pady=15)

        # Wiersz 4: status
        self.label_result = tk.Label(left, text="", wraplength=330, justify="left")
        self.label_result.grid(row=4, column=0, columnspan=3)

        # --- Prawa strona: lista możliwych konwersji ---
        right = tk.LabelFrame(self.window, text="Możliwe konwersje")
        right.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.window.rowconfigure(0, weight=1)
        right.rowconfigure(0, weight=1)
        right.columnconfigure(0, weight=1)

        self.listbox = tk.Listbox(right, exportselection=False)
        self.listbox.grid(row=0, column=0, sticky="nsew", padx=(5, 0), pady=5)
        scroll = ttk.Scrollbar(right, orient="vertical", command=self.listbox.yview)
        scroll.grid(row=0, column=1, sticky="ns", pady=5)
        self.listbox.config(yscrollcommand=scroll.set)
        self.listbox.bind("<<ListboxSelect>>", self.on_list_select)

        # lista po prawej jest stała - wypełniamy ją raz, wszystkimi konwersjami
        for a, b in self.all_pairs:
            self.listbox.insert(tk.END, f"{a}  →  {b}")

        self.refresh()

    # ------------------------------------------------------------------ pomocnicze
    def current_file_ext(self):
        path = self.file_var.get().strip()
        return Path(path).suffix.lower() if path else None

    def current_source(self):
        """Rozszerzenie wejściowe wynikające z pliku lub z wyboru formatu wejściowego."""
        ext = self.current_file_ext()
        if ext:
            return ext
        selected = self.input_format.get()
        return None if selected == ANY_FORMAT else selected

    def refresh(self):
        """Odświeża pole 'Konwertuj na' (lista po prawej się nie zmienia)."""
        src = self.current_source()
        self.pairs = [k for k in self.all_pairs if src is None or k[0] == src]

        targets = list(dict.fromkeys(b for _, b in self.pairs))
        self.format_list.config(values=targets)
        if targets:
            self.format_list.current(0)
        else:
            self.format_list.set("")
        self.update_status()

    def update_status(self):
        src = self.current_source()
        target = self.format_list.get()
        if src and not self.pairs:
            self.label_result.config(text=f"Brak konwersji dla formatu {src}")
        elif target:
            name = os.path.basename(self.file_var.get())
            self.label_result.config(text=f"Plik: {name or '-'} → format: {target}")
        else:
            self.label_result.config(text="")
        self.update_button_state()

    def update_button_state(self):
        """Przycisk aktywny tylko, gdy wybrano plik i nie trwa konwersja."""
        has_file = bool(self.file_var.get().strip())
        state = "normal" if has_file and not self.busy else "disabled"
        self.button_convert.config(state=state)

    # ------------------------------------------------------------------ zdarzenia
    def on_input_format_change(self, _event=None):
        selected = self.input_format.get()
        ext = self.current_file_ext()
        # wybrany plik nie pasuje do nowo wybranego formatu -> czyścimy pole pliku
        if ext and selected != ANY_FORMAT and ext != selected:
            self.file_var.set("")
        self.refresh()

    def on_list_select(self, _event=None):
        sel = self.listbox.curselection()
        if not sel:
            return
        src, tgt = self.all_pairs[sel[0]]
        self.input_format.set(src)
        if self.current_file_ext() and self.current_file_ext() != src:
            self.file_var.set("")
        self.refresh()  # dopasowuje pole 'Konwertuj na' do nowego formatu wejściowego
        self.format_list.set(tgt)
        self.update_status()

    def choose_file(self):
        selected = self.input_format.get()
        if selected != ANY_FORMAT:
            filetypes = [(f"Pliki {selected}", f"*{selected}"), ("Wszystkie pliki", "*.*")]
        else:
            patterns = tuple(f"*{s}" for s in self.sources)
            filetypes = [("Obsługiwane pliki", patterns)]
            filetypes += [(f"Pliki {s}", f"*{s}") for s in self.sources]
            filetypes.append(("Wszystkie pliki", "*.*"))

        path = filedialog.askopenfilename(title="Wybierz plik do konwersji", filetypes=filetypes)
        if not path:
            return

        self.file_var.set(path)
        ext = self.current_file_ext()
        if ext in self.sources:
            self.input_format.set(ext)
        self.refresh()

    # ------------------------------------------------------------------ konwersja
    def convert_and_save(self):
        source = self.file_var.get().strip()
        if not source:
            messagebox.showwarning("Brak pliku", "Najpierw wybierz plik do konwersji.")
            return
        if not os.path.isfile(source):
            messagebox.showerror("Błąd", f"Plik nie istnieje:\n{source}")
            return

        src_ext = Path(source).suffix.lower()
        tgt_ext = self.format_list.get()
        func = REGISTRY.get((src_ext, tgt_ext))
        if func is None:
            messagebox.showerror(
                "Błąd", f"Brak konwersji {src_ext or '(brak rozszerzenia)'} → {tgt_ext or '?'}."
            )
            return

        dest = filedialog.asksaveasfilename(
            title="Zapisz jako",
            defaultextension=tgt_ext,
            initialfile=Path(source).stem + tgt_ext,
            filetypes=[(f"Pliki {tgt_ext}", f"*{tgt_ext}"), ("Wszystkie pliki", "*.*")],
        )
        if not dest:
            return

        # konwersja w osobnym wątku, żeby okno się nie zawieszało
        self.busy = True
        self.update_button_state()
        self.label_result.config(text="Konwertuję, proszę czekać...")
        threading.Thread(
            target=self._worker, args=(func, Path(source), dest), daemon=True
        ).start()
        self.window.after(100, self._poll_result)

    def _worker(self, func, source: Path, dest: str):
        """Działa w osobnym wątku - bez żadnych wywołań tkintera."""
        try:
            # konwertery zapisują do katalogu, więc konwertujemy do tymczasowego
            # folderu, a wynik przenosimy pod wybraną przez użytkownika ścieżkę
            with tempfile.TemporaryDirectory() as tmp:
                result = func(source, Path(tmp))
                shutil.move(str(result), dest)
            self.result_queue.put(("ok", dest))
        except Exception as e:
            self.result_queue.put(("error", e))

    def _poll_result(self):
        try:
            status, payload = self.result_queue.get_nowait()
        except queue.Empty:
            self.window.after(100, self._poll_result)  # konwersja jeszcze trwa
            return

        self.busy = False
        self.update_button_state()
        if status == "ok":
            self.label_result.config(text=f"Zapisano: {payload}")
            messagebox.showinfo("Gotowe", f"Zapisano:\n{payload}")
        else:
            self.label_result.config(text="")
            self.show_error(payload)

    def show_error(self, e: Exception):
        if isinstance(e, EmptyInputFile):
            messagebox.showwarning("Pusty plik", str(e))
        elif isinstance(e, JsonIsNested):
            messagebox.showerror("Zagnieżdżony JSON", str(e))
        elif isinstance(e, CorruptedInputFile):
            messagebox.showerror("Uszkodzony plik", str(e))
        elif isinstance(e, FileNotFoundError):
            messagebox.showerror("Nie znaleziono pliku", str(e))
        elif isinstance(e, subprocess.TimeoutExpired):
            messagebox.showerror("Przekroczono czas", f"Konwersja trwała zbyt długo:\n{e}")
        elif isinstance(e, PermissionError):
            messagebox.showerror("Brak uprawnień", f"Nie można zapisać pliku:\n{e}")
        else:
            messagebox.showerror("Błąd konwersji", f"{type(e).__name__}: {e}")

    def start(self):
        self.window.mainloop()