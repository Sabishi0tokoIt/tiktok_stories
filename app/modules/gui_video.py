# app/modules/video/gui_video.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from .video import load_video
from .messages import show_status_message
from ..utils.debug import log_message

from PyQt5.QtWidgets import QVBoxLayout, QWidget


class VideoControls(QWidget):
    def __init__(self, parent=None):
        super(VideoControls, self).__init__(parent)

        self.layout_principal = None
        self.parent = parent  # Almacenar una referencia al padre (la ventana principal)

        # Iniciar el ui
        self.init_ui()

    def init_ui(self):
        """Inicializa la interfaz de usuario para los controles de video."""
        # Layout principal
        self.layout_principal = QVBoxLayout(self)
        log_message("debug", "Inicializando la interfaz de usuario de VideoControls.")

        # Agregar la función mostrar medios
        show_media_widget = self.show_media_widget()
        self.layout_principal.addWidget(show_media_widget)


        '''# Botón para cargar video
        self.load_video_button = QPushButton("Cargar Video")
        self.load_video_button.clicked.connect(self.load_video)
        layout.addWidget(self.load_video_button)

        # Botón para reproducir video y audio
        self.play_button = QPushButton("Reproducir Video y Audio")
        self.play_button.clicked.connect(self.play_video_audio)
        layout.addWidget(self.play_button)

        # Botón para detener video y audio
        self.stop_button = QPushButton("Detener Video y Audio")
        self.stop_button.clicked.connect(self.stop_video_audio)
        layout.addWidget(self.stop_button)

        # Botón para guardar video y audio
        self.save_button = QPushButton("Guardar Video y Audio")
        self.save_button.clicked.connect(self.save_media)
        layout.addWidget(self.save_button)

        self.setLayout(layout)
        '''
        log_message("success", "Interfaz de VideoControls inicializada.")

    def show_media_widget(self):
        import gi
        gi.require_version('Gst', '1.0')
        from gi.repository import Gst, GObject

        """Crea un espacio para mostrar el video."""
        # Crear un nuevo widget donde se mostrará el video
        self.video_widget = QWidget(self)
        self.layout_principal.addWidget(self.video_widget)

        # Crear un layout para el widget de video
        self.video_layout = QVBoxLayout(self.video_widget)

        # Crear un elemento de GStreamer para el video
        self.video_sink = Gst.ElementFactory.make("qt5videosink", "video_sink")
        if not self.video_sink:
            log_message("error", "No se pudo crear el sink para el video.")
            return

        # Integrar el widget de GStreamer en el layout
        self.video_layout.addWidget(self.video_sink)

        # Iniciar GStreamer
        GObject.threads_init()
        Gst.init(None)

        log_message("info", "Widget de video creado y agregado al layout.")

    def load_video(self):
        """Carga un video utilizando la función load_video."""
        load_video(None)
        show_status_message("Video catgado", "info")

    '''def play_video_audio(self):
        """Reproduce el video y audio utilizando la función play_video_audio."""
        play_video_audio()
        show_status_message("Reproduciendo video y audio", "info")

    def stop_video_audio(self):
        """Detiene la reproducción utilizando la función stop_video_audio."""
        stop_video_audio()
        show_status_message("Reproducción detenida", "info")

    def save_media(self):
        """Guarda el video y audio utilizando la función save_media."""
        save_media()
        self.status_label.setText("Archivo guardado.")
        show_status_message("Archivo guardado", "info")'''