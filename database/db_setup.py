import sqlite3
import os
import hashlib

DB_PATH = os.path.join("data", "constancias.db")

def crear_base_de_datos():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        # Tabla de docentes
        cursor.execute(''' 
            CREATE TABLE IF NOT EXISTS docentes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                grado TEXT NOT NULL,
                nombre TEXT NOT NULL
            );
        ''')

        # Tabla de usuarios
        cursor.execute(''' 
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL UNIQUE,
                contrasena TEXT NOT NULL,
                es_superusuario INTEGER DEFAULT 0
            );
        ''')

        # Tabla de responsables
        cursor.execute(''' 
            CREATE TABLE IF NOT EXISTS responsables (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                grado TEXT NOT NULL,
                nombre TEXT NOT NULL,
                rol TEXT NOT NULL
            );
        ''')

        # Tabla de eventos
        cursor.execute(''' 
            CREATE TABLE IF NOT EXISTS eventos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                fecha TEXT NOT NULL
            );
        ''')

        # Tabla de constancias generadas
        cursor.execute(''' 
            CREATE TABLE IF NOT EXISTS constancias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo TEXT NOT NULL,
                fecha_elaboracion TEXT NOT NULL,
                id_evento INTEGER,
                id_responsable INTEGER,
                docentes TEXT,
                rol_docente TEXT,
                html TEXT,
                FOREIGN KEY (id_evento) REFERENCES eventos(id),
                FOREIGN KEY (id_responsable) REFERENCES responsables(id)
            );
        ''')

        # # Tabla intermedia para docentes en constancias
        # cursor.execute(''' 
        #     CREATE TABLE IF NOT EXISTS constancia_docente (
        #         id INTEGER PRIMARY KEY AUTOINCREMENT,
        #         id_constancia INTEGER,
        #         id_docente INTEGER,
        #         rol_en_evento TEXT NOT NULL,
        #         FOREIGN KEY (id_constancia) REFERENCES constancias(id),
        #         FOREIGN KEY (id_docente) REFERENCES docentes(id)
        #     );
        # # ''')

        # # Tabla de historial de constancias
        # cursor.execute(''' 
        #     CREATE TABLE IF NOT EXISTS historial_constancias (
        #         id INTEGER PRIMARY KEY AUTOINCREMENT,
        #         contenido TEXT NOT NULL,
        #         fecha_emision TEXT NOT NULL
        #     );
        # ''')

        # Crear superusuario inicial si no existe
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE es_superusuario = 1")
        if cursor.fetchone()[0] == 0:
            contrasena_hash = hashlib.sha256("admin123".encode()).hexdigest()
            cursor.execute(
                "INSERT INTO usuarios (nombre, contrasena, es_superusuario) VALUES (?, ?, 1)",
                ("admin", contrasena_hash)
            )

        conn.commit()
        print("Base de datos creada correctamente.")

if __name__ == "__main__":
    crear_base_de_datos()
