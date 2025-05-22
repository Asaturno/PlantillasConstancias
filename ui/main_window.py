import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import hashlib
from ui.gestion_docentes import GestorDocentes
from ui.gestion_eventos import GestorEventos
from ui.gestion_responsables import GestorResponsables
from ui.historial import HistorialConstancias
from ui.crear_constancia import CrearConstancia
from ui.gestion_superusuarios import GestorSuperusuarios

class MainWindow(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack(fill=tk.BOTH, expand=True)

        # Configurar estilo
        self.style = ttk.Style()
        self._configurar_estilos()
        self._build_ui()

    def _configurar_estilos(self):
        """Configura los estilos visuales"""
        self.style.theme_use('clam')
        self.style.configure('.', background='#ecf0f1')
        self.style.configure('TFrame', background='#ecf0f1')
        self.style.configure('TLabel', background='#ecf0f1',
                           foreground='#2c3e50', font=('Arial', 10))
        self.style.configure('TButton', font=('Arial', 10, 'bold'), padding=8)

        # Estilos para botones
        self.style.map('Primary.TButton',
                     background=[('active', '#2980b9'), ('!active', '#3498db')],
                     foreground=[('active', 'white'), ('!active', 'white')])

        self.style.map('Success.TButton',
                     background=[('active', '#27ae60'), ('!active', '#2ecc71')],
                     foreground=[('active', 'white'), ('!active', 'white')])

        self.style.map('Danger.TButton',
                     background=[('active', '#c0392b'), ('!active', '#e74c3c')],
                     foreground=[('active', 'white'), ('!active', 'white')])

        self.style.map('Dark.TButton',
                     background=[('active', '#1a252f'), ('!active', '#2c3e50')],
                     foreground=[('active', 'white'), ('!active', 'white')])

    def _build_ui(self):
        """Construye la interfaz de usuario"""
        # Frame principal
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Título
        title = ttk.Label(main_frame,
                        text="Sistema de Gestión de Constancias",
                        font=("Arial", 16, "bold"),
                        foreground="#2c3e50")
        title.pack(pady=(0, 20))

        # Botones
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(expand=True)

        buttons = [
            ("Gestión de Docentes", self._acceder_gestion_docentes, 'Primary.TButton'),
            ("Gestión de Responsables", self._acceder_gestion_responsables, 'Success.TButton'),
            ("Gestión de Eventos", self._acceder_gestion_eventos, 'Dark.TButton'),
            ("Crear Constancia", self.abrir_crear_constancia, 'Success.TButton'),
            ("Gestión de Constancias", self.abrir_historial, 'Success.TButton'),
            ("Gestión de Superusuarios", self._acceder_gestion_superusuarios, 'Danger.TButton')
        ]

        for text, command, style in buttons:
            btn = ttk.Button(
                btn_frame,
                text=text,
                command=command,
                style=style,
                width=25,
                padding=10
            )
            btn.pack(pady=8, ipady=5, fill=tk.X)

        # Botón salir
        ttk.Button(
            btn_frame,
            text="Salir",
            command=self.master.quit,
            style='Danger.TButton'
        ).pack(pady=(20, 0), ipady=5, fill=tk.X)

    def _autenticar_superusuario(self):
        """Muestra diálogo para autenticar superusuario"""
        dialog = tk.Toplevel(self)
        dialog.title("Autenticación requerida")
        dialog.geometry("400x220")
        dialog.resizable(False, False)
        
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Ingrese credenciales de superusuario", 
                 font=('Arial', 11)).pack(pady=(0, 15))
        
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(form_frame, text="Usuario:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        nombre_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=nombre_var, width=25).grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Label(form_frame, text="Contraseña:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        contrasena_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=contrasena_var, show="*", width=25).grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(15, 0))
        
        resultado = {'autenticado': False}
        
        def verificar():
            conn = sqlite3.connect("data/constancias.db")
            cursor = conn.cursor()
            
            contrasena_hash = hashlib.sha256(contrasena_var.get().encode()).hexdigest()
            cursor.execute(
                "SELECT id FROM usuarios WHERE nombre = ? AND contrasena = ? AND es_superusuario = 1",
                (nombre_var.get(), contrasena_hash)
            )
            
            if cursor.fetchone():
                resultado['autenticado'] = True
                dialog.destroy()
            else:
                messagebox.showerror("Error", "Credenciales incorrectas", parent=dialog)
            
            conn.close()
        
        ttk.Button(btn_frame, text="Aceptar", command=verificar,
                  style='Primary.TButton').pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Cancelar", command=dialog.destroy,
                  style='Danger.TButton').pack(side=tk.RIGHT, padx=10)
        
        dialog.transient(self.master)
        dialog.grab_set()
        self.wait_window(dialog)
        
        return resultado['autenticado']

    def _acceder_gestion_docentes(self):
        if self._autenticar_superusuario():
            GestorDocentes(self.master)

    def _acceder_gestion_eventos(self):
        if self._autenticar_superusuario():
            GestorEventos(self.master)

    def _acceder_gestion_responsables(self):
        if self._autenticar_superusuario():
            GestorResponsables(self.master)

    def _acceder_gestion_superusuarios(self):
        if self._autenticar_superusuario():
            GestorSuperusuarios(self.master)

    def abrir_historial(self):
        HistorialConstancias(self.master)

    def abrir_crear_constancia(self):
        CrearConstancia(self.master)
