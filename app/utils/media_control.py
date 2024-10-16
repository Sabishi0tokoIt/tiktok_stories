# app/utils/media_control.py
import os
import subprocess
import ffmpeg
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtCore import QObject, QTimer
from app.utils.debug import log_message
from app.utils.directories import get_tmp_dir


class MediaPlayer(QObject):
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MediaPlayer, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()
        self.process = None
        log_message("success", "MediaPlayer configurado.")

    def play(self, file_name=None, is_audio=True):
        """Reproduce un archivo de audio usando FFmpeg."""
        self.stop()  # Detener cualquier reproducción anterior

        # Ruta temporal para el archivo de audio
        temp_audio_path = os.path.join(get_tmp_dir(), 'final_temp_audio.mp3')

        # Si es audio, usa el archivo temporal
        if is_audio:
            uri = temp_audio_path  # Usar el archivo temporal si es solo audio
        else:
            # Lógica para video (opcional)
            if not file_name:
                file_name, _ = QFileDialog.getOpenFileName(None, "Seleccionar archivo de video", "",
                                                           "Video files (*.mp4 *.avi *.mov *.mkv)")
            if not file_name:
                QMessageBox.critical(None, "Error", "No se seleccionó ningún archivo de video.")
                return
            uri = file_name  # Usar el archivo seleccionado

        try:
            # Comando de FFmpeg para reproducir audio o video
            command = ["ffplay", "-nodisp", "-autoexit", uri]

            # Ejecutar el comando
            self.process = subprocess.Popen(command)
            log_message("success", f"Reproducción iniciada para {'audio' if is_audio else 'video'}: {uri}")
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error al intentar reproducir el archivo: {e}")
            log_message("error", f"Error al reproducir {'audio' if is_audio else 'video'}: {e}", exc_info=True)

    def stop(self):
        """Detiene la reproducción actual."""
        if self.process:
            self.process.terminate()  # Termina el proceso de FFmpeg
            self.process = None
            log_message("info", "Reproducción detenida.")
        else:
            log_message("warning", "No hay ninguna reproducción en curso que detener.")

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
        if self.process:
            self.process.terminate()  # Termina el proceso de FFmpeg
            self.process = None
            log_message("info", "Reproducción detenida.")
            self.stop_loop()  # Detener el bucle de video si está activo
        else:
            log_message("warning", "No hay ninguna reproducción en curso que detener.")
