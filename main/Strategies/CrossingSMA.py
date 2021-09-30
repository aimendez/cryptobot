import pandas_ta as ta

strategy_test = ta.Strategy(
                name="Crossing Moving Average - https://www.investopedia.com/ask/answers/122314/how-do-i-use-moving-average-ma-create-forex-trading-strategy.asp",
                ta=[
                    {"kind": "ema", "length": 5},
                    {"kind": "ema", "length": 20},
                    {"kind": "ema", "length": 50},
                ]
            )   
