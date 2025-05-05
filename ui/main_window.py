import tkinter as tk
from tkinter import ttk

from ui.gestion_docentes import GestorDocentes
from ui.gestion_eventos import GestorEventos
from ui.gestion_responsables import GestorResponsables
from ui.crear_constancia import CrearConstancia
from ui.historial import HistorialConstancias


class MainWindow(tk.Frame):
    def __init__(self,master=None):
        super().__init__(master)

        self.master = master
        self.pack(expand=True)
        self._build_ui()
        
        # self.title("Sistema de Gestión de Constancias")
        # self.geometry("500x400")
        # self.resizable(False, False)

        self._build_ui()

    def _build_ui(self):
        title = tk.Label(self, text="Sistema de Constancias", font=("Helvetica", 20, "bold"))
        title.pack(pady=20)

        btn_gestion_docentes = ttk.Button(self, text="Gestión de Docentes", width=30, command=self.abrir_gestion_docentes)
        btn_gestion_docentes.pack(pady=10)

        btn_gestion_responsables = ttk.Button(self, text="Gestión de Responsables", width=30, command=self.abrir_gestion_responsables)
        btn_gestion_responsables.pack(pady=10)

        btn_gestion_eventos = ttk.Button(self, text="Gestión de Eventos", width=30, command=self.abrir_gestion_eventos)
        btn_gestion_eventos.pack(pady=10)

        btn_nueva_constancia = ttk.Button(self, text="Crear Nueva Constancia", width=30, command=self.abrir_crear_constancia)
        btn_nueva_constancia.pack(pady=10)

        btn_historial = ttk.Button(self, text="Historial de Constancias", width=30, command=self.abrir_historial)
        btn_historial.pack(pady=10)

        ttk.Button(self, text="Salir", command=self.master.quit).pack(fill=tk.X, padx=30, pady=20)

    # Métodos placeholder que luego conectaremos con cada vista
    def abrir_gestion_docentes(self):
        GestorDocentes(self.master)

    def abrir_gestion_eventos(self):
        GestorEventos(self.master)

    def abrir_gestion_responsables(self):
        GestorResponsables(self.master)

    def abrir_crear_constancia(self):
        CrearConstancia(self.master)

    def abrir_historial(self):
        HistorialConstancias(self.master)

# if __name__ == "__main__":
#     app = MainWindow()
#     app.mainloop()
