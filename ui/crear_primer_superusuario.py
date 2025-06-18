import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import hashlib


class CrearPrimerSuperusuario(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Crear Superusuario Inicial")
        self.geometry("400x250")
        self.resizable(False, False)

        self.style = ttk.Style()
        self._configurar_estilos()
        self._build_ui()

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
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="Debe crear el primer superusuario del sistema",
                  font=('Arial', 11, 'bold')).pack(pady=(0, 15))

        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill=tk.X, pady=5)

        # Nombre
        ttk.Label(form_frame, text="Nombre:").grid(
            row=0, column=0, sticky="e", padx=5, pady=5)
        self.nombre_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.nombre_var).grid(
            row=0, column=1, sticky="ew", padx=5, pady=5)

        # Contraseña
        ttk.Label(form_frame, text="Contraseña:").grid(
            row=1, column=0, sticky="e", padx=5, pady=5)
        self.contrasena_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.contrasena_var,
                  show="*").grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        # Confirmar Contraseña
        ttk.Label(form_frame, text="Confirmar:").grid(
            row=2, column=0, sticky="e", padx=5, pady=5)
        self.confirmar_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.confirmar_var,
                  show="*").grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        # Botones
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(btn_frame, text="Crear", command=self._crear_superusuario,
                   style='Primary.TButton').pack(side=tk.LEFT, padx=5)

    def _crear_superusuario(self):
        nombre = self.nombre_var.get().strip()
        contrasena = self.contrasena_var.get()
        confirmar = self.confirmar_var.get()

        if not nombre:
            messagebox.showwarning(
                "Error", "Debe ingresar un nombre de usuario")
            return

        if not contrasena or not confirmar:
            messagebox.showwarning(
                "Error", "Debe ingresar y confirmar la contraseña")
            return

        if contrasena != confirmar:
            messagebox.showwarning("Error", "Las contraseñas no coinciden")
            return

        if len(contrasena) < 6:
            messagebox.showwarning(
                "Error", "La contraseña debe tener al menos 6 caracteres")
            return

        conn = None
        try:
            conn = sqlite3.connect("data/constancias.db")
            cursor = conn.cursor()

            # Verificar si ya existe un superusuario
            cursor.execute(
                "SELECT COUNT(*) FROM usuarios WHERE es_superusuario = 1")
            if cursor.fetchone()[0] > 0:
                messagebox.showwarning(
                    "Error", "Ya existe un superusuario en el sistema")
                return

            # Crear hash de la contraseña
            contrasena_hash = hashlib.sha256(contrasena.encode()).hexdigest()

            # Insertar nuevo superusuario
            cursor.execute("""
                INSERT INTO usuarios (nombre, contrasena, es_superusuario) 
                VALUES (?, ?, 1)
            """, (nombre, contrasena_hash))

            conn.commit()
            messagebox.showinfo("Éxito", "Superusuario creado correctamente")
            self.destroy()

        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error de base de datos: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Error inesperado: {str(e)}")
        finally:
            if conn:
                conn.close()
