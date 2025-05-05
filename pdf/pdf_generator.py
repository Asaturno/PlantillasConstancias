import os
import webview
from weasyprint import HTML
from tkinter import filedialog, messagebox
import threading
from datetime import datetime

class ConstanciaEditorAPI:
    def __init__(self, html_renderizado):
        self.html_renderizado = html_renderizado

    def exportar_pdf(self):
        # Pedir ruta de guardado
        ruta_pdf = filedialog.asksaveasfilename(defaultextension=".pdf",
                                                filetypes=[("Archivos PDF", "*.pdf")],
                                                title="Guardar constancia como PDF")

        if ruta_pdf:
            try:
                HTML(string=self.html_renderizado, base_url=os.getcwd()).write_pdf(ruta_pdf)
                messagebox.showinfo("Éxito", "La constancia fue exportada correctamente.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo exportar el PDF:\n{e}")
        else:
            messagebox.showinfo("Cancelado", "Exportación cancelada por el usuario.")

def abrir_editor(datos_constancia):
    # Cargar plantilla HTML
    ruta_base = os.path.dirname(os.path.abspath(__file__))
    ruta_plantilla = os.path.join(ruta_base, "plantilla_constancia.html")

    with open(ruta_plantilla, "r", encoding="utf-8") as f:
        plantilla = f.read()

    # Ruta absoluta al logo
    logo_path = os.path.abspath("logo_uaemex.png")
    logo_url = f"file:///{logo_path.replace(os.sep, '/')}"

    # Reemplazo de marcadores con datos reales
    html_renderizado = plantilla.format(
        rol_responsable=datos_constancia['rol_responsable'],
        tipo=datos_constancia['tipo'],
        docentes=datos_constancia['docentes'],
        rol_docente=datos_constancia['rol_docente'],
        nombre_evento=datos_constancia['nombre_evento'],
        fecha_evento=datos_constancia['fecha_evento'],
        fecha_emision=datetime.now().strftime("%d de %B de %Y"),
        grado_responsable=datos_constancia['grado_responsable'],
        nombre_responsable=datos_constancia['nombre_responsable'],
        logo=logo_url  # Si usas {logo} en plantilla
    )

    api = ConstanciaEditorAPI(html_renderizado)


    webview.create_window(
            "Vista previa de la constancia",
            html=html_renderizado + """
            <br><button onclick="window.pywebview.api.exportar_pdf()">Exportar a PDF</button>
            """,
            js_api=api,
            width=850,
            height=1000
        )
    webview.start()
