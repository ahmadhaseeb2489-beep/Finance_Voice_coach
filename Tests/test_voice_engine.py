# test_basic.py - Test voice engine
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from voice_engine import VoiceEngine
def main():
    engine = VoiceEngine()
    engine.speak("Hello! I'm your finance coach")

    # Test listening
    command = engine.listen()
    print(f"You said: {command}")

    engine.speak(f"You told me: {command}")


if __name__ == "__main__":
    main()