import glob
import os
import time
import ffmpeg  # Asegúrate de importar la biblioteca FFmpeg

from google.cloud import texttospeech

from app.utils.directories import get_data_dir, get_tmp_dir
from app.utils.debug import log_message
from app.modules.messages import show_status_message
from app.config.credentials import GoogleCloudAPIManager

# Inicializar el manejador de API de Google Cloud
google_cloud_manager = GoogleCloudAPIManager()

def delete_temp_mp3_files(temp_dir):
    # Asegúrate de que el directorio temporal exista
    assert os.path.exists(temp_dir), f"El directorio {temp_dir} no existe."

    # Eliminar todos los archivos .mp3 en el directorio temporal
    mp3_files = glob.glob(os.path.join(temp_dir, '*.mp3'))

    if not mp3_files:
        log_message("info", "No se encontraron archivos .mp3 para eliminar.")
        return  # Salir si no hay archivos para eliminar

    for mp3_file in mp3_files:
        try:
            os.remove(mp3_file)
            log_message("info", f"Archivo eliminado: {mp3_file}")
        except FileNotFoundError:
            log_message("warning", f"El archivo {mp3_file} no se encontró para eliminar.")
        except PermissionError:
            log_message("error", f"No se tiene permiso para eliminar el archivo {mp3_file}.", exc_info=True)
        except Exception as e:
            log_message("error", f"No se pudo eliminar el archivo {mp3_file}: {e}", exc_info=True)

def convert_text(parent):
    CHAR_LIMIT = 4500
    client = google_cloud_manager.get_client('texttospeech')

    data_dir = get_data_dir()
    temp_dir = get_tmp_dir()

    delete_temp_mp3_files(temp_dir)

    text_file_path = os.path.join(data_dir, 'text_for_user.txt')
    voice_file_path = os.path.join(data_dir, 'voice_config.txt')
    country_id_file_path = os.path.join(data_dir, 'country_code.txt')
    gender_mf_file_path = os.path.join(data_dir, 'gender.txt')
    speed_file_path = os.path.join(data_dir, 'speed.txt')
    pitch_file_path = os.path.join(data_dir, 'pitch.txt')

    try:
        show_status_message("Leyendo archivo para convertir...", "info")

        # Usar with para abrir archivos y asegurar su cierre automático
        with open(text_file_path, 'r', encoding='utf-8') as file:
            text = file.read().strip()

        with open(voice_file_path, 'r', encoding='utf-8') as file:
            voice_name = file.read().strip()

        with open(country_id_file_path, 'r', encoding='utf-8') as file:
            country_id = file.read().strip()

        with open(gender_mf_file_path, 'r', encoding='utf-8') as file:
            gender_mf = file.read().strip()

        with open(speed_file_path, 'r', encoding='utf-8') as file:
            speaking_rate = float(file.read().strip())

        with open(pitch_file_path, 'r', encoding='utf-8') as file:
            speaking_pitch = int(file.read().strip())

        # Validar que los archivos leídos no estén vacíos
        assert text, "El archivo 'text_for_user.txt' está vacío."
        assert voice_name, "El archivo 'voice_config.txt' está vacío."

        # Configuración de voz y audio
        voice_params = texttospeech.VoiceSelectionParams(
            language_code=country_id,
            name=voice_name,
            ssml_gender=texttospeech.SsmlVoiceGender[gender_mf.upper()]
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=speaking_rate,
            pitch=speaking_pitch / 100.0
        )

        # Dividir el texto en fragmentos
        text_chunks = split_text_by_paragraphs(text, CHAR_LIMIT)

        audio_segments = []
        for idx, chunk in enumerate(text_chunks):
            ssml_text = f'<speak><prosody rate="{speaking_rate}" pitch="{speaking_pitch}Hz">{chunk}</prosody></speak>'
            input_text = texttospeech.SynthesisInput(ssml=ssml_text)
            show_status_message("Convirtiendo audio...", "info")

            response = client.synthesize_speech(input=input_text, voice=voice_params, audio_config=audio_config)

            if response.audio_content:
                temp_file_path = os.path.join(temp_dir, f"temp_audio_{idx}.mp3")
                with open(temp_file_path, 'wb') as temp_file:
                    temp_file.write(response.audio_content)
                    audio_segments.append(temp_file_path)
            else:
                log_message("warning", "Respuesta de síntesis de voz vacía.")

        final_audio_path = os.path.join(temp_dir, 'final_temp_audio.mp3')
        show_status_message("Concatenando archivos de audio...", "info")
        combine_audio_files_ffmpeg(audio_segments, final_audio_path)

        show_status_message("Conversión finalizada", "success")
        return final_audio_path

    except AssertionError as e:
        log_message("error", f"Error de aserción: {e}", exc_info=True)
        show_status_message(f"Error de aserción: {str(e)}", "error")
        return None

    except ValueError as e:
        log_message("error", f"Error de valor: {e}", exc_info=True)
        show_status_message(f"Error de valor: {str(e)}", "error")
        return None

    except Exception as e:
        log_message("error", f"Error al convertir el texto: {e}", exc_info=True)
        show_status_message(f"Error al convertir el texto: {str(e)}", "error")
        return None

def split_text_by_paragraphs(text, max_length):
    try:
        assert text, "El texto no puede estar vacío."
        assert max_length > 0, "La longitud máxima debe ser mayor que cero."

        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""

        for paragraph in paragraphs:
            paragraph = paragraph.strip()

            if len(current_chunk) + len(paragraph) > max_length:
                if len(current_chunk) <= max_length:
                    chunks.append(current_chunk.strip())
                    current_chunk = paragraph
                else:
                    chunks.append(current_chunk.strip())
                    current_chunk = paragraph
            else:
                current_chunk += paragraph + "\n\n"

        if current_chunk:
            chunks.append(current_chunk.strip())

        log_message("info", f"Número total de fragmentos: {len(chunks)}")
        return chunks

    except AssertionError as e:
        log_message("error", f"Error de aserción en split_text_by_paragraphs: {e}", exc_info=True)
        return []

    except Exception as e:
        log_message("error", f"Error inesperado en split_text_by_paragraphs: {str(e)}", exc_info=True)
        return []

def combine_audio_files_ffmpeg(audio_segments, output_file):
    """
    Combina archivos de audio utilizando FFmpeg.

    :param audio_segments: Lista de archivos de audio a combinar.
    :param output_file: Nombre del archivo de salida.
    """
    try:
        assert audio_segments, "No hay archivos de audio para concatenar."

        # Crear el comando de FFmpeg para concatenar archivos
        input_args = ''.join([f"-i '{segment}' " for segment in audio_segments])
        cmd = f"ffmpeg {input_args}-filter_complex 'concat=n={len(audio_segments)}:v=0:a=1' -y '{output_file}'"

        log_message("debug", f"Comando de FFmpeg: {cmd}")

        # Ejecutar el comando
        process = ffmpeg.input('pipe:0').output(output_file).global_args('-loglevel', 'error')
        process.run()

        show_status_message("Conversión de audio exitosa", "success")
    except AssertionError as e:
        log_message("error", f"Error de aserción: {e}", exc_info=True)
        show_status_message(str(e), "error")
    except Exception as e:
        log_message("error", f"Error en combine_audio_files_ffmpeg: {str(e)}", exc_info=True)
        show_status_message(f"Error al combinar archivos: {str(e)}", "error")
