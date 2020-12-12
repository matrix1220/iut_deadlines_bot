
from sqlalchemy.types import TypeDecorator, VARCHAR
import json

class JSONEncoded(TypeDecorator):
    impl = VARCHAR

    def process_bind_param(self, value, dialect):
        if value is not None: value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None: value = json.loads(value)
        return value

from sqlalchemy.ext.mutable import Mutable, MutableList, MutableDict

class MutableObject(MutableDict):
	@classmethod
	def coerce(cls, key, value):
		if isinstance(value, dict):
			return MutableObject(value)
		return MutableDict.coerce(key, value)

	def __setattr__(self, attr, value):
		MutableDict.__setitem__(self, attr, value)

	def __getattr__(self, attr):
		if attr in self: return self[attr]
		else: return object.__getattr__(self, attr)

	def __getitem__(self, index):
		return MutableDict.__getitem__(self, index)