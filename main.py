# main.py

from PyQt5.QtWidgets import QApplication
from start import MainApp
from app.utils.debug import clean_old_logs, setup_logging, log_message, log_event_and_function
import sys

if __name__ == "__main__":
    # Usar try/except para manejar excepciones globales y asegurarse de que se registren los errores críticos.
    try:
        # Limpiar logs antiguos al iniciar
        clean_old_logs()
        log_message("info", "Logs antiguos limpiados correctamente.")

        # Iniciar el sistema de logging (debug)
        setup_logging()
        log_message("success", "Sistema de logging iniciado correctamente.")

        # Crear una instancia de la aplicación PyQt
        app = QApplication([])

        # Inicializar la interfaz principal
        window = MainApp()

        # Verificación de que la ventana se haya creado correctamente usando assert
        assert window is not None, "La ventana principal no pudo ser inicializada."
        log_message("info", "Ventana principal inicializada correctamente.")

        # Registrar el evento y la función
        log_event_and_function("Aplicación principal", "window.show()")
        window.show()
        log_message("info", "Aplicación principal iniciada correctamente.")

        # Iniciar el bucle de la aplicación
        app.exec_()

    except AssertionError as ae:
        # Registrar errores de aserción (fallos lógicos en el código)
        log_message("critical", f"Error crítico de aserción: {ae}", exc_info=True)
        sys.exit(1)  # Salir de la aplicación con código de error

    except Exception as e:
        # Capturar cualquier otra excepción y registrarla
        log_message("error", f"Se ha producido un error inesperado: {e}", exc_info=True)
        sys.exit(1)  # Salir de la aplicación con código de error

    finally:
        # Finalmente, se ejecuta siempre. Aquí puedes colocar cualquier acción de limpieza si fuera necesario.
        log_message("debug", "Aplicación terminada.")
