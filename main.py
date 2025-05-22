import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import sqlite3
import hashlib
from ui.main_window import MainWindow
from ui.crear_primer_superusuario import CrearPrimerSuperusuario

def verificar_superusuario_inicial():
    """Verifica si existe al menos un superusuario en la base de datos"""
    conn = None
    try:
        conn = sqlite3.connect("data/constancias.db")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE es_superusuario = 1")
        count = cursor.fetchone()[0]
        return count > 0
    except sqlite3.Error as e:
        print(f"Error al verificar superusuario: {e}")
        return False
    finally:
        if conn:
            conn.close()

def main():
    # Crear base de datos y tablas si no existen
    from database.db_setup import crear_base_de_datos
    crear_base_de_datos()
    
    root = tk.Tk()
    root.withdraw()  # Ocultar ventana principal temporalmente
    
    # Verificar si existe al menos un superusuario
    if not verificar_superusuario_inicial():
        # Mostrar ventana para crear primer superusuario
        messagebox.showinfo(
            "Primer inicio",
            "No se encontraron superusuarios. Debe crear un superusuario inicial."
        )
        
        # Mostrar diálogo para crear superusuario
        crear_super = CrearPrimerSuperusuario(root)
        root.wait_window(crear_super)
        
        # Verificar nuevamente después de cerrar el diálogo
        if not verificar_superusuario_inicial():
            messagebox.showerror(
                "Error", 
                "No se creó ningún superusuario. La aplicación no puede continuar."
            )
            root.destroy()
            return
    
    # Mostrar ventana principal
    root.deiconify()
    root.title("Sistema de Constancias")
    root.geometry("400x500")  # Tamaño ajustado para mejor visualización
    
    # Configurar estilo inicial
    style = ttk.Style()
    style.theme_use('clam')
    
    app = MainWindow(master=root)
    app.mainloop()

if __name__ == "__main__":
    main()