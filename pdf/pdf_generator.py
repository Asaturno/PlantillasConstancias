import os
import webview
from weasyprint import HTML
from tkinter import filedialog, messagebox


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

def vista_previa(text_widgets):
    # Cargar plantilla HTML
    ruta_base = os.path.dirname(os.path.abspath(__file__))
    ruta_plantilla = os.path.join(ruta_base, "plantilla_constancia.html")

    with open(ruta_plantilla, "r", encoding="utf-8") as f:
        plantilla = f.read()

    # Ruta absoluta al logo
    logo_path = os.path.abspath("logo.png")
    logo_url = f"file:///{logo_path.replace(os.sep, '/')}"

    # Reemplazo de marcadores con datos reales
    html_renderizado = plantilla.format(
        logo=logo_url,
        encabezado=text_widgets['Encabezado'],
        intro=text_widgets['Introducción'],
        titulo=text_widgets['Título'],
        docentes=text_widgets['Docentes'],
        cuerpo=text_widgets['Cuerpo'],
        cierre=text_widgets['Cierre'],
        firma=text_widgets['Firma'],
        pie=text_widgets['Pie']
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