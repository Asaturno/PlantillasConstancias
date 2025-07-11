import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import sqlite3
import hashlib
from ui.main_window import MainWindow
from ui.crear_primer_superusuario import CrearPrimerSuperusuario
import os

DB_PATH = os.path.expanduser(r"C:/Users/aleja/OneDrive - Universidad Autónoma del Estado de México/UAEM/Proyecto Constancias/constancias.db")

def verificar_superusuario_inicial():
    """Verifica si existe al menos un superusuario en la base de datos"""
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM usuarios WHERE es_superusuario = 1")
        count = cursor.fetchone()[0]
        return count > 0
    except sqlite3.Error as e:
        print(f"Error al verificar superusuario: {e}")
        return False
    finally:
        if conn:
            conn.close()


def main():
    from database.db_setup import crear_base_de_datos
    crear_base_de_datos()

    root = tk.Tk()
    root.withdraw()  # Ocultar hasta que esté lista la interfaz

    # Verificar superusuario inicial
    if not verificar_superusuario_inicial():
        messagebox.showinfo(
            "Primer inicio",
            "No se encontraron superusuarios. Debe crear un superusuario inicial."
        )
        crear_super = CrearPrimerSuperusuario(root)
        root.wait_window(crear_super)

        if not verificar_superusuario_inicial():
            messagebox.showerror(
                "Error",
                "No se creó ningún superusuario. La aplicación no puede continuar."
            )
            root.destroy()
            return

    # Establecer configuración base
    root.title("Sistema de Constancias")
    root.geometry("900x650")  # ← Aumentamos tamaño para mejor render inicial

    # Crear la ventana principal (pero aún no mostrarla)
    app = MainWindow(master=root)

    # Forzar que todo se actualice internamente antes de mostrar
    root.update_idletasks()
    root.deiconify()
    root.event_generate("<Configure>")  # ← Forzar evento de redimensionamiento

    # Mostrar y mantener al frente
    root.lift()
    root.focus_force()

    # Loop principal
    app.mainloop()


if __name__ == "__main__":
    main()
