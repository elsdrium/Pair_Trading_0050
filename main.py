import matplotlib.pyplot as plt
from RawDataProcessing import *
from BackTesting import *
from matplotlib import pylab as pl
import time

odd = OptionDailyData()
sdd = StockDailyData()

#result = od.getDataByDate('2001/01/01', '2001/12/26', Contract='TXO', Type='Call')


m201202 = datetime.datetime.strptime( '201202', '%Y%m' ).date()

#startTime = time.time()
result = odd.getDataByDate('2012/01/01', '2012/02/26', Contract='TXO', Type='Call', Strike=8000, Maturity=m201202)
#endTime = time.time()

print len(result)
#print endTime - startTime

closeIdx = odd.invKeys['Close']
pl.plot( range(len(result)), [ r[closeIdx] for r in result ] )
plt.show()

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
