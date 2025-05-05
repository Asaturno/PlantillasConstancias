import webview

def abrir_editor(html_contenido):
    # Escapar el contenido para insertar en JavaScript
    html_contenido = html_contenido.replace("\\", "\\\\").replace("`", "'").replace("\n", "").replace('"', '\\"')

    html_editor = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <title>Editor de Constancia</title>
      <link href="https://cdn.quilljs.com/1.3.6/quill.snow.css" rel="stylesheet">
      <script src="https://cdn.quilljs.com/1.3.6/quill.min.js"></script>
      <style>
        body {{
          margin: 0;
          padding: 20px;
          font-family: sans-serif;
        }}
        #editor-container {{
          height: 500px;
          background: #fff;
        }}
      </style>
    </head>
    <body>
      <div id="editor-container"></div>

      <script>
        var quill = new Quill('#editor-container', {{
          theme: 'snow',
          modules: {{
            toolbar: [
              ['bold', 'italic', 'underline'],
              ['link', 'image'],
              [{{
                'list': 'ordered'
              }}, {{
                'list': 'bullet'
              }}],
              ['clean']
            ]
          }}
        }});

        // Insertar contenido HTML inicial
        const html = "{html_contenido}";
        const temp = document.createElement('div');
        temp.innerHTML = html;
        quill.setContents(quill.clipboard.convert(temp.innerHTML), 'silent');

        
      </script>
    </body>
    </html>
    """
#// Futuro: podríamos obtener el contenido con quill.root.innerHTML o quill.getContents()
    webview.create_window("Editor de Constancia", html=html_editor, width=900, height=700)
    webview.start()

