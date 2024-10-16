# app/modules/audio/convert_text.py

import os
import glob
import ffmpeg
from google.cloud import texttospeech

from app.utils.directories import get_data_dir, get_tmp_dir
from app.utils.debug import log_message
from app.modules.messages import show_status_message
from app.config.credentials import GoogleCloudAPIManager

# Inicializar el manejador de API de Google Cloud
google_cloud_manager = GoogleCloudAPIManager()

def delete_temp_mp3_files(temp_dir):
    """Borra todos los archivos temporales .mp3 del directorio temporal."""
    assert os.path.exists(temp_dir), f"El directorio {temp_dir} no existe."
    mp3_files = glob.glob(os.path.join(temp_dir, '*.mp3'))

    if not mp3_files:
        log_message("info", "No se encontraron archivos .mp3 para eliminar.")
        print("No se encontraron archivos .mp3 para eliminar.")
        return

    for mp3_file in mp3_files:
        try:
            os.remove(mp3_file)
            log_message("info", f"Archivo eliminado: {mp3_file}")
            print(f"Archivo eliminado: {mp3_file}")
        except FileNotFoundError:
            log_message("warning", f"El archivo {mp3_file} no se encontró para eliminar.")
            print(f"El archivo {mp3_file} no se encontró para eliminar.")
        except PermissionError:
            log_message("error", f"No se tiene permiso para eliminar el archivo {mp3_file}.", exc_info=True)
            print(f"No se tiene permiso para eliminar el archivo {mp3_file}.")
        except Exception as e:
            log_message("error", f"No se pudo eliminar el archivo {mp3_file}: {e}", exc_info=True)
            print(f"No se pudo eliminar el archivo {mp3_file}: {e}")

def convert_text(parent):
    BYTE_LIMIT = 5000  # Límite de bytes en lugar de caracteres
    client = google_cloud_manager.get_client('texttospeech')

    data_dir = get_data_dir()
    temp_dir = get_tmp_dir()

    print(f"Directorio de datos: {data_dir}")
    print(f"Directorio temporal: {temp_dir}")

    delete_temp_mp3_files(temp_dir)

    text_file_path = os.path.join(data_dir, 'text_for_user.txt')
    voice_file_path = os.path.join(data_dir, 'voice_config.txt')
    country_id_file_path = os.path.join(data_dir, 'country_code.txt')
    gender_mf_file_path = os.path.join(data_dir, 'gender.txt')
    speed_file_path = os.path.join(data_dir, 'speed.txt')
    pitch_file_path = os.path.join(data_dir, 'pitch.txt')

    try:
        show_status_message("Leyendo archivo para convertir...", "info")
        print("Leyendo archivo para convertir...")

        with open(text_file_path, 'r', encoding='utf-8') as file:
            text = file.read().strip()
            print(f"Texto leído: {text[:50]}...")  # Muestra los primeros 50 caracteres

        with open(voice_file_path, 'r', encoding='utf-8') as file:
            voice_name = file.read().strip()
            print(f"Nombre de la voz: {voice_name}")

        with open(country_id_file_path, 'r', encoding='utf-8') as file:
            country_id = file.read().strip()
            print(f"Código de país: {country_id}")

        with open(gender_mf_file_path, 'r', encoding='utf-8') as file:
            gender_mf = file.read().strip()
            print(f"Género: {gender_mf}")

        with open(speed_file_path, 'r', encoding='utf-8') as file:
            speaking_rate = float(file.read().strip())
            print(f"Velocidad de habla: {speaking_rate}")

        with open(pitch_file_path, 'r', encoding='utf-8') as file:
            speaking_pitch = int(file.read().strip())
            print(f"Tono de voz: {speaking_pitch}")

        assert text, "El archivo 'text_for_user.txt' está vacío."
        assert voice_name, "El archivo 'voice_config.txt' está vacío."

        # Configuración de voz y audio
        voice_params = texttospeech.VoiceSelectionParams(
            language_code=country_id,
            name=voice_name,
            ssml_gender=texttospeech.SsmlVoiceGender[gender_mf.upper()]
        )
        print(f"Parámetros de voz: {voice_params}")

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=speaking_rate,
            pitch=speaking_pitch / 100.0
        )
        print(f"Configuración de audio: {audio_config}")

        # Dividir el texto si es necesario por bytes
        text_chunks = split_text_by_bytes(text, BYTE_LIMIT)
        print(f"Fragmentos de texto generados: {len(text_chunks)}")

        audio_segments = []
        for idx, chunk in enumerate(text_chunks):
            input_text = texttospeech.SynthesisInput(text=chunk)
            show_status_message("Convirtiendo audio...", "info")
            print(f"Convirtiendo audio... Fragmento {idx+1}/{len(text_chunks)}")

            response = client.synthesize_speech(input=input_text, voice=voice_params, audio_config=audio_config)

            if response.audio_content:
                temp_file_path = os.path.join(temp_dir, f"temp_audio_{idx}.mp3")
                with open(temp_file_path, 'wb') as temp_file:
                    temp_file.write(response.audio_content)
                    audio_segments.append(temp_file_path)
                    print(f"Archivo temporal creado: {temp_file_path}")
            else:
                log_message("warning", "Respuesta de síntesis de voz vacía.")
                print("Respuesta de síntesis de voz vacía.")

        # Si se generaron múltiples fragmentos, combinarlos
        if len(audio_segments) > 1:
            # Llama a combine_audio_files_ffmpeg() para concatenar los archivos
            combine_audio_files_ffmpeg()
            show_status_message("El texto se convirtio con éxito a audio.", "success")
            return
        elif audio_segments:
            print("Un solo archivo de audio generado.")
            show_status_message("El texto se convirtio con éxito a audio.", "success")
            # Lógica para cambiar el nombre del archivo generado
            # Suponiendo que el archivo se genera como 'temp_audio_2.mp3', lo renombramos a 'final_temp_audio.mp3'
            final_audio_path = os.path.join(temp_dir, 'final_temp_audio.mp3')
            os.rename(audio_segments[0], final_audio_path)

            return final_audio_path  # Devolver el nuevo nombre del archivo
        else:
            show_status_message("No se generaron archivos de audio.", "error")
            print("No se generaron archivos de audio.")
            return None

    except AssertionError as e:
        log_message("error", f"Error de aserción: {e}", exc_info=True)
        show_status_message(f"Error de aserción: {str(e)}", "error")
        print(f"Error de aserción: {str(e)}")
        return None

    except ValueError as e:
        log_message("error", f"Error de valor: {e}", exc_info=True)
        show_status_message(f"Error de valor: {str(e)}", "error")
        print(f"Error de valor: {str(e)}")
        return None

    except Exception as e:
        log_message("error", f"Error al convertir el texto: {e}", exc_info=True)
        show_status_message(f"Error al convertir el texto: {str(e)}", "error")
        print(f"Error al convertir el texto: {str(e)}")
        return None

import os

def split_text_by_bytes(text, byte_limit):
    """Divide el texto en fragmentos respetando el límite de bytes (UTF-8) y guarda las rutas en input.txt."""
    try:
        assert text, "El texto no puede estar vacío."
        assert byte_limit > 0, "El límite de bytes debe ser mayor que cero."

        current_chunk = ""
        chunks = []
        current_size = 0

        for word in text.split():
            word_size = len(word.encode('utf-8')) + 1  # +1 por el espacio

            if current_size + word_size > byte_limit:
                # Agrega el fragmento actual a la lista
                chunks.append(current_chunk.strip())
                # Comienza un nuevo fragmento con la palabra actual
                current_chunk = word + " "
                current_size = word_size
            else:
                # Agrega la palabra actual al fragmento
                current_chunk += word + " "
                current_size += word_size

        # Agrega el último fragmento si no está vacío
        if current_chunk:
            chunks.append(current_chunk.strip())

        # Guarda las rutas de los archivos en input.txt
        temp_input_path = os.path.join(get_tmp_dir(), 'input.txt')
        with open(temp_input_path, 'w', encoding='utf-8') as file:
            for i, chunk in enumerate(chunks):
                # Asumiendo que los nombres de archivos son secuenciales
                file.write(f"file 'C:/Users/sabishi/PycharmProjects/tiktok_stories/tmp/temp_audio_{i}.mp3' \n")

        log_message("info", f"Número total de fragmentos: {len(chunks)}")
        print(f"Número total de fragmentos: {len(chunks)}")
        return chunks

    except AssertionError as e:
        log_message("error", str(e), exc_info=True)
        print(f"Error: {str(e)}")
        return []

def combine_audio_files_ffmpeg():
    """Combina múltiples archivos de audio utilizando FFmpeg."""
    try:

        # Crear un archivo de texto para los segmentos de audio
        output_file = os.path.join(get_tmp_dir(), 'final_temp_audio.mp3')
        input_txt_path = os.path.join(get_tmp_dir(), 'input.txt')

        # Construir el comando para FFmpeg
        cmd = f"ffmpeg -f concat -safe 0 -i {input_txt_path} -c copy {output_file}"
        print(f"Ejecutando comando: {cmd}")
        os.system(cmd)

    except AssertionError as e:
        log_message("error", f"Error de aserción en combine_audio_files_ffmpeg: {e}", exc_info=True)
        print(f"Error de aserción en combine_audio_files_ffmpeg: {str(e)}")

    except Exception as e:
        log_message("error", f"Error inesperado en combine_audio_files_ffmpeg: {str(e)}", exc_info=True)
        print(f"Error inesperado en combine_audio_files_ffmpeg: {str(e)}")

