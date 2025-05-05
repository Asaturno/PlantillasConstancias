import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

class GestorEventos(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Gestión de Eventos")
        self.geometry("400x400")
        self.conn = sqlite3.connect("data/constancias.db")
        self.cursor = self.conn.cursor()
        self._build_ui()
        self._cargar_eventos()
        self.modo_edicion = False
        self.registro_id = None

    def _build_ui(self):
        frame = ttk.Frame(self)
        frame.pack(padx=10, pady=10, fill=tk.X)

        ttk.Label(frame, text="Nombre del evento:").pack()
        self.nombre_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.nombre_var).pack(fill=tk.X)

        ttk.Label(frame, text="Fecha (dd/mm/aaaa):").pack()
        self.fecha_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.fecha_var).pack(fill=tk.X)

        self.btn_agregar = ttk.Button(frame, text="Agregar", command=self._guardar_evento)
        self.btn_agregar.pack(pady=10)

        self.lista = tk.Listbox(self)
        self.lista.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=5)

        ttk.Button(btn_frame, text="Editar", command=self._editar_evento).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Eliminar", command=self._eliminar_evento).pack(side=tk.LEFT, padx=5)

    def _guardar_evento(self):
        nombre = self.nombre_var.get().strip()
        fecha = self.fecha_var.get().strip()
        if not nombre or not fecha:
            messagebox.showwarning("Campos vacíos", "Debes ingresar nombre y fecha.")
            return

        self.cursor.execute("SELECT id FROM eventos WHERE nombre = ? AND fecha = ?", (nombre, fecha))
        existe = self.cursor.fetchone()
        if existe and (not self.modo_edicion or existe[0] != self.registro_id):
            messagebox.showwarning("Duplicado", "Ya existe un evento con ese nombre y fecha.")
            return

        if self.modo_edicion and self.registro_id is not None:
            self.cursor.execute("UPDATE eventos SET nombre = ?, fecha = ? WHERE id = ?",
                                (nombre, fecha, self.registro_id))
            self.conn.commit()
            self.btn_agregar.config(text="Agregar")
            self.modo_edicion = False
            self.registro_id = None
        else:
            self.cursor.execute("INSERT INTO eventos (nombre, fecha) VALUES (?, ?)", (nombre, fecha))
            self.conn.commit()

        self.nombre_var.set("")
        self.fecha_var.set("")
        self._cargar_eventos()

    def _cargar_eventos(self):
        self.lista.delete(0, tk.END)
        self.cursor.execute("SELECT id, nombre, fecha FROM eventos ORDER BY fecha DESC")
        self.registros = self.cursor.fetchall()
        for evento in self.registros:
            self.lista.insert(tk.END, f"{evento[1]} - {evento[2]}")

    def _editar_evento(self):
        seleccion = self.lista.curselection()
        if not seleccion:
            return
        index = seleccion[0]
        registro = self.registros[index]
        self.registro_id = registro[0]
        self.nombre_var.set(registro[1])
        self.fecha_var.set(registro[2])
        self.btn_agregar.config(text="Actualizar")
        self.modo_edicion = True

    def _eliminar_evento(self):
        seleccion = self.lista.curselection()
        if not seleccion:
            return
        index = seleccion[0]
        evento_id = self.registros[index][0]
        confirm = messagebox.askyesno("Eliminar", "¿Deseas eliminar este evento?")
        if confirm:
            self.cursor.execute("DELETE FROM eventos WHERE id = ?", (evento_id,))
            self.conn.commit()
            self._cargar_eventos()
