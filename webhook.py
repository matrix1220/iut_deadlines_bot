from werkzeug.wrappers import Request, Response
from werkzeug.exceptions import HTTPException, NotFound

from object_dict import objectify, dictify
from bot import handle
import json

class JSONException(HTTPException):
	def get_headers(self, environ = None):
		return [("Content-Type", "application/json; charset=utf-8")]

	def get_body(self, environ = None):
		return json.dumps({"ok":False, "code":self.code, "err_str":self.description})
		#{self.code} {escape(self.name) self.get_description(environ)

class JSONNotFound(NotFound, JSONException):
	pass

class JSONResponse(Response):
	def __init__(self, response):
		_Response.__init__(self, json.dumps({"ok":True, "result":response}))


@Request.application
def application(request):
	try:
		request_data = objectify(json.loads(request.data.decode()))
		response = handle(request)
		if response: return request_data(json.dumps(response))
	except Exception as e:
		#print(traceback.format_exc())
		try:
			bot.sendMessage(108268232, traceback.format_exc())
		except Exception as e:
			print(traceback.format_exc())

if __name__ == '__main__':
    from werkzeug.serving import run_simple
    run_simple('0.0.0.0', 5000, application, use_debugger=False, use_reloader=False)