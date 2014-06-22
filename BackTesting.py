import datetime
from RawDataProcessing import *

def StrategyTesting(beginDate, endDate, strategy, optionData=None, stockData=None):
	beginDate = datetime.datetime.strptime( beginDate, '%Y/%m/%d' ).date()
	endDate   = datetime.datetime.strptime( endDate,   '%Y/%m/%d' ).date()
	dtIdx = OptionDailyData.invKeys['Date']

	if optionData is None and stockData is None:
		raise 'No data'

	if optionData is not None:
		i = 0
		while optionData[i][dtIdx] < beginDate: i += 1

	if stockData is not None:
		j = 0
		while stockData[j][dtIdx]  < beginDate:   j += 1

	while (i != None) or (j != None) or (optionData[i][dtIdx] <= endDate) or (stockData[j][dtIdx] <= endDate):
		strategy( optionData=optionData[i], stockData=stockData[j] )
		i += 1
		j += 1
