from datetime import *
from data import *
from timeserie import *

import matplotlib.pyplot as plt
class plot:
	def __init__(self, TimeWindow):
		self.W = TimeWindow
		self.xlabel = 'Date'
		self.ylabel = 'Price'

	def title(self, title):
		plt.title(title)

	def draw(self, TimeSerie, **kwargs): # append name and legend
		ts = TimeSerie & self.W
		plt.plot(sorted(ts.DateSerie().keys()) , ts[:], **kwargs)

	def show(self):
		plt.xlabel(self.xlabel)
		plt.ylabel(self.ylabel)
		plt.grid(True)
		plt.show()

symbol = 'GOOGL'
W = TimeWindow.years(2005,2014)
P = LogPrice(symbol)

x = plot(W)
x.title(symbol + "   " + str(W))
#x.draw(r.var(30))
x.draw(P)
x.draw(P.sma(90), linewidth = 2)
x.show()