from .abstract import MenuStack#, User as _User

class MenuStack(MenuStack):
	def __init__(self, user_id):
		self._stack = []
	def current(self):
		return self._stack[-1]
	def set_current(self, menu):
		self._stack[-1] = menu
	def pop(self):
		return self._stack.pop()
	def push(self, menu):
		return self._stack.append(menu)
	def reset(self):
		self._stack = []
	def empty(self):
		return len(self._stack)==0

	# def find_menu_stack(user_id):
	# 	if user_id in users:
	# 		return users[user_id]
	# 	else:
	# 		menu_stack = MenuStack()
	# 		users[user_id] = menu_stack
	# 		return menu_stack

users = {}