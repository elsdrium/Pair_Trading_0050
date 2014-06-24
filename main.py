from Utilities import *
from RawDataProcessing import *
from matplotlib import pylab as pl
from matplotlib import dates
import datetime
import numpy as np

# ############################# Constants ##############################
beginDate = str2date('2003/07/01')
endDate = str2date('2013/12/31')
maturity = str2date('2012/08/01')

kwargs = {
	'Type': 'Call',
#	'Strike': 8000,
#	'Maturity': maturity
}

stockTransCost = 0.4
futuresTransCost = 200
optionTransCost = 50

# ############################ Loading Data ############################
try:
	len(option_data)
except NameError:
	sdd = StockDailyData()
	idd = IndexDailyData()
	fdd = TXFuturesDailyData()
	odd = TXOptionDailyData()

	print( 'Loading stock data(0050)...' )
	stock_data = sdd.getDataByDate(beginDate, endDate, stockNumber='0050')
	print( '......Done.' )

	print( 'Loading index data(Taiwan Index)...' )
	index_data = idd.getDataByDate(beginDate, endDate)
	print( '......Done.' )

	print( 'Loading futures data(TX)...' )
	futures_data = fdd.getDataByDate(beginDate, endDate, near=True)
	print( '......Done.' )

	print( 'Loading option data(TXO)...' )
	# option data would take huge time to load...
	option_data = odd.getDataByDate(beginDate, endDate, **kwargs)
	print( '......Done.' )

############################ Preprocessing ############################
	dateSequence = np.array([r[sdd.invKeys['Date']] for r in stock_data])

	stockCloseIdx = sdd.invKeys['Close']
	indexCloseIdx = idd.invKeys['Close']
	futuresCloseIdx = fdd.invKeys['Close']
	optionCloseIdx = odd.invKeys['Close']

	# pick close price as daily price
	stockPrice = np.array([r[stockCloseIdx] for r in stock_data])
	indexPrice = np.array([r[indexCloseIdx] for r in index_data])
	futuresPrice = np.array([r[futuresCloseIdx] for r in futures_data])
	optionPrice  = np.array([ r[optionCloseIdx ] for r in option_data  ])

	stockReturn = returnRate(stockPrice)
	indexReturn = returnRate(indexPrice)
	futuresReturn = returnRate(futuresPrice)

# end of try-except scope

########################### Testing Strategy ##########################
positionLimit = {'0050': 50, }
TransactionCost = {'0050': stockTransCost, }

transactionLog = {}
PL = [0]

slow, fast, macd = movingAverageConvergence(stockPrice)
portfolio = {'0050': 0, }
pendingToTrade = {'0050': 0, }

stockDiff = np.append([0], np.diff(stockPrice))
for i in range(len(indexPrice)):

	### update profit & loss
	PL.append(PL[-1])
	for item in portfolio:
		PL[-1] += (stockDiff[i] * portfolio[item])

	### check trading signals
	if macd[i] > 1:
		pendingToTrade['0050'] += 1
	if macd[i] < -1:
		pendingToTrade['0050'] -= 1

	### validate transaction
	for item in pendingToTrade:
		if pendingToTrade[item] > 0 and portfolio[item] >= positionLimit[item]:
			pendingToTrade[item] = 0

		if pendingToTrade[item] < 0 and portfolio[item] <= positionLimit[item]:
			pendingToTrade[item] = 0

	### execute transaction
	transactionLog[dateSequence[i]] = {}
	for item in pendingToTrade:
		if pendingToTrade[item] != 0:
			portfolio[item] += pendingToTrade[item]
			PL[-1] -= (TransactionCost[item] * np.abs(pendingToTrade[item]))
			transactionLog[dateSequence[i]][item] = pendingToTrade[item]
			pendingToTrade[item] = 0


########################## Generating Graphs ##########################

