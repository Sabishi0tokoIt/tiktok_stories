# app/config/lang.py

import os
from app.utils.debug import log_message
from app.utils.directories import get_lang_dir, get_data_dir


class Language:
    def __init__(self, lang):
        self.lang = lang

    def get_lang(self):
        # Ruta del directorio de idiomas
        lang_path = get_lang_dir()

        # Comprobar si el directorio existe
        if not os.path.exists(lang_path):
            log_message("error", f"El directorio de idiomas no se encontró en la ruta {lang_path}")
            raise FileNotFoundError(f"El directorio de idiomas no se encontró en la ruta {lang_path}")

        try:
            # Obtener la lista de elementos en el directorio de idiomas
            elementos = os.listdir(lang_path)

            # Filtrar solo los archivos .py, excluyendo aquellos que contienen __ en ambos extremos
            files_py = [
                archivo[:-3] for archivo in elementos  # Quitamos el ".py" del nombre
                if archivo.endswith('.py') and
                   not archivo.startswith('__') and
                   not ('__' in archivo and archivo.endswith('.py'))
            ]

            log_message("debug", f"Archivos de idioma encontrados: {files_py}")
            return files_py

        except PermissionError:
            log_message("error", f"No tienes permiso para acceder al directorio '{lang_path}'.")
            return []  # Devuelve una lista vacía en caso de error de permisos
        except Exception as e:
            log_message("error", f"Error inesperado al acceder al directorio de idiomas: {e}", exc_info=True)
            return []  # Devuelve una lista vacía en caso de error inesperado

def generate_languages_file():
    """Genera un archivo con la lista de idiomas disponibles."""
    lang_instance = Language('lang')
    lang_list = lang_instance.get_lang()

    # Obtener la ruta del directorio 'text2speech/data'
    data_dir = get_data_dir()

    # Ruta del archivo a crear en 'text2speech/data'
    file_path = os.path.join(data_dir, 'languages.py')

    # Asegurarse de que la lista de idiomas no esté vacía
    assert lang_list, "No se encontraron idiomas para escribir en el archivo."

    try:
        with open(file_path, 'w') as file:
            file.write("LANGUAGES = [\n")
            for lang in lang_list:
                file.write(f"    '{lang}',  # Comentario para {lang}\n")
            file.write("]\n\n")

            # Agregar la función languages_get al final del archivo
            file.write("def languages_get():\n")
            file.write("    return LANGUAGES\n")

        log_message("debug", f"Archivo 'languages.py' creado exitosamente en {file_path}")

    except FileNotFoundError:
        log_message("error", f"El directorio para guardar el archivo no se encontró: {file_path}")
    except PermissionError:
        log_message("error", f"No tienes permiso para escribir en el directorio: {data_dir}")
    except Exception as e:
        log_message("error", f"Error al crear el archivo 'languages.py': {e}", exc_info=True)
