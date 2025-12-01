import speech_recognition as sr

print("Testing microphone...")
print("Available microphones:")
print(sr.Microphone.list_microphone_names())

r = sr.Recognizer()
with sr.Microphone() as source:
    print("Speak something...")
    audio = r.listen(source)

try:
    text = r.recognize_google(audio)
    print(f"You said: {text}")
except Exception as e:
    print(f"Error: {e}")