# app/__init__.py
from .config.lang import generate_languages_file
def initialize_app():
    # Generar el archivo 'languages.py' con la lista de idiomas disponibles
    generate_languages_file()

initialize_app()
