from sqlalchemy import Integer, String, Boolean, Text, DateTime
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship

from config import db, languages
Base = db.base

from .types import JSONEncoded, MutableObject, MutableList

from photon.persistence.sqlalchemy import User as _User


class User(Base, _User):
	__tablename__ = 'users'

	id = Column(Integer, primary_key=True)
	menu_arguments = Column(MutableObject.as_mutable(JSONEncoded))
	language = Column(Integer)
	group_id = Column(Integer)
	#blocked = Column(Boolean, default=False)
	def find_user(user_id):
		user = db.session.query(User).filter(User.id==user_id).first()
		if not user:
			user = User(id=user_id)
			db.session.add(user)

		user.lang = languages[user.language] if user.language else None

		return user


#from enum import IntEnum

class TelegramGroup(Base):
	__tablename__ = 'telegram_groups'

	id = Column(Integer, primary_key=True)
	group_id = Column(Integer)

class Group(Base):
	__tablename__ = 'groups'

	id = Column(Integer, primary_key=True)
	owner = Column(Integer)
	code = Column(String)

	name = Column(String)

class GroupSubject(Base):
	__tablename__ = 'group_subjects'

	id = Column(Integer, primary_key=True)
	group_id = Column(Integer)
	subject_id = Column(Integer)

# class GroupUser(Base):
# 	__tablename__ = 'group_users'

# 	id = Column(Integer, primary_key=True)
# 	user_id = Column(Integer)
# 	group_id = Column(Integer)

class Subject(Base):
	__tablename__ = 'subjects'

	id = Column(Integer, primary_key=True)
	owner = Column(Integer)
	code = Column(String)
	allow_all = Column(Boolean, default=True)

	name = Column(String)
	shortname = Column(String)

class SubjectAdmin(Base):
	__tablename__ = 'subject_admins'

	id = Column(Integer, primary_key=True)
	subject_id = Column(Integer)
	user_id = Column(Integer)

class Deadline(Base):
	__tablename__ = 'deadlines'

	id = Column(Integer, primary_key=True)
	subject_id = Column(Integer, ForeignKey('subjects.id'))
	subject = relationship("Subject")
	deadline = Column(Integer)

	name = Column(String)
	shortname = Column(String)
	#description = Column(String)

class DoneDeadline(Base):
	__tablename__ = 'done_deadlines'

	id = Column(Integer, primary_key=True)
	user_id = Column(Integer)
	deadline_id = Column(Integer)