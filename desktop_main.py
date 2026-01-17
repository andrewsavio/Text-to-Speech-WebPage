import os
import sys
import threading
import time
import uvicorn
import webview
from backend.main import app

# Ensure we can find the modules (especially when frozen)
if getattr(sys, 'frozen', False):
    # Running as compiled exe
    base_dir = sys._MEIPASS
    # Static files location in bundled app
    os.environ["STATIC_DIR"] = os.path.join(base_dir, "static")
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))

# Define port
PORT = 8000
HOST = "127.0.0.1"

def start_server():
    """Starts the FastAPI server in a thread."""
    uvicorn.run(app, host=HOST, port=PORT, log_level="error")

import base64

class Api:
    def __init__(self):
        self.window = None

    def save_audio(self, base64_data):
        print("Save audio requested")
        try:
            filename = self.window.create_file_dialog(
                webview.SAVE_DIALOG,
                directory=os.path.expanduser('~'),
                save_filename='generated_speech.wav',
                file_types=('WAV files (*.wav)', 'All files (*.*)')
            )
            
            if filename:
                # pywebview returns a tuple or string depending on version/OS, usually string for save
                if isinstance(filename, (tuple, list)):
                    filename = filename[0]
                
                # Remove header if present (data:audio/wav;base64,...)
                if ',' in base64_data:
                    base64_data = base64_data.split(',')[1]
                
                audio_bytes = base64.b64decode(base64_data)
                
                with open(filename, 'wb') as f:
                    f.write(audio_bytes)
                
                return {"status": "success", "path": filename}
            return {"status": "cancelled"}
        except Exception as e:
            print(f"Error saving file: {e}")
            return {"status": "error", "message": str(e)}

def main():
    # Start Backend
    t = threading.Thread(target=start_server, daemon=True)
    t.start()

    # Wait a moment for server to start (simple sleep, or we could poll /health)
    time.sleep(1)

    api = Api()

    # Create Window
    # Point to the local server serves the React app
    window = webview.create_window(
        title="Andrew's TTS - Andrew Ltd",
        url=f"http://{HOST}:{PORT}",
        width=1200,
        height=800,
        resizable=True,
        text_select=True, # Useful for copying text
        js_api=api
    )
    api.window = window

    # Start GUI loop
    webview.start(debug=False)

if __name__ == '__main__':
    try:
        # If running via PyInstaller with splash
        import pyi_splash
        pyi_splash.update_text("Initializing AI Models...")
        # Simulate load time or do heavy imports here if they weren't at top level
        # Since we imported 'backend.main' at top, it's already loaded.
        pyi_splash.close()
    except ImportError:
        pass

    main()
