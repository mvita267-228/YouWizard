#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouWizard - Minimalist YouTube Downloader (Tkinter)
Logic Module.
"""

import os
import sys
import json
import time
import threading
import subprocess
from pathlib import Path

try:
    import yt_dlp
except ImportError:
    print("Ошибка: yt-dlp не установлен. Установите его командой: pip install yt-dlp")
    sys.exit(1)

# Словарь переводов для логики
LOGIC_TRANSLATIONS = {
    'en': {
        'downloading_tools': 'Downloading essential tools...',
        'installing_ffmpeg': 'Installing full FFmpeg...',
        'tools_ready': 'Tools installed successfully!',
        'error': 'Error',
        'download_complete': 'Download complete!',
        'download_failed': 'Download failed!',
        'checking_tools': 'Checking tools...'
    },
    'ru': {
        'downloading_tools': 'Загрузка инструментов...',
        'installing_ffmpeg': 'Установка полной версии FFmpeg...',
        'tools_ready': 'Инструменты установлены успешно!',
        'error': 'Ошибка',
        'download_complete': 'Загрузка завершена!',
        'download_failed': 'Ошибка загрузки!',
        'checking_tools': 'Проверка инструментов...'
    }
}


class DownloadWorker:
    """Рабочий поток для загрузки."""
    def __init__(self, url, output_path, format_type, quality, callback, language='ru'):
        self.url = url
        self.output_path = output_path
        self.format_type = format_type
        self.quality = quality
        self.callback = callback
        self.language = language
        self.t = LOGIC_TRANSLATIONS.get(language, LOGIC_TRANSLATIONS['ru'])
        self._stop_flag = False

    def stop(self):
        self._stop_flag = True

    def run(self):
        try:
            if self._stop_flag:
                return

            ydl_opts = {
                'outtmpl': os.path.join(self.output_path, '%(title)s.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
            }

            if self.format_type == 'audio':
                ydl_opts['format'] = 'bestaudio/best'
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            else:
                if self.quality == 'best':
                    ydl_opts['format'] = 'bestvideo+bestaudio/best'
                elif self.quality == '1080':
                    ydl_opts['format'] = 'bestvideo[height<=1080]+bestaudio/best[height<=1080]'
                elif self.quality == '720':
                    ydl_opts['format'] = 'bestvideo[height<=720]+bestaudio/best[height<=720]'
                elif self.quality == '480':
                    ydl_opts['format'] = 'bestvideo[height<=480]+bestaudio/best[height<=480]'
                elif self.quality == '360':
                    ydl_opts['format'] = 'bestvideo[height<=360]+bestaudio/best[height<=360]'
                else:
                    ydl_opts['format'] = 'bestvideo+bestaudio/best'
                
                ydl_opts['merge_output_format'] = 'mp4'

            def progress_hook(d):
                if self._stop_flag:
                    raise Exception('Stopped by user')
                
                if d['status'] == 'downloading':
                    total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                    downloaded = d.get('downloaded_bytes', 0)
                    if total > 0:
                        percent = (downloaded / total) * 100
                        self.callback('progress', percent)
                elif d['status'] == 'finished':
                    self.callback('progress', 100)

            ydl_opts['progress_hooks'] = [progress_hook]

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.url])

            self.callback('done', self.t['download_complete'])

        except Exception as e:
            if not self._stop_flag:
                self.callback('error', f"{self.t['error']}: {str(e)}")


def check_and_install_tools(callback, language='ru'):
    """Проверяет и устанавливает необходимые инструменты."""
    t = LOGIC_TRANSLATIONS.get(language, LOGIC_TRANSLATIONS['ru'])
    
    ffmpeg_found = False
    try:
        result = subprocess.run(['ffmpeg', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        ffmpeg_found = result.returncode == 0
    except FileNotFoundError:
        ffmpeg_found = False

    if not ffmpeg_found:
        callback('status', t['installing_ffmpeg'])
        time.sleep(1)
        callback('status', "FFmpeg not found. Please install FFmpeg manually.")
    else:
        callback('status', t['tools_ready'])
    
    callback('done', t['tools_ready'])


def load_settings(path):
    """Загружает настройки из файла."""
    if path.exists():
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {'first_run': True, 'language': 'ru', 'last_dir': str(Path.home())}


def save_settings(path, settings):
    """Сохраняет настройки в файл."""
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
    except:
        pass


def get_default_download_folder():
    """Возвращает путь к папке загрузок по умолчанию."""
    home = Path.home()
    if os.name == 'nt':
        downloads = home / 'Downloads'
    else:
        downloads = home / 'Downloads'
        if not downloads.exists():
            downloads = home
    
    if not downloads.exists():
        downloads = home
    
    return str(downloads)
