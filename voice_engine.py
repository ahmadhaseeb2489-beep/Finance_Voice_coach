# voice_engine.py - Voice system with sounddevice only
import sounddevice as sd
import pyttsx3
from scipy.io.wavfile import write
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
        print("🎤 Speak now... (using text input for development)")
        command = input("👤 Type your command: ")
        return command.lower()


def listen(self, continuous=False):
    if continuous:
        print("🎤 I'm listening... (say 'stop' to end)")
    else:
        print("🎤 Speak now...")

    try:
        # For now, we'll use continuous text input
        if continuous:
            print("💬 Continuous voice mode - type your messages:")
            while True:
                command = input("👤 You: ")
                if command.lower() in ['stop', 'exit', 'quit']:
                    return "stop"
                yield command.lower()
        else:
            command = input("👤 Type your command: ")
            return command.lower()

    except Exception as e:
        print(f"❌ Error: {e}")
        return "error"