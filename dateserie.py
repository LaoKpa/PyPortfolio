#!/usr/bin/env python
from datetime import *
from timewindow import *
from timeserie import *
import numpy as np

class DateSerie(dict):
	
	def TimeSerie(self, mode = None):
		"""
		Convert a DateSerie to a TimeSerie, filling the days that haven't a value
		to fill this, we consider three modes:
			* smooth		: ...
			* exp			: ...
			* previous/None	: ...
		"""
		ts = []
		date = sorted(self.keys())

		if mode == 'smooth':
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

		if mode == 'exp':
			from math import exp, log
			d = date[0]
			ts.append(self[d])
			x = log(self[d])
			for i in xrange(1, len(date)):
				d_l = d
				x_l = x
				d = date[i]
				x = log(self[d])
				L = (d - d_l).days
				for j in range(L):
					ts.append(exp(x_l + (x - x_l) * (j + 1) / float(L)))

		else:
			d_next = date[0]
			for i in xrange(1, len(date)):
				d = d_next
				d_next = date[i]
				L = (d_next - d).days
				for j in range(L):
					ts.append(self[d])
			ts.append(self[date[-1]])

		return TimeSerie(ts, TimeWindow(min(self.keys()), max(self.keys())))

	def map(self, f):
		h = DateSerie()
		for d, v in self.iteritems():
			h[d] = f(v)
		return h