# app/utils/utils.py

import shutil
import re
from pathlib import Path

from PyQt5.QtWidgets import QTextEdit, QMenu, QSizePolicy, QFileDialog, QMessageBox, QApplication
from PyQt5.QtCore import Qt

from .debug import log_message
from .directories import get_data_dir, get_tmp_dir, get_projects_dir

class CustomTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)

    def paste(self):
        # Obtener el texto del portapapeles
        clipboard = QApplication.clipboard().text()  # Usa QApplication para acceder al portapapeles
        # Limpiar el texto
        cleaned_text = self.clean_text(clipboard)
        # Insertar el texto limpio en el widget
        self.insertPlainText(cleaned_text)

    def clean_text(self, text):
        # Realiza la limpieza del texto aquí

        text = re.sub(r'\n+', '\n\n', text)  # Reemplaza múltiples saltos de línea con uno doble
        text = re.sub(r'\s*\n\s*', ' ', text)  # Elimina espacios antes y después de los saltos de línea
        text = re.sub(r'(?<=[.!?])\n+', '\n\n', text)  # Agrega doble salto de línea después de un punto seguido de salto de línea
        text = re.sub(r' {2,}', ' ', text)  # Reemplaza múltiples espacios por uno solo
        return text

def create_text_entry_with_context_menu(parent):
    """
    Crea un widget QTextEdit con un menú contextual para cortar, copiar, pegar y seleccionar todo.

    Args:
    - parent: El widget padre.

    Returns:
    - QTextEdit: El campo de texto con el menú contextual.
    """
    # Crear el campo de texto personalizado con scrollbar
    text_entry = CustomTextEdit(parent)  # Usar la clase personalizada
    text_entry.setWordWrapMode(True)  # Habilitar ajuste de texto

    # Permitir que el QTextEdit se expanda dinámicamente
    text_entry.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    # Crear el menú contextual y configurarlo
    context_menu = QMenu(parent)
    actions = {
        "Cortar": text_entry.cut,
        "Copiar": text_entry.copy,
        "Pegar": text_entry.paste,  # Aquí se llama a la nueva función paste de CustomTextEdit
        "Seleccionar todo": text_entry.selectAll
    }

    for name, slot in actions.items():
        context_menu.addAction(name, slot)

    # Asignar el menú contextual al campo de texto
    text_entry.setContextMenuPolicy(Qt.CustomContextMenu)
    text_entry.customContextMenuRequested.connect(
        lambda position: context_menu.exec_(text_entry.mapToGlobal(position))
    )

    return text_entry


'''def create_text_entry_with_context_menu(parent):
    """
    Crea un widget QTextEdit con un menú contextual para cortar, copiar, pegar y seleccionar todo.

    Args:
    - parent: El widget padre.

    Returns:
    - QTextEdit: El campo de texto con el menú contextual.
    """
    # Crear el campo de texto con scrollbar (QTextEdit ya incluye un scrollbar por defecto)
    text_entry = QTextEdit(parent)
    text_entry.setWordWrapMode(True)  # Habilitar ajuste de texto

    # Permitir que el QTextEdit se expanda dinámicamente
    text_entry.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    # Crear el menú contextual y configurarlo
    context_menu = QMenu(parent)
    actions = {
        "Cortar": text_entry.cut,
        "Copiar": text_entry.copy,
        "Pegar": text_entry.paste,
        "Seleccionar todo": text_entry.selectAll
    }
    for name, slot in actions.items():
        context_menu.addAction(name, slot)

    # Asignar el menú contextual al campo de texto
    text_entry.setContextMenuPolicy(Qt.CustomContextMenu)
    text_entry.customContextMenuRequested.connect(
        lambda position: context_menu.exec_(text_entry.mapToGlobal(position))
    )

    return text_entry'''

def save_file(file_type: str):
    """
    Función genérica para guardar un archivo en una ubicación seleccionada por el usuario.

    Args:
    - file_type (str): El tipo de archivo a guardar ('audio', 'translate', 'video').

    Returns:
    - str: Mensaje de éxito si el archivo se guarda correctamente.
    """

    # Obtener la ruta del directorio temporal
    temp_dir = get_tmp_dir()

    # Seleccionar el archivo temporal según el tipo
    if file_type == 'audio':
        temp_file_name = temp_dir / 'final_temp_audio.mp3'
        default_extension = ".mp3"
        file_types = [("MP3 files", "*.mp3")]
    elif file_type == 'translate':
        temp_file_name = temp_dir / 'translate.txt'
        default_extension = ".txt"
        file_types = [("Text files", "*.txt")]
    elif file_type == 'video':
        temp_file_name = temp_dir / 'final_video.mp4'
        default_extension = ".mp4"
        file_types = [("MP4 files", "*.mp4")]
    else:
        raise ValueError("Tipo de archivo no válido. Debe ser 'audio', 'translate' o 'video'.")

    # Verificar si el archivo temporal existe
    if not temp_file_name.exists():
        raise Exception(f"No hay ningún archivo temporal '{temp_file_name}' para guardar.")

    # Obtener el directorio de destino para guardar (Proyectos/)
    dest_dir = get_projects_dir()

    # Mostrar el diálogo para seleccionar la ubicación de guardado
    file_path, _ = QFileDialog.getSaveFileName(
        None,
        "Guardar archivo",
        str(dest_dir / f"archivo_guardado{default_extension}"),  # Usar extensión por defecto
        f"Todos los archivos (*.*);;{file_types[0][0]} {file_types[0][1]}",
        default_extension
    )

    if file_path:
        try:
            shutil.copy(temp_file_name, file_path)
            QMessageBox.information(None, "Guardado", f"Archivo guardado en {file_path}")
            return f"Archivo guardado en {file_path}"
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error al guardar el archivo: {e}")
            raise e
    return None

def write(file_name, data):
    """
    Guarda datos en un archivo en el directorio 'data/' y registra el proceso.
    """
    try:
        data_dir = get_data_dir()
        file_path = Path(data_dir) / file_name

        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(data)

        log_message('info', f"Archivo '{file_name}' creado/actualizado exitosamente en {file_path}")

    except Exception as e:
        log_message('error', f"Error al guardar el archivo '{file_name}': {e}", exc_info=True)