import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
import sqlite3
import os
from datetime import datetime
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
from tkinter import filedialog
from ui.vista_previa_html import abrir_editor_secciones
import unicodedata

DB_PATH = os.path.join("data", "constancias.db")

# TEXTO_BASE = """[LOGO DE LA ESCUELA]

# El que suscribe, {rol_responsable}, otorga la presente:

# CONSTANCIA DE {tipo_constancia}
# a:
# {docentes}

# Como {rol_docente} en {nombre_evento}, llevado a cabo el {fecha_evento}

# Toluca, Estado de México, {fecha_emision}
# Atentamente
# [ESLOGAN DE LA ESCUELA]
# [PLACA CONMEMORATIVA]

# {grado_responsable}
# {nombre_responsable}
# {rol_responsable}
# """


def normalize_text(text):
    """Elimina acentos y convierte a mayúsculas para búsqueda sin sensibilidad a acentos"""
    if not text:
        return ""
    text = unicodedata.normalize('NFD', text)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    return text.upper()


class CrearConstancia(tk.Toplevel):
    datos_constancia = {}

    def __init__(self, master=None, historial=None):
        super().__init__(master)
        self.historial = historial
        self.title("Crear Nueva Constancia")
        self.geometry("900x700")
        self.resizable(True, True)

        self.style = ttk.Style()
        self._configurar_estilos()

        self._build_ui()
        self._load_data()

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

        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)

        # Pestaña de configuración
        config_frame = ttk.Frame(notebook)
        notebook.add(config_frame, text="Configuración")

        # Formulario de configuración
        form_frame = ttk.LabelFrame(
            config_frame, text="Datos de la Constancia", padding="10")
        form_frame.pack(fill=tk.X, padx=5, pady=5)

        # Frame para docentes con buscador y seleccionados
        docente_frame = ttk.Frame(form_frame)
        docente_frame.grid(row=0, column=0, columnspan=2,
                           sticky="nsew", padx=5, pady=5)

        # Frame principal horizontal
        docente_main_frame = ttk.Frame(docente_frame)
        docente_main_frame.pack(fill=tk.BOTH, expand=True)

        # Frame para buscador y lista (izquierda)
        search_list_frame = ttk.Frame(docente_main_frame)
        search_list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Buscador
        search_frame = ttk.Frame(search_list_frame)
        search_frame.pack(fill=tk.X)

        self.search_var = tk.StringVar()
        ttk.Label(search_frame, text="Buscar docente:").pack(
            side=tk.LEFT, padx=(0, 5))
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        ttk.Button(search_frame, text="🔍", width=3,
                   command=self._filter_docentes).pack(side=tk.LEFT, padx=(5, 0))

        # Listbox con scrollbar
        list_scroll_frame = ttk.Frame(search_list_frame)
        list_scroll_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(list_scroll_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.docentes_listbox = tk.Listbox(
            list_scroll_frame,
            selectmode=tk.MULTIPLE,
            height=5,
            exportselection=False,
            yscrollcommand=scrollbar.set,
            font=('Arial', 10)
        )
        self.docentes_listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.docentes_listbox.yview)

        # Frame para docentes seleccionados (derecha)
        selected_frame = ttk.LabelFrame(
            docente_main_frame, text="Docentes Seleccionados", width=250)
        selected_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))

        self.selected_listbox = tk.Listbox(
            selected_frame,
            selectmode=tk.SINGLE,
            height=5,
            font=('Arial', 10)
        )
        self.selected_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        btn_remove_frame = ttk.Frame(selected_frame)
        btn_remove_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Button(
            btn_remove_frame,
            text="Quitar seleccionado",
            command=self._quitar_docente,
            style='Danger.TButton'
        ).pack(side=tk.LEFT, expand=True)

        # Selector docentes
        self.docentes_listbox.bind(
            '<<ListboxSelect>>', self._agregar_docentes_seleccionados)
        self.search_var.trace_add(
            "write", lambda *args: self._filter_docentes())

        # Evento
        ttk.Label(form_frame, text="Evento:").grid(
            row=1, column=0, sticky="e", padx=5, pady=5)
        self.evento_cb = ttk.Combobox(
            form_frame, state="readonly", font=('Arial', 10))
        self.evento_cb.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        # Responsable
        ttk.Label(form_frame, text="Responsable:").grid(
            row=2, column=0, sticky="e", padx=5, pady=5)
        self.responsable_cb = ttk.Combobox(
            form_frame, state="readonly", font=('Arial', 10))
        self.responsable_cb.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        # Tipo de constancia
        ttk.Label(form_frame, text="Tipo de constancia:").grid(
            row=3, column=0, sticky="e", padx=5, pady=5)
        self.tipo_entry = ttk.Entry(form_frame, font=('Arial', 10))
        self.tipo_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        # Rol del docente
        ttk.Label(form_frame, text="Rol del docente:").grid(
            row=4, column=0, sticky="e", padx=5, pady=5)
        self.rol_docente_entry = ttk.Entry(form_frame, font=('Arial', 10))
        self.rol_docente_entry.grid(
            row=4, column=1, padx=5, pady=5, sticky="ew")

        # Fecha de emisión
        ttk.Label(form_frame, text="Fecha de emisión:").grid(
            row=5, column=0, sticky="e", padx=5, pady=5)
        self.fecha_entry = ttk.Entry(form_frame, font=('Arial', 10))
        self.fecha_entry.insert(0, datetime.today().strftime("%Y-%m-%d"))
        self.fecha_entry.grid(row=5, column=1, padx=5, pady=5, sticky="ew")

        # Botones de acción
        btn_frame = ttk.Frame(config_frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=10)

        # ttk.Button(btn_frame, text="Prellenar texto", command=self._prellenar_texto,
        #          style='Primary.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Generar vista previa", command=self._generar_plantilla,
                   style='Success.TButton').pack(side=tk.LEFT, padx=5)

        # # Pestaña de edición
        # edit_frame = ttk.Frame(notebook)
        # notebook.add(edit_frame, text="Editor de Texto")

        # ttk.Label(edit_frame, text="Contenido de la constancia:").pack(pady=5)

        # self.editor = ScrolledText(edit_frame, wrap=tk.WORD, width=100, height=20,
        #                          font=('Arial', 11))
        # self.editor.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # # Botones de edición
        # edit_btn_frame = ttk.Frame(edit_frame)
        # edit_btn_frame.pack(fill=tk.X, pady=10)

        # ttk.Button(edit_btn_frame, text="Guardar en historial", command=self._guardar_constancia,
        #          style='Success.TButton').pack(side=tk.LEFT, padx=5)
        # ttk.Button(edit_btn_frame, text="Exportar a PDF", command=self._exportar_pdf,
        #          style='Primary.TButton').pack(side=tk.LEFT, padx=5)

    def _agregar_docentes_seleccionados(self, event):
        """Agrega docentes seleccionados a la lista de seleccionados"""
        indices = self.docentes_listbox.curselection()
        for i in indices:
            docente = self.docentes_listbox.get(i)
            if docente not in self.selected_listbox.get(0, tk.END):
                self.selected_listbox.insert(tk.END, docente)

    def _quitar_docente(self):
        """Quita el docente seleccionado de la lista de seleccionados"""
        selection = self.selected_listbox.curselection()
        if selection:
            self.selected_listbox.delete(selection[0])

    def _filter_docentes(self):
        """Filtra los docentes según el texto del buscador"""
        search_text = normalize_text(self.search_var.get())

        self.docentes_listbox.delete(0, tk.END)

        if not search_text:
            # Mostrar todos si no hay texto de búsqueda
            for _, nombre in self.all_docentes:
                self.docentes_listbox.insert(tk.END, nombre)
        else:
            # Filtrar docentes
            for id_doc, nombre in self.all_docentes:
                if search_text in normalize_text(nombre):
                    self.docentes_listbox.insert(tk.END, nombre)

    def _load_data(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Docentes (guardamos todos para filtrar)
        cursor.execute(
            "SELECT id, grado || ' ' || nombre FROM docentes ORDER BY nombre")
        self.all_docentes = cursor.fetchall()
        self._filter_docentes()  # Mostrar todos inicialmente

        # Evento
        cursor.execute(
            "SELECT id, nombre || ' (' || fecha || ')' FROM eventos ORDER BY fecha DESC")
        self.eventos = cursor.fetchall()
        self.evento_cb["values"] = [e[1] for e in self.eventos]

        # Responsable
        cursor.execute(
            "SELECT id, grado || ' ' || nombre || ' - ' || rol FROM responsables ORDER BY nombre")
        self.responsables = cursor.fetchall()
        self.responsable_cb["values"] = [r[1] for r in self.responsables]

        conn.close()

    def _generar_plantilla(self):
        tipo = self.tipo_entry.get().strip()
        rol_docente = self.rol_docente_entry.get().strip()
        fecha_emision = self.fecha_entry.get().strip()

        if not tipo or not rol_docente or not self.evento_cb.current() >= 0 or not self.responsable_cb.current() >= 0:
            messagebox.showwarning(
                "Campos incompletos", "Completa todos los campos antes de continuar.")
            return

        # Docentes seleccionados
        docentes_texto = "\n".join(self.selected_listbox.get(0, tk.END))
        if not docentes_texto:
            messagebox.showwarning(
                "Sin docentes", "Selecciona al menos un docente.")
            return

        # Evento y responsable
        evento_id, evento_str = self.eventos[self.evento_cb.current()]
        evento_nombre, fecha_evento = evento_str.split(' (')
        fecha_evento = fecha_evento.replace(")", "")

        responsable_id, responsable_str = self.responsables[self.responsable_cb.current(
        )]
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(
            "SELECT grado, nombre, rol FROM responsables WHERE id = ?", (responsable_id,))
        grado_responsable, nombre_responsable, rol_responsable = cur.fetchone()
        conn.close()

        datos = {
            'id_responsable': responsable_id,
            'id_evento': evento_id,
            'rol_responsable': rol_responsable,
            'tipo': tipo,
            'docentes': docentes_texto,
            'rol_docente': rol_docente,
            'nombre_evento': evento_nombre,
            'fecha_evento': fecha_evento,
            'fecha_emision': fecha_emision,
            'grado_responsable': grado_responsable,
            'nombre_responsable': nombre_responsable
        }
        self.datos_constancia = datos

        abrir_editor_secciones(datos)

    def get_datosConstancia(self):
        return self.datos_constancia

    # def _prellenar_texto(self):
    #     tipo = self.tipo_entry.get().strip()
    #     rol_docente = self.rol_docente_entry.get().strip()
    #     fecha_emision = self.fecha_entry.get().strip()

    #     if not tipo or not rol_docente or not self.evento_cb.current() >= 0 or not self.responsable_cb.current() >= 0:
    #         messagebox.showwarning(
    #             "Campos incompletos", "Completa todos los campos antes de continuar.")
    #         return

    #     # Docentes seleccionados
    #     docentes_texto = "\n".join(self.selected_listbox.get(0, tk.END))
    #     if not docentes_texto:
    #         messagebox.showwarning(
    #             "Sin docentes", "Selecciona al menos un docente.")
    #         return

    #     # Evento y responsable
    #     evento_id, evento_str = self.eventos[self.evento_cb.current()]
    #     evento_nombre, fecha_evento = evento_str.split(' (')
    #     fecha_evento = fecha_evento.replace(")", "")

    #     responsable_id, responsable_str = self.responsables[self.responsable_cb.current()]
    #     conn = sqlite3.connect(DB_PATH)
    #     cur = conn.cursor()
    #     cur.execute(
    #         "SELECT grado, nombre, rol FROM responsables WHERE id = ?", (responsable_id,))
    #     grado_responsable, nombre_responsable, rol_responsable = cur.fetchone()
    #     conn.close()

    #     texto = TEXTO_BASE.format(
    #         tipo_constancia=tipo.upper(),
    #         docentes=docentes_texto,
    #         rol_docente=rol_docente,
    #         nombre_evento=evento_nombre,
    #         fecha_evento=fecha_evento,
    #         fecha_emision=fecha_emision,
    #         grado_responsable=grado_responsable,
    #         nombre_responsable=nombre_responsable,
    #         rol_responsable=rol_responsable
    #     )

    #     self.editor.delete("1.0", tk.END)
    #     self.editor.insert(tk.END, texto)

    # def _guardar_constancia(self):
    #     contenido = self.editor.get("1.0", tk.END).strip()
    #     if not contenido:
    #         messagebox.showwarning(
    #             "Sin contenido", "No hay contenido que guardar.")
    #         return

    #     conn = sqlite3.connect(DB_PATH)
    #     cursor = conn.cursor()
    #     cursor.execute("INSERT INTO historial_constancias (contenido, fecha_emision) VALUES (?, ?)", (
    #         contenido,
    #         self.fecha_entry.get().strip()
    #     ))
    #     conn.commit()
    #     conn.close()

    #     # Actualiza el historial si está disponible
    #     if self.historial:
    #         self.historial._load_historial()

    #     messagebox.showinfo("Guardado", "Constancia guardada en historial.")
    #     self.destroy()

    # def _exportar_pdf(self):
    #     contenido = self.editor.get("1.0", tk.END).strip()
    #     if not contenido:
    #         messagebox.showwarning("Vacío", "El contenido está vacío.")
    #         return

    #     archivo = filedialog.asksaveasfilename(
    #         defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
    #     if not archivo:
    #         return

    #     c = canvas.Canvas(archivo, pagesize=LETTER)
    #     width, height = LETTER
    #     x, y = 50, height - 50

    #     for line in contenido.splitlines():
    #         c.drawString(x, y, line)
    #         y -= 15
    #         if y < 50:
    #             c.showPage()
    #             y = height - 50

    #     c.save()
    #     messagebox.showinfo(
    #         "PDF creado", f"El archivo se guardó como:\n{archivo}")
