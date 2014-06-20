from RawDataProcessing import *
from BackTesting import *
from matplotlib import pylab as pl
import time

od = OptionDailyData()
sd = StockDailyData()

#result = od.getDataByDate('2001/01/01', '2001/12/26', Contract='TXO', Type='Call')


m201212 = datetime.datetime.strptime( '201212', '%Y%m' ).date()

#startTime = time.time()
result = od.getDataByDate('2012/11/01', '2012/12/26', Contract='TXO', Type='Call', Strike=8000, Maturity=m201212)
#endTime = time.time()

print len(result)
#print endTime - startTime

closeIdx = od.invKeys['Close']
pl.plot( range(len(result)), [ r[closeIdx] for r in result ] )

"""
from IPython.display import display
import numpy as np
import matplotlib.pyplot as plt

x = np.linspace(-1, 1, 100)

f = lambda t: t**2
g = lambda t: 2**t

plt.plot(x, f(x))
plt.plot(x, g(x))

plt.show()
"""
