#!/usr/bin/env python
from workingday import *
from dateserie import *
import timewindow
import numpy as np

# Create the following functions:
#	* __getitem__(date)
#	* autocorr(N)
#	* Hurst(N)
#   * Fourier(i, N)
#	* ema(N)


class TimeSerie(list):
	""" Pairs (W, x), where x \in A^{len(W)} """

	def __init__(self, ts, TimeWindow):
		"""
		We need to assert that the length of the list equals the length of the TimeWindow
		in further versions we may consider TimeSeries ignoring weekends (when almost all markets are closed)
		or just for specifics days, as the end of the weeks, months or years
		"""
		if isinstance(ts, list):
			assert len(ts) == len(TimeWindow)
			self.extend(ts)
			self.TimeWindow = TimeWindow
		else: # is a scalar
			"""
			We have the injections for a\in A:
			i_a: W -> (W, a^{len(W)})
			"""
			for i in xrange(len(TimeWindow)):
				self.append(ts)
			self.TimeWindow = TimeWindow

	@staticmethod
	def void():
		return TimeSerie([], TimeWindow.void())

	def DateSerie(self):
		h = dict()
		begin = self.TimeWindow.begin
		for i in xrange(len(self)):
			h[begin + i] = self[i]
		return h

	def keys(self):
		keys = []
		begin = self.TimeWindow.begin
		for i in xrange(len(self)):
			keys.append((begin + i).date())
		return keys

	def Integral(self):
		"""
		Reconstruct a timeSerie from its derivative
		we set the first value as 0
		"""
		if self.TimeWindow.void:
			return self
		else:
			ts = [0]
			for i in xrange(len(self)):
				ts.append(ts[-1] + self[i])
			return TimeSerie(ts, self.TimeWindow.extendleft())

	def shift(self, N):
		""" This is the operation that sends (W, x) to (W + n, x) """
		return TimeSerie(self, self.TimeWindow.shift(N))

	def __and__(self, TimeWindow):
		"""
		This is the operation & of TimeWindow extended to TimeSerie 
		TimeWindow operates in TimeSerie through:
			(W, x) & W' = (W & W', x|)
			where x| is defined by:
				x|_n = x_{n + max(b'-b, 0)}

		Notice that:
			* i_a(W) & W' = i_a(W & W')
			* p((W, x) & W') = W & W'
		"""
		W = self.TimeWindow & TimeWindow
		if not W.void:
			shift = W.begin - self.TimeWindow.begin
			ts = self[shift : len(W) + (W.begin - self.TimeWindow.begin)] # verificar isto
			return TimeSerie(ts, W)
		else:
			return TimeSerie.void()

	def __iand__(self, TimeWindow):
		return self & TimeWindow

	def drawdown(self):
		"""
		Calculates the drawdown of the list
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

	def ema(self, N = 7):
		""" Exponential Moving Average """
		# a = 1/N
		pass

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

	def variation(self, N = 1):
		""" Returns P_t - P_{t-N} """
		r = []
		for i in xrange(N, len(self)):
			r.append(self[i] - self[i-N])
		return TimeSerie(r, self.TimeWindow.rolling(N+1))

	def __add__(self, other):
		"""
		If 'other' is of numeric type, then
			(W, x) + a = (W, x + a)
			where x + a is defined by (x+a)_n = x_n + a
		If 'other' is another TimeSerie, then
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
				d_s = W.begin - self.TimeWindow.begin
				d_o = W.begin - other.TimeWindow.begin
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
				d_s = W.begin - self.TimeWindow.begin
				d_o = W.begin - other.TimeWindow.begin
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
				d_s = W.begin - self.TimeWindow.begin
				d_o = W.begin - other.TimeWindow.begin
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
				d_s = W.begin - self.TimeWindow.begin
				d_o = W.begin - other.TimeWindow.begin
				for i in xrange(len(W)):
					ts.append(self[d_s + i] / other[d_o + i])
				return TimeSerie(ts, W)

	def map(self, f):
		return TimeSerie(map(f, self), self.TimeWindow)

	def __abs__(self):
		return self.map(abs)

	def __pow__(self, a):
		""" Returns x^a if a is odd, otherwise returns |x|^a """
		if a%2 == 1:
			return self.map(lambda x: x**a)
		else:
			return self.map(lambda x: abs(x)**a)

	def log(self):
		from math import log
		return self.map(log)

	def exp(self):
		from math import exp
		return self.map(exp)

	def stdev(self, N):
		return self.var(N).sqrt()

	def sqrt(self):
		return self.map(lambda x: abs(x)**.5)

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


	def garch(self, N = 91): # subtrair o valor medio faz uma diferenca insignificante
		assert N > 1
		
		if len(self) < N:
			return TimeSerie.void()

		a = 1/float(N)

		garch = [sum([self[i]**2 for i in xrange(N)])/N]

		for i in xrange(N, len(self)):
			garch.append(a * self[i]**2 + (1-a) * garch[-1])

		return TimeSerie(garch, self.TimeWindow.rolling(N))


	@staticmethod
	def cov(N, X, Y): 
		""" Returns covariance for a moving window of size N """
		W = X.TimeWindow & Y.TimeWindow
		if len(W) < N:
			return TimeSerie.void()

		x = X & W
		y = Y & W

		s_x  = 0
		s_y  = 0
		s_xy = 0

		for i in xrange(N):
			s_x  += x[i]
			s_y  += y[i]
			s_xy += x[i]*y[i]

		cov = [(s_xy - s_x * s_y / N) / (N - 1)]
		for i in xrange(N, len(W)):
			s_x  += x[i] - x[i-N]
			s_y  += y[i] - y[i-N]
			s_xy += x[i]*y[i] - x[i-N]*y[i-N]
			cov.append((s_xy - s_x * s_y / N) / (N - 1))

		return TimeSerie(cov, W.rolling(N))

	@staticmethod
	def corr(N, X, Y): 
		""" Returns correlation for a moving window of size N """
		return TimeSerie.cov(N, X, Y) / ((X & Y.TimeWindow).stdev(N) * (Y & X.TimeWindow).stdev(N))

	@staticmethod
	def covGarch(N, X, Y):
		
		assert N > 1
		
		W = X.TimeWindow & Y.TimeWindow

		if len(W) < N:
			return TimeSerie.void()

		a = 1/float(N)

		x = X & W
		y = Y & W

		cov = [sum([x[i]*y[i] for i in xrange(N)]) / (N - 1)]

		for i in xrange(N, len(W)):
			cov.append(a * x[i] * y[i] + (1-a) * cov[-1])

		return TimeSerie(cov, W.rolling(N))

	@staticmethod
	def corrGarch(N, X, Y): 
		""" Returns correlation for a moving window of size N """
		return TimeSerie.covGarch(N, X, Y) / ((X & Y.TimeWindow).garch(N) * (Y & X.TimeWindow).garch(N)).sqrt()

	def SimpleLinearRegr(self, N, shift = 1):

		if len(self) < N:
			return TimeSerie.void()

		s_x  = N*(N-1)/2
		s_xx = N*(N-1)*(2*N-1)/6
		s_y  = 0
		s_xy = 0
		s_yy = 0

		for i in xrange(N):
			s_y  += self[i]
			s_xy += i * self[i]
			s_yy += self[i] * self[i]

		# N * s_xx - s_x ** 2 = N*N*(N*N-1)/12

		b0 = (s_y * s_xx - s_x * s_xy) / (N*N*(N*N-1)/12)
		b1 = (N * s_xy - s_x * s_y) / (N*N*(N*N-1)/12)
		B0 = [b0]
		B1 = [b1]
		r =  [(N * s_xy - s_x * s_y)/( (N*N*(N*N-1)/12) * (N * s_yy - s_y ** 2))**.5]

		y = [b0 + b1 * (N + shift - 1)]

		for t in xrange(N, len(self)):
			s_x  += N
			s_y  += self[t] - self[t-N]
			s_xx += t**2 - (t-N)**2
			s_xy += t * self[t] - (t-N) * self[t-N]
			s_yy += self[t] ** 2 - self[t-N] ** 2

			b0 = (s_y * s_xx - s_x * s_xy) / (N*N*(N*N-1)/12)
			b1 = (N * s_xy - s_x * s_y) / (N*N*(N*N-1)/12)

			B0.append(b0)
			B1.append(b1)

			r.append((N * s_xy - s_x * s_y)/( (N*N*(N*N-1)/12) * (N * s_yy - s_y ** 2))**.5)
			y.append(b0 + b1 * (t + shift))

		return TimeSerie(y, self.TimeWindow.rolling(N) + shift)

	def MultLinearRegr(self, N, *args, **kwargs): #falta verificar!!!

		n = len(args)
		W = self.TimeWindow
		for k in xrange(n):
			W &= args[k].TimeWindow

		if len(W) < N:
			return TimeSerie.void()

		Y = self & W
		X = []
		if 'constant' in kwargs.keys() and kwargs['constant'] is True:
			n += 1
			X.append(TimeSerie(1, W))

		X.extend([args[k] & W for k in xrange(len(args))])

		XTX = np.matrix(np.zeros((n,n)))
		XTY = np.zeros(n)

		for i in xrange(n):

			XTX[i,i] = sum([X[i][t] ** 2   for t in xrange(N)])
			XTY[i]   = sum([X[i][t] * Y[t] for t in xrange(N)])

			for j in xrange(i):
				s_ij = sum([X[i][t] * X[j][t] for t in xrange(N)])
				XTX[i,j] = s_ij
				XTX[j,i] = s_ij

		b_ = []
		x_ = []
		y_ = []
		x_.append(np.array([X[i][0] for i in xrange(n)]))
		b_.append(np.linalg.solve(XTX, XTY))
		y_.append(np.inner(b_[-1], x_[-1]))

		for t in xrange(N, len(W)):

			for i in xrange(n):
				XTX[i,i] += X[i][t]**2 - X[i][t-N]**2
				XTY[i]   += X[i][t] * Y[t] - X[i][t-N] * Y[t-N]

				for j in xrange(i):
					ds_ij = X[i][t] * X[j][t] - X[i][t-N] * X[j][t-N]
					XTX[i,j] += ds_ij
					XTX[j,i] += ds_ij

			x_.append(np.array([X[i][t] for i in xrange(n)]))
			b_.append(np.linalg.solve(XTX, XTY))
			y_.append(np.inner(b_[-1], x_[-1]))

		if 'coef' in kwargs.keys() and kwargs['coef'] is True:
			return TimeSerie(y_, W.rolling(N)), TimeSerie(b_, W.rolling(N))
		else:
			return TimeSerie(y_, W.rolling(N))

	def alpha_beta(self, N = 260, market_return = None, risk_free_return = None):
		import historical
		if market_return is None: market_return = historical.LogReturns('^GSPC')
		if risk_free_return is None: risk_free_return = historical.risk_free_return()
		self_excess = self - risk_free_return
		market_excess = market_return - risk_free_return
		b = self_excess.MultLinearRegr(N, market_excess, constant = True, coef = True)[1]
		W = b.TimeWindow
		alpha = []
		beta = []
		for i in xrange(len(b)):
			alpha.append(b[i][0])
			beta.append(b[i][1])
		return TimeSerie(alpha, W), TimeSerie(beta, W)

