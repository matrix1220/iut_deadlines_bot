from config import bot, db, languages
from dbscheme import User

from scenario import MainMenu
from botcore import handlers, set_main_menu

set_main_menu(MainMenu)

from Telegrambot import response

import json

def handle(update):
	try:
		_response = main(update)
	finally:
		db.session.commit()
	return _response


def find_user(id):
	user = db.session.query(User).filter(User.id==id).first()
	if not user:
		user = User(id=id)
		db.session.add(user)

	user.lang = languages[user.language] if user.language!=None else None
	
	return user


def main(update):
	if (message := update.message) and (message.chat.type == "private"):
		chat = message.chat
		user = find_user(chat.id)

		if text := message.text:
			if text == "/start" or not user.menu:
				return user.act(MainMenu)()

			if type(user.menu[0])!=int: return user.act(MainMenu)()

			handler = handlers[user.menu[0]]

			return handler.handle_text(user, text)


	elif (callback_query := update.callback_query) and (data := callback_query.data):
		message = callback_query.message
		data = json.loads(data)
		user = find_user(callback_query['from'].id)
		# if not user:
		# 	return response.answerCallbackQuery(callback_query.id)

		handler = handlers[data.pop(0)]

		return handler.handle_callback(user, callback_query, data)


