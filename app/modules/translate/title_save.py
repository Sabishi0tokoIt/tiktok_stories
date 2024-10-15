# app/modules/translate/title_save.py

import os
from app.extra.used_titles import TITLES
from ...utils.directories import get_extra_dir
from ...utils.debug import log_message


def add_title_to_library(title):
    """Agregar un título al diccionario de títulos y guardarlo en el archivo"""

    # Evitar duplicados
    if title not in TITLES:
        TITLES.append(title)

        extra_dir = get_extra_dir()  # Obtener el directorio donde se encuentra 'used_titles.py'
        file_path = extra_dir / "used_titles.py"

        # Verificar permisos de escritura
        if not os.access(file_path, os.W_OK):
            log_message("error", f"El archivo {file_path} no tiene permisos de escritura.")
            return

        # Leer el contenido actual del archivo
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Encontrar la línea que define TITLES y agregar el nuevo título
        for i, line in enumerate(lines):
            if line.strip().startswith("TITLES = ["):
                # Crear la nueva línea para agregar el título
                new_title_line = f'        "{title}",\n'
                # Insertar el nuevo título después de la línea actual
                lines.insert(i + 1, new_title_line)
                break
        else:
            log_message("error", "No se encontró la definición de TITLES en el archivo.")
            return

        # Escribir el contenido modificado de nuevo en el archivo
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(lines)

        log_message("success", f"Título '{title}' agregado y guardado correctamente.")
    else:
        log_message("info", f"El título '{title}' ya existe en el diccionario.")


