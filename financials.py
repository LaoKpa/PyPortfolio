from datetime import *
from urllib import urlopen
from bs4 import BeautifulSoup as parser
from dateserie import DateSerie

# Per Share Data
"""
Revenue per Share ($)
EBITDA per Share ($)
EBIT per Share ($)
Earnings per Share (diluted) ($)
eps without NRI ($)
Dividends Per Share
Book Value Per Share ($)
Tangible Book per share ($)
Month End Stock Price ($)
"""

# Ratios
"""
Return on Equity %
Return on Assets %
Return on Invested Capital %
Return on Capital  - Joel Greenblatt %
Debt to Equity
Gross Margin %
Operating Margin %
Net Margin %
Total Equity to Total Asset
LT Debt to Total Asset
Asset Turnover
Dividend Payout Ratio
"""

# Income Statement
"""
Revenue
Cost of Goods Sold
Gross Profit
Gross Margin %
Operating Income
Operating Margin %
Interest Expense
Other Income (Minority Interest)
Pre-Tax Income
Tax Provision
Tax Rate %
Net Income (Continuing Operations)
Net Income (Discontinued Operations)
Net Income
Net Margin %
Preferred dividends
EPS (Basic)
EPS (Diluted)
Shares Outstanding (Diluted)
Depreciation, Depletion and Amortization
EBITDA
"""

# Balance Sheet
"""
Accounts Receivable
Property, Plant and Equipment
Intangible Assets
Total Assets
Current Portion of Long-Term Debt
Long-Term Debt
Debt to Equity
Total Liabilities
Common Stock
Preferred Stock
Retained Earnings
Accumulated other comprehensive income (loss)
Additional Paid-In Capital
Treasury Stock
Total Equity
Total Equity to Total Asset
"""

# Cashflow Statement
"""
Net Income
Cumulative Effect Of Accounting Change
Net Foreign Currency Exchange Gain
Net Income From Continuing Operations
Depreciation, Depletion and Amortization
Change In Receivables
Change In Inventory
Change In Prepaid Assets
Change In Payables And Accrued Expense
Change In Working Capital
Change In DeferredTax
Stock Based Compensation
Cash Flow from Discontinued Operations
Cash Flow from Others
Cash Flow from Operations						#OpFCF
Purchase Of Property, Plant, Equipment
Sale Of Property, Plant, Equipment
Purchase Of Business
Sale Of Business
Purchase Of Investment
Sale Of Investment
Net Intangibles Purchase And Sale
Cash From Discontinued Investing Activities
Cash Flow from Investing
Issuance of Stock
Repurchase of Stock
Net Issuance of Preferred Stock
Net Issuance of Debt
Cash Flow for Dividends
Other Financing
Cash Flow from Financing
Net Change in Cash
Capital Expenditure
Free Cash Flow								doest appear always (why?) - if not, compute
"""


class FinancialData:
	def __init__(self, symbol):
		self.symbol = symbol
		self.folder = 'Financials/'
		self.ext = '.txt'
		self.header = [] #date
		self.table = []
		self.rows = dict()
		self.data = dict()

	def __path(self):
		return self.folder + self.symbol + self.ext

	@staticmethod
	def __strToDate(str):
		d = datetime.strptime(str,'%b%y')
		m, y = d.month, d.year
		a, m = divmod(m, 12)
		return date(y+a, m+1, 1) - timedelta(days = 1)

	@staticmethod
	def __intToStr(i):
		if i == int(i):
			return str(int(i))
		else:
			return str(i)

	def __download(self):
		url = 'http://www.gurufocus.com/financials/' + self.symbol
		html = parser(urlopen(url).read()).find('table', id="Rf")

		strDate = [th['title'].encode('UTF-8') for th in html('th') if 'class' in th.attrs and 'style4' in th['class']][:-1]
		self.header = map(self.__strToDate, strDate)

		table_count = 0
		col_count = len(self.header)
		columns = len(self.header)

		for td in html('td'):

			if 'call2' in td['class']:
				if table_count > 4: break
				table_count += 1
				table = td.contents[0].encode('UTF-8')
				self.table.append(table)
				self.rows[table] = []

			elif 'title' in td.attrs:
				classAttr = td['class'][0]
				if classAttr in ['th_normal', 'incent', 'tk', '']:
					col_count = 0
					k = td['title'].replace(u'\xa0','').encode('utf8')
					if k != 'Fiscal Period':
						self.rows[table].append(k)
						self.data[k] = []
				elif classAttr in ['style4'] and  col_count < columns and k != 'Fiscal Period':
					self.data[k].append(float(td['title'].encode('UTF-8').replace(',', '')))
					col_count += 1

		# If Gross Profit(GM) is not defined we suppose that COGS = 0
		# and then Gross Profit (GP) = Operating Income
		# in that case we also set Gross Margin % = 100 %
		# because usually when GP is not available GP is set to zero what is not true

		if 'Gross Profit' not in self.rows['Income Statement']:

			i0 = self.rows['Income Statement'].index('Revenue') + 1

			self.rows['Income Statement'].insert(i0, 'Gross Margin %')
			self.rows['Income Statement'].insert(i0, 'Gross Profit')
			self.rows['Income Statement'].insert(i0, 'Cost of Goods Sold')

			self.data['Cost of Goods Sold'] = [0] * columns
			self.data['Gross Profit'] = self.data['Revenue']
			self.data['Gross Margin %'] = [100.0] * columns

		# remove rows that hasn't values
		for table in self.table:
			for row in self.rows[table]:
				if len(self.data[row]) < columns:
					del self.data[row]
					self.rows[table].remove(row)


	def __write(self):
		with open(self.__path(),'w') as f:
			f.write(str(self))

	def __str__(self):
		s = ' ' * 50
		column_width = 10
		for date in self.header:
			s += '%*s' % (column_width, date.strftime('%b%y'))
		s += '\n'
		for table in self.table:
			s += '# ' + table + '\n'
			rows = self.rows[table]
			for k in rows:
				s += '%*s' % (50, k)
				for item in self.data[k]:
					s += '%*s' % (column_width, self.__intToStr(item))
				s += '\n'
			s += '\n'
		return s

	def has(self, row):
		"""
		Checks if FinancialData has a given rubric
		"""
		for table in self.tables:
			if row in self.rows[table]:
				return True
		return False

	def update(self):
		self.__download()
		self.__write()

	def read(self):
		with open(self.__path(),'r') as f:
			
			# First row for dates
			self.header = map(self.__strToDate, f.readline()[:-1].split())

			table_name_line = True

			for line in f:

				if table_name_line:
					table = line[2:-1]
					self.table.append(table)
					self.rows[table] = []
					table_name_line = False

				elif line == '\n':
					table_name_line = True

				else:
					row = line[:50].strip()
					self.rows[table].append(row)
					self.data[row] = map(float, line[51:].split())

	def DateSerie(self, rows):
		"""
		Returns a DateSerie (dictionary) created from self.data
		rows = List
		"""
		emptyList = [0] * len(self.header)

		if len(rows) == 0:
			return None

		elif len(rows) == 1:
			h = DateSerie()
			k = rows[0]
			for i in xrange(len(self.header)):
				d = self.header[i]
				h[d] = self.data.get(k, emptyList)[i]
			return h

		elif len(rows) > 1:
			h = DateSerie()
			for i in xrange(len(self.header)):
				d = self.header[i]
				h[d] = [self.data.get(k, emptyList)[i] for k in rows]
			return h

	def ratio(self, num, den):
		h = DateSerie()
		for i in xrange(len(self.header)):
			d = self.header[i]
			h[d] = self.data[num][i]/self.data[den][i]
		return h

	def __net(self, add, sub = []):
		h = DateSerie()
		emptyList = [0] * len(self.header)
		for i in xrange(len(self.header)):
			d = self.header[i]
			h[d] = sum([self.data.get(k, emptyList)[i] for k in add]) - sum([self.data.get(k, emptyList)[i] for k in sub])
		return h

	def Debt(self):
		return self.__net(['Current Portion of Long-Term Debt','Long-Term Debt'])

	def FCFE(self):
		"""
		FCFE (Free Cashflow to Equity) =
			+ Net Income
			+ Depreciation, Depletion and Amortization
			- Change In Working Capital
			+ Net Issuance of Debt
		"""
		return self.__net(['Net Income','Depreciation, Depletion and Amortization','Net Issuance of Debt'],['Change In Working Capital'])

	def EnterpriseValue(self):
		"""
		EnterpriseValue =
			+ MktCap
			+ Preferred Stock
			+ Debt (Current Portion of Long-Term Debt + Long-Term Debt)
			- Cash, Cash Equivalents, Marketable Securities (*)
		* if exists
		"""
		h = DateSerie()
		for i in xrange(len(self.header)):
			d = self.header[i]
			h[d] = 0
			h[d] += self.data['Shares Outstanding (Diluted)'][i] * self.data['Month End Stock Price ($)'][i]	# MktCap
			h[d] += self.data['Preferred Stock'][i]																# Preferred Stock
			h[d] += self.data['Current Portion of Long-Term Debt'][i] + self.data['Long-Term Debt'][i]			# Debt
			if 'Cash, Cash Equivalents, Marketable Securities' in self.rows:
				h[d] -= self.data['Cash, Cash Equivalents, Marketable Securities'][i]							# Cash
		return h

	def Shares(self):
		return self.DateSerie(['Shares Outstanding (Diluted)'])

	def MktCap(self):
		"""
		Market Capitalization =
			Shares Outstanding * Stock Price
		"""
		h = DateSerie()
		for i in xrange(len(self.header)):
			d = self.header[i]
			h[d] = self.data['Shares Outstanding (Diluted)'][i] * self.data['Month End Stock Price ($)'][i]
		return h		

	def IncomeDropdown(self):
		"""
		Revenue				#Sales
		Gross Profit		#GP
		EBITDA				#EBITDA
		Operating Income	#OI
		Pre-Tax Income		#EBT
		Net Income 			#NI
		"""
		return self.DateSerie(['Revenue', 'Gross Profit', 'EBITDA', 'Operating Income', 'Pre-Tax Income', 'Net Income'])

	def purge(self):
		from os import remove
		remove(self.__path())

	@staticmethod
	def load(symbol):
		fs = FinancialData(symbol)
		fs.read()
		return fs


with open('sp500.txt','r') as f:
	for line in f:
		symbol = line[:-1]
		print symbol
		f = FinancialData(symbol)
		f.update()
