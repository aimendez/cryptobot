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
from Strategies import CrossingSMA as stg


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
		self.strategy = stg.strategy_test
		self.position = False
		self.position_idx = None
		
	def on_open(self, ws):
		'''Displays account details when the connection is open.
		''' 
		print('Connection Succesful!\n')
		self.getAccountDetails()
		self.getOpenOrders()
		print('\nListening ... ')

	def on_close(self, ws):
		'''Closes WebSocket connection and display DF with the candlestick data collected during the session.
		'''
		self.df = self.df[['date', 'open', 'high', 'low', 'close']]
		self.saveCSV(self.df)
		#print(self.df)
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
				o = self.df_candle.open.values[0]#self.df_candle.open.values[0]
				h = self.df_candle.high.values[0]#self.df_candle.high.max()
				l = self.df_candle.low.values[0]#self.df_candle.low.min()
				c = self.df_candle.close.values[0]#self.df_candle.close.values[-1]
				date_str = self.previous_date.strftime('%Y-%m-%d %H:%M') 
				print(f'Date: {date_str}\tOpen: {o}\tHigh: {h}\tLow: {l}\tClose: {c}')
				self.df = self.df.append( pd.DataFrame({'open':o, 'high':h, 'low':l, 'close':c}, index = [date_str]) ) 
				self.df_candle = pd.DataFrame()

				#------------------------------#
				#buy if theres no position and sell 3 min later.
				if not self.position:
					self.buy()
					self.position_idx = self.df.index.get_loc(self.df.index[-1])
				else:
					if self.df.index.get_loc(self.df.index[-1]) - self.position_idx == 3:
						self.sell()
				#-----------------------------#
		else:
			date_str = self.current_date.strftime('%Y-%m-%d %H:%M')
			self.df_candle = pd.DataFrame( {'open':o,'high':h, 'low':l, 'close':c}, index = [date_str] )

			

		#----------------------------------------------------------------------------------------------------------------#
		#----------------------------------------------------------------------------------------------------------------#


	def getAccountDetails(self):
		'''Displays account details and balances from API.
		'''
		account = self.client.get_account()
		print('===================================================================================================')
		print('============================================= BALANCE =============================================')
		print('===================================================================================================\n')
		for asset in account['balances']:
			print(asset)
		print()
		print('===================================================================================================')
		print('===================================================================================================')
		print('===================================================================================================\n\n\n')

	def getOpenOrders(self):

		orders = self.client.get_all_orders(symbol=self.symbol.upper())
		print('===================================================================================================')
		print('========================================= LAST ORDERS =============================================')
		print('===================================================================================================\n')
		for order in orders:
			orderid = order['orderId']
			symbol = order['symbol']
			order_type = order['type']
			side = order['side']
			quantity = order['executedQty']
			print(f'ID: {orderid} \t SYMBOL: {symbol} \t TYPE: {order_type} \t SIDE: {side} \t QTY: {quantity}')
		print()
		print('===================================================================================================')
		print('===================================================================================================')
		print('===================================================================================================\n')

		# checks current position
		if orders[-1]['side'] == 'BUY':
			self.position = True 


	def getHistoricalData(self):
		'''Retrieves historical data of the past hour (60 points, 1 point per minute for 1m interval) and
		appends it into the Bot's DataFrame for technical analysis.
		This method is call only at the begining of the session when no data has been collected yet.
		'''
		list_aux = []
		bars = self.client.get_historical_klines(self.symbol.upper(), self.interval, "1 hour ago UTC") #only for 1m interval. If != then we have to change it
		for bar in bars[:-1]:
			date_bar = datetime.utcfromtimestamp(int(bar[0])/1000).strftime('%Y-%m-%d %H:%M')
			list_aux.append(  pd.DataFrame({'open':float(bar[1]), 'high':float(bar[2]), 'low': float(bar[3]), 'close': float(bar[4])}, index=[date_bar]))
		
		self.df = pd.concat(list_aux)

	
	def sell(self):
		print('PLACING SELL ORDER ...')
		if self.position:
			orders = self.client.get_all_orders(symbol=self.symbol.upper())
			quantity = float(orders[-1]['executedQty'])
			sell_order = self.client.create_order(symbol=self.symbol.upper(), side='SELL', type='MARKET', quantity=quantity)
			#sell_order = self.client.order_market_sell(symbol=self.symbol.upper(), quantity=0.0005)
			self.position = False
			print('SELL ORDER EXCECUTED.')
			print(sell_order)
		else:
			print('CANT PLACE SELL ORDER. NO BUY ORDERS TO SELL.')

	def buy(self):
		print('PLACING BUY ORDER ...')
		if self.position:
			print('CANT PLACE BUY ORDER. ALREADY IN BUY POSITION.')
		else:
			quantity = 0.0005
			buy_order = self.client.create_order(symbol=self.symbol.upper(), side='BUY', type='MARKET', quantity=quantity)
			self.position = True
			print('BUY ORDER EXCECUTED.')
			print(buy_order)


	def saveCSV(self, df):
		period = (df.index[0], df.index[1])
		df.to_csv('./data/'+str(period[0])+'_'+str(period[1])+'.csv')

	def run(self):
		print(botlogo)
		self.getHistoricalData()
		self.ws.run_forever()




