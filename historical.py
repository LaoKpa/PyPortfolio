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

		input_tuple = (self.symbol,
			str(since.month - 1), str(since.day), str(since.year),
			str(until.month - 1), str(until.day), str(until.year))

		self.data = dict()

		url_price = 'http://ichart.yahoo.com/table.csv?s=%s&g=d&a=%s&b=%s&c=%s&d=%s&e=%s&f=%s&ignore=.csv' % input_tuple
		url_div	=   'http://ichart.finance.yahoo.com/x?s=%s&g=v&a=%s&b=%s&c=%s&d=%s&e=%s&f=%s&ignore=.csv' % input_tuple

		try:
			price_data = urlopen(url_price)
			price_data.readline()
			for line in price_data:
				c = line.split(',')
				d = datetime.strptime(c[0],'%Y-%m-%d').date()
				row = [
					float(c[1]),		# Open
					float(c[2]),		# High
					float(c[3]),		# Low
					float(c[4]),		# Close
					float(c[-1][:-1]),	# Adj
					0,					# Div 		(to be edited latter)
					(1,1),				# Split		(to be edited latter)
					int(c[5])]			# Volume
				self.data[d] = row

			div_data = urlopen(url_div)
			div_data.readline()

			for line in div_data:
				c = line.split(',')
				if c[0] == 'DIVIDEND':
					d = date(int(c[1][1:5]), int(c[1][5:7]), int(c[1][7:9]))
					self.data[d][5] = float(c[2][:-1])
				elif c[0] == 'SPLIT':
					d = date(int(c[1][1:5]), int(c[1][5:7]), int(c[1][7:9]))
					split = c[2][:-1].split(':')
					self.data[d][6] = (int(split[0]), int(split[1]))

		except:
			print 'Error downloading ' + self.symbol

	def __write(self):
		with open(self.__path(), 'w') as f:
			column_width = 10
			f.write('Date      ')
			f.write('      Open')
			f.write('      High')
			f.write('       Low')
			f.write('     Close')
			f.write('       Adj')
			f.write('       Div')
			f.write('     Split')
			f.write('      Volume')
			f.write('\n')
			for d in sorted(self.data.iterkeys()):
				row = self.data[d]
				line = d.strftime('%Y-%m-%d')
				for i in xrange(5):
					line += '%*.2f' % (column_width, row[i])
				line += '%*s'     % (column_width, row[5])		# Dividend
				line += ('%d:%d'  % row[6]).rjust(column_width)	# Split
				line += '  %*d\n' % (column_width, row[7])		# Volume
				f.write(line)

	def __append(self):
		with open(self.__path(), 'a') as f:
			for d in sorted(self.data.iterkeys()):
				row = self.data[d]
				line = d.strftime('%Y-%m-%d')
				for i in xrange(5):
					line += '%*.2f' % (column_width, row[i])
				line += '%*s'     % (column_width, row[5])		# Dividend
				line += ('%d:%d'  % row[6]).rjust(column_width)	# Split
				line += '  %*d\n' % (column_width, row[7])		# Volume
				f.write(line)

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
			self.data = dict()
			for line in f:
				d = datetime.strptime(line[:10], '%Y-%m-%d').date()
				c = line[13:-1].split()
				row = []
				for i in xrange(6):
					row.append(float(c[i]))
				row.append(tuple(map(int, c[6].split(':'))))
				row.append(int(c[7]))
				self.data[d] = row
	
	def DateSerie(self, value = 'Adj'):
		"""
		Returns a DateSerie (dictionary) created from self.data,
		except when value = 'Date', when returns the list of dates
		Input (is converted to lowcase)
			'Date'          	- date
			'Open'          	- open
			'High'          	- high
			'Low'           	- low
			'Close'         	- close
			'Adj'	        	- adjusted close
			'Div', 'Dividend'	- dividends
			'Split'				- split ratio
			'Vol', 'Volume' 	- volume
			other values		- all
		"""
		value = value.lower()
		convert = {
			'open'		: 0,
			'high'		: 1,
			'low'		: 2,
			'close'		: 3,
			'adj'		: 4,
			'div'		: 5,
			'dividend'	: 5,
			'vol'		: 7,
			'volume'	: 7}

		if isinstance(value, str):
			value = value.lower()
			
			if value == 'all':
				pass

			elif value == 'date':
				return sorted(self.data.keys())

			elif value == 'split':
				h = DateSerie()
				i = 6
				for d in self.data.iterkeys():
					h[d] = float(self.data[d][6][0])/float(self.data[d][6][1])
				return h

			elif value in convert.keys():
				h = DateSerie()
				i = convert[value]
				for d in self.data.iterkeys():
					h[d] = float(self.data[d][i])
				return h	
		
		return self.data		

	def purge(self):
		from os import remove
		remove(self.__path())

	def clean_data(self, margin = .5):
		"""
		See if there are abdormal returns within data
		if there are, compare data with google finance data to acess veracity
		"""
		self.read()
		problem = False

		p = float(self.data[0][5])
		for i in xrange(1, len(self.data)):
			p_a = p
			p = float(self.data[i][5])
			if abs(p - p_a) >= margin * p_a:
				d = self.data[i][0]
				print 'Abdormal return found for %s on %s, with a ratio of %f' % (self.symbol, d, p/p_a)
				print self.data[i-1]
				print self.data[i]
				print ''
				problem = True
				# url = "http://www.google.com/finance/historical?q=%s&startdate=%s&enddate=%s&output=csv" % (
				#	self.symbol,
				#	self.data[i-1][0].strftime('%b+%d,+%Y'),
				#	self.data[i][0].strftime('%b+%d,+%Y'))

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
		Applies the 'action' to the list of symbols in file
		Options:
			* price
			* read/load
			* download
			* update
			* clean/clean_data
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

# q = Historical('XOM')
# q.read()
# print q.data[date(2015,1,20)]

p = LogPrice('XOM')
print p[-1]