
from .client import inline_button

from . import _globals
from .client import Bot as _Bot
def Bot(token):
	bot = _Bot(token)
	_globals._bot = bot
	return bot

from .client import request #as _request
class ResponseMaker:
	def __getattr__(self, key):
		def function(*args, **kwargs):
			return request(_globals._bot, key, args, kwargs)
		return function

response = ResponseMaker()

# class Handler: pass
# class MenuHandler: pass
# class CallbackHandler: pass
# abstract_handlers = [MenuHandler, CallbackHandler]

def handler(_handler):
	_handler.id = len(handlers)
	handlers.append(_handler)
	return _handler

handlers = []

#menu_handlers = []

async def handle(update):
	if message := update.message:
		chat = message.chat
		if chat.type == "private":
			user = _globals._find_user(chat.id)

			if user.menu_stack.empty(): 
				return await user.main_menu()

			if text := message.text:
				if text == "/start":
					return await user.main_menu()
				return await user.handle_text(text)

	elif callback_query := update.callback_query:
		user = _globals._find_user(callback_query['from'].id)
		if not user:
			return response.answerCallbackQuery(callback_query.id)
		return await user.handle_callback(callback_query)

from .client import Request
# Persistence
# Context

class User:
	_passes = False
	# def __init__(self, menu_stack)
	# 	self.menu_stack = menu_stack
	# 	self._passes = False

	def passes(self):
		self._passes = True

	def act(self, handler):
		async def func(*args, **kwargs):
			result = await self._execute_handle(handler.act, args, kwargs)
			if not self._passes: return result
			self._passes = False
			self.menu_stack.push([handler.id, args, kwargs])
			return result
		return func

	def explicit_act(self, handler):
		async def func(*args, **kwargs):
			result = await self._execute_handle(handler.act, args, kwargs)
			if not self._passes: return result
			self._passes = False
			self.menu_stack.set_current([handler.id, args, kwargs])
			return result
		return func

	async def main_menu(self):
		#self.menu_stack.reset()
		return await self.explicit_act(handlers[0])()

	async def back(self):
		if self.menu_stack.empty():
			return await self.main_menu()
		menu = self.menu_stack.pop()
		handler = handlers[menu[0]]
		return await self.explicit_act(handler)(*menu[1], **menu[2])
		

	async def _execute_handle(self, handle, args, kwargs={}):
		try:
			result = await handle(self, *args, **kwargs)
			if isinstance(result, Request):
				return result.as_response()
			print(result)
			return result
		except dict as e:
			return e
		except Request as e:
			return e.as_response()

	async def handle_text(self, text):
		handler = handlers[self.menu_stack.current()[0]]
		return await self._execute_handle(handler.handle_text, [text])

	async def handle_callback(self, callback_query):
		if data := callback_query.data:
			data = json.loads(data)
			handler = handlers[data.pop(0)]
			return await self._execute_handle(handler.handle_callback, [callback_query, data])

	find_user = None
	def __init_subclass__(cls, **kwargs):
		_globals._find_user = cls.find_user
