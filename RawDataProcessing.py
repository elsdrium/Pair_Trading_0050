# -*- coding: utf-8 -*-
"""
Filtering the TXO data
from 2001 to 2013
"""

import csv
import datetime
import copy
import urllib
from abc import ABCMeta, abstractmethod

class AbstractDailyData:
	"""
	Class Type : Interface
	Class Usage: Download and load daily data
	"""
	__metaclass__ = ABCMeta

	@abstractmethod
	def getDataByDate(self, beginDate, endDate, **kwargs):
		pass

	@abstractmethod
	def saveAsCSV(self, data, filename):
		pass
	@abstractmethod
	def loadCSV(self, filename, **kwargs):
		pass


class OptionDailyData( AbstractDailyData ):
	Keys = ('Date', 'Contract', 'Maturity', 'Strike', 'Type', 'Open', 'High', 'Low', 'Close', 'Volume', 'Settlement', 'OI', 'LastBid', 'LastOffer', 'HisHigh', 'HisLow')
	invKeys = {'Date':0, 'Contract':1, 'Maturity':2, 'Strike':3, 'Type':4, 'Open':5, 'High':6, 'Low':7, 'Close':8, 'Volume':9, 'Settlement':10, 'OI':11, 'LastBid':12, 'LastOffer':13, 'HisHigh':14, 'HisLow':15}
	#data = []

	def __init__(self):
		pass

	def _toDate(self, dateStr):
		return datetime.datetime.strptime( dateStr, '%Y/%m/%d' ).date()

	def _processRow(self, row):
		row[ self.invKeys['Date'] ] = self._toDate( row[ self.invKeys['Date'] ] )
		row[ self.invKeys['Maturity'] ] = datetime.datetime.strptime( str(int(row[ self.invKeys['Maturity'] ])), '%Y%m' ).date()
		row[ self.invKeys['Type'] ] = 'Put' if row[ self.invKeys['Type'] ] == '\xbd\xe6\xc5v' or row[ self.invKeys['Type'] ] == 'Put' else 'Call'

		# except 'Contract', 'Date', 'Maturity', 'Type'
		for key in ('Strike', 'Open', 'High', 'Low', 'Close', 'Volume', 'Settlement', 'OI', 'LastBid', 'LastOffer', 'HisHigh', 'HisLow'):
			row[ self.invKeys[key] ] = float(row[ self.invKeys[key] ])
		return row

	def _validateRow(self, row, **kwargs):
		for key in list(kwargs.keys()):
			if row[ self.invKeys[key] ] != kwargs[key]:
				return False
		return True

	def _readDataFromCSV(self, filename, beginDate, endDate, **kwargs):
		result = []
		with open(filename, 'r') as handle:
			reader = csv.reader(handle)
			next(reader) # skip the header row
			for row in reader:
				try:
					date = self._toDate( row[0] )
					if date < beginDate:
						continue
					elif date > endDate:
						# Original data is sorted by date, so we can stop reading if it exceeds endDate.
						return result

					row = self._processRow(row)
				except:
					continue

				if self._validateRow(row, **kwargs):
					result.append( tuple(row) )
		return result

	def getDataByDate(self, beginDate='2001/01/01', endDate='2013/12/31', **kwargs):
		if isinstance(beginDate, str):
			beginDate = self._toDate( beginDate )
			endDate   = self._toDate( endDate )

		if beginDate > endDate:
			return []

		data = []
		for year in range(beginDate.year, endDate.year+1):
			if year == 2001:
				data += self._readDataFromCSV('../Option_HistoData/2001_opt.csv', beginDate, endDate, **kwargs)
			else:
				data += self._readDataFromCSV('../Option_HistoData/' + str(year) + '_opt/' + str(year) + '_01_06_opt.csv', beginDate, endDate, **kwargs)
				data += self._readDataFromCSV('../Option_HistoData/' + str(year) + '_opt/' + str(year) + '_07_12_opt.csv', beginDate, endDate, **kwargs)
		return data

	def saveAsCSV(self, data, filename):
		with open(filename, 'wb') as f:
			w = csv.writer(f)
			w.writeheader()
			for row in data:
				row = list(row)

				# Very inefficient but important! Avoiding change the content of data.
				tempDate = copy.deepcopy( row[ self.invKeys['Date'] ] )
				tempMaturity = copy.deepcopy( row[ self.invKeys['Maturity'] ] )

				row[ self.invKeys['Date'] ] = row[ self.invKeys['Date'] ].strftime( '%Y/%m/%d' )
				row[ self.invKeys['Maturity'] ] = row[ self.invKeys['Maturity'] ].strftime( '%Y%m' )
				w.writerow( row )

				row[ self.invKeys['Date'] ] = tempDate
				row[ self.invKeys['Maturity'] ] = tempMaturity
				del tempDate
				del tempMaturity
				row = tuple(row)

	def loadCSV(self, filename, **kwargs):
		result = []
		with open(filename, 'r') as handle:
			reader = csv.reader(handle)
			next(reader) # skip the header row
			for row in reader:
				row = self._processRow(row)
				if self._validateRow(row, **kwargs):
					result.append( tuple(row) )
		return result


class StockDailyData( AbstractDailyData ):
	Keys = ('Date', 'Volume', 'Amount', 'Open', 'High', 'Low', 'Close', 'Difference', 'NoOfTransactions')
	invKeys = {'Date':0, 'Volume':1, 'Amount':2, 'Open':3, 'High':4, 'Low':5, 'Close':6, 'Difference':7, 'NoOfTransactions':8}


	def __init__(self):
		pass

	def _toDate(self, dateStr):
		return datetime.datetime.strptime( dateStr, '%Y/%m/%d' ).date()

	def _processRow(self, row):
		row[ self.invKeys['Date'] ]   = self._toDate( row[ self.invKeys['Date'] ] )
		row[ self.invKeys['Amount'] ] = long( row[ self.invKeys['Amount'] ] )
		row[ self.invKeys['Volume'] ] = long( row[ self.invKeys['Volume'] ] )
		row[ self.invKeys['NoOfTransactions'] ] = long( row[ self.invKeys['NoOfTransactions'] ] )
		for key in ('Open', 'High', 'Low', 'Close', 'Difference'):
			row[ self.invKeys['key'] ] = float( row[ self.invKeys['key'] ] )
		return row

	def _validateRow(self, row, **kwargs):
		for key in list(kwargs.keys()):
			if row[ self.invKeys[key] ] != kwargs[key]:
				return False
		return True

	def _readDataFromCSV(self, filename, beginDate, endDate, **kwargs):
		result = []
		with open(filename, 'r') as handle:
			reader = csv.reader(handle)
			next(reader) # skip the 1st header row
			next(reader) # skip the 2nd header row
			for row in reader:
				row = self._processRow(row)
				if self._validateRow(row, **kwargs) and row[ self.invKeys['Date'] ] >= beginDate and row[ self.invKeys['Date'] ] <= endDate:
					result.append( tuple(row) )
		return result

	def getDataByDate(self, beginDate, endDate, **kwargs):
		if isinstance(beginDate, str):
			beginDate = self._toDate( beginDate )
			endDate   = self._toDate( endDate )

		if beginDate > endDate:
			return []

		data = []
		for year in range(beginDate.year, endDate.year+1):
			for month in range(1,13):
				if year == beginDate.year and month < beginDate.month:
					continue
				if year == endDate.year and month > endDate.month:
					continue
				data += self._readDataFromCSV('../Stock_HistoData/stock_' + kwargs['stockNumber'] + '_' + datetime.date(year, month, 1).strftime( '%Y%m' ) + '.csv', beginDate, endDate, **kwargs)
		return data

	def saveAsCSV(self, data, filename):
		with open(filename, 'wb') as f:
			w = csv.writer(f)
			w.writeheader()
			w.writeheader() # write 2 header rows

			for row in data:
				row = list(row)
				tempDate = copy.deepcopy(row[ self.invKeys['Date'] ] )
				row[ self.invKeys['Date'] ] = row[ self.invKeys['Date'] ].strftime( '%Y/%m/%d' )
				w.writerow( row )
				row[ self.invKeys['Date'] ] = tempDate
				del tempDate
				row = tuple(row)


	def loadCSV(self, filename, **kwargs):
		result = []
		with open(filename, 'r') as handle:
			reader = csv.reader(handle)
			next(reader) # skip the 1st header row
			next(reader) # skip the 2nd header row
			for row in reader:
				row = self._processRow(row)
				if self._validateRow(row, **kwargs):
					result.append( tuple(row) )
		return result

	def downloadAllCSVData(self, stockNumber='2330', beginYYYYMM='201401'):
		"""Download stock data by number and date."""
		if isinstance(beginYYYYMM, str):
			beginYYYYMM = datetime.datetime.strptime( beginYYYYMM, '%Y%m' ).date()

		for year in range(beginYYYYMM.year, datetime.datetime.today().year+1):
			for month in range(1, 13):
				if year == beginYYYYMM.year and month < beginYYYYMM.month:
					continue
				if year == datetime.datetime.today().year and month > datetime.datetime.today().month:
					continue
				url = 'http://www.twse.com.tw/ch/trading/exchange/STOCK_DAY/STOCK_DAY_print.php?genpage=genpage/Report'+ datetime.date(year, month, 1).strftime( '%Y%m' ) +'/'+ datetime.date(year, month, 1).strftime( '%Y%m' ) +'_F3_1_8_' + stockNumber + '.php&type=csv'
				filename = '../Stock_HistoData/stock_' + stockNumber + '_' + datetime.date(year, month, 1).strftime( '%Y%m' ) + '.csv'
				urllib.urlretrieve(url, filename)




#oddata = OptionDailyData()
#data = oddata.getDataByDate('2001/01/01', '2001/12/26', Contract='TXO', Type='Call')
#oddata.saveAsCSV( data, 'waha.csv')
#data2 = oddata.loadCSV('waha.csv')

#sddata = StockDailyData()
#sddata.downloadAllCSVData('0050', '200306')  # Run this once is enough

