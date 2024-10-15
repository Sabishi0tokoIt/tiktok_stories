# app/utils/debug.py

import logging
import os
import traceback
import functools

from logging.handlers import RotatingFileHandler
from datetime import datetime
from pathlib import Path
from app.utils.directories import get_project_root

# Variable general para logs de eventos
event_log = set()

# Definir un nuevo nivel de logging para éxito
SUCCESS_LEVEL = 25
logging.addLevelName(SUCCESS_LEVEL, "SUCCESS")

def get_debug_dir() -> Path:
    project_root = get_project_root()
    debug_dir = project_root / 'DEBUG'
    debug_dir.mkdir(parents=True, exist_ok=True)
    return debug_dir

def get_debug_success_dir() -> Path:
    debug_dir = get_debug_dir()
    debug_success_dir = debug_dir / 'success'
    debug_success_dir.mkdir(parents=True, exist_ok=True)
    return debug_success_dir

def get_debug_warning_dir() -> Path:
    debug_dir = get_debug_dir()
    debug_warning_dir = debug_dir / 'warning'
    debug_warning_dir.mkdir(parents=True, exist_ok=True)
    return debug_warning_dir

def get_debug_error_dir() -> Path:
    debug_dir = get_debug_dir()
    debug_error_dir = debug_dir / 'error'
    debug_error_dir.mkdir(parents=True, exist_ok=True)
    return debug_error_dir

def get_debug_debug_dir() -> Path:
    debug_dir = get_debug_dir()
    debug_debug_dir = debug_dir / 'debug'
    debug_debug_dir.mkdir(parents=True, exist_ok=True)
    return debug_debug_dir

def get_debug_critical_dir() -> Path:
    debug_dir = get_debug_dir()
    debug_critical_dir = debug_dir / 'critical'
    debug_critical_dir.mkdir(parents=True, exist_ok=True)
    return debug_critical_dir

def get_debug_info_dir() -> Path:
    debug_dir = get_debug_dir()
    debug_info_dir = debug_dir / 'critical'
    debug_info_dir.mkdir(parents=True, exist_ok=True)
    return debug_info_dir

# Configurar logging

class LevelFilter(logging.Filter):
    """
    Filtro personalizado para permitir que un manejador registre solo los eventos de un nivel específico.
    """

    def __init__(self, level):
        self.level = level

    def filter(self, record):
        # Solo permitir que los registros con el nivel coincidente pasen
        return record.levelno == self.level

def setup_logging():
    """
    Configura el logging para separar los logs por nivel de severidad.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Crear un diccionario de handlers con sus niveles
    handlers = {
        "info": (get_debug_info_dir(), logging.INFO),
        "success": (get_debug_success_dir(), SUCCESS_LEVEL),
        "warning": (get_debug_warning_dir(), logging.WARNING),
        "error": (get_debug_error_dir(), logging.ERROR),
        "debug": (get_debug_debug_dir(), logging.DEBUG),
        "critical": (get_debug_critical_dir(), logging.CRITICAL),
    }

    # Eliminar todos los manejadores previos del logger raíz
    root_logger = logging.getLogger()
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    # Configurar manejadores para cada nivel
    for level_name, (log_dir, log_level) in handlers.items():
        log_file = os.path.join(log_dir, f"{level_name}-{timestamp}.log")
        file_handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=5)
        file_handler.setLevel(logging.DEBUG)  # Acepta todos los niveles, pero se filtra
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'))

        # Aplicar filtro para que solo registre eventos de su nivel específico
        file_handler.addFilter(LevelFilter(log_level))

        # Agregar manejador al logger raíz
        root_logger.addHandler(file_handler)

    # Establecer el nivel de logging más bajo para el logger raíz
    root_logger.setLevel(logging.DEBUG)

    logging.debug("Logging configurado correctamente. Archivos de log creados para cada nivel.")

# Función para registrar mensajes de log
def log_message(level: str, message: str, filename: str = None, lineno: int = None, exc_info: bool = False):
    levels = {
        "info": logging.INFO,
        "success": SUCCESS_LEVEL,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "debug": logging.DEBUG,
        "critical": logging.CRITICAL
    }

    # Obtener el nivel de logging, por defecto DEBUG si no es reconocido
    log_level = levels.get(level.lower(), logging.DEBUG)

    # Si no se proporcionan el nombre del archivo y el número de línea, usar inspección
    if filename is None or lineno is None:
        import inspect
        frame = inspect.currentframe().f_back
        filename = frame.f_code.co_filename
        lineno = frame.f_lineno

    # Crear el mensaje con detalles adicionales
    extra_message = f" - {filename}:{lineno}"

    # Si exc_info es True, añadimos el traceback completo de error
    if exc_info:
        message += "\n" + traceback.format_exc()

    # Registrar el mensaje
    logging.log(log_level, f"{message}{extra_message}")

# Decorador para evitar eventos repetidos y registrar función

def log_event_and_function(event=None, function_name=None):
    """Log eventos de funciones, utilizando el sistema de logging definido."""
    if function_name is not None:
        # Usado como función con dos parámetros
        try:
            # Usar función_name para asegurar que el evento sea único por función
            unique_event = f"{event}_{function_name}"
            if unique_event not in event_log:
                log_message("info", f"Evento: {event}, Función: {function_name}")
                event_log.add(unique_event)
            else:
                log_message("warning", f"Evento ya registrado: {unique_event}")
        except Exception as e:
            log_message("error", f"Error al registrar evento: {event} en función: {function_name}. Detalles: {str(e)}",
                        exc_info=True)

    else:
        # Usado como decorador
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    unique_event = f"{event}_{func.__name__}"  # Combinar evento y nombre de función
                    if unique_event not in event_log:
                        log_message("info", f"Evento: {event}, Ejecutando función: {func.__name__}")
                        event_log.add(unique_event)
                    else:
                        log_message("warning", f"Evento ya registrado: {unique_event}")

                    # Ejecutar la función original
                    result = func(*args, **kwargs)

                    log_message("debug", f"Resultado de la función {func.__name__}: {result}")
                    return result
                except Exception as e:
                    log_message("error", f"Error al ejecutar la función: {func.__name__}. Detalles: {str(e)}",
                                exc_info=True)
                    raise

            return wrapper

        return decorator

def clean_old_logs(max_logs=2):
    """
    Elimina los logs más antiguos en cada directorio de logging
    si se excede el número máximo de archivos permitido.
    """
    # Obtener los directorios de log para cada nivel
    log_directories = [
        get_debug_debug_dir(),
        get_debug_critical_dir(),
        get_debug_error_dir(),
        get_debug_success_dir(),
        get_debug_warning_dir()
    ]

    # Iterar sobre cada directorio de logs
    for log_dir in log_directories:
        log_files = sorted(log_dir.glob("*.log"), key=os.path.getmtime)

        # Mientras haya más archivos que el límite permitido, elimina los más antiguos
        while len(log_files) > max_logs:
            log_files[0].unlink()  # Elimina el archivo de log más antiguo
            log_files.pop(0)       # Remueve el archivo de la lista

    logging.info(f"Se ha completado la limpieza de logs, manteniendo un máximo de {max_logs} por directorio.")
