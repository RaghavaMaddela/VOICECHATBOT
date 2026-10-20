# Voice Chatbot Project Plan (Phase-Wise)

This document outlines the end-to-end engineering roadmap for building a high-performance, low-latency Voice Chatbot.

---

## Architecture Overview & Latency Budget

```
[User Mic] 
    │
    ▼ (16kHz PCM Stream)
[Voice Activity Detection (Silero VAD)]  ~250ms silence detection
    │
    ▼ (WebSocket / WebRTC)
[Streaming STT (Deepgram Nova-2 / Faster-Whisper)]  ~150-250ms
    │
    ▼ (Text stream)
[Conversational LLM (Gemini 2.0 Flash / Groq Llama 3.3)]  ~150ms TTFT
    │
    ▼ (Sentence-by-sentence text chunks)
[Streaming TTS (Cartesia Sonic / ElevenLabs / Kokoro)]  ~150ms
    │
    ▼ (Audio PCM / MP3 chunks)
[Web Audio API Queue + Interruption (Barge-In) Monitor]  ~30ms
    │
    ▼
[User Speaker] (Total TTFA Target: < 800ms)
```

---

## 8-Phase Implementation Roadmap

### Phase 1: Architecture, Scope & Environment Setup  ✅ COMPLETED
* **Objective:** Define bot persona, choose architecture track, and setup project structure.
* **Tasks:**
  - [x] Determine domain and conversational persona (AURA Voice Assistant).
  - [x] Choose Architecture Track A (Cascaded Modular Pipeline with multi-provider fallbacks).
  - [x] Scaffold backend (`backend/app/`) and glassmorphic frontend (`frontend/`).
  - [x] Setup `.env` and `.env.example` configuration for API keys.
* **Deliverable:** [backend/app/config.py](file:///c:/Users/dheer/OneDrive/Desktop/chatbot/backend/app/config.py), [requirements.txt](file:///c:/Users/dheer/OneDrive/Desktop/chatbot/requirements.txt), and [run.py](file:///c:/Users/dheer/OneDrive/Desktop/chatbot/run.py).

---

### Phase 2: Audio Capture, VAD & Streaming Speech-to-Text (STT)  ✅ COMPLETED
* **Objective:** Capture crystal clear microphone audio and stream it for real-time transcription.
* **Tasks:**
  - [x] Frontend: Web Audio API (`AudioContext`, `AudioWorklet`/`ScriptProcessorNode`) for 16kHz mono PCM capture.
  - [x] Implement Root-Mean-Square Voice Activity Detection (VAD) with configurable energy & silence thresholds.
  - [x] Setup bi-directional WebSocket connection (`/ws/voice`) streaming binary PCM audio.
  - [x] Multi-engine STT supporting Deepgram Nova-2, Groq Whisper Large-v3, Google Gemini Audio, and Mock fallback.
* **Deliverable:** [vad_service.py](file:///c:/Users/dheer/OneDrive/Desktop/chatbot/backend/app/services/vad_service.py) and [stt_service.py](file:///c:/Users/dheer/OneDrive/Desktop/chatbot/backend/app/services/stt_service.py).

---

### Phase 3: Conversational LLM Engine & Sentence Boundary Streaming  ✅ COMPLETED
* **Objective:** Process user speech into conversational responses with minimal time-to-first-token.
* **Tasks:**
  - [x] Connect backend to high-throughput streaming LLM engines (Groq Llama 3.3 70B, Google Gemini 2.0 / 1.5 Flash, OpenAI GPT-4o-mini).
  - [x] Implement conversational state management (sliding window memory, conversational persona instructions).
  - [x] Build asynchronous sentence-boundary chunker (splits tokens on `.`, `!`, `?` immediately for pipeline concurrency).
* **Deliverable:** [llm_service.py](file:///c:/Users/dheer/OneDrive/Desktop/chatbot/backend/app/services/llm_service.py).

---

### Phase 4: Low-Latency Streaming TTS & Barge-In (Interruption Handling)  ✅ COMPLETED
* **Objective:** Synthesize speech in real-time and allow the user to interrupt the bot naturally.
* **Tasks:**
  - [x] Integrate multi-provider streaming TTS: Microsoft Edge Neural voices (free, zero-config), ElevenLabs Turbo, Cartesia Sonic.
  - [x] Stream synthesized audio chunks (MP3/PCM) back to frontend over WebSocket.
  - [x] Frontend audio queue: Gapless playback scheduling with Web Audio API.
  - [x] **Barge-in / Interruption Mechanism**: Immediate client-side audio muting and server-side task cancellation (`task.cancel()`).
* **Deliverable:** [tts_service.py](file:///c:/Users/dheer/OneDrive/Desktop/chatbot/backend/app/services/tts_service.py) and [pipeline.py](file:///c:/Users/dheer/OneDrive/Desktop/chatbot/backend/app/pipeline.py).

---

### Phase 5: Modern Web UI & Interactive Audio Visualizer  ✅ COMPLETED
* **Objective:** Build an engaging, responsive interface with visual audio feedback.
* **Tasks:**
  - [x] Interactive Canvas visualizer (pulsing glowing energy orb modulated by microphone and assistant audio volume).
  - [x] Real-time conversation transcript feed with user/assistant bubbles and timestamps.
  - [x] Dynamic latency HUD: Time-To-First-Audio (TTFA), STT latency, and TTS latency display.
  - [x] Settings glass drawer: Live voice selector, LLM model switcher, STT provider picker, and system prompt editor.
  - [x] Acoustic Echo Cancellation (`echoCancellation: true`, `noiseSuppression: true`).
* **Deliverable:** [frontend/index.html](file:///c:/Users/dheer/OneDrive/Desktop/chatbot/frontend/index.html), [frontend/styles.css](file:///c:/Users/dheer/OneDrive/Desktop/chatbot/frontend/styles.css), and [frontend/app.js](file:///c:/Users/dheer/OneDrive/Desktop/chatbot/frontend/app.js).

---

### Phase 6: Performance Optimization & Latency Tuning  ✅ COMPLETED
* **Objective:** Reduce round-trip latency to sub-800ms and eliminate jitter.
* **Tasks:**
  - [x] Calibrated VAD silence threshold (350ms) for natural conversational turn-taking.
  - [x] Concurrent sentence-by-sentence TTS synthesis parallelized with LLM token generation.
  - [x] Connection keep-alive, ping/pong heartbeats, and reconnection management.
* **Deliverable:** Verified end-to-end streaming latency.

---

### Phase 7: Testing, Evaluation & Reliability  ✅ COMPLETED
* **Objective:** Verify voice pipeline accuracy, stress test concurrency, and catch edge cases.
* **Tasks:**
  - [x] Automated unit test suite covering VAD silence detection and synthetic PCM audio frames.
  - [x] Unit test verifying sentence boundary regex parser on streaming token generators.
  - [x] Neural TTS synthesis test verifying actual MP3 audio generation.
  - [x] API integration test verifying health, config, metrics, and static asset serving.
  - [x] End-to-end browser subagent verification of user interface and transcript interactions.
* **Deliverable:** [tests/test_components.py](file:///c:/Users/dheer/OneDrive/Desktop/chatbot/tests/test_components.py) and [tests/test_api.py](file:///c:/Users/dheer/OneDrive/Desktop/chatbot/tests/test_api.py).

---

### Phase 8: Production Deployment & Containerization  ✅ COMPLETED
* **Objective:** Package and deploy the application for secure, scalable public usage.
* **Tasks:**
  - [x] Production multi-stage `Dockerfile` with non-root user and automated container healthcheck.
  - [x] Production `docker-compose.yml` with resource limits, logging caps, and environment injection.
  - [x] WebSocket security: Optional token authentication (`AUTH_TOKEN`) and max concurrency protection (`MAX_CONCURRENT_SESSIONS`).
  - [x] Real-time operational telemetry endpoint (`/api/metrics`).
  - [x] `.dockerignore` for minimal image footprints.
* **Deliverable:** [Dockerfile](file:///c:/Users/dheer/OneDrive/Desktop/chatbot/Dockerfile), [docker-compose.yml](file:///c:/Users/dheer/OneDrive/Desktop/chatbot/docker-compose.yml), and [.dockerignore](file:///c:/Users/dheer/OneDrive/Desktop/chatbot/.dockerignore).
