import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import unicodedata
import re


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
        self.geometry("650x550")
        self.resizable(True, True)

        # Configuración de estilos
        self.style = ttk.Style()
        self._configurar_estilos()

        # Conexión a la base de datos
        self.conn = sqlite3.connect("data/constancias.db")
        self.cursor = self.conn.cursor()
        self.modo_edicion = False
        self.registro_id = None

        # Construir interfaz
        self._build_ui()
        self._cargar_docentes()

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
        """Construye la interfaz de usuario"""
        main_frame = ttk.Frame(self, padding="10 10 10 10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Frame del formulario
        form_frame = ttk.LabelFrame(
            main_frame, text="Formulario de Docente", padding="10")
        form_frame.pack(fill=tk.X, padx=5, pady=5)

        # Campos del formulario
        ttk.Label(form_frame, text="Nombre completo:").grid(
            row=0, column=0, sticky="e", padx=5, pady=5)
        self.nombre_var = tk.StringVar()
        nombre_entry = ttk.Entry(
            form_frame, textvariable=self.nombre_var, width=40)
        nombre_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(form_frame, text="Grado académico:").grid(
            row=1, column=0, sticky="e", padx=5, pady=5)
        self.grado_var = tk.StringVar()
        grado_entry = ttk.Entry(
            form_frame, textvariable=self.grado_var, width=40)
        grado_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        # Botones del formulario
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=10)

        self.btn_agregar = ttk.Button(btn_frame, text="Agregar", command=self._guardar_docente,
                                      style='Primary.TButton', width=15)
        self.btn_agregar.pack(side=tk.LEFT, padx=5)

        ttk.Button(btn_frame, text="Limpiar", command=self._limpiar_formulario,
                   style='Danger.TButton', width=15).pack(side=tk.LEFT, padx=5)

        # Lista de docentes
        list_frame = ttk.LabelFrame(
            main_frame, text="Docentes Registrados", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Treeview para mostrar los docentes
        columns = ('id', 'nombre', 'grado')
        self.tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show='headings',
            selectmode='browse'
        )

        # Configurar columnas
        self.tree.heading('id', text='ID')
        self.tree.heading('nombre', text='Nombre')
        self.tree.heading('grado', text='Grado Académico')

        self.tree.column('id', width=50, anchor='center')
        self.tree.column('nombre', width=250, anchor='w')
        self.tree.column('grado', width=150, anchor='w')

        # Scrollbar
        scrollbar = ttk.Scrollbar(
            list_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Botones de acción
        action_frame = ttk.Frame(list_frame)
        action_frame.pack(fill=tk.X, pady=5)

        ttk.Button(action_frame, text="Editar", command=self._editar_docente,
                   style='Primary.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Eliminar", command=self._eliminar_docente,
                   style='Danger.TButton').pack(side=tk.LEFT, padx=5)
        # ttk.Button(action_frame, text="Actualizar", command=self._cargar_docentes,
        #           style='Success.TButton').pack(side=tk.RIGHT, padx=5)

    def _limpiar_formulario(self):
        """Limpia el formulario y restablece el modo"""
        self.nombre_var.set("")
        self.grado_var.set("")
        self.btn_agregar.config(text="Agregar")
        self.modo_edicion = False
        self.registro_id = None

    def _guardar_docente(self):
        """Guarda un nuevo docente o actualiza uno existente"""
        nombre = self.nombre_var.get().strip()
        grado = self.grado_var.get().strip()

        if not nombre or not grado:
            messagebox.showwarning(
                "Campos vacíos", "Debes ingresar nombre y grado.", parent=self)
            return

        # Verificar duplicados
        self.cursor.execute("SELECT id, nombre, grado FROM docentes")
        nuevo_normalizado = strip_accents_and_upper(nombre + grado)

        for row in self.cursor.fetchall():
            existente_normalizado = strip_accents_and_upper(row[1] + row[2])
            if existente_normalizado == nuevo_normalizado and (not self.modo_edicion or row[0] != self.registro_id):
                messagebox.showwarning(
                    "Duplicado", "Ya existe un docente con el mismo nombre y grado.", parent=self)
                return

        try:
            if self.modo_edicion and self.registro_id is not None:
                # Modo edición
                self.cursor.execute("UPDATE docentes SET nombre = ?, grado = ? WHERE id = ?",
                                    (nombre, grado, self.registro_id))
                mensaje = "Docente actualizado correctamente"
            else:
                # Modo agregar
                self.cursor.execute(
                    "INSERT INTO docentes (nombre, grado) VALUES (?, ?)", (nombre, grado))
                mensaje = "Docente agregado correctamente"

            self.conn.commit()
            messagebox.showinfo("Éxito", mensaje, parent=self)
            self._limpiar_formulario()
            self._cargar_docentes()

        except sqlite3.Error as e:
            messagebox.showerror(
                "Error", f"No se pudo guardar el docente:\n{str(e)}", parent=self)

    def _cargar_docentes(self):
        """Carga los docentes en el Treeview"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        self.cursor.execute(
            "SELECT id, nombre, grado FROM docentes ORDER BY nombre")
        self.registros = self.cursor.fetchall()

        for docente in self.registros:
            self.tree.insert('', 'end', values=docente)

    def _editar_docente(self):
        """Prepara el formulario para editar un docente seleccionado"""
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning(
                "Selección requerida", "Debes seleccionar un docente para editar.", parent=self)
            return

        item = self.tree.item(seleccion[0])
        self.registro_id = item['values'][0]
        self.nombre_var.set(item['values'][1])
        self.grado_var.set(item['values'][2])
        self.btn_agregar.config(text="Actualizar")
        self.modo_edicion = True

    def _eliminar_docente(self):
        """Elimina el docente seleccionado"""
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning(
                "Selección requerida", "Debes seleccionar un docente para eliminar.", parent=self)
            return

        docente_id = self.tree.item(seleccion[0])['values'][0]
        confirm = messagebox.askyesno(
            "Confirmar eliminación",
            "¿Estás seguro de que deseas eliminar este docente?",
            parent=self
        )

        if confirm:
            try:
                self.cursor.execute(
                    "DELETE FROM docentes WHERE id = ?", (docente_id,))
                self.conn.commit()
                messagebox.showinfo(
                    "Éxito", "Docente eliminado correctamente", parent=self)
                self._cargar_docentes()
            except sqlite3.IntegrityError:
                messagebox.showerror(
                    "Error",
                    "No se puede eliminar el docente porque tiene constancias asociadas.",
                    parent=self
                )
            except sqlite3.Error as e:
                messagebox.showerror(
                    "Error", f"No se pudo eliminar el docente:\n{str(e)}", parent=self)

    def destroy(self):
        """Cierra la conexión a la base de datos y destruye la ventana"""
        try:
            self.conn.close()
        except:
            pass
        super().destroy()
