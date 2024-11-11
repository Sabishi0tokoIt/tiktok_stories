# start.py

import os
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from app.utils.directories import get_project_root,  get_images_dir
from app.utils.debug import log_message
from app.utils.style_sheet import dark_theme
# Obtener la ruta raíz del proyecto
project_root = get_project_root()
images_dir_path = get_images_dir()

# Combinar la ruta raíz con la ruta de la imagen
image_path = os.path.join(images_dir_path, 'fondo.jpg')


class MainApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ventana Principal")

        # Eliminar la barra de título
        self.setWindowFlag(Qt.FramelessWindowHint)

        # Bloquear el tamaño de la ventana a 600x400
        self.setFixedSize(600, 400)

        self.setStyleSheet(dark_theme())

        # Centrar la ventana
        self.center_window()

        # Cargar la imagen y aplicarla como fondo
        self.load_background_image(image_path)

        # Crear botones directamente en la ventana principal
        self.create_buttons()

    def center_window(self):
        """Centra la ventana en la pantalla."""
        screen_rect = self.frameGeometry()
        screen_center = QApplication.desktop().availableGeometry().center()
        screen_rect.moveCenter(screen_center)
        self.move(screen_rect.topLeft())
        log_message("success", "Ventana centrada en la pantalla.")

    def load_background_image(self, image_path):
        """Carga la imagen de fondo en la ventana."""
        try:
            assert os.path.exists(image_path), f"La ruta de la imagen no existe: {image_path}"
            self.background_label = QLabel(self)
            pixmap = QPixmap(image_path).scaled(self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)

            self.background_label.setPixmap(pixmap)
            self.background_label.setScaledContents(True)
            self.background_label.setGeometry(self.rect())
            self.background_label.raise_()  # Asegura que la etiqueta esté detrás de otros widgets

            log_message("success", "Imagen de fondo cargada correctamente.")

        except AssertionError as ae:
            log_message("error", f"Error de aserción: {ae}", exc_info=True)
        except Exception as e:
            log_message("error", f"Error al cargar la imagen de fondo: {e}", exc_info=True)

    def create_buttons(self):
        """Crea y establece los botones en la ventana."""
        layout = QVBoxLayout(self)

        # Botón AUDIO
        self.start = QPushButton("INICIAR")

        self.start.setFixedSize(200, 50)
        self.start.setCursor(Qt.PointingHandCursor)
        self.start.clicked.connect(self.start_action)
        layout.addWidget(self.start)

        layout.setAlignment(Qt.AlignCenter)
        self.setLayout(layout)
        log_message("success", "Botones creados y layout establecido.")

    def start_action(self):
        """Acción ejecutada al presionar el botón INICIAR."""
        log_message("info", "Botón INICIAR presionado.")
        self.hide()

        try:
            # Importar y ejecutar la aplicación de gui.py
            from app.gui import TikTokStoriesApp
            self.new_app = TikTokStoriesApp()
            self.new_app.show()
            log_message("success", "Nueva aplicación TikTokStoriesApp mostrada.")
        except ImportError as ie:
            log_message("error", f"Error al importar TikTokStoriesApp: {ie}", exc_info=True)
        except Exception as e:
            log_message("success", f"Error al iniciar la aplicación TikTokStoriesApp: {e}", exc_info=True)

    def keyPressEvent(self, event):
        """Sobreescribe el evento de teclas para detectar la tecla Enter."""
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            log_message("info", "Tecla Enter presionada, ejecutando acción del botón INICIAR.")
            self.start_action()  # Ejecutar la acción del botón INICIAR cuando se presiona Enter


if __name__ == "__main__":
    app = QApplication([])
    main_app = MainApp()
    main_app.show()
    log_message("info", "Aplicación principal iniciada.")
    app.exec_()
