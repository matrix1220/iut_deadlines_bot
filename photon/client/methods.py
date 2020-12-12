from . import Request

class queuedSendMessage(Request):
	def __init__(self, bot, *args, **kwargs):
		Request.__init__(self, bot, "sendMessage", args, kwargs)
		self._waiting = True
		self.bot._message_queue.add_message(kwargs, self)
		
	def __await__(self):
		while self._waiting:
			yield
		return self.result

	def receive(self, result):
		self.result = result
		self._waiting = False

class sendMessage(Request):
	def __init__(self, bot, chat_id, message, **kwargs):
		Request.__init__(self, bot, "sendMessage", [], {"chat_id":chat_id, "text":message})


# def make_data(method, *args, **kwargs):
# 	for x in ['keyboard', 'inline_keyboard', 'remove_keyboard']:
# 		if x in kwargs.keys():
# 			if x=='keyboard': kwargs['reply_markup'] = {x:kwargs[x], "resize_keyboard":True}
# 			else: kwargs['reply_markup'] = {x:kwargs[x]}
# 			del kwargs[x]

# 	if hasattr(methods, method):
# 		data = getattr(methods, method)(*args, **kwargs)
# 	else:
# 		data = kwargs

# 	return method, data