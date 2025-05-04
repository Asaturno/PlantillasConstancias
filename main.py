import tkinter as tk
from database.db_setup import crear_base_de_datos
from ui.main_window import MainWindow

def main():
    crear_base_de_datos()

     # Crea la ventana principal
    root = tk.Tk()
    root.title("Sistema de Constancias")
    root.geometry("400x300")
    app = MainWindow(master=root)
    app.mainloop()

if __name__ == "__main__":
    main()
