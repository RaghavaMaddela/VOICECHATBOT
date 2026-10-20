import uvicorn
import sys
import os

# Add backend directory to sys.path
backend_path = os.path.join(os.path.dirname(__file__), "backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Configure UTF-8 for console output on Windows
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from app.config import settings

if __name__ == "__main__":
    print("\n=======================================================")
    print(">> AURA Voice Chatbot Server Initializing...")
    print(f">> Web Interface : http://{settings.HOST}:{settings.PORT}")
    print(f">> WebSocket URL  : ws://{settings.HOST}:{settings.PORT}/ws/voice")
    print(f">> TTS Engine     : {settings.TTS_PROVIDER} ({settings.EDGE_TTS_VOICE})")
    print(f">> LLM Engine     : {settings.LLM_PROVIDER} ({settings.LLM_MODEL})")
    print(f">> STT Engine     : {settings.STT_PROVIDER}")
    print("=======================================================\n")

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,
        reload_dirs=[backend_path],
        log_level="info"
    )
