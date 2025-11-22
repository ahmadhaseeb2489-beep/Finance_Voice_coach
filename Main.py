# main.py - Main application
from voice_engine import VoiceEngine
from finance_logic import FinanceLogic
from Config import app_config


class FinanceCoach:
    def __init__(self):
        print("🚀 Starting AI Finance Coach...")
        self.voice_engine = VoiceEngine()
        self.finance_logic = FinanceLogic()
        print("✅ All systems ready!")

    def process_command(self, command):
        return self.finance_logic.process_command(command)

    def run(self):
        self.voice_engine.speak("Hello! I'm your AI Finance Coach. Let's chat about your finances!")

        while True:
            command = self.voice_engine.listen()

            if command in ['stop', 'exit', 'quit']:
                break

            response = self.process_command(command)
            self.voice_engine.speak(response)
            print()  # Empty line for readability

        self.voice_engine.speak("Goodbye! Keep tracking your financial goals!")


if __name__ == "__main__":
    coach = FinanceCoach()
    coach.run()