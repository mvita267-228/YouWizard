#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouWizard - Minimalist YouTube Downloader (Tkinter)
Main entry point.
"""

import sys
import os
from pathlib import Path
import tkinter as tk

# Скрытие консольного окна (для Windows)
if sys.platform == 'win32':
    import ctypes
    try:
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    except Exception:
        pass

import logic
from ui import MainWindow, LanguageSelectionDialog, FirstRunDialog


def main():
    """Точка входа в приложение."""
    # Загрузка настроек
    settings_path = Path("settings.json")
    settings = logic.load_settings(settings_path)
    
    # Проверка первого запуска
    if settings.get('first_run', True):
        # Создаем скрытое корневое окно для диалога выбора языка
        root = tk.Tk()
        root.withdraw()  # Скрываем главное окно
        
        # Диалог выбора языка
        lang_dialog = LanguageSelectionDialog(root)
        language = lang_dialog.get_selected_language()
        
        # Обновляем настройки
        settings['first_run'] = False
        settings['language'] = language
        logic.save_settings(settings_path, settings)
        
        # Закрываем временное окно
        root.destroy()
        
        # Создаем главное приложение
        app = MainWindow(logic, language)
        
        # Показываем диалог установки
        install_dialog = FirstRunDialog(app.root, language)
        
        # Запуск проверки инструментов в фоне
        def on_install_complete():
            install_dialog.close()
            app.check_tools()
        
        # Имитация завершения установки через 2 секунды
        app.root.after(2000, on_install_complete)
    else:
        # Не первый запуск
        language = settings.get('language', 'ru')
        app = MainWindow(logic, language)
        app.check_tools()
    
    # Запуск главного цикла
    app.run()


if __name__ == "__main__":
    main()
