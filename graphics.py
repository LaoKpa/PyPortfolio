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