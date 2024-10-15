# app/modules/translate/detect_language.py

from app.config.credentials import GoogleCloudAPIManager
from ...utils.debug import log_message
from ..messages import show_status_message

def detect_language(text: str):
    log_message('info', f"Iniciando la detección de idioma para el texto: {text}")

    # Crear una instancia de GoogleCloudAPIManager
    google_cloud_manager = GoogleCloudAPIManager()

    # Obtener el cliente de traducción
    try:
        translate_client = google_cloud_manager.get_client('translate')
        log_message('info', "Cliente de traducción obtenido correctamente.")
    except Exception as e:
        log_message('error', f"Error al obtener el cliente de traducción: {e}")
        return None

    # Detectar el idioma del texto proporcionado
    try:
        response = translate_client.detect_language(
            parent=f"projects/{google_cloud_manager.get_project_id()}/locations/global",
            content=text
        )
        log_message('debug', f"[DEBUG] Respuesta de detección de idioma: {response}")

        # Asegurarse de que la respuesta tenga el campo esperado
        if response.languages:
            detected_language = response.languages[0].language_code  # Revisar la estructura aquí
            log_message('debug', f"Idioma detectado: {detected_language}")
            show_status_message(f"Idioma a traducir: {detected_language}", "info")
            return detected_language
        else:
            log_message('warning', "No se detectó ningún idioma.")
            return None
    except Exception as e:
        log_message('error', f"Error al detectar el idioma: {e}")
        return None