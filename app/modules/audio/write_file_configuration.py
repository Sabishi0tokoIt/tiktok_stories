# app/modules/audio/write_file_configuration.py

import importlib
from app.utils.utils import write
from app.modules.messages import show_status_message
from app.utils.debug import log_message

def write_file_configuration(parent):
    # Obtiene el idioma seleccionado
    idioma = parent.language_menu.currentText()
    log_message('debug', f"Idioma seleccionado: {idioma}")

    if idioma == "Selecciona un idioma" or not idioma:
        show_status_message("Por favor, seleccione un idioma.", "error")
        parent.convert_button.setEnabled(False)
        log_message('warning', "Idioma no seleccionado.")
        return

    try:
        lang_module = importlib.import_module(f'lang.{idioma}')
        log_message('info', f"Módulo de idioma cargado: {idioma}")
    except ImportError as e:
        show_status_message(f"Error al cargar el módulo de idioma: {e}", "error")
        log_message('error', f"Error al cargar el módulo de idioma: {e}", exc_info=True)
        return

    try:
        country_map = lang_module.country_map
        gender_map = lang_module.gender_map
        style_map = lang_module.style_map
        voices_map = lang_module.voices_map
    except AttributeError as e:
        show_status_message(f"Error al acceder a los diccionarios del módulo: {e}", "error")
        log_message('error', f"Error al acceder a los diccionarios del módulo: {e}", exc_info=True)
        return

    selected_country = parent.country_menu.currentText()
    selected_gender = parent.gender_menu.currentText()
    selected_style = parent.style_menu.currentText()
    selected_voice = parent.voice_menu.currentText()
    log_message('debug', f"Selecciones: país={selected_country}, género={selected_gender}, estilo={selected_style}, voz={selected_voice}")

    if selected_country == "Selecciona un país" or not selected_country:
        show_status_message("Por favor, seleccione un país.", "error")
        parent.convert_button.setEnabled(False)
        log_message('warning', "País no seleccionado.")
        return

    if selected_gender == "Selecciona un género" or not selected_gender:
        show_status_message("Por favor, seleccione un género.", "error")
        parent.convert_button.setEnabled(False)
        log_message('warning', "Género no seleccionado.")
        return

    if selected_style == "Selecciona un estilo" or not selected_style:
        show_status_message("Por favor, seleccione un estilo.", "error")
        parent.convert_button.setEnabled(False)
        log_message('warning', "Estilo no seleccionado.")
        return

    if selected_voice == "Selecciona una voz" or not selected_voice:
        show_status_message("Por favor, seleccione una voz.", "error")
        parent.convert_button.setEnabled(False)
        log_message('warning', "Voz no seleccionada.")
        return

    speed_value = parent.speed_scale.value() / 100.0
    pitch_value = parent.pitch_scale.value()
    user_input_text = parent.text_entry.toPlainText()

    try:
        country_key = country_map[selected_country]
        gender_key = gender_map[selected_gender]
        style_key = style_map[selected_style]
        voice_key = voices_map[country_key][gender_key][style_key][selected_voice]
        voice_conf = f"{country_key}-{style_key}{voice_key}"
    except KeyError as e:
        show_status_message(f"Error al obtener la configuración de voz: {e}", "error")
        log_message('error', f"Error al obtener la configuración de voz: {e}", exc_info=True)
        return

    show_status_message("Verificando configuración...", "info")
    log_message('info', "Verificando configuración...")

    try:
        text = user_input_text
        voice_name = voice_conf
        country_id = country_key
        gender_mf = gender_key

        if not text:
            show_status_message("Campo de texto vacío", "error")
            parent.convert_button.setEnabled(False)
            log_message('warning', "Campo de texto vacío.")
            return

        show_status_message("Configuración de voz aceptada", "success")
        log_message('info', "Configuración de voz aceptada.")

        write('text_for_user.txt', text)
        write('voice_config.txt', voice_name)
        write('country_code.txt', country_id)
        write('gender.txt', gender_mf)
        write('speed.txt', str(speed_value))
        write('pitch.txt', str(pitch_value))

        show_status_message("Configuración verificada correctamente", "success")
        log_message('info', "Configuración verificada y archivos guardados correctamente.")

        parent.convert_button.setEnabled(True)
        parent.verify_button.setEnabled(True)

    except Exception as e:
        show_status_message("Error al guardar los archivos", "error")
        parent.convert_button.setEnabled(False)
        log_message('error', f"Error al guardar los archivos: {e}", exc_info=True)
