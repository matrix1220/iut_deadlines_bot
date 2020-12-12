from werkzeug.wrappers import Request, Response
from werkzeug.exceptions import HTTPException, NotFound

from object_dict import objectify, dictify

from bot import handle

import json, datetime, time, decimal, logging


class CustomEncoder(json.JSONEncoder):
    def default(self, data):
        if isinstance(data, datetime.datetime):
            return data.timestamp()
        elif isinstance(data, datetime.date):
            return time.mktime(data.timetuple())
        elif isinstance(data, decimal.Decimal):
            return float(data)
        elif isinstance(data, db.base):
            return row_as_dict(data)
        else:
            return super().default(data)

def json_dump(data):
	return json.dumps(data, cls=CustomEncoder)

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
		Response.__init__(self, json.dumps(response))


@Request.application
def application(request):
	try:
		request_data = objectify(json.loads(request.data.decode()))
		response = handle(request_data)
		if response: return JSONResponse(response)
	except Exception as e:
		logging.exception(e)