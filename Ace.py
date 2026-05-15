import asyncio
import websockets
import json
import base64
import sounddevice as sd
import numpy as np
import os

SAMPLE_RATE      = 24000
CHUNK_SIZE       = 2048
SILENCE_RMS      = 0.02   # RMS below this counts as silence
SILENCE_SECS     = 0.8    # seconds of silence to end an utterance
MIN_SPEECH_SECS  = 0.4    # ignore clips shorter than this

STATE_FILE = "ace_state.txt"

SYSTEM_PROMPT = (
    "You are Ace, the playful and happy robot assistant for the ACM SIGSOFT "
    "student chapter at Alfaisal University. Answer whatever the user asks, "
    "but always in a fun, upbeat, and friendly tone. Never refuse to answer "
    "a question — just respond naturally like a cheerful helpful robot would. "
    "Keep responses short and conversational, like you are talking not writing. "
    "Always respond in English only, regardless of what language the user speaks."
)

def set_state(state):
    with open(STATE_FILE, "w") as f:
        f.write(state)

async def main():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")

    url = "wss://api.openai.com/v1/realtime?model=gpt-4o-mini-realtime-preview"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "OpenAI-Beta": "realtime=v1",
    }

    loop = asyncio.get_running_loop()
    audio_out = []
    audio_queue = asyncio.Queue()
    responding = False  # True while Ace is generating or playing audio

    async with websockets.connect(url, additional_headers=headers, max_size=None) as ws:
        print("Connecting...")
        while True:
            evt = json.loads(await ws.recv())
            if evt["type"] == "session.created":
                break

        await ws.send(json.dumps({
            "type": "session.update",
            "session": {
                "modalities": ["audio", "text"],
                "instructions": SYSTEM_PROMPT,
                "voice": "coral",
                "input_audio_format": "pcm16",
                "output_audio_format": "pcm16",
                "input_audio_transcription": {"model": "whisper-1", "language": "en"},
                "turn_detection": None,  # manual — we control when to commit
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
                    continue  # ignore mic input while Ace is speaking

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
                            blocksize=CHUNK_SIZE, callback=mic_callback):
            vad = asyncio.create_task(vad_and_commit())

            async for raw in ws:
                evt = json.loads(raw)
                t = evt.get("type", "")

                if t == "conversation.item.input_audio_transcription.completed":
                    transcript = evt.get("transcript", "").strip()
                    item_id = evt.get("item_id")
                    print(f"Heard: '{transcript}'")

                    if "ace" in transcript.lower():
                        print("Wake word detected — responding...")
                        responding = True
                        set_state("thinking")
                        await ws.send(json.dumps({"type": "response.create"}))
                    else:
                        # Delete so it doesn't accumulate in conversation history
                        if item_id:
                            await ws.send(json.dumps({
                                "type": "conversation.item.delete",
                                "item_id": item_id,
                            }))

                elif t == "response.audio.delta":
                    audio_out.append(base64.b64decode(evt["delta"]))
                    if len(audio_out) == 1:
                        set_state("speaking")

                elif t == "response.audio.done":
                    if audio_out:
                        raw_pcm = b"".join(audio_out)
                        pcm_f32 = np.frombuffer(raw_pcm, dtype=np.int16).astype(np.float32) / 32767.0
                        sd.play(pcm_f32, samplerate=SAMPLE_RATE)
                        await loop.run_in_executor(None, sd.wait)
                        audio_out.clear()
                    responding = False
                    set_state("idle")
                    print("Say 'Ace' to continue.")

                elif t == "response.output_item.done":
                    for c in evt.get("item", {}).get("content", []):
                        if c.get("type") == "text":
                            print(f"Ace: {c['text']}")

                elif t == "error":
                    print(f"Error: {evt.get('error', {})}")

            vad.cancel()

if __name__ == "__main__":
    asyncio.run(main())
