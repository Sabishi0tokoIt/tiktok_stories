# app/modules/gui_audio.py
from PyQt5.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QComboBox,
    QLabel,
    QSlider,
    QFileDialog,
)
from PyQt5.QtCore import Qt

from data.languages import languages_get
from app.modules.audio.languages_update import LanguagesUpdater
from app.config.credentials import GoogleCloudAPIManager
from app.modules.messages import show_status_message
from app.utils.utils import save_file
from app.utils.debug import log_message

class AudioControls(QWidget):
    def __init__(self, parent=None):
        super(AudioControls, self).__init__(parent)
        self.parent = parent  # Almacenar una referencia al padre (la ventana principal)


        # Instanciar la clase de configuración de credenciales OAuth
        try:
            self.oauth_config = GoogleCloudAPIManager()
            log_message("debug", "Instancia de GoogleCloudAPIManager obtenida.")

            # Verificar si las credenciales están disponibles
            if not self.oauth_config.creds:
                log_message("error", "Error: No se pudo obtener credenciales.")
                assert False, "Credenciales no disponibles"  # Lanza una excepción si no hay credenciales
            log_message("info", "Credenciales obtenidas correctamente.")

        except Exception as e:
            log_message("critical", f"Error crítico al inicializar la configuración de OAuth: {e}", exc_info=True)
            return

        # Reutilizar el cliente de Text-to-Speech
        try:
            self.client = self.oauth_config.get_client('texttospeech')
            if self.client:
                log_message("success", "Cliente de Google Cloud Text-to-Speech reutilizado exitosamente.")
            else:
                log_message("error", "Error: No se pudo obtener el cliente de Google Cloud Text-to-Speech.")

        except Exception as e:
            log_message("error", f"Error al obtener el cliente de Google Cloud Text-to-Speech: {e}", exc_info=True)

        # Obtener los idiomas disponibles
        try:
            self.idiomas = languages_get()
            log_message("debug", f"Idiomas obtenidos: {self.idiomas}")
        except Exception as e:
            log_message("error", f"Error al obtener los idiomas: {e}", exc_info=True)

        # Actualizar idiomas
        try:
            self.LanguageUpdater = LanguagesUpdater()
            log_message("success", "Actualizador de idiomas inicializado correctamente.")
        except Exception as e:
            log_message("error", f"Error al inicializar LanguagesUpdater: {e}", exc_info=True)

        self.init_ui()

    def init_ui(self):
        """ Inicializar controles de audio y agregar los elementos al layout principal de la ventana padre. """
        log_message("debug", "Iniciando controles de audio.")
        # Crear el Layout principal
        self.layout_principal = QVBoxLayout(self)
        self.layout_principal.setContentsMargins(18, 18, 18, 10)

        # Agregar editor de etxto
        window_widget = self.window_widget()
        self.layout_principal.addWidget(window_widget)

        # Agregar Menus desplegables de idiomas en un layout
        create_dropbox_menus = self.create_dropdown_menus()
        create_dropbox_menus.setContentsMargins(0, 18, 0, 18)
        self.layout_principal.addLayout(create_dropbox_menus)

        # Agregar controles de velocidad y tono
        action_scale = self.action_scale()
        action_scale.setContentsMargins(0, 0, 0, 18)
        self.layout_principal.addLayout(action_scale)

        # Agregar controles de audio (10%)
        create_audio_buttons = self.create_audio_buttons()
        self.layout_principal.addWidget(create_audio_buttons)

    def window_widget(self):
        from app.utils.utils import create_text_entry_with_context_menu
        from pathlib import Path

        # Crear el widget de entrada de texto
        self.text_entry = create_text_entry_with_context_menu(self)
        log_message("debug", "Se creó el widget de entrada de texto con menú contextual.")

        # Cargar los archivos de texto
        title_path = Path('data/title_translate.txt')
        text_path = Path('data/text_translate.txt')

        try:
            # Cargar el contenido del archivo title_translate.txt
            if title_path.exists():
                with open(title_path, 'r', encoding='utf-8') as title_file:
                    title_content = title_file.read().strip()
            else:
                log_message("warning", "El archivo title_translate.txt no se encontró.")
                title_content = ""

            # Cargar el contenido del archivo text_translate.txt
            if text_path.exists():
                with open(text_path, 'r', encoding='utf-8') as text_file:
                    text_content = text_file.read().strip()
            else:
                log_message("warning", "El archivo text_translate.txt no se encontró.")
                text_content = ""

            # Establecer el contenido en el widget de entrada de texto
            combined_content = f"{title_content}\n{text_content}"
            self.text_entry.setPlainText(combined_content)  # Usa setPlainText si es QTextEdit
            log_message("info", "Contenido de los archivos cargado en el widget de entrada de texto.")

        except Exception as e:
            log_message("error", f"Error al cargar los archivos de texto: {e}", exc_info=True)

        return self.text_entry

    def create_dropdown_menus(self):
        """ Crear los menús desplegables de idiomas, país, género, estilo y voz. """
        self.config_layout = QHBoxLayout()

        # Menú de idiomas
        self.language_menu = QComboBox(self)
        self.language_menu.addItem("Selecciona un idioma")
        self.language_menu.setFixedHeight(25)
        for idioma in self.idiomas:
            self.language_menu.addItem(idioma)
        self.config_layout.addWidget(self.language_menu)

        # Menú de países
        self.country_menu = QComboBox(self)
        self.country_menu.addItem("Selecciona un país")
        self.country_menu.setFixedHeight(25)

        if self.language_menu.currentText() != "Selecciona un idioma":
            for country in self.paises[self.language_menu.currentText()]:
                self.country_menu.addItem(country)
        self.config_layout.addWidget(self.country_menu)

        # Menú de géneros
        self.gender_menu = QComboBox(self)
        self.gender_menu.addItem("Selecciona un género")
        self.gender_menu.setFixedHeight(25)
        self.config_layout.addWidget(self.gender_menu)

        # Menú de estilos
        self.style_menu = QComboBox(self)
        self.style_menu.addItem("Selecciona un estilo")
        self.style_menu.setFixedHeight(25)
        self.config_layout.addWidget(self.style_menu)

        # Menú de voces
        self.voice_menu = QComboBox(self)
        self.voice_menu.addItem("Selecciona una voz")
        self.voice_menu.setFixedHeight(25)
        self.config_layout.addWidget(self.voice_menu)

        # Vincular los widgets al actualizador de idiomas
        self.LanguageUpdater.bind_widgets(
            self.language_menu,
            self.country_menu,
            self.gender_menu,
            self.style_menu,
            self.voice_menu
        )

        log_message("debug", "Widgets vinculados para el actualizador de idiomas.")
        return self.config_layout

    def create_audio_buttons(self):
        """ Crear los botones para validar, convertir, reproducir y guardar audio. """
        log_message("debug", "Creando botones de audio.")

        audio_controls_widget = QWidget(self)
        audio_controls_widget.setContentsMargins(0, 0, 0, 0)
        self.audio_button_layout = QHBoxLayout(audio_controls_widget)
        self.audio_button_layout.setContentsMargins(0, 0, 0, 8)

        # Botones para validar, convertir, reproducir y guardar audio
        self.verify_button = QPushButton("Validar Configuración")
        self.verify_button.clicked.connect(self.write_file_configuration)
        self.audio_button_layout.addWidget(self.verify_button)

        self.convert_button = QPushButton("Convertir a MP3")
        self.convert_button.clicked.connect(self.convert_text)
        self.convert_button.setEnabled(False)  # Deshabilitado por defecto
        self.audio_button_layout.addWidget(self.convert_button)

        self.play_button = QPushButton("Reproducir Audio")
        self.play_button.clicked.connect(self.play_audio)
        self.play_button.setEnabled(False)  # Deshabilitado por defecto
        self.audio_button_layout.addWidget(self.play_button)

        self.stop_button = QPushButton("Detener reproducción")
        self.stop_button.clicked.connect(self.stop_audio)
        self.stop_button.setEnabled(False)
        self.audio_button_layout.addWidget(self.stop_button)

        self.save_button = QPushButton("Guardar Audio")
        self.save_button.clicked.connect(self.save_audio)
        self.save_button.setEnabled(False)  # Deshabilitado por defecto
        self.audio_button_layout.addWidget(self.save_button)

        log_message("debug", "Botones de audio creados y añadidos al layout.")
        return audio_controls_widget

    def action_scale(self):
        """ Crear controles deslizantes para ajustar la velocidad y el tono. """
        log_message("debug", "Creando controles deslizantes para velocidad y tono.")

        adjustment_layout = QHBoxLayout()

        # Layout para la escala de velocidad
        speed_layout = QVBoxLayout()
        self.speed_label = QLabel("Velocidad de Voz: x1.0")
        speed_layout.addWidget(self.speed_label)

        self.speed_scale = QSlider(Qt.Horizontal, self)
        self.speed_scale.setRange(25, 200)  # Mapeamos el rango de 0.25 a 2.0 en valores enteros (25 a 200)
        self.speed_scale.setSingleStep(5)  # Incremento de 0.05
        self.speed_scale.setValue(100)  # Valor predeterminado (x1.0)
        self.speed_scale.valueChanged.connect(self.update_speed_label)  # Conectar la actualización de la etiqueta
        speed_layout.addWidget(self.speed_scale)

        # Layout para la escala de tono
        pitch_layout = QVBoxLayout()
        self.pitch_label = QLabel("Tono de Voz: 0 Hz")
        pitch_layout.addWidget(self.pitch_label)

        self.pitch_scale = QSlider(Qt.Horizontal, self)
        self.pitch_scale.setRange(-500, 500)  # Rango de -500 a 500 Hz
        self.pitch_scale.setSingleStep(10)  # Incremento de 10 Hz
        self.pitch_scale.setValue(0)  # Valor predeterminado (0 Hz)
        self.pitch_scale.valueChanged.connect(self.update_pitch_label)  # Conectar la actualización de la etiqueta
        pitch_layout.addWidget(self.pitch_scale)

        # Añadir los layouts de velocidad y tono al layout horizontal
        adjustment_layout.addLayout(speed_layout)
        adjustment_layout.addLayout(pitch_layout)

        log_message("debug", "Controles deslizantes para velocidad y tono creados.")
        return adjustment_layout

    def update_speed_label(self, value):
        speed = value / 100.0  # Convertir el valor a un valor de 0.25 a 2.0
        self.speed_label.setText(f"Velocidad de Voz: x{speed:.2f}")
        log_message("debug", "Velocidad de voz actualizada: x%.2f", speed)

    def update_pitch_label(self, value):
        self.pitch_label.setText(f"Tono de Voz: {value} Hz")
        log_message("debug", "Tono de voz actualizado: %d Hz", value)

    def write_file_configuration(self):
        from app.modules.audio.write_file_configuration import write_file_configuration

        log_message("debug", "Escribiendo configuración de archivo.")
        try:
            # Llamada al método para escribir la configuración
            write_file_configuration(self)
            log_message("success", "Configuración de archivo escrita exitosamente.")
        except Exception as e:
            log_message("error", "Error al escribir la configuración de archivo: %s", e, exc_info=True)
            show_status_message("Error al escribir la configuración de archivo.", "error")

    def convert_text(self):
        from .audio.convert_text import convert_text
        from app.utils.singleton_status import StatusManager

        StatusManager.get_instance().get_status_label().setText("")

        log_message("debug", "Convirtiendo texto.")
        try:
            convert_text(self)
            log_message("success", "Texto convertido exitosamente.")
            self.play_button.setEnabled(True)
            self.stop_button.setEnabled(True)
            self.save_button.setEnabled(True)
            # Reactivar el botón continuar
            self.parent.enable_continue_button()
        except Exception as e:
            log_message("error", "Error al convertir texto: %s", e, exc_info=True)
            show_status_message("Error al convertir el texto.")

    def play_audio(self):
        from app.utils.media_control import MediaPlayer
        """Reproduce el archivo de audio temporal generado."""
        try:
            MediaPlayer().play(is_audio=True)
            log_message("success", "Audio reproducido exitosamente.")
            self.play_button.setEnabled(False)  # Deshabilitar el botón de reproducir
            self.stop_button.setEnabled(True)  # Habilitar el botón de detener
        except Exception as e:
            log_message("error", f"Error al reproducir audio: {e}", exc_info=True)
            show_status_message(f"Error al reproducir el archivo de audio: {e}", "error")

    def stop_audio(self):
        from ..utils.media_control import MediaPlayer
        """Detiene la reproducción del archivo de audio temporal."""
        try:
            MediaPlayer().stop()
            log_message("success", "Audio detenido exitosamente.")
            self.play_button.setEnabled(True)  # Habilitar el botón de reproducir
            self.stop_button.setEnabled(False)  # Deshabilitar el botón de detener
        except Exception as e:
            log_message("error", f"Error al detener el audio en reproducción.", exc_info=True)
            show_status_message("Error al detener el audio en reproducción.", "error")

    def save_audio(self):
        log_message("debug", "Guardando audio.")
        try:
            filename, _ = QFileDialog.getSaveFileName(self, "Guardar Audio", "", "Archivos de Audio (*.mp3)")
            if filename:
                save_file(filename, self.audio_data)
                log_message("success", "Audio guardado exitosamente en: %s", filename)
            else:
                log_message("warning", "Guardar audio cancelado por el usuario.")
        except Exception as e:
            log_message("error", "Error al guardar audio: %s", e, exc_info=True)
            show_status_message("Error al guardar el audio.")
