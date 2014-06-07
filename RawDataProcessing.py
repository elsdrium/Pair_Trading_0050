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
	#data = []

	def __init__(self):
		pass

	def _toDate(self, dateStr):
		return datetime.datetime.strptime( dateStr, '%Y/%m/%d' ).date()

	def _processRow(self, row):
		row['Date'] = self._toDate( row['Date'] )
		row['Maturity'] = datetime.datetime.strptime( str(int(row['Maturity'])), '%Y%m' ).date()
		row['Type'] = 'Put' if row['Type'] == '\xbd\xe6\xc5v' or row['Type'] == 'Put' else 'Call'

		# except 'Contract', 'Date', 'Maturity', 'Type'
		for key in ('Strike', 'Open', 'High', 'Low', 'Close', 'Volume', 'Settlement', 'OI', 'LastBid', 'LastOffer', 'HisHigh', 'HisLow'):
			row[key] = float(row[key])
		return row

	def _validateRow(self, row, **kwargs):
		for key in list(kwargs.keys()):
			if row[key] != kwargs[key]:
				return False
		return True

	def _readDataFromCSV(self, filename, beginDate, endDate, **kwargs):
		result = []
		with open(filename, 'r') as handle:
			reader = csv.DictReader(handle, self.Keys)
			next(reader) # skip the header row
			for row in reader:
				try:
					row = self._processRow(row)
				except:
					continue

				if self._validateRow(row, **kwargs) and row['Date'] >= beginDate:
					if row['Date'] <= endDate:
						result.append( row )
					else:
						return result
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
			w = csv.DictWriter(f, self.Keys)
			w.writeheader()
			for row in data:
				# Very inefficient but important! Avoid changing the content of data.
				tempDate = copy.deepcopy(row['Date'])
				tempMaturity = copy.deepcopy(row['Maturity'])

				row['Date'] = row['Date'].strftime( '%Y/%m/%d' )
				row['Maturity'] = row['Maturity'].strftime( '%Y%m' )
				w.writerow( row )

				row['Date'] = tempDate
				row['Maturity'] = tempMaturity
				del tempDate
				del tempMaturity

	def loadCSV(self, filename, **kwargs):
		result = []
		with open(filename, 'r') as handle:
			reader = csv.DictReader(handle, self.Keys)
			next(reader) # skip the header row
			for row in reader:
				row = self._processRow(row)
				if self._validateRow(row, **kwargs):
					result.append( row )
		return result


class StockDailyData( AbstractDailyData ):
	Keys = ('Date', 'Volume', 'Amount', 'Open', 'High', 'Low', 'Close', 'Difference', 'NoOfTransactions')

	def __init__(self):
		pass

	def _toDate(self, dateStr):
		return datetime.datetime.strptime( dateStr, '%Y/%m/%d' ).date()

	def _processRow(self, row):
		row['Date'] = self._toDate(row['Date'])
		row['Amount'] = long(row['Amount'])
		row['Volume'] = long(row['Volume'])
		row['NoOfTransactions'] = long(row['NoOfTransactions'])
		for key in ('Open', 'High', 'Low', 'Close', 'Difference'):
			row['key'] = float(row['key'])
		return row

	def _validateRow(self, row, **kwargs):
		for key in list(kwargs.keys()):
			if row[key] != kwargs[key]:
				return False
		return True

	def _readDataFromCSV(self, filename, beginDate, endDate, **kwargs):
		result = []
		with open(filename, 'r') as handle:
			reader = csv.DictReader(handle, self.Keys)
			next(reader) # skip the 1st header row
			next(reader) # skip the 2nd header row
			for row in reader:
				row = self._processRow(row)
				if self._validateRow(row, **kwargs) and row['Date'] >= beginDate and row['Date'] <= endDate:
					result.append( row )
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
			w = csv.DictWriter(f, self.Keys)
			w.writeheader()
			w.writeheader() # write 2 header rows

			for row in data:
				tempDate = copy.deepcopy(row['Date'])
				row['Date'] = row['Date'].strftime( '%Y/%m/%d' )
				w.writerow( row )
				row['Date'] = tempDate
				del tempDate


	def loadCSV(self, filename, **kwargs):
		result = []
		with open(filename, 'r') as handle:
			reader = csv.DictReader(handle, self.Keys)
			next(reader) # skip the 1st header row
			next(reader) # skip the 2nd header row
			for row in reader:
				row = self._processRow(row)
				if self._validateRow(row, **kwargs):
					result.append( row )
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

