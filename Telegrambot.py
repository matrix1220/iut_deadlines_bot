import requests, time, json
from object_dict import objectify, dictify

class methods:
	def sendMessage(chat_id, text, **kwargs):
		return {"chat_id":chat_id, "text":text, **kwargs}
	def getChatMember(chat_id, user_id):
		return {"chat_id":chat_id, "user_id":user_id}
	def deleteMessage(chat_id, message_id):
		return {"chat_id":chat_id, "message_id":message_id}
	def answerCallbackQuery(callback_query_id, **kwargs):
		return {"callback_query_id":callback_query_id, **kwargs}
	def editMessageText(chat_id, message_id, **kwargs):
		return {"chat_id":chat_id, "message_id":message_id,  **kwargs}
	def editMessageReplyMarkup(chat_id, message_id, reply_markup):
		return {"chat_id":chat_id, "message_id":message_id,  "reply_markup":reply_markup}


def inline_button(text, callback_data = None, **kwargs):
	kwargs.update({"text":text})
	if callback_data!=None: kwargs.update({"callback_data":json.dumps(callback_data)})
	return kwargs

class Exception(Exception):
	def __init__(self, description, error_code = None):
		super().__init__(description)
		self.description = description
		self.error_code = error_code

class Request:
	send_message_limit = time.time()
	def __init__(self, method, *args, **kwargs):
		self.method = method

		for x in ['keyboard', 'inline_keyboard', 'remove_keyboard']:
			if x in kwargs.keys():
				if x=='keyboard': kwargs['reply_markup'] = {x:kwargs[x], "resize_keyboard":True}
				else: kwargs['reply_markup'] = {x:kwargs[x]}
				del kwargs[x]

		if hasattr(methods, method):
			self.data = getattr(methods, method)(*args, **kwargs)
		else:
			self.data = kwargs

		if method == "sendMessage":
			delta_time = Request.send_message_limit - time.time()
			if delta_time > 0:
				if delta_time > 0.8:
					time.sleep(delta_time)
			else:
				Request.send_message_limit = time.time()

			Request.send_message_limit += 0.06

class dataMaker:
	def __getattr__(self, key):
		def function(*args, **kwargs):
			temp = Request(key, *args, **kwargs)
			return {'method':temp.method, **temp.data}
		return function

response = dataMaker()

class bot:
	def __init__(self, token, debug=True):
		self._token = token
		self._debug = debug

	def _send(self, method, args={}):
		if self._debug: print(method, args)
		data = objectify(requests.post('https://api.telegram.org/bot' + self._token + '/' + method, json=args).json())
		if self._debug: print(data)

		if not data.ok: raise Exception(data.description, data.error_code)
		return data.result

	def long_polling(self, timeout = 30):
		offset = -1
		for update in self.getUpdates(offset=offset):
				offset = update.update_id + 1

		while True:
			for update in self.getUpdates(offset=offset, timeout=timeout):
				yield update
				offset = update.update_id + 1

	def __getattr__(self, key):
		def function(*args, **kwargs):
			temp = Request(key, *args, **kwargs)
			return self._send(temp.method, temp.data)
		return function
