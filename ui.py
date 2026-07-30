#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouWizard - UI Module
Contains all UI components: dialogs, main window, and custom widgets.
"""

import sys
import os
from pathlib import Path

try:
    from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                                 QHBoxLayout, QLineEdit, QPushButton, QLabel, 
                                 QComboBox, QProgressBar, QMessageBox, QFileDialog,
                                 QDialog, QFrame, QRadioButton, QButtonGroup)
    from PyQt6.QtCore import Qt, QPoint
    from PyQt6.QtGui import QFont, QCursor
except ImportError:
    print("Ошибка: PyQt6 не установлен. Установите его командой: pip install PyQt6")
    sys.exit(1)

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
        'select_folder': 'Select Download Folder',
        'select_language': 'Select Language',
        'language_en': 'English',
        'language_ru': 'Russian',
        'btn_start': 'Start Setup',
        'downloading_tools': 'Downloading essential tools...\nPlease wait.',
        'installing_ffmpeg': 'Installing full FFmpeg...',
        'tools_ready': 'Tools installed successfully!',
        'quality_label': 'Quality:',
        'quality_best': 'Best',
        'quality_1080': '1080p',
        'quality_720': '720p',
        'quality_480': '480p',
        'quality_360': '360p'
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
        'select_folder': 'Выберите папку для загрузки',
        'select_language': 'Выберите язык',
        'language_en': 'Английский',
        'language_ru': 'Русский',
        'btn_start': 'Начать настройку',
        'downloading_tools': 'Загрузка инструментов...\nПожалуйста, подождите.',
        'installing_ffmpeg': 'Установка полной версии FFmpeg...',
        'tools_ready': 'Инструменты установлены успешно!',
        'quality_label': 'Качество:',
        'quality_best': 'Лучшее',
        'quality_1080': '1080p',
        'quality_720': '720p',
        'quality_480': '480p',
        'quality_360': '360p'
    }
}


class LanguageSelectionDialog(QDialog):
    """Диалог выбора языка при первом запуске."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMinimumWidth(350)
        self.selected_language = 'ru'  # По умолчанию русский
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #2b2b2b;
                border-radius: 15px;
                padding: 25px;
                color: white;
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(15)
        
        title = QLabel("🌍 Select Language / Выберите язык")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Группа кнопок
        self.lang_group = QButtonGroup(self)
        
        # English radio button
        self.en_radio = QRadioButton("English")
        self.en_radio.setStyleSheet("""
            QRadioButton {
                color: #ffffff;
                font-size: 14px;
                spacing: 10px;
            }
            QRadioButton::indicator {
                width: 20px;
                height: 20px;
                border-radius: 10px;
                border: 2px solid #555;
                background-color: #333;
            }
            QRadioButton::indicator:checked {
                background-color: #bb86fc;
                border: 2px solid #bb86fc;
            }
        """)
        self.en_radio.setChecked(False)
        
        # Russian radio button
        self.ru_radio = QRadioButton("Русский")
        self.ru_radio.setStyleSheet("""
            QRadioButton {
                color: #ffffff;
                font-size: 14px;
                spacing: 10px;
            }
            QRadioButton::indicator {
                width: 20px;
                height: 20px;
                border-radius: 10px;
                border: 2px solid #555;
                background-color: #333;
            }
            QRadioButton::indicator:checked {
                background-color: #bb86fc;
                border: 2px solid #bb86fc;
            }
        """)
        self.ru_radio.setChecked(True)
        
        self.lang_group.addButton(self.en_radio)
        self.lang_group.addButton(self.ru_radio)
        
        # Кнопка старта
        self.start_btn = QPushButton("Start Setup / Начать настройку")
        self.start_btn.setStyleSheet("""
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
        """)
        self.start_btn.clicked.connect(self.accept)
        
        card_layout.addWidget(title)
        card_layout.addWidget(self.en_radio)
        card_layout.addWidget(self.ru_radio)
        card_layout.addWidget(self.start_btn)
        
        layout.addWidget(card)
    
    def get_selected_language(self):
        if self.en_radio.isChecked():
            return 'en'
        return 'ru'


class FirstRunDialog(QDialog):
    """Диалог первого запуска с прогрессом установки."""
    def __init__(self, language='ru', parent=None):
        super().__init__(parent)
        # Делаем диалог модальным окном с обычными рамками
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowTitleHint)
        self.setModal(True)
        self.setMinimumWidth(350)
        self.setMinimumHeight(200)
        self.language = language
        self.t = TRANSLATIONS[self.language]
        self.setWindowTitle(self.t['first_run_title'])
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        title = QLabel("⚙️ " + self.t['first_run_title'])
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        msg = QLabel(self.t['downloading_tools'])
        msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        msg.setWordWrap(True)
        msg.setStyleSheet("color: #aaaaaa; margin-top: 10px; font-size: 13px;")
        
        self.bar = QProgressBar()
        self.bar.setTextVisible(False)
        self.bar.setFixedHeight(8)
        self.bar.setStyleSheet("""
            QProgressBar {
                background-color: #444;
                border-radius: 4px;
            }
            QProgressBar::chunk {
                background-color: #bb86fc;
                border-radius: 4px;
            }
        """)
        
        self.status_text = QLabel("")
        self.status_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_text.setStyleSheet("color: #888; font-size: 11px;")
        
        layout.addWidget(title)
        layout.addWidget(msg)
        layout.addWidget(self.bar)
        layout.addWidget(self.status_text)
        
    def set_progress(self, val, text):
        self.bar.setValue(val)
        self.status_text.setText(text)


class MainWindow(QMainWindow):
    """Главное окно приложения."""
    def __init__(self, language='ru', logic_module=None):
        super().__init__()
        self.logic = logic_module
        self.settings = self.logic.load_settings(Path("settings.json")) if self.logic else {'first_run': True, 'language': 'ru', 'last_dir': str(Path.home())}
        
        # Используем переданный язык или сохраняем из настроек
        if 'language' not in self.settings:
            self.settings['language'] = language
            if self.logic:
                self.logic.save_settings(Path("settings.json"), self.settings)
        
        self.lang = self.settings.get('language', 'ru')
        self.t = TRANSLATIONS[self.lang]
        
        # Флаг для отслеживания состояния - устанавливаем ДО init_ui
        self.tools_check_started = False
        
        self.init_ui()
        # Не вызываем check_tools() сразу - вызовем после показа окна

    def showEvent(self, event):
        # Вызываем проверку инструментов только после первого показа окна
        super().showEvent(event)
        if not self.tools_check_started:
            self.tools_check_started = True
            self.check_tools()

    def init_ui(self):
        self.setWindowTitle(self.t['title'])
        self.setMinimumSize(450, 250)
        self.setMaximumSize(600, 400)
        
        # Убираем стандартную рамку окна для кастомного заголовка
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        
        # Переменные для перетаскивания окна
        self._drag_pos = None
        self._is_maximized = False
        
        self.setStyleSheet("""
            QMainWindow {
                background-color: #121212;
            }
            QWidget {
                background-color: #121212;
                color: #ffffff;
                font-family: 'Segoe UI', sans-serif;
            }
            /* Стили для кастомного заголовка */
            #title_bar {
                background-color: #1f1f1f;
                padding: 8px;
            }
            #title_label {
                color: #bb86fc;
                font-weight: bold;
                font-size: 14px;
            }
            #close_btn, #minimize_btn, #maximize_btn {
                background-color: transparent;
                border: none;
                color: #888;
                font-size: 18px;
                padding: 5px 10px;
            }
            #close_btn:hover {
                background-color: #cf6679;
                color: white;
            }
            #minimize_btn:hover, #maximize_btn:hover {
                background-color: #333;
                color: white;
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

        # Создаем центральный виджет с вертикальным layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Создаем кастомную заголовочную панель
        title_bar = QWidget()
        title_bar.setObjectName("title_bar")
        title_bar.setFixedHeight(40)
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(10, 0, 10, 0)
        
        # Заголовок окна
        self.title_label = QLabel("🎬 YouWizard")
        self.title_label.setObjectName("title_label")
        title_layout.addWidget(self.title_label)
        
        # Пружина для прижатия кнопок вправо
        title_layout.addStretch()
        
        # Кнопка свернуть
        self.minimize_btn = QPushButton("─")
        self.minimize_btn.setObjectName("minimize_btn")
        self.minimize_btn.setFixedSize(30, 30)
        self.minimize_btn.clicked.connect(self.showMinimized)
        title_layout.addWidget(self.minimize_btn)
        
        # Кнопка развернуть/восстановить
        self.maximize_btn = QPushButton("□")
        self.maximize_btn.setObjectName("maximize_btn")
        self.maximize_btn.setFixedSize(30, 30)
        self.maximize_btn.clicked.connect(self.toggle_maximize)
        title_layout.addWidget(self.maximize_btn)
        
        # Кнопка закрытия
        self.close_btn = QPushButton("✕")
        self.close_btn.setObjectName("close_btn")
        self.close_btn.setFixedSize(30, 30)
        self.close_btn.clicked.connect(self.close)
        title_layout.addWidget(self.close_btn)
        
        main_layout.addWidget(title_bar)
        
        # Основной контент
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(20)
        
        header = QLabel("🎬 YouWizard")
        header.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        header.setStyleSheet("color: #bb86fc; margin-bottom: 10px;")
        content_layout.addWidget(header)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText(self.t['url_placeholder'])
        content_layout.addWidget(self.url_input)

        settings_layout = QHBoxLayout()
        settings_layout.setSpacing(15)
        
        self.format_combo = QComboBox()
        self.format_combo.addItems([self.t['format_video'], self.t['format_audio']])
        self.format_combo.setCurrentIndex(0)
        settings_layout.addWidget(self.format_combo, 2)
        
        # Выбор качества (только для видео)
        self.quality_combo = QComboBox()
        self.quality_combo.addItem(self.t['quality_best'], 'best')
        self.quality_combo.addItem(self.t['quality_1080'], '1080')
        self.quality_combo.addItem(self.t['quality_720'], '720')
        self.quality_combo.addItem(self.t['quality_480'], '480')
        self.quality_combo.addItem(self.t['quality_360'], '360')
        self.quality_combo.setVisible(True)
        settings_layout.addWidget(self.quality_combo, 2)
        
        self.browse_btn = QPushButton(self.t['btn_browse'])
        self.browse_btn.setFixedWidth(50)
        self.browse_btn.clicked.connect(self.browse_folder)
        settings_layout.addWidget(self.browse_btn)
        
        content_layout.addLayout(settings_layout)

        self.download_btn = QPushButton(f"📥 {self.t['btn_download']}")
        self.download_btn.setFixedHeight(50)
        self.download_btn.clicked.connect(self.start_download)
        content_layout.addWidget(self.download_btn)

        self.status_label = QLabel(self.t['status_ready'])
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(self.status_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        content_layout.addWidget(self.progress_bar)
        
        # Добавляем spacer для прижатия контента вверх
        content_layout.addStretch()
        
        main_layout.addWidget(content_widget, 1)

    # Методы для перетаскивания окна
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.title_label.underMouse():
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._drag_pos is not None and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
        super().mouseReleaseEvent(event)

    def toggle_maximize(self):
        """Переключение между обычным режимом и полным экраном."""
        if self._is_maximized:
            self.showNormal()
            self.maximize_btn.setText("□")
            self._is_maximized = False
        else:
            self.showMaximized()
            self.maximize_btn.setText("❐")
            self._is_maximized = True

    def check_tools(self):
        if self.settings.get('first_run', True):
            # Передаем выбранный язык в диалог установки и показываем модально
            self.install_dialog = FirstRunDialog(self.lang, self)
            self.install_dialog.show()
            
            self.installer = self.logic.ToolsInstaller()
            self.installer.progress.connect(lambda v, t: self.install_dialog.set_progress(v, t))
            self.installer.finished.connect(self.on_install_finished)
            self.installer.start()
            
            # Закрываем главное окно пока идет установка (чтобы не было двух окон)
            self.hide()
        else:
            if not (self.logic.INSTALL_DIR / "yt-dlp.exe").exists():
                 self.settings['first_run'] = True
                 if self.logic:
                     self.logic.save_settings(Path("settings.json"), self.settings)
                 self.check_tools()

    def on_install_finished(self, success):
        self.install_dialog.close()
        if success:
            self.settings['first_run'] = False
            if self.logic:
                self.logic.save_settings(Path("settings.json"), self.settings)
            # Обновляем переводы после установки
            self.t = TRANSLATIONS[self.lang]
            self.status_label.setText("✅ " + self.t['tools_ready'])
            # Показываем главное окно после успешной установки
            self.show()
            self.raise_()
            self.activateWindow()
        else:
            self.show()
            self.raise_()
            self.activateWindow()
            QMessageBox.critical(self, "Error", "Failed to install tools. Check internet connection.")

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, self.t['select_folder'], self.settings.get('last_dir', ''))
        if folder:
            self.settings['last_dir'] = folder
            if self.logic:
                self.logic.save_settings(Path("settings.json"), self.settings)

    def start_download(self):
        url = self.url_input.text().strip()
        if not url:
            return
        
        self.download_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText(self.t['status_downloading'])
        
        fmt = 'audio' if self.format_combo.currentIndex() == 1 else 'video'
        quality = self.quality_combo.currentData() if fmt == 'video' else 'best'
        out_template = os.path.join(self.settings.get('last_dir', '.'), '%(title)s.%(ext)s')
        
        self.worker = self.logic.Worker(url, out_template, fmt, self.logic.INSTALL_DIR, quality=quality)
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
