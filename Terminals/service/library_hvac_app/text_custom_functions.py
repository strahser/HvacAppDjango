import io


class StringBuilder:
	_file_str = None

	def __init__(self):
		self._file_str = io.StringIO()

	def Append(self, str):
		self._file_str.write(str)

	def __str__(self):
		return self._file_str.getvalue()
