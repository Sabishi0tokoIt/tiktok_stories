# app/modules/translate/write_file_configuration.py

from ...utils.debug import log_message
from ...utils.utils import write
from ..messages import show_status_message


def write_file_configuration(text, title):
    """ Guarda la traducción y el título en archivos. """
    show_status_message("Almacenando la traducción para el siguiente paso", "info")
    try:
        if not text:
            show_status_message("Aún no se ha realizado la traducción.", "error")
            log_message('warning', "Aún no se ha realizado la traducción.")
            return

        # Mostrar la configuración de voz en un cuadro de diálogo
        show_status_message("Traducción validada", "success")
        log_message('success', "Traducción validada.")

        # Guardar los textos en archivos usando la función 'write'
        write('text_translate.txt', text)
        write('title_translate.txt', title)

        show_status_message("Traducción almacenada para el siguiente paso.", "success")
        log_message('info', "Traducción almacenada para el siguiente paso.")

    except Exception as e:
        show_status_message("Error al guardar los archivos", "error")
        log_message('error', f"Error al guardar los archivos: {e}", exc_info=True)