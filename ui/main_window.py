import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from ui.gestion_docentes import GestorDocentes
from ui.gestion_eventos import GestorEventos
from ui.gestion_responsables import GestorResponsables
from ui.historial import HistorialConstancias
from ui.crear_constancia import CrearConstancia
from ui.gestion_superusuarios import GestorSuperusuarios
import sqlite3
import hashlib


class MainWindow(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack(fill=tk.BOTH, expand=True)

        # Cargar fondo
        self.original_bg = Image.open("Fondo1.png")
        self.bg_photo = ImageTk.PhotoImage(self.original_bg)

        # Fondo como label
        self.fondo = tk.Label(self.master, image=self.bg_photo)
        self.fondo.place(x=0, y=0, relwidth=1, relheight=1)

        # Contenedor de botones centrado
        self.container = ttk.Frame(
            self.master, padding=20, style="Card.TFrame")
        self.container.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Estilos
        self.style = ttk.Style()
        self._configurar_estilos()

        # Construcción de UI
        self._build_ui()

    def _configurar_estilos(self):
        self.style.theme_use("clam")

        # Estilos globales
        self.style.configure("TLabel", background="#ffffff",
                             foreground="#2c3e50", font=('Arial', 12, 'bold'))

        # Estilo para los botones por defecto
        self.style.configure("TButton", font=('Arial', 11),
                             padding=10, background="#2E5E2E", foreground="white")
        self.style.map("TButton", background=[("active", "#244B24")])

        # 🎯 Estilo especial con hover personalizado
        self.style.configure("Hover.TButton",
                             font=('Arial', 11, 'bold'),
                             padding=10,
                             background="#2E5E2E",
                             foreground="white",
                             borderwidth=2)

        self.style.map("Hover.TButton",
                       background=[("active", "white")],
                       foreground=[("active", "#2E5E2E")],
                       bordercolor=[("active", "#a58a42")])  # Este último solo funciona si el sistema lo respeta

        # Frame contenedor
        self.style.configure("Card.TFrame", background="#ffffff")

    def _build_ui(self):
        ttk.Label(self.container, text="Sistema de Gestión de Constancias",
                  font=("Arial", 16, "bold"), foreground="#2E5E2E",
                  background="#ffffff").pack(pady=(0, 20))

        btn_frame = ttk.Frame(self.container, style="Card.TFrame")
        btn_frame.pack()

        buttons = [
            ("Gestión de Docentes", self._acceder_gestion_docentes),
            ("Gestión de Responsables", self._acceder_gestion_responsables),
            ("Gestión de Eventos", self._acceder_gestion_eventos),
            ("Crear Constancia", self.abrir_crear_constancia),
            ("Gestión de Constancias", self.abrir_historial),
            ("Gestión de Superusuarios", self._acceder_gestion_superusuarios),
        ]

        for text, command in buttons:
            ttk.Button(btn_frame, text=text, command=command,
                       style="Hover.TButton", width=25).pack(pady=6, fill=tk.X)

        ttk.Button(btn_frame, text="Salir", command=self.master.quit,
                   style="Hover.TButton").pack(pady=(20, 0), fill=tk.X)

    def _autenticar_superusuario(self):
        dialog = tk.Toplevel(self)
        dialog.title("Autenticación requerida")
        dialog.geometry("400x230")
        dialog.resizable(False, False)
        dialog.configure(bg="#e9e6df")

        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="🔐 Ingreso de Superusuario",
                  font=("Arial", 13, "bold"),
                  foreground="#2E5E2E").pack(pady=(0, 15))

        nombre_var = tk.StringVar()
        contrasena_var = tk.StringVar()

        form_frame = ttk.Frame(frame)
        form_frame.pack(pady=5)

        ttk.Label(form_frame, text="Usuario:").grid(
            row=0, column=0, sticky="e", padx=5, pady=5)
        ttk.Entry(form_frame, textvariable=nombre_var,
                  width=25).grid(row=0, column=1, padx=5)

        ttk.Label(form_frame, text="Contraseña:").grid(
            row=1, column=0, sticky="e", padx=5, pady=5)
        ttk.Entry(form_frame, textvariable=contrasena_var,
                  show="*", width=25).grid(row=1, column=1, padx=5)

        resultado = {'autenticado': False}

        def verificar():
            conn = sqlite3.connect("data/constancias.db")
            cursor = conn.cursor()
            hash_pass = hashlib.sha256(
                contrasena_var.get().encode()).hexdigest()
            cursor.execute("SELECT id FROM usuarios WHERE nombre=? AND contrasena=? AND es_superusuario=1",
                           (nombre_var.get(), hash_pass))
            if cursor.fetchone():
                resultado['autenticado'] = True
                dialog.destroy()
            else:
                tk.messagebox.showerror("Error", "Credenciales incorrectas")
            conn.close()

        ttk.Button(frame, text="Aceptar", command=verificar,
                   style="Hover.TButton").pack(pady=15)

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
