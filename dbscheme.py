from sqlalchemy import Integer, String, Boolean, Text, DateTime
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship

from sqlalchemy.ext.declarative import declarative_base
base = declarative_base()

from dbscheme_types import JSONEncoded, MutableObject
from sqlalchemy.ext.mutable import MutableList

from botcore import User as _User


class User(base, _User):
	__tablename__ = 'users'

	id = Column(Integer, primary_key=True)
	menu = Column(MutableList.as_mutable(JSONEncoded))
	menu_arguments = Column(MutableObject.as_mutable(JSONEncoded))
	goback = Column(MutableList.as_mutable(JSONEncoded))
	language = Column(Integer)
	group_id = Column(Integer)
	#blocked = Column(Boolean, default=False)


#from enum import IntEnum

class TelegramGroup(base):
	__tablename__ = 'telegram_groups'

	id = Column(Integer, primary_key=True)
	group_id = Column(Integer)

class Group(base):
	__tablename__ = 'groups'

	id = Column(Integer, primary_key=True)
	owner = Column(Integer)
	code = Column(String)

	name = Column(String)

class GroupSubject(base):
	__tablename__ = 'group_subjects'

	id = Column(Integer, primary_key=True)
	group_id = Column(Integer)
	subject_id = Column(Integer)

# class GroupUser(base):
# 	__tablename__ = 'group_users'

# 	id = Column(Integer, primary_key=True)
# 	user_id = Column(Integer)
# 	group_id = Column(Integer)

class Subject(base):
	__tablename__ = 'subjects'

	id = Column(Integer, primary_key=True)
	owner = Column(Integer)
	code = Column(String)
	allow_all = Column(Boolean, default=True)

	name = Column(String)
	shortname = Column(String)

class SubjectAdmin(base):
	__tablename__ = 'subject_admins'

	id = Column(Integer, primary_key=True)
	subject_id = Column(Integer)
	user_id = Column(Integer)

class Deadline(base):
	__tablename__ = 'deadlines'

	id = Column(Integer, primary_key=True)
	subject_id = Column(Integer, ForeignKey('subjects.id'))
	subject = relationship("Subject")
	deadline = Column(Integer)

	name = Column(String)
	shortname = Column(String)
	#description = Column(String)

class DoneDeadline(base):
	__tablename__ = 'done_deadlines'

	id = Column(Integer, primary_key=True)
	user_id = Column(Integer)
	deadline_id = Column(Integer)

from config import db
base.metadata.create_all(db.engine)