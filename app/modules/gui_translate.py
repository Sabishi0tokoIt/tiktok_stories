# app/modules/gui_translate.py

from PyQt5.QtWidgets import (
    QWidget,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit
)
from ..modules.messages import show_status_message
from ..utils.utils import create_text_entry_with_context_menu
from ..utils.debug import log_message

class TranslateControl(QWidget):

    def __init__(self, parent=None):
        super(TranslateControl, self).__init__(parent)
        self.layout_principal = None
        self.parent = parent  # Almacenar una referencia al padre (la ventana principal)

        # Iniciar el ui
        self.init_ui()

    def init_ui(self):
        """ Inicializar controles de traducción y agregar los elementos al layout principal de la ventana padre. """
        log_message("info", "Inicializando la interfaz de usuario para traducción.")

        # Crear el Layout principal
        self.layout_principal = QVBoxLayout(self)

        # Agregar el espacio para la entrada de texto y la traducción
        text_to_translate_widget = self.text_to_translate_widget()
        self.layout_principal.addWidget(text_to_translate_widget)

        # Agregar el espacio para el título de entrada y la traducción
        title_widget = self.title_widget()
        title_widget.setFixedHeight(60)
        self.layout_principal.addWidget(title_widget)

        # Agregar el botón de traduccións
        translate_control_button = self.translate_control_button()
        self.layout_principal.addWidget(translate_control_button)
        log_message("info", "Controles de traducción inicializados.")

    def create_text_entry_widget(self):
        """ Crea un campo de entrada de texto """
        self.text_entry = create_text_entry_with_context_menu(self)
        self.text_entry.setPlaceholderText("Ingrese el texto a traducir...")
        self.text_entry.setAcceptRichText(False)
        log_message("info", "Campo de entrada de texto creado.")
        return self.text_entry

    def create_translation_widget(self):
        """ Crea un campo para mostrar el texto traducido """
        self.translation_label = QTextEdit(self)
        self.translation_label.setReadOnly(True)
        log_message("info", "Campo de traducción creado.")
        return self.translation_label

    def text_to_translate_widget(self):
        """ Crea un widget que contiene el campo de entrada del texto y el campo de traducción """
        # Crear un layout horizontal
        text_translate_layout = QHBoxLayout()

        # Crear el campo de entrada del texto
        text_to_translate = self.create_text_entry_widget()
        text_translate_layout.addWidget(text_to_translate)

        # Crear el campo de traducción del texto
        text_translation_layout = self.create_translation_widget()
        text_translate_layout.addWidget(text_translation_layout)

        # Crear un widget contenedor y añadir el layout
        text_translate_widget = QWidget()
        text_translate_widget.setLayout(text_translate_layout)

        return text_translate_widget

    def create_title_entry_widget(self):
        """ Crea un campo de entrada para el título """
        self.title_entry = create_text_entry_with_context_menu(self)
        self.title_entry.setPlaceholderText("Ingrese el título...")
        self.title_entry.setAcceptRichText(False)
        log_message("info", "Campo de título creado.")
        return self.title_entry

    def create_translation_title_widget(self):
        """ Crea un campo para mostrar el título traducido """
        self.translation_title_label = QTextEdit(self)
        self.translation_title_label.setReadOnly(True)
        log_message("info", "Campo de traducción del título creado.")
        return self.translation_title_label

    def title_widget(self):
        """ Crea un widget que contiene el campo de entrada del título y el campo de traducción del título """
        # Crear el layout horizontal
        title_layout = QHBoxLayout()

        # Crear el campo de entrada del título
        title_entry = self.create_title_entry_widget()
        title_layout.addWidget(title_entry)

        # Crear el campo de traducción del título
        translation_title = self.create_translation_title_widget()
        title_layout.addWidget(translation_title)

        # Crear un widget contenedor y añadir el layout
        title_widget = QWidget()
        title_widget.setLayout(title_layout)

        log_message("info", "Widget de título creado con entrada y traducción.")
        return title_widget

    def translate_control_button(self):
        translate_controls_widget = QWidget(self)
        self.translate_button_layout = QHBoxLayout(translate_controls_widget)

        # Crear el botón de verificación de título
        self.verify_title_button = QPushButton("Verificar título")
        self.verify_title_button.clicked.connect(self.verify_title)
        self.translate_button_layout.addWidget(self.verify_title_button)

        # Crear el botón de traducción
        self.translate_button = QPushButton("Traducir")
        self.translate_button.clicked.connect(self.translate_text)
        self.translate_button.setEnabled(False)
        self.translate_button_layout.addWidget(self.translate_button)

        # Crear el botón de traducción

        self.validate_button = QPushButton("Validar Traducción")
        self.validate_button.clicked.connect(self.write_file_configuration)
        self.validate_button.clicked.connect(self.title_save)
        self.validate_button.setEnabled(False)
        self.translate_button_layout.addWidget(self.validate_button)

        log_message("info", "Botón de traducción creado.")
        return translate_controls_widget

    def verify_title(self):
        from app.extra.used_titles import TITLES
        """Verifica si el título ya existe y activa/desactiva los botones."""
        # Obtener el título ingresado por el usuario
        input_title = self.title_entry.toPlainText().strip()

        if not input_title:  # Si el campo está vacío, desactiva los botones
            show_status_message("Por favor, ingresa un título.", "warning")
            return

        # Verificar si el título ya existe
        if input_title in TITLES:
            show_status_message("El título ya existe.", "warning")
        else:
            # Si no existe, activa los botones
            self.translate_button.setEnabled(True)
            show_status_message("Título válido. Puedes traducir.", "success")

    def translate_text(self):
        from app.modules.translate.translate_text import translate_text_with_model
        from app.modules.translate.detect_language import detect_language

        # Limpiar los campos de traducción si no están vacíos
        if self.translation_title_label.toPlainText().strip() or self.translation_label.toPlainText().strip():
            self.translation_title_label.clear()
            self.translation_label.clear()

        # Realizar la traducción del texto y el título ingresados en el campo.
        input_text = self.text_entry.toPlainText()
        input_title = self.title_entry.toPlainText()

        if not input_text.strip() or not input_title.strip():
            show_status_message("Se necesitan los dos campos llenos. Por favor, ingresa un título y texto para traducir.", "error")
            log_message("warning", "Intento de traducción sin texto o título ingresado.")
            return

        try:
            log_message("debug", "Iniciando detección del idioma...")
            # Detectar el idioma del texto ingresado
            detected_language = detect_language(input_text)
            detected_language_title = detect_language(input_title)

            log_message("debug", f"Idioma detectado: {detected_language}, {detected_language_title}")

            if not detected_language or not detected_language_title:  # Corregido

                show_status_message("No se pudo detectar el idioma", "error")
                log_message("warning", "No se pudo detectar el idioma del texto o título.")
                return

            log_message("debug", f"Iniciando traducción del título: {input_title}")
            log_message("debug", f"Iniciando traducción del texto: {input_text}")

            # Realiza la traducción usando el modelo personalizado
            translated_text = translate_text_with_model(
                text=input_text,
                target_language='es',
                source_language=detected_language
            )
            translated_title = translate_text_with_model(  # Traducción del título
                text=input_title,
                target_language='es',
                source_language=detected_language_title
            )

            # Mostrar la traducción en la etiqueta de resultado
            if translated_text and translated_title:  # Comprobar ambos resultados

                # Activar el botón 'Validar'
                self.validate_button.setEnabled(True)

                self.translation_label.setText(translated_text)  # Actualiza el QTextEdit con la traducción
                self.translation_title_label.setText(translated_title)  # Actualiza el QTextEdit del título
                show_status_message("Texto traducido", "success")
                log_message("debug", f"Traducción exitosa: {translated_text}")
                log_message("debug", f"Traducción exitosa del título: {translated_title}")
            else:
                show_status_message("Error en la traducción", "error")
                log_message("warning", "Traducción fallida: texto traducido o título es None")

        except Exception as e:
            show_status_message(f"Error al traducir: {e}", "error")
            log_message("error", f"Error durante la traducción: {e}")

    def write_file_configuration(self):
        """ Lógica para guardar los archivos de traducción """

        try:
            # Intentar realizar la importación
            from .translate.write_file_configuration import write_file_configuration
            show_status_message("Validando la configuración", "info")
            log_message("info", "Módulo write_file_configuration importado correctamente.")

            try:
                # Obtener el texto y título de los campos correspondientes
                input_text = self.translation_label.toPlainText().strip()
                input_title = self.translation_title_label.toPlainText().strip()

                # Llamada al método para escribir la configuración
                write_file_configuration(input_text, input_title)
                log_message("success", "Configuración de archivo escrita exitosamente.")

                # Reactivar el botón continuar
                self.parent.enable_continue_button()

            except Exception as e:
                log_message("error", f"Error al escribir la configuración de archivo: {e}", exc_info=True)
                show_status_message("Error al escribir la configuración de archivo.", "error")

        except ImportError as e:
            # Manejar el error de importación
            log_message("error", f"Error al importar write_file_configuration: {e}")
            show_status_message("No se pudo importar el módulo write_file_configuration.", "error")

    def title_save(self):
        from ..modules.translate.title_save import add_title_to_library
        """Función para manejar la acción de guardar el título ingresado"""
        log_message("info", "Agregando título al diccionario")
        try:
            # Obtener el texto del título ingresado
            input_title = self.title_entry.toPlainText().strip()

            if not input_title:
                log_message("warning", "Título vacío, no se puede agregar.")
                return

            # Llamada a la función que guarda el título en la biblioteca
            add_title_to_library(input_title)
            log_message("success", "Título agregado correctamente.")
        except Exception as e:
            log_message("error", f"Error al agregar el título: {e}")