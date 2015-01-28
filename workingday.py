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
		elif isinstance(other, workingday):   # not well writen
			w_self = self.weekday()
			w_other = other.weekday()
			b = w_self - w_other
			a = int(((super(workingday, self).__sub__(other)).days-b)/7)
			return 5 * a + b

	def __shift(self, n):
		a = int((self.weekday() + n)/5)
		b = n - 5*a
		d = super(workingday, self).__add__(timedelta(days = 7*a + b))
		return workingday(d.year, d.month, d.day)

	def __str__(self):
		return super(workingday, self).__str__()

	def date(self):
		return date(self.year, self.month, self.day)

	@staticmethod
	def today():
		d = date.today()
		w = d.weekday()
		if w in [5,6]:
			d -= timedelta(7-w)
		return workingday(d.year, d.month, d.day)

	@staticmethod
	def strptime(inputstr, strformat):
		d = datetime.strptime(inputstr, strformat)
		return workingday(d.year, d.month, d.day)

	@staticmethod
	def __valid(date):
		if date.weekday() in [5, 6]:
			return False
		else:
			return True

	@staticmethod
	def first(year, month):
		w = date(year, month, 1).weekday()
		shift = 0
		if w in [5, 6]:
			shift = 7 - w
		return workingday(year, month, 1 + shift)

	@staticmethod
	def last(year, month):
		a, month = divmod(month, 12)
		return workingday.first(year+a, month+1) - 1