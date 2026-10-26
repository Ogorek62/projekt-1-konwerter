import tkinter as tk
from tkinter import ttk

root = tk.Tk()

root.title("Konwerter")
ttk.Label(root, text="Cześć").pack()
ttk.Button(root, text="Kliknij", command=lambda: print("klik")).pack()
root.mainloop()