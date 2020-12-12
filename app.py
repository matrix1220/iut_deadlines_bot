from waitress import serve
from werkzeug.serving import run_simple

from webhook import application
from config import debug
if debug:
	run_simple('0.0.0.0', 8080, application, use_debugger=True, use_reloader=True)
else:
	serve(application, listen='*:8080')