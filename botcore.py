
class User:
	__passes = False

	def passes(self):
		self.__passes = True

	#menu = None
	#goback = None

	def act(self, handler):
		def tmp(*args, **kwargs):
			result = handler.act(self, *args, **kwargs)
			if self.__passes:
				self.__passes = False
				if self.menu: self.goback.append(self.menu)
				self.menu = [handler.id, args, kwargs]

			return result
		return tmp

	def explicit_act(self, handler):
		def tmp(*args, **kwargs):
			result = handler.act(self, *args, **kwargs)
			if self.__passes:
				self.__passes = False
				self.menu = [handler.id, args, kwargs]

			return result
		return tmp

	def back(self):
		if self.goback:
			menu = self.goback.pop()
			handler = handlers[menu[0]]
			return self.explicit_act(handler)(*menu[1], **menu[2])
		elif main_menu:
			return self.explicit_act(main_menu)()

def handler(_handler):
	_handler.id = len(handlers)
	handlers.append(_handler)
	return _handler

handlers = []

main_menu = None

def set_main_menu(_handler):
	global main_menu
	main_menu = _handler

print(handlers)