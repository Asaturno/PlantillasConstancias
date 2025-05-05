import webview

class API:
    def exportar_pdf(self, html_content):
        from weasyprint import HTML
        from tkinter import filedialog, Tk

        try:
            root = Tk()
            root.withdraw()
            ruta = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                title="Guardar constancia como PDF"
            )
            root.destroy()

            if not ruta:
                return "Exportación cancelada por el usuario"

            HTML(string=html_content).write_pdf(ruta)
            return "PDF exportado con éxito"
        except Exception as e:
            return f"Error: {str(e)}"

def abrir_editor(html_generado):
    html_editor = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Editor de Constancia</title>
        <link href="https://cdn.quilljs.com/1.3.6/quill.snow.css" rel="stylesheet">
        <style>
            #editor {{
                height: 500px;
                background: white;
                padding: 20px;
            }}
            .botonera {{
                margin-top: 15px;
            }}
        </style>
    </head>
    <body>
        <h2>Editor de Constancia</h2>
        <div id="editor">{html_generado}</div>
        <div class="botonera">
            <button onclick="exportarPDF()">Exportar a PDF</button>
        </div>

        <script src="https://cdn.quilljs.com/1.3.6/quill.js"></script>
        <script>
            var quill = new Quill('#editor', {{
                theme: 'snow'
            }});

            async function exportarPDF() {{
                const htmlContent = document.querySelector('.ql-editor').innerHTML;
                const resultado = await window.pywebview.api.exportar_pdf(htmlContent);
                alert(resultado);
            }}
        </script>
    </body>
    </html>
    """

    ventana = webview.create_window("Vista previa de constancia", html=html_editor, js_api=API(), width=800, height=700)
    webview.start()
