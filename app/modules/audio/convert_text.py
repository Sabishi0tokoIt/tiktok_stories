# app/modules/audio/convert_text.py

import glob
import os
import time
import gi

from google.cloud import texttospeech

from ...utils.directories import get_data_dir, get_tmp_dir
from ...utils.debug import log_message
from ..messages import show_status_message
from ...config.credentials import GoogleCloudAPIManager

gi.require_version('Gst', '1.0')
from gi.repository import Gst

# Inicializar GStreamer
Gst.init(None)

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
        combine_audio_files_gstreamer(audio_segments, final_audio_path, parent)

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
    """
    Divide el texto en fragmentos basados en párrafos, sin exceder la longitud máxima especificada.

    :param text: El texto completo que se desea dividir.
    :param max_length: Longitud máxima permitida para cada fragmento.
    :return: Una lista de fragmentos de texto.
    """
    try:
        # Aserción para verificar que el texto no esté vacío y max_length sea positivo
        assert text, "El texto no puede estar vacío."
        assert max_length > 0, "La longitud máxima debe ser mayor que cero."

        paragraphs = text.split('\n\n')  # Dividir el texto en párrafos
        chunks = []
        current_chunk = ""

        for paragraph in paragraphs:
            paragraph = paragraph.strip()

            # Verificar si añadir este párrafo hace que supere el límite
            if len(current_chunk) + len(paragraph) > max_length:
                # Comprobar si el párrafo actual por sí solo excede el límite
                if len(current_chunk) <= max_length:
                    # Agregar el bloque actual al conjunto de fragmentos
                    chunks.append(current_chunk.strip())
                    current_chunk = paragraph
                else:
                    # En caso de que el párrafo anterior sea demasiado grande, dividir allí
                    chunks.append(current_chunk.strip())
                    current_chunk = paragraph
            else:
                current_chunk += paragraph + "\n\n"

        # Asegurarse de agregar el último bloque
        if current_chunk:
            chunks.append(current_chunk.strip())

        log_message("info", f"Número total de fragmentos: {len(chunks)}")
        return chunks

    except AssertionError as e:
        log_message("error", f"Error de aserción en split_text_by_paragraphs: {e}", exc_info=True)
        return []  # Retornar lista vacía en caso de error

    except Exception as e:
        log_message("error", f"Error inesperado en split_text_by_paragraphs: {str(e)}", exc_info=True)
        return []  # Retornar lista vacía en caso de error inesperado


def combine_audio_files_gstreamer(audio_segments, output_file, parent):
    """
    Combina archivos de audio utilizando GStreamer.

    :param audio_segments: Lista de archivos de audio a combinar.
    :param output_file: Nombre del archivo de salida.
    :param status_label: Etiqueta para mostrar el estado en la UI.
    :param parent: Objeto padre que contiene los controles de audio.
    """
    try:
        # Asegúrate de que audio_segments no esté vacío
        assert audio_segments, "No hay archivos de audio para concatenar."

        # Crear el pipeline base de GStreamer
        pipeline_desc = f"concat name=c ! audioconvert ! lamemp3enc ! filesink location={output_file}"

        # Agregar los archivos de audio a concatenar
        for file in audio_segments:
            # Validar cada archivo
            assert isinstance(file, str) and file, f"Archivo no válido: {file}"
            pipeline_desc = f"filesrc location={file} ! decodebin ! audioconvert ! audioresample ! c. {pipeline_desc}"

        log_message("debug", f"Pipeline de GStreamer: {pipeline_desc}")

        # Crear el pipeline usando la descripción
        pipeline = Gst.parse_launch(pipeline_desc)

        # Establecer el estado a PLAYING
        pipeline.set_state(Gst.State.PLAYING)

        # Registrar el tiempo de inicio
        start_time = time.time()

        # Manejar mensajes del bus para esperar a EOS (End Of Stream)
        bus = pipeline.get_bus()
        message = bus.poll(Gst.MessageType.EOS, Gst.CLOCK_TIME_NONE)

        if message:
            # Registrar el tiempo de finalización y calcular el tiempo transcurrido
            end_time = time.time()
            elapsed_time = end_time - start_time
            log_message("info", f"Tiempo de concatenación: {elapsed_time:.2f} segundos")

            # Establecer el estado del pipeline a NULL al finalizar
            pipeline.set_state(Gst.State.NULL)

            show_status_message("Conversión de audio exitosa", "success")

            # Habilitar botones tras éxito en la conversión
            parent.audio_controls.play_button.setEnabled(True)
            parent.audio_controls.save_button.setEnabled(True)
        else:
            log_message("warning", "No se recibió mensaje EOS del bus de GStreamer.")
            show_status_message("Advertencia: No se recibió mensaje de finalización.", "warning")

    except AssertionError as e:
        log_message("error", f"Error de aserción: {e}", exc_info=True)
        show_status_message(str(e), "error")

    except Exception as e:
        log_message("error", f"Error en combine_audio_files_gstreamer: {str(e)}", exc_info=True)
        show_status_message(f"Error al combinar archivos: {str(e)}", "error")
