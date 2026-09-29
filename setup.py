#!/usr/bin/env python
"""
Jarvis Voice Assistant - Setup Script
Bu skript loyihani initialize qiladi va kerakli dependencies-larni install qiladi
"""

import os
import sys
import subprocess
import platform
import shutil
import tempfile
import zipfile
from urllib.request import urlopen
from engine.config import PROJECT_ROOT, VOSK_MODEL_PATH

def install_dependencies():
    """Pipfile-dan dependencies install qilish"""
    print("=" * 50)
    print("Installing dependencies...")
    print("=" * 50)
    
    packages = [
        "eel",
        "playsound==1.2.2",
        "pyttsx3",
        "edge-tts==7.2.8",
        "SpeechRecognition",
        "vosk==0.3.45",
        "pywhatkit",
        "pyaudio",
        "huggingface_hub==2.0.0",
        "beautifulsoup4",
        "requests",
        "pyperclip",
        "pillow",
    ]
    
    print("\nInstalling packages...")
    failed_packages = []
    for package in packages:
        print(f"Installing {package}...")
        result = subprocess.run([sys.executable, "-m", "pip", "install", package, "-q"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ {package} installed successfully")
        else:
            print(f"✗ Warning with {package}, but continuing...")
            failed_packages.append(package)
    
    if failed_packages:
        print("\n✗ Failed to install: " + ", ".join(failed_packages))
        return False

    print("\n✓ Packages installation completed!")
    return True

def init_database():
    """Database initialize qilish"""
    print("\n" + "=" * 50)
    print("Initializing database...")
    print("=" * 50)
    
    try:
        from engine.db import init_database
        init_database()
        print("✓ Database initialized successfully!")
        return True
    except Exception as e:
        print(f"✗ Error initializing database: {e}")
        return False

def create_directories():
    """Kerakli directories yaratish"""
    print("\n" + "=" * 50)
    print("Creating directories...")
    print("=" * 50)
    
    directories = [
        "www/assets/audio",
        "www/assets/img",
        "engine",
    ]
    
    success = True
    for directory in directories:
        try:
            directory_path = os.path.join(PROJECT_ROOT, directory)
            os.makedirs(directory_path, exist_ok=True)
            print(f"✓ Directory created: {directory_path}")
        except Exception as e:
            print(f"✗ Error creating directory {directory}: {e}")
            success = False
    
    return success


def ensure_vosk_model():
    model_config = os.path.join(VOSK_MODEL_PATH, "conf", "model.conf")
    if os.path.isfile(model_config):
        print("✓ Uzbek offline speech model is already installed")
        return True

    engine_dir = os.path.join(PROJECT_ROOT, "engine")
    archive_path = None
    try:
        descriptor, archive_path = tempfile.mkstemp(suffix=".zip")
        os.close(descriptor)
        model_url = "https://alphacephei.com/vosk/models/vosk-model-small-uz-0.22.zip"
        print("Downloading the 49 MB Uzbek offline speech model...")
        with urlopen(model_url, timeout=120) as response, open(archive_path, "wb") as archive_file:
            shutil.copyfileobj(response, archive_file)

        engine_root = os.path.abspath(engine_dir)
        with zipfile.ZipFile(archive_path) as archive:
            for member in archive.namelist():
                destination = os.path.abspath(os.path.join(engine_root, member))
                if os.path.commonpath((engine_root, destination)) != engine_root:
                    raise ValueError("Model archive contains an invalid path")
            archive.extractall(engine_root)

        if not os.path.isfile(model_config):
            raise FileNotFoundError("Vosk model archive did not contain the expected model")
        print("✓ Uzbek offline speech model installed")
        return True
    except Exception as error:
        print(f"✗ Could not install Uzbek offline speech model ({type(error).__name__})")
        return False
    finally:
        if archive_path and os.path.exists(archive_path):
            os.remove(archive_path)

def main():
    """Main setup function"""
    print("\n")
    print("╔" + "=" * 48 + "╗")
    print("║" + " " * 10 + "JARVIS VOICE ASSISTANT - SETUP" + " " * 8 + "║")
    print("╚" + "=" * 48 + "╝")
    print(f"\nPlatform: {platform.system()}")
    print(f"Python Version: {sys.version}")
    
    # Step 1: Create directories
    if not create_directories():
        print("\n✗ Setup failed at directory creation step")
        return False
    
    # Step 2: Install dependencies
    if not install_dependencies():
        print("\n✗ Setup failed at dependency installation step")
        return False

    # Step 3: Install the offline Uzbek wake-word model
    if not ensure_vosk_model():
        print("\n✗ Setup failed at Uzbek speech model installation step")
        return False
    
    # Step 4: Initialize database
    if not init_database():
        print("\n✗ Setup failed at database initialization step")
        return False
    
    print("\n" + "=" * 50)
    print("✓ SETUP COMPLETED SUCCESSFULLY!")
    print("=" * 50)
    print("\nYou can now run the application with:")
    print("  python run.py")
    print("\nOr for development:")
    print("  python main.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
