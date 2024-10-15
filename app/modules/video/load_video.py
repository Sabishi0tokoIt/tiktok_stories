# app/modules/video/load_video.py

from PyQt5.QtWidgets import QFileDialog, QMessageBox, QWidget
import os

from app.modules.messages import show_status_message
from app.utils.debug import log_message
from app.utils.directories import get_tmp_dir, get_project_root, get_data_dir, get_videos_dir, get_projects_dir

class LoadVideoControls(QWidget):
    """Clase para cargar el video."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_video_path = None  # Atributo para almacenar la ruta del video cargado

    def load_video(self):
        """Carga un video utilizando el cuadro de diálogo."""
        try:
            # Definir el directorio de videos
            videos_dir = os.path.join(get_project_root(), 'includes', 'videos')

            # Abrir el cuadro de diálogo para seleccionar un archivo de video
            video_path, _ = QFileDialog.getOpenFileName(self, "Seleccionar archivo de video", videos_dir,
                                                         "Video Files (*.mp4 *.avi *.mkv *.mov)")

            if video_path:
                # Guarda la ruta del video cargado en el atributo de instancia
                self.current_video_path = video_path
                initialize_player()  # Asegúrate de que el reproductor esté inicializado
                set_video_uri(video_path)  # Configura la URI del video en el reproductor
                show_status_message("Video cargado exitosamente", "info")
            else:
                show_status_message("No se seleccionó ningún video", "warning")
        except Exception as e:
            log_message("error", f"Error al cargar el video: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", "No se pudo cargar el video.")

def set_video_uri(video_path):
    """Configura la URI del video en el reproductor."""
    global player
    if player:
        player.set_property("uri", "file://" + video_path)
        log_message("info", f"URI del video configurada: {video_path}")
    else:
        log_message("error", "Reproductor no inicializado. No se pudo establecer la URI del video.")
