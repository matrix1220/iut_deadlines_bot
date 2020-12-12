from abc import ABC, abstractmethod

class MenuStack(ABC):
	@abstractmethod
	def __init__(self, user_id):
		pass
	@abstractmethod
	def current(self):
		pass
	@abstractmethod
	def set_current(self, menu):
		pass
	@abstractmethod
	def pop(self):
		pass
	@abstractmethod
	def push(self, menu):
		pass
	@abstractmethod
	def reset(self):
		pass
	@abstractmethod
	def empty(self):
		pass