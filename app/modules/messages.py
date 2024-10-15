# app/modules/messages.py

from PyQt5.QtCore import Qt
from ..utils.debug import log_message
from ..utils.singleton_status import StatusManager


def show_status_message(message: str, msg_type: str) -> None:
    """
    Muestra un mensaje de estado en la interfaz de usuario.
    :param message: El mensaje a mostrar.
    :param msg_type: El tipo de mensaje ('error', 'success', 'warning', 'info', u otro).
    """
    status_label = StatusManager.get_instance().get_status_label()
    if not status_label:
        log_message("error", "status_label no está inicializado.")
        return

    try:
        # Limpiar el mensaje anterior
        status_label.setText("")  # Limpia el mensaje previo

        # Manejar los diferentes tipos de mensaje
        styles = {
            "error": ("background-color: red; color: white; font-weight: bold;", "error"),
            "success": ("background-color: green; color: white; font-weight: bold;", "info"),
            "warning": ("background-color: orange; color: white; font-weight: bold;", "warning"),
            "info": ("background-color: blue; color: white; font-weight: bold;", "info"),
        }

        style, log_level = styles.get(msg_type, ("background-color: white; color: black;", "debug"))
        status_label.setStyleSheet(style)
        log_message(log_level, message)

        # Establecer el texto del mensaje
        status_label.setText(message)
        status_label.setAlignment(Qt.AlignCenter)

    except AssertionError as e:
        log_message("error", f"Error de aserción: {e}", exc_info=True)

    except Exception as e:
        log_message("error", f"Error inesperado al mostrar el mensaje de estado: {e}", exc_info=True)
