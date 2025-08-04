# src/__main__.py

import keyboard
import time
import threading
import os
import cv2
import numpy as np
from ffpyplayer.player import MediaPlayer
from tkinter import messagebox, Tk
from utils import load_config, get_clipboard_text, handle_first_launch, get_string, APP_NAME, resource_path
from assistant import get_completion
from gui import AppGUI

# Для защиты от повторного запуска
try:
    import win32event
    import win32api
    from winerror import ERROR_ALREADY_EXISTS
    SINGLE_INSTANCE_SUPPORTED = True
except ImportError:
    SINGLE_INSTANCE_SUPPORTED = False
    print("Warning: pywin32 not installed. Single instance lock is disabled.")


# Глобальные переменные
text_hotkey_handler = None
screenshot_hotkey_handler = None
gui_app = None

def play_splash_screen():
    """Воспроизводит приветственное видео в центрированном окне без рамок и со звуком."""
    video_path = resource_path("assets/splash.mp4")
    if not os.path.exists(video_path):
        print("Splash screen video (splash.mp4) not found in assets. Skipping.")
        return

    try:
        cap = cv2.VideoCapture(video_path)
        player = MediaPlayer(video_path)  # Для воспроизведения аудио

        if not cap.isOpened():
            print("Error: Could not open splash screen video.")
            player.close_player()
            return

        video_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        video_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        window_name = "MishAI Splash Screen"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

        # Получаем размеры экрана
        root = Tk()
        root.withdraw()
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        root.destroy()

        # Вычисляем позицию для центрирования видео на черном фоне
        x_pos = (screen_width - video_width) // 2
        y_pos = (screen_height - video_height) // 2

        while cap.isOpened():
            ret, frame = cap.read()
            audio_frame, val = player.get_frame()

            if not ret or val == 'eof':
                break
            
            # Создаем черный фон на весь экран
            background = np.zeros((screen_height, screen_width, 3), dtype=np.uint8)

            # "Вклеиваем" кадр видео в центр черного фона
            background[y_pos:y_pos + video_height, x_pos:x_pos + video_width] = frame

            cv2.imshow(window_name, background)

            if cv2.waitKey(25) & 0xFF == 27:  # Клавиша Esc для пропуска
                break
        
        cap.release()
        player.close_player()
        cv2.destroyAllWindows()

    except Exception as e:
        print(f"An error occurred while playing splash screen: {e}")
        cv2.destroyAllWindows()


def process_text_request():
    """Обрабатывает запрос для выделенного текста."""
    if not gui_app or not gui_app.is_running:
        return
    print("Text hotkey activated!")
    try:
        keyboard.send('ctrl+c')
        time.sleep(0.1)
        prompt = get_clipboard_text()
        if not prompt:
            return
        
        config = load_config()
        start_request_worker(prompt, config)
    except Exception as e:
        print(f"An error in process_text_request: {e}")

def process_screenshot_request():
    """Запускает процесс выбора области на экране."""
    if not gui_app or not gui_app.is_running:
        return
    print("Screenshot hotkey activated! Please select a region.")
    
    gui_app.hide_window()
    gui_app.root.after(150, lambda: gui_app.start_region_selection(handle_cropped_image))

def handle_cropped_image(image):
    """
    Колбэк-функция, которая вызывается после выбора области.
    Получает обрезанное изображение и запускает его обработку.
    """
    if image:
        print("Region selected, processing image...")
        config = load_config()
        lang = config.get('Settings', 'language', fallback='ru')
        prompt = get_string('screenshot_prompt', lang)
        start_request_worker(prompt, config, image=image)
    else:
        print("Region selection was cancelled.")

def start_request_worker(prompt, config, image=None):
    """Запускает фоновый поток для обработки запроса к AI."""
    gui_app.show_loading_window()

    provider = config.get('Settings', 'provider', fallback='gemini')
    api_key_name = 'gemini_key' if provider == 'gemini' else 'openai_key'
    api_key = config.get('API', api_key_name, fallback='')
    
    model = config.get('Settings', 'model', fallback='gemini-1.5-flash')
    language = config.get('Settings', 'language', fallback='ru')

    def request_worker():
        try:
            response_text = get_completion(prompt, provider, api_key, model, language, image=image)
            if gui_app.is_running:
                gui_app.root.after(0, gui_app.show_response_window, response_text)
        except Exception as e:
            print(f"Error getting completion: {e}")
            error_message = get_string('error_generic', language).format(error=e)
            if gui_app.is_running:
                gui_app.root.after(0, gui_app.show_response_window, error_message)

    threading.Thread(target=request_worker, daemon=True).start()

def update_hotkeys(text_hotkey, screenshot_hotkey):
    """Отменяет старые горячие клавиши и регистрирует новые."""
    global text_hotkey_handler, screenshot_hotkey_handler
    
    if text_hotkey_handler:
        keyboard.remove_hotkey(text_hotkey_handler)
    if screenshot_hotkey_handler:
        keyboard.remove_hotkey(screenshot_hotkey_handler)
    
    try:
        text_hotkey_handler = keyboard.add_hotkey(text_hotkey, process_text_request)
        print(f"Text hotkey registered: '{text_hotkey}'")
    except Exception as e:
        print(f"Failed to register text hotkey: {e}")
        
    try:
        screenshot_hotkey_handler = keyboard.add_hotkey(screenshot_hotkey, process_screenshot_request)
        print(f"Screenshot hotkey registered: '{screenshot_hotkey}'")
    except Exception as e:
        print(f"Failed to register screenshot hotkey: {e}")

def main():
    global gui_app
    mutex = None
    
    if SINGLE_INSTANCE_SUPPORTED:
        mutex_name = f"{APP_NAME}_Mutex_1.0"
        mutex = win32event.CreateMutex(None, 1, mutex_name)
        if win32api.GetLastError() == ERROR_ALREADY_EXISTS:
            lang = load_config().get('Settings', 'language', fallback='ru')
            messagebox.showwarning(
                get_string('already_running_title', lang),
                get_string('already_running_message', lang)
            )
            return

    try:
        # Воспроизводим видео перед запуском основного приложения
        play_splash_screen()

        handle_first_launch()
        config = load_config()
        
        gui_app = AppGUI(on_hotkey_save=update_hotkeys)

        initial_text_hotkey = config.get('Settings', 'hotkey', fallback='ctrl+shift+q')
        initial_screenshot_hotkey = config.get('Settings', 'screenshot_hotkey', fallback='ctrl+shift+s')
        update_hotkeys(initial_text_hotkey, initial_screenshot_hotkey)

        gui_app.run()
        print("Application closed. Unhooking all hotkeys.")
        keyboard.unhook_all()
    finally:
        if SINGLE_INSTANCE_SUPPORTED and mutex:
            win32api.CloseHandle(mutex)

if __name__ == "__main__":
    main()
