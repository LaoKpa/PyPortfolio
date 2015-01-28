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

		plt.plot(ts.keys() , ts[:], **kwargs)

	def scatter(self, x, y, **kwargs): # append name and legend
		plt.plot(x, y, **kwargs)

	def show(self):
		plt.xlabel(self.xlabel)
		plt.ylabel(self.ylabel)
		plt.grid(True)
		plt.show()