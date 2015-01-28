from timeserie import TimeSerie
from timewindow import TimeWindow
from workingday import workingday
import historical

class performance:
	def __init__(self, P):
		self.R_f = historical.risk_free_return()
		self.R_m = historical.LogReturns('^GSPC')
		self.P = P
		self.R = P.variation()
		self.first_year = max(2005, self.R.TimeWindow.begin.year)
		self.__sharpe_ratio()
		self.__alpha_beta()

	def __sharpe_ratio(self):
		self.mean = []
		self.stdev = []
		self.sharpe = []
		for year in xrange(self.first_year, 2015):
			W = TimeWindow(workingday.first(year, 1), workingday.first(year + 1, 1))
			P = self.P & W
			R = self.R & W
			self.mean.append((P[-1] - P[0])*100)
			self.stdev.append(R.stdev(len(W))[0]*100)
			r_f = (self.R_f & W).sma(len(W))[0]
			self.sharpe.append((self.mean[-1] - r_f)/self.stdev[-1])

	def __alpha_beta(self):
		self.alpha = []
		self.beta = []
		for year in xrange(self.first_year, 2015):
			W = TimeWindow(workingday.first(year, 1), workingday.first(year + 1, 1))
			R = self.R & W
			alpha, beta = R.alpha_beta(N = len(W))
			self.alpha.append(alpha[0]*260)
			self.beta.append(beta[0])

	def __str__(self):
		string = 'YEAR    MEAN   STDEV   SHARPE   ALPHA    BETA\n'
		for i in xrange(2015 - self.first_year):
			string += str(self.first_year + i)
			string += '%*.2f' % (8, self.mean[i])
			string += '%*.2f' % (8, self.stdev[i])
			string += '%*.2f' % (8, self.sharpe[i])
			string += '%*.2f' % (8, self.alpha[i])
			string += '%*.2f' % (8, self.beta[i])
			string += '\n'
		string 
		return string
		