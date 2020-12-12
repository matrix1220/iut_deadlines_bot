from .client import request
import _globals
#from _globals import _bot
def sendMessage(*args, **kwargs):
	return request(_globals._bot, "sendMessage", args, kwargs)