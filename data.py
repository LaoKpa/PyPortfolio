#!/usr/bin/env python
from datetime import *
from dateserie import *

# create a new class that stores data from several stocks
# cut the date of begining to memory savings purposes (for instance, BeginDate = year(2000))

# import from another sources than yahoo finance
# import financial statements
#	* income statement
#	* balance sheet
#	* cash flow statement

# storage financial data in a sqlite database instead of files

class QuoteIO:

	folder = 'data/'
	ext =  '.txt'

	def __init__(self, symbol):
		self.symbol = symbol

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
			pass

	def __write(self):
		with open(self.__path(), 'w') as f:
			f.write('DATE\t\tOPEN\tHIGH\tLOW\tCLOSE\tADJ\tVOL\n')
			for l in self.data:
				strline = l[0]
				for i in xrange(1, 6):
					strline += '\t' + l[i];
				strline += '\n'
				f.write(strline)

	def __append(self):
		with open(self.__path(), 'a') as f:
			for l in self.data:
				strline = l[0]
				for i in xrange(1, 6):
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
	def loaded(symbol):
		quote = QuoteIO(symbol)
		quote.read()
		return quote

def LogPrice(symbol):
	from math import log
	return QuoteIO.loaded(symbol).DateSerie().map(log).TimeSerie()

def LogReturns(symbol):
	return LogPrice(symbol).variation()



