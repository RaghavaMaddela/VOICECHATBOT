import os
import sys
import io
import wave
import time
import asyncio
import streamlit as st

# Add backend directory to sys.path
backend_path = os.path.join(os.path.dirname(__file__), "backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.config import settings
from app.services.stt_service import STTService
from app.services.llm_service import LLMService
from app.services.tts_service import TTSService

# Set Page Config
st.set_page_config(
    page_title="AURA — Real-Time Voice AI",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Glassmorphic Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700&family=Plus+Jakarta+Sans:wght@400;500;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .stApp {
        background-color: #07090e;
        color: #f8fafc;
    }
    
    .main-title {
        font-family: 'Outfit', sans-serif;
        font-size: 2.3rem;
        font-weight: 700;
        letter-spacing: 1.5px;
        background: linear-gradient(120deg, #ffffff, #a5b4fc, #38bdf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    
    .sub-title {
        color: #94a3b8;
        font-size: 0.95rem;
        margin-bottom: 20px;
    }

    .metric-card {
        background: rgba(23, 31, 52, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 12px 18px;
        text-align: center;
        backdrop-filter: blur(16px);
        margin-bottom: 12px;
    }
    
    .metric-val {
        font-size: 1.3rem;
        font-weight: 700;
        color: #38bdf8;
    }
    
    .metric-lbl {
        font-size: 0.75rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }
    
    .stChatMessage {
        border-radius: 14px;
        border: 1px solid rgba(255, 255, 255, 0.06);
        background: rgba(18, 24, 40, 0.5);
        backdrop-filter: blur(12px);
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)

# Helper function to run async methods synchronously
def run_async(coro):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    if loop.is_running():
        import nest_asyncio
        nest_asyncio.apply()
    return loop.run_until_complete(coro)

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I am AURA, your voice intelligence assistant. Record your voice or type below to talk with me!"}
    ]

if "last_processed_audio_id" not in st.session_state:
    st.session_state.last_processed_audio_id = None

if "metrics" not in st.session_state:
    st.session_state.metrics = {"stt_ms": 0, "tts_ms": 0, "total_turns": 0}

# Initialize Services
@st.cache_resource
def get_services():
    return STTService(), LLMService(), TTSService()

stt_service, llm_service, tts_service = get_services()

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.markdown("<h2 style='font-family:Outfit;'>⚙️ Voice Engine Settings</h2>", unsafe_allow_html=True)
    
    # Provider selectors
    selected_voice = st.selectbox(
        "TTS Neural Voice",
        options=[
            "en-US-JennyNeural",
            "en-US-GuyNeural",
            "en-US-AriaNeural",
            "en-GB-SoniaNeural",
            "en-AU-NatashaNeural"
        ],
        index=0,
        help="Free, high-fidelity neural voices powered by Microsoft Edge-TTS."
    )
    settings.EDGE_TTS_VOICE = selected_voice
    tts_service.voice = selected_voice

    llm_choice = st.selectbox(
        "LLM Intelligence Provider",
        options=["groq", "gemini", "openai", "mock"],
        index=0 if settings.GROQ_API_KEY else (1 if settings.GEMINI_API_KEY else 3),
        help="Select LLM reasoning backend."
    )
    settings.LLM_PROVIDER = llm_choice
    llm_service.provider = llm_choice

    stt_choice = st.selectbox(
        "Speech-to-Text (STT) Provider",
        options=["deepgram", "groq_whisper", "mock"],
        index=0 if settings.DEEPGRAM_API_KEY else 2,
        help="Engine used to transcribe microphone voice."
    )
    settings.STT_PROVIDER = stt_choice
    stt_service.provider = stt_choice

    st.markdown("---")
    
    # Latency Telemetry
    st.markdown("### 📊 Performance HUD")
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-val">{st.session_state.metrics['stt_ms']} ms</div>
            <div class="metric-lbl">STT Speed</div>
        </div>
        """, unsafe_allow_html=True)
    with col_b:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-val">{st.session_state.metrics['tts_ms']} ms</div>
            <div class="metric-lbl">TTS Speed</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"<div style='text-align:center; color:#94a3b8; font-size:0.8rem;'>Turns Processed: <b>{st.session_state.metrics['total_turns']}</b></div>", unsafe_allow_html=True)

    st.markdown("---")
    if st.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state.messages = [
            {"role": "assistant", "content": "Conversation cleared! Ready for your next question."}
        ]
        st.rerun()

# --- MAIN CONTENT ---
st.markdown("<h1 class='main-title'>AURA — Real-Time Voice AI</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>Conversational Intelligence with Streaming Neural Speech & Instant Audio Playback</p>", unsafe_allow_html=True)

# Audio Input Deck
input_col, status_col = st.columns([3, 1])

with input_col:
    # Use native st.audio_input if available (Streamlit >= 1.40)
    audio_value = None
    if hasattr(st, "audio_input"):
        audio_value = st.audio_input("🎙️ Speak into your microphone:")
    else:
        audio_value = st.file_uploader("Upload Audio recording (WAV/MP3):", type=["wav", "mp3", "m4a", "ogg"])

with status_col:
    st.markdown("### Status")
    if settings.GROQ_API_KEY or settings.GEMINI_API_KEY:
        st.success("⚡ Live AI Active")
    else:
        st.info("💡 Simulation Mode (Free)")

# Render Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if "audio" in msg and msg["audio"]:
            st.audio(msg["audio"], format="audio/mp3")

# Process User Voice Recording
if audio_value is not None:
    # Generate unique ID for current audio clip
    audio_id = f"{audio_value.name}_{audio_value.size}" if hasattr(audio_value, "name") else str(audio_value.size)
    
    if st.session_state.last_processed_audio_id != audio_id:
        st.session_state.last_processed_audio_id = audio_id
        
        with st.spinner("🎧 Transcribing your voice..."):
            raw_audio_bytes = audio_value.read()
            t0 = time.time()
            
            # If audio is already a WAV file, extract or convert to PCM
            try:
                with wave.open(io.BytesIO(raw_audio_bytes), "rb") as wf:
                    pcm_bytes = wf.readframes(wf.getnframes())
            except Exception:
                pcm_bytes = raw_audio_bytes

            # Transcribe
            user_transcript = run_async(stt_service.transcribe_audio(pcm_bytes))
            stt_latency = int((time.time() - t0) * 1000)
            st.session_state.metrics["stt_ms"] = stt_latency

        if user_transcript.strip():
            # Add user message
            st.session_state.messages.append({"role": "user", "content": user_transcript})
            
            with st.chat_message("user"):
                st.write(user_transcript)

            # Generate Assistant Response
            with st.chat_message("assistant"):
                with st.spinner("🧠 Thinking & Synthesizing voice..."):
                    history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
                    
                    # LLM Generation
                    async def get_llm_response():
                        stream = llm_service.stream_response(history)
                        full_text = ""
                        async for token in stream:
                            full_text += token
                        return full_text

                    reply_text = run_async(get_llm_response())
                    st.write(reply_text)

                    # TTS Speech Synthesis
                    t_tts = time.time()
                    audio_bytes = run_async(tts_service.synthesize_sentence(reply_text))
                    tts_latency = int((time.time() - t_tts) * 1000)
                    st.session_state.metrics["tts_ms"] = tts_latency
                    st.session_state.metrics["total_turns"] += 1

                    if audio_bytes:
                        st.audio(audio_bytes, format="audio/mp3", autoplay=True)
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": reply_text,
                            "audio": audio_bytes
                        })
                    else:
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": reply_text
                        })

            st.rerun()

# Text Fallback Input
text_prompt = st.chat_input("Or type a question to get a voice response...")
if text_prompt:
    st.session_state.messages.append({"role": "user", "content": text_prompt})
    with st.chat_message("user"):
        st.write(text_prompt)

    with st.chat_message("assistant"):
        with st.spinner("Synthesizing voice response..."):
            history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
            
            async def get_llm_response():
                stream = llm_service.stream_response(history)
                full_text = ""
                async for token in stream:
                    full_text += token
                return full_text

            reply_text = run_async(get_llm_response())
            st.write(reply_text)

            t_tts = time.time()
            audio_bytes = run_async(tts_service.synthesize_sentence(reply_text))
            tts_latency = int((time.time() - t_tts) * 1000)
            st.session_state.metrics["tts_ms"] = tts_latency
            st.session_state.metrics["total_turns"] += 1

            if audio_bytes:
                st.audio(audio_bytes, format="audio/mp3", autoplay=True)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": reply_text,
                    "audio": audio_bytes
                })
            else:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": reply_text
                })

    st.rerun()
