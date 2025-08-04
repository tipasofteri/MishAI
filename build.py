import os
import subprocess
import shutil
import sys
import time 

APP_NAME = "MishAI"
APP_VERSION = "2.0.0"
MAIN_SCRIPT = os.path.join("src", "__main__.py")
ASSETS_DIR = os.path.join("src", "assets")
ICON_PATH = os.path.join(ASSETS_DIR, "icon.ico")
OUTPUT_DIR = "dist"

INNO_SCRIPT_TEMPLATE = f'''

[Setup]
AppId={{{{ {APP_NAME}-GUID }}}}
AppName={APP_NAME}
AppVersion={APP_VERSION}
DefaultDirName={{autopf}}\\{APP_NAME}
DefaultGroupName={APP_NAME}
OutputDir=installers
OutputBaseFilename={APP_NAME}-v{APP_VERSION}-setup
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
SetupIconFile={os.path.abspath(ICON_PATH)}
UninstallDisplayIcon={{app}}\\{APP_NAME}.exe

[Languages]
Name: "russian"; MessagesFile: "compiler:Languages\\Russian.isl"

[Tasks]
Name: "desktopicon"; Description: "{{cm:CreateDesktopIcon}}"; GroupDescription: "{{cm:AdditionalIcons}}";
Name: "startup"; Description: "Start {APP_NAME} on Windows logon"; GroupDescription: "Auto start";

[Files]
Source: "{OUTPUT_DIR}\\{APP_NAME}.exe"; DestDir: "{{app}}"; Flags: ignoreversion

[Icons]
Name: "{{group}}\\{APP_NAME}"; Filename: "{{app}}\\{APP_NAME}.exe"
Name: "{{commondesktop}}\\{APP_NAME}"; Filename: "{{app}}\\{APP_NAME}.exe"; Tasks: desktopicon

[Run]
Filename: "{{app}}\\{APP_NAME}.exe"; Description: "{{cm:LaunchProgram,{APP_NAME}}}"; Flags: nowait postinstall skipifsilent

[Registry]
Root: HKA; Subkey: "Software\\Microsoft\\Windows\\CurrentVersion\\Run"; ValueType: string; ValueName: "{APP_NAME}"; ValueData: """{{app}}\\{APP_NAME}.exe"""; Tasks: startup
'''

def run_command(command):
    print(f"--- Execution: {' '.join(command)} ---")
    try:
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        print(result.stdout)
        if result.stderr:
            print("--- Stderr: ---")
            print(result.stderr)
    except subprocess.CalledProcessError as e:
        print(f"--- Error (code: {e.returncode}) ---")
        print("--- Stdout: ---")
        print(e.stdout)
        print("--- Stderr: ---")
        print(e.stderr)
        sys.exit(e.returncode)
    except FileNotFoundError:
        print(f"--- Error: command '{command[0]}' not found ---")
        sys.exit(1)

def main():
    for dir_to_clean in [OUTPUT_DIR, "build", "installers"]:
        if os.path.exists(dir_to_clean):
            print(f"Cleaning the folder '{dir_to_clean}'...")
            shutil.rmtree(dir_to_clean)
    
    print("Step 1: Building .exe file...")
    pyinstaller_command = [
        sys.executable,
        "-m", "PyInstaller",
        "--name", APP_NAME,
        "--onefile",
        "--windowed",
        f"--icon={ICON_PATH}",
        "--add-data", f"{ASSETS_DIR}{os.pathsep}assets",
        MAIN_SCRIPT
    ]
    run_command(pyinstaller_command)

    print("Waiting for file release...")
    time.sleep(5)

    print("Step 2: Creating installer script...")
    iss_filename = "mishagpt_installer.iss"
    with open(iss_filename, "w", encoding="utf-8") as f:
        f.write(INNO_SCRIPT_TEMPLATE)

    print("Step 3: Compiling installer...")
    iscc_path = "C:\\Program Files (x86)\\Inno Setup 6\\ISCC.exe"
    if not os.path.exists(iscc_path):
        print("Error: Inno Setup not found")
        return
        
    inno_command = [iscc_path, iss_filename]
    run_command(inno_command)
    
    os.remove(iss_filename)
    os.remove(f"{APP_NAME}.spec")
    print("\nBuild completed")
    print(f"Installer: {os.path.abspath('installers')}")

if __name__ == "__main__":
    main()
