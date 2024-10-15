# app/modules/translate/translate_text.py

from app.config.credentials import GoogleCloudAPIManager
from ...utils.debug import log_message


def translate_text_with_model(text: str, target_language: str, source_language: str = None):
    # Crear una instancia de GoogleCloudAPIManager
    google_cloud_manager = GoogleCloudAPIManager()

    # Obtener el cliente de traducción
    try:
        translate_client = google_cloud_manager.get_client('translate')
        log_message('info', "Cliente de traducción obtenido correctamente.")
    except Exception as e:
        log_message('error', f"Error al obtener el cliente de traducción: {e}")
        return None

    # Obtener el project_id
    try:
        project_id = google_cloud_manager.get_project_id()
        log_message("info", "Identificación del proyecto de Google Cloud obtenido exitosamente.")
        if not project_id:
            log_message('warning', "No se pudo obtener el project_id.")
            return None
    except Exception as e:
        log_message('error', f"Error al obtener el project_id: {str(e)}", exc_info=True)
        return None

    # Configurar los parámetros del proyecto y modelo personalizado
    model_id = "general/nmt"
    location = "us-central1"
    parent = f"projects/{project_id}/locations/{location}"
    model_path = f"{parent}/models/{model_id}"

    log_message('debug', f"Parámetros de traducción - Project ID: {project_id}, Model Path: {model_path}")

    try:
        # Realizar la traducción utilizando el modelo personalizado
        response = translate_client.translate_text(
            request={
                "contents": [text],
                "target_language_code": target_language,
                "source_language_code": source_language,
                "model": model_path,
                "parent": parent,
                "mime_type": "text/plain",
            }
        )
        log_message('debug', f"Respuesta de Google Translate: {response}")

        # Retornar el texto traducido
        return response.translations[0].translated_text

    except Exception as e:
        log_message('error', f"Error al traducir: {str(e)}", exc_info=True)
        return None
