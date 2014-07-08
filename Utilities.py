# -*- coding: utf-8 -*-
"""
Some methods
from 2001 to 2013
"""
__author__ = 'chen hsueh-min'

import datetime
import numpy as np
# from RawDataProcessing import *
from scipy.stats.stats import pearsonr


def str2date(dateStr):
	return datetime.datetime.strptime(dateStr, '%Y/%m/%d').date()


def returnRate(data):
	return np.diff(data) / map(float, data[:len(data) - 1])


def nCorrelation(x, y, n=None, pValue=False):
	if n is None:
		if pValue:
			return pearsonr(x, y)
		else:
			return pearsonr(x, y)[0]
	else:
		if pValue:
			return [pearsonr(x[k - n:k], y[k - n:k]) for k in range(n, len(x) + 1)]
		else:
			return [pearsonr(x[k - n:k], y[k - n:k])[0] for k in range(n, len(x) + 1)]

# from matplotlib example
def movingAverage(x, n, type='simple'):
	"""
	compute an n period moving average.

	type is 'simple' | 'exponential'

	"""
	x = np.asarray(x)
	if type == 'simple':
		weights = np.ones(n)
	else:
		weights = np.exp(np.linspace(-1., 0., n))

	weights /= weights.sum()

	a = np.convolve(x, weights, mode='full')[:len(x)]
	a[:n] = a[n]
	return a

# from matplotlib example
def relativeStrength(prices, n=14):
	"""
	compute the n period relative strength indicator
	http://stockcharts.com/school/doku.php?id=chart_school:glossary_r#relativestrengthindex
	http://www.investopedia.com/terms/r/rsi.asp
	"""

	deltas = np.diff(prices)
	seed = deltas[:n + 1]
	up = seed[seed >= 0].sum() / n
	down = -seed[seed < 0].sum() / n
	rs = up / down
	rsi = np.zeros_like(prices)
	rsi[:n] = 100. - 100. / (1. + rs)

	for i in range(n, len(prices)):
		delta = deltas[i - 1]  # cause the diff is 1 shorter

		if delta > 0:
			upval = delta
			downval = 0.
		else:
			upval = 0.
			downval = -delta

		up = (up * (n - 1) + upval) / n
		down = (down * (n - 1) + downval) / n

		rs = up / down
		rsi[i] = 100. - 100. / (1. + rs)

	return rsi

# from matplotlib example
def movingAverageConvergence(x, nslow=26, nfast=12):
	"""
	compute the MACD (Moving Average Convergence/Divergence) using a fast and slow exponential moving avg'
	return value is emaslow, emafast, macd which are len(x) arrays
	"""
	emaslow = movingAverage(x, nslow, type='exponential')
	emafast = movingAverage(x, nfast, type='exponential')
	return emaslow, emafast, emafast - emaslow