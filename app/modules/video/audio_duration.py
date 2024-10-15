# app/modules/video/audio_duration.py

import os
import subprocess
from app.utils.utils import get_tmp_dir, log_message, log_event_and_function

@log_event_and_function("get_audio_duration_event")  # Agregar el decorador
def get_audio_duration_ffmpeg(audio_path=None):
    """
    Obtiene la duración del archivo de audio usando ffmpeg en milisegundos.

    Args:
    - audio_path (str or None): Ruta del archivo de audio. Si no se proporciona,
                                se usará el archivo 'final_audio.mp3' en el directorio temporal.

    Returns:
    - int: Duración del archivo de audio en milisegundos.
    """
    if audio_path is None:
        audio_path = get_tmp_dir() / 'final_audio.mp3'  # Archivo de audio predeterminado

    if not os.path.exists(audio_path):
        log_message("warning", "El archivo de audio %s no existe.", audio_path)
        return -1

    try:
        log_message("debug", "Ejecutando ffmpeg para obtener la duración del audio en %s", audio_path)

        # Ejecutar el comando de ffmpeg para obtener la duración en milisegundos
        result = subprocess.run(
            ["ffmpeg", "-i", str(audio_path), "-hide_banner"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        # Buscar la línea que contiene "Duration"
        for line in result.stdout.splitlines():
            if "Duration" in line:
                duration_str = line.split(",")[0].split("Duration: ")[1].strip()
                h, m, s = map(float, duration_str.split(":"))
                # Convertir a milisegundos
                duration_ms = int((h * 3600 + m * 60 + s) * 1000)
                log_message("info", "Duración del audio obtenida: %d ms", duration_ms)
                return duration_ms

        log_message("warning", "No se encontró la duración en la salida de ffmpeg.")

    except Exception as e:
        log_message("error", "Error al obtener la duración del audio: %s", str(e))
        return -1
