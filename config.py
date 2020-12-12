
import os.path
debug = os.path.exists("debug")

import Telegrambot
if debug:
	token = "305643264:AAGwALg3QDiH2OrNzqehgoPdeXwpIqY416c"
else:
	token = "1410154354:AAEd9YJFFowWQrlkI3gPV0KkdT_PG7fNpeY"
bot = Telegrambot.bot(token, debug=debug)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker as _sessionmaker

class db:
	engine = create_engine('sqlite:///datebase.db', echo=debug)
	sessionmaker = _sessionmaker(bind=engine)
	session = sessionmaker()

import yaml
from object_dict import objectify

languages = []
for x in ['language_en.yaml']:
	languages.append(objectify(yaml.load(open(x).read(), Loader=yaml.Loader)))

