import yfinance as yf
import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator
import json
from http.server import BaseHTTPRequestHandler
import json
import requests
import traceback
import os
import time
class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type','text/plain')
        self.end_headers()

        self.wfile.write('Hello, world!'.encode('utf-8'))
        return
    def fetch_data(symbol="XAUUSD=X", interval="1m", period="1d"):
        """Fetch XAUUSD data from Yahoo Finance."""
        data = yf.download(tickers=symbol, interval=interval, period=period)
        data = data.dropna()  # Drop rows with missing values
        return data
    
    def calculate_indicators(data):
        """Calculate indicators for scalping."""
        data['EMA_Short'] = EMAIndicator(data['Close'], window=9).ema_indicator()
        data['EMA_Long'] = EMAIndicator(data['Close'], window=21).ema_indicator()
        data['RSI'] = RSIIndicator(data['Close'], window=14).rsi()
        return data
    
    def check_trading_signals(data):
        """Check if conditions for buy/sell signals are met."""
        last_row = data.iloc[-1]
        signal = None
    
        # Example scalping strategy:
        if last_row['EMA_Short'] > last_row['EMA_Long'] and last_row['RSI'] < 30:
            signal = "ORDER_TYPE_BUY"
        elif last_row['EMA_Short'] < last_row['EMA_Long'] and last_row['RSI'] > 70:
            signal = "ORDER_TYPE_SELL"
        return signal, last_row['Close']
    
    def do_POST(self):
        """Main handler for Vercel function."""
        # Fetch and process data
        data = fetch_data()
        data = calculate_indicators(data)
        signal, price = check_trading_signals(data)
        if (signal):
            account=os.getenv("ACCOUNT_ID_NADIRA")
            token=os.getenv("METAAPI_TOKEN_NADIRA")
            forward_url = f"https://mt-client-api-v1.london.agiliumtrade.ai/users/current/accounts/{account}/trade"
            # Create response payload
            buy_json={
                "symbol": "XAUUSDm",
                "actionType": signal,
                "volume": 1,
                "stopLoss": 0,
                "takeProfit": 10,
                "takeProfitUnits": "RELATIVE_PIPS"
            }
            headers = {
                'Accept': 'application/json',
                'auth-token':token,
                'Content-Type':'application/json'
                # Add any other required headers here
            }
            
            response = requests.post(
                forward_url,
                json=buy_json,
                headers=headers
            )
      
        return {
            "statusCode": 200,
            "body": json.dumps(response)
        }
