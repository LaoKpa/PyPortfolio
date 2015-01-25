#!/usr/bin/env python
from datetime import *
from dateserie import *

class Historical:

	def __init__(self, symbol):
		self.symbol = symbol
		self.folder = 'Historical/'
		self.ext =  '.txt'

	def __path(self):
		return self.folder + self.symbol + self.ext

	def __download(self, since = date(1900,1,1)):
		"""
		Downloads data from yahoo finance from date begin until today
		(other sources than yahoo finance may be considered in future)
		"""
		from urllib import urlopen
		until = date.today()

		url = 'http://ichart.yahoo.com/table.csv?s=%s&d=%s&e=%s&f=%s&g=d&a=%s&b=%s&c=%s&ignore=.csv' % (self.symbol,
				str(until.month - 1), str(until.day), str(until.year),
				str(since.month - 1), str(since.day), str(since.year))

		strdata = urlopen(url)
		strdata.readline()
		self.data = []

		try:
			for line in strdata:
				c = line.split(',')
				c[5], c[-1] = c[-1][:-1], c[5]
				self.data.append(c)
			self.data.reverse()
		except:
			print 'Error downloading ' + self.symbol

	def __write(self):
		with open(self.__path(), 'w') as f:
			f.write('DATE\t\tOPEN\tHIGH\tLOW\tCLOSE\tADJ\tVOL\n')
			for l in self.data:
				strline = l[0]
				for i in xrange(1, 7):
					strline += '\t' + l[i];
				strline += '\n'
				f.write(strline)

	def __append(self):
		with open(self.__path(), 'a') as f:
			for l in self.data:
				strline = l[0]
				for i in xrange(1, 7):
					strline += '\t' + l[i];
				strline += '\n'
				f.write(strline)

	def update(self):
		""" Download data from the server and update information at the database file """
		with open(self.__path(), 'w+') as f:
			try:
				last_line = f.readlines()[-1]
				since  = datetime.strptime(line[0], '%Y-%m-%d').date() + timedelta(days = 1)
				create = False
			except:
				create = True

			if create:
				self.__download()
				self.__write()
			else:
				self.__download(since)
				self.__append()

	def read(self):
		""" Read data from the file (and write them at self.data) """
		with open(self.__path(), 'r') as f:
			f.readline()
			self.data = []
			for line in f:
				newLine = line.split('\t')
				newLine[-1] = newLine[-1][:-1]
				self.data.append(newLine)
	
	def DateSerie(self, i = 5):
		"""
		Returns a DateSerie (dictionary) created from self.data,
		except when i = 0, when returns the list of dates
		Input:
			0 - date
			1 - open
			2 - high
			3 - low
			4 - close
			5 - adjusted close
			6 - volume
		"""
		if i == 0:
			return [datetime.strptime(line[0], '%Y-%m-%d').date() for line in self.data]
		else:
			h = DateSerie()
			for line in self.data:
				d = datetime.strptime(line[0], '%Y-%m-%d').date()
				h[d] = float(line[i])
			return h

	def purge(self):
		from os import remove
		remove(self.__path())

	@staticmethod
	def load(symbol):
		quote = Historical(symbol)
		quote.read()
		return quote

def LogPrice(symbol):
	from math import log
	return Historical.load(symbol).DateSerie().map(log).TimeSerie()

def LogReturns(symbol):
	return LogPrice(symbol).variation()

"""
with open('sp400.txt','r') as f:
	for line in f:
		symbol = line[:-1]
		print symbol
		f = Historical(symbol)
		f.update()
"""