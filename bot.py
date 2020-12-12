from config import db
import photon, scenario

async def handle(update):
	try:
		_response = await photon.handle(update)
	finally:
		db.session.commit()
	return _response


