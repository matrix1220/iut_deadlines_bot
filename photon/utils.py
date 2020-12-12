
def format(data, **kwargs):
	if isinstance(data, list):
		for x, y in enumerate(data): data[x] = format(y, **kwargs)
	elif isinstance(data, dict):
		for x, y in data.items(): data[x] = format(y, **kwargs)
	elif isinstance(data, str):
		return data.format(**kwargs)
	return data


