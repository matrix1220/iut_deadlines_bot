from config import bot
from bot import handle
import asyncio

asyncio.run(bot.long_polling(handle))