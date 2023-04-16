class BrokenConnectionError(Exception):
	def __init__(self):
		pass


class EmptyFileError(Exception):
	def __init__(self, text: str):
		self.text = text


class GroupCommentsClosedError(Exception):
	def __init__(self, text: str):
		self.text = text
