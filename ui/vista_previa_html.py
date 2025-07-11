import tkinter as tk
from tkinter import ttk
import webview
import os
from pdf.pdf_generator import vista_previa

# Función para aplicar formato
def aplicar_formato(text_widget, estilo):
    try:
        start = text_widget.index("sel.first")
        end = text_widget.index("sel.last")
        text_widget.tag_add(estilo, start, end)
    except tk.TclError:
        pass

# Convierte el contenido con tags a HTML
def convertir_texto_a_html(widget):
    texto = widget.get("1.0", "end-1c")

    # Aplica formato en orden de prioridad
    for tag in widget.tag_names():
        ranges = widget.tag_ranges(tag)
        for i in range(0, len(ranges), 2):
            start = ranges[i]
            end = ranges[i + 1]
            contenido = widget.get(start, end)
            html_formato = {
                "negrita": f"<strong>{contenido}</strong>",
                "cursiva": f"<em>{contenido}</em>",
                "subrayado": f"<u>{contenido}</u>"
            }.get(tag, contenido)

            # Reemplazo básico
            texto = texto.replace(contenido, html_formato, 1)

    return texto.replace("\n", "<br>")

# Ventana principal del editor de secciones
def abrir_editor_secciones(datos_constancia):
    root = tk.Toplevel()
    root.title("Editor de Secciones de Constancia")
    root.geometry("850x600")  # Tamaño inicial

    # ---------- SCROLLABLE CONTAINER ----------
    contenedor = ttk.Frame(root)
    contenedor.pack(fill="both", expand=True)

    canvas = tk.Canvas(contenedor)
    scrollbar = ttk.Scrollbar(contenedor, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)

    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    # Frame interior dentro del canvas
    frame_interno = ttk.Frame(canvas)
    canvas.create_window((0, 0), window=frame_interno, anchor="nw")

    # Expandir scroll cuando se agregan elementos
    def ajustar_scroll(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    frame_interno.bind("<Configure>", ajustar_scroll)

    # Rueda del mouse
    canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

    # ---------- SECCIONES ----------
    cuerpo = (f"Como {datos_constancia['rol_docente']} en {datos_constancia['nombre_evento']}, actividad llevada a cabo el {datos_constancia['fecha_evento']}.")
    if datos_constancia['avalada']:
        cuerpo += (f"\n\nActividad avalada por los H.H. Consejos Académico y de Gobierno, ambos en sesión ordinaria, celebradas el {datos_constancia['fecha_evento']}")

    secciones = {
        "Encabezado": f"Universidad Autónoma del Estado de México",
        "Introducción": f"El que suscribe, {datos_constancia['rol_responsable']}, otorga la presente:",
        "Título": f"Constancia de {datos_constancia['tipo']}",
        "Docentes": f"{datos_constancia['docentes']}",
        "Cuerpo": cuerpo,
        "Cierre": f"Toluca, Estado de México, {datos_constancia['fecha_emision']}",
        "Firma": f"ATENTAMENTE\nPATRIA CIENCIA Y TRABAJO\n“2025, 195 años de la apertura del Instituto Literario en la Ciudad de Toluca”\n\n\n\n\n\n{datos_constancia['grado_responsable']}\n{datos_constancia['nombre_responsable']}\n{datos_constancia['rol_responsable']}",
        "Pie": f"Calle Heriberto Enríquez No. 904, esquina Ceboruco,\nCol. Azteca C.P. 50150 Toluca, Estado de México\nTels. 722.217.12.17, 722.212.08.08\nplantelangelmariagaribay@uaemex.mx"
    }


    text_widgets = {}

    for titulo, contenido in secciones.items():
        frame = ttk.LabelFrame(frame_interno, text=titulo)
        frame.pack(fill="x", padx=10, pady=5, anchor="n")

        text_area = tk.Text(frame, height=5, wrap="word", font=("Arial", 12))
        text_area.insert("1.0", contenido)
        text_area.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        # Estilos
        text_area.tag_configure("negrita", font=("Arial", 12, "bold"))
        text_area.tag_configure("cursiva", font=("Arial", 12, "italic"))
        text_area.tag_configure("subrayado", font=("Arial", 12, "underline"))

        # Botones de formato
        botones = ttk.Frame(frame)
        botones.pack(side="right", padx=5, pady=5)

        ttk.Button(botones, text="B", command=lambda w=text_area: aplicar_formato(w, "negrita")).pack()
        ttk.Button(botones, text="I", command=lambda w=text_area: aplicar_formato(w, "cursiva")).pack()
        ttk.Button(botones, text="U", command=lambda w=text_area: aplicar_formato(w, "subrayado")).pack()

        text_widgets[titulo] = text_area


    # ---------- BOTÓN DE VISTA PREVIA ----------
    vista_btn = ttk.Button(frame_interno, text="Vista previa", command=lambda: generar_vista_previa(text_widgets, datos_constancia))
    vista_btn.pack(pady=20)

def generar_vista_previa(text_widgets, datos_constancia):
    secciones_html={}
    for nombre, widget in text_widgets.items():
        html = convertir_texto_a_html(widget)
        secciones_html[nombre] = html
    vista_previa(secciones_html, datos_constancia)
