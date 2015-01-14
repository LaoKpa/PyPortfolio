#!/usr/bin/env python
from datetime import *
from timewindow import *
from timeserie import *
import numpy as np

# Exclude weekends from TimeWindow and TimeSerie
# Review the following methods:
# TimeWindow
#	* len
#	* shift
# DateSerie
#	* TimeSerie
# TimeSerieommits/master
#	* DateSerie
#	* Integral
#	* and
# 	* + - * /
# Note: instead of timedelta(days = n) another function should be used compare and shift dates
# if n%5 == 0 then d.shift(n) := d + timedelta(days = 7*(n/5)), that is, if we shift d five working days
# this is the same as add 7 days. The formula cames from induction
# so d.shift(5*a + b) = (d + timedelta(days = 7*a)).shift(b)
# let weekday(d) = 0,1,2,3,4
# for a given date d, we can set b such than 0 <= (weekday(d) + b) < 5
# that is a = floor((weekday(d) + n)/5) and b is the remainder
# so d.shift(n) = (d + timedelta(days = 7*floor((weekday(d) + n)/5))).shift(n - 5 * floor((weekday(d) + n)/5))
# where shift only need to be defined within a week

class DateSerie(dict):
	
	def TimeSerie(self):
		ts = []
		date = sorted(self.keys())
		d = date[0]
		x = self[d]
		ts.append(x)
		for i in xrange(1, len(date)):
			d_l = d
			x_l = x
			d = date[i]
			x = self[d]
			L = (d - d_l).days
			for j in range(L):
				ts.append(x_l + (x - x_l) * (j + 1) / float(L))
		return TimeSerie(ts, TimeWindow(min(self.keys()), max(self.keys())))

	def map(self, f):
		h = DateSerie()
		for d, v in self.iteritems():
			h[d] = f(v)
		return h