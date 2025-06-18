import os
import webview
from weasyprint import HTML
from tkinter import filedialog, messagebox
import sqlite3

DB_PATH = os.path.join("data", "constancias.db")

class ConstanciaEditorAPI:
    def __init__(self, html_renderizado, datos_constancia):
        self.html_renderizado = html_renderizado
        self.datos_constancia = datos_constancia
        
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

    def guardar_constancia(self):
        datos_constancia = self.datos_constancia
        # Conexión a BD
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Obtener datos
        tipo = datos_constancia['tipo']
        fecha_elab = datos_constancia['fecha_emision']
        id_evento = datos_constancia['id_evento']
        id_responsable = datos_constancia['id_responsable']
        docentes = datos_constancia['docentes']
        rol_docente = datos_constancia['rol_docente']

        # Insertar datos
        cursor.execute('''
            INSERT INTO constancias (tipo, fecha_elaboracion, id_evento, id_responsable, docentes, rol_docente, html)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (tipo, fecha_elab, id_evento, id_responsable, docentes, rol_docente, self.html_renderizado))
        messagebox.showinfo("Guardado", "Constancia guardada en historial.")

        conn.commit()
        conn.close()

import base64

def convertir_imagen_base64(ruta):
    with open(ruta, "rb") as img_file:
        encoded = base64.b64encode(img_file.read()).decode("utf-8")
    return f"data:image/png;base64,{encoded}"

def vista_previa(text_widgets, datos_constancia):
    # Cargar plantilla HTML
    ruta_base = os.path.dirname(os.path.abspath(__file__))
    ruta_plantilla = os.path.join(ruta_base, "plantilla_constancia.html")

    with open(ruta_plantilla, "r", encoding="utf-8") as f:
        plantilla = f.read()

    # Ruta absoluta al logo
    ruta_base = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(ruta_base, "..", "assets", "logo.png")
    logo_path = os.path.abspath(logo_path)
    logo_url = f"file:///{logo_path.replace(os.sep, '/')}"
    print("Logo URL:", logo_url)

    logo_base64 = convertir_imagen_base64(logo_path)

    # Pie de pagina 
    ruta_base = os.path.dirname(os.path.abspath(__file__))
    piebg_path = os.path.join(ruta_base, "..", "assets", "descarga_e.jpg")
    piebg_path = os.path.abspath(piebg_path)
    piebg_url = f"file:///{piebg_path.replace(os.sep, '/')}"
    print("Logo URL:", piebg_url)

    piebg_base64 = convertir_imagen_base64(piebg_path)
    # Reemplazo de marcadores con datos reales
    html_renderizado = plantilla.format(
        logo=logo_base64,
        encabezado=text_widgets['Encabezado'],
        intro=text_widgets['Introducción'],
        titulo=text_widgets['Título'],
        docentes=text_widgets['Docentes'],
        cuerpo=text_widgets['Cuerpo'],
        cierre=text_widgets['Cierre'],
        firma=text_widgets['Firma'],
        pie=text_widgets['Pie'],
        fondo_pie=piebg_base64
    )

    crear_visa_previa(html_renderizado, datos_constancia)
    # api = ConstanciaEditorAPI(html_renderizado)

    # webview.create_window(
    #         "Vista previa de la constancia",
    #         html=html_renderizado + """
    #         <br><button onclick="window.pywebview.api.exportar_pdf()">Exportar a PDF</button>
    #         <br><button onclick="window.pywebview.api.guardar_constancia(datos_constancia)">Guardar Constancia</button>
    #         """,
    #         js_api=api,
    #         width=850,
    #         height=1000
    #     )
    # webview.start()

def crear_visa_previa(html_renderizado, datos_constancia):
    api = ConstanciaEditorAPI(html_renderizado, datos_constancia)

    webview.create_window(
            "Vista previa de la constancia",
            html=html_renderizado + """
            <br><button onclick="window.pywebview.api.exportar_pdf()">Exportar a PDF</button>
            <br><button onclick="window.pywebview.api.guardar_constancia()">Guardar Constancia</button>
            """,
            js_api=api,
            width=850,
            height=1000
        )
    webview.start()