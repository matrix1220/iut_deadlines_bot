from sqlalchemy import Integer, Column

from .types import JSONEncoded, MutableList

from ..abstract import MenuStack

class MenuStack(MutableList, MenuStack):
	@classmethod
	def coerce(cls, key, value):
		print(value)
		if value is None:
			return MenuStack()
		if isinstance(value, list):
			return MenuStack(value)
		return MutableList.coerce(key, value)

	def current(self):
		return self[-1]
	def set_current(self, menu):
		if not self.empty():
			self[-1] = menu
		else:
			self.push(menu)
	def pop(self):
		return MutableList.pop(self)
	def push(self, menu):
		return MutableList.append(self, menu)
	def reset(self):
		MutableList.clear(self)
	def empty(self):
		return len(self)==0
		
from photon import User as _User
class User(_User):
	__tablename__ = 'users'
	id = Column(Integer, primary_key=True)
	menu_stack = Column(MenuStack.as_mutable(JSONEncoded))
