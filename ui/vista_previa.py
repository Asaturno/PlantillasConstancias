# import tkinter as tk
# from tkinter import ttk, messagebox
# from tkinter.scrolledtext import ScrolledText

# class VistaPreviaPDF(tk.Toplevel):
#     def __init__(self, master, contenido):
#         super().__init__(master)
#         self.title("Vista previa de constancia")
#         self.geometry("800x600")
#         self.contenido = contenido

#         label = tk.Label(self, text="Vista previa (sólo lectura)", font=("Arial", 12, "bold"))
#         label.pack(pady=5)

#         self.preview = ScrolledText(self, wrap=tk.WORD, font=("Times New Roman", 12))
#         self.preview.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
#         self.preview.insert(tk.END, contenido)
#         self.preview.config(state=tk.DISABLED)

#         ttk.Button(self, text="Exportar a PDF", command=self._exportar_pdf).pack(pady=10)

#     def _exportar_pdf(self):
#         from reportlab.lib.pagesizes import LETTER
#         from reportlab.pdfgen import canvas
#         from tkinter import filedialog

#         archivo = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
#         if not archivo:
#             return

#         c = canvas.Canvas(archivo, pagesize=LETTER)
#         width, height = LETTER
#         x, y = 50, height - 50

#         for line in self.contenido.splitlines():
#             c.drawString(x, y, line)
#             y -= 15
#             if y < 50:
#                 c.showPage()
#                 y = height - 50

#         c.save()
#         messagebox.showinfo("PDF creado", f"El archivo se guardó como:\n{archivo}")
#         self.destroy()
