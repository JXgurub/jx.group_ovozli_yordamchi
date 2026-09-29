import os 
import sys
import eel
from engine.features import playAssistantSound
from engine.command import allCommands
from engine.config import WEB_HOST, WEB_PORT, WWW_DIR
from engine.db import init_database

def start():
    """Jarvis asosiy funksiyasi"""
    try:
        # Database initialize qilish
        init_database()
        print("Database initialized")
        
        # Eel initialize
        eel.init(WWW_DIR)
        
        # Assistant sound qo'yish
        playAssistantSound()
        
        # Web browser ochish
        # Cross-platform support
        assistant_url = f"http://{WEB_HOST}:{WEB_PORT}/index.html?desktop=1"
        try:
            if sys.platform == 'win32':
                os.system(f'start msedge.exe --app="{assistant_url}"')
            elif sys.platform == 'darwin':  # macOS
                os.system(f'open -a "Microsoft Edge" "{assistant_url}"')
            else:  # Linux
                os.system(f'microsoft-edge --app="{assistant_url}" &')
        except:
            print("Web browser could not be opened")
        
        # Eel app start
        eel.start('index.html', mode=None, host=WEB_HOST, port=WEB_PORT, block=True, cmdline_args=['--disable-blink-features=AutomationControlled'])
        
    except Exception as e:
        print(f"Error in start(): {e}")
        import traceback
        traceback.print_exc()
        raise





