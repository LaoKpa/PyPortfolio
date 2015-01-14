#!/usr/bin/env python
from datetime import *

class TimeWindow:

	def __init__(self, begin, end):
		"""
		Creates a new TimeWindow begining at 'begin' and ending at 'end'
		if begin is after end then TimeWindow will be declared as void

		The set of TimeWindows is in bijection with {(a,b)\in \Z^2 | a <= b} \cup {*}
		where * is the void TimeWindow and the integers a, b came from a given bijection
		between date and the set of integers \Z
		"""
		if begin > end:
			self.void = True
		
		else:
			self.begin = begin
			self.end = end
			self.void = False

	def __and__(self, other):
		"""
		Returns the intersection of two TimeWindows W & W'
		This operation satisfies:
			W & W = W 			(idempotent)
			W & W' = W' & W 	(commutative)
			W & * = * 			(absorbing element)
		"""
		if self.void or other.void:
			return TimeWindow.void()

		elif self.begin > other.end or other.begin > self.end:
			return TimeWindow.void()

		else:
			return TimeWindow(
				max(self.begin, other.begin),
				min(self.end,   other.end))

	def __contains__(self, other): 
		"""
		Returns True or False
		'c' establishes an order within the TimeSeries
		in particular:
			* c W, for all W
			W & W' c W for all W, W'
			W + n ~c W for all W, n\in\Z, except when W = *
		"""
		if self.void:
			return False

		if isinstance(other, TimeWindow):
			if other.void:
				return True
			elif other.begin >= self.begin and other.end <= self.end:
				return True

		elif isinstance(other, date):
			if other >= self.begin and other <= self.end:
				return True
		
		return False

	def __len__(self):
		"""
		Returns the lenght of the TimeWindow
		Satisfies:
			* len(W) >= 0
				equality occurs if and only if W = *
				otherwise (that is, if W != *) len(W) > 0
			* len(W + n) = len(W)
			* len(W & W') <= min(len(W), len(W'))
				equality occurs if and only if W = W'
				otherwise (that is, if W != W') len(W & W') < min(len(W), len(W'))
		"""
		if self.void:
			return 0
		else:
			return (self.end - self.begin).days + 1

	def shift(self, N):
		"""
		This operatior moves the TimeWindow n days forward
		if n is negative it moves TimeWindow -n bays backwards
		"""
		if self.void:
			return self
		else:
			return TimeWindow(
				self.begin + timedelta(days = N),
				self.end   + timedelta(days = N))

	def __add__(self, N):
		return self.shift(N)

	def __sub__(self, N):
		return self.shift(-N)

	def rolling(self, N):
		"""
		This operatior is equivalent to W & (W+N-1)
		"""
		return (self & self.shift(N-1))

	def __str__(self):
		return self.begin.strftime('%d/%m/%Y') + ' - ' + self.end.strftime('%d/%m/%Y') 

	@staticmethod
	def void():
		return TimeWindow(1,0)

	@staticmethod
	def year(year):
		begin = date(year,1,1)
		end = date(year,12,31)
		return TimeWindow(begin, end)

	@staticmethod
	def years(year1, year2):
		assert not year1 > year2
		begin = date(year1,1,1)
		end = date(year2,12,31)
		return TimeWindow(begin, end)

class DateSerie(dict):
	
	def TimeSerie(self):
		ts = []
		date = sorted(self.keys())
		d = date[0]
		x = self[d]
		ts.append(x)
		for i in xrange(1, len(date)):
			d_l = d
			x_l = x
			d = date[i]
			x = self[d]
			L = (d - d_l).days
			for j in range(L):
				ts.append(x_l + (x - x_l) * (j + 1) / float(L))
		return TimeSerie(ts, TimeWindow(min(self.keys()), max(self.keys())))

	def map(self, f):
		h = DateSerie()
		for d, v in self.iteritems():
			h[d] = f(v)
		return h		


class TimeSerie(list):
	"""
	pairs (W, x)
		x \in A^{len(W)}

	We have the injections for a\in A:
		i_a: W -> (W, a^{len(W)})
	And the projection:
		p : (W, x) -> W
	"""

	def __init__(self, ts, TimeWindow):
		"""
		We need to assert that the length of the list equals the length of the TimeWindow
		in further versions we may consider TimeSeries ignoring weekends (when almost all markets are closed)
		or just for specifics days, as the end of the weeks, months or years
		"""
		assert len(ts) == len(TimeWindow)
		self.extend(ts)
		self.TimeWindow = TimeWindow

	@staticmethod
	def void():
		return TimeSerie([], TimeWindow.void())

	def DateSerie(self):
		h = dict()
		begin = self.TimeWindow.begin
		for i in xrange(len(self)):
			h[begin + timedelta(days = i)] = self[i]
		return h

	def shift(self, N):
		"""
		This is the operation that sends (W, x) to (W + n, x)
		"""
		return TimeSerie(self, self.TimeWindow.shift(N))

	def __and__(self, TimeWindow):
		"""
		This is the operation & of TimeWindow extended to TimeSerie 
		TimeWindow operates in TimeSerie through:
			(W, x) & W' = (W & W', x|)
			where x| is defined by:
				x|_n = x_{n + max(b'-b, 0)}

		notice that:
			* i_a(W) & W' = i_a(W & W')
			* p((W, x) & W') = W & W'

		"""
		W = self.TimeWindow & TimeWindow
		if not W.void:
			shift = (W.begin - self.TimeWindow.begin).days
			ts = self[shift : len(W) + (W.begin - self.TimeWindow.begin).days]
			return TimeSerie(ts, W)
		else:
			return TimeSerie.void()

	def drawdown(self):
		"""
		calculates the drawdown of the list
		that is, the serie dd_n = max(x[:n]) - x[n]
		"""
		if len(self) > 0:
			T = [self[0]]
			drawdown = [0]
			for i in xrange(1, len(self)):
				T.append(max(T[-1], self[i]))
				drawdown.append(T[i] - self[i])
			return TimeSerie(drawdown, self.TimeWindow)
		else:
			return self

	def maxValue(self):
		"""
		calculates the max of the list until the current day,
		that is, max_n = max(x[:n])
		"""
		if len(self) > 1:
			M = [self[0]]
			for i in xrange(1, len(self)):
				M.append(max(M[-1], self[i]))
			return TimeSerie(M, self.TimeWindow)
		else:
			return self

	def sma(self, N = 7):
		""" Simple Moving Average """
		if len(self) < N:
			return TimeSerie.void()
		else:
			sma = [sum(self[0:N])/N]
			for i in xrange(N, len(self)):
				sma.append(sma[-1] + (self[i] - self[i-N])/N)
			return TimeSerie(sma, self.TimeWindow.rolling(N))

	def wma(self, N = 7):
		""" Weighted Moving Average """
		if len(self) < N:
			return TimeSerie.void()
		else:
			D = N * (N + 1) / 2
			sma = self.sma(N)
			wma = [sum([(i+1) * self[i] for i in xrange(N)])]
			for i in xrange(N, len(self)):
				wma.append((N * self[i] + D * wma[i-N] - N * sma[i-N])/D)
			return TimeSerie(wma, self.TimeWindow.rolling(N))

	# verificar
	def variation(self, N = 1):
		""" Returns P_t - P_{t-N} """
		r = []
		for i in xrange(N, len(self)):
			r.append(self[i] - self[i-N])
		return TimeSerie(r, self.TimeWindow.rolling(N+1))

	def map(self, f):
		return TimeSerie(map(f, self), self.TimeWindow)

	def __add__(self, other):
		"""
		if 'other' is of numeric type, then
			(W, x) + a = (W, x + a)
			where x + a is defined by (x+a)_n = x_n + a
		if 'other' is another TimeSerie, then
			(W, x) + (W', x') = (W & W', x'')
			where x'' is defined by x''_n = x_{n + max(b'-b, 0)} + x'_{n + max(b-b', 0)}
		"""

		if isinstance(other, (int, float, long, complex)):
			return self.map(lambda x: x + other)

		elif isinstance(other, TimeSerie):
			W = self.TimeWindow & other.TimeWindow
			if W.void:
				return TimeSerie.void()
			else:
				ts = []
				d_s = (W.begin - self.TimeWindow.begin).days
				d_o = (W.begin - other.TimeWindow.begin).days
				for i in xrange(len(W)):
					ts.append(self[d_s + i] + other[d_o + i])
				return TimeSerie(ts, W)

	def __sub__(self, other):

		if isinstance(other, (int, float, long, complex)):
			return self.map(lambda x: x - other)

		elif isinstance(other, TimeSerie):
			W = self.TimeWindow & other.TimeWindow
			if W.void:
				return TimeSerie.void()
			else:
				ts = []
				d_s = (W.begin - self.TimeWindow.begin).days
				d_o = (W.begin - other.TimeWindow.begin).days
				for i in xrange(len(W)):
					ts.append(self[d_s + i] - other[d_o + i])
				return TimeSerie(ts, W)

	def __mul__(self, other):

		if isinstance(other, (int, float, long, complex)):
			return self.map(lambda x: x * other)

		elif isinstance(other, TimeSerie):
			W = self.TimeWindow & other.TimeWindow
			if W.void:
				return TimeSerie.void()
			else:
				ts = []
				d_s = (W.begin - self.TimeWindow.begin).days
				d_o = (W.begin - other.TimeWindow.begin).days
				for i in xrange(len(W)):
					ts.append(self[d_s + i] * other[d_o + i])
				return TimeSerie(ts, W)

	def __div__(self, other):

		if isinstance(other, (int, float, long, complex)):
			return self.map(lambda x: x / other)

		elif isinstance(other, TimeSerie):
			W = self.TimeWindow & other.TimeWindow
			if W.void:
				return TimeSerie.void()
			else:
				ts = []
				d_s = (W.begin - self.TimeWindow.begin).days
				d_o = (W.begin - other.TimeWindow.begin).days
				for i in xrange(len(W)):
					ts.append(self[d_s + i] / other[d_o + i])
				return TimeSerie(ts, W)

	def __abs__(self):
		return self.map(abs)

	def log(self):
		from math import log
		return self.map(log)

	def exp(self):
		from math import exp
		return self.map(exp)

	def var(self, N): 
		"""
		Returns variance for a moving window of size N
		For a given day t, its value is the variance of the timeserie in the interval [t-(w-1), t]
		"""
		if len(self) < N:
			return TimeSerie.void()

		s_x  = 0
		s_xx = 0

		for i in xrange(N):
			s_x  += self[i]
			s_xx += self[i]**2

		var = [(s_xx - s_x * s_x / N) / (N - 1)]
		for i in xrange(N, len(self)):
			s_x  += self[i] - self[i-N]
			s_xx += self[i]**2 - self[i-N]**2
			var.append((s_xx - s_x * s_x / N) / (N - 1))

		return TimeSerie(var, self.TimeWindow.rolling(N))

	def stdev(self, N):
		return self.var(N)**.5