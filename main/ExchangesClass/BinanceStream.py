import websocket
import json 
from static.botlogo import botlogo
from datetime  import datetime
import pandas as pd
from static.botlogo import botlogo
from binance.client import Client
import config 

class BinanceBot(object):
	def __init__(self, symbol, interval):
		#------------- Connect to BINANCE API ---------------#
		self.client = Client(config.API_KEY_DEMO, config.API_SECRET_DEMO)
		self.client.API_URL = 'https://testnet.binance.vision/api'
		#------------ Connect to WebSocket ------------------#
		self.symbol = symbol
		self.interval = interval 
		self.socket = f'wss://stream.binance.com:9443/ws/{symbol}@kline_{interval}'
		ws = websocket.WebSocketApp( self.socket, 
									on_open = self.on_open,  
									on_message = self.on_message,
									on_close = self.on_close,
									on_error = self.on_error
									)
		self.ws = ws
		#----------------- Class Variables ----------------#
		self.df_candle = pd.DataFrame()
		self.df = pd.DataFrame()
		self.current_date = self.previous_date = None
		self.prev_min = self.curr_min = None


	def on_open(self, ws):
		'''Displays account details when the connection is open.
		''' 
		print('Connection Succesful!\n')
		self.getAccountDetails()
		print('\nListening ... ')

	def on_close(self, ws):
		'''Closes WebSocket connection and display DF with the candlestick data collected during the session.
		'''
		self.df = self.df[['date', 'open', 'high', 'low', 'close']]
		print(self.df)
		print('\nConnection Closed\n')

	def on_error(self, ws, err):
		print('\nCONNECTION INTERRUPTED',  err)
		print()

	def on_message(self, ws, message):
		candlestick = json.loads(message)
		self.previous_date = self.current_date
		self.current_date = datetime.utcfromtimestamp(int(candlestick['k']['T'])/1000)
		o,h,l,c = float(candlestick['k']['o']), float(candlestick['k']['h']), float(candlestick['k']['l']), float(candlestick['k']['c'])
		#----------------------------------------------------------------------------------------------------------------#
		#----------------------------------------------------------------------------------------------------------------#
		# this block should should be in a utils.py file maybe?
		self.prev_min = self.curr_min
		self.curr_min = self.current_date.minute #for minute (1m,5m,15m,30m) data. If hour or day, we have to change it
		if self.curr_min != self.prev_min:
			if not self.df_candle.empty:
				o = self.df_candle.open.values[0]
				h = self.df_candle.high.max()
				l = self.df_candle.low.min()
				c = self.df_candle.close.values[-1]
				date_str = self.previous_date.strftime('%Y-%m-%d %H:%M') 
				print(f'Date: {date_str}\tOpen: {o}\tHigh: {h}\tLow: {l}\tClose: {c}')
				self.df = self.df.append( {'date':date_str, 'open':o, 'high':h, 'low':l, 'close':c}, ignore_index=True)
				self.df_candle = pd.DataFrame()
		else:
			date_str = self.current_date.strftime('%Y-%m-%d %H:%M')
			self.df_candle = self.df_candle.append( {'date': date_str , 'open':o,'high':h, 'low':l, 'close':c}, ignore_index=True )
		#----------------------------------------------------------------------------------------------------------------#
		#----------------------------------------------------------------------------------------------------------------#


	def getAccountDetails(self):
		'''Displays account details and balances from API.
		'''
		account = self.client.get_account()
		print('===================================================================================================')
		print('========================================= ACCOUNT DETAILS =========================================')
		print('===================================================================================================\n')
		print('----------------------------------------- Balances ------------------------------------------------\n')
		for asset in account['balances']:
			print(asset)
		print()
		print('===================================================================================================')
		print('===================================================================================================')
		print('===================================================================================================\n')


	def getHistoricalData(self):
		'''Retrieves historical data of the past hour (60 points, 1 point per minute for 1m interval) and
		appends it into the Bot's DataFrame for technical analysis.
		This method is call only at the begining of the session when no data has been collected yet.
		'''
		bars = self.client.get_historical_klines(self.symbol.upper(), self.interval, "1 hour ago UTC") #only for 1m interval. If != then we have to change it
		for bar in bars[:-1]:
			date_bar = datetime.utcfromtimestamp(int(bar[0])/1000).strftime('%Y-%m-%d %H:%M')
			self.df = self.df.append(  {'date':date_bar, 'open':float(bar[1]), 'high':float(bar[2]), 'low': float(bar[3]), 'close': float(bar[4])}, ignore_index=True)

	def run(self):
		print(botlogo)
		self.getHistoricalData()
		self.ws.run_forever()



