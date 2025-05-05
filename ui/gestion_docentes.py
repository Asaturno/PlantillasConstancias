import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import unicodedata
import re

def strip_accents_and_upper(texto):
    if not texto:
        return ""
    # Eliminar acentos
    texto = unicodedata.normalize('NFD', texto)
    texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')
    # Convertir a mayúsculas
    texto = texto.upper()
    # Eliminar espacios y signos de puntuación comunes
    texto = re.sub(r'[ .,\-]', '', texto)
    return texto.strip().strip()

def strip_accents_and_upper(texto):
    if not texto:
        return ""
    texto = unicodedata.normalize('NFD', texto)
    texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')
    return texto.upper().strip()

class GestorDocentes(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Gestión de Docentes")
        self.geometry("400x400")
        self.conn = sqlite3.connect("data/constancias.db")
        self.cursor = self.conn.cursor()
        self._build_ui()
        self._cargar_docentes()
        self.modo_edicion = False
        self.registro_id = None

    def _build_ui(self):
        frame = ttk.Frame(self)
        frame.pack(padx=10, pady=10, fill=tk.X)

        ttk.Label(frame, text="Nombre:").pack()
        self.nombre_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.nombre_var).pack(fill=tk.X)

        ttk.Label(frame, text="Grado:").pack()
        self.grado_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.grado_var).pack(fill=tk.X)

        self.btn_agregar = ttk.Button(frame, text="Agregar", command=self._guardar_docente)
        self.btn_agregar.pack(pady=10)

        self.lista = tk.Listbox(self)
        self.lista.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=5)

        ttk.Button(btn_frame, text="Editar", command=self._editar_docente).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Eliminar", command=self._eliminar_docente).pack(side=tk.LEFT, padx=5)

    def _guardar_docente(self):
        nombre = self.nombre_var.get().strip()
        grado = self.grado_var.get().strip()
        if not nombre or not grado:
            messagebox.showwarning("Campos vacíos", "Debes ingresar nombre y grado.")
            return

        self.cursor.execute("SELECT id, nombre, grado FROM docentes")
        nuevo_normalizado = strip_accents_and_upper(nombre + grado)
        for row in self.cursor.fetchall():
            existente_normalizado = strip_accents_and_upper(row[1] + row[2])
            if existente_normalizado == nuevo_normalizado:
                messagebox.showwarning("Duplicado", "Ya existe un docente con el mismo nombre y grado.")
                return

        if self.modo_edicion and self.registro_id is not None:
            self.cursor.execute("UPDATE docentes SET nombre = ?, grado = ? WHERE id = ?",
                                (nombre, grado, self.registro_id))
            self.conn.commit()
            self.btn_agregar.config(text="Agregar")
            self.modo_edicion = False
            self.registro_id = None
        else:
            self.cursor.execute("INSERT INTO docentes (nombre, grado) VALUES (?, ?)", (nombre, grado))
            self.conn.commit()

        self.nombre_var.set("")
        self.grado_var.set("")
        self._cargar_docentes()

    def _cargar_docentes(self):
        self.lista.delete(0, tk.END)
        self.cursor.execute("SELECT id, nombre, grado FROM docentes ORDER BY nombre")
        self.registros = self.cursor.fetchall()
        for docente in self.registros:
            self.lista.insert(tk.END, f"{docente[2]} {docente[1]}")

    def _editar_docente(self):
        seleccion = self.lista.curselection()
        if not seleccion:
            return
        index = seleccion[0]
        registro = self.registros[index]
        self.registro_id = registro[0]
        self.nombre_var.set(registro[1])
        self.grado_var.set(registro[2])
        self.btn_agregar.config(text="Actualizar")
        self.modo_edicion = True

    def _eliminar_docente(self):
        seleccion = self.lista.curselection()
        if not seleccion:
            return
        index = seleccion[0]
        docente_id = self.registros[index][0]
        confirm = messagebox.askyesno("Eliminar", "¿Deseas eliminar este docente?")
        if confirm:
            self.cursor.execute("DELETE FROM docentes WHERE id = ?", (docente_id,))
            self.conn.commit()
            self._cargar_docentes()
