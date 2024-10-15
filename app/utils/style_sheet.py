# app/utils/style_sheet.py

def dark_theme():
    return """
        QWidget {
            background-color: #242424;
            color: #ffffff;
        }
        QMainWindow {
            background-color: #242424;
            color: #ffffff;
        }
        QLabel {
            color: #ffffff;
        }
        QPushButton {
            background-color: #333333;
            color: #ffffff;
            border: 1px solid #555555;
            padding: 10px;
            border-radius: 5px;
        }
        #status_widget {
            background-color: #333333;
            border: 1px solid #555555;
            border-radius: 5px;
        }
        QPushButton:hover {
            background-color: #555555;
        }
        QLineEdit {
            background-color: #333333;
            color: #ffffff;
            border: 1px solid #555555;
        }
        QTextEdit {
            background-color: #333333;
            color: #ffffff;
            border: 1px solid #555555;
            border-radius: 5px;

        }
        QComboBox {
            background-color: #333333;
            color: #ffffff;
            border: 1px solid #555555;
            border-radius: 5px;
        }
        QMenuBar {
            background-color: #222222;
            color: #ffffff;
            
        }
        QMenu {
            background-color: #222222;
            color: #ffffff;
            border: 1px solid #555555;
            border-radius: 5px;
        }
        QMenu::item {
            padding: 5px 20px;
        }

        QMenu::item:selected {
            background-color: #333333;
        }

        QMenu::item:hover {
            background-color: #333333;
            color: #ffffff;
        }
        QScrollBar {
            background-color: #222222;
        }
        QCheckBox, QRadioButton {
            color: #ffffff;
        }
        QToolTip {
            background-color: #e6f1ff;
            color: #0078d7;
            border: 1px solid #0078d7;
        }
    """

def light_theme():
    return """
        QWidget {
            background-color: #ffffff;
            color: #000000;
        }
        QMainWindow {
            background-color: #ffffff;
        }
        QLabel {
            color: #000000;
        }
        QPushButton {
            background-color: #f0f0f0;
            color: #000000;
            border: 1px solid #cccccc;
            padding: 5px;
        }
        QPushButton:hover {
            background-color: #dddddd;
        }
        QLineEdit {
            background-color: #ffffff;
            color: #000000;
            border: 1px solid #cccccc;
        }
        QTextEdit {
            background-color: #ffffff;
            color: #000000;
            border: 1px solid #cccccc;
        }
        QComboBox {
            background-color: #ffffff;
            color: #000000;
            border: 1px solid #cccccc;
        }
        QMenuBar {
            background-color: #f0f0f0;
            color: #000000;
            border-radius: 5px;
        }
        QMenu {
            background-color: #f0f0f0;
            color: #000000;
            border-radius: 5px;
        }
        QScrollBar {
            background-color: #f0f0f0;
        }
        QCheckBox, QRadioButton {
            color: #000000;
        }
        
    """

def minimalist_white_blue_theme():
    return """
        QWidget {
            background-color: #ffffff;
            color: #0078d7;
        }
        QMainWindow {
            background-color: #ffffff;
        }
        QLabel {
            color: #0078d7;
            font-weight: bold;
        }
        QPushButton {
            background-color: #e6f1ff;
            color: #0078d7;
            border: 1px solid #0078d7;
            padding: 8px;
        }
        QPushButton:hover {
            background-color: #0078d7;
            color: #ffffff;
        }
        QLineEdit {
            background-color: #ffffff;
            color: #0078d7;
            border: 1px solid #0078d7;
        }
        QTextEdit {
            background-color: #ffffff;
            color: #0078d7;
            border: 1px solid #0078d7;
        }
        QComboBox {
            background-color: #ffffff;
            color: #0078d7;
            border: 1px solid #0078d7;
        }
        QMenuBar {
            background-color: #e6f1ff;
            color: #0078d7;
        }
        QMenu {
            background-color: #e6f1ff;
            color: #0078d7;
        }
        QScrollBar {
            background-color: #e6f1ff;
        }
        QCheckBox, QRadioButton {
            color: #0078d7;
        }
        QToolTip {
            background-color: #e6f1ff;
            color: #0078d7;
            border: 1px solid #0078d7;
        }
    """

def retro_orange_theme():
    return """
        QWidget {
            background-color: #000000;
            color: #ff8800;
        }
        QMainWindow {
            background-color: #000000;
        }
        QLabel {
            color: #ff8800;
            font-weight: bold;
        }
        QPushButton {
            background-color: #222222;
            color: #ff8800;
            border: 1px solid #ff8800;
            padding: 8px;
        }
        QPushButton:hover {
            background-color: #ff8800;
            color: #000000;
        }
        QLineEdit {
            background-color: #222222;
            color: #ff8800;
            border: 1px solid #ff8800;
        }
        QTextEdit {
            background-color: #222222;
            color: #ff8800;
            border: 1px solid #ff8800;
        }
        QComboBox {
            background-color: #222222;
            color: #ff8800;
            border: 1px solid #ff8800;
        }
        QMenuBar {
            background-color: #000000;
            color: #ff8800;
        }
        QMenu {
            background-color: #000000;
            color: #ff8800;
        }
        QScrollBar {
            background-color: #222222;
        }
        QCheckBox, QRadioButton {
            color: #ff8800;
        }
        QToolTip {
            background-color: #222222;
            color: #ff8800;
            border: 1px solid #ff8800;
        }
    """

def neon_green_dark_theme():
    return """
        QWidget {
            background-color: #0d0d0d;
            color: #00ff00;
        }
        QMainWindow {
            background-color: #0d0d0d;
        }
        QLabel {
            color: #00ff00;
            font-weight: bold;
        }
        QPushButton {
            background-color: #1a1a1a;
            color: #00ff00;
            border: 1px solid #00ff00;
            padding: 8px;
        }
        QPushButton:hover {
            background-color: #00ff00;
            color: #000000;
        }
        QLineEdit {
            background-color: #1a1a1a;
            color: #00ff00;
            border: 1px solid #00ff00;
        }
        QTextEdit {
            background-color: #1a1a1a;
            color: #00ff00;
            border: 1px solid #00ff00;
        }
        QComboBox {
            background-color: #1a1a1a;
            color: #00ff00;
            border: 1px solid #00ff00;
        }
        QMenuBar {
            background-color: #0d0d0d;
            color: #00ff00;
        }
        QMenu {
            background-color: #0d0d0d;
            color: #00ff00;
        }
        QScrollBar {
            background-color: #1a1a1a;
        }
        QCheckBox, QRadioButton {
            color: #00ff00;
        }
        QToolTip {
            background-color: #1a1a1a;
            color: #00ff00;
            border: 1px solid #00ff00;
        }
    """

def elegant_dark_blue_theme():
    return """
        QWidget {
            background-color: #1e1e2f;
            color: #e0e0e0;
        }
        QMainWindow {
            background-color: #1e1e2f;
        }
        QLabel {
            color: #f0f0f0;
            font-weight: bold;
        }
        QPushButton {
            background-color: #2c2f4a;
            color: #a3c9f7;
            border: 1px solid #3a3f5c;
            padding: 8px;
        }
        QPushButton:hover {
            background-color: #404768;
        }
        QLineEdit {
            background-color: #2a2d46;
            color: #e0e0e0;
            border: 1px solid #4a4f76;
        }
        QTextEdit {
            background-color: #2a2d46;
            color: #e0e0e0;
            border: 1px solid #4a4f76;
        }
        QComboBox {
            background-color: #2a2d46;
            color: #e0e0e0;
            border: 1px solid #4a4f76;
        }
        QMenuBar {
            background-color: #1c1f32;
            color: #a3c9f7;
        }
        QMenu {
            background-color: #1c1f32;
            color: #a3c9f7;
        }
        QScrollBar {
            background-color: #2a2d46;
        }
        QCheckBox, QRadioButton {
            color: #a3c9f7;
        }
        QToolTip {
            background-color: #2a2d46;
            color: #ffffff;
            border: 1px solid #3a3f5c;
        }
    """


