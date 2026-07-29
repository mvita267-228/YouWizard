#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouWizard - Minimalist YouTube Downloader (PyQt6)
Main entry point.
"""

import sys
from pathlib import Path

# Скрытие консольного окна (для Windows)
if sys.platform == 'win32':
    import ctypes
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

try:
    from PyQt6.QtWidgets import QApplication, QDialog
    from PyQt6.QtGui import QFont
except ImportError:
    print("Ошибка: PyQt6 не установлен. Установите его командой: pip install PyQt6")
    sys.exit(1)

# Импортируем модули
import logic
import ui


if __name__ == '__main__':
    app = QApplication(sys.argv)
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    # Проверяем, нужен ли выбор языка (первый запуск)
    settings_file = Path("settings.json")
    language = 'ru'  # язык по умолчанию
    
    if not settings_file.exists():
        # Показываем диалог выбора языка перед созданием главного окна
        lang_dialog = ui.LanguageSelectionDialog()
        if lang_dialog.exec() == QDialog.DialogCode.Accepted:
            language = lang_dialog.get_selected_language()
    
    window = ui.MainWindow(language, logic_module=logic)
    window.show()
    sys.exit(app.exec())
