from binance.client import Client
import websocket
import json
import config
#-----------------------------------------------------------------------#
# CONNECT TO BINANCE API
client = Client(config.API_KEY_DEMO, config.API_SECRET_DEMO) #here you have to put your info from ur account
client.API_URL = 'https://testnet.binance.vision/api'
account = client.get_account()

#-----------------------------------------------------------------------#
# FUNCTIONS FOR WEBSOCKET
def on_open(ws): #when open the connection is gonna do whatever this functions does
	print('Connection Succesful!\n')
	print(account)
	print('\nListening ... ')

def on_close(ws): #when closing the connection is gonna call this function
	print('\nConnection Closed\n')

def on_error(ws, err): #if theres an error, is gonna call this function
	print('\nCONNECTION INTERRUPTED',  err)

def on_message(ws, message): #every time we receive a message this functions gets called 
	current_tick = json.loads(message) #this is the info that came from binance
	#this are not candlestick yet, these are raw prices comming in that need to be 
	#aggregated to form a candlestick of the desire interval.
	#------------------------------------------------#
	# here we apply some strategy with those cnadles #
	#------------------------------------------------#
	print(current_tick)

def enterBuyPosition():
	#here check conditions to enter a BUY(LONG) position
	return 

def enterSellPosition():
	#here check conditions to Sell
	return 

def strategy():
	return 

#-----------------------------------------------------------------------#
# CONNECT TO WEBSCOKET
symbol = 'btcusdt'
interval = '1m'
ws = websocket.WebSocketApp( f'wss://stream.binance.com:9443/ws/{symbol}@kline_{interval}',
							on_open =  on_open,  
							on_message =  on_message,
							on_close =  on_close,
							on_error =  on_error
							)

#-----------------------------------------------------------------------#
# START RECEIVING INFO
#ws.run_forever()



orders = client.get_all_orders(symbol=symbol.upper())
quantity = float(orders[-1]['executedQty'])
sell_order = self.client.create_order(symbol=symbol.upper(), side='SELL', type='MARKET', quantity=quantity)
print(sell_order)