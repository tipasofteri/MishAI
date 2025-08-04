# src/utils.py

import configparser
import pyperclip
import os
import sys
import customtkinter as ctk

APP_NAME = "MishAI"
APPDATA_PATH = os.path.join(os.getenv('APPDATA'), APP_NAME)
CONFIG_FILE = os.path.join(APPDATA_PATH, 'config.ini')

translations = {
    'ru': {
        'first_launch_title': "Первый запуск MishAI",
        'first_launch_prompt': "Пожалуйста, введите ваш Google AI API ключ:",
        'screenshot_prompt': "Реши задачу или ответь на вопрос с этого изображения.",
        'system_prompt': "Ты — MishAI, быстрый и полезный ассистент. Отвечай на русском языке, кратко и по делу.",
        'openai_vision_not_supported': "Распознавание изображений для OpenAI пока не реализовано.",
        'error_api': "Произошла ошибка при обращении к API {provider}:\n{error}",
        'error_generic': "Произошла ошибка:\n{error}",
        'settings_title': "Настройки MishAI",
        'tab_general': "Основные",
        'tab_api': "API",
        'label_language': "Язык (UI и ответов AI):",
        'label_hotkey_text': "Горячая клавиша (текст):",
        'label_hotkey_screenshot': "Горячая клавиша (скриншот) :      (НЕ РЕКОМЕНДУЕТСЯ)",
        'label_provider': "Провайдер:",
        'label_model': "Модель:",
        'label_gemini_api_key': "Gemini API Ключ:",
        'label_openai_api_key': "OpenAI API Ключ:",
        'button_save': "Сохранить и закрыть",
        'button_cancel': "Отмена",
        'loading_message': "Идет обработка запроса...",
        'tray_settings': "Настройки",
        'tray_exit': "Выход",
        'already_running_title': "Приложение уже запущено",
        'already_running_message': "Другая копия MishAI уже работает.",
    },
    'en': {
        'first_launch_title': "MishAI First Launch",
        'first_launch_prompt': "Please enter your Google AI API key:",
        'screenshot_prompt': "Solve the task or answer the question from this image.",
        'system_prompt': "You are MishAI, a fast and helpful assistant. Respond in English, concisely and to the point.",
        'openai_vision_not_supported': "Image recognition for OpenAI is not yet implemented.",
        'error_api': "An error occurred while contacting the {provider} API:\n{error}",
        'error_generic': "An error occurred:\n{error}",
        'settings_title': "MishAI Settings",
        'tab_general': "General",
        'tab_api': "API",
        'label_language': "Language (UI and AI responses):",
        'label_hotkey_text': "Hotkey (Text):",
        'label_hotkey_screenshot': "Hotkey (Screenshot):      (NOT RECOMMENDED)",
        'label_provider': "Provider:",
        'label_model': "Model:",
        'label_gemini_api_key': "Gemini API Key:",
        'label_openai_api_key': "OpenAI API Key:",
        'button_save': "Save and Close",
        'button_cancel': "Cancel",
        'loading_message': "Processing request...",
        'tray_settings': "Settings",
        'tray_exit': "Exit",
        'already_running_title': "Application Already Running",
        'already_running_message': "Another instance of MishAI is already running.",
    }
}

def get_string(key, lang='ru'):
    return translations.get(lang, translations['ru']).get(key, f"<{key}>")

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath("src")
    return os.path.join(base_path, relative_path)

def load_config() -> configparser.ConfigParser:
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE, encoding='utf-8')
    return config

def save_config(config: configparser.ConfigParser):
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, 'w', encoding='utf-8') as configfile:
        config.write(configfile)

def get_clipboard_text() -> str:
    return pyperclip.paste()

def handle_first_launch():
    if not os.path.exists(CONFIG_FILE):
        print("First launch detected. Requesting API key.")
        dialog = ctk.CTkInputDialog(
            text=get_string('first_launch_prompt', 'en'),
            title=get_string('first_launch_title', 'en')
        )
        api_key = dialog.get_input()
        
        config = configparser.ConfigParser()
        config['API'] = {
            'gemini_key': api_key if api_key else 'YOUR_GEMINI_API_KEY_HERE',
            'openai_key': 'YOUR_OPENAI_API_KEY_HERE'
        }
        config['Settings'] = {
            'provider': 'gemini',
            'model': 'gemini-1.5-flash',
            'language': 'ru',
            'hotkey': 'ctrl+shift+q',
            'screenshot_hotkey': 'ctrl+shift+s',
            'autoclose_seconds': '0'
        }
        save_config(config)
        print(f"Config file created at: {CONFIG_FILE}")
