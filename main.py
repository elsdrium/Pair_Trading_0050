from Utilities import *
from RawDataProcessing import *
from matplotlib import pylab as pl
from matplotlib import dates
import datetime
import numpy as np

############################## Constants ##############################
beginDate = str2date('2003/07/01')
endDate = str2date('2003/10/31')
maturity = str2date('2012/08/01')

kwargs = {
	'Type': 'Call',
	# 'Strike': 8000,
	# 'Maturity': maturity,
}

outOfMoney = 100

stockTransCost = 0.2
futuresTransCost = 0
optionTransCost = 0.8

############################# Loading Data ############################
try:
	# no needs to reload data every time
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

	# ########################### Preprocessing ############################
	dateSequence = np.array([r[sdd.invKeys['Date']] for r in stock_data])

	stockCloseIdx = sdd.invKeys['Close']
	indexCloseIdx = idd.invKeys['Close']
	futuresCloseIdx = fdd.invKeys['Close']
	optionCloseIdx = odd.invKeys['Close']

	# pick close price as daily price
	stockPrice = np.array([r[stockCloseIdx] for r in stock_data])
	indexPrice = np.array([r[indexCloseIdx] for r in index_data])
	futuresPrice = np.array([r[futuresCloseIdx] for r in futures_data])
	#optionPrice = np.array([r[optionCloseIdx] for r in option_data])

	stockReturn = returnRate(stockPrice)
	indexReturn = returnRate(indexPrice)
	futuresReturn = returnRate(futuresPrice)

# end of try-except scope

########################### Testing Strategy ##########################
opdata = []
def selectOptionPrice():
	optionMaturityIdx  = odd.invKeys['Maturity']
	optionStrikeIdx    = odd.invKeys['Strike']
	optionDateIdx      = odd.invKeys['Date']
	futuresMaturityIdx = fdd.invKeys['Maturity']
	futuresDateIdx     = fdd.invKeys['Date']

	result = []
	i = 0
	for f in futures_data:
		while i != len(option_data):
			if option_data[i][optionDateIdx] < f[futuresDateIdx]:
				i += 1
				continue

			if option_data[i][optionMaturityIdx] == f[futuresMaturityIdx] and option_data[i][optionStrikeIdx] - f[futuresCloseIdx] >= outOfMoney:
				result.append( option_data[i][optionCloseIdx] )
				opdata.append( option_data[i] )
				i += 1
				break
			else:
				i += 1

	return result


optionPrice = selectOptionPrice()

positionLimit = {'0050': 50,
                 'TXO': 50,
                 'TX': 50,
}
TransactionCost = {'0050': stockTransCost,
                   'TXO': optionTransCost,
                   'TX': futuresTransCost,
}

portfolio      = {'0050': 0, 'TXO': 0, 'TX': 0}
pendingToTrade = {'0050': 0, 'TXO': 0, 'TX': 0}
priceDifference = {'0050': np.append([0], np.diff(stockPrice)),
                   'TXO': np.append([0], np.diff(optionPrice)),
                   'TX': np.append([0], np.diff(futuresPrice)),
}

transactionLog = {}
PL = [0]


# slow, fast, macd = movingAverageConvergence(stockPrice)
randomNumber = np.round(np.random.lognormal() * 100)

for i in range(len(indexPrice)):

	### check maturity
	todayMaturity = False
	if i + 1 < len(indexPrice) and futures_data[i + 1][fdd.invKeys['Maturity']] != futures_data[i][
		fdd.invKeys['Maturity']]:
		todayMaturity = True

	### update profit & loss
	PL.append(PL[-1])
	for item in portfolio:
		PL[-1] += (priceDifference[item][i] * portfolio[item])

	### check trading signals
	if i == randomNumber:
		#pendingToTrade['0050'] += 5000
		pendingToTrade['TXO'] -= 50

	if i >= randomNumber:
		if portfolio['TXO'] == 0:
			pendingToTrade['TXO'] -= 50

	### check futures / option matures
	if todayMaturity:
		pendingToTrade['TXO'] = -portfolio['TXO']
		pendingToTrade['TX']  = -portfolio['TX']

	### validate transaction
	for item in pendingToTrade:
		if pendingToTrade[item] > 0 and portfolio[item] >= positionLimit[item]:
			pendingToTrade[item] = 0

		if pendingToTrade[item] < 0 and -portfolio[item] >= positionLimit[item]:
			pendingToTrade[item] = 0

	### execute transaction
	transactionLog[dateSequence[i]] = {}
	for item in pendingToTrade:
		if pendingToTrade[item] != 0:
			print( str(dateSequence[i]) + ' : ' + item + ' ' + str(pendingToTrade[item]) )
			print( '     Price : ' + str(optionPrice[i]) )
			print( '     Data  : ' + str(opdata[i]) )
			print( '  Futures  : ' + str(futuresPrice[i]) )
			portfolio[item] += pendingToTrade[item]
			PL[-1] -= (TransactionCost[item] * np.abs(pendingToTrade[item]))
			transactionLog[dateSequence[i]][item] = pendingToTrade[item]
			pendingToTrade[item] = 0

PL = PL[1:]


########################## Generating Graphs ##########################
pl.plot(dateSequence, PL)
