import json
import os
import re
import sys
import subprocess
import urllib.request
import shutil
from datetime import datetime
from pathlib import Path

from PyQt5.QtCore import Qt, QProcess, QTimer, QSize, pyqtSignal, QThread
from PyQt5.QtGui import QColor, QPalette, QIcon, QFont
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QButtonGroup,
    QCheckBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QProgressBar,
    QRadioButton,
    QScrollArea,
    QSizePolicy,
    QStackedWidget,
    QSystemTrayIcon,
    QVBoxLayout,
    QWidget,
    QMenu,
    QStyle,
    QComboBox,
)


APP_NAME = "YouWizard"

# URLs для загрузки инструментов
YTDLP_URL = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe"
FFMPEG_URL = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"

# Переводы интерфейса
TRANSLATIONS = {
    "ru": {
        "app_title": "YouWizard",
        "logo": "🎬 YouWizard",
        "subtitle": "Media Downloader",
        "nav_download": "📥 Скачать",
        "nav_history": "📁 Загрузки",
        "nav_settings": "⚙️ Настройки",
        "exit": "🚪 Выход",
        "download_page_title": "Скачать медиа",
        "download_page_subtitle": "Видео загружается через yt-dlp. MP4 обрабатывается через ffmpeg без перекодирования.",
        "url_placeholder": "Вставьте ссылку на видео (YouTube, Vimeo, TikTok...)",
        "mode_title": "Что скачать",
        "mode_video": "🎬 Видео + Аудио",
        "mode_audio": "🎵 Только аудио",
        "quality_title": "Качество видео",
        "quality_hint": "2K / 4K / 8K скрыты. Включите в настройках.",
        "audio_title": "Формат и качество аудио",
        "audio_bitrate": "Битрейт:",
        "folder_title": "Папка загрузок",
        "choose_folder": "📂 Выбрать",
        "download_btn": "▶️ Скачать",
        "stop_btn": "⏹️ Остановить",
        "status_ready": "✅ Готов к работе",
        "status_downloading": "⏳ Загрузка...",
        "status_finished": "✅ Завершено",
        "status_error": "❌ Ошибка",
        "recent_title": "🕐 Последние 5 загрузок",
        "recent_empty": "📭 Пока пусто",
        "open_btn": "📂 Открыть",
        "file_not_found_title": "Файл не найден",
        "file_not_found_msg": "Файл был удалён или перемещён.",
        "history_title": "📜 История загрузок",
        "open_folder_btn": "📂 Открыть папку",
        "settings_title": "⚙️ Настройки",
        "settings_general": "Основные",
        "close_to_tray": "Сворачивать в трей при закрытии",
        "show_high_res": "Показывать 2K/4K/8K",
        "default_mode": "Режим по умолчанию",
        "default_mode_video": "Видео",
        "default_mode_audio": "Аудио",
        "language": "Язык интерфейса",
        "language_ru": "Русский",
        "language_en": "English",
        "logs_title": "Логи",
        "enable_logs": "Включить логирование",
        "cleanup_interval": "Очистка каждые (мин):",
        "keep_logs": "Хранить логов:",
        "save_btn": "💾 Сохранить",
        "saved_title": "Сохранено",
        "saved_msg": "Настройки сохранены. Перезапустите приложение.",
        "tools_info": "Информация о компонентах",
        "tray_open": "Открыть YouWizard",
        "tray_logs": "Открыть логи",
        "tray_exit": "Выход",
        "tray_msg_title": "YouWizard",
        "tray_msg_text": "Работает в фоне...",
        "error_tools_title": "Ошибка",
        "error_tools_msg": "Компоненты не найдены. Загружаю...",
        "error_url_title": "Ошибка",
        "error_url_msg": "Введите URL видео.",
        "downloading": "Загрузка...",
        "stopped": "Остановлено.",
        "finished": "Готово!",
        "error_download_title": "Ошибка загрузки",
        "no_files_yet": "Файлов пока нет.",
        "installing_tools": "📦 Установка компонентов...",
        "downloading_ytdlp": "⬇️ Загрузка yt-dlp...",
        "downloading_ffmpeg": "⬇️ Загрузка ffmpeg...",
        "install_complete": "✅ Компоненты установлены!",
        "first_run_title": "Первый запуск",
        "first_run_msg": "Приложение загружает необходимые компоненты. Это займёт несколько минут.",
    },
    "en": {
        "app_title": "YouWizard",
        "logo": "🎬 YouWizard",
        "subtitle": "Media Downloader",
        "nav_download": "📥 Download",
        "nav_history": "📁 Downloads",
        "nav_settings": "⚙️ Settings",
        "exit": "🚪 Exit",
        "download_page_title": "Download Media",
        "download_page_subtitle": "Videos downloaded via yt-dlp. MP4 processed via ffmpeg without re-encoding.",
        "url_placeholder": "Paste video URL (YouTube, Vimeo, TikTok...)",
        "mode_title": "What to download",
        "mode_video": "🎬 Video + Audio",
        "mode_audio": "🎵 Audio Only",
        "quality_title": "Video Quality",
        "quality_hint": "2K / 4K / 8K hidden. Enable in settings.",
        "audio_title": "Audio Format & Quality",
        "audio_bitrate": "Bitrate:",
        "folder_title": "Download Folder",
        "choose_folder": "📂 Choose",
        "download_btn": "▶️ Download",
        "stop_btn": "⏹️ Stop",
        "status_ready": "✅ Ready",
        "status_downloading": "⏳ Downloading...",
        "status_finished": "✅ Complete",
        "status_error": "❌ Error",
        "recent_title": "🕐 Last 5 Downloads",
        "recent_empty": "📭 Empty",
        "open_btn": "📂 Open",
        "file_not_found_title": "File Not Found",
        "file_not_found_msg": "File was deleted or moved.",
        "history_title": "📜 Download History",
        "open_folder_btn": "📂 Open Folder",
        "settings_title": "⚙️ Settings",
        "settings_general": "General",
        "close_to_tray": "Minimize to tray on close",
        "show_high_res": "Show 2K/4K/8K",
        "default_mode": "Default Mode",
        "default_mode_video": "Video",
        "default_mode_audio": "Audio",
        "language": "Interface Language",
        "language_ru": "Русский",
        "language_en": "English",
        "logs_title": "Logs",
        "enable_logs": "Enable logging",
        "cleanup_interval": "Cleanup every (min):",
        "keep_logs": "Keep logs:",
        "save_btn": "💾 Save",
        "saved_title": "Saved",
        "saved_msg": "Settings saved. Restart application.",
        "tools_info": "Components Info",
        "tray_open": "Open YouWizard",
        "tray_logs": "Open logs",
        "tray_exit": "Exit",
        "tray_msg_title": "YouWizard",
        "tray_msg_text": "Running in background...",
        "error_tools_title": "Error",
        "error_tools_msg": "Components not found. Downloading...",
        "error_url_title": "Error",
        "error_url_msg": "Enter video URL.",
        "downloading": "Downloading...",
        "stopped": "Stopped.",
        "finished": "Done!",
        "error_download_title": "Download Error",
        "no_files_yet": "No files yet.",
        "installing_tools": "📦 Installing components...",
        "downloading_ytdlp": "⬇️ Downloading yt-dlp...",
        "downloading_ffmpeg": "⬇️ Downloading ffmpeg...",
        "install_complete": "✅ Components installed!",
        "first_run_title": "First Run",
        "first_run_msg": "Application is downloading required components. This may take a few minutes.",
    }
}


def root_dir() -> Path:
    return Path(__file__).resolve().parent


ROOT = root_dir()
BIN = ROOT / "bin"
SETTINGS_DIR = ROOT / "settings"
SETTINGS_FILE = SETTINGS_DIR / "settings.json"

YTDLP = BIN / "yt-dlp.exe"
FFMPEG = BIN / "ffmpeg.exe"
FFPROBE = BIN / "ffprobe.exe"


DEFAULT_SETTINGS = {
    "_warning_ru": "ВНИМАНИЕ: если вы не знаете, за что отвечает параметр, не изменяйте этот файл вручную.",
    "_warning_en": "WARNING: if you do not know what a setting does, do not edit this file manually.",
    "app": {
        "close_to_tray": True,
        "language": "ru",
        "first_run": True
    },
    "downloads": {
        "download_folder": "downloads",
        "default_mode": "video",
        "show_high_res_options": False,
        "recent_downloads": []
    },
    "audio": {
        "format": "mp3",
        "quality": "192K"
    },
    "logs": {
        "enabled": True,
        "folder": "settings/logs",
        "cleanup_interval_minutes": 60,
        "keep_last_logs": 20
    },
    "tools": {
        "ytdlp_installed": False,
        "ffmpeg_installed": False
    }
}


def deep_update(base: dict, patch: dict) -> None:
    for key, value in patch.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            deep_update(base[key], value)
        else:
            base[key] = value


def save_settings(settings: dict) -> None:
    SETTINGS_DIR.mkdir(parents=True, exist_ok=True)
    SETTINGS_FILE.write_text(
        json.dumps(settings, ensure_ascii=False, indent=4),
        encoding="utf-8"
    )


def load_settings() -> dict:
    SETTINGS_DIR.mkdir(parents=True, exist_ok=True)

    if not SETTINGS_FILE.exists():
        save_settings(DEFAULT_SETTINGS)
        return json.loads(json.dumps(DEFAULT_SETTINGS))

    try:
        data = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))

        if not isinstance(data, dict):
            raise ValueError("settings.json is not object")

        result = json.loads(json.dumps(DEFAULT_SETTINGS))
        deep_update(result, data)
        return result

    except Exception:
        broken = SETTINGS_DIR / "settings.broken.json"

        try:
            SETTINGS_FILE.replace(broken)
        except Exception:
            pass

        save_settings(DEFAULT_SETTINGS)
        return json.loads(json.dumps(DEFAULT_SETTINGS))


class ToolsInstaller(QThread):
    """Поток для загрузки и установки инструментов"""
    progress_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool)
    
    def __init__(self):
        super().__init__()
        self.bin_dir = BIN
        
    def run(self):
        try:
            self.bin_dir.mkdir(parents=True, exist_ok=True)
            
            # Загрузка yt-dlp
            self.progress_signal.emit("downloading_ytdlp")
            ytdlp_path = self.bin_dir / "yt-dlp.exe"
            urllib.request.urlretrieve(YTDLP_URL, str(ytdlp_path))
            
            # Загрузка ffmpeg (zip архив)
            self.progress_signal.emit("downloading_ffmpeg")
            import zipfile
            import tempfile
            
            zip_path = self.bin_dir / "ffmpeg.zip"
            urllib.request.urlretrieve(FFMPEG_URL, str(zip_path))
            
            # Распаковка ffmpeg
            with zipfile.ZipFile(str(zip_path), 'r') as zip_ref:
                # Находим папку с бинарниками (обычно внутри bin/)
                zip_ref.extractall(str(self.bin_dir))
            
            # Удаляем zip
            zip_path.unlink()
            
            # Перемещаем exe файлы из подпапки в bin
            extracted_dirs = [d for d in self.bin_dir.iterdir() if d.is_dir() and d.name.startswith('ffmpeg')]
            if extracted_dirs:
                ffmpeg_dir = extracted_dirs[0]
                bin_subdir = ffmpeg_dir / 'bin'
                if bin_subdir.exists():
                    for exe_file in bin_subdir.glob('*.exe'):
                        dest = self.bin_dir / exe_file.name
                        if dest.exists():
                            dest.unlink()
                        exe_file.rename(dest)
                
                # Удаляем папку с исходными файлами
                shutil.rmtree(ffmpeg_dir)
            
            self.finished_signal.emit(True)
            
        except Exception as e:
            print(f"Error installing tools: {e}")
            self.finished_signal.emit(False)


def check_tools_installed() -> tuple[bool, bool]:
    """Проверяет, установлены ли инструменты"""
    ytdlp_installed = YTDLP.exists()
    ffmpeg_installed = FFMPEG.exists()
    return ytdlp_installed, ffmpeg_installed


def install_tools_if_needed(settings: dict) -> bool:
    """Устанавливает инструменты если их нет или первый запуск"""
    first_run = settings.get("app", {}).get("first_run", True)
    ytdlp_installed, ffmpeg_installed = check_tools_installed()
    
    if first_run or not ytdlp_installed or not ffmpeg_installed:
        return True  # Нужно установить
    return False  # Всё установлено


def app_path(text: str) -> Path:
    text = text.strip()

    if not text:
        return ROOT / "downloads"

    path = Path(text)

    if path.is_absolute():
        return path

    return ROOT / path


def logs_dir(settings: dict) -> Path:
    folder = settings.get("logs", {}).get("folder", "settings/logs")
    path = app_path(folder)
    path.mkdir(parents=True, exist_ok=True)
    return path


def cleanup_logs(settings: dict) -> None:
    folder = logs_dir(settings)

    try:
        keep = int(settings.get("logs", {}).get("keep_last_logs", 20))
    except Exception:
        keep = 20

    keep = max(1, keep)

    files = sorted(
        folder.glob("*.txt"),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )

    for file in files[keep:]:
        try:
            file.unlink()
        except Exception:
            pass


def newest_file(folder: Path) -> Path | None:
    if not folder.exists():
        return None

    exts = {".mp4", ".mp3", ".m4a", ".webm", ".mkv", ".opus", ".ogg", ".flac", ".wav", ".aac"}
    files = [p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in exts]

    if not files:
        return None

    return max(files, key=lambda p: p.stat().st_mtime)


def add_recent(settings: dict, file: Path) -> None:
    recent = settings.setdefault("downloads", {}).setdefault("recent_downloads", [])

    recent.insert(0, {
        "name": file.name,
        "path": str(file),
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    clean = []
    used = set()

    for item in recent:
        path = item.get("path", "")

        if not path or path in used:
            continue

        used.add(path)
        clean.append(item)

    settings["downloads"]["recent_downloads"] = clean[:5]
    save_settings(settings)


def open_path(path: Path) -> None:
    try:
        os.startfile(path)
    except Exception:
        QMessageBox.warning(None, "Ошибка", f"Не удалось открыть:\n{path}")


def apply_dark_palette(app: QApplication) -> None:
    """Применяет полностью тёмную тему с современными цветами"""
    palette = QPalette()
    
    # Основные цвета тёмной темы
    palette.setColor(QPalette.Window, QColor("#121212"))
    palette.setColor(QPalette.WindowText, QColor("#E0E0E0"))
    palette.setColor(QPalette.Base, QColor("#1E1E1E"))
    palette.setColor(QPalette.AlternateBase, QColor("#252525"))
    palette.setColor(QPalette.ToolTipBase, QColor("#1E1E1E"))
    palette.setColor(QPalette.ToolTipText, QColor("#E0E0E0"))
    palette.setColor(QPalette.Text, QColor("#E0E0E0"))
    palette.setColor(QPalette.Button, QColor("#2D2D2D"))
    palette.setColor(QPalette.ButtonText, QColor("#E0E0E0"))
    palette.setColor(QPalette.BrightText, QColor("#FFFFFF"))
    palette.setColor(QPalette.Link, QColor("#64B5F6"))
    palette.setColor(QPalette.Light, QColor("#3D3D3D"))
    palette.setColor(QPalette.Midlight, QColor("#323232"))
    palette.setColor(QPalette.Dark, QColor("#1A1A1A"))
    palette.setColor(QPalette.Mid, QColor("#2A2A2A"))
    palette.setColor(QPalette.Shadow, QColor("#0A0A0A"))
    palette.setColor(QPalette.Highlight, QColor("#BB86FC"))
    palette.setColor(QPalette.HighlightedText, QColor("#000000"))
    
    app.setPalette(palette)
    
    # Применяем стилизацию через stylesheet для более современного вида
    app.setStyleSheet("""
        QMainWindow {
            background-color: #121212;
        }
        
        QWidget {
            background-color: #121212;
            color: #E0E0E0;
            font-family: 'Segoe UI', Arial, sans-serif;
        }
        
        QLabel#AppLogo {
            font-size: 32px;
            font-weight: bold;
            color: #BB86FC;
            padding: 10px;
        }
        
        QLabel#AppSubtitle {
            font-size: 14px;
            color: #A0A0A0;
            padding-bottom: 20px;
        }
        
        QLabel#SectionTitle {
            font-size: 16px;
            font-weight: bold;
            color: #BB86FC;
            padding: 5px;
        }
        
        QLabel#Muted {
            color: #757575;
            font-style: italic;
        }
        
        QPushButton {
            background-color: #2D2D2D;
            border: 1px solid #3D3D3D;
            border-radius: 8px;
            padding: 10px 20px;
            color: #E0E0E0;
            font-weight: bold;
        }
        
        QPushButton:hover {
            background-color: #3D3D3D;
            border-color: #BB86FC;
        }
        
        QPushButton:pressed {
            background-color: #BB86FC;
            color: #000000;
        }
        
        QPushButton#PrimaryButton {
            background-color: #BB86FC;
            color: #000000;
            border: none;
        }
        
        QPushButton#PrimaryButton:hover {
            background-color: #9965F4;
        }
        
        QPushButton#NavButton {
            background-color: transparent;
            border: none;
            border-radius: 8px;
            text-align: left;
            padding: 12px 16px;
            font-size: 14px;
        }
        
        QPushButton#NavButton:hover {
            background-color: #1E1E1E;
        }
        
        QPushButton#NavButton:checked {
            background-color: #2D2D2D;
            border-left: 3px solid #BB86FC;
        }
        
        QLineEdit {
            background-color: #1E1E1E;
            border: 1px solid #3D3D3D;
            border-radius: 8px;
            padding: 12px;
            color: #E0E0E0;
            selection-background-color: #BB86FC;
            selection-color: #000000;
        }
        
        QLineEdit:focus {
            border-color: #BB86FC;
        }
        
        QRadioButton {
            spacing: 10px;
        }
        
        QRadioButton::indicator {
            width: 20px;
            height: 20px;
            border-radius: 10px;
            border: 2px solid #3D3D3D;
            background-color: #1E1E1E;
        }
        
        QRadioButton::indicator:checked {
            background-color: #BB86FC;
            border-color: #BB86FC;
        }
        
        QCheckBox {
            spacing: 10px;
        }
        
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
            border-radius: 4px;
            border: 2px solid #3D3D3D;
            background-color: #1E1E1E;
        }
        
        QCheckBox::indicator:checked {
            background-color: #BB86FC;
            border-color: #BB86FC;
        }
        
        QComboBox {
            background-color: #1E1E1E;
            border: 1px solid #3D3D3D;
            border-radius: 8px;
            padding: 10px;
            color: #E0E0E0;
        }
        
        QComboBox:hover {
            border-color: #BB86FC;
        }
        
        QComboBox::drop-down {
            border: none;
            width: 30px;
        }
        
        QComboBox QAbstractItemView {
            background-color: #1E1E1E;
            border: 1px solid #3D3D3D;
            selection-background-color: #BB86FC;
            selection-color: #000000;
        }
        
        QProgressBar {
            background-color: #1E1E1E;
            border: none;
            border-radius: 8px;
            height: 20px;
            text-align: center;
        }
        
        QProgressBar::chunk {
            background-color: #BB86FC;
            border-radius: 8px;
        }
        
        QScrollArea {
            border: none;
            background-color: #121212;
        }
        
        QScrollArea#PageScroll {
            background-color: #121212;
        }
        
        QScrollBar:vertical {
            background-color: #121212;
            width: 12px;
            border-radius: 6px;
        }
        
        QScrollBar::handle:vertical {
            background-color: #3D3D3D;
            border-radius: 6px;
            min-height: 30px;
        }
        
        QScrollBar::handle:vertical:hover {
            background-color: #4D4D4D;
        }
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
        
        QFrame#Card {
            background-color: #1E1E1E;
            border: 1px solid #2D2D2D;
            border-radius: 12px;
        }
        
        QFrame#RecentRow {
            background-color: #252525;
            border-radius: 8px;
        }
        
        QLabel#RecentText {
            color: #E0E0E0;
        }
        
        QMenu {
            background-color: #1E1E1E;
            border: 1px solid #3D3D3D;
            border-radius: 8px;
            padding: 8px;
        }
        
        QMenu::item {
            padding: 8px 16px;
            border-radius: 4px;
        }
        
        QMenu::item:selected {
            background-color: #BB86FC;
            color: #000000;
        }
        
        QMessageBox {
            background-color: #1E1E1E;
        }
        
        QMessageBox QLabel {
            color: #E0E0E0;
        }
        
        QMessageBox QPushButton {
            min-width: 80px;
        }
    """)


def make_scroll_page(page: QWidget) -> QScrollArea:
    scroll = QScrollArea()
    scroll.setObjectName("PageScroll")
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QFrame.NoFrame)
    scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
    scroll.setWidget(page)
    return scroll


class Logger:
    def __init__(self, settings: dict):
        self.enabled = bool(settings.get("logs", {}).get("enabled", True))
        log_dir = logs_dir(settings)
        self.file = log_dir / f"youwizard_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"

        self.write("=== YouWizard started ===")
        self.write(f"Root: {ROOT}")
        self.write(f"Time: {datetime.now().isoformat(timespec='seconds')}")
        self.write("")

    def write(self, text: str) -> None:
        if not self.enabled:
            return

        try:
            with self.file.open("a", encoding="utf-8") as f:
                f.write(text.rstrip() + "\n")
        except Exception:
            pass

    def block(self, text: str) -> None:
        for line in text.splitlines():
            self.write(line)


class Card(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("Card")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)


class NavButton(QPushButton):
    def __init__(self, text: str, icon: QIcon = None):
        super().__init__(text)
        self.setCheckable(True)
        self.setMinimumHeight(44)
        self.setCursor(Qt.PointingHandCursor)
        if icon:
            self.setIcon(icon)
            size_val = self.style().pixelMetric(QStyle.PM_SmallIconSize) * 2
            self.setIconSize(QSize(size_val, size_val))   # исправлено: передаём QSize


class QualityButton(QRadioButton):
    def __init__(self, text: str, height_value: int | None):
        super().__init__(text)
        self.height_value = height_value
        self.setObjectName("QualityButton")
        self.setMinimumHeight(42)
        self.setCursor(Qt.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)


class RecentList(Card):
    def __init__(self, window: "MainWindow", title: str):
        super().__init__()
        self.window = window

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(16, 16, 16, 16)
        self.layout.setSpacing(10)

        label = QLabel(title)
        label.setObjectName("SectionTitle")
        self.layout.addWidget(label)

        self.items = QVBoxLayout()
        self.items.setSpacing(8)
        self.layout.addLayout(self.items)

        self.refresh()

    def clear_items(self) -> None:
        while self.items.count():
            item = self.items.takeAt(0)
            widget = item.widget()

            if widget:
                widget.deleteLater()

    def refresh(self) -> None:
        self.clear_items()

        recent = self.window.settings.get("downloads", {}).get("recent_downloads", [])[:5]
        t = self.window.get_text()

        if not recent:
            empty = QLabel(t["recent_empty"])
            empty.setObjectName("Muted")
            empty.setWordWrap(True)
            self.items.addWidget(empty)
            return

        for item in recent:
            row = QFrame()
            row.setObjectName("RecentRow")

            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(12, 8, 12, 8)
            row_layout.setSpacing(10)

            name = item.get("name", "File")
            date = item.get("date", "")
            path = item.get("path", "")

            text = QLabel(f"{name}\n{date}")
            text.setObjectName("RecentText")
            text.setWordWrap(True)

            open_btn = QPushButton(t["open_btn"])
            open_btn.setFixedWidth(105)
            open_btn.clicked.connect(lambda checked=False, p=path: self.open_file(p))

            row_layout.addWidget(text, 1)
            row_layout.addWidget(open_btn)

            self.items.addWidget(row)

    def open_file(self, path: str) -> None:
        p = Path(path)
        t = self.window.get_text()

        if p.exists():
            open_path(p)
        else:
            QMessageBox.warning(self, t["file_not_found_title"], t["file_not_found_msg"])


class DownloadPage(QWidget):
    def __init__(self, window: "MainWindow"):
        super().__init__()
        self.window = window
        self.process: QProcess | None = None
        self.current_folder: Path | None = None
        self.selected_quality: int | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)

        t = self.window.get_text()

        title = QLabel(t["download_page_title"])
        title.setObjectName("PageTitle")

        subtitle = QLabel(t["download_page_subtitle"])
        subtitle.setObjectName("Muted")
        subtitle.setWordWrap(True)

        self.url = QLineEdit()
        self.url.setPlaceholderText(t["url_placeholder"])
        self.url.setMinimumHeight(46)

        self.mode_card = Card()
        mode_layout = QVBoxLayout(self.mode_card)
        mode_layout.setContentsMargins(16, 16, 16, 16)
        mode_layout.setSpacing(8)

        mode_title = QLabel(t["mode_title"])
        mode_title.setObjectName("SectionTitle")

        self.video_radio = QRadioButton(t["mode_video"])
        self.audio_radio = QRadioButton(t["mode_audio"])

        self.mode_group = QButtonGroup(self)
        self.mode_group.addButton(self.video_radio)
        self.mode_group.addButton(self.audio_radio)

        if self.window.settings["downloads"].get("default_mode") == "audio":
            self.audio_radio.setChecked(True)
        else:
            self.video_radio.setChecked(True)

        self.video_radio.toggled.connect(self.update_mode)

        mode_layout.addWidget(mode_title)
        mode_layout.addWidget(self.video_radio)
        mode_layout.addWidget(self.audio_radio)

        self.quality_card = Card()
        quality_layout = QVBoxLayout(self.quality_card)
        quality_layout.setContentsMargins(16, 16, 16, 16)
        quality_layout.setSpacing(10)

        quality_title = QLabel(t["quality_title"])
        quality_title.setObjectName("SectionTitle")

        self.quality_group = QButtonGroup(self)
        self.quality_group.setExclusive(True)

        self.quality_grid = QGridLayout()
        self.quality_grid.setHorizontalSpacing(8)
        self.quality_grid.setVerticalSpacing(8)

        quality_hint = QLabel(t["quality_hint"])
        quality_hint.setObjectName("Muted")
        quality_hint.setWordWrap(True)

        quality_layout.addWidget(quality_title)
        quality_layout.addLayout(self.quality_grid)
        quality_layout.addWidget(quality_hint)

        self.rebuild_quality_buttons()

        self.audio_card = Card()
        audio_layout = QVBoxLayout(self.audio_card)
        audio_layout.setContentsMargins(16, 16, 16, 16)
        audio_layout.setSpacing(8)

        audio_title = QLabel(t["audio_title"])
        audio_title.setObjectName("SectionTitle")

        self.mp3_radio = QRadioButton("MP3")
        self.m4a_radio = QRadioButton("M4A")

        self.audio_group = QButtonGroup(self)
        self.audio_group.addButton(self.mp3_radio)
        self.audio_group.addButton(self.m4a_radio)

        if self.window.settings["audio"].get("format") == "m4a":
            self.m4a_radio.setChecked(True)
        else:
            self.mp3_radio.setChecked(True)

        audio_quality_layout = QHBoxLayout()
        audio_quality_layout.setSpacing(8)
        audio_quality_label = QLabel(t["audio_bitrate"])
        self.audio_quality_combo = QComboBox()
        self.audio_quality_combo.addItems(["128K", "192K", "256K", "320K"])
        current_quality = self.window.settings["audio"].get("quality", "192K")
        idx = self.audio_quality_combo.findText(current_quality)
        if idx >= 0:
            self.audio_quality_combo.setCurrentIndex(idx)
        audio_quality_layout.addWidget(audio_quality_label)
        audio_quality_layout.addWidget(self.audio_quality_combo, 1)

        audio_layout.addWidget(audio_title)
        audio_layout.addWidget(self.mp3_radio)
        audio_layout.addWidget(self.m4a_radio)
        audio_layout.addLayout(audio_quality_layout)

        folder_card = Card()
        folder_layout = QVBoxLayout(folder_card)
        folder_layout.setContentsMargins(16, 16, 16, 16)
        folder_layout.setSpacing(10)

        folder_title = QLabel(t["folder_title"])
        folder_title.setObjectName("SectionTitle")

        folder_row = QHBoxLayout()
        folder_row.setSpacing(10)

        self.folder = QLineEdit()
        self.folder.setMinimumHeight(46)
        self.folder.setText(self.window.download_folder())

        choose = QPushButton(t["choose_folder"])
        choose.setMinimumHeight(46)
        choose.clicked.connect(self.choose_folder)

        folder_row.addWidget(self.folder, 1)
        folder_row.addWidget(choose)

        folder_layout.addWidget(folder_title)
        folder_layout.addLayout(folder_row)

        buttons = QHBoxLayout()
        buttons.setSpacing(10)

        self.download_btn = QPushButton(t["download_btn"])
        self.download_btn.setObjectName("Primary")
        self.download_btn.setMinimumHeight(48)
        self.download_btn.clicked.connect(self.start_download)

        self.stop_btn = QPushButton(t["stop_btn"])
        self.stop_btn.setMinimumHeight(48)
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_download)

        buttons.addWidget(self.download_btn)
        buttons.addWidget(self.stop_btn)

        self.progress = QProgressBar()
        self.progress.setMinimumHeight(26)
        self.progress.setValue(0)
        self.progress.setTextVisible(True)

        self.status = QLabel(t["status_ready"])
        self.status.setObjectName("Muted")
        self.status.setWordWrap(True)

        self.recent = RecentList(self.window, t["recent_title"])

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(self.url)
        layout.addWidget(self.mode_card)
        layout.addWidget(self.quality_card)
        layout.addWidget(self.audio_card)
        layout.addWidget(folder_card)
        layout.addLayout(buttons)
        layout.addWidget(self.progress)
        layout.addWidget(self.status)
        layout.addWidget(self.recent)
        layout.addStretch()

        self.update_mode()

    def clear_quality_grid(self) -> None:
        while self.quality_grid.count():
            item = self.quality_grid.takeAt(0)
            widget = item.widget()

            if widget:
                self.quality_group.removeButton(widget)
                widget.deleteLater()

    def rebuild_quality_buttons(self) -> None:
        self.clear_quality_grid()

        if self.window.settings["downloads"].get("show_high_res_options", False):
            qualities = [
                ("Лучшее", None),
                ("8K", 4320),
                ("4K", 2160),
                ("2K", 1440),
                ("1080p", 1080),
                ("720p", 720),
                ("480p", 480),
                ("360p", 360),
            ]
        else:
            qualities = [
                ("Лучшее", None),
                ("1080p", 1080),
                ("720p", 720),
                ("480p", 480),
                ("360p", 360),
            ]

        columns = 4

        for i, (name, height) in enumerate(qualities):
            btn = QualityButton(name, height)
            btn.toggled.connect(lambda checked, b=btn: self.set_quality(b, checked))

            self.quality_group.addButton(btn)
            self.quality_grid.addWidget(btn, i // columns, i % columns)

            if i == 0:
                btn.setChecked(True)

        for col in range(columns):
            self.quality_grid.setColumnStretch(col, 1)

    def set_quality(self, button: QualityButton, checked: bool) -> None:
        if checked:
            self.selected_quality = button.height_value

    def refresh_recent(self) -> None:
        self.recent.refresh()

    def update_mode(self) -> None:
        is_video = self.video_radio.isChecked()
        self.quality_card.setVisible(is_video)
        self.audio_card.setVisible(not is_video)

    def choose_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(
            self,
            "Выбрать папку загрузок",
            str(app_path(self.folder.text())),
            QFileDialog.Option.DontUseNativeDialog
        )

        if folder:
            self.folder.setText(folder)

    def check_tools(self) -> bool:
        missing = []

        if not YTDLP.exists():
            missing.append(str(YTDLP))

        if not FFMPEG.exists():
            missing.append(str(FFMPEG))

        if missing:
            QMessageBox.critical(
                self,
                "Не найдены инструменты",
                "Не найдены файлы:\n\n" + "\n".join(missing) + "\n\nПоложи их в папку bin."
            )
            return False

        return True

    def video_command(self, url: str, folder: Path) -> list[str]:
        if self.selected_quality is None:
            fmt = (
                "bv*[vcodec^=avc1][ext=mp4][height>=360]+ba[ext=m4a]/"
                "bv*[ext=mp4][height>=360]+ba[ext=m4a]/"
                "b[ext=mp4][height>=360]/"
                "b[height>=360]/b"
            )
        else:
            h = self.selected_quality
            fmt = (
                f"bv*[vcodec^=avc1][ext=mp4][height<={h}][height>=360]+ba[ext=m4a]/"
                f"bv*[ext=mp4][height<={h}][height>=360]+ba[ext=m4a]/"
                f"b[ext=mp4][height<={h}][height>=360]/"
                f"b[height<={h}][height>=360]/b"
            )

        output = str(folder / "%(title).200s.%(ext)s")

        return [
            str(YTDLP),
            "--newline",
            "--no-playlist",
            "--ffmpeg-location",
            str(BIN),
            "-f",
            fmt,
            "--merge-output-format",
            "mp4",
            "-o",
            output,
            url
        ]

    def audio_command(self, url: str, folder: Path) -> list[str]:
        audio_format = "m4a" if self.m4a_radio.isChecked() else "mp3"
        output = str(folder / "%(title).200s.%(ext)s")
        audio_quality = self.audio_quality_combo.currentText()

        return [
            str(YTDLP),
            "--newline",
            "--no-playlist",
            "--ffmpeg-location",
            str(BIN),
            "-x",
            "--audio-format",
            audio_format,
            "--audio-quality",
            audio_quality,
            "-o",
            output,
            url
        ]

    def start_download(self) -> None:
        if self.process is not None:
            t = self.window.get_text()
            QMessageBox.warning(self, t["error_download_title"], "Сначала останови текущую загрузку." if self.window.get_lang() == "ru" else "Stop current download first.")
            return

        url = self.url.text().strip()
        t = self.window.get_text()

        if not url:
            QMessageBox.warning(self, t["error_url_title"], t["error_url_msg"])
            return

        if not self.check_tools():
            return

        folder = app_path(self.folder.text())
        folder.mkdir(parents=True, exist_ok=True)
        self.current_folder = folder

        self.window.settings["downloads"]["download_folder"] = self.folder.text().strip() or "downloads"
        self.window.settings["downloads"]["default_mode"] = "video" if self.video_radio.isChecked() else "audio"
        self.window.settings["audio"]["format"] = "m4a" if self.m4a_radio.isChecked() else "mp3"
        self.window.settings["audio"]["quality"] = self.audio_quality_combo.currentText()
        save_settings(self.window.settings)

        if self.video_radio.isChecked():
            command = self.video_command(url, folder)
        else:
            command = self.audio_command(url, folder)

        self.window.logger.write("")
        self.window.logger.write("=== Download started ===")
        self.window.logger.write(" ".join(f'"{x}"' if " " in x else x for x in command))
        self.window.logger.write("")

        self.process = QProcess(self)
        self.process.setProgram(command[0])
        self.process.setArguments(command[1:])
        self.process.setProcessChannelMode(QProcess.MergedChannels)

        self.process.readyReadStandardOutput.connect(self.on_output)
        self.process.finished.connect(self.on_finished)
        self.process.errorOccurred.connect(self.on_error)

        self.progress.setValue(0)
        self.status.setText(t["downloading"])
        self.download_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

        self.process.start()

    def stop_download(self) -> None:
        if self.process and self.process.state() != QProcess.NotRunning:
            self.process.kill()
            t = self.window.get_text()
            self.status.setText(t["stopped"])
            self.window.logger.write("Download stopped by user.")
            self.stop_btn.setEnabled(False)

    def on_output(self) -> None:
        if not self.process:
            return

        data = bytes(self.process.readAllStandardOutput()).decode("utf-8", errors="replace")

        if not data:
            return

        self.window.logger.block(data)
        t = self.window.get_text()

        for line in data.splitlines():
            match = re.search(r"\[download\]\s+(\d+(?:\.\d+)?)%", line)

            if match:
                percent = int(float(match.group(1)))
                percent = max(0, min(100, percent))
                self.progress.setValue(percent)
                self.status.setText(f"{t['downloading']} {percent}%")

            if "[Merger]" in line:
                self.status.setText("Объединение видео и аудио..." if self.window.get_lang() == "ru" else "Merging video and audio...")

            if "[ExtractAudio]" in line:
                self.status.setText("Извлечение аудио..." if self.window.get_lang() == "ru" else "Extracting audio...")

    def on_finished(self, exit_code: int, exit_status) -> None:
        t = self.window.get_text()
        if exit_code == 0:
            self.progress.setValue(100)
            self.status.setText(t["finished"])

            if self.current_folder:
                file = newest_file(self.current_folder)

                if file:
                    add_recent(self.window.settings, file)
                    self.window.refresh_recent()

            self.window.tray_msg(t["app_title"], t["finished"])
            self.window.logger.write("=== Download finished ===")
        else:
            self.status.setText(f"{t['error_download_title']}. Код: {exit_code}." if self.window.get_lang() == "ru" else f"Download error. Code: {exit_code}.")
            self.window.tray_msg(t["app_title"], t["error_download_title"])
            self.window.logger.write(f"=== Download failed: {exit_code} ===")

        self.process = None
        self.download_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

    def on_error(self) -> None:
        t = self.window.get_text()
        self.status.setText("Ошибка запуска yt-dlp." if self.window.get_lang() == "ru" else "yt-dlp launch error.")
        self.window.logger.write("QProcess error.")

        self.process = None
        self.download_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)


class HistoryPage(QWidget):
    def __init__(self, window: "MainWindow"):
        super().__init__()
        self.window = window

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)

        t = self.window.get_text()

        title = QLabel(t["history_title"])
        title.setObjectName("PageTitle")

        subtitle = QLabel(t["recent_title"])
        subtitle.setObjectName("Muted")
        subtitle.setWordWrap(True)

        self.recent = RecentList(self.window, t["recent_title"])

        open_folder = QPushButton(t["open_folder_btn"])
        open_folder.setObjectName("Primary")
        open_folder.setMinimumHeight(48)
        open_folder.clicked.connect(self.open_folder)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(self.recent)
        layout.addWidget(open_folder)
        layout.addStretch()

    def refresh(self) -> None:
        self.recent.refresh()

    def open_folder(self) -> None:
        folder = app_path(self.window.settings["downloads"].get("download_folder", "downloads"))
        folder.mkdir(parents=True, exist_ok=True)
        open_path(folder)


class SettingsPage(QWidget):
    def __init__(self, window: "MainWindow"):
        super().__init__()
        self.window = window

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)

        t = self.window.get_text()

        title = QLabel(t["settings_title"])
        title.setObjectName("PageTitle")

        subtitle = QLabel(t["settings_general"])
        subtitle.setObjectName("Muted")
        subtitle.setWordWrap(True)

        card = Card()
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 16, 16, 16)
        card_layout.setSpacing(12)

        folder_label = QLabel(t["folder_title"])
        folder_label.setObjectName("SectionTitle")

        folder_row = QHBoxLayout()
        folder_row.setSpacing(10)

        self.folder = QLineEdit()
        self.folder.setMinimumHeight(46)
        self.folder.setText(self.window.download_folder())

        choose = QPushButton(t["choose_folder"])
        choose.setMinimumHeight(46)
        choose.clicked.connect(self.choose_folder)

        folder_row.addWidget(self.folder, 1)
        folder_row.addWidget(choose)

        self.high_res = QCheckBox(t["show_high_res"])
        self.high_res.setChecked(
            bool(self.window.settings["downloads"].get("show_high_res_options", False))
        )

        # Выбор языка
        lang_label = QLabel(t["language"])
        lang_label.setObjectName("SectionTitle")
        self.lang_combo = QComboBox()
        self.lang_combo.addItem(t["language_ru"], "ru")
        self.lang_combo.addItem(t["language_en"], "en")
        current_lang = self.window.settings["app"].get("language", "ru")
        for i in range(self.lang_combo.count()):
            if self.lang_combo.itemData(i) == current_lang:
                self.lang_combo.setCurrentIndex(i)
                break

        audio_quality_label = QLabel(t["audio_title"])
        audio_quality_label.setObjectName("SectionTitle")
        self.audio_quality_combo = QComboBox()
        self.audio_quality_combo.addItems(["128K", "192K", "256K", "320K"])
        current_quality = self.window.settings["audio"].get("quality", "192K")
        idx = self.audio_quality_combo.findText(current_quality)
        if idx >= 0:
            self.audio_quality_combo.setCurrentIndex(idx)

        save = QPushButton(t["save_btn"])
        save.setObjectName("Primary")
        save.setMinimumHeight(48)
        save.clicked.connect(self.save)

        open_settings = QPushButton("Open settings.json")
        open_settings.setMinimumHeight(44)
        open_settings.clicked.connect(lambda: open_path(SETTINGS_FILE))

        open_logs = QPushButton("Open logs" if self.window.get_lang() == "en" else "Открыть логи")
        open_logs.setMinimumHeight(44)
        open_logs.clicked.connect(lambda: open_path(logs_dir(self.window.settings)))

        self.info = QLabel()
        self.info.setObjectName("Muted")
        self.info.setWordWrap(True)

        card_layout.addWidget(folder_label)
        card_layout.addLayout(folder_row)
        card_layout.addWidget(self.high_res)
        card_layout.addWidget(lang_label)
        card_layout.addWidget(self.lang_combo)
        card_layout.addWidget(audio_quality_label)
        card_layout.addWidget(self.audio_quality_combo)
        card_layout.addWidget(save)
        card_layout.addWidget(open_settings)
        card_layout.addWidget(open_logs)
        card_layout.addWidget(self.info)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(card)
        layout.addStretch()

        self.update_info()

    def choose_folder(self) -> None:
        t = self.window.get_text()
        folder = QFileDialog.getExistingDirectory(
            self,
            t["folder_title"],
            str(app_path(self.folder.text())),
            QFileDialog.Option.DontUseNativeDialog
        )

        if folder:
            self.folder.setText(folder)

    def save(self) -> None:
        self.window.settings["downloads"]["download_folder"] = self.folder.text().strip() or "downloads"
        self.window.settings["downloads"]["show_high_res_options"] = self.high_res.isChecked()
        self.window.settings["audio"]["quality"] = self.audio_quality_combo.currentText()
        # Сохранение выбранного языка
        lang_index = self.lang_combo.currentIndex()
        self.window.settings["app"]["language"] = self.lang_combo.itemData(lang_index)
        save_settings(self.window.settings)

        self.window.download_page.rebuild_quality_buttons()
        self.window.download_page.folder.setText(self.window.download_folder())
        self.window.download_page.audio_quality_combo.setCurrentText(self.audio_quality_combo.currentText())
        self.update_info()

        t = self.window.get_text()
        QMessageBox.information(self, t["saved_title"], t["saved_msg"])

    def update_info(self) -> None:
        lang = self.window.get_lang()
        self.info.setText(
            f"yt-dlp.exe: {'найден' if YTDLP.exists() else 'not found'}\n"
            f"ffmpeg.exe: {'найден' if FFMPEG.exists() else 'not found'}\n"
            f"ffprobe.exe: {'найден' if FFPROBE.exists() else 'not found'}\n"
            f"{'Логи' if lang == 'ru' else 'Logs'}: {logs_dir(self.window.settings)}"
        )


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.settings = load_settings()
        self.logger = Logger(self.settings)

        cleanup_logs(self.settings)

        t = self.get_text()

        self.setWindowTitle(t["app_title"])
        self.resize(1040, 680)
        self.setMinimumSize(820, 560)

        # Установка иконок
        icon = self.style().standardIcon(QStyle.SP_MediaPlay)
        self.setWindowIcon(icon)

        self.tray = QSystemTrayIcon(self)
        self.tray.setIcon(icon)
        self.tray.setToolTip(t["app_title"])
        self.setup_tray()

        self.cleanup_timer = QTimer(self)
        self.cleanup_timer.timeout.connect(self.cleanup_logs)

        try:
            minutes = int(self.settings["logs"].get("cleanup_interval_minutes", 60))
        except Exception:
            minutes = 60

        self.cleanup_timer.start(max(1, minutes) * 60 * 1000)

        background = QWidget()
        background.setObjectName("Background")

        background_layout = QHBoxLayout(background)
        background_layout.setContentsMargins(14, 14, 14, 14)

        shell = QFrame()
        shell.setObjectName("Shell")

        shell_layout = QHBoxLayout(shell)
        shell_layout.setContentsMargins(0, 0, 0, 0)
        shell_layout.setSpacing(0)

        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(220)

        side_layout = QVBoxLayout(sidebar)
        side_layout.setContentsMargins(14, 18, 14, 18)
        side_layout.setSpacing(10)

        logo = QLabel(t["logo"])
        logo.setObjectName("Logo")

        desc = QLabel(t["subtitle"])
        desc.setObjectName("Muted")

        side_layout.addWidget(logo)
        side_layout.addWidget(desc)
        side_layout.addSpacing(18)

        self.stack = QStackedWidget()
        self.stack.setObjectName("Stack")

        self.download_page = DownloadPage(self)
        self.history_page = HistoryPage(self)
        self.settings_page = SettingsPage(self)

        self.stack.addWidget(make_scroll_page(self.download_page))
        self.stack.addWidget(make_scroll_page(self.history_page))
        self.stack.addWidget(make_scroll_page(self.settings_page))

        self.nav_buttons = []

        self.add_nav(side_layout, t["nav_download"], 0, self.style().standardIcon(QStyle.SP_ArrowDown))
        self.add_nav(side_layout, t["nav_history"], 1, self.style().standardIcon(QStyle.SP_DirOpenIcon))
        self.add_nav(side_layout, t["nav_settings"], 2, self.style().standardIcon(QStyle.SP_FileDialogDetailedView))

        side_layout.addStretch()

        exit_btn = QPushButton(t["exit"])
        exit_btn.setMinimumHeight(44)
        exit_btn.clicked.connect(QApplication.quit)
        side_layout.addWidget(exit_btn)

        shell_layout.addWidget(sidebar)
        shell_layout.addWidget(self.stack, 1)

        background_layout.addWidget(shell)
        self.setCentralWidget(background)

        self.nav_buttons[0].setChecked(True)

        self.apply_style()
        self.logger.write("Application ready.")

    def get_lang(self) -> str:
        return self.settings["app"].get("language", "ru")

    def get_text(self) -> dict:
        lang = self.get_lang()
        return TRANSLATIONS.get(lang, TRANSLATIONS["ru"])

    def download_folder(self) -> str:
        return self.settings["downloads"].get("download_folder", "downloads")

    def add_nav(self, layout: QVBoxLayout, text: str, index: int, icon: QIcon = None) -> None:
        btn = NavButton(text, icon)
        btn.clicked.connect(lambda checked=False, i=index: self.switch(i))
        layout.addWidget(btn)
        self.nav_buttons.append(btn)

    def switch(self, index: int) -> None:
        self.stack.setCurrentIndex(index)

        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)

        if index == 1:
            self.history_page.refresh()

        if index == 2:
            self.settings_page.update_info()

    def refresh_recent(self) -> None:
        self.download_page.refresh_recent()
        self.history_page.refresh()

    def setup_tray(self) -> None:
        menu = QMenu()
        t = self.get_text()

        open_action = QAction(t["tray_open"], self)
        open_action.triggered.connect(self.show_window)

        logs_action = QAction(t["tray_logs"], self)
        logs_action.triggered.connect(lambda: open_path(logs_dir(self.settings)))

        exit_action = QAction(t["tray_exit"], self)
        exit_action.triggered.connect(QApplication.quit)

        menu.addAction(open_action)
        menu.addAction(logs_action)
        menu.addSeparator()
        menu.addAction(exit_action)

        self.tray.setContextMenu(menu)
        self.tray.show()

    def show_window(self) -> None:
        self.show()
        self.raise_()
        self.activateWindow()

    def tray_msg(self, title: str, text: str) -> None:
        if self.tray.isVisible():
            self.tray.showMessage(title, text, QSystemTrayIcon.Information, 3000)

    def cleanup_logs(self) -> None:
        cleanup_logs(self.settings)
        self.logger.write("Log cleanup completed.")

    def closeEvent(self, event) -> None:
        t = self.get_text()
        if self.settings["app"].get("close_to_tray", True):
            event.ignore()
            self.hide()
            self.tray_msg(t["tray_msg_title"], t["tray_msg_text"])
            self.logger.write("Window hidden to tray.")
        else:
            event.accept()

    def apply_style(self) -> None:
        self.setStyleSheet("""
            * {
                outline: 0;
            }

            QWidget {
                background: #1A1A1A;
                color: #F0F0F0;
                font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
                font-size: 14px;
            }

            #Background {
                background: #1A1A1A;
            }

            #Shell {
                background: #232323;
                border: 1px solid #3A3A3C;
                border-radius: 10px;
            }

            #Sidebar {
                background: #1C1C1C;
                border-right: 1px solid #333333;
                border-top-left-radius: 10px;
                border-bottom-left-radius: 10px;
            }

            #Stack {
                background: #232323;
                border: none;
                border-top-right-radius: 10px;
                border-bottom-right-radius: 10px;
            }

            #PageScroll {
                background: transparent;
                border: none;
            }

            #PageScroll QWidget {
                background: transparent;
            }

            #Logo {
                background: transparent;
                color: white;
                font-size: 26px;
                font-weight: 800;
            }

            #PageTitle {
                background: transparent;
                color: white;
                font-size: 30px;
                font-weight: 800;
            }

            #SectionTitle {
                background: transparent;
                color: white;
                font-size: 15px;
                font-weight: 700;
                margin-bottom: 4px;
            }

            #Muted {
                background: transparent;
                color: #A9A9B2;
            }

            #Card {
                background: #2C2C2E;
                border: 1px solid #3C3C40;
                border-radius: 10px;
            }

            #RecentRow {
                background: #2A2A2C;
                border: 1px solid #3A3A3D;
                border-radius: 8px;
            }

            #RecentText {
                background: transparent;
                color: #F0F0F0;
            }

            QPushButton {
                background: #38383A;
                color: white;
                border: 1px solid #4A4A50;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: 600;
            }

            QPushButton:hover {
                background: #48484C;
                border-color: #5A5A62;
            }

            QPushButton:pressed {
                background: #2C2C2E;
            }

            QPushButton:checked {
                background: #0A84FF;
                border-color: #0A84FF;
                color: white;
            }

            QPushButton:disabled {
                background: #2A2A2D;
                color: #777780;
                border-color: #3A3A3D;
            }

            #Primary {
                background: #0A84FF;
                border-color: #0A84FF;
                color: white;
            }

            #Primary:hover {
                background: #2B94FF;
            }

            QLineEdit {
                background: #1C1C1E;
                color: white;
                border: 1px solid #4A4A50;
                border-radius: 8px;
                padding: 9px 12px;
                selection-background-color: #0A84FF;
            }

            QLineEdit:hover {
                border-color: #62626A;
            }

            QLineEdit:focus {
                border-color: #0A84FF;
            }

            QRadioButton,
            QCheckBox {
                background: transparent;
                color: #F0F0F0;
                spacing: 10px;
                padding: 7px;
                border-radius: 6px;
            }

            QRadioButton:hover,
            QCheckBox:hover {
                background: #333336;
            }

            QRadioButton#QualityButton {
                background: #1C1C1E;
                border: 1px solid #4A4A50;
                border-radius: 8px;
                padding: 8px 12px;
                min-width: 82px;
                font-weight: 600;
            }

            QRadioButton#QualityButton:hover {
                border-color: #62626A;
                background: #2A2A2D;
            }

            QRadioButton#QualityButton:checked {
                background: #0A84FF;
                border-color: #0A84FF;
                color: white;
            }

            QRadioButton#QualityButton::indicator {
                width: 0px;
                height: 0px;
            }

            QRadioButton::indicator {
                width: 18px;
                height: 18px;
                border: 1px solid #686870;
                border-radius: 9px;
                background: #1C1C1E;
            }

            QRadioButton::indicator:checked {
                background: #0A84FF;
                border: 1px solid #0A84FF;
            }

            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 1px solid #686870;
                border-radius: 4px;
                background: #1C1C1E;
            }

            QCheckBox::indicator:checked {
                background: #0A84FF;
                border: 1px solid #0A84FF;
            }

            QProgressBar {
                background: #1C1C1E;
                color: white;
                border: 1px solid #4A4A50;
                border-radius: 8px;
                text-align: center;
                font-weight: bold;
            }

            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #0A84FF, stop:1 #2B94FF);
                border-radius: 7px;
            }

            QComboBox {
                background: #1C1C1E;
                color: white;
                border: 1px solid #4A4A50;
                border-radius: 8px;
                padding: 8px 12px;
                min-height: 20px;
            }

            QComboBox:hover {
                border-color: #62626A;
            }

            QComboBox QAbstractItemView {
                background: #2C2C2E;
                border: 1px solid #4A4A50;
                selection-background-color: #0A84FF;
                color: white;
            }

            QMenu {
                background: #2C2C2E;
                color: white;
                border: 1px solid #4A4A50;
                border-radius: 8px;
                padding: 4px;
            }

            QMenu::item {
                padding: 8px 22px;
                border-radius: 4px;
            }

            QMenu::item:selected {
                background: #0A84FF;
            }

            QMessageBox {
                background: #1A1A1A;
                color: white;
            }

            QMessageBox QLabel {
                color: white;
                background: transparent;
            }

            QFileDialog {
                background: #1A1A1A;
                color: white;
            }

            QScrollBar:vertical {
                background: #232323;
                width: 12px;
                margin: 2px;
                border: none;
                border-radius: 6px;
            }

            QScrollBar::handle:vertical {
                background: #4A4A50;
                min-height: 28px;
                border-radius: 6px;
            }

            QScrollBar::handle:vertical:hover {
                background: #5A5A62;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
                background: transparent;
            }

            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: transparent;
            }

            QScrollBar:horizontal {
                background: #232323;
                height: 12px;
                margin: 2px;
                border: none;
                border-radius: 6px;
            }

            QScrollBar::handle:horizontal {
                background: #4A4A50;
                min-width: 28px;
                border-radius: 6px;
            }

            QScrollBar::handle:horizontal:hover {
                background: #5A5A62;
            }

            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal {
                width: 0px;
                background: transparent;
            }

            QScrollBar::add-page:horizontal,
            QScrollBar::sub-page:horizontal {
                background: transparent;
            }
        """)


class FirstRunDialog(QMessageBox):
    """Диалог первого запуска с установкой инструментов"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setIcon(QMessageBox.Information)
        self.setWindowTitle("Первый запуск / First Run")
        self.setText("📦 Установка компонентов...\n\nПриложение загрузит необходимые инструменты (yt-dlp, ffmpeg).\nЭто займёт несколько минут.")
        self.setStandardButtons(QMessageBox.NoButton)
        
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)  # Бесконечная анимация
        self.layout().addWidget(self.progress)


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setStyle("Fusion")
    apply_dark_palette(app)

    # Загружаем настройки
    settings = load_settings()
    
    # Проверяем, нужна ли установка инструментов
    first_run = settings.get("app", {}).get("first_run", True)
    ytdlp_installed, ffmpeg_installed = check_tools_installed()
    
    if first_run or not ytdlp_installed or not ffmpeg_installed:
        # Показываем диалог установки
        install_dialog = FirstRunDialog()
        install_dialog.show()
        
        # Запускаем установку в отдельном потоке
        installer = ToolsInstaller()
        installer.progress_signal.connect(lambda msg: print(f"Installing: {msg}"))
        
        def on_install_finished(success):
            install_dialog.close()
            if success:
                # Обновляем настройки
                settings["tools"]["ytdlp_installed"] = True
                settings["tools"]["ffmpeg_installed"] = True
                settings["app"]["first_run"] = False
                save_settings(settings)
                
                # Показываем сообщение об успехе
                QMessageBox.information(None, "✅ Готово!", 
                    "Компоненты успешно установлены!\n\nComponents installed successfully!")
            else:
                QMessageBox.critical(None, "❌ Ошибка", 
                    "Не удалось установить компоненты.\nПопробуйте вручную загрузить yt-dlp и ffmpeg.\n\nFailed to install components.")
            # Запускаем основное окно
            window = MainWindow()
            window.show()
        
        installer.finished_signal.connect(on_install_finished)
        installer.start()
    else:
        # Инструменты уже установлены, запускаем приложение
        window = MainWindow()
        window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
