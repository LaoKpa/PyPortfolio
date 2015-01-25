#!/usr/bin/env python
from datetime import *
from historical import *
from dateserie import *
from timewindow import *
from timeserie import *
import numpy as np

class state:
	""" This class describe an expected state """
	def __init__(self, symbol_list, r_f = 0.00008):
		self.symbol = symbol_list					# symbol array for each day (may change along the time)
		self.u = np.zeros(len(self))				# expected returns
		self.S = np.matrix(np.identity(len(self)))	# expected covariance matrix
		self.r_f = r_f								# risk free rate

	def __len__(self):
		return len(self.symbol)

	def setU(self, symbol, m):
		i = self.symbol.index(symbol)
		self.u[i] = m

	def setV(self, symbol, s):
		i = self.symbol.index(symbol)
		self.S[i,i] = s

	def setS(self, symbol_i, symbol_j, s):
		i = self.symbol.index(symbol_i)
		j = self.symbol.index(symbol_j)
		self.S[i,j] = s
		self.S[j,i] = s

	def index(self, symbol):
		return self.symbol.index(symbol)

	def PCA(self): #principal component analysis, return eigenvectors matrix
		pass

	def kelly(self, f = 1.0):
		b = np.linalg.solve(self.S, self.u - self.r_f) * f
		return { s : self.b[self.index(s)] for s in self.symbol }

	def markowitz(self):
		kelly = np.linalg.solve(self.S, self.u - self.r_f)
		kellyLeverage = sum(abs(kelly))
		b = kelly / kellyLeverage
		return { s : self.b[self.index(s)] for s in self.symbol }

def StateSerie(N, X):
	"""
	Returns a TimeSerie of states
	"""
	#assert len(X[k].TimeWindow) >= N para todo o k
	symbols = X.keys()

	beg = min([X[symbol].TimeWindow.begin for symbol in symbols])
	end = max([X[symbol].TimeWindow.end   for symbol in symbols])

	W = TimeWindow(beg, end).rolling(N)

	TSsymbols = [[] for t in xrange(len(W))]

	b = dict()
	e = dict()
	
	for symbol in symbols:
		b[symbol] = (X[symbol].TimeWindow.begin - beg).days
		e[symbol] = (X[symbol].TimeWindow.end - beg).days - N + 1 # is this ok?

	for symbol in symbols:
		for t in xrange(b[symbol], e[symbol]):
			TSsymbols[t].append(symbol)

	#initialize StateSerie
	StateSerie = TimeSerie([state(TSsymbols[t]) for t in xrange(len(W))], W)

	#compute values for i (u, var), and cov for ij, j<i
	for i in xrange(len(symbols)):
		symbol_i = symbols[i]
		b_i = b[symbol_i]
		e_i = e[symbol_i]
		u = X[symbol_i].sma(N) #we can use another estimators in future
		s = X[symbol_i].garch(N)
		# append u and s 
		for t in xrange(b_i, e_i + 1):
			StateSerie[t].setU(symbol_i, u[t - b_i])
			StateSerie[t].setV(symbol_i, s[t - b_i])

		for j in xrange(i):
			symbol_j = symbols[j]
			s = TimeSerie.covGarch(N, X[symbol_i], X[symbol_j])
			b_ij = max(b[symbol_i], b[symbol_j])
			e_ij = min(e[symbol_i], e[symbol_j])
			for t in xrange(b_ij, e_ij + 1):
				StateSerie[t].setS(symbol_i, symbol_j, s[t - b_ij])

	return StateSerie

"""
X = dict()
symbol_list = ['AAPL','MSFT','MCD','XOM']
for symbol in symbol_list:
	X[symbol] = LogReturns(symbol) & TimeWindow.years(2005,2013)

ss = StateSerie(365*3, X)
"""



"""
X = dict()

W = TimeWindow(date.today(), date.today()+timedelta(days=4))
X['A'] = TimeSerie([1,2,3,4,9],W+1)
X['B'] = TimeSerie([4,3,2,1,1],W)

ss = StateSerie(3, X)
print len(ss)
for i in xrange(len(ss)):
	print ss[i].S
"""


# _ * * * * *
# * * * * * _
#
# _ _ _ * * *
# _ _ * * *