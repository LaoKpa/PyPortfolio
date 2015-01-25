from datetime import *
from historical import *
from timewindow import *
from timeserie import *
from graphics import *


symbol = 'GOOGL'
W = TimeWindow.years(2010,2014)
P = LogPrice(symbol)
R = LogReturns(symbol)
LR = P.SimpleLinearRegr(365, shift = 1)
V = P.variation().stdev(365) * 9

x = plot(W)
x.title(symbol + "   " + str(W))

x.draw(P)
x.draw(P.sma(90), linewidth = 2, color='green')
x.draw(LR, linewidth = 2, color='black')
x.draw(LR+V, linewidth = .5, color='red')
x.draw(LR-V, linewidth = .5, color='red')



x.show()