from RawDataProcessing import *

od = OptionDailyData()
sd = StockDailyData()

#result = od.getDataByDate('2001/01/01', '2001/12/26', Contract='TXO', Type='Call')


m201212 = datetime.datetime.strptime( '201212', '%Y%m' ).date()

result = od.getDataByDate('2012/11/01', '2012/12/26', Contract='TXO', Type='Call', Maturity=m201212)
print result

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
