# app/utils/media_control.py

import os
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QObject, QTimer, QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from app.utils.debug import log_message
from app.utils.directories import get_tmp_dir, get_data_dir


class MediaPlayer(QObject):
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MediaPlayer, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()
        self.audio_player = QMediaPlayer(None, QMediaPlayer.StreamPlayback)
        self.video_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)

        # Configurar conexiones de señal para depuración
        self.audio_player.stateChanged.connect(self.debug_audio_state)
        self.audio_player.error.connect(self.handle_audio_error)
        self.video_player.stateChanged.connect(self.debug_video_state)
        self.video_player.error.connect(self.handle_video_error)

        self.loop_timer = QTimer()
        self.is_playing_video = False
        self.video_file = None  # Atributo para almacenar el video seleccionado
        log_message("success", "MediaPlayer configurado.")
        print("MediaPlayer inicializado.")

    def play_audio(self, temp_audio_path):
        """Reproduce el archivo de audio usando QMediaPlayer."""
        print(f"Intentando reproducir audio desde: {temp_audio_path}")

        url = QUrl.fromLocalFile(temp_audio_path)
        print(f"URL del archivo de audio: {url.toString()}")

        media_content = QMediaContent(url)
        print(f"Contenido multimedia cargado: {'Nulo' if media_content.isNull() else 'Válido'}")

        if media_content.isNull():
            print("Error: El contenido multimedia es nulo.")
            return

        self.audio_player.setMedia(media_content)
        print("Contenido de audio configurado en QMediaPlayer.")

        self.audio_player.play()
        print("Reproducción de audio iniciada.")
        log_message("success", f"Reproducción de audio iniciada: {temp_audio_path}")

    def play_video(self, temp_audio_path):
        """Reproduce el video en bucle usando QMediaPlayer."""
        print(f"Intentando reproducir video desde: {temp_audio_path}")

        self.video_player.setMedia(QMediaContent(QUrl.fromLocalFile(temp_audio_path)))
        self.video_player.setVolume(0)  # Silenciar el video si solo quieres el audio
        self.video_player.play()
        self.is_playing_video = True
        print("Reproducción de video iniciada.")
        log_message("success", f"Reproducción de video iniciada: {temp_audio_path}")

    def load_video(self, video_path):
        """Carga el archivo de video seleccionado y lo almacena."""
        self.video_file = video_path
        print(f"Archivo de video cargado: {video_path}")
        log_message("success", f"Archivo de video cargado: {video_path}")

    def play(self, play_type):
        """Inicia la reproducción de audio y/o video."""
        temp_audio_path = os.path.join(get_tmp_dir(), 'final_temp_audio.mp3')
        print(f"Ruta del archivo de audio temporal: {temp_audio_path}")

        if not os.path.exists(temp_audio_path):
            print(f"Error: El archivo de audio no existe en la ruta: {temp_audio_path}")
            return

        self.stop()  # Detener cualquier reproducción anterior

        if play_type == 'audio':
            # Solo reproducir audio
            print("Iniciando reproducción de solo audio.")
            self.play_audio(temp_audio_path)

        elif play_type == 'video' and self.video_file:
            # Leer la duración del audio desde el archivo
            duration_path = os.path.join(get_data_dir(), 'audio_duration.txt')
            print(f"Ruta del archivo de duración del audio: {duration_path}")

            try:
                with open(duration_path, 'r') as f:
                    audio_duration = int(f.read().strip())  # Leer y convertir a entero
                    print(f"Duración del audio leída: {audio_duration} ms")
            except Exception as e:
                print(f"Error al leer la duración del audio: {e}")
                QMessageBox.critical(None, "Error", f"Error al leer la duración del audio: {e}")
                log_message("error", f"Error al leer duración: {e}", exc_info=True)
                return

            # Reproducir audio
            print("Iniciando reproducción de audio.")
            self.play_audio(temp_audio_path)

            # Reproducir video
            print("Iniciando reproducción de video.")
            self.play_video(self.video_file)

            # Configurar temporizador para reiniciar el video
            self.loop_timer.timeout.connect(lambda: self.video_player.setPosition(0))
            self.loop_timer.start(audio_duration)  # Reiniciar el video al final del audio
            print("Temporizador para bucle de video configurado.")

    def stop(self):
        """Detiene la reproducción actual."""
        if self.audio_player.state() == QMediaPlayer.PlayingState:
            self.audio_player.stop()
            print("Reproducción de audio detenida.")
            log_message("info", "Reproducción de audio detenida.")

        if self.video_player.state() == QMediaPlayer.PlayingState:
            self.video_player.stop()
            self.is_playing_video = False
            print("Reproducción de video detenida.")
            log_message("info", "Reproducción de video detenida.")

        self.loop_timer.stop()  # Detener el temporizador si está activo
        print("Temporizador detenido.")

    def debug_audio_state(self, state):
        states = {
            0: 'Stopped',
            1: 'Playing',
            2: 'Paused'
        }
        print(f"Estado del reproductor de audio: {states.get(state, 'Desconocido')}")

    def handle_audio_error(self):
        print(f"Error en QMediaPlayer de audio: {self.audio_player.errorString()}")

    def debug_video_state(self, state):
        states = {
            0: 'Stopped',
            1: 'Playing',
            2: 'Paused'
        }
        print(f"Estado del reproductor de video: {states.get(state, 'Desconocido')}")

    def handle_video_error(self):
        print(f"Error en QMediaPlayer de video: {self.video_player.errorString()}")
