# This file is part of YouWizard.
#
# YouWizard is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# YouWizard is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with YouWizard.  If not, see <https://www.gnu.org/licenses/>.

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys
from logic import AppLogic, LanguageManager

class ModernStyle:
    """Современный стиль для приложения"""
    COLORS = {
        'bg': '#2b2b2b',
        'fg': '#ffffff',
        'accent': '#4a90e2',
        'accent_hover': '#357abd',
        'header': '#1f1f1f',
        'entry_bg': '#3c3c3c',
        'entry_fg': '#ffffff',
        'button_fg': '#ffffff'
    }
    
    FONTS = {
        'title': ('Segoe UI', 14, 'bold'),
        'normal': ('Segoe UI', 10),
        'button': ('Segoe UI', 10, 'bold')
    }

class LanguageDialog(tk.Toplevel):
    """Диалог выбора языка"""
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.callback = callback
        self.title("Select Language / Выберите язык")
        self.geometry("400x250")
        self.resizable(False, False)
        
        # Центрирование окна
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 400) // 2
        y = (self.winfo_screenheight() - 250) // 2
        self.geometry(f"400x250+{x}+{y}")
        
        # Убираем стандартные декорации и делаем модальным
        self.transient(parent)
        self.grab_set()
        
        # Стиль
        self.configure(bg=ModernStyle.COLORS['bg'])
        
        # Заголовок
        title_label = tk.Label(
            self, 
            text="Select Interface Language\nВыберите язык интерфейса",
            font=ModernStyle.FONTS['title'],
            bg=ModernStyle.COLORS['bg'],
            fg=ModernStyle.COLORS['fg']
        )
        title_label.pack(pady=30)
        
        # Фрейм для кнопок
        btn_frame = tk.Frame(self, bg=ModernStyle.COLORS['bg'])
        btn_frame.pack(pady=20)
        
        # Кнопка English
        self.btn_en = self.create_modern_button(
            btn_frame, "English", lambda: self.select_language('en'),
            bg=ModernStyle.COLORS['accent']
        )
        self.btn_en.pack(pady=10, padx=20)
        
        # Кнопка Русский
        self.btn_ru = self.create_modern_button(
            btn_frame, "Русский", lambda: self.select_language('ru'),
            bg=ModernStyle.COLORS['accent']
        )
        self.btn_ru.pack(pady=10, padx=20)
    
    def create_modern_button(self, parent, text, command, bg):
        """Создание современной кнопки"""
        btn = tk.Button(
            parent,
            text=text,
            font=ModernStyle.FONTS['button'],
            bg=bg,
            fg=ModernStyle.COLORS['button_fg'],
            border=0,
            padx=30,
            pady=10,
            cursor="hand2",
            command=command
        )
        btn.bind("<Enter>", lambda e: btn.configure(bg=ModernStyle.COLORS['accent_hover']))
        btn.bind("<Leave>", lambda e: btn.configure(bg=bg))
        return btn
    
    def select_language(self, lang):
        self.callback(lang)
        self.destroy()

class HeaderBar(tk.Frame):
    """Кастомная заголовочная панель"""
    def __init__(self, parent, app_window):
        super().__init__(parent, bg=ModernStyle.COLORS['header'], height=40)
        self.app_window = app_window
        self.pack(fill=tk.X, side=tk.TOP)
        self.pack_propagate(False)
        
        # Заголовок
        self.title_label = tk.Label(
            self,
            text="YouWizard",
            font=ModernStyle.FONTS['title'],
            bg=ModernStyle.COLORS['header'],
            fg=ModernStyle.COLORS['fg']
        )
        self.title_label.pack(side=tk.LEFT, padx=15)
        
        # Контейнер для кнопок
        self.btn_frame = tk.Frame(self, bg=ModernStyle.COLORS['header'])
        self.btn_frame.pack(side=tk.RIGHT, padx=10)
        
        # Кнопки управления
        self.create_control_button("─", self.minimize)
        self.create_control_button("□", self.toggle_maximize, name="maximize_btn")
        self.create_control_button("✕", self.close_app, bg="#e81123")
        
        # Перетаскивание
        self.title_label.bind("<ButtonPress-1>", self.start_drag)
        self.title_label.bind("<B1-Motion>", self.do_drag)
        self.bind("<ButtonPress-1>", self.start_drag)
        self.bind("<B1-Motion>", self.do_drag)
        
        self.drag_x = 0
        self.drag_y = 0
        self.is_maximized = False
        self.normal_geometry = ""
    
    def create_control_button(self, text, command, bg=None, name=None):
        color = bg if bg else '#3c3c3c'
        hover_color = bg if bg else '#505050'
        
        btn = tk.Button(
            self.btn_frame,
            text=text,
            font=("Segoe UI", 12),
            bg=color,
            fg='#ffffff',
            border=0,
            width=3,
            height=1,
            cursor="hand2",
            command=command
        )
        if name:
            setattr(self, name, btn)
        btn.pack(side=tk.LEFT, padx=2)
        btn.bind("<Enter>", lambda e: btn.configure(bg=hover_color))
        btn.bind("<Leave>", lambda e: btn.configure(bg=color))
    
    def start_drag(self, event):
        if not self.is_maximized:
            self.drag_x = event.x
            self.drag_y = event.y
    
    def do_drag(self, event):
        if not self.is_maximized:
            x = self.app_window.winfo_x() + (event.x - self.drag_x)
            y = self.app_window.winfo_y() + (event.y - self.drag_y)
            self.app_window.geometry(f"+{x}+{y}")
    
    def minimize(self):
        self.app_window.iconify()
    
    def toggle_maximize(self):
        if self.is_maximized:
            self.app_window.geometry(self.normal_geometry)
            self.maximize_btn.configure(text="□")
            self.is_maximized = False
        else:
            self.normal_geometry = self.app_window.geometry()
            self.app_window.attributes('-fullscreen', True)
            self.maximize_btn.configure(text="❐")
            self.is_maximized = True
    
    def close_app(self):
        self.app_window.quit()

class MainWindow(tk.Tk):
    """Главное окно приложения"""
    def __init__(self):
        super().__init__()
        
        self.title("YouWizard")
        self.geometry("800x600")
        self.minsize(600, 400)
        self.configure(bg=ModernStyle.COLORS['bg'])
        
        # Логика приложения
        self.logic = AppLogic(self)
        self.lang_manager = LanguageManager()
        
        # Заголовочная панель
        self.header = HeaderBar(self, self)
        
        # Основной контент
        self.create_main_content()
        
        # Проверка первого запуска
        self.after(100, self.check_first_run)
    
    def create_main_content(self):
        """Создание основного контента"""
        main_frame = tk.Frame(self, bg=ModernStyle.COLORS['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # URL ввода
        url_frame = tk.Frame(main_frame, bg=ModernStyle.COLORS['bg'])
        url_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(
            url_frame,
            text=self.lang_manager.get_text("url_label"),
            font=ModernStyle.FONTS['normal'],
            bg=ModernStyle.COLORS['bg'],
            fg=ModernStyle.COLORS['fg']
        ).pack(anchor=tk.W, pady=(0, 5))
        
        self.url_entry = tk.Entry(
            url_frame,
            font=ModernStyle.FONTS['normal'],
            bg=ModernStyle.COLORS['entry_bg'],
            fg=ModernStyle.COLORS['entry_fg'],
            insertbackground='white',
            relief=tk.FLAT,
            pady=10
        )
        self.url_entry.pack(fill=tk.X, ipady=5)
        
        # Настройки
        settings_frame = tk.Frame(main_frame, bg=ModernStyle.COLORS['bg'])
        settings_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Качество
        quality_frame = tk.Frame(settings_frame, bg=ModernStyle.COLORS['bg'])
        quality_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        tk.Label(
            quality_frame,
            text=self.lang_manager.get_text("quality_label"),
            font=ModernStyle.FONTS['normal'],
            bg=ModernStyle.COLORS['bg'],
            fg=ModernStyle.COLORS['fg']
        ).pack(anchor=tk.W, pady=(0, 5))
        
        self.quality_var = tk.StringVar(value="best")
        qualities = [
            ("Best Quality", "best"),
            ("1080p", "1080"),
            ("720p", "720"),
            ("480p", "480"),
            ("360p", "360")
        ]
        
        for text, value in qualities:
            rb = tk.Radiobutton(
                quality_frame,
                text=self.lang_manager.get_text(f"quality_{value}"),
                variable=self.quality_var,
                value=value,
                font=ModernStyle.FONTS['normal'],
                bg=ModernStyle.COLORS['bg'],
                fg=ModernStyle.COLORS['fg'],
                selectcolor=ModernStyle.COLORS['accent'],
                activebackground=ModernStyle.COLORS['bg'],
                activeforeground=ModernStyle.COLORS['fg']
            )
            rb.pack(anchor=tk.W)
        
        # Папка сохранения
        folder_frame = tk.Frame(settings_frame, bg=ModernStyle.COLORS['bg'])
        folder_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))
        
        tk.Label(
            folder_frame,
            text=self.lang_manager.get_text("folder_label"),
            font=ModernStyle.FONTS['normal'],
            bg=ModernStyle.COLORS['bg'],
            fg=ModernStyle.COLORS['fg']
        ).pack(anchor=tk.W, pady=(0, 5))
        
        folder_btn_frame = tk.Frame(folder_frame, bg=ModernStyle.COLORS['bg'])
        folder_btn_frame.pack(fill=tk.X)
        
        self.folder_path = tk.StringVar()
        self.folder_entry = tk.Entry(
            folder_btn_frame,
            textvariable=self.folder_path,
            font=ModernStyle.FONTS['normal'],
            bg=ModernStyle.COLORS['entry_bg'],
            fg=ModernStyle.COLORS['entry_fg'],
            relief=tk.FLAT,
            state='readonly'
        )
        self.folder_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5)
        
        browse_btn = self.create_modern_button(
            folder_btn_frame, 
            self.lang_manager.get_text("browse_btn"),
            self.browse_folder,
            width=12
        )
        browse_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        # Кнопки действий
        action_frame = tk.Frame(main_frame, bg=ModernStyle.COLORS['bg'])
        action_frame.pack(fill=tk.X, pady=(20, 0))
        
        self.download_video_btn = self.create_modern_button(
            action_frame,
            self.lang_manager.get_text("download_video_btn"),
            self.download_video,
            bg=ModernStyle.COLORS['accent'],
            fill=tk.X
        )
        self.download_video_btn.pack(pady=(0, 10))
        
        self.download_audio_btn = self.create_modern_button(
            action_frame,
            self.lang_manager.get_text("download_audio_btn"),
            self.download_audio,
            bg='#27ae60',
            fill=tk.X
        )
        self.download_audio_btn.pack()
        
        # Статус бар
        self.status_var = tk.StringVar(value=self.lang_manager.get_text("ready_status"))
        status_label = tk.Label(
            main_frame,
            textvariable=self.status_var,
            font=ModernStyle.FONTS['normal'],
            bg=ModernStyle.COLORS['bg'],
            fg=ModernStyle.COLORS['fg']
        )
        status_label.pack(pady=(20, 0))
        
        # Прогресс бар
        self.progress = ttk.Progressbar(
            main_frame,
            mode='indeterminate',
            style='modern.Horizontal.TProgressbar'
        )
        self.progress.pack(fill=tk.X, pady=(10, 0))
        
        # Настройка стиля прогресс бара
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('modern.Horizontal.TProgressbar',
                       background=ModernStyle.COLORS['accent'],
                       troughcolor=ModernStyle.COLORS['entry_bg'],
                       borderwidth=0,
                       lightcolor=ModernStyle.COLORS['accent'],
                       darkcolor=ModernStyle.COLORS['accent'])
    
    def create_modern_button(self, parent, text, command, bg=None, width=None, fill=None):
        """Создание современной кнопки"""
        color = bg if bg else ModernStyle.COLORS['accent']
        hover_color = ModernStyle.COLORS['accent_hover'] if bg == ModernStyle.COLORS['accent'] else '#219150'
        
        btn = tk.Button(
            parent,
            text=text,
            font=ModernStyle.FONTS['button'],
            bg=color,
            fg=ModernStyle.COLORS['button_fg'],
            border=0,
            padx=20,
            pady=12,
            cursor="hand2",
            command=command
        )
        if width:
            btn.configure(width=width)
        if fill:
            btn.pack(fill=fill)
        
        btn.bind("<Enter>", lambda e: btn.configure(bg=hover_color))
        btn.bind("<Leave>", lambda e: btn.configure(bg=color))
        return btn
    
    def check_first_run(self):
        """Проверка первого запуска"""
        if not os.path.exists("config.ini"):
            self.withdraw()  # Скрываем главное окно
            dialog = LanguageDialog(self, self.on_language_selected)
            dialog.protocol("WM_DELETE_WINDOW", lambda: None)  # Запрет закрытия без выбора
    
    def on_language_selected(self, lang):
        """Обработчик выбора языка"""
        self.lang_manager.set_language(lang)
        self.deiconify()  # Показываем главное окно
        self.logic.install_tools(self.status_var, self.progress)
    
    def browse_folder(self):
        """Выбор папки для сохранения"""
        folder = filedialog.askdirectory(initialdir=self.folder_path.get() or os.path.expanduser("~/Downloads"))
        if folder:
            self.folder_path.set(folder)
    
    def download_video(self):
        """Скачивание видео"""
        url = self.url_entry.get()
        if not url:
            messagebox.showwarning("Warning", "Please enter a URL")
            return
        
        self.progress.start()
        self.status_var.set(self.lang_manager.get_text("downloading_status"))
        self.download_video_btn.configure(state='disabled')
        self.download_audio_btn.configure(state='disabled')
        
        self.logic.download(
            url,
            self.folder_path.get() or os.path.expanduser("~/Downloads"),
            self.quality_var.get(),
            'video',
            self.on_download_complete
        )
    
    def download_audio(self):
        """Скачивание аудио"""
        url = self.url_entry.get()
        if not url:
            messagebox.showwarning("Warning", "Please enter a URL")
            return
        
        self.progress.start()
        self.status_var.set(self.lang_manager.get_text("downloading_status"))
        self.download_video_btn.configure(state='disabled')
        self.download_audio_btn.configure(state='disabled')
        
        self.logic.download(
            url,
            self.folder_path.get() or os.path.expanduser("~/Downloads"),
            self.quality_var.get(),
            'audio',
            self.on_download_complete
        )
    
    def on_download_complete(self, success, message):
        """Обработчик завершения загрузки"""
        self.progress.stop()
        self.download_video_btn.configure(state='normal')
        self.download_audio_btn.configure(state='normal')
        
        if success:
            self.status_var.set(self.lang_manager.get_text("completed_status"))
            messagebox.showinfo("Success", message)
        else:
            self.status_var.set(self.lang_manager.get_text("error_status"))
            messagebox.showerror("Error", message)

if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
