import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os

DB_PATH = os.path.join("data", "constancias.db")

class GestionEventos(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Gestión de Eventos")
        self.geometry("600x400")
        self.resizable(False, False)

        self._build_ui()
        self._load_eventos()

    def _build_ui(self):
        columns = ("ID", "Nombre", "Fecha")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=180)
        self.tree.pack(pady=10)

        form_frame = tk.Frame(self)
        form_frame.pack(pady=10)

        tk.Label(form_frame, text="Nombre:").grid(row=0, column=0)
        self.nombre_entry = tk.Entry(form_frame)
        self.nombre_entry.grid(row=0, column=1, padx=5)

        tk.Label(form_frame, text="Fecha (YYYY-MM-DD):").grid(row=1, column=0)
        self.fecha_entry = tk.Entry(form_frame)
        self.fecha_entry.grid(row=1, column=1, padx=5)

        btn_frame = tk.Frame(self)
        btn_frame.pack()

        ttk.Button(btn_frame, text="Agregar", command=self.agregar_evento).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="Editar", command=self.editar_evento).grid(row=0, column=1, padx=5)
        ttk.Button(btn_frame, text="Eliminar", command=self.eliminar_evento).grid(row=0, column=2, padx=5)
        ttk.Button(btn_frame, text="Actualizar", command=self._load_eventos).grid(row=0, column=3, padx=5)

        self.tree.bind("<<TreeviewSelect>>", self._cargar_datos_seleccionados)

    def _load_eventos(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, fecha FROM eventos")
        for evento in cursor.fetchall():
            self.tree.insert("", "end", values=evento)
        conn.close()

    def agregar_evento(self):
        nombre = self.nombre_entry.get().strip()
        fecha = self.fecha_entry.get().strip()

        if not nombre or not fecha:
            messagebox.showwarning("Campos vacíos", "Por favor complete todos los campos.")
            return

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO eventos (nombre, fecha) VALUES (?, ?)", (nombre, fecha))
        conn.commit()
        conn.close()

        self._load_eventos()
        self.nombre_entry.delete(0, tk.END)
        self.fecha_entry.delete(0, tk.END)

    def editar_evento(self):
        selected = self.tree.selection()
        if not selected:
            return
        evento_id = self.tree.item(selected[0])["values"][0]

        nombre = self.nombre_entry.get().strip()
        fecha = self.fecha_entry.get().strip()

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("UPDATE eventos SET nombre = ?, fecha = ? WHERE id = ?", (nombre, fecha, evento_id))
        conn.commit()
        conn.close()

        self._load_eventos()

    def eliminar_evento(self):
        selected = self.tree.selection()
        if not selected:
            return
        evento_id = self.tree.item(selected[0])["values"][0]

        if messagebox.askyesno("Confirmar eliminación", "¿Deseas eliminar este evento?"):
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM eventos WHERE id = ?", (evento_id,))
            conn.commit()
            conn.close()
            self._load_eventos()

    def _cargar_datos_seleccionados(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        _, nombre, fecha = self.tree.item(selected[0])["values"]
        self.nombre_entry.delete(0, tk.END)
        self.nombre_entry.insert(0, nombre)
        self.fecha_entry.delete(0, tk.END)
        self.fecha_entry.insert(0, fecha)
