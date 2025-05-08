import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

class GestorEventos(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Gestión de Eventos")
        self.geometry("600x500")
        
        self.style = ttk.Style()
        self._configurar_estilos()
        
        self.conn = sqlite3.connect("data/constancias.db")
        self.cursor = self.conn.cursor()
        self.modo_edicion = False
        self.registro_id = None
        
        self._build_ui()
        self._cargar_eventos()

    def _configurar_estilos(self):
        """Configura los estilos visuales"""
        self.style.theme_use('clam')
        self.style.configure('.', background='#ecf0f1')
        self.style.configure('TFrame', background='#ecf0f1')
        self.style.configure('TLabel', background='#ecf0f1', foreground='#2c3e50', font=('Arial', 10))
        self.style.configure('TButton', font=('Arial', 10, 'bold'), padding=8)
        self.style.configure('Treeview', font=('Arial', 10), rowheight=25)
        self.style.configure('Treeview.Heading', font=('Arial', 10, 'bold'), 
                           background='#2c3e50', foreground='white')
        
        self.style.map('Primary.TButton',
                     background=[('active', '#2980b9'), ('!active', '#3498db')],
                     foreground=[('active', 'white'), ('!active', 'white')])
        
        self.style.map('Danger.TButton',
                     background=[('active', '#c0392b'), ('!active', '#e74c3c')],
                     foreground=[('active', 'white'), ('!active', 'white')])

    def _build_ui(self):
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Formulario
        form_frame = ttk.LabelFrame(main_frame, text="Formulario de Evento", padding="10")
        form_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Nombre del evento:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.nombre_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.nombre_var, font=('Arial', 10)).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        ttk.Label(form_frame, text="Fecha (AAAA-MM-DD):").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.fecha_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.fecha_var, font=('Arial', 10)).grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=2, columnspan=2, pady=10)
        
        self.btn_agregar = ttk.Button(btn_frame, text="Agregar", command=self._guardar_evento,
                                    style='Primary.TButton')
        self.btn_agregar.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame, text="Limpiar", command=self._limpiar_formulario,
                  style='Danger.TButton').pack(side=tk.LEFT, padx=5)
        
        # Lista de eventos
        list_frame = ttk.LabelFrame(main_frame, text="Eventos Registrados", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        columns = ('ID', 'Nombre', 'Fecha')
        self.tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show='headings',
            selectmode='browse'
        )
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor='center')
            
        self.tree.column('Nombre', width=250)
        self.tree.column('Fecha', width=150)
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Botones de acción
        action_frame = ttk.Frame(list_frame)
        action_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(action_frame, text="Editar", command=self._editar_evento,
                  style='Primary.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Eliminar", command=self._eliminar_evento,
                  style='Danger.TButton').pack(side=tk.LEFT, padx=5)
        # ttk.Button(action_frame, text="Actualizar", command=self._cargar_eventos,
        #           style='Primary.TButton').pack(side=tk.RIGHT, padx=5)

    def _limpiar_formulario(self):
        self.nombre_var.set("")
        self.fecha_var.set("")
        self.btn_agregar.config(text="Agregar")
        self.modo_edicion = False
        self.registro_id = None

    def _guardar_evento(self):
        nombre = self.nombre_var.get().strip()
        fecha = self.fecha_var.get().strip()
        
        if not nombre or not fecha:
            messagebox.showwarning("Campos vacíos", "Debes ingresar nombre y fecha.")
            return
            
        try:
            # Validar formato de fecha
            datetime.strptime(fecha, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error de formato", "La fecha debe estar en formato AAAA-MM-DD")
            return

        if self.modo_edicion and self.registro_id is not None:
            self.cursor.execute("UPDATE eventos SET nombre = ?, fecha = ? WHERE id = ?",
                              (nombre, fecha, self.registro_id))
            self.conn.commit()
            messagebox.showinfo("Éxito", "Evento actualizado correctamente")
        else:
            self.cursor.execute("INSERT INTO eventos (nombre, fecha) VALUES (?, ?)", (nombre, fecha))
            self.conn.commit()
            messagebox.showinfo("Éxito", "Evento agregado correctamente")

        self._limpiar_formulario()
        self._cargar_eventos()

    def _cargar_eventos(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        self.cursor.execute("SELECT id, nombre, fecha FROM eventos ORDER BY fecha DESC")
        self.registros = self.cursor.fetchall()
        
        for evento in self.registros:
            self.tree.insert('', 'end', values=evento)

    def _editar_evento(self):
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Selección requerida", "Selecciona un evento para editar")
            return
            
        item = self.tree.item(seleccion[0])
        self.registro_id = item['values'][0]
        self.nombre_var.set(item['values'][1])
        self.fecha_var.set(item['values'][2])
        self.btn_agregar.config(text="Actualizar")
        self.modo_edicion = True

    def _eliminar_evento(self):
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Selección requerida", "Selecciona un evento para eliminar")
            return
            
        evento_id = self.tree.item(seleccion[0])['values'][0]
        confirm = messagebox.askyesno("Confirmar", "¿Estás seguro de eliminar este evento?")
        
        if confirm:
            try:
                self.cursor.execute("DELETE FROM eventos WHERE id = ?", (evento_id,))
                self.conn.commit()
                messagebox.showinfo("Éxito", "Evento eliminado correctamente")
                self._cargar_eventos()
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "No se puede eliminar el evento porque tiene constancias asociadas")

    def destroy(self):
        self.conn.close()
        super().destroy()