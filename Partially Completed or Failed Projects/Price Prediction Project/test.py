import yfinance as yf

try:
    sp500 = yf.Ticker("SPY")
    data = sp500.history(period="5d")  # Fetch recent data
    print(data)
except Exception as e:
    print("Error fetching data:", e)
