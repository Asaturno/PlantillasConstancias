import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import unicodedata
import re
import os

DB_PATH = os.path.expanduser("~") + "/OneDrive - Universidad Autónoma del Estado de México/UAEM/Proyecto Constancias/constancias.db"


def strip_accents_and_upper(texto):
    if not texto:
        return ""
    texto = unicodedata.normalize('NFD', texto)
    texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')
    texto = texto.upper()
    texto = re.sub(r'[ .,\-]', '', texto)
    return texto.strip()


class GestorResponsables(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Gestión de Responsables")
        self.geometry("700x550")

        self.style = ttk.Style()
        self._configurar_estilos()

        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        self.modo_edicion = False
        self.registro_id = None

        self._build_ui()
        self._cargar_responsables()

    def _configurar_estilos(self):
        """Configura los estilos visuales"""
        self.style.theme_use('clam')
        self.style.configure('.', background='#f5f5f5')
        self.style.configure('TFrame', background='#f5f5f5')
        self.style.configure('TLabel', background='#f5f5f5',
                             foreground='#333333', font=('Arial', 10))
        self.style.configure('Treeview', font=('Arial', 10), rowheight=25,
                             fieldbackground='#ffffff', foreground='#333333')
        self.style.configure('Treeview.Heading', font=('Arial', 10, 'bold'),
                             background='#3498db', foreground='white')
        self.style.configure('TEntry', font=('Arial', 10), padding=5)

        # Estilo global para todos los botones
        self.style.configure("TButton",
                             font=('Arial', 11),
                             padding=10,
                             background="#2E5E2E",
                             foreground="white",
                             borderwidth=2)

        self.style.map("TButton",
                       background=[('active', 'white')],
                       foreground=[('active', '#2E5E2E')],
                       bordercolor=[('active', '#a58a42')])

    def _build_ui(self):
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Formulario
        form_frame = ttk.LabelFrame(
            main_frame, text="Formulario de Responsable", padding="10")
        form_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(form_frame, text="Nombre:").grid(
            row=0, column=0, sticky="e", padx=5, pady=5)
        self.nombre_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.nombre_var, font=('Arial', 10)).grid(
            row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(form_frame, text="Grado:").grid(
            row=1, column=0, sticky="e", padx=5, pady=5)
        self.grado_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.grado_var, font=('Arial', 10)).grid(
            row=1, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(form_frame, text="Rol:").grid(
            row=2, column=0, sticky="e", padx=5, pady=5)
        self.rol_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.rol_var, font=('Arial', 10)).grid(
            row=2, column=1, padx=5, pady=5, sticky="ew")

        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=3, columnspan=2, pady=10)

        self.btn_agregar = ttk.Button(btn_frame, text="Agregar", command=self._guardar_responsable,
                                      style='Primary.TButton')
        self.btn_agregar.pack(side=tk.LEFT, padx=5)

        ttk.Button(btn_frame, text="Limpiar", command=self._limpiar_formulario,
                   style='Danger.TButton').pack(side=tk.LEFT, padx=5)

        # Lista de responsables
        list_frame = ttk.LabelFrame(
            main_frame, text="Responsables Registrados", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        columns = ('ID', 'Nombre', 'Grado', 'Rol')
        self.tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show='headings',
            selectmode='browse'
        )

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor='center')

        self.tree.column('Nombre', width=200)
        self.tree.column('Grado', width=150)
        self.tree.column('Rol', width=200)

        scrollbar = ttk.Scrollbar(
            list_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Botones de acción
        action_frame = ttk.Frame(list_frame)
        action_frame.pack(fill=tk.X, pady=5)

        ttk.Button(action_frame, text="Editar", command=self._editar_responsable,
                   style='Primary.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Eliminar", command=self._eliminar_responsable,
                   style='Danger.TButton').pack(side=tk.LEFT, padx=5)
        # ttk.Button(action_frame, text="Actualizar", command=self._cargar_responsables,
        #           style='Success.TButton').pack(side=tk.RIGHT, padx=5)

    def _limpiar_formulario(self):
        self.nombre_var.set("")
        self.grado_var.set("")
        self.rol_var.set("")
        self.btn_agregar.config(text="Agregar")
        self.modo_edicion = False
        self.registro_id = None

    def _guardar_responsable(self):
        nombre = self.nombre_var.get().strip()
        grado = self.grado_var.get().strip()
        rol = self.rol_var.get().strip()

        if not nombre or not grado or not rol:
            messagebox.showwarning(
                "Campos vacíos", "Debes ingresar nombre, grado y rol.")
            return

        self.cursor.execute("SELECT id, nombre, grado FROM responsables")
        nuevo_normalizado = strip_accents_and_upper(nombre + grado)
        for row in self.cursor.fetchall():
            existente_normalizado = strip_accents_and_upper(row[1] + row[2])
            if existente_normalizado == nuevo_normalizado:
                messagebox.showwarning(
                    "Duplicado", "Ya existe un responsable con ese nombre y grado.")
                return

        if self.modo_edicion and self.registro_id is not None:
            self.cursor.execute("UPDATE responsables SET nombre = ?, grado = ?, rol = ? WHERE id = ?",
                                (nombre, grado, rol, self.registro_id))
            self.conn.commit()
            messagebox.showinfo(
                "Éxito", "Responsable actualizado correctamente")
        else:
            self.cursor.execute("INSERT INTO responsables (nombre, grado, rol) VALUES (?, ?, ?)",
                                (nombre, grado, rol))
            self.conn.commit()
            messagebox.showinfo("Éxito", "Responsable agregado correctamente")

        self._limpiar_formulario()
        self._cargar_responsables()

    def _cargar_responsables(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        self.cursor.execute(
            "SELECT id, nombre, grado, rol FROM responsables ORDER BY nombre")
        self.registros = self.cursor.fetchall()

        for responsable in self.registros:
            self.tree.insert('', 'end', values=responsable)

    def _editar_responsable(self):
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Selección requerida",
                                   "Selecciona un responsable para editar")
            return

        item = self.tree.item(seleccion[0])
        self.registro_id = item['values'][0]
        self.nombre_var.set(item['values'][1])
        self.grado_var.set(item['values'][2])
        self.rol_var.set(item['values'][3])
        self.btn_agregar.config(text="Actualizar")
        self.modo_edicion = True

    def _eliminar_responsable(self):
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Selección requerida",
                                   "Selecciona un responsable para eliminar")
            return

        responsable_id = self.tree.item(seleccion[0])['values'][0]
        confirm = messagebox.askyesno(
            "Confirmar", "¿Estás seguro de eliminar este responsable?")

        if confirm:
            try:
                self.cursor.execute(
                    "DELETE FROM responsables WHERE id = ?", (responsable_id,))
                self.conn.commit()
                messagebox.showinfo(
                    "Éxito", "Responsable eliminado correctamente")
                self._cargar_responsables()
            except sqlite3.IntegrityError:
                messagebox.showerror(
                    "Error", "No se puede eliminar el responsable porque tiene constancias asociadas")

    def destroy(self):
        self.conn.close()
        super().destroy()
