# RomasterBot

Библиотека для управления чат-ботами в веб-мессенджере.

## Установка
pip install romasterbot

## Пример
```python
from romasterbot import RomasterBot

api = RomasterBot()
bot = api.create_bot("MyBot")
api.send_message("MyBot", "Привет!")
print(api.get_messages("MyBot"))