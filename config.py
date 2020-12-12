
import os.path
debug = os.path.exists("debug")

import logging
if debug:
	logging.basicConfig(level=logging.DEBUG)
else:
	logging.basicConfig(filename='app.log', filemode='w', level=logging.ERROR)

import photon
if debug:
	bot = photon.Bot("305643264:AAGwALg3QDiH2OrNzqehgoPdeXwpIqY416c")
else:
	bot = photon.Bot("1410154354:AAEd9YJFFowWQrlkI3gPV0KkdT_PG7fNpeY")

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker as _sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import yaml
from object_dict import objectify

languages = []
for x in ['language_en.yaml']:
	languages.append(objectify(yaml.load(open(x).read(), Loader=yaml.Loader)))

class db:
	engine = create_engine('sqlite:///datebase.db', echo=debug)
	sessionmaker = _sessionmaker(bind=engine)
	base = declarative_base()
	session = sessionmaker()

import dbscheme
db.base.metadata.create_all(db.engine)