from datetime import *
from data import *
from timewindow import *
from timeserie import *
from graphics import *


symbol = 'GOOGL'
W = TimeWindow.years(2010,2014)
P = LogPrice(symbol)

LR = P.SimpleLinearRegr(91, shift = 0)
V = P.variation().stdev(365) * 9

x = plot(W)
x.title(symbol + "   " + str(W))

N = 90
x.draw(P)
x.draw(P.sma(N), linewidth = 2, color='green')
x.draw(LR, linewidth = 2, color='black')
x.draw(LR+V, linewidth = .5, color='red')
x.draw(LR-V, linewidth = .5, color='red')
x.show()
