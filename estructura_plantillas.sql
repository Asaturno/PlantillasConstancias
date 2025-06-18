CREATE TABLE IF NOT EXISTS docentes (
    id SERIAL PRIMARY KEY,
    grado TEXT NOT NULL,
    nombre TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    nombre TEXT NOT NULL UNIQUE,
    contrasena TEXT NOT NULL,
    es_superusuario BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS responsables (
    id SERIAL PRIMARY KEY,
    grado TEXT NOT NULL,
    nombre TEXT NOT NULL,
    rol TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS eventos (
    id SERIAL PRIMARY KEY,
    nombre TEXT NOT NULL,
    fecha DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS constancias (
    id SERIAL PRIMARY KEY,
    tipo TEXT NOT NULL,
    fecha_elaboracion DATE NOT NULL,
    id_evento INTEGER REFERENCES eventos(id),
    id_responsable INTEGER REFERENCES responsables(id),
    docentes TEXT,
    rol_docente TEXT,
    html TEXT
);

CREATE EXTENSION IF NOT EXISTS pgcrypto;

INSERT INTO usuarios (nombre, contrasena, es_superusuario)
SELECT 'admin', encode(digest('admin123', 'sha256'), 'hex'), TRUE
WHERE NOT EXISTS (
    SELECT 1 FROM usuarios WHERE es_superusuario = TRUE
);
