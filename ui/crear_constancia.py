import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
import sqlite3
import os
from datetime import datetime
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
from tkinter import filedialog

from pdf.pdf_generator import abrir_editor

DB_PATH = os.path.join("data", "constancias.db")

# HTML_PLANTILLA = """

#     <!-- Logo superior -->
#     <img src="logo_uaemex.png" alt="Logo UAEM" style="width: 100px; margin-bottom: 10px;">

#     <!-- Encabezado -->
#     <div style="font-weight: bold;">Universidad Autónoma del Estado de México</div>

#     <!-- Introducción -->
#     <div style="text-align: justify; margin: 30px auto; max-width: 700px; line-height: 1.6;">
#       El que suscribe, {rol_responsable}, otorga la presente: <br>
#     </div>

#     <!-- Título -->
#     <div style="font-weight: bold; font-size: 22px; margin-top: 20px;">Constancia de {tipo}</div>

#     <!-- Nombre -->
#     <div>a:</div>
#     <div style="font-weight: bold; font-size: 18px; margin: 10px 0;">{docentes}</div>

#     <!-- Cuerpo -->
#     <div style="text-align: justify; margin: 30px auto; max-width: 700px; line-height: 1.6;">
#       Como <strong>{rol_docente}</strong> en
#       <strong>{nombre_evento}</strong> actividad llevada a cabo el 
#       <strong>{fecha_evento}</strong> del año en curso, durante el periodo<strong>---</strong>.
#       <br><br>
#     </div>

#     <!-- Lugar y fecha -->
#     <div>Toluca, Edo. de México {fecha_emision}.</div>

#     <!-- Firma -->
#     <div style="margin-top: 60px; font-weight: bold;">
#       ATENTAMENTE<br>
#       PATRIA CIENCIA Y TRABAJO<br>
#       <em>“2025, 195 años de la apertura del Instituto Literario en la Ciudad de Toluca</em><br><br><br>
#       {grado_responsable}<br>
#       {nombre_responsable}<br>
#       {rol_responsable}
#     </div>

#     <!-- Pie de página -->
#     <div style="font-size: 12px; margin-top: 40px; text-align: left;">
#       C.c.p. Archivo<br>
#       ZGMV/eez<br><br>
#       Calle Heriberto Enríquez No. 904, esquina Ceboruco,<br>
#       Col. Azteca C.P. 50150 Toluca, Estado de México<br>
#       Tels. 722.217.12.17, 722.212.08.08<br>
#       plantelangelmariagaribay@uaemex.mx
#     </div>
# """

class CrearConstancia(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Crear Nueva Constancia")
        self.geometry("850x700")

        self._build_ui()
        self._load_data()

    def _build_ui(self):
        # Selección de datos
        form = tk.Frame(self)
        form.pack(pady=10, fill=tk.X)
 
        tk.Label(form, text="Docentes:").grid(row=0, column=0, sticky="e")
        self.docentes_cb = tk.Listbox(form, selectmode=tk.MULTIPLE, height=5, exportselection=False)
        self.docentes_cb.grid(row=0, column=1, padx=5)

        tk.Label(form, text="Evento:").grid(row=1, column=0, sticky="e")
        self.evento_cb = ttk.Combobox(form, state="readonly")
        self.evento_cb.grid(row=1, column=1, padx=5)

        tk.Label(form, text="Responsable:").grid(row=2, column=0, sticky="e")
        self.responsable_cb = ttk.Combobox(form, state="readonly")
        self.responsable_cb.grid(row=2, column=1, padx=5)

        tk.Label(form, text="Tipo de constancia:").grid(row=3, column=0, sticky="e")
        self.tipo_entry = tk.Entry(form)
        self.tipo_entry.grid(row=3, column=1, padx=5)

        tk.Label(form, text="Rol del docente en el evento:").grid(row=4, column=0, sticky="e")
        self.rol_docente_entry = tk.Entry(form)
        self.rol_docente_entry.grid(row=4, column=1, padx=5)

        tk.Label(form, text="Fecha de emisión:").grid(row=5, column=0, sticky="e")
        self.fecha_entry = tk.Entry(form)
        self.fecha_entry.insert(0, datetime.today().strftime("%Y-%m-%d"))
        self.fecha_entry.grid(row=5, column=1, padx=5)

        # Editor de texto
        tk.Label(self, text="Vista previa de la constancia (editable):").pack()
        self.editor = ScrolledText(self, wrap=tk.WORD, width=100, height=20)
        self.editor.pack(padx=10, pady=10)

        # Botones
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)

        # ttk.Button(btn_frame, text="Prellenar texto", command=self._prellenar_texto).grid(row=0, column=0, padx=10)
        ttk.Button(btn_frame, text="Generar vista previa", command=self._generar_plantilla).grid(row=2, column=1, padx=10) #botón nuevo, abrir TinyMCE
        # ttk.Button(btn_frame, text="Guardar en historial", command=self._guardar_constancia).grid(row=0, column=1, padx=10)
        # ttk.Button(btn_frame, text="Exportar a PDF", command=self._exportar_pdf).grid(row=1, column=1, padx=10)


    def _load_data(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Docentes
        cursor.execute("SELECT id, grado || ' ' || nombre FROM docentes")
        self.docentes = cursor.fetchall()
        for _, nombre in self.docentes:
            self.docentes_cb.insert(tk.END, nombre)

        # Evento
        cursor.execute("SELECT id, nombre || ' (' || fecha || ')' FROM eventos")
        self.eventos = cursor.fetchall()
        self.evento_cb["values"] = [e[1] for e in self.eventos]

        # Responsable
        cursor.execute("SELECT id, grado || ' ' || nombre || ' - ' || rol FROM responsables")
        self.responsables = cursor.fetchall()
        self.responsable_cb["values"] = [r[1] for r in self.responsables]

        conn.close()

    def _generar_plantilla(self):
        tipo = self.tipo_entry.get().strip()
        rol_docente = self.rol_docente_entry.get().strip()
        fecha_emision = self.fecha_entry.get().strip()


        if not tipo or not rol_docente or not self.evento_cb.current() >= 0 or not self.responsable_cb.current() >= 0:
            messagebox.showwarning("Campos incompletos", "Completa todos los campos antes de continuar.")
            return
        
        # Docentes
        indices = self.docentes_cb.curselection()
        if not indices:
            messagebox.showwarning("Sin docentes", "Selecciona al menos un docente.")
            return
        docentes_texto = "\n".join([self.docentes[i][1] for i in indices])

        # Evento y responsable
        evento_id, evento_str = self.eventos[self.evento_cb.current()]
        evento_nombre, fecha_evento = evento_str.split(' (')
        fecha_evento = fecha_evento.replace(")", "")

        responsable_id, responsable_str = self.responsables[self.responsable_cb.current()]
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT grado, nombre, rol FROM responsables WHERE id = ?", (responsable_id,))
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

        abrir_editor(datos)

    # def _guardar_constancia(self):
    #     contenido = self.editor.get("1.0", tk.END).strip()
    #     if not contenido:
    #         messagebox.showwarning("Sin contenido", "No hay contenido que guardar.")
    #         return

    #     conn = sqlite3.connect(DB_PATH)
    #     cursor = conn.cursor()
    #     cursor.execute("INSERT INTO historial_constancias (contenido, fecha_emision) VALUES (?, ?)", (
    #         contenido,
    #         self.fecha_entry.get().strip()
    #     ))
    #     conn.commit()
    #     conn.close()

    #     messagebox.showinfo("Guardado", "Constancia guardada en historial.")
    #     self.destroy()


    def _exportar_pdf(self):
        contenido = self.editor.get("1.0", tk.END).strip()
        if not contenido:
            messagebox.showwarning("Vacío", "El contenido está vacío.")
            return

        archivo = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
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
        messagebox.showinfo("PDF creado", f"El archivo se guardó como:\n{archivo}")

