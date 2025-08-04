<div align="center">

<img src="src/assets/logo.png" alt="MishAI Logo" width="150" />

MishAI
The smart desktop assistant for Windows that instantly answers your questions from selected text or screen regions.

<p align="center">
<a href="https://github.com/tipasofteri/MishAI/releases"><img src="https://img.shields.io/github/v/release/tipasofteri/MishAI?style=for-the-badge" /></a>
<a href="#"><img src="https://img.shields.io/badge/python-3.10+-blue.svg?style=for-the-badge&logo=python" /></a>
<a href="#"><img src="https://img.shields.io/badge/license-MIT-green.svg?style=for-the-badge" /></a>
</p>

</div>

📖 About The Project
Tired of constantly switching between your work and a browser tab to ask a quick question? MishAI solves this problem.

This lightweight native assistant for Windows lives in your system tray and integrates the power of leading AI models (Google Gemini and OpenAI GPT) directly into your workflow. Whether you're analyzing code, translating a sentence, or trying to understand a complex diagram in a screenshot, MishAI is always just a hotkey away.

Simply select text or a screen region to get an instant, context-aware answer without ever leaving your current application.

<div align="center">

Application Demo:

</div>

🎯 Key Features
Dual Capture Modes:

📰 Text: Instantly analyze any selected text.

🖼️ Screenshot: Select any area on your screen, and the AI will understand what's on it.

Flexible Configuration:

🔧 Fully customizable hotkeys.

🌐 Multi-language support (Russian/English) for both UI and AI responses.

⚙️ Choose your AI provider (Gemini/OpenAI), model, and manage API keys independently through a user-friendly menu.

Smart UX:

🚀 Welcome video on first launch.

📋 Automatically copies the AI's response to the clipboard.

🔒 Prevents multiple instances of the application from running.

🌙 Runs in the background via a system tray icon.

🛠️ Built With
Python 3

CustomTkinter: For creating the modern GUI.

Pystray: For the system tray icon.

Keyboard: For global hotkey management.

MSS: For screen capturing.

OpenCV & ffpyplayer: For splash screen video playback.

PyInstaller & Inno Setup: For building a full-fledged .exe installer.

🚀 Getting Started
To get a local copy up and running, follow these simple steps.

Prerequisites
Python (3.10 or higher)

Git

Installation
Clone the repo:

git clone https://github.com/tipasofteri/MishAI.git
cd MishAI

Create and activate a virtual environment:

python -m venv .venv
.venv\Scripts\activate

Install all dependencies:

pip install -r requirements.txt

Run the application:

python src

On the first launch, the app will ask for your API key and create a configuration file in %AppData%/MishAI.

💻 Usage
To analyze text: Select text anywhere and press Ctrl+Shift+Q (by default).

To analyze a screenshot: Press Ctrl+Shift+S (by default), select a region of your screen, and release the mouse button.

Settings: Right-click the tray icon to open the settings menu, where you can change hotkeys, language, model, and API keys.

📦 Building The Installer
If you want to build your own setup.exe from the source code:

Install Inno Setup: Download and install Inno Setup.

Run the build script:

python build.py

The final installer MishAI-vX.X.X-setup.exe will appear in the installers folder.
