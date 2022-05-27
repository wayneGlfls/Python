import matplotlib.pyplot as plt
import ta
import numpy as np
import yfinance as yf
import pandas as pd



df = yf.download('EML.AX',start='2015-01-01',end='2022-4-14')

df.Close = df['Adj Close']

def applyindicators(df):
    df['SMA_200']  = df.Close.rolling(200).mean()
    df['SMA_20']  = df.Close.rolling(20).mean()
    df['stddev'] = df.Close.rolling(20).std()
    df['Upper'] = df.SMA_20 + 2.5*df.stddev
    df['Lower'] = df.SMA_20 - 2.5*df.stddev
    df['rsi'] = ta.momentum.rsi(df.Close,2)
       
(applyindicators(df))

def conditions(df):
    df['Buy'] = np.where((df.Close > df.SMA_200) & (df.Close < df.Lower) & (0.97 * df.Close >= df.Low.shift(-1)),1,0) 
    df['Sell'] = np.where((df.rsi > 50),1,0)
    df['BuyPrice'] = 0.97*df.Close
    df['SellPrice'] = df.Open.shift(-1)

def matchedtrades(df):
    Buy_sells = df[(df.Buy == 1)|(df.Sell == 1)]
    matched_Buy_Sell = Buy_sells[(Buy_sells.Buy.diff() == 1) | (Buy_sells.Sell.diff() == 1) ]
    return matched_Buy_Sell

df.tail(250)[['Close','SMA_20','Upper','Lower']].plot()
(conditions(df))

#print(df.tail(250))
print(matchedtrades(df))
plt.show()
    
