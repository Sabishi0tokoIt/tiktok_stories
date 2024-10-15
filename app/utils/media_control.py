# app/utils/media_control.py

# app/utils/media_control.py

import gi
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtCore import QTimer
from .debug import log_message
from .directories import get_tmp_dir

gi.require_version('Gst', '1.0')
from gi.repository import Gst

class MediaPlayer:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MediaPlayer, cls).__new__(cls)
            cls._instance._init_gst()
        return cls._instance

    def _init_gst(self):
        Gst.init(None)  # Inicializa GStreamer
        self.pipeline = None
        log_message("success", "GStreamer inicializado y MediaPlayer configurado.")
        self.loop_timer = None

    def play(self, file_name=None, is_audio=True):
        """Reproduce un archivo de audio o video usando GStreamer."""
        if self.pipeline:
            self.pipeline.set_state(Gst.State.NULL)  # Detener cualquier reproducción anterior

        # Reproducir audio
        temp_audio_path = get_tmp_dir() / 'final_temp_audio.mp3'
        audio_uri = f"file://{str(temp_audio_path)}"

        if is_audio:
            uri = audio_uri  # Si es solo audio
        else:
            if not file_name:
                file_name, _ = QFileDialog.getOpenFileName(None, "Seleccionar archivo de video", "",
                                                           "Video files (*.mp4 *.avi *.mov *.mkv)")
            if file_name:
                uri = f"file://{str(file_name)}"
                self.loop_video(file_name)  # Reproducir video en bucle
            else:
                QMessageBox.critical(None, "Error", "No se seleccionó ningún archivo de video.")
                return

        try:
            # Crear el pipeline de GStreamer para audio y video
            self.pipeline = Gst.parse_launch(f"playbin uri={uri}")

            # Conectar el bus de mensajes para eventos como fin de reproducción
            bus = self.pipeline.get_bus()
            bus.add_signal_watch()
            bus.connect("message", self.on_message)

            # Iniciar la reproducción de audio
            self.pipeline.set_state(Gst.State.PLAYING)
            log_message("success", f"Reproducción iniciada para {'audio' if is_audio else 'video'}: {uri}")
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error al intentar reproducir el archivo: {e}")
            log_message("error", f"Error al reproducir {'audio' if is_audio else 'video'}: {e}", exc_info=True)

    def loop_video(self, file_name):
        """Reproduce el video en bucle por un tiempo asignado."""
        self.stop_loop()  # Asegurarse de que no haya un temporizador anterior
        self.loop_timer = QTimer()
        self.loop_timer.timeout.connect(lambda: self.play(file_name, is_audio=False))
        self.loop_timer.start(10000)  # Reproducir en bucle cada 10 segundos (ajusta el tiempo según sea necesario)

    def stop_loop(self):
        """Detiene el bucle de reproducción del video."""
        if self.loop_timer:
            self.loop_timer.stop()
            self.loop_timer = None

    def stop(self):
        """Detiene la reproducción actual."""
        if self.pipeline:
            self.pipeline.set_state(Gst.State.NULL)  # Cambia el estado a NULL para detener la reproducción
            log_message("info", "Reproducción detenida.")
            self.stop_loop()  # Detener el bucle de video si está activo
        else:
            log_message("warning", "No hay ninguna reproducción en curso que detener.")

    def on_message(self, bus, message):
        """Maneja los mensajes del bus de GStreamer."""
        t = message.type
        if t == Gst.MessageType.EOS:
            self.pipeline.set_state(Gst.State.NULL)  # Fin de la reproducción
            log_message("info", "Reproducción finalizada.")
            self.stop_loop()  # Asegurarse de detener el bucle al final de la reproducción
        elif t == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            log_message("error", f"Error en GStreamer: {err}, debug info: {debug}")
            self.pipeline.set_state(Gst.State.NULL)
            self.stop_loop()  # Detener el bucle si hay un error

