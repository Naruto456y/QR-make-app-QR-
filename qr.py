import sys
import os
import time
import qrcode
import subprocess
import platform
from PIL import Image
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLineEdit, QPushButton, QLabel, 
                             QProgressBar, QMessageBox, QFrame)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QFont, QPalette, QColor

class QRThread(QThread):
    finished = pyqtSignal(object, str, str)
    error = pyqtSignal(str)
    
    def __init__(self, url):
        super().__init__()
        self.url = url
        
    def run(self):
        try:
            img = qrcode.make(self.url)
            name = f"qr_{int(time.time())}.png"
            
            qr_folder = "QR_Codes"
            if not os.path.exists(qr_folder):
                os.mkdir(qr_folder)
            
            file_path = os.path.join(qr_folder, name)
            img.save(file_path)
            
            self.finished.emit(img, name, file_path)
        except Exception as e:
            self.error.emit(str(e))

class QRGeneratorPyQt(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_directory = os.getcwd()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Генератор QR-кодов")
        self.setFixedSize(500, 650)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2c3e50;
            }
            QFrame {
                background-color: #34495e;
                border-radius: 10px;
            }
            QLineEdit {
                background-color: #2c3e50;
                color: #ecf0f1;
                border: 2px solid #3498db;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
            }
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
            QPushButton#clear {
                background-color: #e67e22;
            }
            QPushButton#clear:hover {
                background-color: #f39c12;
            }
            QPushButton#folder {
                background-color: #2980b9;
            }
            QPushButton#folder:hover {
                background-color: #3498db;
            }
            QLabel {
                color: #ecf0f1;
            }
            QProgressBar {
                border: 2px solid #34495e;
                border-radius: 5px;
                text-align: center;
                color: white;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 3px;
            }
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)
        
        # Заголовок
        title = QLabel("Генератор QR-кодов")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 20, QFont.Bold))
        layout.addWidget(title)
        
        subtitle = QLabel("Введите ссылку или текст для создания QR-кода")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setFont(QFont("Arial", 11))
        subtitle.setStyleSheet("color: #bdc3c7;")
        layout.addWidget(subtitle)
        
        # Поле ввода
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Введите ссылку или текст здесь...")
        self.url_input.returnPressed.connect(self.generate_qr)
        layout.addWidget(self.url_input)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        
        self.generate_btn = QPushButton("Сгенерировать QR-код")
        self.generate_btn.clicked.connect(self.generate_qr)
        self.generate_btn.setFixedHeight(40)
        buttons_layout.addWidget(self.generate_btn)
        
        self.clear_btn = QPushButton("Очистить")
        self.clear_btn.setObjectName("clear")
        self.clear_btn.clicked.connect(self.clear_field)
        self.clear_btn.setFixedHeight(40)
        buttons_layout.addWidget(self.clear_btn)
        
        layout.addLayout(buttons_layout)
        
        # Статус
        self.status_label = QLabel("Готов к генерации")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFont(QFont("Arial", 10, QFont.Bold))
        self.status_label.setStyleSheet("color: #3498db;")
        layout.addWidget(self.status_label)
        
        # Прогресс-бар
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Превью
        preview_label = QLabel("Предпросмотр QR-кода:")
        preview_label.setAlignment(Qt.AlignCenter)
        preview_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(preview_label)
        
        self.preview_frame = QFrame()
        self.preview_frame.setFixedSize(200, 200)
        self.preview_frame.setStyleSheet("background-color: #34495e; border: 2px dashed #7f8c8d;")
        
        preview_layout = QVBoxLayout(self.preview_frame)
        self.qr_preview = QLabel("QR-код появится здесь")
        self.qr_preview.setAlignment(Qt.AlignCenter)
        self.qr_preview.setStyleSheet("color: #95a5a6; font-size: 12px;")
        preview_layout.addWidget(self.qr_preview)
        
        layout.addWidget(self.preview_frame, alignment=Qt.AlignCenter)
        
        # Информация
        info_label = QLabel("Файлы сохраняются в папке QR_Codes")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("color: #7f8c8d; font-size: 10px;")
        layout.addWidget(info_label)
        
        # Кнопка открытия папки
        self.folder_btn = QPushButton("📁 Открыть папку с QR-кодами")
        self.folder_btn.setObjectName("folder")
        self.folder_btn.clicked.connect(self.open_qr_folder)
        self.folder_btn.setFixedHeight(35)
        layout.addWidget(self.folder_btn)
        
        layout.addStretch()
        
    def clear_field(self):
        self.url_input.clear()
        self.url_input.setFocus()
        
    def generate_qr(self):
        url = self.url_input.text().strip()
        
        if not url:
            QMessageBox.warning(self, "Внимание", "Пожалуйста, введите ссылку или текст!")
            self.url_input.setFocus()
            return
            
        self.generate_btn.setEnabled(False)
        self.status_label.setText("Генерируем QR-код...")
        self.status_label.setStyleSheet("color: #f39c12;")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # indeterminate progress
        
        self.thread = QRThread(url)
        self.thread.finished.connect(self.on_generation_finished)
        self.thread.error.connect(self.on_generation_error)
        self.thread.start()
        
    def on_generation_finished(self, img, name, file_path):
        self.generate_btn.setEnabled(True)
        self.status_label.setText("QR-код успешно сгенерирован!")
        self.status_label.setStyleSheet("color: #2ecc71;")
        self.progress_bar.setVisible(False)
        
        # Сохраняем превью
        preview_path = "temp_preview.png"
        img.save(preview_path)
        
        pixmap = QPixmap(preview_path)
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(180, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.qr_preview.setPixmap(scaled_pixmap)
            self.qr_preview.setText("")
        
        # Открываем файл
        try:
            if platform.system() == 'Windows':
                os.startfile(file_path)
            elif platform.system() == 'Darwin':
                subprocess.run(['open', file_path])
            else:
                subprocess.run(['xdg-open', file_path])
        except:
            pass
            
        # Очищаем поле
        self.clear_field()
        
    def on_generation_error(self, error_msg):
        self.generate_btn.setEnabled(True)
        self.status_label.setText("Ошибка генерации!")
        self.status_label.setStyleSheet("color: #e74c3c;")
        self.progress_bar.setVisible(False)
        QMessageBox.critical(self, "Ошибка", f"Произошла ошибка:\n{error_msg}")
        self.url_input.setFocus()
        
    def open_qr_folder(self):
        folder_path = os.path.join(self.current_directory, "QR_Codes")
        if os.path.exists(folder_path):
            try:
                if platform.system() == 'Windows':
                    os.startfile(folder_path)
                elif platform.system() == 'Darwin':
                    subprocess.run(['open', folder_path])
                else:
                    subprocess.run(['xdg-open', folder_path])
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось открыть папку:\n{e}")
        else:
            QMessageBox.information(self, "Информация", "Папка QR_Codes еще не создана. Сгенерируйте первый QR-код!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QRGeneratorPyQt()
    window.show()
    sys.exit(app.exec_())