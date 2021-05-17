from ExchangesClass.BinanceStream import BinanceBot

if __name__ == '__main__':
	
	#----- user specifics -----#
	symbol = 'btcusdt' 
	interval = '1m'

	#----- run bot -------#
	bot = BinanceBot(symbol, interval)
	bot.run()
	