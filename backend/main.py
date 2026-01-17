import sys
import os
import logging
import io
import tempfile
from pathlib import Path
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
import uvicorn

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add pocket-tts to path
# Assuming the structure is:
# /root
#   /backend
#   /pocket-tts-main
#     /pocket-tts-main (contents of the zip usually have a nested folder, user confirmed this structure)
POCKET_TTS_PATH = Path(__file__).parent.parent / "pocket-tts-main" / "pocket-tts-main"
sys.path.append(str(POCKET_TTS_PATH))

try:
    from pocket_tts.models.tts_model import TTSModel
    from pocket_tts.default_parameters import DEFAULT_VARIANT
    from pocket_tts.utils.utils import PREDEFINED_VOICES
    import pocket_tts
    logger.info(f"Loaded pocket_tts from: {pocket_tts.__file__}")
    logger.info(f"Available predefined voices: {list(PREDEFINED_VOICES.keys())}")
except ImportError as e:
    logger.error(f"Failed to import pocket_tts. Ensure the path is correct: {POCKET_TTS_PATH}")
    raise e

app = FastAPI(title="Pocket TTS Web API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for now, dev mode
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve Frontend
# In production/docker, frontend build will be in "static" directory relative to main.py or /app/static
# For Desktop (PyInstaller), we set STATIC_DIR env var or look in sys._MEIPASS/static
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
     # PyInstaller temp dir
    STATIC_DIR = Path(sys._MEIPASS) / "static"
elif "STATIC_DIR" in os.environ:
    STATIC_DIR = Path(os.environ["STATIC_DIR"])
else:
    STATIC_DIR = Path("/app/static")
    if not STATIC_DIR.exists():
        STATIC_DIR = Path(__file__).parent / "static" # Local fallback

if STATIC_DIR.exists():
    app.mount("/assets", StaticFiles(directory=STATIC_DIR / "assets"), name="assets")
else:
    logger.warning(f"Static directory not found at: {STATIC_DIR}")

@app.get("/")
async def serve_index():
    if (STATIC_DIR / "index.html").exists():
        return FileResponse(STATIC_DIR / "index.html")
    return {"message": "Frontend not found. Run verify build."}


# Global variables for model
tts_model = None
global_model_state = None

def get_model():
    global tts_model
    if tts_model is None:
        logger.info("Loading TTS Model...")
        # Load default variant
        tts_model = TTSModel.load_model(DEFAULT_VARIANT)
        logger.info("TTS Model loaded.")
    return tts_model

@app.on_event("startup")
async def startup_event():
    get_model()

@app.get("/health")
async def health_check():
    return {"status": "healthy", "model_loaded": tts_model is not None}

@app.get("/voices")
async def get_voices():
    """Return list of predefined voices + generic ones if any"""
    # Create a nice list of voices. 
    # Based on README, we have some preset URLs.
    voices = [
        {"id": "alba", "name": "Alba", "url": "hf://kyutai/tts-voices/alba-mackenna/casual.wav"},
        {"id": "marius", "name": "Marius", "url": "hf://kyutai/tts-voices/voice-donations/Selfie.wav"},
        {"id": "javert", "name": "Javert", "url": "hf://kyutai/tts-voices/voice-donations/Butter.wav"},
        {"id": "jean", "name": "Jean", "url": "hf://kyutai/tts-voices/ears/p010/freeform_speech_01.wav"},
        {"id": "fantine", "name": "Fantine", "url": "hf://kyutai/tts-voices/vctk/p244_023.wav"},
        {"id": "cosette", "name": "Cosette", "url": "hf://kyutai/tts-voices/expresso/ex04-ex02_confused_001_channel1_499s.wav"},
        {"id": "eponine", "name": "Eponine", "url": "hf://kyutai/tts-voices/vctk/p262_023.wav"},
        {"id": "azelma", "name": "Azelma", "url": "hf://kyutai/tts-voices/vctk/p303_023.wav"},
    ]
    return voices

@app.post("/generate")
async def generate_audio(
    text: str = Form(...),
    voice_url: str = Form(None),
    voice_file: UploadFile = File(None)
):
    if not text:
        raise HTTPException(status_code=400, detail="Text is required")
    
    current_model = get_model()
    
    # Determine which voice to use
    model_state = None
    
    if voice_file:
        # Load custom voice from upload
        try:
            # Save properly to temp file to ensure libsndfile can read it
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                content = await voice_file.read()
                tmp.write(content)
                tmp_path = tmp.name
            
            model_state = current_model.get_state_for_audio_prompt(tmp_path, truncate=True)
            os.unlink(tmp_path) # Cleanup
        except Exception as e:
            logger.error(f"Error processing voice file: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to process voice file: {str(e)}")

    elif voice_url:
        # Load preset voice
        if voice_url in PREDEFINED_VOICES:
             # It's a key
             try:
                 model_state = current_model._cached_get_state_for_audio_prompt(voice_url, truncate=True)
             except Exception as e:
                 logger.error(f"Error loading preset voice: {e}")
                 raise HTTPException(status_code=500, detail=f"Failed to load preset voice: {str(e)}")
        else:
             # It's a URL
            try:
                logger.info(f"Fetching voice from URL: {voice_url}")
                model_state = current_model.get_state_for_audio_prompt(voice_url, truncate=True)
            except Exception as e:
                logger.error(f"Error fetching voice URL: {e}")
                raise HTTPException(status_code=500, detail=f"Failed to fetch voice: {str(e)}")
    else:
        # Default voice if none provided
        # Use 'alba' which is a predefined voice key that works without voice cloning weights
        try:
            default_voice = "alba"
            model_state = current_model._cached_get_state_for_audio_prompt(default_voice, truncate=True)
        except Exception as e:
             logger.error(f"Error loading default voice: {e}")
             raise HTTPException(status_code=500, detail=f"Failed to load default voice: {str(e)}")

    if model_state is None:
         raise HTTPException(status_code=500, detail="Could not initialize voice state")

    # Generate Audio Stream
    def iterpath():
        try:
            # generate_audio_stream yields chunks of numpy arrays (or tensors)
            audio_chunks = model.generate_audio_stream(
                model_state=model_state,
                text_to_generate=text
            )
            
            # We need to convert these raw chunks to a streamable wave format or just raw PCM.
            # However, browsers handle WAV streams better if headers are correct, which is hard for streaming.
            # An alternative is to just yield raw bytes if the client can handle it, 
            # BUT: pocket-tts `stream_audio_chunks` is a helper that writes to a file.
            # Let's look at how their `serve` command does it.
            # It uses a "FileLikeToQueue" and `yield queue.get()`.
            # And it sets media_type="audio/wav" with Transfer-Encoding: chunked.
            
            # Re-implementing the queue logic from their main.py might be safest.
            pass
        except Exception as e:
            logger.error(f"Generation error: {e}")
            yield b""

    # Using the exact same logic as their implementation for robustness because Streaming WAV is tricky
    from queue import Queue
    import threading
    from pocket_tts.data.audio import stream_audio_chunks as write_audio_chunks
    
    queue = Queue()

    def write_to_queue_wrapper():
        class FileLikeToQueue(io.IOBase):
            def __init__(self, q):
                self.q = q
            def write(self, data):
                self.q.put(data)
            def flush(self):
                pass
            def close(self):
                self.q.put(None)

        try:
            # We must use the model instance to generate stream
            gen = current_model.generate_audio_stream(
                model_state=model_state,
                text_to_generate=text,
                frames_after_eos=None, # Auto
                copy_state=True
            )
            
            # Write to our queue wrapper
            write_audio_chunks(
                FileLikeToQueue(queue),
                gen,
                current_model.config.mimi.sample_rate
            )
        except Exception as e:
            logger.error(f"Streaming error: {e}")
        finally:
            queue.put(None) # Signal end

    thread = threading.Thread(target=write_to_queue_wrapper)
    thread.start()

    def yield_chunks():
        while True:
            data = queue.get()
            if data is None:
                break
            yield data
        thread.join()

    return StreamingResponse(
        yield_chunks(),
        media_type="audio/wav",
        headers={
            "Content-Disposition": "attachment; filename=generated_speech.wav",
        }
    )

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
