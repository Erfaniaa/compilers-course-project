class x:
	y = {}

	def __init__(self, y):
		self.y = y

	def a(self):
		self.y.prin()


class yy:
	def prin(self):
		print('hello')


z = yy()
w = x(z)
w.a()
