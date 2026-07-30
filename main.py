#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouWizard - Minimalist YouTube Downloader (Tkinter)
Main entry point.
"""

import sys
import os
from pathlib import Path

# Скрытие консольного окна (для Windows)
if sys.platform == 'win32':
    import ctypes
    try:
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    except Exception:
        pass

import logic
import ui

if __name__ == '__main__':
    # Проверяем, нужен ли выбор языка (первый запуск)
    settings_file = Path("settings.json")
    language = 'ru'  # язык по умолчанию
    
    if not settings_file.exists():
        # Показываем диалог выбора языка перед созданием главного окна
        lang_dialog = ui.LanguageSelectionDialog()
        selected_lang = lang_dialog.run()
        if selected_lang:
            language = selected_lang
        else:
            sys.exit(0)
    
    # Запускаем главное приложение
    app = ui.MainWindow(language, logic_module=logic)
    app.run()
