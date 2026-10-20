# 🎙️ AURA — Real-Time Conversational Voice AI

AURA is an enterprise-grade, low-latency conversational voice chatbot built with a **Python (FastAPI + WebSockets)** backend and a glassmorphic **HTML5/JS Web Audio API** frontend.

It features **sub-second streaming Time-To-First-Audio (TTFA < 800ms)** and native **Barge-in / Interruption handling** (you can talk over the AI and it instantly stops speaking).

---

## 🚀 Key Features

* **Sub-Second Streaming Pipeline**: Streams user audio chunks directly over WebSockets, detects voice boundaries with Root-Mean-Square Energy VAD, streams LLM output with sentence-boundary chunking, and synthesizes audio concurrently.
* **Instant Barge-in (Interruption Support)**: When the user speaks while the assistant is speaking, client-side playback is muted immediately and the backend aborts ongoing generation tasks (`task.cancel()`).
* **Zero-Config Neural Voice (Free Out of the Box)**: Defaults to high-fidelity Microsoft Edge Neural TTS voices (`Jenny`, `Guy`, `Sonia`, etc.) with zero paid API keys required.
* **Pluggable Architecture**:
  * **STT**: Deepgram Nova-2, Groq Whisper Large-v3, Browser Web Speech, or Mock Simulator.
  * **LLM**: Groq (Llama 3.3 70B), Google Gemini 2.0 / 1.5 Flash, OpenAI (GPT-4o-mini), or Mock.
  * **TTS**: Edge-TTS (Free), ElevenLabs Turbo, Cartesia Sonic.
* **Modern Glassmorphic UI**: Dynamic pulsating energy orb canvas visualizer, live performance latency HUD (TTFA, STT, TTS ms), real-time chat bubbles, and settings drawer.

---

## 🛠️ Project Structure

```
chatbot/
├── backend/
│   ├── app/
│   │   ├── config.py             # Pydantic environment configuration
│   │   ├── main.py               # FastAPI server, REST & WebSocket routes
│   │   ├── pipeline.py           # Orchestrator: VAD -> STT -> LLM -> TTS -> Barge-In
│   │   └── services/
│   │       ├── vad_service.py    # Voice Activity Detection & Silence thresholding
│   │       ├── stt_service.py    # Streaming Speech-to-Text integration
│   │       ├── llm_service.py    # Streaming LLM with async sentence chunker
│   │       └── tts_service.py    # Multi-engine low-latency speech synthesis
├── frontend/
│   ├── index.html                # Responsive web app interface
│   ├── styles.css                # Glassmorphic dark theme & micro-animations
│   └── app.js                    # Web Audio API, WebSocket queue & Canvas visualizer
├── tests/
│   ├── test_components.py        # VAD, sentence chunker, and TTS tests
│   └── test_api.py               # Health & Config endpoint tests
├── .env.example                  # Environment configuration template
├── PROJECT_PLAN.md               # 8-phase implementation roadmap
├── requirements.txt              # Python dependencies
└── run.py                        # Single-command launcher
```

---

## 🏃 Quick Start

### 1. Activate the Virtual Environment
```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

### 2. Configure API Keys (Optional)
Open `.env` and add your preferred provider keys:

```env
# Fast Speech-to-Text
STT_PROVIDER=deepgram
DEEPGRAM_API_KEY=your_deepgram_api_key

# Fast LLM Reasoning
LLM_PROVIDER=groq
GROQ_API_KEY=your_groq_api_key

# High-Quality Neural Voices (Edge-TTS is free and requires NO key!)
TTS_PROVIDER=edge_tts
EDGE_TTS_VOICE=en-US-JennyNeural
```

*(If you don't enter keys, the application automatically uses Edge-TTS for real voices and the built-in local simulator for instant testing).*

### 3. Run the Voice Chatbot
```powershell
python run.py
```

### 4. Open in Browser
Navigate to **`http://127.0.0.1:8000`** in your browser, click **"Start Voice Session"**, grant microphone access, and speak!

---

## 🧪 Running Tests

To run the automated pipeline and API tests:
```powershell
.\.venv\Scripts\python.exe -m unittest discover tests
```
