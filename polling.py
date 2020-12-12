from bot import bot, handle
import traceback

from config import debug
timeout = 30
if debug: timeout = 2

polling = iter(bot.long_polling(timeout=timeout))

while True:
	try:
		update = next(polling)
	except Exception as e:
		print(traceback.format_exc())
		polling = iter(bot.long_polling())
		continue

	try:
		temp = handle(update)
		if temp: bot._send(temp.pop('method'), temp)
	except Exception as e:
		print(traceback.format_exc())
		# try:
		# 	bot.sendMessage(108268232, traceback.format_exc())
		# except Exception as e:
		# 	print(traceback.format_exc())