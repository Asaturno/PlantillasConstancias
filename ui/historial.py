import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
import sqlite3
import os
# from ui.vista_previa import VistaPreviaPDF
from ui.crear_constancia import CrearConstancia
import tempfile
import webbrowser
from weasyprint import HTML
from tkinter import filedialog, messagebox


DB_PATH = os.path.expanduser("~") + "/OneDrive - Universidad Autónoma del Estado de México/UAEM/Proyecto Constancias/constancias.db"



class HistorialConstancias(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Historial de Constancias")
        self.geometry("900x650")

        self.style = ttk.Style()
        self._configurar_estilos()

        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()

        self._build_ui()
        self._load_historial()

    def _configurar_estilos(self):
        """Configura los estilos visuales"""
        self.style.theme_use('clam')
        self.style.configure('.', background='#ecf0f1')
        self.style.configure('TFrame', background='#ecf0f1')
        self.style.configure('TLabel', background='#ecf0f1',
                             foreground='#2c3e50', font=('Arial', 10))
        self.style.configure('TButton', font=('Arial', 10, 'bold'), padding=8)
        self.style.configure('Treeview', font=('Arial', 10), rowheight=25)
        self.style.configure('Treeview.Heading', font=('Arial', 10, 'bold'),
                             background='#2c3e50', foreground='white')

        self.style.map('Primary.TButton',
                       background=[('active', '#2980b9'),
                                   ('!active', '#3498db')],
                       foreground=[('active', 'white'), ('!active', 'white')])

        self.style.map('Danger.TButton',
                       background=[('active', '#c0392b'),
                                   ('!active', '#e74c3c')],
                       foreground=[('active', 'white'), ('!active', 'white')])

        self.style.map('Success.TButton',
                       background=[('active', '#27ae60'),
                                   ('!active', '#2ecc71')],
                       foreground=[('active', 'white'), ('!active', 'white')])

    def _build_ui(self):
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Panel izquierdo (lista)
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        ttk.Label(left_frame, text="Constancias registradas",
                  font=('Arial', 11, 'bold')).pack(pady=5)

        filter_frame = ttk.LabelFrame(left_frame, text="Filtros de búsqueda")
        filter_frame.pack(fill=tk.X, pady=5)

        ttk.Label(filter_frame, text="Docente:").grid(
            row=0, column=0, sticky='e')
        self.docente_entry = ttk.Entry(filter_frame)
        self.docente_entry.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(filter_frame, text="Evento:").grid(
            row=1, column=0, sticky='e')
        self.evento_entry = ttk.Entry(filter_frame)
        self.evento_entry.grid(row=1, column=1, padx=5, pady=2)


        ttk.Button(filter_frame, text="Buscar", command=self._aplicar_filtros).grid(
            row=3, column=0, columnspan=2, pady=5)

        # Sugerencias de docente
        self.docente_sugerencias = tk.Listbox(filter_frame, height=3)
        self.docente_sugerencias.grid(row=0, column=2, padx=5)
        self.docente_sugerencias.bind(
            "<<ListboxSelect>>", self._seleccionar_docente)
        self.docente_sugerencias.grid_remove()

        # Sugerencias de evento
        self.evento_sugerencias = tk.Listbox(filter_frame, height=3)
        self.evento_sugerencias.grid(row=1, column=2, padx=5)
        self.evento_sugerencias.bind(
            "<<ListboxSelect>>", self._seleccionar_evento)
        self.evento_sugerencias.grid_remove()

        self.docente_entry.bind(
            "<KeyRelease>", self._actualizar_sugerencias_docente)
        self.evento_entry.bind(
            "<KeyRelease>", self._actualizar_sugerencias_evento)

        self.constancia_list = ttk.Treeview(left_frame, columns=(
            'ID', 'Fecha'), show='headings', height=20)
        self.constancia_list.heading('ID', text='ID')
        self.constancia_list.heading('Fecha', text='Fecha')
        self.constancia_list.column('ID', width=50, anchor='center')
        self.constancia_list.column('Fecha', width=150, anchor='center')
        self.constancia_list.pack(fill=tk.Y)
        self.constancia_list.bind("<<TreeviewSelect>>", self._mostrar_detalle)

        scrollbar = ttk.Scrollbar(
            left_frame, orient="vertical", command=self.constancia_list.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.constancia_list.configure(yscrollcommand=scrollbar.set)

        # Panel derecho (detalle)
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH,
                         expand=True, padx=5, pady=5)

        ttk.Label(right_frame, text="Vista previa",
                  font=('Arial', 11, 'bold')).pack(pady=5)

        self.preview_btn = ttk.Button(right_frame, text="Abrir vista previa en navegador", command=self._vista_previa_html)
        self.preview_btn.pack(pady=10)
        # self.text_area = ScrolledText(
        #     right_frame, wrap=tk.WORD, font=('Arial', 11))
        # self.text_area.pack(fill=tk.BOTH, expand=True)

        # Botones de acción
        btn_frame = ttk.Frame(right_frame)
        btn_frame.pack(fill=tk.X, pady=10)

        ttk.Button(btn_frame, text="Crear nueva constancia",
                   command=self._abrir_crear_constancia).pack(side=tk.LEFT, padx=5)
        # ttk.Button(btn_frame, text="Copiar texto", command=self._copiar_texto,
        #            style='Primary.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Exportar a PDF", command=self._exportar_pdf,
                   style='Success.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Eliminar constancia", command=self._eliminar_constancia,
                   style='Danger.TButton').pack(side=tk.RIGHT, padx=5)

    def _load_historial(self):
        self.cursor.execute("SELECT id, fecha_elaboracion FROM constancias ORDER BY id DESC")
        self.registros = self.cursor.fetchall()

        for item in self.constancia_list.get_children():
            self.constancia_list.delete(item)
              
        for reg in self.registros:
            self.constancia_list.insert('', 'end', values=(reg[0], reg[1]))

    def _mostrar_detalle(self, event):
        if not self.constancia_list.selection():
            return

        selected_item = self.constancia_list.selection()[0]
        constancia_id = self.constancia_list.item(selected_item)['values'][0]

        # self.cursor.execute(
        #     "SELECT contenido FROM historial_constancias WHERE id = ?", (constancia_id,))
        # contenido = self.cursor.fetchone()[0]

        # self.text_area.config(state=tk.NORMAL)
        # self.text_area.delete("1.0", tk.END)
        # self.text_area.insert(tk.END, contenido)
        # self.text_area.config(state=tk.DISABLED)

    def _vista_previa_html(self):
        if not self.constancia_list.selection():
            messagebox.showwarning("Advertencia", "Selecciona una constancia para ver la vista previa.")
            return
        
        selected_item = self.constancia_list.selection()[0]
        constancia_id = self.constancia_list.item(selected_item)['values'][0]
        
        self.cursor.execute("SELECT html FROM constancias WHERE id = ?", (constancia_id,))
        resultado = self.cursor.fetchone()
        if resultado:
            html_content = resultado[0]
            with tempfile.NamedTemporaryFile('w', delete=False, suffix=".html", encoding="utf-8") as f:
                f.write(html_content)
                webbrowser.open('file://' + os.path.abspath(f.name))


    def _exportar_pdf(self):
        if not self.constancia_list.selection():
            messagebox.showwarning("Advertencia", "Selecciona una constancia para ver la vista previa.")
            return
        
        selected_item = self.constancia_list.selection()[0]
        constancia_id = self.constancia_list.item(selected_item)['values'][0]
        
        self.cursor.execute("SELECT html FROM constancias WHERE id = ?", (constancia_id,))
        resultado = self.cursor.fetchone()
        if resultado:
            html_content = resultado[0]

            # Pedir ruta de guardado
            ruta_pdf = filedialog.asksaveasfilename(defaultextension=".pdf",
                                                    filetypes=[("Archivos PDF", "*.pdf")],
                                                    title="Guardar constancia como PDF")

            if ruta_pdf:
                try:
                    HTML(string=html_content, base_url=os.getcwd()).write_pdf(ruta_pdf)
                    messagebox.showinfo("Éxito", "La constancia fue exportada correctamente.")
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo exportar el PDF:\n{e}")
            else:
                messagebox.showinfo("Cancelado", "Exportación cancelada por el usuario.")

    def _eliminar_constancia(self):
        if not self.constancia_list.selection():
            return

        selected_item = self.constancia_list.selection()[0]
        constancia_id = self.constancia_list.item(selected_item)['values'][0]

        if messagebox.askyesno("Eliminar", "¿Seguro que deseas eliminar esta constancia del historial?"):
            self.cursor.execute(
                "DELETE FROM constancias WHERE id = ?", (constancia_id,))
            self.conn.commit()
            messagebox.showinfo("Eliminado", "Constancia eliminada.")
            self._load_historial()
            self.text_area.config(state=tk.NORMAL)
            self.text_area.delete("1.0", tk.END)
            self.text_area.config(state=tk.DISABLED)

    def destroy(self):
        self.conn.close()
        super().destroy()

    def _abrir_crear_constancia(self):
        CrearConstancia(self.master, historial=self)

    def _actualizar_sugerencias_docente(self, event):
        texto = self.docente_entry.get().strip()
        self.docente_sugerencias.delete(0, tk.END)
        if texto:
            self.cursor.execute(
                "SELECT DISTINCT grado || ' ' || nombre FROM docentes WHERE nombre LIKE ?", (f"%{texto}%",))
            resultados = self.cursor.fetchall()
            if resultados:
                for r in resultados:
                    self.docente_sugerencias.insert(tk.END, r[0])
                self.docente_sugerencias.grid()
            else:
                self.docente_sugerencias.grid_remove()
        else:
            self.docente_sugerencias.grid_remove()

    def _actualizar_sugerencias_evento(self, event):
        texto = self.evento_entry.get().strip()
        self.evento_sugerencias.delete(0, tk.END)
        if texto:
            self.cursor.execute(
                "SELECT DISTINCT nombre FROM eventos WHERE nombre LIKE ?", (f"%{texto}%",))
            resultados = self.cursor.fetchall()
            if resultados:
                for r in resultados:
                    self.evento_sugerencias.insert(tk.END, r[0])
                self.evento_sugerencias.grid()
            else:
                self.evento_sugerencias.grid_remove()
        else:
            self.evento_sugerencias.grid_remove()

    def _aplicar_filtros(self):
        docente = self.docente_entry.get().strip()
        evento = self.evento_entry.get().strip()

        query = "SELECT id, fecha_elaboracion, contenido FROM constancias WHERE 1=1"
        params = []

        if docente:
            query += " AND contenido LIKE ?"
            params.append(f"%{docente}%")

        if evento:
            query += " AND id_evento IN (SELECT id FROM eventos WHERE nombre LIKE ?)"
            params.append(f"%{evento}%")

        self.cursor.execute(query, params)
        resultados = self.cursor.fetchall()

        # Limpiar lista
        for item in self.constancia_list.get_children():
            self.constancia_list.delete(item)

        # Mostrar solo los filtrados
        for reg in resultados:
            self.constancia_list.insert('', 'end', values=(reg[0], reg[1]))

        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete("1.0", tk.END)
        self.text_area.config(state=tk.DISABLED)

    def _seleccionar_docente(self, event):
        seleccion = self.docente_sugerencias.get(
            self.docente_sugerencias.curselection())
        self.docente_entry.delete(0, tk.END)
        self.docente_entry.insert(0, seleccion)
        self.docente_sugerencias.grid_remove()
        self._aplicar_filtros()

    def _seleccionar_evento(self, event):
        seleccion = self.evento_sugerencias.get(
            self.evento_sugerencias.curselection())
        self.evento_entry.delete(0, tk.END)
        self.evento_entry.insert(0, seleccion)
        self.evento_sugerencias.grid_remove()
        self._aplicar_filtros()
