#!/usr/bin/env python
from datetime import *
from timewindow import *
from dateserie import *
import numpy as np

# Create the following functions:
# TimeSerie
#	* __getitem__(date)
#	* autocorr(N) #  N - window size
#	* GARCH(s0 = 0.001, w = 0.001, a = 0.05, b = 0.094)
#	* Hurst(N  = 365)
#   * Fourier(i, N = 365)
#	* FourierArray(N)
#	* FrequencyFilter(filter)			filter is a list or an array
#	* SimpleLinearRegr(N, shift = 1, returnCoefs = False)
#	* SimplePolyRegr(n, N, shift = 1, returnCoefs = False)
#	* MultLinearRegr(X, N, shift = 1, returnCoefs = False)
#	* @staticmethod cov(X, Y, N = 365)
#	* @staticmethod corr(X, Y, N = 365)
#	* @staticmethod covGARCH(X, Y, s0 = 0.001, w = 0.001, a = 0.05, b = 0.094)
# covMatrix(dict, pairMethod = TimeSerie.corr)

# use np.ndarray instead of list in TimeSerie

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

	def Integral(self):
		"""
		Reconstruct a timeSerie from its derivative
		we set the first value as 0
		"""
		if self.void:
			return self
		else:
			ts = [0]
			for i in xrange(len(self)):
				ts.append(ts[-1] + self[i])
			return TimeSerie(ts, TimeWindow(self.TimeWindow.begin - timedelta(days = 1), self.TimeWindow.end)) # the is a more elegant formula?

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
		return self.var(N).map(lambda x: x**.5)

	def SimpleLinearRegr(self, N, shift = 1):

		assert N > 1

		if len(self) < N:
			return TimeSerie.void()

		s_x  = 0
		s_xx = 0
		s_y  = 0
		s_xy = 0
		s_yy = 0

		# existe uma formula para s_x e s_xx

		for i in xrange(N):
			s_x  += i
			s_y  += self[i]
			s_xx += i * i
			s_xy += i * self[i]
			s_yy += self[i] * self[i]

		b0 = (s_y * s_xx - s_x * s_xy)/(N * s_xx - s_x ** 2)
		b1 = (N * s_xy - s_x * s_y)/(N * s_xx - s_x ** 2)
		B0 = [b0]
		B1 = [b1]
		r =  [(N * s_xy - s_x * s_y)/((N * s_xx - s_x ** 2) * (N * s_yy - s_y ** 2))**.5]

		y = [b0 + b1 * (N + shift - 1)]

		for t in xrange(N, len(self)):
			s_x  += N
			s_y  += self[t] - self[t-N]
			s_xx += t**2 - (t-N)**2
			s_xy += t * self[t] - (t-N) * self[t-N]
			s_yy += self[t] ** 2 - self[t-N] ** 2

			b0 = (s_y * s_xx - s_x * s_xy)/(N * s_xx - s_x ** 2)
			b1 = (N * s_xy - s_x * s_y)/(N * s_xx - s_x ** 2)
			#b0 = (s_y * (s_xx - (t - N) * s_x) + s_xy * (N * (t - N) - s_x))/(N * s_xx - s_x ** 2)
			#b1 = (N * s_xy - s_x * s_y)/(N * s_xx - s_x ** 2)

			B0.append(b0)
			B1.append(b1)
			r.append((N * s_xy - s_x * s_y)/((N * s_xx - s_x ** 2) * (N * s_yy - s_y ** 2))**.5)
			y.append(b0 + b1 * (t + shift))

		return TimeSerie(y, self.TimeWindow.rolling(N) + shift)