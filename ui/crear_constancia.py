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

DB_PATH = os.path.join("data", "constancias.db")

TEXTO_BASE = """[LOGO DE LA ESCUELA]
 
 El que suscribe, {rol_responsable}, otorga la presente:
 
 CONSTANCIA DE {tipo_constancia}
 a:
 {docentes}
 
 Como {rol_docente} en {nombre_evento}, llevado a cabo el {fecha_evento}
 
 Toluca, Estado de México, {fecha_emision}
 Atentamente
 [ESLOGAN DE LA ESCUELA]
 [PLACA CONMEMORATIVA]
 
 {grado_responsable}
 {nombre_responsable}
 {rol_responsable}
 """


class CrearConstancia(tk.Toplevel):
    def __init__(self, master=None, historial=None):
        super().__init__(master)
        self.historial = historial
        self.title("Crear Nueva Constancia")
        self.geometry("900x700")

        self.style = ttk.Style()
        self._configurar_estilos()
        self._build_ui()
        self._load_data()

    def _configurar_estilos(self):
        """Configura los estilos visuales"""
        self.style.theme_use('clam')
        self.style.configure('.', background='#ecf0f1')
        self.style.configure('TFrame', background='#ecf0f1')
        self.style.configure('TLabel', background='#ecf0f1',
                             foreground='#2c3e50', font=('Arial', 10))
        self.style.configure('TButton', font=('Arial', 10, 'bold'), padding=8)

        self.style.map('Primary.TButton',
                       background=[('active', '#2980b9'),
                                   ('!active', '#3498db')],
                       foreground=[('active', 'white'), ('!active', 'white')])

        self.style.map('Success.TButton',
                       background=[('active', '#27ae60'),
                                   ('!active', '#2ecc71')],
                       foreground=[('active', 'white'), ('!active', 'white')])

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

        # Docentes
        ttk.Label(form_frame, text="Docentes:").grid(
            row=0, column=0, sticky="e", padx=5, pady=5)
        self.docentes_cb = tk.Listbox(
            form_frame, selectmode=tk.MULTIPLE, height=5, exportselection=False)
        self.docentes_cb.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Evento
        ttk.Label(form_frame, text="Evento:").grid(
            row=1, column=0, sticky="e", padx=5, pady=5)
        self.evento_cb = ttk.Combobox(form_frame, state="readonly")
        self.evento_cb.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        # Responsable
        ttk.Label(form_frame, text="Responsable:").grid(
            row=2, column=0, sticky="e", padx=5, pady=5)
        self.responsable_cb = ttk.Combobox(form_frame, state="readonly")
        self.responsable_cb.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        # Tipo de constancia
        ttk.Label(form_frame, text="Tipo de constancia:").grid(
            row=3, column=0, sticky="e", padx=5, pady=5)
        self.tipo_entry = ttk.Entry(form_frame)
        self.tipo_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        # Rol del docente
        ttk.Label(form_frame, text="Rol del docente:").grid(
            row=4, column=0, sticky="e", padx=5, pady=5)
        self.rol_docente_entry = ttk.Entry(form_frame)
        self.rol_docente_entry.grid(
            row=4, column=1, padx=5, pady=5, sticky="ew")

        # Fecha de emisión
        ttk.Label(form_frame, text="Fecha de emisión:").grid(
            row=5, column=0, sticky="e", padx=5, pady=5)
        self.fecha_entry = ttk.Entry(form_frame)
        self.fecha_entry.insert(0, datetime.today().strftime("%Y-%m-%d"))
        self.fecha_entry.grid(row=5, column=1, padx=5, pady=5, sticky="ew")

        # Botones de acción
        btn_frame = ttk.Frame(config_frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=10)

        ttk.Button(btn_frame, text="Prellenar texto", command=self._prellenar_texto,
                   style='Primary.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Generar vista previa", command=self._generar_plantilla,
                   style='Success.TButton').pack(side=tk.LEFT, padx=5)

        # Pestaña de edición
        edit_frame = ttk.Frame(notebook)
        notebook.add(edit_frame, text="Editor de Texto")

        ttk.Label(edit_frame, text="Contenido de la constancia:").pack(pady=5)

        self.editor = ScrolledText(edit_frame, wrap=tk.WORD, width=100, height=20,
                                   font=('Arial', 11))
        self.editor.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Botones de edición
        edit_btn_frame = ttk.Frame(edit_frame)
        edit_btn_frame.pack(fill=tk.X, pady=10)

        ttk.Button(edit_btn_frame, text="Guardar en historial", command=self._guardar_constancia,
                   style='Success.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(edit_btn_frame, text="Exportar a PDF", command=self._exportar_pdf,
                   style='Primary.TButton').pack(side=tk.LEFT, padx=5)

    def _load_data(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Docentes
        cursor.execute("SELECT id, grado || ' ' || nombre FROM docentes")
        self.docentes = cursor.fetchall()
        for _, nombre in self.docentes:
            self.docentes_cb.insert(tk.END, nombre)

        # Evento
        cursor.execute(
            "SELECT id, nombre || ' (' || fecha || ')' FROM eventos")
        self.eventos = cursor.fetchall()
        self.evento_cb["values"] = [e[1] for e in self.eventos]

        # Responsable
        cursor.execute(
            "SELECT id, grado || ' ' || nombre || ' - ' || rol FROM responsables")
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

        # Docentes
        indices = self.docentes_cb.curselection()
        if not indices:
            messagebox.showwarning(
                "Sin docentes", "Selecciona al menos un docente.")
            return
        docentes_texto = "\n".join([self.docentes[i][1] for i in indices])

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

        abrir_editor_secciones(datos)

    def _prellenar_texto(self):
        tipo = self.tipo_entry.get().strip()
        rol_docente = self.rol_docente_entry.get().strip()
        fecha_emision = self.fecha_entry.get().strip()

        if not tipo or not rol_docente or not self.evento_cb.current() >= 0 or not self.responsable_cb.current() >= 0:
            messagebox.showwarning(
                "Campos incompletos", "Completa todos los campos antes de continuar.")
            return

        # Docentes
        indices = self.docentes_cb.curselection()
        if not indices:
            messagebox.showwarning(
                "Sin docentes", "Selecciona al menos un docente.")
            return
        docentes_texto = "\n".join([self.docentes[i][1] for i in indices])

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

        texto = TEXTO_BASE.format(
            tipo_constancia=tipo.upper(),
            docentes=docentes_texto,
            rol_docente=rol_docente,
            nombre_evento=evento_nombre,
            fecha_evento=fecha_evento,
            fecha_emision=fecha_emision,
            grado_responsable=grado_responsable,
            nombre_responsable=nombre_responsable,
            rol_responsable=rol_responsable
        )

        self.editor.delete("1.0", tk.END)
        self.editor.insert(tk.END, texto)

    def _guardar_constancia(self):
        contenido = self.editor.get("1.0", tk.END).strip()
        if not contenido:
            messagebox.showwarning(
                "Sin contenido", "No hay contenido que guardar.")
            return

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO historial_constancias (contenido, fecha_emision) VALUES (?, ?)", (
            contenido,
            self.fecha_entry.get().strip()
        ))
        conn.commit()
        conn.close()

        # ACTUALIZA EL HISTORIAL
        if self.historial:
            self.historial._load_historial()

        messagebox.showinfo("Guardado", "Constancia guardada en historial.")
        self.destroy()

    def _exportar_pdf(self):
        contenido = self.editor.get("1.0", tk.END).strip()
        if not contenido:
            messagebox.showwarning("Vacío", "El contenido está vacío.")
            return

        archivo = filedialog.asksaveasfilename(
            defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if not archivo:
            return

        c = canvas.Canvas(archivo, pagesize=LETTER)
        width, height = LETTER
        x, y = 50, height - 50

        for line in contenido.splitlines():
            c.drawString(x, y, line)
            y -= 15
            if y < 50:
                c.showPage()
                y = height - 50

        c.save()
        messagebox.showinfo(
            "PDF creado", f"El archivo se guardó como:\n{archivo}")
