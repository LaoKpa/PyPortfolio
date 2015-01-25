from datetime import *

# Exclude weekends
# Note: instead of timedelta(days = n) another function should be used compare and shift dates
# if n%5 == 0 then d.shift(n) := d + timedelta(days = 7*(n/5)), that is, if we shift d five working days
# this is the same as add 7 days. The formula cames from induction
# so d.shift(5*a + b) = (d + timedelta(days = 7*a)).shift(b)
# let weekday(d) = 0,1,2,3,4
# for a given date d, we can set b such than 0 <= (weekday(d) + b) < 5
# then n = 5a + b => 0 <= weekday(d) + n - 5a < 5   ==>   -1 + (weekday(d) + n)/5 < n <= (weekday(d) + n)/5
# that is a = floor((weekday(d) + n)/5) and b is the remainder
# so d.shift(n) = d + timedelta(days = 7*a + b)
# where shift only need to be defined within a week

class workingday(date):
	def __init__(self, year, month, day):
		date.__init__(year, month, day)
		assert workingday.__valid(self)

	def __add__(self, n):
		return self.__shift(n)

	def __sub__(self, other):
		if isinstance(other, int):
			return self.__shift(-other)
		elif isinstance(other, workingday):
			w1 = self.weekday()
			d1 = super(workingday, self).__add__(timedelta(days = -w1))
			d2 = super(workingday, other).__add__(timedelta(days = -w1))
			# now d1 - d2 = 7*a + b
			a, b = divmod((d1 - d2).days, 7)
			return 5*a + b

	def __shift(self, n):
		a = int((self.weekday() + n)/5)
		b = n - 5*a
		d = super(workingday, self).__add__(timedelta(days = 7*a + b))
		return workingday(d.year, d.month, d.day)

	@staticmethod
	def __valid(date):
		if date.weekday() in [5, 6]:
			return False
		else:
			return True

	@staticmethod
	def firstworkingday(year, month):
		pass

	@staticmethod
	def lastworkingday(year, month):
		pass