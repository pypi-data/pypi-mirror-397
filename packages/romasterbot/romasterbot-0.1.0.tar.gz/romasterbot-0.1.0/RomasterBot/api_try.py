class RomasterBot:
    def __init__(self):
        self.bots = {}

    def create_bot(self, name):
        self.bots[name] = []
        return f"Бот {name} создан"

    def send(self, name, text):
        self.bots[name].append(text)