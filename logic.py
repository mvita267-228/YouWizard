#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouWizard - Logic Module
Handles business logic, tool installation, and download operations.
"""

import sys
import os
import json
import subprocess
import shutil
from pathlib import Path

try:
    from PyQt6.QtCore import Qt, QThread, pyqtSignal
except ImportError:
    print("Ошибка: PyQt6 не установлен. Установите его командой: pip install PyQt6")
    sys.exit(1)

# Конфигурация
INSTALL_DIR = Path("bin")


class ToolsInstaller(QThread):
    """Поток для установки yt-dlp и FFmpeg."""
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
            
            # 2. Установка полной версии FFmpeg
            self.progress.emit(30, "Downloading full FFmpeg...")
            if sys.platform == 'win32':
                # Используем полную версию со всеми компонентами
                ff_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
                zip_path = INSTALL_DIR / "ffmpeg_full.zip"
                
                try:
                    urllib.request.urlretrieve(ff_url, zip_path)
                    self.progress.emit(60, "Extracting FFmpeg...")
                    
                    import zipfile
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        # Извлекаем все файлы из bin директории
                        for file in zip_ref.namelist():
                            if file.startswith("ffmpeg-master-latest-win64-gpl/bin/"):
                                zip_ref.extract(file, INSTALL_DIR)
                                src = INSTALL_DIR / file
                                filename = file.split("/")[-1]
                                dst = INSTALL_DIR / filename
                                if src != dst:
                                    shutil.move(src, dst)
                        
                        # Очищаем временную директорию
                        temp_dir = INSTALL_DIR / "ffmpeg-master-latest-win64-gpl"
                        if temp_dir.exists():
                            shutil.rmtree(temp_dir)
                    
                    zip_path.unlink()
                    self.progress.emit(90, "Cleaning up...")
                except Exception as e:
                    print(f"FFmpeg download error: {e}")
                    # Пробуем альтернативный источник
                    try:
                        ff_url_alt = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
                        urllib.request.urlretrieve(ff_url_alt, zip_path)
                        self.progress.emit(60, "Extracting FFmpeg (alternative)...")
                        
                        import zipfile
                        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                            for file in zip_ref.namelist():
                                if file.startswith("ffmpeg-release-essentials/bin/"):
                                    zip_ref.extract(file, INSTALL_DIR)
                                    src = INSTALL_DIR / file
                                    filename = file.split("/")[-1]
                                    dst = INSTALL_DIR / filename
                                    if src != dst:
                                        shutil.move(src, dst)
                            
                            temp_dir = INSTALL_DIR / "ffmpeg-release-essentials"
                            if temp_dir.exists():
                                shutil.rmtree(temp_dir)
                        
                        zip_path.unlink()
                    except Exception as e2:
                        print(f"Alternative FFmpeg download failed: {e2}")

            self.progress.emit(100, "Done")
            self.finished.emit(True)
        except Exception as e:
            print(f"Install error: {e}")
            self.finished.emit(False)


class Worker(QThread):
    """Поток для загрузки видео/аудио."""
    progress = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, url, output_template, format_type, bin_path, quality='best'):
        super().__init__()
        self.url = url
        self.output_template = output_template
        self.format_type = format_type
        self.bin_path = str(bin_path)
        self.quality = quality

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
                # Выбор качества для видео
                if self.quality == 'best':
                    cmd.extend(['-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'])
                else:
                    # Формируем фильтр качества на основе выбора пользователя
                    height = self.quality
                    cmd.extend(['-f', f'bestvideo[height<={height}][ext=mp4]+bestaudio[ext=m4a]/best[height<={height}][ext=mp4]/best[height<={height}]'])

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


def load_settings(settings_file):
    """Загрузка настроек из файла."""
    if settings_file.exists():
        with open(settings_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'first_run': True, 'language': 'ru', 'last_dir': str(Path.home())}


def save_settings(settings_file, settings):
    """Сохранение настроек в файл."""
    with open(settings_file, 'w', encoding='utf-8') as f:
        json.dump(settings, f)
