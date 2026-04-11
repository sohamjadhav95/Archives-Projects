import ccxt
import time
import json
import csv
import os
import threading
import websocket
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from datetime import datetime

# ==============================
# CONFIG
# ==============================

CSV_FILE = "btc_doge_algo_log.csv"

# API KEYS (TESTNET)
API_KEY = "EYBAeJVWTp4IoAmTZtTvi3LpBj5WtaToAWzLYpEi2nbiLUPn4SfP3yVrsD6bjeWk"
API_SECRET = "R2i0rohBITp6TvkrwkVDEZTOQ2qlyGdAIwrwyXwZNH5SOAa2xYmuoLtNT0xEswdK"

# Trade Config
BTC_QTY = 0.012
DOGE_QTY = 8731.0

# Manual start position
current_position = "BTC_LONG"   # or "DOGE_LONG"

# ==============================
# STATE VARIABLES
# ==============================

btc_index = 1000.0
doge_index = 1000.0

prev_btc_price = None
prev_doge_price = None

latest_close = {
    "BTCUSDT": {"price": None, "time": None},
    "DOGEUSDT": {"price": None, "time": None}
}

# Graph Data
plot_x = []
plot_btc = []
plot_doge = []

# ==============================
# EXCHANGE SETUP
# ==============================

print("Connecting to Binance Futures Testnet...")
exchange = ccxt.binance({
    "apiKey": API_KEY,
    "secret": API_SECRET,
    "enableRateLimit": True,
    "options": {
        "defaultType": "future",
    }
})
exchange.set_sandbox_mode(True)  # Enable Testnet
print("Connected!")

# ==============================
# ORDER EXECUTION FUNCTIONS
# ==============================

def cancel_all_open_orders():
    """Cancels all open orders for BTC and DOGE."""
    try:
        exchange.cancel_all_orders("BTC/USDT")
        exchange.cancel_all_orders("DOGE/USDT")
        print("Cancelled all open orders.")
    except Exception as e:
        print(f"Error cancelling orders: {e}")

def close_all_positions():
    """Closes all open positions for BTC and DOGE using Market Reduce-Only."""
    try:
        positions = exchange.fetch_positions()
        for p in positions:
            symbol = p['symbol']
            # We only care about BTC/USDT and DOGE/USDT
            if symbol not in ["BTC/USDT:USDT", "DOGE/USDT:USDT"]:
                continue
                
            contracts = float(p['contracts'])
            side = p['side'] # 'long' or 'short'
            
            if contracts > 0:
                # To close a LONG, we SELL. To close a SHORT, we BUY.
                close_side = 'sell' if side == 'long' else 'buy'
                
                print(f"Closing {side} {symbol} ({contracts})...")
                exchange.create_order(
                    symbol=symbol,
                    type='MARKET',
                    side=close_side,
                    amount=contracts,
                    params={"reduceOnly": True}
                )
                time.sleep(0.5) # Slight delay to ensure processing
        print("All positions closed.")
    except Exception as e:
        print(f"Error closing positions: {e}")

def place_positions(new_state):
    """
    Places new positions based on the desired state.
    BTC_LONG  -> Long BTC, Short DOGE
    DOGE_LONG -> Long DOGE, Short BTC
    """
    try:
        print(f"Executing orders for: {new_state}")
        
        if new_state == "BTC_LONG":
            # Long BTC
            exchange.create_market_order("BTC/USDT", "buy", BTC_QTY)
            print(f"Placed BUY BTC ({BTC_QTY})")
            
            # Short DOGE
            exchange.create_market_order("DOGE/USDT", "sell", DOGE_QTY)
            print(f"Placed SELL DOGE ({DOGE_QTY})")
            
        elif new_state == "DOGE_LONG":
            # Long DOGE
            exchange.create_market_order("DOGE/USDT", "buy", DOGE_QTY)
            print(f"Placed BUY DOGE ({DOGE_QTY})")
            
            # Short BTC
            exchange.create_market_order("BTC/USDT", "sell", BTC_QTY)
            print(f"Placed SELL BTC ({BTC_QTY})")
            
        print("Order placement complete.")
        
    except Exception as e:
        print(f"Error placing orders: {e}")

# ==============================
# CSV INITIALIZATION
# ==============================

file_exists = os.path.isfile(CSV_FILE)
with open(CSV_FILE, mode="a", newline="") as f:
    writer = csv.writer(f)
    if not file_exists:
        writer.writerow([
            "timestamp",
            "btc_price",
            "doge_price",
            "btc_pct",
            "doge_pct",
            "btc_index",
            "doge_index",
            "spread",
            "current_position",
            "flip_occurred"
        ])

print("Algo started | Initial position:", current_position)

# ==============================
# CORE ALGO LOGIC (RUNS ON EVERY MIN CLOSE)
# ==============================



# ==============================
# WEBSOCKET HANDLERS
# ==============================

def on_message(ws, message):
    msg = json.loads(message)

    if "data" not in msg:
        return

    data = msg["data"]
    if data.get("e") != "kline":
        return

    k = data["k"]
    
    symbol = k["s"]
    close_price = float(k["c"])

    # Just update the latest price and time continuously
    latest_close[symbol] = {
        "price": close_price,
        "time": datetime.now() # Use local system time for freshness check
    }

def on_open(ws):
    print("WebSocket connected")

def on_error(ws, error):
    print("WebSocket error:", error)

def on_close(ws):
    print("WebSocket closed")

# ==============================
# SCHEDULER & MAIN LOOP
# ==============================

def on_interval():
    """Runs every 30 seconds."""
    global btc_index, doge_index
    global prev_btc_price, prev_doge_price
    global current_position

    # 1. Get latest prices
    btc_data = latest_close["BTCUSDT"]
    doge_data = latest_close["DOGEUSDT"]

    # Check if data is fresh (within last 10 seconds)
    if btc_data["price"] is None or doge_data["price"] is None:
        print("Waiting for data...")
        return

    btc_price = btc_data["price"]
    doge_price = doge_data["price"]
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # First run only initializes
    if prev_btc_price is None:
        prev_btc_price = btc_price
        prev_doge_price = doge_price
        print(f"[{ts}] Initializing prices... BTC={btc_price}, DOGE={doge_price}")
        
        # >>> FORCE INITIAL POSITION EXECUTION <<<
        print(f"[{ts}] [INIT] Forcing initial position: {current_position}")
        cancel_all_open_orders()
        close_all_positions()
        place_positions(current_position)
        
        return

    # % change (over last 30s)
    try:
        btc_pct = (btc_price - prev_btc_price) / prev_btc_price
        doge_pct = (doge_price - prev_doge_price) / prev_doge_price
    except ZeroDivisionError:
        btc_pct = 0
        doge_pct = 0

    # Index update
    btc_index *= (1 + btc_pct)
    doge_index *= (1 + doge_pct)

    spread = doge_index - btc_index

    # Desired position
    desired_position = "DOGE_LONG" if spread > 0 else "BTC_LONG"

    flip_occurred = 0
    if desired_position != current_position:
        flip_occurred = 1
        current_position = desired_position

        # >>> ORDER EXECUTION START <<<
        print(f"\n[{ts}] [FLIP DETECTED] Switching to {current_position}...")
        cancel_all_open_orders()
        close_all_positions()
        place_positions(current_position)
        # >>> ORDER EXECUTION END <<<

    # Append to CSV
    with open(CSV_FILE, mode="a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            ts,
            btc_price,
            doge_price,
            round(btc_pct, 6),
            round(doge_pct, 6),
            round(btc_index, 3),
            round(doge_index, 3),
            round(spread, 3),
            current_position,
            flip_occurred
        ])

    print(
        f"[{ts}] BTC={btc_price} ({btc_pct:.4%}) DOGE={doge_price} ({doge_pct:.4%}) "
        f"Spread={spread:.2f} "
        f"{'FLIP' if flip_occurred else 'HOLD'} → {current_position}"
    )

    # Update previous prices for NEXT interval
    prev_btc_price = btc_price
    prev_doge_price = doge_price
    
    # Store for Plotting (Keep last 100 points to avoid memory issues)
    plot_x.append(ts.split(" ")[1]) # Just time
    plot_btc.append(btc_index)
    plot_doge.append(doge_index)
    
    if len(plot_x) > 100:
        plot_x.pop(0)
        plot_btc.pop(0)
        plot_doge.pop(0)


def update_plot(frame):
    """Refreshes the plot."""
    plt.cla() # Clear axis
    
    if not plot_x:
        return

    plt.plot(plot_x, plot_btc, label="BTC Index", color="orange")
    plt.plot(plot_x, plot_doge, label="DOGE Index", color="green")
    
    plt.title(f"Real-Time Asset Index (Spread: {doge_index - btc_index:.2f})")
    plt.legend(loc="upper left")
    plt.xticks(rotation=45, ha='right')
    
    # Limit x-axis tick labels to avoid clutter
    if len(plot_x) > 10:
        # Show every Nth label
        n = len(plot_x) // 10
        ax = plt.gca()
        for index, label in enumerate(ax.xaxis.get_ticklabels()):
            if index % n != 0:
                label.set_visible(False)
    
    plt.tight_layout()


def run_scheduler():
    """Loops and triggers on_interval at :00 and :30 seconds."""
    print("Scheduler started. Waiting for next 30s mark...")
    while True:
        now = datetime.now()
        second = now.second
        microsecond = now.microsecond
        
        # Calculate time to sleep until next :00 or :30
        if second < 30:
            sleep_seconds = 30 - second - (microsecond / 1_000_000)
        else:
            sleep_seconds = 60 - second - (microsecond / 1_000_000)
            
        time.sleep(sleep_seconds)
        
        # Run logic
        try:
            on_interval()
        except Exception as e:
            print(f"Error in interval logic: {e}")
        
        # Sleep a bit to avoid double triggering if logic is super fast
        time.sleep(1) 

def start_ws():
    stream_url = (
        "wss://fstream.binance.com/stream?"
        "streams=btcusdt@kline_1m/dogeusdt@kline_1m"
    )

    ws = websocket.WebSocketApp(
        stream_url,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    
def start_app():
    stream_url = (
        "wss://fstream.binance.com/stream?"
        "streams=btcusdt@kline_1m/dogeusdt@kline_1m"
    )

    ws = websocket.WebSocketApp(
        stream_url,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    
    # 1. Start Scheduler (Background)
    t_sched = threading.Thread(target=run_scheduler)
    t_sched.daemon = True
    t_sched.start()
    
    # 2. Start WebSocket (Background)
    wst = threading.Thread(target=ws.run_forever)
    wst.daemon = True
    wst.start()
    
    # 3. Start Plot (Main Thread - Blocking)
    print("Starting Graph...")
    fig = plt.figure(figsize=(10, 6))
    ani = animation.FuncAnimation(fig, update_plot, interval=1000)
    plt.show()


if __name__ == "__main__":
    start_app()
