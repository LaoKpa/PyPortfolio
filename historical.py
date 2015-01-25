#!/usr/bin/env python
from datetime import *
from dateserie import *
from urllib import urlopen

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
	
	def DateSerie(self, value = 'Adj'):
		"""
		Returns a DateSerie (dictionary) created from self.data,
		except when value = 'Date', when returns the list of dates
		Input (is converted to lowcase)
			'Date'          - date
			'Open'          - open
			'High'          - high
			'Low'           - low
			'Close'         - close
			'Adj'	        - adjusted close
			'Vol', 'Volume' - volume
			other values	- all
		"""
		value = value.lower()
		map = {
			'open'	: 1,
			'high'	: 2,
			'low'	: 3,
			'close'	: 4,
			'adj'	: 5,
			'vol'	: 6,
			'volume':6,
			}

		if value == 'date':
			return [datetime.strptime(line[0], '%Y-%m-%d').date() for line in self.data]

		elif value in map.keys():
			h = DateSerie()
			i = map[value]
			for line in self.data:
				d = datetime.strptime(line[0], '%Y-%m-%d').date()
				h[d] = float(line[i])
			return h

		else:
			h = DateSerie()
			for line in self.data:
				d = datetime.strptime(line[0], '%Y-%m-%d').date()
				h[d] = [float(line[i]) for i in xrange(1, 7)]
			return h			

	def purge(self):
		from os import remove
		remove(self.__path())

	def clean_data(self, margin = .5):
		self.read()
		problem = False

		p = float(self.data[0][5])
		for i in xrange(1, len(self.data)):
			p_a = p
			p = float(self.data[i][5])
			if abs(p - p_a) >= margin * p_a:
				print 'Abdormal return found for %s on %s, with a ratio of %f' % (self.symbol, self.data[i][0], p/p_a)
				print self.data[i-1]
				print self.data[i]
				print ''
				problem = True

		if problem:
			answer = raw_input('Do you want to (re)update data? (y/n)')
			if answer.lower() == 'y':
				self.update()
				print '...'
				print 'Completed update'
				answer = raw_input('Do you want to re-check data? (y/n)')
				if answer.lower() == 'y':
					self.clean_data(margin)
		else:
			print 'Data from %s is clean' % self.symbol

	@staticmethod
	def load(symbol):
		quote = Historical(symbol)
		quote.read()
		return quote

	@staticmethod
	def list(file, action = 'Read'):
		"""
		action:
			price
			read/load
			download
			update
			clean/clean_data
		"""
		action = action.lower()
		quote = dict()
		with open(file, 'r') as f:
			for line in f: #atention if there is a header
				symbol = line[:-1] #atention if there is another columns
				quote[symbol] = Historical(symbol)

		if action in ['price']:
			price = dict()
			for symbol, q in quote.iteritems():
				q.read()
				price[symbol] = q.DateSerie().TimeSerie()
			return price
		elif action in ['read', 'load']:
			for symbol in quote.iterkeys():
				quote[symbol].read()
			return quote
		elif action in ['download']:
			for symbol in quote.iterkeys():
				quote[symbol].__download()
			return quote
		elif action in ['update']:
			for symbol in quote.iterkeys():
				quote[symbol].__update()
		elif action in ['clean', 'clean_data']:
			for symbol in quote.iterkeys():
				quote[symbol].clean_data()

def LogPrice(symbol):
	from math import log
	return Historical.load(symbol).DateSerie().map(log).TimeSerie()

def LogReturns(symbol):
	return LogPrice(symbol).variation()

q = Historical.list('sp400.txt','read')