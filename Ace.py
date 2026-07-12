import asyncio
import base64
import sounddevice as sd
import numpy as np
import os
import wave
import io
import subprocess
import yt_dlp
from datetime import datetime, timezone
from openai import AsyncOpenAI
from piper.voice import PiperVoice

INPUT_DEVICE  = int(os.getenv("ACE_INPUT_DEVICE",  "1"))
OUTPUT_DEVICE = int(os.getenv("ACE_OUTPUT_DEVICE", "5"))

SAMPLE_RATE      = int(os.getenv("ACE_SAMPLE_RATE", "24000"))
OUTPUT_RATE      = int(os.getenv("ACE_OUTPUT_RATE", "0")) or None  # None = use native rate
API_SAMPLE_RATE  = 24000   # Realtime API always expects 24000
CHUNK_SIZE       = 2048
SILENCE_RMS      = 0.02
SILENCE_SECS     = 0.4
MIN_SPEECH_SECS  = 0.2

STATE_FILE  = "ace_state.txt"
CMD_FILE    = "ace_command.txt"
LANG_FILE   = "ace_lang.txt"
VOICE_MODEL = "en_GB-semaine-medium.onnx"

DEMO_SCRIPT = [
    "Hi there! I'm Ace, the robot assistant for ACM SIGSOFT at Alfaisal University. Say my name to ask me anything!",
    "ACM SIGSOFT is where future software engineers connect, compete, and build things that actually matter!",
    "Software engineering is not just coding — it is about solving real problems for real people!",
    "From AI to cybersecurity, the ACM chapter at Alfaisal brings the future of tech straight to your campus!",
    "The best software in the world starts with great engineers — and great engineers start right here at Alfaisal!",
]

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
    "Keep responses very short — never more than 2 sentences, like you are talking not writing. Always finish your sentence completely before stopping. "
    "Never use emojis or special symbols in your responses. "
    "You will be given the current date/time, language instruction, and web search results before each response — "
    "always follow the language instruction exactly."
)

voice = PiperVoice.load(VOICE_MODEL)

music_process = None

with open(LANG_FILE, "w") as f:
    f.write("en")

def set_state(state):
    with open(STATE_FILE, "w") as f:
        f.write(state)

def get_lang():
    try:
        with open(LANG_FILE, "r") as f:
            return f.read().strip()
    except Exception:
        return "en"

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

def play_youtube(song_name):
    global music_process
    stop_music()
    try:
        ydl_opts = {"format": "bestaudio/best", "quiet": True, "no_warnings": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch1:{song_name}", download=False)
            entry = info.get("entries", [info])[0]
            url = entry["url"]
            title = entry.get("title", song_name)
        music_process = subprocess.Popen(
            ["mpv", "--no-video", "--really-quiet", url],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        print(f"Now playing: {title}")
        return f"Playing {title}!"
    except Exception as e:
        print(f"YouTube error: {e}")
        return "Sorry, I could not find that song."

def stop_music():
    global music_process
    if music_process and music_process.poll() is None:
        music_process.terminate()
        music_process = None

def trim_to_sentence(text):
    last = max(text.rfind("."), text.rfind("!"), text.rfind("?"))
    return text[:last + 1] if last != -1 else text

def play_audio(audio, src_rate):
    target_rate = OUTPUT_RATE or src_rate
    if target_rate != src_rate:
        from scipy.signal import resample_poly
        import math
        g = math.gcd(target_rate, src_rate)
        audio = resample_poly(audio, target_rate // g, src_rate // g).astype(np.float32)
    sd.play(audio, samplerate=target_rate, device=OUTPUT_DEVICE)
    sd.wait()

def synthesize_and_play(text):
    wav_io = io.BytesIO()
    with wave.open(wav_io, "wb") as wf:
        voice.synthesize_wav(text, wf)
    wav_io.seek(0)
    with wave.open(wav_io, "rb") as wf:
        frames = wf.readframes(wf.getnframes())
        src_rate = wf.getframerate()
    audio = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32767.0
    play_audio(audio, src_rate)

async def main():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")

    client = AsyncOpenAI(api_key=api_key)
    loop          = asyncio.get_running_loop()

    async def speak(text, force_lang=None):
        try:
            lang = force_lang or get_lang()
            if lang == "ar":
                response = await client.audio.speech.create(
                    model="tts-1",
                    voice="alloy",
                    input=text,
                    response_format="wav"
                )
                def play_openai_wav():
                    wav_io = io.BytesIO(response.content)
                    with wave.open(wav_io, "rb") as wf:
                        frames   = wf.readframes(wf.getnframes())
                        src_rate = wf.getframerate()
                    audio = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32767.0
                    play_audio(audio, src_rate)
                await loop.run_in_executor(None, play_openai_wav)
            else:
                await loop.run_in_executor(None, synthesize_and_play, text)
        except Exception as e:
            print(f"Speech error: {e}")
    text_buf      = []
    transcript_buf = {}
    audio_queue   = asyncio.Queue()
    cmd_queue     = asyncio.Queue()
    responding    = False
    last_text     = ""
    demo_idx      = 0

    async def poll_commands():
        while True:
            await asyncio.sleep(0.5)
            try:
                with open(CMD_FILE, "r") as f:
                    cmd = f.read().strip()
                if cmd:
                    with open(CMD_FILE, "w") as f:
                        f.write("")
                    await cmd_queue.put(cmd)
            except Exception:
                pass

    print("Connecting...")
    async with client.realtime.connect(model="gpt-realtime-mini") as conn:
        await conn.session.update(session={
            "type": "realtime",
            "instructions": SYSTEM_PROMPT,
            "output_modalities": ["text"],
            "audio": {
                "input": {
                    "transcription": {"model": "whisper-1"},
                    "turn_detection": None,
                },
            },
        })

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
                            if SAMPLE_RATE != API_SAMPLE_RATE:
                                from scipy.signal import resample_poly
                                full = resample_poly(full, API_SAMPLE_RATE, SAMPLE_RATE).astype(np.float32)
                            pcm = (full * 32767).astype(np.int16).tobytes()
                            await conn.input_audio_buffer.append(
                                audio=base64.b64encode(pcm).decode()
                            )
                            await conn.input_audio_buffer.commit()
                        else:
                            await conn.input_audio_buffer.clear()
                        speech_buf.clear()
                        is_speaking = False
                        silence_count = 0
                        set_state("idle")

        def mic_callback(indata, _frames, _time_info, _status):
            loop.call_soon_threadsafe(audio_queue.put_nowait, indata.copy())

        async def handle_commands():
            nonlocal responding, last_text, demo_idx
            while True:
                cmd = await cmd_queue.get()
                if responding:
                    continue
                responding = True

                if cmd == "repeat":
                    if last_text:
                        set_state("speaking")
                        await speak(last_text)
                        set_state("idle")
                    responding = False

                elif cmd == "demo":
                    text = DEMO_SCRIPT[demo_idx % len(DEMO_SCRIPT)]
                    demo_idx += 1
                    print(f"Demo: {text}")
                    set_state("speaking")
                    await speak(text)
                    last_text = text
                    set_state("idle")
                    responding = False

                else:
                    prompts = {
                        "acm_info": "In one sentence, tell the audience why they should join the ACM SIGSOFT student chapter at Alfaisal University.",
                        "joke":     "Tell me a short programming joke. One sentence only.",
                        "fun_fact": "Give me one surprising fun fact about software engineering. One sentence only.",
                    }
                    prompt = prompts.get(cmd)
                    if prompt:
                        if get_lang() == "ar":
                            prompt += " Respond in Arabic only."
                        set_state("thinking")
                        await conn.conversation.item.create(item={
                            "type": "message",
                            "role": "user",
                            "content": [{"type": "input_text", "text": prompt}],
                        })
                        await conn.response.create(response={"max_output_tokens": 60})
                        # responding=False is set by the response.output_text.done handler
                    else:
                        responding = False

        with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype=np.float32,
                            blocksize=CHUNK_SIZE, callback=mic_callback, device=INPUT_DEVICE):
            vad  = asyncio.create_task(vad_and_commit())
            poll = asyncio.create_task(poll_commands())
            cmds = asyncio.create_task(handle_commands())

            async for event in conn:
                t = event.type

                if t == "conversation.item.input_audio_transcription.delta":
                    item_id = getattr(event, "item_id", None)
                    if item_id:
                        transcript_buf[item_id] = transcript_buf.get(item_id, "") + getattr(event, "delta", "")

                elif t == "conversation.item.input_audio_transcription.completed":
                    item_id = getattr(event, "item_id", None)
                    transcript = (getattr(event, "transcript", None) or transcript_buf.pop(item_id, "")).strip()
                    print(f"Heard: '{transcript}'")

                    if "ace" in transcript.lower():
                        query = transcript.lower().replace("ace", "").strip(" ,.")

                        if "stop" in query:
                            stop_music()
                            await speak("Stopped.", "en")
                            set_state("idle")

                        elif query.startswith("play") or " play " in query:
                            song = query.replace("play", "").strip(" ,.")
                            responding = True
                            set_state("thinking")
                            announcement = await loop.run_in_executor(None, play_youtube, song)
                            set_state("speaking")
                            await speak(announcement, "en")
                            responding = False
                            set_state("idle")

                        else:
                            print("Wake word detected — responding...")
                            responding = True
                            set_state("thinking")
                            now = datetime.now(timezone.utc).strftime("%A, %B %d %Y, %H:%M UTC")

                            if needs_search(query):
                                print(f"Searching: '{query}'")
                                await asyncio.sleep(1)
                                await speak("Let me look that up for you.", "en")
                                results = await loop.run_in_executor(None, web_search, query)
                                snippets = "\n".join(
                                    f"- {r.get('title','')}: {r.get('body','')}"
                                    for r in results
                                ) if results else "No results found."
                                context = (f"Current date and time: {now}\n\n"
                                           f"Web search results for '{query}':\n{snippets}")
                            else:
                                context = f"Current date and time: {now}"

                            if get_lang() == "ar":
                                context += "\n\nRespond in Arabic only."

                            await conn.conversation.item.create(item={
                                "type": "message",
                                "role": "user",
                                "content": [{"type": "input_text", "text": context}],
                            })
                            await conn.response.create(response={"max_output_tokens": 20})

                    else:
                        if item_id:
                            await conn.conversation.item.delete(item_id=item_id)

                elif t == "response.output_text.delta":
                    text_buf.append(getattr(event, "delta", ""))

                elif t == "response.output_text.done":
                    full_text = trim_to_sentence(
                        (getattr(event, "text", "") or "".join(text_buf)).strip()
                    )
                    text_buf.clear()
                    try:
                        if full_text:
                            print(f"Ace: {full_text}")
                            last_text = full_text
                            set_state("speaking")
                            await speak(full_text)
                    finally:
                        responding = False
                        set_state("idle")
                        print("Say 'Ace' to continue.")

                elif t == "error":
                    print(f"Error: {getattr(event, 'error', {})}")

            vad.cancel()
            poll.cancel()
            cmds.cancel()

if __name__ == "__main__":
    asyncio.run(main())
