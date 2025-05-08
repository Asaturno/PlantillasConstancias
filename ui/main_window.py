import tkinter as tk
from tkinter import ttk
from ui.gestion_docentes import GestorDocentes
from ui.gestion_eventos import GestorEventos
from ui.gestion_responsables import GestorResponsables
from ui.historial import HistorialConstancias
from ui.crear_constancia import CrearConstancia


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
                       background=[('active', '#2980b9'),
                                   ('!active', '#3498db')],
                       foreground=[('active', 'white'), ('!active', 'white')])

        self.style.map('Success.TButton',
                       background=[('active', '#27ae60'),
                                   ('!active', '#2ecc71')],
                       foreground=[('active', 'white'), ('!active', 'white')])

        self.style.map('Danger.TButton',
                       background=[('active', '#c0392b'),
                                   ('!active', '#e74c3c')],
                       foreground=[('active', 'white'), ('!active', 'white')])

        self.style.map('Dark.TButton',
                       background=[('active', '#1a252f'),
                                   ('!active', '#2c3e50')],
                       foreground=[('active', 'white'), ('!active', 'white')])

    def _build_ui(self):
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
            ("Gestión de Docentes", self.abrir_gestion_docentes, 'Primary.TButton'),
            ("Gestión de Responsables",
             self.abrir_gestion_responsables, 'Success.TButton'),
            ("Gestión de Eventos", self.abrir_gestion_eventos, 'Dark.TButton'),
            ("Crear Constancia", self.abrir_crear_constancia, 'Success.TButton'),
            ("Gestión de Constancias", self.abrir_historial, 'Success.TButton')
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

    def abrir_gestion_docentes(self):
        GestorDocentes(self.master)

    def abrir_gestion_eventos(self):
        GestorEventos(self.master)

    def abrir_gestion_responsables(self):
        GestorResponsables(self.master)

    def abrir_historial(self):
        HistorialConstancias(self.master)

    def abrir_crear_constancia(self):
        CrearConstancia(self.master)
