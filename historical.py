#!/usr/bin/env python
from workingday import workingday
from dateserie import DateSerie
from urllib import urlopen

class Historical:

	def __init__(self, symbol):
		self.symbol = symbol
		self.folder = 'Historical/'
		self.ext =  '.txt'

	def __path(self):
		return self.folder + self.symbol + self.ext

	def __path_dividends(self):
		return self.folder + 'Dividends/' + self.symbol + self.ext

	def __download(self, since = workingday(1900,1,1)):
		"""
		Downloads data from yahoo finance from date begin until today
		(other sources than yahoo finance may be considered in future)
		"""
		until = workingday.today()

		input_tuple = (self.symbol,
			str(since.month - 1), str(since.day), str(since.year),
			str(until.month - 1), str(until.day), str(until.year))

		self.price    = dict()
		self.dividend = dict()
		self.split    = dict()

		try:
			url = 'http://ichart.yahoo.com/table.csv?s=%s&g=d&a=%s&b=%s&c=%s&d=%s&e=%s&f=%s&ignore=.csv' % input_tuple
			raw_data = urlopen(url)
			raw_data.readline()

			for line in raw_data:
				l = line.split(',')
				d = workingday.strptime(l[0],'%Y-%m-%d')
				row = [
					float(l[1]),       # Open
					float(l[2]),       # High
					float(l[3]),       # Low
					float(l[4]),       # Close
					float(l[-1][:-1]), # Adj
					int(l[5])]         # Volume
				self.price[d] = row

			# get dividend and split data
			url	= 'http://ichart.finance.yahoo.com/x?s=%s&g=v&a=%s&b=%s&c=%s&d=%s&e=%s&f=%s&ignore=.csv' % input_tuple
			raw_data = urlopen(url)
			raw_data.readline()

			for line in raw_data:
				l = line.split(',')
				if l[0] == 'DIVIDEND':
					d = workingday(int(l[1][1:5]), int(l[1][5:7]), int(l[1][7:9]))
					self.dividend[d] = float(l[2][:-1])
				elif l[0] == 'SPLIT':
					d = workingday(int(l[1][1:5]), int(l[1][5:7]), int(l[1][7:9]))
					self.split[d] = tuple(map(int, l[2][:-1].split(':')))

		except:
			print 'Error downloading ' + self.symbol

	def __write(self, mode = 'w'):

		with open(self.__path(), mode) as f:

			column_width = 10

			if mode in ['w', 'w+']:
				f.write('Date      ')
				f.write('      Open')
				f.write('      High')
				f.write('       Low')
				f.write('     Close')
				f.write('       Adj')
				f.write('      Volume')
				f.write('\n')

			for d in sorted(self.price.iterkeys()):
				row = self.price[d]
				line = d.strftime('%Y-%m-%d')
				for i in xrange(5):
					line += '%*.2f' % (column_width, row[i])
				line += '%*d\n' % (12, row[5]) # Volume
				f.write(line)

		with open(self.__path_dividends(), mode) as f:

			column_width = 10

			if mode in ['w', 'w+']:
				f.write('Date\n')

			date = []
			date.extend(self.dividend.keys())
			date.extend(self.split.keys())

			for d in sorted(date):
				if d in self.dividend.keys():
					line = d.strftime('%Y-%m-%d')
					line += '  Dividend'
					line += '%*s' % (column_width, self.dividend[d])
					line += '\n'
				if d in self.split.keys():
					line = d.strftime('%Y-%m-%d')
					line += '     Split'
					line += ('%d:%d'  % self.split[d]).rjust(column_width)
					line += '\n'
				f.write(line)

	def update(self, purge = True):
		""" Download data from the server and update information at the database file """ # need to complete
		if purge:
			self.__download()
			self.__write()
		else:
			pass

	def read(self):
		""" Read data from the files (and write them at self.price, dividend, split) """
		with open(self.__path(), 'r') as f:
			f.readline()
			self.price = dict()
			for line in f:
				d = workingday.strptime(line[:10], '%Y-%m-%d')
				c = line[13:-1].split()
				row = []
				for i in xrange(5):
					row.append(float(c[i]))
				row.append(int(c[5]))
				self.price[d] = row

		self.dividend = dict()
		self.split = dict()
		try:
			with open(self.__path_dividends(), 'r') as f:
				f.readline()
				for line in f:
					d = workingday.strptime(line[:10], '%Y-%m-%d')
					c = line[10:-1].split()
					if c[0] == 'Dividend':
						self.dividend[d] = float(c[1])
					elif c[0] == 'Split':
						self.split[d] = tuple(map(int, c[1].split(':')))
		except:
			pass

	
	def DateSerie(self, value = 'Adj'):
		"""
		Returns a DateSerie (dictionary) created from self.data,
		except when value = 'Date', when returns the list of dates
		Input (is converted to lowcase)
			'Open'            - open
			'High'            - high
			'Low'             - low
			'Close'           - close
			'Adj'             - adjusted close
			'Vol', 'Volume'   - volume
			'Split'           - split ratio
			'Returns'         - adjusted returns (own calculation)	# to be done
		"""

		if isinstance(value, str):
			value = value.lower()

			convert = {
				'open'     : 0,
				'high'     : 1,
				'low'      : 2,
				'close'    : 3,
				'adj'      : 4,
				'vol'      : 5,
				'volume'   : 5}

			if value in convert.keys():
				h = DateSerie()
				i = convert[value]
				for d in self.price.iterkeys():
					h[d] = float(self.price[d][i])
				return h

			elif value == 'split':
				h = DateSerie()
				for d, s in self.split.iteritems():
					h[d] = float(s[1])/float(s[0])
				return h

			elif value in ['returns']:
				tax_rate = .25
				pass

	def purge(self):
		from os import remove
		remove(self.__path())

	def clean(self, margin = .95):
		"""
		See if there are abdormal returns within data
		if there are, compare data with google finance data to acess veracity
		"""

		self.read()
		problem = False
		date = sorted(self.price.keys())
		p = self.price[date[0]][4]

		for i in xrange(1, len(date)):

			d = date[i]
			p_a = p
			p = self.price[d][4]

			if p == 0 or p_a == 0:
				problem_date = d
				problem = True
				if p == 0:
					print 'Price equal to zero on %s' % d

			elif p/p_a - 1 >= margin or p_a/p >= 1 + margin:
				problem_date = d
				problem = True
				d_a = date[i-1]
				print 'Abdormal return found for %s on %s, with a ratio of %f' % (self.symbol, d, p/p_a)
				print self.price[d_a]
				print self.price[d]
				if d in self.dividend.keys():
					print 'Dividend:   %s' % self.dividend[d]
				if d in self.split.keys():
					print 'Split:   %d:%d' % self.split[d]
				print '  Data from google-finance to compare:'

				url = "http://www.google.com/finance/historical?q=%s&startdate=%s&enddate=%s&output=csv" % (
					self.symbol,
					d_a.strftime('%b+%d,+%Y'),
					d.strftime('%b+%d,+%Y'))
				google_data = urlopen(url)
				line = google_data.readlines()
				for i in xrange(len(line)-1, 0, -1):
					print line[i],
				print ''

		if problem:
			answer = raw_input('Append to the log file? (y/n)   ')
			#answer = raw_input('Do you want to (re)update data? (y/n)')
			if answer.lower() == 'y':
				with open('log.txt','a') as f:
					f.write("%s %s\n" % (self.symbol, problem_date.strftime('%Y-%m-%d')))
				#self.update()
				#print '...'
				#print 'Completed update'
				#answer = raw_input('Do you want to re-check data? (y/n)')
				#if answer.lower() == 'y':
				#	self.clean_data(margin)
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
		 * clean
		"""
		action = action.lower()
		quote = dict()
		with open(file, 'r') as f:
			for line in f:
				symbol = line[:-1]
				quote[symbol] = Historical(symbol)

		if action in ['price']:
			price = dict()
			for symbol, q in quote.iteritems():
				q.read()
				price[symbol] = q.DateSerie().TimeSerie()
			return price
		if action in ['log-price']:
			from math import log
			price = dict()
			for symbol, q in quote.iteritems():
				q.read()
				price[symbol] = q.DateSerie().map(log).TimeSerie()
			return price
		elif action in ['read', 'load']:
			for symbol in sorted(quote.iterkeys()):
				quote[symbol].read()
				print symbol
			return quote
		elif action in ['download']:
			for symbol in sorted(quote.iterkeys()):
				quote[symbol].__download()
			return quote
		elif action in ['update']:
			for symbol in sorted(quote.iterkeys()):
				quote[symbol].update()
		elif action in ['clean']:
			for symbol in sorted(quote.iterkeys()):
				quote[symbol].clean()

def LogPrice(symbol):
	from math import log
	return Historical.load(symbol).DateSerie().map(log).TimeSerie()

def LogReturns(symbol):
	return LogPrice(symbol).variation()

def risk_free_return():
	file_name = 'FED/yields_10Y.csv'
	with open(file_name, 'r') as f:
		for i in xrange(7): f.readline()
		h = DateSerie()
		rate = 0
		for line in f:
			c = line[:-1].split(',')
			try:
				h[workingday.strptime(c[0], '%Y-%m-%d')] = float(c[1])*0.01
			except:
				pass
	return h.TimeSerie()