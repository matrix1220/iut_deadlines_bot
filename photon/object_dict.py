class ObjectDict(dict):
	def __setattr__(self, attr, value):
		dict.__setitem__(self, attr, value)

	def __getattr__(self, attr):
		if attr in self: return self[attr]
		else: return None

	def __repr__(self):
		return 'ObjectDict(' + dict.__repr__(self) + ')'

	def __add__(self, other):
		return {**self, **other}

	def __bool__(self):
		return bool(self.keys())

	# def __getitem__(self, index):
	# 	return dict.__getitem__(self, index)

def objectify(data):
	if isinstance(data, dict):
		for x, y in data.items(): data[x] = objectify(y)
		data = ObjectDict(data)
	elif isinstance(data, list):
		for x, y in enumerate(data): data[x] = objectify(y)
	return data

def dictify(data):
	if isinstance(data, dict):
		for x, y in data.items(): data[x] = dictify(y)
	elif isinstance(data, list):
		for x, y in enumerate(data): data[x] = dictify(y)
	return data