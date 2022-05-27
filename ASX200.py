import matplotlib.pyplot as plt
import yfinance as yf
from sqlalchemy import create_engine
import pandas as pd
import numpy as np
import ta

engine = create_engine('sqlite:///WayneDB2.db')
symbol = pd.read_html('https://en.wikipedia.org/wiki/S%26P/ASX_200')[0] 
symbols = (symbol.Code.to_list())      


def applyindicators(df):
    df['SMA_200']  = df.Close.rolling(200).mean()
    df['SMA_20']  = df.Close.rolling(20).mean()
    df['stddev'] = df.Close.rolling(20).std()
    df['Upper'] = df.SMA_20 + 2.5*df.stddev
    df['Lower'] = df.SMA_20 - 2.5*df.stddev
    df['rsi'] = ta.momentum.rsi(df.Close,2)
    
def conditions(df):
    df['Buy'] = np.where((df.Close > df.SMA_200) & (df.Close < df.Lower) & (0.97 * df.Close >= df.Low.shift(-1)),1,0) 
    df['Sell'] = np.where((df.rsi > 50),1,0)
    df['BuyPrice'] = 0.97*df.Close
    df['SellPrice'] = df.Open.shift(-1)
    
def matchedtrades(df):
    Buy_sells = df[(df.Buy == 1)|(df.Sell == 1)]
    matched_Buy_Sell = Buy_sells[(Buy_sells.Buy.diff() == 1) | (Buy_sells.Sell.diff() == 1) ]
    return matched_Buy_Sell

tradeslist = []
for newSymbol in symbols[1:10:]:
    df = yf.download(newSymbol+'.AX',start='2015-01-01',end='2022-5-27')
    #df = pd.read_sql(newSymbol+'.AX',engine,index_col='Date')
    df.Close = df['Adj Close']
    applyindicators(df)
    conditions(df)
    df['Symbol'] = newSymbol
    trades = matchedtrades(df)
    tradeslist.append(trades)
    
tradesdf = pd.concat(tradeslist)
tradesdf['profit'] = (tradesdf.SellPrice.shift(-1) - tradesdf.BuyPrice)/tradesdf.BuyPrice
frame = pd.DataFrame({'profit':tradesdf[::2].profit.values,
                      'Buydates':tradesdf[::2].profit.index,
                      'Selldates':tradesdf[1::2].profit.index,
                      'Buyprice':tradesdf[::2].BuyPrice.values,
                      'Sellprice':tradesdf[1::2].SellPrice.values,
                      'Symbol':tradesdf[::2].Symbol})

sorted_df = frame.sort_values(by='Buydates')
sorted_df = sorted_df.set_index('Buydates',drop=False)

(sorted_df.profit+1).cumprod().plot()
print(tradesdf)
print(sorted_df)
plt.show()


    
