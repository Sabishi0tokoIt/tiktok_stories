# app/modules/audio/languages_update.py

from app.utils.debug import log_message

class LanguagesUpdater:
    def __init__(self):
        self.language_var = None
        self.country_var = None
        self.gender_var = None
        self.style_var = None
        self.voice_var = None

        self.country_map = {}
        self.gender_map = {}
        self.style_map = {}
        self.voices_map = {}

        # Registro inicial del estado
        log_message('debug', "LanguagesUpdater initialized with empty mappings.")

        try:
            # Asegurarse de que todos los mapas se inicialicen correctamente
            assert isinstance(self.country_map, dict), "country_map should be a dictionary."
            assert isinstance(self.gender_map, dict), "gender_map should be a dictionary."
            assert isinstance(self.style_map, dict), "style_map should be a dictionary."
            assert isinstance(self.voices_map, dict), "voices_map should be a dictionary."
            log_message('info', "Language mappings initialized as empty dictionaries.")

        except AssertionError as e:
            log_message('error', f"Initialization error: {e}", exc_info=True)
        except Exception as e:
            log_message('critical', f"Unexpected error during initialization: {e}", exc_info=True)

    def update_country_options(self):
        selected_language = self.language_var.currentText()
        log_message('info', f"Selected language: {selected_language}")

        try:
            # Intentar importar el módulo del idioma seleccionado
            lang_module = __import__(f'lang.{selected_language}',
                                     fromlist=['country_map', 'gender_map', 'style_map', 'voices_map'])
            log_message('info', f"Loaded language module for {selected_language}.")

            # Asignar mapas de país, género, estilo y voces
            self.country_map = lang_module.country_map
            self.gender_map = lang_module.gender_map
            self.style_map = lang_module.style_map
            self.voices_map = lang_module.voices_map
            log_message('debug', "Country, gender, style, and voices maps updated.")

            # Actualizar opciones de país
            country_options = list(self.country_map.keys())

            assert country_options, "Country options are empty after loading the language module."

            self.country_var.clear()
            self.country_var.addItem("Selecciona un país")
            index = self.country_var.findText("Selecciona un país")
            self.country_var.model().item(index).setEnabled(False)

            for country in country_options:
                self.country_var.addItem(country)
            self.country_var.setCurrentText("Selecciona un país")
            log_message('info', f"Updated country options: {country_options}")

            # Llamar a la función para actualizar las opciones de género
            self.update_gender_options()

        except ImportError as e:
            log_message('error', f"No se pudo cargar el módulo para el idioma '{selected_language}': {e}",
                        exc_info=True)
        except AssertionError as ae:
            log_message('warning', str(ae))  # Registro de advertencia si las opciones de país están vacías
        except Exception as e:
            log_message('error', f"Unexpected error in update_country_options: {e}", exc_info=True)

    def update_gender_options(self):
        try:
            # Obtener el país seleccionado
            country = self.country_var.currentText()
            log_message('info', f"Selected country: {country}")

            # Verificar si el país está en el mapa de países
            assert country in self.country_map, f"Country '{country}' not in country_map."

            # Obtener opciones de género
            gender_options = list(self.gender_map.keys())

            # Limpiar el menú de géneros y agregar la opción inicial
            self.gender_var.clear()
            self.gender_var.addItem("Selecciona un género")
            index = self.gender_var.findText("Selecciona un género")
            self.gender_var.model().item(index).setEnabled(False)

            # Agregar las opciones de género al menú
            for gender in gender_options:
                self.gender_var.addItem(gender)

            self.gender_var.setCurrentText("Selecciona un género")
            log_message('info', f"Updated gender options: {gender_options}")

            # Llamar a la función para actualizar las opciones de estilo
            self.update_style_options()

        except AssertionError as ae:
            log_message('warning', str(ae))  # Registro del mensaje de advertencia si la aserción falla
        except Exception as e:
            log_message('error', f"Error updating gender options: {e}", exc_info=True)

    def update_style_options(self):
        try:
            # Obtener valores de los menús desplegables
            country = self.country_var.currentText()
            gender = self.gender_var.currentText()
            log_message('info', f"Selected country: {country}, Selected gender: {gender}")

            # Verificar que el país y el género son válidos
            if country not in self.country_map or gender not in self.gender_map:
                log_message('warning', f"Country '{country}' or gender '{gender}' not found in mappings.")
                return

            country_code = self.country_map[country]
            gender_code = self.gender_map[gender]

            # Comprobar si hay voces disponibles para el país y género seleccionados
            if country_code not in self.voices_map or gender_code not in self.voices_map[country_code]:
                log_message('warning',
                            f"No voices found for country code '{country_code}' and gender code '{gender_code}'.")
                return

            style_options_in_english = list(self.voices_map[country_code][gender_code].keys())

            # Crear un mapa inverso de estilos
            reverse_style_map = {v: k for k, v in self.style_map.items()}

            # Obtener las opciones de estilo traducidas
            style_options = [reverse_style_map.get(style, style) for style in style_options_in_english]

            # Limpiar el menú de estilos y agregar opciones
            self.style_var.clear()
            self.style_var.addItem("Selecciona un estilo")
            index = self.style_var.findText("Selecciona un estilo")
            self.style_var.model().item(index).setEnabled(False)

            for style in style_options:
                self.style_var.addItem(style)

            self.style_var.setCurrentText("Selecciona un estilo")
            log_message('info', f"Updated style options: {style_options}")

        except Exception as e:
            log_message('error', f"Error updating style options: {e}", exc_info=True)

    def update_voice_options(self):
        try:
            # Obtener valores de los menús desplegables
            country = self.country_var.currentText()
            gender = self.gender_var.currentText()
            style = self.style_var.currentText()

            log_message('info', f"Selected country: {country}, gender: {gender}, style: {style}")

            # Verificar que el estilo es válido
            if style == "Selecciona un estilo" or style not in self.style_map:
                log_message('warning', f"Style '{style}' not selected or not in style_map.")
                return

            style_translated = self.style_map.get(style)
            if not style_translated:
                log_message('warning', f"Style '{style}' not found in style_map.")
                return

            # Verificar que el país y el género son válidos
            if country not in self.country_map or gender not in self.gender_map:
                log_message('warning', f"Country '{country}' or gender '{gender}' not found in mappings.")
                return

            country_code = self.country_map[country]
            gender_code = self.gender_map[gender]

            # Comprobar si hay voces disponibles para el país y género seleccionados
            if country_code not in self.voices_map or gender_code not in self.voices_map[country_code]:
                log_message('warning',
                            f"No voices found for country code '{country_code}' and gender code '{gender_code}'.")
                return

            if style_translated not in self.voices_map[country_code][gender_code]:
                log_message('warning',
                            f"Style '{style_translated}' not found for country code '{country_code}' and gender code '{gender_code}'.")
                return

            # Obtener opciones de voz y actualizar el menú de voces
            voice_options = list(self.voices_map[country_code][gender_code][style_translated].keys())

            # Limpiar el menú de voces y agregar opciones
            self.voice_var.clear()
            self.voice_var.addItem("Selecciona una voz")
            index = self.voice_var.findText("Selecciona una voz")
            self.voice_var.model().item(index).setEnabled(False)

            for voice in voice_options:
                self.voice_var.addItem(voice)

            self.voice_var.setCurrentText("Selecciona una voz")
            log_message('info', f"Updated voice options: {voice_options}")

        except Exception as e:
            log_message('error', f"Error updating voice options: {e}", exc_info=True)

    def bind_widgets(self, language_menu, country_menu, gender_menu, style_menu, voice_menu):
        try:
            # Aserción para verificar que los menús no sean None
            assert language_menu is not None, "language_menu no puede ser None."
            assert country_menu is not None, "country_menu no puede ser None."
            assert gender_menu is not None, "gender_menu no puede ser None."
            assert style_menu is not None, "style_menu no puede ser None."
            assert voice_menu is not None, "voice_menu no puede ser None."

            self.language_var = language_menu
            self.country_var = country_menu
            self.gender_var = gender_menu
            self.style_var = style_menu
            self.voice_var = voice_menu

            # Conectar señales a sus slots correspondientes
            self.language_var.currentIndexChanged.connect(self.update_country_options)
            self.country_var.currentIndexChanged.connect(self.update_gender_options)
            self.gender_var.currentIndexChanged.connect(self.update_style_options)
            self.style_var.currentIndexChanged.connect(self.update_voice_options)

            log_message('info', "Widgets vinculados a funciones de actualización.")

        except AssertionError as e:
            log_message('error', f"Error de aserción en bind_widgets: {e}", exc_info=True)
        except Exception as e:
            log_message('error', f"Error inesperado en bind_widgets: {e}", exc_info=True)
