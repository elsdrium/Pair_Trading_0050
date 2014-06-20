import datetime
from RawDataProcessing import *

def StrategyTesting(beginDate, endDate, strategy, optionData=None, stockData=None):
	beginDate = datetime.datetime.strptime( beginDate, '%Y/%m/%d' ).date()
	endDate   = datetime.datetime.strptime( endDate,   '%Y/%m/%d' ).date()
	dtIdx = OptionDailyData.invKeys['Date']

	dataList = [optionData, stockData]
	for data in dataList:
		if data[dtIdx] < beginDate: continue
		if data[dtIdx] > endDate:   break

		strategy(data)