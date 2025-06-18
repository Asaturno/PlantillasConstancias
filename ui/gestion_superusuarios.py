import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import hashlib


class GestorSuperusuarios(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Gestión de Superusuarios")
        self.geometry("600x400")

        self.style = ttk.Style()
        self._configurar_estilos()

        self.conn = sqlite3.connect("data/constancias.db")
        self.cursor = self.conn.cursor()
        self.modo_edicion = False
        self.registro_id = None

        self._build_ui()
        self._cargar_superusuarios()

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

        form_frame = ttk.LabelFrame(
            main_frame, text="Formulario de Superusuario", padding="10")
        form_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(form_frame, text="Nombre:").grid(
            row=0, column=0, sticky="e", padx=5, pady=5)
        self.nombre_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.nombre_var).grid(
            row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(form_frame, text="Contraseña:").grid(
            row=1, column=0, sticky="e", padx=5, pady=5)
        self.contrasena_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.contrasena_var,
                  show="*").grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(form_frame, text="Confirmar Contraseña:").grid(
            row=2, column=0, sticky="e", padx=5, pady=5)
        self.confirmar_contrasena_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.confirmar_contrasena_var,
                  show="*").grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=3, columnspan=2, pady=10)

        self.btn_guardar = ttk.Button(btn_frame, text="Guardar", command=self._guardar_superusuario,
                                      style='Primary.TButton')
        self.btn_guardar.pack(side=tk.LEFT, padx=5)

        ttk.Button(btn_frame, text="Limpiar", command=self._limpiar_formulario,
                   style='Danger.TButton').pack(side=tk.LEFT, padx=5)

        list_frame = ttk.LabelFrame(
            main_frame, text="Superusuarios Registrados", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        columns = ('ID', 'Nombre')
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

        scrollbar = ttk.Scrollbar(
            list_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(fill=tk.BOTH, expand=True)

        action_frame = ttk.Frame(list_frame)
        action_frame.pack(fill=tk.X, pady=5)

        ttk.Button(action_frame, text="Editar", command=self._editar_superusuario,
                   style='Primary.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Eliminar", command=self._eliminar_superusuario,
                   style='Danger.TButton').pack(side=tk.LEFT, padx=5)

    def _limpiar_formulario(self):
        self.nombre_var.set("")
        self.contrasena_var.set("")
        self.confirmar_contrasena_var.set("")
        self.btn_guardar.config(text="Guardar")
        self.modo_edicion = False
        self.registro_id = None

    def _guardar_superusuario(self):
        nombre = self.nombre_var.get().strip()
        contrasena = self.contrasena_var.get()
        confirmar_contrasena = self.confirmar_contrasena_var.get()

        if not nombre:
            messagebox.showwarning(
                "Campo vacío", "Debes ingresar un nombre de usuario.", parent=self)
            return

        if not contrasena or not confirmar_contrasena:
            messagebox.showwarning(
                "Campo vacío", "Debes ingresar y confirmar la contraseña.", parent=self)
            return

        if contrasena != confirmar_contrasena:
            messagebox.showwarning(
                "Error", "Las contraseñas no coinciden.", parent=self)
            return

        if len(contrasena) < 6:
            messagebox.showwarning(
                "Error", "La contraseña debe tener al menos 6 caracteres.", parent=self)
            return

        if not self.modo_edicion:
            self.cursor.execute(
                "SELECT id FROM usuarios WHERE nombre = ? AND es_superusuario = 1", (nombre,))
            if self.cursor.fetchone():
                messagebox.showwarning(
                    "Error", "Ya existe un superusuario con ese nombre.", parent=self)
                return

        contrasena_hash = hashlib.sha256(contrasena.encode()).hexdigest()

        try:
            if self.modo_edicion and self.registro_id is not None:
                self.cursor.execute(
                    "UPDATE usuarios SET nombre = ?, contrasena = ?, es_superusuario = 1 WHERE id = ?",
                    (nombre, contrasena_hash, self.registro_id)
                )
                mensaje = "Superusuario actualizado correctamente"
            else:
                self.cursor.execute(
                    "INSERT INTO usuarios (nombre, contrasena, es_superusuario) VALUES (?, ?, 1)",
                    (nombre, contrasena_hash)
                )
                mensaje = "Superusuario creado correctamente"

            self.conn.commit()
            messagebox.showinfo("Éxito", mensaje, parent=self)
            self._limpiar_formulario()
            self._cargar_superusuarios()

        except sqlite3.Error as e:
            messagebox.showerror(
                "Error", f"No se pudo guardar el superusuario:\n{str(e)}", parent=self)

    def _cargar_superusuarios(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        self.cursor.execute(
            "SELECT id, nombre FROM usuarios WHERE es_superusuario = 1 ORDER BY nombre")
        self.registros = self.cursor.fetchall()

        for superusuario in self.registros:
            self.tree.insert('', 'end', values=superusuario)

    def _editar_superusuario(self):
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning(
                "Selección requerida", "Debes seleccionar un superusuario para editar.", parent=self)
            return

        item = self.tree.item(seleccion[0])
        self.registro_id = item['values'][0]
        self.nombre_var.set(item['values'][1])
        self.btn_guardar.config(text="Actualizar")
        self.modo_edicion = True

    def _eliminar_superusuario(self):
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning(
                "Selección requerida", "Debes seleccionar un superusuario para eliminar.", parent=self)
            return

        superusuario_id = self.tree.item(seleccion[0])['values'][0]

        if superusuario_id == 1:
            messagebox.showwarning(
                "Error", "No se puede eliminar el superusuario principal 'admin'.", parent=self)
            return

        confirm = messagebox.askyesno(
            "Confirmar eliminación", "¿Estás seguro de que deseas eliminar este superusuario?", parent=self)

        if confirm:
            try:
                self.cursor.execute(
                    "DELETE FROM usuarios WHERE id = ? AND es_superusuario = 1", (superusuario_id,))
                self.conn.commit()
                messagebox.showinfo(
                    "Éxito", "Superusuario eliminado correctamente", parent=self)
                self._cargar_superusuarios()
            except sqlite3.Error as e:
                messagebox.showerror(
                    "Error", f"No se pudo eliminar el superusuario:\n{str(e)}", parent=self)

    def destroy(self):
        try:
            self.conn.close()
        except:
            pass
        super().destroy()
