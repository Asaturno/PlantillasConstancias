import webview

def abrir_editor(html_contenido):
    # Contenido HTML con TinyMCE 
    html_editor = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="UTF-8">
      <script src="https://cdn.tiny.cloud/1/nj7cl63s6yjhu7aa6mkc0y0yjph4725hnk5ia2lrwlvrctas/tinymce/7/tinymce.min.js" referrerpolicy="origin"></script>
      <script>
        let initial_content = `{html_contenido.replace("`", "'")}`;
        tinymce.init({{
          selector: '#editor',
          height: 600,
          menubar: false,
          plugins: 'lists link image table code',
          toolbar: 'undo redo | styles | bold italic underline | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | code',
          setup: function (editor) {{
            editor.on('init', function () {{
              editor.setContent(initial_content);
            }});
          }}
        }});
      </script>
    </head>
    <body>
      <textarea id="editor"></textarea>
    </body>
    </html>
    """
    webview.create_window("Editor de Constancia", html=html_editor, width=900, height=700)
    webview.start()
