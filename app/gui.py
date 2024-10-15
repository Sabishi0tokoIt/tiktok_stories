# app/gui.py

import sys
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
)
from PyQt5.QtCore import Qt

from .modules.gui_translate import TranslateControl
from .utils.debug import log_message
from .utils.style_sheet import (
    dark_theme,
    light_theme,
    elegant_dark_blue_theme,
    minimalist_white_blue_theme,
    neon_green_dark_theme, retro_orange_theme,
)


class TikTokStoriesApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Configuración de Idioma")
        self.setGeometry(100, 100, 1000, 800)
        self.setMinimumSize(1000, 800)

        # Aplicar tema oscuro a la ventana principal
        self.setStyleSheet(dark_theme())

        # Inicializar current_step
        self.current_step = 0


        # Configurar interfaz gráfica
        try:
            self.init_ui()
            log_message("success", "Interfaz gráfica configurada correctamente.")
        except Exception as e:
            log_message("error", f"Error al configurar la interfaz gráfica: {e}", exc_info=True)

    def init_ui(self):
        """ Inicializa la interfaz de usuario. """
        # Crear un widget central
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)


        # Crear layout principal para agregar los widgets
        self.layout_principal = QVBoxLayout(central_widget)
        self.layout_principal.setContentsMargins(5, 5, 5, 5)

        # Crear layout superior para agregar los widgets dinámicos
        self.top_layout = QVBoxLayout(self)
        self.layout_principal.addLayout(self.top_layout)

        # Agregar barra de mensaje de estado y botón de continuar
        status_and_continue_button = self.status_and_continue_button()
        self.layout_principal.addWidget(status_and_continue_button)

        # Inicializar TranslateControl
        self.translate_controls = TranslateControl(self)
        self.top_layout.addWidget(self.translate_controls)

    def continue_control_button(self):
        continue_controls_widget = QWidget(self)
        self.continue_button_layout = QHBoxLayout(continue_controls_widget)

        # Crear el botón de continuar
        self.continue_button = QPushButton("Continuar")
        self.continue_button.clicked.connect(self.next_step)
        self.continue_button.setEnabled(True)

        # Agregar el botón de continuar al layout correcto
        self.continue_button_layout.addWidget(self.continue_button)

        return continue_controls_widget

    def enable_continue_button(self):
        """Función para activar el botón 'Continuar' después de completar una acción."""
        self.continue_button.setEnabled(True)
        log_message("info", "Botón 'Continuar' reactivado.")

    def next_step(self):
        """Método que maneja la acción al presionar el botón 'Continuar'."""
        from .modules.gui_audio import AudioControls
        from .modules.gui_video import VideoControls

        try:
            if self.current_step == 0:  # De TranslateControl a AudioControls
                log_message("debug", "Iniciando cambio de TranslateControl a AudioControls.")

                # Ocultar y remover TranslateControl
                self.top_layout.removeWidget(self.translate_controls)
                self.translate_controls.hide()

                # Verificar si ya existen AudioControls
                if not hasattr(self, 'audio_controls'):
                    log_message("debug", "Creando nuevos AudioControls.")
                    self.audio_controls = AudioControls(self)
                    log_message("success", "audio_controls creado: %s", self.audio_controls)
                else:
                    log_message("debug", "AudioControls existentes detectados.")

                # Mostrar AudioControls
                self.top_layout.addWidget(self.audio_controls)
                self.audio_controls.show()

                # Actualizar el paso actual
                self.current_step = 1
                log_message("success", "Cambiado de TranslateControl a AudioControls.")

            elif self.current_step == 1:  # De AudioControls a VideoControls
                log_message("debug", "Iniciando cambio de AudioControls a VideoControls.")

                # Verificar si existen AudioControls y ocultarlos
                if hasattr(self, 'audio_controls'):
                    self.top_layout.removeWidget(self.audio_controls)
                    self.audio_controls.hide()
                    log_message("success", "AudioControls ocultados.")
                else:
                    log_message("warning", "No se encontró audio_controls para ocultar.")

                # Crear y mostrar VideoControls
                if not hasattr(self, 'video_controls'):
                    log_message("debug", "Creando nuevos VideoControls.")
                    self.video_controls = VideoControls(self)
                    log_message("success", "video_controls creado: %s", self.video_controls)
                else:
                    log_message("debug", "VideoControls existentes detectados.")

                self.top_layout.addWidget(self.video_controls)
                self.video_controls.show()

                # Actualizar el paso actual
                self.current_step = 2
                log_message("success", "Cambiado de AudioControls a VideoControls.")

            elif self.current_step == 2:  # De VideoControls a TranslateControl
                log_message("debug", "Iniciando cambio de VideoControls a TranslateControl.")

                # Verificar si existen VideoControls y ocultarlos
                if hasattr(self, 'video_controls'):
                    self.top_layout.removeWidget(self.video_controls)
                    self.video_controls.hide()
                    log_message("success", "VideoControls ocultados.")
                else:
                    log_message("warning", "No se encontró video_controls para ocultar.")

                # Volver a mostrar TranslateControl si fue previamente ocultado
                if not self.translate_controls.isVisible():
                    self.top_layout.addWidget(self.translate_controls)
                    self.translate_controls.show()

                # Actualizar el paso actual
                self.current_step = 0
                log_message("success", "Cambiado de VideoControls a TranslateControl.")

            # Desactivar el botón 'Continuar' una vez completado el cambio
            self.continue_button.setEnabled(True)

        except Exception as e:
            log_message("error", "Error al cambiar de controles: %s", e, exc_info=True)
    '''def next_step(self):
        """Método que maneja la acción al presionar el botón 'Continuar'."""
        from .modules.gui_audio import AudioControls

        try:
            if self.current_step == 0:  # De TranslateControl a AudioControls
                log_message("debug", "Iniciando cambio de TranslateControl a AudioControls.")

                # Ocultar y remover TranslateControl
                self.top_layout.removeWidget(self.translate_controls)
                self.translate_controls.hide()

                # Verificar si ya existen AudioControls
                if not hasattr(self, 'audio_controls'):
                    log_message("debug", "Creando nuevos AudioControls.")
                    self.audio_controls = AudioControls(self)
                    log_message("success", "audio_controls creado: %s", self.audio_controls)
                else:
                    log_message("debug", "AudioControls existentes detectados.")

                # Mostrar AudioControls
                self.top_layout.addWidget(self.audio_controls)
                self.audio_controls.show()

                # Actualizar el paso actual
                self.current_step = 1
                log_message("success", "Cambiado de TranslateControl a AudioControls.")

            elif self.current_step == 1:  # De AudioControls a TranslateControl
                log_message("debug", "Iniciando cambio de AudioControls a TranslateControl.")

                # Verificar si existen AudioControls y ocultarlos
                if hasattr(self, 'audio_controls'):
                    self.top_layout.removeWidget(self.audio_controls)
                    self.audio_controls.hide()
                    log_message("success", "AudioControls ocultados.")
                else:
                    log_message("warning", "No se encontró audio_controls para ocultar.")

                # Volver a mostrar TranslateControl si fue previamente ocultado
                if not self.translate_controls.isVisible():
                    self.top_layout.addWidget(self.translate_controls)
                    self.translate_controls.show()

                # Actualizar el paso actual
                self.current_step = 0
                log_message("success", "Cambiado de AudioControls a TranslateControl.")

            # Desactivar el botón 'Continuar' una vez completado el cambio
            self.continue_button.setEnabled(True)

        except Exception as e:
            log_message("error", "Error al cambiar de controles: %s", e, exc_info=True)'''

    def message_bg(self):
        """ Crea una etiqueta para mostrar el estado. """
        from app.utils.singleton_status import StatusManager

        # Crear la etiqueta de estado
        self.status_label = QLabel("", self)
        self.status_label.setAlignment(Qt.AlignCenter)

        # Asignar status_label al Singleton después de configurarlo
        StatusManager.get_instance().set_status_label(self.status_label)

        # Crear un layout para el QLabel
        status_layout = QHBoxLayout()
        status_layout.addWidget(self.status_label)
        status_layout.setContentsMargins(0, 0, 0, 0)

        # Crear un widget contenedor para el estado
        status_widget = QWidget(self)
        status_widget.setLayout(status_layout)

        # Aplicar un color de fondo genérico al widget contenedor
        status_widget.setStyleSheet(
            """
            background-color: #333333;
            border: 1px solid #555555;
            border-radius: 5px;
            """
            )  # Color de fondo genérico (puedes cambiarlo)

        return status_widget

    def status_and_continue_button(self):
        """ Crea un widget que contiene el campo de estado y boton continar """

        # Crear el layout horizontal
        status_continue_layout = QHBoxLayout()

        # Crear el campo de los mensajes de estado
        status_message = self.message_bg()
        status_message.setFixedHeight(35)
        status_continue_layout.addWidget(status_message)

        # Crear el campo del botón continuar
        continue_button = self.continue_control_button()
        continue_button.setFixedWidth(200)
        status_continue_layout.addWidget(continue_button)

        # Crear un widget contenedor y añadir el layout
        status_continue_button_widget = QWidget()
        status_continue_button_widget.setContentsMargins(9, 0, 0, 0)

        status_continue_button_widget.setLayout(status_continue_layout)

        log_message("info", "Widget de título creado con entrada y traducción.")
        return status_continue_button_widget

# Ejecutar la aplicación
if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        window = TikTokStoriesApp()
        window.show()
        log_message("success", "Aplicación iniciada.")
        sys.exit(app.exec_())
    except Exception as e:
        log_message("error", f"Error al iniciar la aplicación: {e}", exc_info=True)
