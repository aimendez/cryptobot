import pandas as pd 

df_candle = pd.DataFrame()
date_str = "2021-05-31 10:31"
o = h = l = c = 100
df_candle = df_candle.append( {'date': date_str , 'open':o,'high':h, 'low':l, 'close':c}, ignore_index=  True )
print(df_candle )