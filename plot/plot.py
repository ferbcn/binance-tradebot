import sys
sys.path.append('..')

from Queue import deque
from binance.enums import *

from Trader import Trader
from config import TRADING_PAIR

analyze = Trader.analyze
client = Trader.client

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
import datetime as dt
import matplotlib.dates as mdates

class Plot(object):

    def get_hist_close(self):
        klines = client.get_historical_klines(TRADING_PAIR, KLINE_INTERVAL_1MINUTE, "1 day ago UTC")
        close_prices = [float(kline[4]) for kline in klines]
        close_times = [float(kline[0])/1000 for kline in klines]
        times = []
        for time in close_times:
            times.append(dt.datetime.fromtimestamp (time))
        return close_prices, times


    def analyze_all (self, data_closes):
        close_prices = deque (data_closes[:500], maxlen=500)
        remaining = data_closes[len (close_prices):]

        # send the modified data to the analyzer
        analyzed_data = []
        analyzed_data.append (analyze (close_prices))

        for close in remaining:
            close_prices.append (close)
            analyzed_data.append (analyze (close_prices))
        return analyzed_data


    def plot(self):
        closes, times = self.get_hist_close()
        analyzed = self.analyze_all(closes) # length 941
        times = times[499:]

        hull = [x['hull'] for x in analyzed]
        ema = [x['ema'] for x in analyzed]
        closes = [x['close'] for x in analyzed]
        buy_indices = [i for i, x in enumerate(analyzed) if x['buy_now']]
        buy_prices = [hull[x] for x in buy_indices]
        sell_indices = [i for i, x in enumerate(analyzed) if x['sell_now']]
        sell_prices = [hull[x] for x in sell_indices]

        buy_times = []
        sell_times = []
        for index in buy_indices:
            buy_times.append(times[index])
        for index in sell_indices:
            sell_times.append(times[index])


        figure (num=None, figsize=(10, 8), dpi=90, facecolor='w', edgecolor='k')
        plt.gcf ().canvas.set_window_title ('Historical Buy / Sell Points')

        s1 = plt.subplot(211)
        plt.title ('Buying Points')
        plt.plot (times, closes, label='close', c='orange')
        plt.plot(times, hull, label='hull MA', c='blue')
        plt.plot(times, ema, label='exponential MA', c='green')
        plt.scatter(buy_times, buy_prices, c='g', label='buying point')
        ax = plt.gca ()  # create ref to axis
        ax.xaxis.set_major_locator (mdates.MinuteLocator (interval=180))
        ax.xaxis.set_major_formatter (mdates.DateFormatter ('%H:%M'))

        ax.set_facecolor ("lightgrey")
        ax.yaxis.grid (color="gray", linestyle='dashed')
        ax.xaxis.grid (color="gray", linestyle='dashed')
        ax.legend()

        s2 = plt.subplot (212)
        plt.title ('Selling Points')
        plt.plot (times, closes, label='close', c='orange')
        plt.plot(times, hull, label='hull MA', c='blue')
        plt.plot(times, ema, label='exponential MA', c='green')
        plt.scatter(sell_times, sell_prices, c='r', label='selling point')
        ax = plt.gca ()  # create ref to axis
        ax.xaxis.set_major_locator (mdates.MinuteLocator (interval=180))
        ax.xaxis.set_major_formatter (mdates.DateFormatter ('%H:%M'))
        ax.set_facecolor ("lightgrey")
        ax.yaxis.grid (color="gray", linestyle='dashed')
        ax.xaxis.grid (color="gray", linestyle='dashed')
        ax.legend ()

        plt.show ()

if __name__ == '__main__':
    plot = Plot()
    plot.plot()
