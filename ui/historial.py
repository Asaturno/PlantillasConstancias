import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
import sqlite3
import os
from ui.vista_previa import VistaPreviaPDF

DB_PATH = os.path.join("data", "constancias.db")

class HistorialConstancias(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Historial de Constancias")
        self.geometry("900x600")

        self._build_ui()
        self._load_historial()

    def _build_ui(self):
        main_frame = tk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Lista lateral
        self.constancia_list = tk.Listbox(main_frame, width=40)
        self.constancia_list.pack(side=tk.LEFT, fill=tk.Y)
        self.constancia_list.bind("<<ListboxSelect>>", self._mostrar_detalle)

        # Área de texto
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.text_area = ScrolledText(right_frame, wrap=tk.WORD, height=25)
        self.text_area.pack(fill=tk.BOTH, expand=True)

        # Botones
        btn_frame = tk.Frame(right_frame)
        btn_frame.pack(pady=5)

        ttk.Button(btn_frame, text="Copiar texto", command=self._copiar_texto).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Eliminar constancia", command=self._eliminar_constancia).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Exportar a PDF", command=self._vista_previa_pdf).pack(side=tk.LEFT, padx=5)


    def _load_historial(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()

        self.cursor.execute("SELECT id, fecha_emision FROM historial_constancias ORDER BY id DESC")
        self.registros = self.cursor.fetchall()

        self.constancia_list.delete(0, tk.END)
        for reg in self.registros:
            self.constancia_list.insert(tk.END, f"ID {reg[0]} - {reg[1]}")

    def _mostrar_detalle(self, event):
        if not self.constancia_list.curselection():
            return
        index = self.constancia_list.curselection()[0]
        constancia_id = self.registros[index][0]

        self.cursor.execute("SELECT contenido FROM historial_constancias WHERE id = ?", (constancia_id,))
        contenido = self.cursor.fetchone()[0]

        self.text_area.delete("1.0", tk.END)
        self.text_area.insert(tk.END, contenido)
    
    def _vista_previa_pdf(self):
        if not self.constancia_list.curselection():
            return
        index = self.constancia_list.curselection()[0]
        constancia_id = self.registros[index][0]

        self.cursor.execute("SELECT contenido FROM historial_constancias WHERE id = ?", (constancia_id,))
        contenido = self.cursor.fetchone()[0]

        VistaPreviaPDF(self, contenido)


    def _copiar_texto(self):
        texto = self.text_area.get("1.0", tk.END).strip()
        if texto:
            self.clipboard_clear()
            self.clipboard_append(texto)
            messagebox.showinfo("Copiado", "El texto se ha copiado al portapapeles.")

    def _eliminar_constancia(self):
        if not self.constancia_list.curselection():
            return
        index = self.constancia_list.curselection()[0]
        constancia_id = self.registros[index][0]

        if messagebox.askyesno("Eliminar", "¿Seguro que deseas eliminar esta constancia del historial?"):
            self.cursor.execute("DELETE FROM historial_constancias WHERE id = ?", (constancia_id,))
            self.conn.commit()
            messagebox.showinfo("Eliminado", "Constancia eliminada.")
            self._load_historial()
            self.text_area.delete("1.0", tk.END)

    def destroy(self):
        self.conn.close()
        super().destroy()

