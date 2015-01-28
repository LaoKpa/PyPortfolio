#!/usr/bin/env python
from workingday import *

class TimeWindow:

	def __init__(self, begin, end):
		"""
		Creates a new TimeWindow begining at 'begin' and ending at 'end'
		if begin is after end then TimeWindow will be declared as void

		The set of TimeWindows is in bijection with {(a,b)\in \Z^2 | a <= b} \cup {*}
		where * is the void TimeWindow and the integers a, b came from a given bijection
		between date and the set of integers \Z
		"""
		if begin > end:
			self.void = True
		
		else:
			self.begin = begin
			self.end = end
			self.void = False

	def __and__(self, other):
		"""
		Returns the intersection of two TimeWindows W & W'
		This operation satisfies:
			W & W = W 			(idempotent)
			W & W' = W' & W 	(commutative)
			W & * = * 			(absorbing element)
		"""
		if self.void or other.void:
			return TimeWindow.void()

		elif self.begin > other.end or other.begin > self.end:
			return TimeWindow.void()

		else:
			return TimeWindow(
				max(self.begin, other.begin),
				min(self.end,   other.end))

	def __contains__(self, other): 
		"""
		Returns True or False
		'c' establishes an order within the TimeWindows
		in particular:
			* c W, for all W
			W & W' c W for all W, W'
			W + n ~c W for all W, n\in\Z, except when W = *
		"""
		if self.void:
			return False

		if isinstance(other, TimeWindow):
			if other.void:
				return True
			elif other.begin >= self.begin and other.end <= self.end:
				return True

		elif isinstance(other, (workingday, date)):
			if other >= self.begin and other <= self.end:
				return True
		
		return False

	def __len__(self):
		"""
		Returns the lenght of the TimeWindow
		Satisfies:
			* len(W) >= 0
				equality occurs if and only if W = *
				otherwise (that is, if W != *) len(W) > 0
			* len(W + n) = len(W)
			* len(W & W') <= min(len(W), len(W'))
				equality occurs if and only if W = W'
				otherwise (that is, if W != W') len(W & W') < min(len(W), len(W'))
		"""
		if self.void:
			return 0
		else:
			return (self.end - self.begin) + 1

	def shift(self, N):
		"""
		This operatior moves the TimeWindow n days forward
		if n is negative it moves TimeWindow -n bays backwards
		"""
		if self.void:
			return self
		else:
			return TimeWindow(self.begin + N, self.end + N)

	def __add__(self, N):
		return self.shift(N)

	def __sub__(self, N):
		return self.shift(-N)

	def extend(self, N = 1):
		return TimeWindow(self.begin, self.end + N)

	def extendleft(self, N = 1):
		return TimeWindow(self.begin - N, self.end)

	def rolling(self, N):
		""" This operatior is equivalent to W & (W+N-1) """
		return (self & self.shift(N-1))

	def __str__(self):
		return self.begin.strftime('%d/%m/%Y') + ' - ' + self.end.strftime('%d/%m/%Y')

	@staticmethod
	def void():
		return TimeWindow(1,0)

	@staticmethod
	def year(year):
		begin = workingday.first(year,1)
		end = workingday.last(year,12)
		return TimeWindow(begin, end)

	@staticmethod
	def month(month, year):
		begin = workingday.first(year, month, 1)
		end = workingday.last(year, month, 1)
		return TimeWindow(begin, end)

	@staticmethod
	def years(year1, year2):
		assert not year1 > year2
		begin = workingday.first(year1,1)
		end = workingday.last(year2,12)
		return TimeWindow(begin, end)