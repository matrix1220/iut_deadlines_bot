from config import bot, db, languages
from photon import response, inline_button, handler
from dbscheme import User, Group, Subject, Deadline, GroupSubject, DoneDeadline
from photon.utils import format

from sqlalchemy import and_

import datetime, random, string, re

session = db.session

def shorten_name(name):
	#return re.sub("_+","_", re.sub("[^a-zA-Z0-9]","_", name))
	return re.sub("([^_])[^_]*_?","\\1", re.sub("_+","_", re.sub("[^a-zA-Z0-9]","_", name))).upper()

@handler
class SelectLanguage:
	async def act(user):
		user.passes() # SelectLanguage.ids
		text = ''
		keyboard = []
		for language in languages:
			text += language.select_language + "\n"
			keyboard.append([language.language])
		return response.sendMessage(user.id, text, keyboard=keyboard)
	async def handle_text(user, text):
		for x, language in enumerate(languages):
			if text == language.language:
				user.language = x
				user.lang = languages[user.language]
				return user.back()

@handler
class MainMenu:
	async def act(user):
		user.goback = []
		if user.language==None: return await user.act(SelectLanguage)()
		user.passes() # MainMenu.ids
		if user.group_id:
			keyboard = [[user.lang.main_menu.deadlines], [user.lang.main_menu.my_group], [user.lang.main_menu.my_subjects]]
			return response.sendMessage(user.id, user.lang.main_menu.title, keyboard=keyboard)
		else:
			keyboard = [[user.lang.main_menu.new_group]]
			return response.sendMessage(user.id, user.lang.main_menu.not_in_group, keyboard=keyboard)

	async def handle_text(user, text):
		if user.group_id:
			if text == "/help":
				return response.sendMessage(user.id, user.lang.help)
			elif text == "/about":
				return response.sendMessage(user.id, user.lang.about)
			elif text == user.lang.main_menu.deadlines:
				return await user.act(Deadlines)()
			elif text == user.lang.main_menu.my_group:
				return await user.act(MyGroup)()
			elif text == user.lang.main_menu.my_subjects:
				return await user.act(MySubjects)()
		else:
			if text == user.lang.main_menu.new_group:
				return await user.act(NewGroup)()
			else:
				group = session.query(Group).filter(Group.code==text).first()
				if not group: return response.sendMessage(user.id, user.lang.not_found)
				user.group_id = group.id
				return await user.act(MyGroup)()

@handler
class Deadlines:
	async def act(user):
		if not user.group_id: return response.sendMessage(user.id, user.lang.error)
		user.passes() # Deadlines.ids
		deadlines = session.query(Deadline).filter(and_(
			Deadline.subject_id.in_(session.query(GroupSubject.subject_id).filter(GroupSubject.group_id==user.group_id).cte()),
			Deadline.id.notin_(session.query(DoneDeadline.deadline_id).filter(DoneDeadline.user_id==user.id).cte())
		)).all()

		text = "Deadlines:\n"

		for deadline in deadlines:
			text += f"/{deadline.id} {deadline.subject.name} {deadline.name}\n{datetime.datetime.fromtimestamp(deadline.deadline)}\n\n"

		if len(deadlines)==0:
			text += user.lang.empty


		keyboard = [[user.lang.deadlines.refresh], [user.lang.back]]
		return response.sendMessage(user.id, text, keyboard=keyboard)

	async def handle_text(user, text):
		if text == user.lang.back: return user.back()
		elif text == user.lang.deadlines.refresh: return await user.explicit_act(Deadlines)()
		deadlines = session.query(Deadline).filter(
			Deadline.subject_id.in_(session.query(GroupSubject.subject_id).filter(GroupSubject.group_id==user.group_id).cte())
		).all()
		for deadline in deadlines:
			if text == f"/{deadline.id}":
				return await user.act(DeadlineMenu)(deadline_id=deadline.id)

@handler
class DeadlineMenu:
	async def act(user, deadline_id):
		user.passes() # DeadlineMenu.ids
		user.menu_arguments = {"deadline_id":deadline_id}
		deadline = session.query(Deadline).filter(Deadline.id==deadline_id).first()
		if not deadline: return user.back()
		text = f"{deadline.subject.name}\n{deadline.name}\n{datetime.datetime.fromtimestamp(deadline.deadline)}"

		done_deadline = session.query(DoneDeadline).filter(and_(
			DoneDeadline.user_id==user.id,
			DoneDeadline.deadline_id==deadline.id
		)).first()

		keyboard = []
		if done_deadline:
			keyboard.append([user.lang.deadline_menu.mark_as_undone])
		else:
			keyboard.append([user.lang.deadline_menu.mark_as_done])

		if deadline.subject.owner==user.id:
			keyboard.append([user.lang.deadline_menu.edit])

		keyboard.append([user.lang.back])

		return response.sendMessage(user.id, text, keyboard=keyboard)

	async def handle_text(user, text):
		if text == user.lang.back:
			return user.back()
		elif text == user.lang.deadline_menu.edit:
			return await user.act(EditDeadline)(user.menu_arguments.deadline_id)

		done_deadline = session.query(DoneDeadline).filter(and_(
			DoneDeadline.user_id==user.id,
			DoneDeadline.deadline_id==user.menu_arguments.deadline_id
		)).first()	

		if text == user.lang.deadline_menu.mark_as_done:
			if done_deadline: return user.back()
			done_deadline = DoneDeadline(user_id=user.id, deadline_id=user.menu_arguments.deadline_id)
			session.add(done_deadline)
			bot.sendMessage(user.id, user.lang.successful)
			return user.back()
		elif text == user.lang.deadline_menu.mark_as_undone:
			if not done_deadline: return user.back()
			session.delete(done_deadline)
			bot.sendMessage(user.id, user.lang.successful)
			return user.back()

@handler
class MyGroup:
	async def act(user):
		user.passes() # MyGroup.ids

		group = session.query(Group).filter(Group.id==user.group_id).first()
		subjects = session.query(Subject).filter(
			Subject.id.in_(session.query(GroupSubject.subject_id).filter(GroupSubject.group_id==user.group_id).cte())
		)
		text = f"Name: {group.name}\ncode: `{group.code}`\n\n"
		for subject in subjects:
			text += f"/{subject.shortname} {subject.name}\n"
		keyboard = [[user.lang.my_group.add_subject], [user.lang.my_group.leave_group], [user.lang.back]]
		return response.sendMessage(user.id, text, keyboard=keyboard, parse_mode="Markdown")

	async def handle_text(user, text):
		if text == user.lang.back: return user.back()
		elif text == user.lang.my_group.add_subject:
			return await user.act(MyGroup.AddSubject)()
		elif text == user.lang.my_group.leave_group:
			user.group_id = None
			return await user.explicit_act(MainMenu)()

		subjects = session.query(Subject).filter(
			Subject.id.in_(session.query(GroupSubject.subject_id).filter(GroupSubject.group_id==user.group_id).cte())
		)
		for subject in subjects:
			if text == f"/{subject.shortname}":
				return await user.act(SubjectMenu)(subject_id=subject.id)

	@handler
	class AddSubject:
		async def act(user):
			user.passes() # MyGroup.AddSubject.ids
			return response.sendMessage(user.id, user.lang.my_group.enter_subject_code, keyboard=[[user.lang.back]])
		async def handle_text(user, text):
			if text == user.lang.back: return user.back()
			subject = session.query(Subject).filter(Subject.code==text).first()
			if not subject: return response.sendMessage(user.id, user.lang.not_found)
			group_subject = GroupSubject(group_id=user.group_id, subject_id=subject.id)
			session.add(group_subject)
			bot.sendMessage(user.id, user.lang.successful)
			return user.back()

@handler
class NewGroup:
	async def act(user):
		user.menu_arguments = {}
		return await user.explicit_act(NewGroup.Name)()

	@handler
	class Name:
		async def act(user):
			user.passes() # NewGroup.Name.ids
			return response.sendMessage(user.id, user.lang.new_group.enter_name, keyboard=[[user.lang.back]])
		async def handle_text(user, text):
			if text == user.lang.back: return user.back()
			user.menu_arguments.name = text
			code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
			group = Group(owner=user.id, code=code, **dict(user.menu_arguments))
			session.add(group)
			session.commit()
			user.group_id = group.id
			bot.sendMessage(user.id, user.lang.successful)
			return user.back()

@handler
class MySubjects:
	async def act(user):
		user.passes() # MySubjects.ids
		subjects = session.query(Subject).filter(Subject.owner==user.id).all()
		text = "List of your subjects:\n"
		for x in subjects:
			text += f"/{x.shortname} {x.name}\n"

		if len(subjects)==0:
			text += user.lang.empty

		keyboard = [[user.lang.my_subjects.new_subject], [user.lang.back]]
		return response.sendMessage(user.id, text, keyboard=keyboard)

	async def handle_text(user, text):
		if text == user.lang.back:
			return user.back()
		elif text == user.lang.my_subjects.new_subject:
			return await user.act(NewSubject)()

		subjects = session.query(Subject).filter(Subject.owner==user.id)
		for subject in subjects:
			if text == f"/{subject.shortname}":
				return await user.act(SubjectMenu)(subject_id=subject.id)

@handler
class NewSubject:
	async def act(user):
		user.menu_arguments = {}
		return await user.act(NewSubject.Name)()

	# 	if text == user.lang.back: return user.back()
	@handler
	class Name:
		async def act(user):
			user.passes() # NewSubject.Name.ids
			return response.sendMessage(user.id, user.lang.new_subject.enter_name, keyboard=[[user.lang.back]])
		async def handle_text(user, text):
			if text == user.lang.back: return user.back()
			user.menu_arguments.name = text
			user.menu_arguments.shortname = shorten_name(text)
			return await user.explicit_act(NewSubject.ShortName)()

	@handler
	class ShortName:
		async def act(user):
			user.passes() # NewSubject.ShortName.ids
			return response.sendMessage(user.id, user.lang.new_subject.enter_shortname, keyboard=[[user.menu_arguments.shortname], [user.lang.back]])
		async def handle_text(user, text):
			if text == user.lang.back: return user.back()
			if re.match("[^a-zA-Z0-9_]", text)!=None: return response.sendMessage(user.id, user.lang.error)
			user.menu_arguments.shortname = text
			code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
			subject = Subject(owner=user.id, code=code, **dict(user.menu_arguments))
			session.add(subject)
			bot.sendMessage(user.id, user.lang.successful)
			return user.back()

@handler
class SubjectMenu:
	async def act(user, subject_id):
		user.passes() # SubjectMenu.ids
		user.menu_arguments = {"subject_id":subject_id}
		subject = session.query(Subject).filter(Subject.id==subject_id).first()
		text = f"Name: {subject.name}\nShortname: {subject.shortname}\ncode: `{subject.code}`\n\n"

		deadlines = session.query(Deadline).filter(Deadline.subject_id==subject_id).all()
		text += "Deadlines:\n"

		for deadline in deadlines:
			text += f"/{deadline.id} {deadline.name}\n{datetime.datetime.fromtimestamp(deadline.deadline)}\n\n"

		keyboard = [[user.lang.my_subjects.new_deadline], [user.lang.back]]
		return response.sendMessage(user.id, text, keyboard=keyboard)

	async def handle_text(user, text):
		if text == user.lang.back:
			return user.back()
		elif text == user.lang.my_subjects.new_deadline:
			return await user.act(NewDeadline)(subject_id=user.menu_arguments.subject_id)

		deadlines = session.query(Deadline).filter(Deadline.subject_id==user.menu_arguments.subject_id).all()
		for deadline in deadlines:
			if text == f"/{deadline.id}":
				return await user.act(DeadlineMenu)(deadline_id=deadline.id)

@handler
class EditDeadline:
	async def act(user, deadline_id):
		user.menu_arguments = {"deadline_id":deadline_id}
		deadline = session.query(Deadline).filter(Deadline.id==deadline_id).first()
		if not deadline: return response.sendMessage(user.id, user.lang.not_found)
		if deadline.subject.owner!=user.id: return response.sendMessage(user.id, "you do not have permission")
		keyboard = [
			[user.lang.edit_deadline.name],
			[user.lang.edit_deadline.shortname],
			[user.lang.edit_deadline.date],
			[user.lang.edit_deadline.time],
			[user.lang.edit_deadline.delete],
			[user.lang.back]
		]
		user.passes()
		return response.sendMessage(user.id, user.lang.edit_deadline.title, keyboard=keyboard)

	async def handle_text(user, text):
		if text == user.lang.back: return user.back()
		elif text == user.lang.edit_deadline.name: return await user.act(EditDeadline.Name)()
		elif text == user.lang.edit_deadline.shortname: return await user.act(EditDeadline.ShortName)()
		elif text == user.lang.edit_deadline.date: return await user.act(EditDeadline.Date)()
		elif text == user.lang.edit_deadline.time: return await user.act(EditDeadline.Time)()
		elif text == user.lang.edit_deadline.delete:
			deadline = session.query(Deadline).filter(Deadline.id==user.menu_arguments.deadline_id).first()
			session.delete(deadline)
			return user.back()

	@handler
	class Name:
		async def act(user):
			user.passes() # NewDeadline.Name.ids
			return response.sendMessage(user.id, user.lang.new_deadline.enter_name, keyboard=[[user.lang.back]])
		async def handle_text(user, text):
			if text == user.lang.back: return user.back()
			deadline = session.query(Deadline).filter(Deadline.id==user.menu_arguments.deadline_id).first()
			deadline.name = text
			return user.back()

	@handler
	class ShortName:
		async def act(user):
			user.passes() # NewDeadline.ShortName.ids
			return response.sendMessage(user.id, user.lang.new_deadline.enter_shortname, keyboard=[[user.lang.back]])
		async def handle_text(user, text):
			if text == user.lang.back: return user.back()
			if re.match("[^a-zA-Z0-9_]", text)!=None: return response.sendMessage(user.id, user.lang.error)
			deadline = session.query(Deadline).filter(Deadline.id==user.menu_arguments.deadline_id).first()
			deadline.shortname = text
			return user.back()

	@handler
	class Date:
		async def act(user):
			user.passes() # NewDeadline.Date.ids
			return response.sendMessage(user.id, user.lang.new_deadline.enter_date, keyboard=[[user.lang.back]])
		async def handle_text(user, text):
			if text == user.lang.back: return user.back()

			if matches := re.match(r"^(\d\d?)$", text):
				input_date = {"day": int(matches.group(1))}
			elif matches := re.match(r"^(\d\d?).(\d\d?)$", text):
				input_date = {"day": int(matches.group(1)), "month": int(matches.group(2))}
			elif matches := re.match(r"^(\d\d?).(\d\d?).(\d\d\d\d)$", text):
				input_date = {"day": int(matches.group(1)), "month": int(matches.group(2)), "year": int(matches.group(3))}
			else:
				return response.sendMessage(user.id, user.lang.error)

			deadline = session.query(Deadline).filter(Deadline.id==user.menu_arguments.deadline_id).first()

			try:
				date = datetime.datetime.fromtimestamp(deadline.deadline).replace(**input_date)
			except ValueError as e:
				return response.sendMessage(user.id, str(e))

			# if date < datetime.datetime.today():
			# 	return response.sendMessage(user.id, str(e))

			deadline.deadline = int(date.timestamp())
			return user.back()

	@handler
	class Time:
		async def act(user):
			user.passes() # NewDeadline.Time.ids
			return response.sendMessage(user.id, user.lang.new_deadline.enter_time, keyboard=[["23:59"], [user.lang.back]])
		async def handle_text(user, text):
			if text == user.lang.back: return user.back()

			if matches := re.match(r"^(\d\d):(\d\d)$", text):
				input_time = {"hour": int(matches.group(1)), "minute":int(matches.group(2)), "second":59}
			elif matches := re.match(r"^(\d\d):(\d\d):(\d\d)$", text):
				input_time = {"hour": int(matches.group(1)), "minute":int(matches.group(2)), "second":int(matches.group(3))}
			else:
				return response.sendMessage(user.id, user.lang.error)

			deadline = session.query(Deadline).filter(Deadline.id==user.menu_arguments.deadline_id).first()

			try:
				date = datetime.datetime.fromtimestamp(deadline.deadline).replace(**input_time)
			except ValueError as e:
				return response.sendMessage(user.id, str(e))

			deadline.deadline = int(date.timestamp())
			return user.back()

@handler
class NewDeadline:
	async def act(user, subject_id):
		user.menu_arguments = {"subject_id":subject_id}
		subject = session.query(Subject).filter(Subject.id==subject_id).first()
		if not subject: return response.sendMessage(user.id, user.lang.not_found)
		if not subject.allow_all:
			if subject.owner!=user.id: return response.sendMessage(user.id, "you do not have permission")
		return await user.act(NewDeadline.Name)()

	@handler
	class Name:
		async def act(user):
			user.passes() # NewDeadline.Name.ids
			return response.sendMessage(user.id, user.lang.new_deadline.enter_name, keyboard=[[user.lang.back]])
		async def handle_text(user, text):
			if text == user.lang.back: return user.back()
			user.menu_arguments.name = text
			user.menu_arguments.shortname = shorten_name(text)
			return await user.explicit_act(NewDeadline.ShortName)()

	@handler
	class ShortName:
		async def act(user):
			user.passes() # NewDeadline.ShortName.ids
			return response.sendMessage(user.id, user.lang.new_deadline.enter_shortname, keyboard=[[user.menu_arguments.shortname], [user.lang.back]])
		async def handle_text(user, text):
			if text == user.lang.back: return await user.explicit_act(NewDeadline.Name)()
			if re.match("[^a-zA-Z0-9_]", text)!=None: return response.sendMessage(user.id, user.lang.error)
			user.menu_arguments.shortname = text
			return await user.explicit_act(NewDeadline.Date)()

	@handler
	class Date:
		async def act(user):
			user.passes() # NewDeadline.Date.ids
			return response.sendMessage(user.id, user.lang.new_deadline.enter_date, keyboard=[[user.lang.back]])
		async def handle_text(user, text):
			if text == user.lang.back: return await user.explicit_act(NewDeadline.ShortName)()

			if matches := re.match(r"^(\d\d?)$", text):
				input_date = {"day": int(matches.group(1))}
			elif matches := re.match(r"^(\d\d?).(\d\d?)$", text):
				input_date = {"day": int(matches.group(1)), "month": int(matches.group(2))}
			elif matches := re.match(r"^(\d\d?).(\d\d?).(\d\d\d\d)$", text):
				input_date = {"day": int(matches.group(1)), "month": int(matches.group(2)), "year": int(matches.group(3))}
			else:
				return response.sendMessage(user.id, user.lang.error)

			try:
				date = datetime.datetime.today().replace(**input_date)
			except ValueError as e:
				return response.sendMessage(user.id, str(e))

			# if date < datetime.datetime.today():
			# 	return response.sendMessage(user.id, str(e))

			user.menu_arguments.deadline = input_date
			return await user.explicit_act(NewDeadline.Time)()

	@handler
	class Time:
		async def act(user):
			user.passes() # NewDeadline.Time.ids
			return response.sendMessage(user.id, user.lang.new_deadline.enter_time, keyboard=[["23:59"], [user.lang.back]])
		async def handle_text(user, text):
			if text == user.lang.back: return await user.explicit_act(NewDeadline.Date)()

			if matches := re.match(r"^(\d\d):(\d\d)$", text):
				input_time = {"hour": int(matches.group(1)), "minute":int(matches.group(2)), "second":59}
			elif matches := re.match(r"^(\d\d):(\d\d):(\d\d)$", text):
				input_time = {"hour": int(matches.group(1)), "minute":int(matches.group(2)), "second":int(matches.group(3))}
			else:
				return response.sendMessage(user.id, user.lang.error)

			try:
				date = datetime.datetime.today().replace(**user.menu_arguments.deadline, **input_time)
			except ValueError as e:
				return response.sendMessage(user.id, str(e))

			user.menu_arguments.deadline = int(date.timestamp())

			deadline = Deadline(**dict(user.menu_arguments))
			session.add(deadline)
			bot.sendMessage(user.id, user.lang.successful)
			return user.back()

# class NewDeadline:
# 	async def act(user):
# 		user.passes() # NewDeadline.ids
# 		keyboard = [[user.lang.select], [user.lang.my_subjects.new_subject], [user.lang.back]]
# 		return response.sendMessage(user.id, text, keyboard=keyboard)

# 	async def handle_text(user, text):
# 		if text == user.lang.back:
# 			return user.back()
# 		elif text == user.lang.my_subjects.new_subject:
# 			return act(MySubjects.NewSubject)(user)	

# class Orders(CallbackHandler):
# 	async def act(user):
# 		return response.sendMessage(user.id, user.lang.select, inline_keyboard=keyboard)
# 	async def handle_callback(user, query, data):
# 		pass
