from Utilities import *
from RawDataProcessing import *
from matplotlib import pylab as pl
from matplotlib import dates
from scipy import stats
import datetime
import numpy as np

# ############################# Constants ##############################
beginDate = str2date('2004/4/01')
endDate = str2date('2013/12/31')
initCapital = 10**6

kwargs = {
'Type': 'Call',  # 'Strike': 8000,  # 'Maturity': maturity,
}

moneyness = -0

stockTransCost = 1000
futuresTransCost = 150
optionTransCost = 100

UNIT = {'0050': 1000,
        'TXO': 50,
        'TX': 50,
}

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

dividend0050 = {475: 1.85, 832: 4.0, 1077: 2.5, 1328: 2.0, 1578: 1.0, 1828: 2.2, 2076: 1.95, 2325: 1.85, 2571: 1.35}


# end of try-except scope

########################### Testing Strategy ##########################

optionMaturityIdx = odd.invKeys['Maturity']
optionStrikeIdx = odd.invKeys['Strike']
optionDateIdx = odd.invKeys['Date']
futuresMaturityIdx = fdd.invKeys['Maturity']
futuresDateIdx = fdd.invKeys['Date']

beginDateIndex = 0
while beginDateIndex < len(futures_data) and futures_data[beginDateIndex][futuresDateIdx] < beginDate:
	beginDateIndex += 1


def selectOptionData(outOfMoney=0):
	result = []
	currentStrike = None
	j = 0

	for i in range(beginDateIndex, len(futures_data)):
		maturity = futures_data[i][futuresMaturityIdx]
		todayMaturity = False
		if i + 1 < len(indexPrice) and futures_data[i + 1][futuresMaturityIdx] != futures_data[i][futuresMaturityIdx]:
			todayMaturity = True

		while j != len(option_data):
			if option_data[j][optionDateIdx] < futures_data[i][futuresDateIdx]:
				j += 1
				continue

			if option_data[j][optionMaturityIdx] != maturity:
				j += 1
				continue

			if currentStrike is None:
				if option_data[j][optionStrikeIdx] > (futures_data[i][futuresCloseIdx] + outOfMoney):
					currentStrike = option_data[j][optionStrikeIdx]
					result.append(option_data[j])
					j += 1
					break
				else:
					j += 1
					continue
			elif currentStrike != option_data[j][optionStrikeIdx]:
				j += 1
				continue
			else:
				result.append(option_data[j])
				if todayMaturity:
					currentStrike = None
				j += 1
				break

	return result


selectedOptionData = selectOptionData(0)
optionPrice = [data[optionCloseIdx] for data in selectedOptionData]

selectedSellOptionData = selectOptionData(300)
sellOptionPrice = [data[optionCloseIdx] for data in selectedSellOptionData]

positionLimit = {'0050': 10,
                 'TXO': 10,
                 'TX': 10,
}
TransactionCost = {'0050': stockTransCost,
                   'TXO': optionTransCost,
                   'TX':  optionTransCost,
}

portfolio = {'0050': 0, 'TXO': 0, 'TX': 0}
pendingToTrade = {'0050': 0, 'TXO': 0, 'TX': 0}
priceDifference = {'0050': np.append([0], np.diff(stockPrice)),
                   'TXO': np.append([0] * (beginDateIndex + 1), np.diff(optionPrice)),
                   'TX' : np.append([0] * (beginDateIndex + 1), np.diff(sellOptionPrice)),
}

transactionLog = {}
PL = [0]
monthlyPL = [(beginDate, 0)]

constant = 0.075
slow, fast, macd = movingAverageConvergence(indexPrice)
signal = movingAverage(macd, 9, type='exponential')
convergence = macd - signal

initFlag  = bool(1)
shortFlag = bool(0)
hedgeFlag = bool(1)
sellOptionFlag = bool(1)

#cnt = 0
#currentInit = 0
for i in range(beginDateIndex, len(indexPrice)):

	### check maturity
	todayMaturity = False
	if i + 1 < len(indexPrice) and futures_data[i + 1][fdd.invKeys['Maturity']] != futures_data[i][
		fdd.invKeys['Maturity']]:
		todayMaturity = True

	### update profit & loss
	PL.append(PL[-1])
	for item in portfolio:
		PL[-1] += (priceDifference[item][i] * portfolio[item] * UNIT[item])

	if dividend0050.has_key(len(PL) - 2):
		PL[-1] += dividend0050[len(PL) - 2] * portfolio['0050'] * UNIT['0050']

	################## check trading signals ###############################

	# initial position
	if initFlag:
		initFlag = False
		pendingToTrade['0050'] += 10

	# 2 strategies
	if hedgeFlag:
		if (-macd[i]) > constant*fast[i]:
			pendingToTrade['TXO'] -= 10
	else:
		if (-macd[i]) > constant*fast[i]:
			pendingToTrade['TXO'] -= 10
			pendingToTrade['TX'] -= portfolio['TX']
			sellOptionFlag = False

		sellAmount = 5
		if not sellOptionFlag:
			pendingToTrade['TX'] -= sellAmount
			sellOptionFlag = True

		if todayMaturity and sellOptionFlag:
			sellOptionFlag = False

		# stopping loss
		if macd[i] > constant*fast[i]:
			pendingToTrade['TXO'] = -portfolio['TXO']
			pendingToTrade['TX']  = -portfolio['TX']


#	if i > 0 and macd[i-1] < 0 and convergence[i - 1] > 0 and convergence[i] < 0:
#		pendingToTrade['TXO'] -= shortAmount
#		shortFlag = True
#
#	if i > 0 and macd[i-1] > 0 and convergence[i - 1] < 0 and convergence[i] > 0:
#		pendingToTrade['TXO'] -= shortAmount
#		shortFlag = True

#	if i > 0 and convergence[i - 1] < 0 and convergence[i] > 0:
#		pendingToTrade['TXO'] -= portfolio['TXO']
#		shortFlag = False

	########################################################################

	### check futures / option matures
	if todayMaturity:
		pendingToTrade['TXO'] = -portfolio['TXO']
		pendingToTrade['TX'] = -portfolio['TX']

		priceDifference['TXO'][i + 1] = 0
		priceDifference['TX'][i + 1] = 0

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
			portfolio[item] += pendingToTrade[item]
			PL[-1] -= (TransactionCost[item] * np.abs(pendingToTrade[item]))
			transactionLog[dateSequence[i]][item] = pendingToTrade[item]
			pendingToTrade[item] = 0

	### for performance estimation
	if todayMaturity:
		monthlyPL.append( (futures_data[i][futuresDateIdx], PL[-1]) )

PL = PL[1:]


########################## Generating Graphs ##########################
pl.plot( dateSequence[beginDateIndex:], PL )


returnRate = 100 * PL[-1] / initCapital
periodYears = (len(dateSequence)-beginDateIndex) / 248.0

if hedgeFlag:
	print( 'Strategy : Hedging' )
else:
	print( 'Strategy : Aggressive Selling' )

print( 'Period : {:.2f} years'.format(periodYears) )
print( 'Trading Times : {}'.format(len([log for log in transactionLog if len(transactionLog[log]) != 0])) )
print( 'Max P&L :   {:.0f}'.format(max(PL)) )
print( 'Min P&L :  {:.0f}'.format(min(PL)) )
print( 'Final P&L : {:.0f}'.format(PL[-1]) )
print( 'Ttl Return : {:.3f}%'.format( returnRate ) )
print( 'Avg Return : {:.3f}%'.format( returnRate / periodYears ) )
