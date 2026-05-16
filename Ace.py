import asyncio
import websockets
import json
import base64
import sounddevice as sd
import numpy as np
import os
import wave
import io
from datetime import datetime, timezone
from piper.voice import PiperVoice

INPUT_DEVICE  = 1
OUTPUT_DEVICE = 5

SAMPLE_RATE      = 24000
CHUNK_SIZE       = 2048
SILENCE_RMS      = 0.02
SILENCE_SECS     = 0.4
MIN_SPEECH_SECS  = 0.2

STATE_FILE  = "ace_state.txt"
VOICE_MODEL = "en_GB-semaine-medium.onnx"

NO_SEARCH_PHRASES = {
    "hello", "hi", "hey", "thanks", "thank you", "bye", "goodbye",
    "good morning", "good afternoon", "good evening", "how are you",
    "what's up", "whats up", "nice", "cool", "okay", "ok",
}

SYSTEM_PROMPT = (
    "You are Ace, the playful and happy robot assistant for the ACM SIGSOFT "
    "student chapter at Alfaisal University. Answer whatever the user asks, "
    "but always in a fun, upbeat, and friendly tone. Never refuse to answer "
    "a question — just respond naturally like a cheerful helpful robot would. "
    "Keep responses very short — 1 or 2 sentences max, like you are talking not writing. "
    "Always respond in English only, regardless of what language the user speaks. "
    "Never use emojis or special symbols in your responses. "
    "You will be given the current date/time and web search results before each response — "
    "use them to give accurate, up-to-date answers."
)

voice = PiperVoice.load(VOICE_MODEL)

def set_state(state):
    with open(STATE_FILE, "w") as f:
        f.write(state)

def needs_search(query):
    q = query.lower().strip()
    if len(q.split()) <= 2:
        return False
    return not any(q.startswith(p) or q == p for p in NO_SEARCH_PHRASES)

def web_search(query):
    try:
        tavily_key = os.getenv("TAVILY_API_KEY")
        if tavily_key:
            from tavily import TavilyClient
            client = TavilyClient(api_key=tavily_key)
            response = client.search(query, max_results=1)
            return [{"title": r.get("title", ""), "body": r.get("content", "")[:200]}
                    for r in response.get("results", [])]
        else:
            from ddgs import DDGS
            with DDGS() as ddgs:
                return [{"title": r.get("title", ""), "body": r.get("body", "")[:200]}
                        for r in list(ddgs.text(query, max_results=1))]
    except Exception:
        return []

def trim_to_sentence(text):
    last = max(text.rfind("."), text.rfind("!"), text.rfind("?"))
    return text[:last + 1] if last != -1 else text

def synthesize_and_play(text):
    wav_io = io.BytesIO()
    with wave.open(wav_io, "wb") as wf:
        voice.synthesize_wav(text, wf)
    wav_io.seek(0)
    with wave.open(wav_io, "rb") as wf:
        frames = wf.readframes(wf.getnframes())
        sample_rate = wf.getframerate()
    audio = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32767.0
    sd.play(audio, samplerate=sample_rate, device=OUTPUT_DEVICE)
    sd.wait()

async def main():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")

    url = "wss://api.openai.com/v1/realtime?model=gpt-4o-mini-realtime-preview"
    headers = {"Authorization": f"Bearer {api_key}"}

    loop = asyncio.get_running_loop()
    text_buf = []
    audio_queue = asyncio.Queue()
    responding = False

    async with websockets.connect(url, additional_headers=headers, max_size=None) as ws:
        print("Connecting...")
        while True:
            evt = json.loads(await ws.recv())
            if evt["type"] == "session.created":
                break

        await ws.send(json.dumps({
            "type": "session.update",
            "session": {
                "type": "realtime",
                "model": "gpt-4o-mini-realtime-preview",
                "instructions": SYSTEM_PROMPT,
                "output_modalities": ["text"],
                "audio": {
                    "input": {
                        "format": {"type": "audio/pcm", "rate": 24000},
                        "transcription": {"model": "whisper-1", "language": "en"},
                        "turn_detection": None,
                    },
                },
            },
        }))

        while True:
            evt = json.loads(await ws.recv())
            if evt["type"] == "error":
                raise RuntimeError(f"API error: {evt.get('error')}")
            if evt["type"] == "session.updated":
                break

        set_state("idle")
        print("Ready. Say 'Ace' to start.")

        async def vad_and_commit():
            speech_buf = []
            is_speaking = False
            silence_count = 0
            silence_frames = int(SILENCE_SECS * SAMPLE_RATE / CHUNK_SIZE)

            while True:
                chunk = await audio_queue.get()
                if responding:
                    continue
                rms = float(np.sqrt(np.mean(chunk ** 2)))
                if rms > SILENCE_RMS:
                    if not is_speaking:
                        set_state("listening")
                    is_speaking = True
                    silence_count = 0
                    speech_buf.append(chunk)
                elif is_speaking:
                    silence_count += 1
                    speech_buf.append(chunk)
                    if silence_count >= silence_frames:
                        duration = len(speech_buf) * CHUNK_SIZE / SAMPLE_RATE
                        if duration >= MIN_SPEECH_SECS:
                            full = np.concatenate(speech_buf)
                            pcm = (full * 32767).astype(np.int16).tobytes()
                            await ws.send(json.dumps({
                                "type": "input_audio_buffer.append",
                                "audio": base64.b64encode(pcm).decode(),
                            }))
                            await ws.send(json.dumps({"type": "input_audio_buffer.commit"}))
                        else:
                            await ws.send(json.dumps({"type": "input_audio_buffer.clear"}))
                        speech_buf.clear()
                        is_speaking = False
                        silence_count = 0
                        set_state("idle")

        def mic_callback(indata, _frames, _time_info, _status):
            loop.call_soon_threadsafe(audio_queue.put_nowait, indata.copy())

        with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype=np.float32,
                            blocksize=CHUNK_SIZE, callback=mic_callback, device=INPUT_DEVICE):
            vad = asyncio.create_task(vad_and_commit())

            async for raw in ws:
                evt = json.loads(raw)
                t = evt.get("type", "")

                if t == "conversation.item.input_audio_transcription.delta":
                    transcript = evt.get("delta", "").strip()
                    item_id = evt.get("item_id")
                    print(f"Heard: '{transcript}'")

                    if "ace" in transcript.lower():
                        print("Wake word detected — responding...")
                        responding = True
                        set_state("thinking")

                        query = transcript.lower().replace("ace", "").strip(" ,.")
                        now = datetime.now(timezone.utc).strftime("%A, %B %d %Y, %H:%M UTC")

                        if needs_search(query):
                            print(f"Searching: '{query}'")
                            results = await loop.run_in_executor(None, web_search, query)
                            snippets = "\n".join(
                                f"- {r.get('title','')}: {r.get('body','')}"
                                for r in results
                            ) if results else "No results found."
                            context = (f"Current date and time: {now}\n\n"
                                       f"Web search results for '{query}':\n{snippets}")
                        else:
                            context = f"Current date and time: {now}"

                        await ws.send(json.dumps({
                            "type": "conversation.item.create",
                            "item": {
                                "type": "message",
                                "role": "user",
                                "content": [{"type": "input_text", "text": context}],
                            },
                        }))
                        await ws.send(json.dumps({
                            "type": "response.create",
                            "response": {"max_output_tokens": 20},
                        }))

                    else:
                        if item_id:
                            await ws.send(json.dumps({
                                "type": "conversation.item.delete",
                                "item_id": item_id,
                            }))

                elif t == "response.output_text.delta":
                    text_buf.append(evt.get("delta", ""))

                elif t == "response.output_text.done":
                    full_text = trim_to_sentence(evt.get("text", "").strip() or "".join(text_buf).strip())
                    text_buf.clear()
                    if full_text:
                        print(f"Ace: {full_text}")
                        set_state("speaking")
                        await loop.run_in_executor(None, synthesize_and_play, full_text)
                    responding = False
                    set_state("idle")
                    print("Say 'Ace' to continue.")

                elif t == "error":
                    print(f"Error: {evt.get('error', {})}")

            vad.cancel()

if __name__ == "__main__":
    asyncio.run(main())
