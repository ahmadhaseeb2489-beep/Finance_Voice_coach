# voice_engine.py - Voice system with sounddevice only
import sounddevice as sd
import pyttsx3
import soundfile as sf
import tempfile
import os
from Config import app_config


class VoiceEngine:
    def __init__(self):
        print("🔊 Initializing Voice Engine...")
        self.tts_engine = pyttsx3.init()
        self.setup_voice()
        print("✅ Voice Engine ready!")

    def setup_voice(self):
        voices = self.tts_engine.getProperty('voices')
        if len(voices) > 1:
            self.tts_engine.setProperty('voice', voices[1].id)
        self.tts_engine.setProperty('rate', app_config.VOICE_RATE)
        self.tts_engine.setProperty('volume', app_config.VOICE_VOLUME)

    def speak(self, text):
        print(f"🤖 AI: {text}")
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()

    def listen(self):
        print("🎤 Speak now! (I'm listening...)")

        try:
            import sounddevice as sd
            import json
            import queue
            import vosk

            # Initialize Vosk model (will download small model)
            model_path = "vosk-model-small-en-us-0.15"
            if not os.path.exists(model_path):
                print("📥 Downloading speech model...")
                import urllib.request
                import zipfile
                url = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
                urllib.request.urlretrieve(url, "model.zip")
                with zipfile.ZipFile("model.zip", 'r') as zip_ref:
                    zip_ref.extractall(".")
                os.remove("model.zip")

            model = vosk.Model(model_path)
            recognizer = vosk.KaldiRecognizer(model, 16000)

            # Record audio
            q = queue.Queue()

            def callback(indata, frames, time, status):
                if status:
                    print(status)
                q.put(bytes(indata))

            print("🔊 Recording... Speak now!")
            with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                                   channels=1, callback=callback):
                rec = []
                while True:
                    data = q.get()
                    if recognizer.AcceptWaveform(data):
                        result = json.loads(recognizer.Result())
                        if result['text']:
                            print(f"👤 You said: {result['text']}")
                            return result['text'].lower()
                    rec.append(data)

        except Exception as e:
            print(f"❌ Speech recognition error: {e}")
            print("🔧 Using text input instead...")
            command = input("👤 Type your command: ")
            return command.lower()