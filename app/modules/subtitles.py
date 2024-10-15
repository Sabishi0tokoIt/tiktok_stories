# app/modules/subtitles.py

import os
import subprocess
import vlc
from app.modules.video import current_audio_path, load_text  # Importar la función y variable global
from app.utils.utils import log_message, log_event_and_function


@log_event_and_function("generate_srt_from_text_file_event")  # Decorador para la función
def generate_srt_from_text_file(text_path, total_audio_duration, file_name="subtitulos.srt"):
    """
    Genera un archivo SRT basado en el contenido de un archivo de texto.
    :param text_path: La ruta del archivo de texto.
    :param total_audio_duration: Duración total del audio en segundos.
    :param file_name: El nombre del archivo SRT que se generará.
    """
    log_message("info", "Iniciando la generación del archivo SRT.")
    text = load_text(text_path)  # Usa load_text() para obtener el texto
    text_parts = text.split(". ")  # Dividimos el texto en frases
    duration_per_part = total_audio_duration / len(text_parts)

    def format_time(seconds):
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        milliseconds = int((seconds - int(seconds)) * 1000)
        return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

    srt_content = ""
    for i, part in enumerate(text_parts):
        start = i * duration_per_part
        end = (i + 1) * duration_per_part
        srt_content += f"{i + 1}\n"
        srt_content += f"{format_time(start)} --> {format_time(end)}\n"
        srt_content += f"{part}\n\n"

    with open(file_name, "w", encoding="utf-8") as f:
        f.write(srt_content)

    log_message("info", f"Subtítulos guardados en {file_name}")
    return file_name


@log_event_and_function("add_subtitles_to_video_event")  # Decorador para la función
def add_subtitles_to_video(video_path, subtitles_path, output_path):
    """
    Añade subtítulos a un archivo de video usando ffmpeg.
    :param video_path: La ruta del archivo de video.
    :param subtitles_path: La ruta del archivo SRT con los subtítulos.
    :param output_path: La ruta del archivo de video de salida.
    """
    log_message("info", "Iniciando la adición de subtítulos al video.")
    command = [
        'ffmpeg', '-i', video_path, '-vf', f'subtitles={subtitles_path}',
        '-c:a', 'copy', output_path
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        log_message("error", f"Error al agregar subtítulos al video: {result.stderr}")
        raise RuntimeError(f"Error al agregar subtítulos al video: {result.stderr}")
    log_message("info", f"Video con subtítulos guardado en {output_path}")


@log_event_and_function("process_subtitles_event")  # Decorador para la función
def process_subtitles():
    """
    Función para procesar subtítulos: generar archivo SRT y añadir subtítulos al video.
    """
    from app.utils.utils import get_data_dir
    from tkinter import filedialog, messagebox

    # Rutas de los archivos
    text_path = os.path.join(get_data_dir(), 'text_for_user.txt')  # Archivo de texto para subtítulos

    # Verificar si el archivo de texto existe
    if not os.path.exists(text_path):
        log_message("error", "No se encontró el archivo de texto para los subtítulos.")
        raise FileNotFoundError("No se encontró el archivo de texto para los subtítulos.")

    # Obtener el archivo de audio actual cargado
    audio_file_path = current_audio_path

    if audio_file_path is None:
        log_message("error", "No se ha cargado ningún archivo de audio.")
        raise ValueError("No se ha cargado ningún archivo de audio.")

    # Obtener la duración total del audio
    try:
        audio_duration = vlc.MediaPlayer(audio_file_path).get_length() / 1000  # Duración en segundos
    except Exception as e:
        log_message("error", f"Error al obtener la duración del audio: {e}")
        raise RuntimeError(f"Error al obtener la duración del audio: {e}")

    # Generar archivo SRT usando el texto del archivo
    subtitles_path = generate_srt_from_text_file(text_path, audio_duration)

    # Seleccionar el archivo de video
    video_path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4 *.avi *.mkv *.mov")])
    if not video_path:
        log_message("error", "No se ha seleccionado ningún video.")
        raise ValueError("No se ha seleccionado ningún video.")

    # Definir la ruta de salida para el video con subtítulos
    out_path = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("MP4 files", "*.mp4")])

    if out_path:
        # Aplicar los subtítulos usando ffmpeg
        try:
            add_subtitles_to_video(video_path, subtitles_path, out_path)
            return out_path
        except RuntimeError as e:
            log_message("error", f"Error al agregar subtítulos al video: {e}")
            raise RuntimeError(f"Error al agregar subtítulos al video: {e}")

    log_message("error", "No se ha especificado una ruta de salida para el video.")
    raise ValueError("No se ha especificado una ruta de salida para el video.")
