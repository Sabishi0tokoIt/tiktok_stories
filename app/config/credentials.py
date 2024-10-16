# app/config/credentials.py

import os
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.cloud import texttospeech
from google.cloud import translate
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from app.utils.directories import get_project_root
from app.utils.debug import log_message, log_event_and_function


class GoogleCloudAPIManager:
    _instance = None  # Para implementar Singleton

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(GoogleCloudAPIManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):  # Evita la inicialización repetida
            log_message("info", "Inicializando OAuthCredentialsConfig...")

            self.root_path = os.path.join(get_project_root(), 'credentials')
            self.ensure_credentials_dir()

            self.credentials_path = os.path.join(self.root_path, 'credentials.json')
            self.token_path = os.path.join(self.root_path, 'token.json')
            self.creds = None
            self.client = None
            self.project_id = None

            # Inicializa los clientes de Google Cloud a None
            self.texttospeech_client = None
            self.translate_client = None

            self.scopes = ['https://www.googleapis.com/auth/cloud-platform']

            # Verificar y cargar credenciales/token
            self.check_token_and_auth()

            # Marcar como inicializado para el patrón Singleton
            self._initialized = True

    def ensure_credentials_dir(self):
        """Crea el directorio de credenciales si no existe."""
        if not os.path.exists(self.root_path):
            os.makedirs(self.root_path)
            log_message("info", f"Directorio de credenciales creado: {self.root_path}")

    @log_event_and_function("check_token_and_auth_event")
    def check_token_and_auth(self):
        """Verifica si existe un token válido, si no, inicia el flujo OAuth."""
        try:
            if os.path.exists(self.token_path):
                log_message("info", "Token existente encontrado, cargándolo...")
                self.creds = Credentials.from_authorized_user_file(self.token_path, self.scopes)

                if self.creds and self.creds.valid:
                    log_message("info", "Token válido, se omite la verificación de seguridad.")
                    return

                if self.creds.expired and self.creds.refresh_token:
                    log_message("info", "Token expirado, renovando...")
                    self.creds.refresh(Request())
                    log_message("info", "Token renovado exitosamente.")
                    self.save_token()
                    return
                else:
                    log_message("warning", "El token no es válido o no se puede renovar, iniciando flujo OAuth.")
            else:
                log_message("warning", "No se encontró un token, iniciando flujo OAuth.")

            self.auth_flow()

        except Exception as e:
            log_message("error", f"Error en el proceso de verificación de token: {e}", exc_info=True)

    @log_event_and_function("auth_flow_event")
    def auth_flow(self):
        """Inicia el flujo OAuth 2.0 para obtener nuevas credenciales."""
        if not os.path.exists(self.credentials_path):
            log_message("warning", "No se encontró archivo de credenciales, solicitando selección.")
            self.credentials_path = self.ask_for_credentials()
            if not self.credentials_path:
                log_message("error", "No se seleccionó un archivo de credenciales.")
                return

        flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, self.scopes)
        log_message("info", "Autenticando...")
        try:
            self.creds = flow.run_local_server(port=0)
            log_message("info", "Autenticación completada exitosamente.")
            self.save_token()
        except Exception as e:
            log_message("error", f"Error durante la autenticación: {e}", exc_info=True)

    @log_event_and_function("ask_for_credentils_event")
    def ask_for_credentials(self):
        """Solicita al usuario seleccionar el archivo de credenciales de OAuth."""
        options = QFileDialog.Options()
        credentials_file, _ = QFileDialog.getOpenFileName(
            None,
            "Seleccione el archivo de credenciales de OAuth",
            "",
            "JSON Files (*.json);;All Files (*)",
            options=options
        )
        if not credentials_file:
            QMessageBox.critical(None, "Error", "No se seleccionó un archivo de credenciales.")
            log_message("error", "No se seleccionó un archivo de credenciales.")
            return None
        log_message("info", f"Archivo de credenciales seleccionado: {credentials_file}")
        return credentials_file

    def save_token(self):
        """Guarda el token OAuth y el project_id en el directorio de credenciales."""
        if self.creds:
            try:
                with open(self.credentials_path, 'r') as f:
                    credentials_data = json.load(f)
                    self.project_id = credentials_data.get('installed', {}).get('project_id')
                    if not self.project_id:
                        log_message("warning", "No se encontró el 'project_id' en las credenciales.")

                with open(self.token_path, 'w') as token_file:
                    token_data = {
                        'token': self.creds.token,
                        'refresh_token': self.creds.refresh_token,
                        'token_uri': self.creds.token_uri,
                        'client_id': self.creds.client_id,
                        'client_secret': self.creds.client_secret,
                        'scopes': self.creds.scopes,
                        'project_id': self.project_id  # Guardamos el project_id aquí
                    }
                    json.dump(token_data, token_file)
                    log_message("info", f"Token y Project ID guardados en {self.token_path}")
            except Exception as e:
                log_message("error", f"Error al guardar el token: {e}", exc_info=True)

    def get_project_id(self):
        """Devuelve el project_id almacenado en el token."""
        if not self.project_id:
            if os.path.exists(self.token_path):
                try:
                    with open(self.token_path, 'r') as token_file:
                        token_data = json.load(token_file)
                        self.project_id = token_data.get('project_id')
                        log_message("info", f"Project ID obtenido del token: {self.project_id}")
                except Exception as e:
                    log_message("error", f"Error al cargar el project_id del token: {e}", exc_info=True)
            else:
                log_message("warning", "No se encontró el token.")
        return self.project_id

    def get_client(self, service):
        """Devuelve el cliente para el servicio de Google Cloud especificado."""
        assert self.creds, "No hay credenciales disponibles."
        log_message("info", f"Solicitando cliente para el servicio: {service}")

        try:
            if service == 'texttospeech':
                if self.texttospeech_client is None:
                    self.texttospeech_client = texttospeech.TextToSpeechClient(credentials=self.creds)
                    log_message("info", "Cliente Text-to-Speech creado exitosamente.")
                return self.texttospeech_client

            elif service == 'translate':
                if self.translate_client is None:
                    self.translate_client = translate.TranslationServiceClient(credentials=self.creds)
                    log_message("info", "Cliente Translation creado exitosamente.")
                return self.translate_client

            else:
                log_message("warning", f"Servicio '{service}' no soportado.")
                return None

        except Exception as e:
            log_message("error", f"Error al obtener el cliente para el servicio '{service}': {e}", exc_info=True)
            return None
