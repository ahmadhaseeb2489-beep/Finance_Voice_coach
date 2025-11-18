try:
    import speechrecognition
    import pyttsx3
    import sounddevice
    import pandas
    import numpy
    print("✅ All dependencies installed successfully!")
except ImportError as e:
    print(f"❌ Missing dependency: {e}")