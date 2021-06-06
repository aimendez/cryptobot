import websocket
import json 
from static.botlogo import botlogo
from datetime  import datetime
import pandas as pd
from static.botlogo import botlogo
from binance.client import Client
import config 
import matplotlib.pyplot as plt
import pandas_ta as ta



strategy_test = ta.Strategy(
                name="Crossing Moving Average - https://www.investopedia.com/ask/answers/122314/how-do-i-use-moving-average-ma-create-forex-trading-strategy.asp",
                description="SMA 50,200, BBANDS, RSI, MACD and Volume SMA 20",
                ta=[
                    {"kind": "ema", "length": 5},
                    {"kind": "ema", "length": 20},
                    {"kind": "ema", "length": 50},
                ]
            )   

import os 
cwd = os.getcwd()
df = pd.read_csv(cwd+'\\data\\0_1.csv', index_col=0)
df.set_index(pd.DatetimeIndex(df["date"]), inplace=True)
df.ta.cores = 0
df.ta.strategy(strategy_test)
#df.ta.log_return(cumulative=True, append=True)

print(df)