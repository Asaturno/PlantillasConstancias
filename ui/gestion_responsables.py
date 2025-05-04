import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os

DB_PATH = os.path.join("data", "constancias.db")

class GestionResponsables(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Gestión de Responsables")
        self.geometry("650x400")
        self.resizable(False, False)

        self._build_ui()
        self._load_responsables()

    def _build_ui(self):
        columns = ("ID", "Grado", "Nombre", "Rol")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        self.tree.pack(pady=10)

        form_frame = tk.Frame(self)
        form_frame.pack(pady=10)

        tk.Label(form_frame, text="Grado:").grid(row=0, column=0)
        self.grado_entry = tk.Entry(form_frame)
        self.grado_entry.grid(row=0, column=1, padx=5)

        tk.Label(form_frame, text="Nombre:").grid(row=1, column=0)
        self.nombre_entry = tk.Entry(form_frame)
        self.nombre_entry.grid(row=1, column=1, padx=5)

        tk.Label(form_frame, text="Rol:").grid(row=2, column=0)
        self.rol_entry = tk.Entry(form_frame)
        self.rol_entry.grid(row=2, column=1, padx=5)

        btn_frame = tk.Frame(self)
        btn_frame.pack()

        ttk.Button(btn_frame, text="Agregar", command=self.agregar_responsable).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="Editar", command=self.editar_responsable).grid(row=0, column=1, padx=5)
        ttk.Button(btn_frame, text="Eliminar", command=self.eliminar_responsable).grid(row=0, column=2, padx=5)
        ttk.Button(btn_frame, text="Actualizar", command=self._load_responsables).grid(row=0, column=3, padx=5)

        self.tree.bind("<<TreeviewSelect>>", self._cargar_datos_seleccionados)

    def _load_responsables(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, grado, nombre, rol FROM responsables")
        for responsable in cursor.fetchall():
            self.tree.insert("", "end", values=responsable)
        conn.close()

    def agregar_responsable(self):
        grado = self.grado_entry.get().strip()
        nombre = self.nombre_entry.get().strip()
        rol = self.rol_entry.get().strip()

        if not grado or not nombre or not rol:
            messagebox.showwarning("Campos vacíos", "Por favor complete todos los campos.")
            return

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO responsables (grado, nombre, rol) VALUES (?, ?, ?)", (grado, nombre, rol))
        conn.commit()
        conn.close()

        self._load_responsables()
        self.grado_entry.delete(0, tk.END)
        self.nombre_entry.delete(0, tk.END)
        self.rol_entry.delete(0, tk.END)

    def editar_responsable(self):
        selected = self.tree.selection()
        if not selected:
            return
        responsable_id = self.tree.item(selected[0])["values"][0]

        grado = self.grado_entry.get().strip()
        nombre = self.nombre_entry.get().strip()
        rol = self.rol_entry.get().strip()

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("UPDATE responsables SET grado = ?, nombre = ?, rol = ? WHERE id = ?", (grado, nombre, rol, responsable_id))
        conn.commit()
        conn.close()

        self._load_responsables()

    def eliminar_responsable(self):
        selected = self.tree.selection()
        if not selected:
            return
        responsable_id = self.tree.item(selected[0])["values"][0]

        if messagebox.askyesno("Confirmar eliminación", "¿Deseas eliminar este responsable?"):
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM responsables WHERE id = ?", (responsable_id,))
            conn.commit()
            conn.close()
            self._load_responsables()

    def _cargar_datos_seleccionados(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        _, grado, nombre, rol = self.tree.item(selected[0])["values"]
        self.grado_entry.delete(0, tk.END)
        self.grado_entry.insert(0, grado)
        self.nombre_entry.delete(0, tk.END)
        self.nombre_entry.insert(0, nombre)
        self.rol_entry.delete(0, tk.END)
        self.rol_entry.insert(0, rol)
