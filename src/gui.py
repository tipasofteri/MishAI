# src/gui.py

import customtkinter as ctk
from PIL import Image
import pystray
import threading
import pyperclip
import mss
from utils import resource_path, load_config, save_config, get_string, APP_NAME

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class SettingsWindow(ctk.CTkToplevel):
    """Класс для окна настроек с вкладками."""
    def __init__(self, master, on_hotkey_save):
        super().__init__(master)
        self.on_hotkey_save = on_hotkey_save
        self.config = load_config()
        self.lang = self.config.get('Settings', 'language', fallback='ru')

        self.title(get_string('settings_title', self.lang))
        self.geometry("450x450")
        self.transient(master)
        self.grab_set()
        
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(expand=True, fill="both", padx=10, pady=10)

        self.general_tab = self.tabview.add(get_string('tab_general', self.lang))
        self.api_tab = self.tabview.add(get_string('tab_api', self.lang))

        self._create_general_tab_widgets()
        self._create_api_tab_widgets()
        self._create_buttons()
        self._load_settings()
        self._bind_paste_events() # <-- ИЗМЕНЕНО: Вызываем новую функцию

    def _bind_paste_events(self):
        """Принудительно включает вставку (Ctrl+V) для всех полей ввода."""
        for entry in [self.hotkey_entry, self.screenshot_hotkey_entry, self.gemini_api_key_entry, self.openai_api_key_entry]:
            entry.bind("<Control-v>", lambda e, w=entry: w.event_generate("<<Paste>>"))

    def _create_general_tab_widgets(self):
        frame = ctk.CTkFrame(self.general_tab)
        frame.pack(pady=10, padx=10, fill="x")
        
        ctk.CTkLabel(frame, text=get_string('label_language', self.lang)).pack(pady=5, padx=10, anchor="w")
        self.language_menu = ctk.CTkOptionMenu(frame, values=["Русский", "English"])
        self.language_menu.pack(pady=5, padx=10, fill="x")

        ctk.CTkLabel(frame, text=get_string('label_hotkey_text', self.lang)).pack(pady=5, padx=10, anchor="w")
        self.hotkey_entry = ctk.CTkEntry(frame)
        self.hotkey_entry.pack(pady=5, padx=10, fill="x")

        ctk.CTkLabel(frame, text=get_string('label_hotkey_screenshot', self.lang)).pack(pady=5, padx=10, anchor="w")
        self.screenshot_hotkey_entry = ctk.CTkEntry(frame)
        self.screenshot_hotkey_entry.pack(pady=5, padx=10, fill="x")
        
    def _create_api_tab_widgets(self):
        self.api_frame = ctk.CTkFrame(self.api_tab)
        self.api_frame.pack(pady=10, padx=10, fill="x")

        ctk.CTkLabel(self.api_frame, text=get_string('label_provider', self.lang)).pack(pady=(5,0), padx=10, anchor="w")
        self.provider_menu = ctk.CTkOptionMenu(self.api_frame, values=["gemini", "openai"], command=self._update_api_fields)
        self.provider_menu.pack(pady=5, padx=10, fill="x")

        ctk.CTkLabel(self.api_frame, text=get_string('label_model', self.lang)).pack(pady=(5,0), padx=10, anchor="w")
        self.model_menu = ctk.CTkOptionMenu(self.api_frame, values=[])
        self.model_menu.pack(pady=5, padx=10, fill="x")

        self.gemini_key_frame = ctk.CTkFrame(self.api_frame, fg_color="transparent")
        ctk.CTkLabel(self.gemini_key_frame, text=get_string('label_gemini_api_key', self.lang)).pack(pady=(5,0), padx=10, anchor="w")
        self.gemini_api_key_entry = ctk.CTkEntry(self.gemini_key_frame, show="*")
        self.gemini_api_key_entry.pack(pady=5, padx=10, fill="x")

        self.openai_key_frame = ctk.CTkFrame(self.api_frame, fg_color="transparent")
        ctk.CTkLabel(self.openai_key_frame, text=get_string('label_openai_api_key', self.lang)).pack(pady=(5,0), padx=10, anchor="w")
        self.openai_api_key_entry = ctk.CTkEntry(self.openai_key_frame, show="*")
        self.openai_api_key_entry.pack(pady=5, padx=10, fill="x")

    def _update_api_fields(self, provider):
        gemini_models = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-1.0-pro"]
        openai_models = ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"]
        
        if provider == 'gemini':
            self.model_menu.configure(values=gemini_models)
            self.gemini_key_frame.pack(pady=5, padx=0, fill="x")
            self.openai_key_frame.pack_forget()
        else:
            self.model_menu.configure(values=openai_models)
            self.openai_key_frame.pack(pady=5, padx=0, fill="x")
            self.gemini_key_frame.pack_forget()
        
        current_model = self.config.get('Settings', 'model')
        available_models = self.model_menu.cget("values")
        if current_model not in available_models:
            self.model_menu.set(available_models[0])
        else:
            self.model_menu.set(current_model)

    def _create_buttons(self):
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(side="bottom", fill="x", padx=10, pady=10)
        button_frame.grid_columnconfigure((0, 1), weight=1)

        save_button = ctk.CTkButton(button_frame, text=get_string('button_save', self.lang), command=self._save_settings)
        save_button.grid(row=0, column=0, padx=5, sticky="ew")

        cancel_button = ctk.CTkButton(button_frame, text=get_string('button_cancel', self.lang), command=self.destroy, fg_color="gray")
        cancel_button.grid(row=0, column=1, padx=5, sticky="ew")

    def _load_settings(self):
        lang_map = {'ru': 'Русский', 'en': 'English'}
        current_lang_code = self.config.get('Settings', 'language', fallback='ru')
        self.language_menu.set(lang_map.get(current_lang_code, 'Русский'))
        
        self.hotkey_entry.insert(0, self.config.get('Settings', 'hotkey', fallback='ctrl+shift+q'))
        self.screenshot_hotkey_entry.insert(0, self.config.get('Settings', 'screenshot_hotkey', fallback='ctrl+shift+s'))
        
        provider = self.config.get('Settings', 'provider', fallback='gemini')
        self.provider_menu.set(provider)
        
        self.gemini_api_key_entry.insert(0, self.config.get('API', 'gemini_key', fallback=''))
        self.openai_api_key_entry.insert(0, self.config.get('API', 'openai_key', fallback=''))

        self._update_api_fields(provider)

    def _save_settings(self):
        lang_map_rev = {'Русский': 'ru', 'English': 'en'}
        new_lang_code = lang_map_rev.get(self.language_menu.get(), 'ru')
        
        text_hotkey = self.hotkey_entry.get()
        screenshot_hotkey = self.screenshot_hotkey_entry.get()
        
        self.config.set('Settings', 'language', new_lang_code)
        self.config.set('Settings', 'hotkey', text_hotkey)
        self.config.set('Settings', 'screenshot_hotkey', screenshot_hotkey)
        self.config.set('Settings', 'provider', self.provider_menu.get())
        self.config.set('Settings', 'model', self.model_menu.get())
        self.config.set('API', 'gemini_key', self.gemini_api_key_entry.get())
        self.config.set('API', 'openai_key', self.openai_api_key_entry.get())
        
        save_config(self.config)
        
        if self.on_hotkey_save:
            self.on_hotkey_save(text_hotkey, screenshot_hotkey)
            
        self.destroy()

class AppGUI:
    def __init__(self, on_hotkey_save=None):
        self.is_running = True
        self.on_hotkey_save = on_hotkey_save
        self.settings_window = None
        self.selection_overlay = None
        
        self.root = ctk.CTk()
        self.root.withdraw()
        self.root.title(APP_NAME)
        self.root.geometry("500x400")
        
        self.root.protocol("WM_DELETE_WINDOW", self.hide_window)
        self.root.bind("<Escape>", self.hide_window)
        
        self.response_textbox = ctk.CTkTextbox(self.root, wrap="word", font=("Arial", 14))
        self.response_textbox.pack(expand=True, fill="both", padx=10, pady=10)
        self.response_textbox.configure(state="disabled")

    def start_region_selection(self, callback):
        if self.selection_overlay and self.selection_overlay.winfo_exists():
            self.selection_overlay.focus()
            return
        self.selection_overlay = SelectionOverlay(self.root, on_selection_complete=callback)

    def show_loading_window(self):
        lang = load_config().get('Settings', 'language', fallback='ru')
        self._update_textbox(get_string('loading_message', lang), copy=False)
        self._center_and_show_window()

    def show_response_window(self, text):
        self._update_textbox(text, copy=True)
        self._center_and_show_window()

    def _update_textbox(self, text, copy=False):
        if copy:
            try:
                pyperclip.copy(text)
                print("Response copied to clipboard.")
            except Exception as e:
                print(f"Failed to copy to clipboard: {e}")
        
        self.response_textbox.configure(state="normal")
        self.response_textbox.delete("1.0", "end")
        self.response_textbox.insert("1.0", text)
        self.response_textbox.configure(state="disabled")

    def _center_and_show_window(self):
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (self.root.winfo_width() // 2)
        y = (screen_height // 2) - (self.root.winfo_height() // 2)
        self.root.geometry(f"+{x}+{y}")
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def hide_window(self, event=None):
        self.root.withdraw()

    def _schedule_settings_window(self):
        """Безопасно вызывает окно настроек из основного потока GUI."""
        self.root.after(0, self.show_settings_window)

    def show_settings_window(self):
        """Создает и показывает окно настроек. Вызывается из основного потока."""
        if self.settings_window is None or not self.settings_window.winfo_exists():
            self.settings_window = SettingsWindow(self.root, self.on_hotkey_save)
        self.settings_window.focus()

    def setup_tray_icon(self):
        try:
            image = Image.open(resource_path("assets/icon.png"))
        except FileNotFoundError:
            image = Image.new('RGB', (64, 64), color='blue')
        
        lang = load_config().get('Settings', 'language', fallback='ru')
        menu = (
            pystray.MenuItem(get_string('tray_settings', lang), self._schedule_settings_window),
            pystray.MenuItem(get_string('tray_exit', lang), self.quit_app)
        )
        icon = pystray.Icon(APP_NAME, image, APP_NAME, menu)
        icon.run()
        
    def run(self):
        threading.Thread(target=self.setup_tray_icon, daemon=True).start()
        self.root.mainloop()

    def _schedule_quit(self):
        """Безопасно планирует выход из приложения в основном потоке."""
        self.is_running = False
        self.root.after(0, self.root.destroy)

    def quit_app(self, icon, item=None):
        """Корректно завершает работу приложения."""
        icon.stop()
        self._schedule_quit()

class SelectionOverlay(ctk.CTkToplevel):
    def __init__(self, master, on_selection_complete):
        super().__init__(master)
        self.on_selection_complete = on_selection_complete
        self.start_x = None
        self.start_y = None
        self.rect = None
        self.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}+0+0")
        self.overrideredirect(True)
        self.attributes("-alpha", 0.3)
        self.attributes("-topmost", True)
        self.configure(cursor="crosshair")
        self.canvas = ctk.CTkCanvas(self, highlightthickness=0, bg="black")
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        self.bind("<Escape>", self.cancel_selection)

    def on_button_press(self, event):
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)
        if self.rect: self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline='red', width=2)

    def on_mouse_drag(self, event):
        cur_x, cur_y = (self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))
        self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)

    def on_button_release(self, event):
        self.withdraw()
        end_x, end_y = (self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))
        left, top = int(min(self.start_x, end_x)), int(min(self.start_y, end_y))
        width, height = int(abs(end_x - self.start_x)), int(abs(end_y - self.start_y))
        if width > 5 and height > 5:
            with mss.mss() as sct:
                sct_img = sct.grab({"top": top, "left": left, "width": width, "height": height})
                self.on_selection_complete(Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX"))
        else: self.on_selection_complete(None)
        self.destroy()

    def cancel_selection(self, event=None):
        self.on_selection_complete(None)
        self.destroy()
