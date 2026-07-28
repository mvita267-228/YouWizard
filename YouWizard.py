#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouWizard - Minimalist YouTube Downloader (PyQt6)
"""

import sys
import os
import json
import subprocess
import shutil
from pathlib import Path

# Скрытие консольного окна (для Windows)
if sys.platform == 'win32':
    import ctypes
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

try:
    from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                                 QHBoxLayout, QLineEdit, QPushButton, QLabel, 
                                 QComboBox, QProgressBar, QMessageBox, QFileDialog,
                                 QDialog, QFrame)
    from PyQt6.QtCore import Qt, QThread, pyqtSignal
    from PyQt6.QtGui import QFont
except ImportError:
    print("Ошибка: PyQt6 не установлен. Установите его командой: pip install PyQt6")
    sys.exit(1)

# Конфигурация
APP_NAME = "YouWizard"
SETTINGS_FILE = Path("settings.json")
INSTALL_DIR = Path("bin")

# Словарь переводов
TRANSLATIONS = {
    'en': {
        'title': 'YouWizard',
        'url_placeholder': 'Paste video URL here...',
        'format_video': 'Video (MP4)',
        'format_audio': 'Audio (MP3)',
        'btn_download': 'Download',
        'btn_browse': '...',
        'status_ready': 'Ready',
        'status_downloading': 'Downloading...',
        'status_done': 'Done!',
        'status_error': 'Error',
        'first_run_title': 'Setup',
        'first_run_msg': 'Downloading essential tools...',
        'select_folder': 'Select Download Folder'
    },
    'ru': {
        'title': 'YouWizard',
        'url_placeholder': 'Вставьте ссылку на видео...',
        'format_video': 'Видео (MP4)',
        'format_audio': 'Аудио (MP3)',
        'btn_download': 'Скачать',
        'btn_browse': '...',
        'status_ready': 'Готов',
        'status_downloading': 'Загрузка...',
        'status_done': 'Готово!',
        'status_error': 'Ошибка',
        'first_run_title': 'Настройка',
        'first_run_msg': 'Загрузка инструментов...',
        'select_folder': 'Выберите папку для загрузки'
    }
}

class ToolsInstaller(QThread):
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(bool)

    def run(self):
        try:
            INSTALL_DIR.mkdir(exist_ok=True)
            
            # 1. Установка yt-dlp
            self.progress.emit(10, "Downloading yt-dlp...")
            yt_dlp_path = INSTALL_DIR / ("yt-dlp.exe" if sys.platform == 'win32' else "yt-dlp")
            
            import urllib.request
            yt_url = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe" if sys.platform == 'win32' else "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp"
            
            if not yt_dlp_path.exists():
                urllib.request.urlretrieve(yt_url, yt_dlp_path)
            
            # 2. Установка FFmpeg (облегченная версия)
            self.progress.emit(50, "Downloading ffmpeg-lite...")
            if sys.platform == 'win32':
                # Используем zip с только необходимыми файлами
                ff_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl-shared.zip"
                zip_path = INSTALL_DIR / "ffmpeg.zip"
                
                try:
                    urllib.request.urlretrieve(ff_url, zip_path)
                    self.progress.emit(70, "Extracting ffmpeg...")
                    
                    import zipfile
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        for file in zip_ref.namelist():
                            if file.endswith("bin/ffmpeg.exe"):
                                zip_ref.extract(file, INSTALL_DIR)
                                src = INSTALL_DIR / file
                                dst = INSTALL_DIR / "ffmpeg.exe"
                                shutil.move(src, dst)
                                break
                    
                    zip_path.unlink()
                except Exception as e:
                    print(f"FFmpeg download warning: {e}")
                    # Продолжаем даже если ffmpeg не загрузился

            self.progress.emit(100, "Done")
            self.finished.emit(True)
        except Exception as e:
            print(f"Install error: {e}")
            self.finished.emit(False)

class Worker(QThread):
    progress = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, url, output_template, format_type, bin_path):
        super().__init__()
        self.url = url
        self.output_template = output_template
        self.format_type = format_type
        self.bin_path = str(bin_path)

    def run(self):
        try:
            cmd = [
                os.path.join(self.bin_path, "yt-dlp.exe" if sys.platform == 'win32' else "yt-dlp"),
                '--ffmpeg-location', os.path.join(self.bin_path, "ffmpeg.exe" if sys.platform == 'win32' else "ffmpeg"),
                '-o', self.output_template,
                '--no-warnings',
                '--newline'
            ]

            if self.format_type == 'audio':
                cmd.extend(['-x', '--audio-format', 'mp3', '--audio-quality', '0'])
            else:
                cmd.extend(['-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'])

            process = subprocess.Popen(
                cmd + [self.url],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )

            for line in process.stdout:
                if '[download]' in line or 'Destination' in line:
                    self.progress.emit(line.strip())
            
            process.wait()
            if process.returncode == 0:
                self.finished.emit(True, "Success")
            else:
                self.finished.emit(False, "Error occurred")
                
        except Exception as e:
            self.finished.emit(False, str(e))

class FirstRunDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMinimumWidth(300)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #2b2b2b;
                border-radius: 15px;
                padding: 20px;
                color: white;
            }
        """)
        card_layout = QVBoxLayout(card)
        
        title = QLabel("⚙️ Setup")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        msg = QLabel("Downloading essential tools...\nPlease wait.")
        msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        msg.setStyleSheet("color: #aaaaaa; margin-top: 10px;")
        
        self.bar = QProgressBar()
        self.bar.setTextVisible(False)
        self.bar.setFixedHeight(6)
        self.bar.setStyleSheet("""
            QProgressBar {
                background-color: #444;
                border-radius: 3px;
            }
            QProgressBar::chunk {
                background-color: #bb86fc;
                border-radius: 3px;
            }
        """)
        
        card_layout.addWidget(title)
        card_layout.addWidget(msg)
        card_layout.addWidget(self.bar)
        
        layout.addWidget(card)
        
    def set_progress(self, val, text):
        self.bar.setValue(val)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = self.load_settings()
        self.lang = self.settings.get('language', 'ru')
        self.t = TRANSLATIONS[self.lang]
        
        self.init_ui()
        self.check_tools()

    def load_settings(self):
        if SETTINGS_FILE.exists():
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {'first_run': True, 'language': 'ru', 'last_dir': str(Path.home())}

    def save_settings(self):
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.settings, f)

    def init_ui(self):
        self.setWindowTitle(self.t['title'])
        self.setMinimumSize(450, 250)
        self.setMaximumSize(600, 400)
        
        self.setStyleSheet("""
            QMainWindow {
                background-color: #121212;
            }
            QWidget {
                background-color: #121212;
                color: #ffffff;
                font-family: 'Segoe UI', sans-serif;
            }
            QLineEdit {
                background-color: #1e1e1e;
                border: 1px solid #333;
                border-radius: 8px;
                padding: 12px;
                color: white;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #bb86fc;
            }
            QPushButton {
                background-color: #bb86fc;
                color: #000;
                border: none;
                border-radius: 8px;
                padding: 12px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #9965f4;
            }
            QPushButton:pressed {
                background-color: #7c4dff;
            }
            QComboBox {
                background-color: #1e1e1e;
                border: 1px solid #333;
                border-radius: 8px;
                padding: 10px;
                color: white;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox QAbstractItemView {
                background-color: #1e1e1e;
                border: 1px solid #333;
                selection-background-color: #bb86fc;
                color: white;
            }
            QLabel {
                color: #888;
                font-size: 12px;
            }
            QProgressBar {
                background-color: #1e1e1e;
                border-radius: 4px;
                height: 4px;
                border: none;
            }
            QProgressBar::chunk {
                background-color: #03dac6;
                border-radius: 4px;
            }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        header = QLabel("🎬 YouWizard")
        header.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        header.setStyleSheet("color: #bb86fc; margin-bottom: 10px;")
        layout.addWidget(header)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText(self.t['url_placeholder'])
        layout.addWidget(self.url_input)

        settings_layout = QHBoxLayout()
        settings_layout.setSpacing(15)
        
        self.format_combo = QComboBox()
        self.format_combo.addItems([self.t['format_video'], self.t['format_audio']])
        self.format_combo.setCurrentIndex(0)
        settings_layout.addWidget(self.format_combo, 2)
        
        self.browse_btn = QPushButton(self.t['btn_browse'])
        self.browse_btn.setFixedWidth(50)
        self.browse_btn.clicked.connect(self.browse_folder)
        settings_layout.addWidget(self.browse_btn)
        
        layout.addLayout(settings_layout)

        self.download_btn = QPushButton(f"📥 {self.t['btn_download']}")
        self.download_btn.setFixedHeight(50)
        self.download_btn.clicked.connect(self.start_download)
        layout.addWidget(self.download_btn)

        self.status_label = QLabel(self.t['status_ready'])
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

    def check_tools(self):
        if self.settings.get('first_run', True):
            self.install_dialog = FirstRunDialog(self)
            self.install_dialog.show()
            
            self.installer = ToolsInstaller()
            self.installer.progress.connect(lambda v, t: self.install_dialog.set_progress(v, t))
            self.installer.finished.connect(self.on_install_finished)
            self.installer.start()
        else:
            if not (INSTALL_DIR / "yt-dlp.exe").exists():
                 self.settings['first_run'] = True
                 self.save_settings()
                 self.check_tools()

    def on_install_finished(self, success):
        self.install_dialog.close()
        if success:
            self.settings['first_run'] = False
            self.save_settings()
            self.status_label.setText("✅ Ready")
        else:
            QMessageBox.critical(self, "Error", "Failed to install tools. Check internet connection.")

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, self.t['select_folder'], self.settings.get('last_dir', ''))
        if folder:
            self.settings['last_dir'] = folder
            self.save_settings()

    def start_download(self):
        url = self.url_input.text().strip()
        if not url:
            return
        
        self.download_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText(self.t['status_downloading'])
        
        fmt = 'audio' if self.format_combo.currentIndex() == 1 else 'video'
        out_template = os.path.join(self.settings.get('last_dir', '.'), '%(title)s.%(ext)s')
        
        self.worker = Worker(url, out_template, fmt, INSTALL_DIR)
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.on_download_finished)
        self.worker.start()

    def update_progress(self, text):
        if '%' in text:
            try:
                percent = float(text.split('%')[0].split()[-1])
                self.progress_bar.setValue(int(percent))
            except:
                pass
        self.status_label.setText(text[:50] + "..." if len(text) > 50 else text)

    def on_download_finished(self, success, msg):
        self.download_btn.setEnabled(True)
        if success:
            self.status_label.setText(self.t['status_done'])
            self.progress_bar.setValue(100)
        else:
            self.status_label.setText(f"{self.t['status_error']}: {msg}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
